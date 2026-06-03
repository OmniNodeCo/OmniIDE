"""Status bar with Git branch display."""

import os
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from src.config import SUPPORTED_EXTENSIONS, APP_NAME, APP_VERSION

from src.utils.icon_manager import IconManager


class StatusBar:
    """Bottom status bar with Git info."""

    def __init__(self, parent, app):
        self.app = app
        self.icon_mgr = IconManager()
        self._icon_refs = []

        self.frame = ttk.Frame(parent, padding=(4, 2))

        # Left — status message
        info_icon = self.icon_mgr.get("info", 12)
        self._icon_refs.append(info_icon)

        self.status_label = ttk.Label(
            self.frame,
            text=f"  {APP_NAME} v{APP_VERSION} — Ready",
            image=info_icon,
            compound=LEFT,
            font=("Segoe UI", 9),
            style="Status.TLabel",
        )
        self.status_label.pack(side=LEFT)

        # Right — cursor position
        self.cursor_label = ttk.Label(
            self.frame,
            text="Ln 1, Col 1  ",
            font=("Segoe UI", 9),
            style="Status.TLabel",
        )
        self.cursor_label.pack(side=RIGHT)

        # File type
        self.filetype_label = ttk.Label(
            self.frame,
            text="  Text  ",
            font=("Segoe UI", 9),
            style="Status.TLabel",
        )
        self.filetype_label.pack(side=RIGHT, padx=(0, 12))

        # Encoding
        self.encoding_label = ttk.Label(
            self.frame,
            text="  UTF-8  ",
            font=("Segoe UI", 9),
            style="Status.TLabel",
        )
        self.encoding_label.pack(side=RIGHT, padx=(0, 12))

        # Git branch
        git_icon = self.icon_mgr.get("folder_git", 12)
        self._icon_refs.append(git_icon)

        self.git_label = ttk.Label(
            self.frame,
            text="",
            image=git_icon,
            compound=LEFT,
            font=("Segoe UI", 9),
            style="Status.TLabel",
        )
        self.git_label.pack(side=RIGHT, padx=(0, 12))

    def set_text(self, text):
        self.status_label.configure(text=f"  {text}")

    def update_cursor_position(self, editor):
        try:
            pos = editor.index("insert")
            line, col = pos.split(".")
            self.cursor_label.configure(text=f"Ln {line}, Col {int(col) + 1}  ")
        except Exception:
            pass

    def update_file_type(self, filepath):
        if filepath:
            ext = os.path.splitext(filepath)[1].lower()
            lang = SUPPORTED_EXTENSIONS.get(ext, "Text")
            self.filetype_label.configure(text=f"  {lang}  ")
        else:
            self.filetype_label.configure(text="  Text  ")

    def update_git_branch(self, branch):
        """Update the Git branch display."""
        if branch:
            self.git_label.configure(text=f" {branch}")
        else:
            self.git_label.configure(text="")