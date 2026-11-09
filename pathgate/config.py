from pathlib import Path
import os
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# pathgate/config.py
ALLOWED_PATHS: list[str] = []   # filled in by configure() at startup
_state = {"read_only": False}

def configure(paths: list[str], read_only: bool) -> None:
    ALLOWED_PATHS.clear()
    ALLOWED_PATHS.extend(paths)      # mutate in place so existing imports see it
    _state["read_only"] = read_only

def is_read_only() -> bool:
    return _state["read_only"]


def is_path_allowed(path):
    abs_path = os.path.realpath(path)  # resolves symlinks too
    for allowed in ALLOWED_PATHS:
        allowed_normalized = os.path.realpath(allowed)
        # Ensure that the allowed path ends with separator before prefix check
        if not allowed_normalized.endswith(os.sep):
            allowed_normalized += os.sep
        # check exact match
        if abs_path == os.path.realpath(allowed) or abs_path.startswith(allowed_normalized):
            return True
    return False
