from __future__ import annotations

import os
import sys


APP_NAME = "SnapRename"
APP_WINDOW_TITLE = "SnapRename"
APP_VERSION = "1.0.0"

_ROOT = os.path.dirname(os.path.abspath(__file__))


def _ensure_dir(path: str) -> str:
    os.makedirs(path, exist_ok=True)
    return path


def get_app_root() -> str:
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return _ROOT


def get_resource_root() -> str:
    if getattr(sys, "frozen", False):
        meipass = getattr(sys, "_MEIPASS", "")
        if meipass:
            return meipass
        return os.path.dirname(sys.executable)
    return _ROOT


def get_resource_path(*parts: str) -> str:
    return os.path.join(get_resource_root(), *parts)


def is_portable_mode() -> bool:
    return os.path.exists(os.path.join(get_app_root(), "portable.flag"))


def get_data_root() -> str:
    if is_portable_mode():
        return _ensure_dir(os.path.join(get_app_root(), "data"))
    appdata = os.environ.get("APPDATA") or os.path.expanduser("~")
    return _ensure_dir(os.path.join(appdata, APP_NAME))


def get_logs_dir() -> str:
    return _ensure_dir(os.path.join(get_data_root(), "logs"))


def get_backup_root() -> str:
    return _ensure_dir(os.path.join(get_data_root(), "_backup"))


def get_presets_dir() -> str:
    return _ensure_dir(os.path.join(get_data_root(), "presets"))


def get_bundled_presets_dir() -> str:
    return get_resource_path("presets")
