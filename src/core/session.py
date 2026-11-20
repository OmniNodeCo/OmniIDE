"""Workspace session save/restore (open tabs across restarts).

Pure Python — no Qt imports so it can be unit-tested headless.
"""

import json
import os

from src.config import CONFIG_DIR

SESSION_PATH = os.path.join(CONFIG_DIR, "session.json")


def save_session(files, active_index=0):
    """Persist the open file list (absolute paths) and active tab index."""
    payload = {
        "files": [os.path.abspath(f) for f in files if f],
        "active_index": int(active_index),
    }
    try:
        with open(SESSION_PATH, "w") as f:
            json.dump(payload, f, indent=2)
        return True
    except Exception:
        return False


def load_session():
    """Return (files, active_index). Missing files are filtered out."""
    if not os.path.exists(SESSION_PATH):
        return [], 0
    try:
        with open(SESSION_PATH, "r") as f:
            data = json.load(f)
        files = [f for f in data.get("files", []) if os.path.isfile(f)]
        active = data.get("active_index", 0)
        if not (0 <= active < len(files)):
            active = 0
        return files, active
    except Exception:
        return [], 0


def clear_session():
    try:
        if os.path.exists(SESSION_PATH):
            os.remove(SESSION_PATH)
        return True
    except Exception:
        return False
