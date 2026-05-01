"""Entry point for SnapRename."""

import os
import ctypes
import threading
import http.server
import socketserver
import webview

from app_paths import APP_WINDOW_TITLE, get_resource_path
from bridge import Bridge
from theme import apply_acrylic

FRONTEND_DIR = get_resource_path("frontend", "dist")
INDEX_HTML = os.path.join(FRONTEND_DIR, "index.html")
DEV_SERVER = "http://localhost:5173"


def _find_free_port(start: int = 18080) -> int:
    import socket
    for port in range(start, start + 100):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(("127.0.0.1", port))
                return port
        except OSError:
            continue
    return start


def _start_http_server(directory: str) -> tuple[int, threading.Thread]:
    """Serve static files from directory on localhost:free-port in a daemon thread."""

    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=directory, **kwargs)

        def log_message(self, format, *args):
            pass

    port = _find_free_port()
    server = socketserver.TCPServer(("127.0.0.1", port), Handler)
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    return port, t


def _get_hwnd(title: str) -> int | None:
    hwnd = ctypes.windll.user32.FindWindowW(None, title)
    return hwnd if hwnd else None


def main():
    bridge = Bridge()

    if os.path.exists(INDEX_HTML):
        port, _ = _start_http_server(FRONTEND_DIR)
        url = f"http://127.0.0.1:{port}"
    else:
        url = DEV_SERVER

    window = webview.create_window(
        APP_WINDOW_TITLE,
        url=url,
        width=1152,
        height=700,
        min_size=(960, 550),
        js_api=bridge,
    )

    bridge.set_window(window)

    def on_shown():
        hwnd = _get_hwnd(APP_WINDOW_TITLE)
        if hwnd:
            try:
                apply_acrylic(hwnd)
            except Exception:
                pass

    window.events.shown += on_shown
    webview.start(debug=not os.path.exists(INDEX_HTML))


if __name__ == "__main__":
    main()
