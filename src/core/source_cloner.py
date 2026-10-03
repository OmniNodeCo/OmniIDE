"""Clone external base source trees (VS Code) into the user's machine.

The actual ``git clone`` runs in a daemon thread; progress and results
are posted back to the Qt main thread via signals (same pattern as the
extension manager).
"""

import os
import shutil
import subprocess
import threading

from PyQt6.QtCore import QObject, pyqtSignal

# Base source repositories OmniIDE can clone
SOURCE_REPOS = {
    "vscode": {
        "label": "VS Code (microsoft/vscode)",
        "url": "https://github.com/microsoft/vscode.git",
        "default_name": "vscode",
    },
}


def build_clone_command(git_path, url, dest, depth=1):
    """Build the git clone argv for a shallow base-source clone."""
    return [git_path, "clone", "--depth", str(depth), url, dest]


def validate_destination(base_dir, repo_name):
    """Return (ok, final_dest, error_message).

    Ensures base_dir exists and the target folder is free.
    """
    if not base_dir or not os.path.isdir(base_dir):
        return False, None, "Destination folder does not exist."
    dest = os.path.join(base_dir, repo_name)
    if os.path.exists(dest):
        return False, None, f"'{repo_name}' already exists in {base_dir}."
    return True, dest, None


class CloneSignals(QObject):
    status = pyqtSignal(str)
    finished = pyqtSignal(bool, str)   # (ok, message_or_path)


class SourceCloner:
    """Clones a base source repo (VS Code) with progress callbacks."""

    def __init__(self, git_path=None):
        self.git_path = git_path or shutil.which("git")
        self.signals = CloneSignals()

    def has_git(self):
        return self.git_path is not None

    def start(self, repo_key, dest_dir, depth=1):
        """Start cloning in a worker thread.

        ``dest_dir`` is the parent folder; the repo folder name is added.
        Emits signals.status(str) and signals.finished(bool, str).
        """
        repo = SOURCE_REPOS.get(repo_key)
        if repo is None:
            self.signals.finished.emit(False, f"Unknown repo: {repo_key}")
            return False

        ok, dest, err = validate_destination(dest_dir, repo["default_name"])
        if not ok:
            self.signals.finished.emit(False, err)
            return False

        cmd = build_clone_command(self.git_path, repo["url"], dest, depth)

        def _worker():
            try:
                self.signals.status.emit(
                    f"Cloning {repo['label']} (shallow, depth {depth})...")
                proc = subprocess.run(
                    cmd, capture_output=True, text=True, timeout=3600,
                )
                if proc.returncode == 0:
                    size = self._folder_size(dest)
                    self.signals.finished.emit(
                        True,
                        f"{dest} ({self._human(size)})",
                    )
                else:
                    tail = (proc.stderr or proc.stdout or "").strip()[-400:]
                    self.signals.finished.emit(False, tail or "Clone failed.")
            except subprocess.TimeoutExpired:
                self.signals.finished.emit(False, "Clone timed out.")
            except Exception as e:
                self.signals.finished.emit(False, str(e))

        threading.Thread(target=_worker, daemon=True).start()
        return True

    @staticmethod
    def _folder_size(path):
        total = 0
        for dirpath, _dirnames, filenames in os.walk(path):
            for name in filenames:
                try:
                    total += os.path.getsize(os.path.join(dirpath, name))
                except OSError:
                    continue
        return total

    @staticmethod
    def _human(n):
        for unit in ("B", "KB", "MB", "GB"):
            if n < 1024 or unit == "GB":
                return f"{n:.0f} {unit}" if unit == "B" else f"{n:.1f} {unit}"
            n /= 1024
