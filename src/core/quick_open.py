"""Project file index for Quick Open (Ctrl+P).

Walks the project directory once, caches the file list, and supports
fuzzy ranking. Pure Python — no Qt imports.
"""

from __future__ import annotations

import os

from src.core.fuzzy import rank as fuzzy_rank

# Directories that are never useful in Quick Open
IGNORED_DIRS = {
    ".git", ".svn", ".hg", "node_modules", "__pycache__", ".venv",
    "venv", ".tox", ".nox", ".mypy_cache", ".pytest_cache", ".ruff_cache",
    ".idea", ".vscode", ".eggs", "dist", "build", "out", "target",
    ".next", ".nuxt", ".output", ".parcel-cache", ".svelte-kit",
    "coverage", ".cache", ".npm", ".yarn",
}

IGNORED_EXTS = {
    ".png", ".jpg", ".jpeg", ".gif", ".ico", ".bmp", ".webp", ".tiff",
    ".woff", ".woff2", ".ttf", ".eot", ".otf",
    ".pdf", ".zip", ".gz", ".tar", ".7z", ".rar",
    ".pyc", ".pyo", ".class", ".o", ".obj", ".a", ".so", ".dll",
    ".exe", ".bin", ".dat", ".wasm", ".mp3", ".mp4", ".wav", ".avi",
    ".mov", ".psd", ".ai", ".sketch", ".exe",
}

MAX_FILES = 20000


class QuickOpenIndex:
    """Cached, ranked file index for a project directory."""

    def __init__(self):
        self.root = None
        self.files = []  # list of absolute paths

    def needs_refresh(self, root):
        return self.root != root or not os.path.isdir(root or "")

    def refresh(self, root):
        """(Re)build the index for ``root``."""
        if not root or not os.path.isdir(root):
            self.root = None
            self.files = []
            return self.files

        root = os.path.abspath(root)
        files = []
        for dirpath, dirnames, filenames in os.walk(root):
            # In-place prune of ignored dirs (keeps os.walk fast)
            dirnames[:] = [
                d for d in dirnames
                if d not in IGNORED_DIRS and not d.endswith(".egg-info")
            ]
            rel_dir = os.path.relpath(dirpath, root)
            for name in filenames:
                if name in IGNORED_DIRS or name.startswith("."):
                    continue
                ext = os.path.splitext(name)[1].lower()
                if ext in IGNORED_EXTS:
                    continue
                full = os.path.join(dirpath, name)
                # Skip huge files (> 2 MB) — not sensible to quick-open
                try:
                    if os.path.getsize(full) > 2_000_000:
                        continue
                except OSError:
                    continue
                files.append(full)
                if len(files) >= MAX_FILES:
                    break
            if len(files) >= MAX_FILES:
                break

        self.root = root
        self.files = files
        return files

    def query(self, query: str, limit: int = 50):
        """Fuzzy-search the index. Returns [(path, rel_path, score)]."""
        root = self.root or ""
        results = fuzzy_rank(self.files, lambda p: p, query, limit)
        out = []
        for path, s in results:
            rel = os.path.relpath(path, root) if root else path
            out.append((path, rel, s))
        return out
