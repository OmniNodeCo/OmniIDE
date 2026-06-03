"""Sidebar panel with file tree and SVG icons."""

import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from src.ui.file_tree import FileTree
from src.utils.icon_manager import IconManager


class Sidebar:
    """Left sidebar with explorer."""

    def __init__(self, parent, app):
        self.app = app
        self.visible = True
        self.icon_mgr = IconManager()
        self._icon_refs = []

        self.frame = ttk.Frame(parent, width=app.settings["sidebar_width"])
        self.frame.pack_propagate(False)

        # Header
        header = ttk.Frame(self.frame)
        header.pack(fill=X, padx=8, pady=(8, 4))

        explorer_icon = self.icon_mgr.get("explorer", 16)
        self._icon_refs.append(explorer_icon)

        ttk.Label(
            header,
            text=" EXPLORER",
            image=explorer_icon,
            compound=LEFT,
            font=("Segoe UI", 10, "bold"),
        ).pack(side=LEFT)

        open_icon = self.icon_mgr.get("open_file", 16)
        self._icon_refs.append(open_icon)

        ttk.Button(
            header,
            image=open_icon,
            bootstyle="info-link",
            command=app.open_project,
        ).pack(side=RIGHT)

        ttk.Separator(self.frame).pack(fill=X, padx=8, pady=4)

        # Quick actions
        actions = ttk.Frame(self.frame)
        actions.pack(fill=X, padx=8, pady=(0, 4))

        new_icon = self.icon_mgr.get("new_file", 16)
        self._icon_refs.append(new_icon)

        ttk.Button(
            actions,
            text=" New File",
            image=new_icon,
            compound=LEFT,
            bootstyle="success-outline",
            command=app.file_manager.new_file,
        ).pack(fill=X, pady=1)

        file_icon = self.icon_mgr.get("file", 16)
        self._icon_refs.append(file_icon)

        ttk.Button(
            actions,
            text=" Open File",
            image=file_icon,
            compound=LEFT,
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