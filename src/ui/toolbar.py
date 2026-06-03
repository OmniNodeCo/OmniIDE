"""Top toolbar with SVG icon buttons."""

import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from src.utils.icon_manager import IconManager


class Toolbar:
    """Top action toolbar with SVG icons."""

    def __init__(self, parent, app):
        self.app = app
        self.icon_mgr = IconManager()
        self._icon_refs = []

        self.frame = ttk.Frame(parent, padding=(4, 2))

        buttons = [
            ("new_file", "New", app.file_manager.new_file, "info-outline"),
            ("open_file", "Open", app.file_manager.open_file, "info-outline"),
            ("save", "Save", app.file_manager.save_file, "success-outline"),
            (None, None, None, None),  # separator
            ("search", "Find", app.toggle_search, "warning-outline"),
            (None, None, None, None),
            ("theme", "Theme", app.switch_theme, "secondary-outline"),
        ]

        for icon_name, text, command, style in buttons:
            if icon_name is None:
                ttk.Separator(self.frame, orient=VERTICAL).pack(
                    side=LEFT, fill=tk.Y, padx=6, pady=2
                )
            else:
                icon = self.icon_mgr.get(icon_name, 16)
                self._icon_refs.append(icon)

                btn = ttk.Button(
                    self.frame,
                    text=f" {text}",
                    image=icon,
                    compound=LEFT,
                    command=command,
                    bootstyle=style,
                    padding=(8, 4),
                )
                btn.pack(side=LEFT, padx=2)