"""Top toolbar with action buttons."""

import ttkbootstrap as ttk
from ttkbootstrap.constants import *


class Toolbar:
    """Top action toolbar."""

    def __init__(self, parent, app):
        self.app = app
        self.frame = ttk.Frame(parent, padding=(4, 2))

        buttons = [
            ("📄 New", app.file_manager.new_file, "info-outline"),
            ("📂 Open", app.file_manager.open_file, "info-outline"),
            ("💾 Save", app.file_manager.save_file, "success-outline"),
            ("|", None, None),
            ("🔍 Find", app.toggle_search, "warning-outline"),
            ("|", None, None),
            ("🌙 Theme", app.switch_theme, "secondary-outline"),
        ]

        for text, command, style in buttons:
            if text == "|":
                ttk.Separator(self.frame, orient=VERTICAL).pack(
                    side=LEFT, fill=Y, padx=6, pady=2
                )
            else:
                btn = ttk.Button(
                    self.frame,
                    text=text,
                    command=command,
                    bootstyle=style,
                    padding=(8, 4),
                )
                btn.pack(side=LEFT, padx=2)