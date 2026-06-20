"""Top toolbar — VS Code style with round icon+text buttons."""

import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from src.utils.icon_manager import IconManager
from src.utils.styles import make_round_btn, make_icon_btn


class Toolbar:
    """Top action toolbar."""

    def __init__(self, parent, app):
        self.app = app
        self.icon_mgr = IconManager()
        self._icon_refs = []

        self.frame = ttk.Frame(parent, padding=(8, 4, 8, 4))

        # File group
        self._btn("new_file", "New", app.file_manager.new_file, "info")
        self._btn("open_file", "Open", app.file_manager.open_file, "info")
        self._btn("save", "Save", app.file_manager.save_file, "success")

        self._sep()

        # Edit
        self._btn("search", "Find", app.toggle_search, "warning")

        self._sep()

        # View
        self._btn("theme", "Theme", app.switch_theme, "secondary")
        self._btn("settings", "Settings", lambda: app.open_settings(), "secondary")

        # Right-aligned
        spacer = ttk.Frame(self.frame)
        spacer.pack(side=LEFT, fill=X, expand=True)

        # Command palette button on the right
        self._btn("terminal", "Palette", lambda: app.toggle_command_palette(), "info", side=RIGHT)

    def _btn(self, icon_name, text, command, style, side=LEFT):
        icon = self.icon_mgr.get(icon_name, 14)
        self._icon_refs.append(icon)

        btn = make_round_btn(
            self.frame, text, icon, command, style,
            self._icon_refs, size="small",
        )
        btn.pack(side=side, padx=2)

    def _sep(self):
        ttk.Separator(self.frame, orient=VERTICAL).pack(
            side=LEFT, fill=tk.Y, padx=8, pady=3
        )