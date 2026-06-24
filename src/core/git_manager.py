"""Git operations — PyQt6 dialogs."""

import subprocess
import os
import shutil
import threading

from PyQt6.QtWidgets import QMessageBox, QInputDialog, QFileDialog, QDialog, QVBoxLayout, QPlainTextEdit, QPushButton


class GitManager:
    def __init__(self, app):
        self.app = app
        self.repo_path = None
        self.is_repo = False
        self.git_path = shutil.which("git")
        self.current_branch = ""

    def has_git(self):
        return self.git_path is not None

    def detect_repo(self, path):
        self.repo_path = path
        self.is_repo = os.path.isdir(os.path.join(path, ".git"))
        if self.is_repo:
            self.current_branch = self._get_branch()
            self.app.statusbar.update_git_branch(self.current_branch)
        return self.is_repo

    def _run(self, args, cwd=None):
        if not self.git_path:
            return False, "Git not installed."
        try:
            r = subprocess.run(
                [self.git_path] + args,
                cwd=cwd or self.repo_path or os.getcwd(),
                capture_output=True, text=True, timeout=30,
            )
            return r.returncode == 0, (r.stdout + r.stderr).strip()
        except Exception as e:
            return False, str(e)

    def _get_branch(self):
        ok, out = self._run(["branch", "--show-current"])
        return out.strip() if ok else "unknown"

    def _check(self):
        if not self.has_git():
            QMessageBox.warning(self.app, "Git", "Git not installed.")
            return False
        if not self.is_repo:
            QMessageBox.warning(self.app, "Git", "Not a Git repo. Use Init first.")
            return False
        return True

    def _show_output(self, title, text):
        d = QDialog(self.app)
        d.setWindowTitle(title)
        d.resize(600, 400)
        layout = QVBoxLayout(d)
        t = QPlainTextEdit()
        t.setPlainText(text)
        t.setReadOnly(True)
        layout.addWidget(t)
        btn = QPushButton("Close")
        btn.clicked.connect(d.accept)
        layout.addWidget(btn)
        d.exec()

    def clone_repo(self):
        if not self.has_git():
            QMessageBox.warning(self.app, "Git", "Git not installed.")
            return
        url, ok = QInputDialog.getText(self.app, "Clone", "Repository URL:")
        if not ok or not url:
            return
        dest = QFileDialog.getExistingDirectory(self.app, "Destination")
        if not dest:
            return
        self.app.set_status(f"Cloning {url}...")

        def _do():
            ok, out = self._run(["clone", url], cwd=dest)
            if ok:
                repo_name = url.rstrip("/").split("/")[-1].replace(".git", "")
                repo_path = os.path.join(dest, repo_name)
                if os.path.isdir(repo_path):
                    self.app.open_project(repo_path)
                self.app.set_status(f"Cloned: {repo_name}")
            else:
                self.app.set_status("Clone failed")
                QMessageBox.warning(self.app, "Clone Failed", out)

        threading.Thread(target=_do, daemon=True).start()

    def init_repo(self):
        if not self.has_git():
            QMessageBox.warning(self.app, "Git", "Git not installed.")
            return
        path = self.app.current_project_path
        if not path:
            QMessageBox.warning(self.app, "Git", "Open a folder first.")
            return
        ok, out = self._run(["init"], cwd=path)
        if ok:
            self.detect_repo(path)
            self.app.set_status("Git initialized")
        else:
            QMessageBox.warning(self.app, "Init Failed", out)

    def git_status(self):
        if not self._check(): return
        ok, out = self._run(["status"])
        self._show_output("Git Status", out)

    def git_diff(self):
        if not self._check(): return
        ok, out = self._run(["diff", "--stat"])
        self._show_output("Git Diff", out or "(No changes)")

    def git_add_all(self):
        if not self._check(): return
        ok, out = self._run(["add", "-A"])
        self.app.set_status("Staged all" if ok else "Stage failed")

    def git_commit(self):
        if not self._check(): return
        msg, ok = QInputDialog.getText(self.app, "Commit", "Message:")
        if not ok or not msg: return
        ok, out = self._run(["commit", "-m", msg])
        self.app.set_status(f"Committed: {msg[:40]}" if ok else "Commit failed")
        if not ok:
            QMessageBox.warning(self.app, "Commit Failed", out)

    def git_push(self):
        if not self._check(): return
        self.app.set_status("Pushing...")
        def _do():
            ok, out = self._run(["push"])
            self.app.set_status("Pushed" if ok else "Push failed")
        threading.Thread(target=_do, daemon=True).start()

    def git_pull(self):
        if not self._check(): return
        self.app.set_status("Pulling...")
        def _do():
            ok, out = self._run(["pull"])
            self.app.set_status("Pulled" if ok else "Pull failed")
        threading.Thread(target=_do, daemon=True).start()

    def git_log(self):
        if not self._check(): return
        ok, out = self._run(["log", "--oneline", "--graph", "-20"])
        self._show_output("Git Log", out)

    def git_branch(self):
        if not self._check(): return
        ok, out = self._run(["branch", "-a"])
        self._show_output("Branches", out)

    def add_remote(self):
        if not self._check(): return
        url, ok = QInputDialog.getText(self.app, "Remote", "Remote URL:")
        if not ok or not url: return
        ok, out = self._run(["remote", "add", "origin", url])
        if not ok:
            ok, out = self._run(["remote", "set-url", "origin", url])
        self.app.set_status("Remote set" if ok else "Remote failed")