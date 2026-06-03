"""Sidebar panel with file tree and actions."""

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from src.ui.file_tree import FileTree


class Sidebar:
    """Left sidebar with explorer."""

    def __init__(self, parent, app):
        self.app = app
        self.visible = True

        self.frame = ttk.Frame(parent, width=app.settings["sidebar_width"])
        self.frame.pack_propagate(False)

        # Header
        header = ttk.Frame(self.frame)
        header.pack(fill=X, padx=8, pady=(8, 4))

        ttk.Label(
            header,
            text="📁 EXPLORER",
            font=("Segoe UI", 10, "bold"),
        ).pack(side=LEFT)

        ttk.Button(
            header, text="📂",
            bootstyle="info-link",
            command=app.open_project,
        ).pack(side=RIGHT)

        # Separator
        ttk.Separator(self.frame).pack(fill=X, padx=8, pady=4)

        # Quick actions
        actions = ttk.Frame(self.frame)
        actions.pack(fill=X, padx=8, pady=(0, 4))

        ttk.Button(
            actions, text="+ New File",
            bootstyle="success-outline",
            command=app.file_manager.new_file,
        ).pack(fill=X, pady=1)

        ttk.Button(
            actions, text="📄 Open File",
            bootstyle="info-outline",
            command=app.file_manager.open_file,
        ).pack(fill=X, pady=1)

        ttk.Separator(self.frame).pack(fill=X, padx=8, pady=4)

        # File tree
        self.file_tree = FileTree(self.frame, app)
        self.file_tree.frame.pack(fill=BOTH, expand=True, padx=4, pady=4)

    def toggle(self):
        if self.visible:
            self.frame.pack_forget()
            self.visible = False
        else:
            self.frame.pack(side=LEFT, fill=Y)
            self.visible = True