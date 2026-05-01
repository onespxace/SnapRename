"""Backup manager — creates timestamped backups and supports undo."""

from __future__ import annotations

import os
import shutil
import json
from datetime import datetime
from app_paths import get_backup_root
from models.file_item import FileItem


class BackupManager:
    """Backs up files before rename and restores on undo."""

    def __init__(self):
        self._last_backup_dir: str = ""
        self._undo_map: dict[str, str] = {}  # new_path -> original_path

    def backup(self, files: list[FileItem]) -> str:
        """Copy all files to a timestamped backup directory. Returns backup dir path."""
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = os.path.join(get_backup_root(), ts)
        os.makedirs(backup_dir, exist_ok=True)

        undo_map: dict[str, str] = {}
        for f in files:
            if os.path.exists(f.path):
                dst = os.path.join(backup_dir, f.original_name)
                shutil.copy2(f.path, dst)
                undo_map[f.path] = f.original_name

        # Save undo map as JSON for persistence
        map_path = os.path.join(backup_dir, "undo_map.json")
        with open(map_path, "w", encoding="utf-8") as fh:
            json.dump(undo_map, fh, ensure_ascii=False, indent=2)

        self._last_backup_dir = backup_dir
        self._undo_map = undo_map
        return backup_dir

    def restore(self, rename_map: dict[str, str] | None = None) -> list[str] | None:
        """Restore files from the last backup. Optionally accepts {new_path: original_path} rename_map to clean up renamed files first.
        Returns list of restored original paths on success, None on failure."""

        # If a rename map is provided, try to reverse the renaming first
        if rename_map:
            for new_path, original_path in rename_map.items():
                if os.path.exists(new_path):
                    try:
                        if new_path != original_path:
                            shutil.move(new_path, original_path)
                    except OSError:
                        continue

        # Then restore any remaining files from backup
        backups_root = get_backup_root()
        if not os.path.isdir(backups_root):
            return None

        dirs = sorted(
            [d for d in os.listdir(backups_root) if os.path.isdir(os.path.join(backups_root, d))],
            reverse=True,
        )
        if not dirs:
            return None

        backup_dir = os.path.join(backups_root, dirs[0])
        map_path = os.path.join(backup_dir, "undo_map.json")

        if not os.path.exists(map_path):
            return None

        with open(map_path, "r", encoding="utf-8") as fh:
            undo_map: dict[str, str] = json.load(fh)

        restored: list[str] = []
        for original_path, original_name in undo_map.items():
            backup_path = os.path.join(backup_dir, original_name)
            if os.path.exists(backup_path):
                try:
                    # If the renamed file was already moved back, skip
                    if os.path.exists(original_path):
                        continue
                    shutil.move(backup_path, original_path)
                    restored.append(original_path)
                except OSError:
                    pass

        return restored if restored else None
