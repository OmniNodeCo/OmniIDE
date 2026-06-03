"""Top toolbar with modern buttons and Git actions."""

import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from src.utils.icon_manager import IconManager


class Toolbar:
    """Top action toolbar with modern styled buttons."""

    def __init__(self, parent, app):
        self.app = app
        self.icon_mgr = IconManager()
        self._icon_refs = []

        self.frame = ttk.Frame(parent, padding=(6, 4))

        # ── File actions ──
        self._add_btn("new_file", "New", app.file_manager.new_file, "info")
        self._add_btn("open_file", "Open", app.file_manager.open_file, "info")
        self._add_btn("save", "Save", app.file_manager.save_file, "success")

        self._add_sep()

        # ── Edit actions ──
        self._add_btn("search", "Find", app.toggle_search, "warning")

        self._add_sep()

        # ── Git actions ──
        self._add_btn("folder_git", "Clone", app.git_manager.clone_repo, "danger")
        self._add_btn("success", "Commit", app.git_manager.git_commit, "success")
        self._add_btn("arrow_right", "Push", app.git_manager.git_push, "info")
        self._add_btn("arrow_left", "Pull", app.git_manager.git_pull, "info")

        self._add_sep()

        # ── View ──
        self._add_btn("theme", "Theme", app.switch_theme, "secondary")

    def _add_btn(self, icon_name, text, command, style):
        """Add a modern styled button."""
        icon = self.icon_mgr.get(icon_name, 16)
        self._icon_refs.append(icon)

        btn = ttk.Button(
            self.frame,
            text=f" {text}",
            image=icon,
            compound=LEFT,
            command=command,
            bootstyle=f"{style}-outline",
            padding=(10, 5),
        )
        btn.pack(side=LEFT, padx=2)

        # Hover effects
        original_style = f"{style}-outline"
        hover_style = style

        def on_enter(e, b=btn, s=hover_style):
            b.configure(bootstyle=s)

        def on_leave(e, b=btn, s=original_style):
            b.configure(bootstyle=s)

        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)

    def _add_sep(self):
        """Add a vertical separator."""
        ttk.Separator(self.frame, orient=VERTICAL).pack(
            side=LEFT, fill=tk.Y, padx=8, pady=2
        )