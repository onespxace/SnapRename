import logging
import os
import sys
from datetime import datetime

from app_paths import get_logs_dir

LOG_DIR = get_logs_dir()
LOG_FILE = os.path.join(LOG_DIR, f"app_{datetime.now().strftime('%Y%m%d')}.log")

os.makedirs(LOG_DIR, exist_ok=True)

_formatter = logging.Formatter(
    "[%(asctime)s] %(levelname)-5s %(name)s ‣ %(message)s",
    datefmt="%H:%M:%S",
)

_file_handler: logging.Handler | None = None
try:
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    _file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    _file_handler.setFormatter(_formatter)
except OSError:
    _file_handler = None

_console_handler = logging.StreamHandler(sys.stdout)
_console_handler.setFormatter(_formatter)

_logger = logging.getLogger("BatchRenamer")
_logger.setLevel(logging.DEBUG)
if _file_handler:
    _logger.addHandler(_file_handler)
_logger.addHandler(_console_handler)

def get_logger(name: str = "BatchRenamer") -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    if not logger.handlers:
        if _file_handler:
            logger.addHandler(_file_handler)
        logger.addHandler(_console_handler)
    return logger

def log_error(msg: str, exc: Exception | None = None):
    if exc:
        _logger.error(f"{msg} | {exc}")
    else:
        _logger.error(msg)

def log_info(msg: str):
    _logger.info(msg)

def log_debug(msg: str):
    _logger.debug(msg)

def log_warning(msg: str):
    _logger.warning(msg)
