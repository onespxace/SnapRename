"""pywebview JS bridge — exposes Python API to React frontend."""

from __future__ import annotations
import os
import shutil
import threading
import webview

from models.file_item import FileItem
from models.rule_segment import RuleSegment, SegmentType
from py_engine.extractor import SmartExtractor
from core.renamer import RenameEngine
from core.backup import BackupManager
from core.table_importer import TableImporter
from core.preset_manager import PresetManager
from core.classifier import group_files, get_classify_fields
from core.logger import get_logger, log_info, log_error, log_debug, log_warning

log = get_logger("Bridge")


class Bridge:
    """API class exposed to JavaScript via webview.expose."""

    def __init__(self):
        self.files: list[FileItem] = []
        self.segments: list[RuleSegment] = []
        self.preview_index: int = -1
        self.selected_segment_index: int = -1
        self.table_df = None
        self.table_columns: list[str] = []
        self._window: webview.Window | None = None

        self.extractor = SmartExtractor()
        self.renamer = RenameEngine()
        self.backup_mgr = BackupManager()
        self.table_importer = TableImporter()
        self.preset_mgr = PresetManager()
        self.preset_mgr.ensure_builtin_presets()

        self._theme = "light"
        self._notify_timer: threading.Timer | None = None
        self._last_rename_map: dict[str, str] = {}
        self.classify_rules: list[str] = []  # ordered field names for classification

    def set_window(self, window: webview.Window):
        self._window = window

    # ── File operations ──

    def add_files(self, paths: list[str]):
        existing = {f.path for f in self.files}
        new = [FileItem(path=p) for p in paths if p not in existing]
        if not new:
            return
        self.files.extend(new)
        for f in new:
            f.extracted_fields = self.extractor.extract(f.original_name)
        self._refresh_derived()
        if not self.files or self.preview_index < 0:
            self.preview_index = 0
        self._notify_state()

    def add_folder(self, path: str):
        import os
        gathered = []
        for root, _, filenames in os.walk(path):
            for fn in filenames:
                gathered.append(os.path.join(root, fn))
        self.add_files(gathered)

    def clear_files(self):
        self.files.clear()
        self.preview_index = -1
        self._notify_state()

    def get_files(self) -> list[dict]:
        return [f.to_dict() for f in self.files]

    def get_preview_file(self) -> dict | None:
        if 0 <= self.preview_index < len(self.files):
            f = self.files[self.preview_index]
            idx = self.files.index(f) + 1
            f.new_name = self.renamer.generate_name(f, self.segments, idx, self.table_df)
            return f.to_dict()
        return None

    def set_preview_index(self, index: int):
        if 0 <= index < len(self.files):
            self.preview_index = index
            self._notify_state()

    # ── Segment operations ──

    def add_segment(self, segment_type: str, kwargs: dict | None = None):
        try:
            st = SegmentType[segment_type]
        except KeyError:
            return
        kw = kwargs or {}
        seg = RuleSegment(type=st, position=len(self.segments), **kw)
        self.segments.append(seg)
        self._notify_state()

    def remove_segment(self, index: int):
        if 0 <= index < len(self.segments):
            del self.segments[index]
        self._reindex()
        self._notify_state()

    def move_segment(self, from_idx: int, to_idx: int):
        n = len(self.segments)
        if 0 <= from_idx < n and 0 <= to_idx < n:
            seg = self.segments.pop(from_idx)
            self.segments.insert(to_idx, seg)
        self._reindex()
        self._notify_state()

    def update_segment(self, index: int, data: dict):
        if 0 <= index < len(self.segments):
            seg = self.segments[index]
            for k, v in data.items():
                if hasattr(seg, k):
                    if k == "type" and isinstance(v, str):
                        try:
                            st = SegmentType[v]
                            setattr(seg, k, st)
                        except KeyError:
                            pass
                    else:
                        try:
                            setattr(seg, k, v)
                        except (TypeError, ValueError):
                            pass
        self._notify_state()

    def select_segment(self, index: int):
        self.selected_segment_index = index
        for i, s in enumerate(self.segments):
            s.selected = (i == index)
        self._notify_state()

    def get_segments(self) -> list[dict]:
        return [s.to_dict() for s in self.segments]

    def get_selected_segment(self) -> dict | None:
        if 0 <= self.selected_segment_index < len(self.segments):
            return self.segments[self.selected_segment_index].to_dict()
        return None

    def get_available_fields(self) -> list[str]:
        return self.extractor.get_available_fields(self.files)

    # ── Table operations ──

    def import_table(self, path: str) -> dict | None:
        result = self.table_importer.import_file(path)
        if result is not None:
            self.table_df, self.table_columns = result
            self._notify_state()
            return {"columns": self.table_columns, "rows": len(self.table_df)}
        return None

    def get_table_info(self) -> dict | None:
        if self.table_df is not None:
            return {"columns": self.table_columns, "rows": len(self.table_df)}
        return None

    # ── Rename operations ──

    def execute_rename(self) -> dict:
        if not self.files or not self.segments:
            return {"success": 0, "failed": 0}
        rename_map = {}
        for i, f in enumerate(self.files):
            new_name = self.renamer.generate_name(f, self.segments, i + 1, self.table_df)
            rename_map[f.path] = new_name
        conflicts = self.renamer.check_conflicts(self.files, rename_map)
        self.backup_mgr.backup(self.files)
        success, failed, renamed = self.renamer.execute(rename_map, self.classify_rules if self.classify_rules else None)
        path_map = {os.path.normpath(old): new for old, new in renamed.items()}
        for f in self.files:
            np = path_map.get(os.path.normpath(f.path))
            if np:
                f.path = np
                f.original_name = os.path.basename(np)
                f.new_name = f.original_name
        self._last_rename_map = {new: old for old, new in renamed.items()}
        self._notify_state()
        return {"success": success, "failed": failed, "conflicts": len(conflicts)}

    def undo_rename(self) -> int:
        if not self._last_rename_map:
            return 0
        reverse_map = {new_path: os.path.join(os.path.dirname(new_path), os.path.basename(old_path))
                       for new_path, old_path in self._last_rename_map.items()}
        restored_count = 0
        for new_path, old_name in reverse_map.items():
            if os.path.exists(new_path):
                restored_path = os.path.join(os.path.dirname(new_path), os.path.basename(old_name))
                try:
                    if new_path != restored_path:
                        shutil.move(new_path, restored_path)
                    restored_count += 1
                except OSError:
                    pass
        # Fallback: restore from backup for files that were moved but can't be undone
        backup_restored = self.backup_mgr.restore(self._last_rename_map)
        if backup_restored:
            for original_path in backup_restored:
                restored_count += 1
        # Update FileItem paths
        if restored_count:
            for f in self.files:
                old = self._last_rename_map.get(f.path)
                if old:
                    f.path = old
                    f.original_name = os.path.basename(old)
                    f.new_name = f.original_name
        self._last_rename_map = {}
        self._notify_state()
        return restored_count

    # ── Preset operations ──

    def save_preset(self, name: str):
        self.preset_mgr.save(name, self.segments)

    def load_preset(self, name: str) -> list[dict]:
        segs = self.preset_mgr.load(name)
        if segs:
            self.segments = segs
            self._notify_state()
            return [s.to_dict() for s in segs]
        return []

    def list_presets(self) -> list[str]:
        return self.preset_mgr.list_presets()

    # ── Classification ──

    def set_classify_rules(self, fields: list[str]):
        self.classify_rules = fields
        self._notify_state()

    def get_classify_groups(self) -> dict:
        if not self.classify_rules or not self.files:
            return {"groups": {}}
        grouped = group_files(self.files, self.classify_rules)
        return {
            "groups": {k: [f.to_dict() for f in v] for k, v in grouped.items()},
            "rules": self.classify_rules,
        }

    def get_classify_fields(self) -> list[str]:
        return get_classify_fields(self.files)

    def classify_export(self, output_dir: str) -> dict:
        """Rename all files + copy to output folder organized by classification."""
        log_info(f"分组导出开始 → {output_dir}")
        log_info(f"文件数={len(self.files)}, 分段规则数={len(self.segments)}, 分组规则={self.classify_rules}")

        if not self.files:
            log_warning("分组导出失败：没有文件")
            return {"success": 0, "failed": 0, "error": "没有文件"}
        if not self.classify_rules:
            log_warning("分组导出失败：未设置分组规则")
            return {"success": 0, "failed": 0, "error": "未设置分组规则"}
        try:
            rename_map = {}
            for i, f in enumerate(self.files):
                if self.segments:
                    new_name = self.renamer.generate_name(f, self.segments, i + 1, self.table_df)
                else:
                    new_name = f.original_name
                rename_map[f.path] = new_name
                log_debug(f"  文件{i+1}: {f.original_name} → {new_name}")

            from core.classifier import group_files
            groups = group_files(self.files, self.classify_rules)
            log_info(f"分组结果：{len(groups)} 组")
            for g, gf in groups.items():
                log_info(f"  组「{g}」→ {len(gf)} 个文件")

            success, failed = self.renamer.execute_to_folder(self.files, rename_map, output_dir, self.classify_rules)

            log_info(f"分组导出完成：{success} 成功, {failed} 失败")
            import os
            if os.path.isdir(output_dir):
                for root, dirs, files_in_dir in os.walk(output_dir):
                    for fn in files_in_dir:
                        log_debug(f"  已创建: {os.path.join(root, fn)}")

            return {"success": success, "failed": failed}
        except Exception as e:
            log_error(f"分组导出异常", e)
            return {"success": 0, "failed": 0, "error": str(e)}

    # ── Theme ──

    def cycle_theme(self) -> str:
        from theme import toggle_theme
        themes = ["light", "highcontrast", "dark"]
        idx = themes.index(self._theme) if self._theme in themes else 0
        self._theme = themes[(idx + 1) % len(themes)]
        toggle_theme()
        return self._theme

    def get_is_dark(self) -> bool:
        return self._theme != "light"

    def get_is_highcontrast(self) -> bool:
        return self._theme == "highcontrast"

    # ── Native dialogs ──

    def pick_files(self) -> list[str]:
        import tkinter.filedialog as fd
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        paths = fd.askopenfilenames(title="选择文件")
        root.destroy()
        return list(paths)

    def pick_folder(self) -> str:
        import tkinter.filedialog as fd
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        path = fd.askdirectory(title="选择文件夹")
        root.destroy()
        return path

    def pick_table(self) -> str:
        import tkinter.filedialog as fd
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        path = fd.askopenfilename(
            title="导入表格",
            filetypes=[("表格文件", "*.csv *.xlsx *.xls"), ("CSV", "*.csv"), ("Excel", "*.xlsx *.xls")],
        )
        root.destroy()
        return path

    # ── Full state sync ──

    def generate_all_previews(self) -> list[dict]:
        """Generate new_name for all files and return the list."""
        result = []
        for i, f in enumerate(self.files):
            f.new_name = self.renamer.generate_name(f, self.segments, i + 1, self.table_df)
            result.append(f.to_dict())
        self._notify_state()
        return result

    def get_full_state(self) -> dict:
        if self.files and self.preview_index < 0:
            self.preview_index = 0
        # Generate preview names for ALL files
        for i, f in enumerate(self.files):
            f.new_name = self.renamer.generate_name(f, self.segments, i + 1, self.table_df)
        preview = None
        if self.files and 0 <= self.preview_index < len(self.files):
            preview = self.files[self.preview_index].to_dict()
        return {
            "files": [f.to_dict() for f in self.files],
            "segments": [s.to_dict() for s in self.segments],
            "previewIndex": self.preview_index,
            "selectedSegmentIndex": self.selected_segment_index,
            "previewFile": preview,
            "availableFields": self.extractor.get_available_fields(self.files),
            "tableInfo": {"columns": self.table_columns, "rows": len(self.table_df)} if self.table_df is not None else None,
            "isDark": self._theme != "light",
            "theme": self._theme,
            "classifyRules": self.classify_rules,
            "classifyFields": get_classify_fields(self.files),
            "classifyGroups": {k: [f.to_dict() for f in v] for k, v in group_files(self.files, self.classify_rules).items()} if self.classify_rules else {},
        }

    # ── Internal ──

    def _refresh_derived(self):
        for f in self.files:
            if not f.extracted_fields:
                f.extracted_fields = self.extractor.extract(f.original_name)

    def _reindex(self):
        for i, s in enumerate(self.segments):
            s.position = i

    def _notify_state(self):
        pass  # Frontend syncs on its own timing, no push needed
