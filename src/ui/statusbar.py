"""Status bar at the bottom of the window."""

import os
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from src.config import SUPPORTED_EXTENSIONS, APP_NAME, APP_VERSION


class StatusBar:
    """Bottom status bar."""

    def __init__(self, parent, app):
        self.app = app

        self.frame = ttk.Frame(parent, padding=(4, 2))

        # Left side - status message
        self.status_label = ttk.Label(
            self.frame,
            text=f"  {APP_NAME} v{APP_VERSION} — Ready",
            font=("Segoe UI", 9),
            style="Status.TLabel",
        )
        self.status_label.pack(side=LEFT)

        # Right side - cursor position
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