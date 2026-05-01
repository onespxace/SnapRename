"""Rename engine — generates new filenames from rules and executes renames."""

import os
import re
from datetime import datetime
from models.file_item import FileItem
from models.rule_segment import RuleSegment, SegmentType
from core.logger import log_info, log_debug, log_error, log_warning


class RenameEngine:
    """Apply ordered RuleSegments to generate new filenames."""

    def generate_name(
        self,
        f: FileItem,
        segments: list[RuleSegment],
        index: int = 1,
        table_df=None,
    ) -> str:
        """Build new filename from segments. Returns new name (without path)."""
        parts: list[str] = []
        ext = FileItem.get_ext(f.original_name)

        for seg in sorted(segments, key=lambda s: s.position):
            part = self._render_segment(seg, f, index, table_df)
            if part:
                parts.append(part)

        name = "".join(parts) + ext
        return self._sanitize(name)

    def _render_segment(self, seg: RuleSegment, f: FileItem, index: int, table_df) -> str:
        if seg.type == SegmentType.TEXT:
            return seg.text
        elif seg.type == SegmentType.COUNTER:
            n = seg.counter_start + seg.counter_step * (index - 1)
            if seg.counter_padding > 0:
                return str(n).zfill(seg.counter_padding)
            return str(n)
        elif seg.type == SegmentType.DATE:
            return datetime.now().strftime(seg.date_format)
        elif seg.type == SegmentType.EXTRACT:
            return self._extract_field(seg, f, table_df)
        elif seg.type == SegmentType.TABLE_FIELD:
            return self._table_field(seg, f, table_df)
        elif seg.type == SegmentType.KEYWORD:
            return self._keyword_field(seg, f)
        return ""

    def _keyword_field(self, seg: RuleSegment, f: FileItem) -> str:
        keywords = [kw.strip() for kw in seg.keyword_list.replace("，", ",").split(",") if kw.strip()]
        if not keywords:
            return ""
        base = FileItem.get_stem(f.original_name)
        best = ""
        best_pos = -1
        for kw in keywords:
            pos = base.find(kw)
            if pos != -1 and (best_pos == -1 or pos < best_pos):
                start = max(0, pos - seg.keyword_range)
                end = min(len(base), pos + len(kw) + seg.keyword_range)
                best = base[start:end]
                best_pos = pos
        return best

    def _extract_field(self, seg: RuleSegment, f: FileItem, table_df) -> str:
        field = seg.extract_field
        if not field:
            return ""
        value = f.extracted_fields.get(field, "")
        if not value and seg.extract_regex:
            m = re.search(seg.extract_regex, f.original_name)
            if m:
                value = m.group(1) if m.groups() else m.group(0)
        if value:
            value = value[:seg.extract_max_len]
            if len(value) < seg.extract_min_len:
                value = ""
        if value and table_df is not None and seg.table_column:
            col = seg.table_column
            if col in table_df.columns:
                valid_values = set(table_df[col].dropna().astype(str))
                if value not in valid_values:
                    value = ""
        if not value:
            return "[原]"
        return value

    def _table_field(self, seg: RuleSegment, f: FileItem, table_df) -> str:
        if table_df is None or not seg.table_column:
            return ""
        col = seg.table_column
        if col not in table_df.columns:
            return ""
        name = f.extracted_fields.get("姓名", "")
        sid = f.extracted_fields.get("学号", "") or f.extracted_fields.get("大学号", "")
        for _, row in table_df.iterrows():
            row_name = str(row.get("姓名", row.get("name", "")))
            row_sid = str(row.get("学号", row.get("id", row.get("student_id", row.get("大学号", "")))))
            if (name and name in row_name) or (sid and sid in row_sid):
                return str(row[col])
        return ""

    def check_conflicts(self, files: list[FileItem], rename_map: dict[str, str]) -> list[str]:
        conflicts: list[str] = []
        seen: dict[str, str] = {}
        for f in files:
            new_name = rename_map.get(f.path, f.original_name)
            new_path = os.path.join(f.dirname(), new_name)
            if new_path in seen:
                conflicts.append(f"{f.original_name} → {new_name} (冲突: {seen[new_path]})")
            elif os.path.exists(new_path) and new_path != f.path:
                conflicts.append(f"{f.original_name} → {new_name} (目标已存在)")
            seen[new_path] = f.path
        return conflicts

    def execute(self, rename_map: dict[str, str], classify_rules: list[str] | None = None) -> tuple[int, int, dict[str, str]]:
        import shutil as sh
        success = 0
        failed = 0
        renamed: dict[str, str] = {}
        for src, new_name in rename_map.items():
            dst = os.path.join(os.path.dirname(src), new_name)
            try:
                if src != dst:
                    sh.move(src, dst)
                renamed[src] = dst
                success += 1
            except OSError:
                failed += 1
        return success, failed, renamed

    def execute_to_folder(self, files: list[FileItem], rename_map: dict[str, str], output_dir: str, classify_rules: list[str]) -> tuple[int, int]:
        """Rename + copy to output folder, organized by classification subfolders."""
        from core.classifier import group_files
        import shutil as sh
        output_dir_abs = os.path.normpath(os.path.abspath(output_dir))
        try:
            os.makedirs(output_dir_abs, exist_ok=True)
        except OSError as e:
            log_error(f"无法创建输出目录 {output_dir_abs}", e)
            return 0, 0
        if classify_rules:
            groups = group_files(files, classify_rules)
        else:
            groups = {"全部": files}
        log_info(f"execute_to_folder: {len(groups)} 组, 目标={output_dir_abs}")
        success = 0
        failed = 0
        for label, group_files_list in groups.items():
            parts = [self._sanitize(p) for p in label.split("｜")]
            parts = [p for p in parts if p]
            if not parts:
                parts = ["未知"]
            subdir = os.path.join(output_dir_abs, *parts)
            log_info(f"  创建文件夹: {subdir} ({len(group_files_list)} 个文件)")
            try:
                os.makedirs(subdir, exist_ok=True)
            except OSError as e:
                log_error(f"  无法创建文件夹 {subdir}", e)
                continue
            for f in group_files_list:
                new_name = self._sanitize(rename_map.get(f.path, f.original_name))
                dst = os.path.join(subdir, new_name)
                try:
                    log_debug(f"    复制: {f.original_name} → {dst}")
                    sh.copy(f.path, dst)
                    success += 1
                except OSError as e:
                    log_warning(f"    复制失败: {f.path} → {dst} | {e}")
                    failed += 1
        log_info(f"execute_to_folder 完成: {success} 成功, {failed} 失败")
        return success, failed

    def _sanitize(self, name: str) -> str:
        invalid = '<>:"/\\|?*'
        for ch in invalid:
            name = name.replace(ch, "")
        name = name.strip()
        if not name:
            name = "untitled"
        return name
