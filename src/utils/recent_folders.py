"""Recent folders (projects) tracking."""

import json
import os

from src.config import CONFIG_DIR

RECENT_FOLDERS_PATH = os.path.join(CONFIG_DIR, "recent_folders.json")
MAX_FOLDERS = 10


class RecentFolders:
    """Tracks recently opened project folders."""

    def __init__(self, max_folders=MAX_FOLDERS):
        self.max_folders = max_folders
        self.folders = self._load()

    def _load(self):
        if os.path.exists(RECENT_FOLDERS_PATH):
            try:
                with open(RECENT_FOLDERS_PATH, "r") as f:
                    data = json.load(f)
                return [fp for fp in data if os.path.isdir(fp)]
            except Exception:
                pass
        return []

    def _save(self):
        try:
            with open(RECENT_FOLDERS_PATH, "w") as f:
                json.dump(self.folders, f, indent=2)
        except Exception:
            pass

    def add(self, folder):
        folder = os.path.abspath(folder)
        if not os.path.isdir(folder):
            return
        if folder in self.folders:
            self.folders.remove(folder)
        self.folders.insert(0, folder)
        self.folders = self.folders[: self.max_folders]
        self._save()

    def get_all(self):
        return self.folders.copy()

    def clear(self):
        self.folders = []
        self._save()
