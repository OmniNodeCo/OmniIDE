"""Recent files tracking."""

import json
import os
from src.config import RECENT_FILES_PATH, DEFAULT_SETTINGS


class RecentFilesManager:
    """Manages recently opened files list."""

    def __init__(self):
        self.max_files = DEFAULT_SETTINGS["max_recent_files"]
        self.files = self._load()

    def _load(self):
        if os.path.exists(RECENT_FILES_PATH):
            try:
                with open(RECENT_FILES_PATH, "r") as f:
                    data = json.load(f)
                # Filter out files that no longer exist
                return [fp for fp in data if os.path.exists(fp)]
            except Exception:
                pass
        return []

    def _save(self):
        try:
            with open(RECENT_FILES_PATH, "w") as f:
                json.dump(self.files, f, indent=2)
        except Exception:
            pass

    def add(self, filepath):
        """Add a file to recent files list."""
        filepath = os.path.abspath(filepath)
        if filepath in self.files:
            self.files.remove(filepath)
        self.files.insert(0, filepath)
        self.files = self.files[:self.max_files]
        self._save()

    def get_all(self):
        """Return list of recent files."""
        return self.files.copy()

    def clear(self):
        """Clear all recent files."""
        self.files = []
        self._save()