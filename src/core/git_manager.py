"""Git integration — clone, init, status, commit, push, pull."""

import subprocess
import os
import shutil
import threading
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox, simpledialog, filedialog


class GitManager:
    """Manages Git operations for the current project."""

    def __init__(self, app):
        self.app = app
        self.repo_path = None
        self.is_repo = False
        self.git_path = shutil.which("git")
        self.current_branch = ""

    def has_git(self):
        """Check if git is installed."""
        return self.git_path is not None

    def detect_repo(self, path):
        """Detect if a directory is a Git repo."""
        git_dir = os.path.join(path, ".git")
        self.repo_path = path
        self.is_repo = os.path.isdir(git_dir)

        if self.is_repo:
            self.current_branch = self._get_branch()
            self.app.set_status(
                f"Git: {self.current_branch} | {os.path.basename(path)}"
            )
        return self.is_repo

    def _run_git(self, args, cwd=None):
        """Run a git command and return (success, output)."""
        if not self.git_path:
            return False, "Git is not installed."

        work_dir = cwd or self.repo_path or os.getcwd()

        try:
            result = subprocess.run(
                [self.git_path] + args,
                cwd=work_dir,
                capture_output=True,
                text=True,
                timeout=30,
            )
            output = result.stdout + result.stderr
            return result.returncode == 0, output.strip()
        except subprocess.TimeoutExpired:
            return False, "Command timed out."
        except Exception as e:
            return False, str(e)

    def _get_branch(self):
        """Get current branch name."""
        ok, out = self._run_git(["branch", "--show-current"])
        return out.strip() if ok else "unknown"

    # ──────────────────────────────────────
    # Public actions
    # ──────────────────────────────────────

    def clone_repo(self):
        """Clone a remote repository."""
        if not self.has_git():
            messagebox.showerror("Git", "Git is not installed on this system.")
            return

        url = simpledialog.askstring(
            "Clone Repository",
            "Enter repository URL:\n\n"
            "Example: https://github.com/user/repo.git",
            parent=self.app.root,
        )

        if not url:
            return

        dest = filedialog.askdirectory(
            title="Select destination folder",
            parent=self.app.root,
        )

        if not dest:
            return

        self.app.set_status(f"Cloning {url}...")

        def _do_clone():
            ok, out = self._run_git(["clone", url], cwd=dest)
            self.app.root.after(0, lambda: self._on_clone_done(ok, out, dest, url))

        threading.Thread(target=_do_clone, daemon=True).start()

    def _on_clone_done(self, ok, out, dest, url):
        if ok:
            # Find the cloned directory
            repo_name = url.rstrip("/").split("/")[-1].replace(".git", "")
            repo_path = os.path.join(dest, repo_name)

            if os.path.isdir(repo_path):
                self.app.open_project(repo_path)

            self.app.set_status(f"Cloned: {repo_name}")
            messagebox.showinfo("Clone", f"Repository cloned successfully!\n\n{repo_path}")
        else:
            self.app.set_status("Clone failed")
            messagebox.showerror("Clone Failed", out)

    def init_repo(self):
        """Initialize a new Git repo."""
        if not self.has_git():
            messagebox.showerror("Git", "Git is not installed.")
            return

        path = self.app.current_project_path
        if not path:
            messagebox.showwarning("Git", "Open a project folder first.")
            return

        ok, out = self._run_git(["init"], cwd=path)
        if ok:
            self.detect_repo(path)
            self.app.set_status(f"Git initialized in {os.path.basename(path)}")
            messagebox.showinfo("Git Init", "Repository initialized!")
        else:
            messagebox.showerror("Git Init Failed", out)

    def git_status(self):
        """Show git status in a dialog."""
        if not self._check_repo():
            return

        ok, out = self._run_git(["status"])
        self._show_git_dialog("Git Status", out)

    def git_add_all(self):
        """Stage all changes."""
        if not self._check_repo():
            return

        ok, out = self._run_git(["add", "-A"])
        if ok:
            self.app.set_status("All changes staged")
        else:
            messagebox.showerror("Git Add", out)

    def git_commit(self):
        """Commit staged changes."""
        if not self._check_repo():
            return

        msg = simpledialog.askstring(
            "Git Commit",
            "Enter commit message:",
            parent=self.app.root,
        )

        if not msg:
            return

        ok, out = self._run_git(["commit", "-m", msg])
        if ok:
            self.app.set_status(f"Committed: {msg[:50]}")
            messagebox.showinfo("Commit", f"Committed successfully!\n\n{out}")
        else:
            messagebox.showerror("Commit Failed", out)

    def git_push(self):
        """Push to remote."""
        if not self._check_repo():
            return

        self.app.set_status("Pushing...")

        def _do_push():
            ok, out = self._run_git(["push"])
            self.app.root.after(0, lambda: self._on_push_done(ok, out))

        threading.Thread(target=_do_push, daemon=True).start()

    def _on_push_done(self, ok, out):
        if ok:
            self.app.set_status("Push successful")
            messagebox.showinfo("Push", "Pushed successfully!")
        else:
            self.app.set_status("Push failed")
            messagebox.showerror("Push Failed", out)

    def git_pull(self):
        """Pull from remote."""
        if not self._check_repo():
            return

        self.app.set_status("Pulling...")

        def _do_pull():
            ok, out = self._run_git(["pull"])
            self.app.root.after(0, lambda: self._on_pull_done(ok, out))

        threading.Thread(target=_do_pull, daemon=True).start()

    def _on_pull_done(self, ok, out):
        if ok:
            self.app.set_status("Pull successful")
            messagebox.showinfo("Pull", f"Pulled successfully!\n\n{out}")
            # Refresh file tree
            if self.app.current_project_path:
                self.app.sidebar.file_tree.load_directory(
                    self.app.current_project_path
                )
        else:
            self.app.set_status("Pull failed")
            messagebox.showerror("Pull Failed", out)

    def git_log(self):
        """Show recent git log."""
        if not self._check_repo():
            return

        ok, out = self._run_git([
            "log", "--oneline", "--graph", "--decorate", "-20"
        ])
        self._show_git_dialog("Git Log (last 20)", out)

    def git_branch(self):
        """Show branches."""
        if not self._check_repo():
            return

        ok, out = self._run_git(["branch", "-a"])
        self._show_git_dialog("Git Branches", out)

    def git_diff(self):
        """Show diff."""
        if not self._check_repo():
            return

        ok, out = self._run_git(["diff", "--stat"])
        if not out.strip():
            out = "(No changes)"
        self._show_git_dialog("Git Diff", out)

    def add_remote(self):
        """Add a remote origin."""
        if not self._check_repo():
            return

        url = simpledialog.askstring(
            "Add Remote",
            "Enter remote URL:\n\n"
            "Example: https://github.com/user/repo.git",
            parent=self.app.root,
        )

        if not url:
            return

        ok, out = self._run_git(["remote", "add", "origin", url])
        if ok:
            self.app.set_status(f"Remote added: {url}")
            messagebox.showinfo("Remote", f"Remote 'origin' added!\n{url}")
        else:
            # Maybe origin already exists, try set-url
            ok2, out2 = self._run_git(["remote", "set-url", "origin", url])
            if ok2:
                self.app.set_status(f"Remote updated: {url}")
                messagebox.showinfo("Remote", f"Remote 'origin' updated!\n{url}")
            else:
                messagebox.showerror("Remote Failed", f"{out}\n{out2}")

    # ──────────────────────────────────────
    # Helpers
    # ──────────────────────────────────────

    def _check_repo(self):
        """Verify we're in a git repo."""
        if not self.has_git():
            messagebox.showerror("Git", "Git is not installed.")
            return False
        if not self.is_repo:
            messagebox.showwarning(
                "Git",
                "Not a Git repository.\nUse Git > Init to create one."
            )
            return False
        return True

    def _show_git_dialog(self, title, content):
        """Show a dialog with git output."""
        dialog = tk.Toplevel(self.app.root)
        dialog.title(title)
        dialog.geometry("600x400")
        dialog.transient(self.app.root)
        dialog.grab_set()

        text = tk.Text(
            dialog,
            font=("Consolas", 11),
            bg=self.app.colors["terminal_bg"],
            fg=self.app.colors["terminal_fg"],
            relief="flat",
            padx=12,
            pady=8,
            wrap="word",
        )
        text.pack(fill=BOTH, expand=True)
        text.insert("1.0", content)
        text.configure(state="disabled")

        ttk.Button(
            dialog, text="Close",
            bootstyle="secondary",
            command=dialog.destroy,
            padding=(16, 6),
        ).pack(pady=8)