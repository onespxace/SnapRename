"""Design system — theme toggle + window effects."""

from __future__ import annotations

import ctypes
from ctypes import wintypes

_is_dark = False


def is_dark() -> bool:
    return _is_dark


def toggle_theme():
    global _is_dark
    _is_dark = not _is_dark
    return _is_dark


def apply_acrylic(hwnd: int):
    """Apply acrylic/blur effect to window background (Windows 10/11)."""
    try:
        from ctypes import windll
        accent = ctypes.c_int(4)  # ACCENT_ENABLE_ACRYLICBLURBEHIND
        data = (ctypes.c_int * 4)(accent, 1, 0x99000000, 0)
        comp = (ctypes.c_int * 4)(1, *data)
        windll.user32.SetWindowCompositionAttribute(wintypes.HWND(hwnd), ctypes.byref(comp))
    except Exception:
        pass
