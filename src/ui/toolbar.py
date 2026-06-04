"""Top toolbar with properly hovering round buttons."""

import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from src.utils.icon_manager import IconManager
from src.utils.styles import make_round_btn


class Toolbar:
    """Top action toolbar."""

    def __init__(self, parent, app):
        self.app = app
        self.icon_mgr = IconManager()
        self._icon_refs = []

        self.frame = ttk.Frame(parent, padding=(6, 4))

        make_round_btn(
            self.frame, "New",
            self.icon_mgr.get("new_file", 14),
            app.file_manager.new_file, "info",
            self._icon_refs,
        ).pack(side=LEFT, padx=2)

        make_round_btn(
            self.frame, "Open",
            self.icon_mgr.get("open_file", 14),
            app.file_manager.open_file, "info",
            self._icon_refs,
        ).pack(side=LEFT, padx=2)

        make_round_btn(
            self.frame, "Save",
            self.icon_mgr.get("save", 14),
            app.file_manager.save_file, "success",
            self._icon_refs,
        ).pack(side=LEFT, padx=2)

        self._sep()

        make_round_btn(
            self.frame, "Find",
            self.icon_mgr.get("search", 14),
            app.toggle_search, "warning",
            self._icon_refs,
        ).pack(side=LEFT, padx=2)

        self._sep()

        make_round_btn(
            self.frame, "Theme",
            self.icon_mgr.get("theme", 14),
            app.switch_theme, "secondary",
            self._icon_refs,
        ).pack(side=LEFT, padx=2)

    def _sep(self):
        ttk.Separator(self.frame, orient=VERTICAL).pack(
            side=LEFT, fill=tk.Y, padx=8, pady=3
        )