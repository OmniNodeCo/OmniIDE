"""File tree explorer with SVG icons."""

import os
import tkinter as tk
import tkinter.ttk as tkttk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from src.utils.icon_manager import (
    IconManager,
    get_file_icon_name,
    get_folder_icon_name,
)


class FileTree:
    """Treeview file explorer with SVG icons."""

    IGNORE = {
        "__pycache__", ".git", ".svn", "node_modules",
        ".venv", "venv", ".idea", ".vscode", ".DS_Store",
        "dist", "build", ".eggs",
    }

    def __init__(self, parent, app):
        self.app = app
        self.icon_mgr = IconManager()
        self._icon_refs = []  # prevent garbage collection

        self.frame = ttk.Frame(parent)

        self.tree = tkttk.Treeview(
            self.frame,
            show="tree",
            selectmode="browse",
        )
        self.tree.pack(side=LEFT, fill=BOTH, expand=True)

        scrollbar = tkttk.Scrollbar(
            self.frame, orient=tk.VERTICAL, command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=RIGHT, fill=tk.Y)

        self.tree.bind("<Double-1>", self._on_double_click)
        self.tree.bind("<Return>", self._on_double_click)

    def _get_icon(self, name, size=16):
        """Get an icon image and keep a reference so it's not garbage collected."""
        img = self.icon_mgr.get(name, size)
        self._icon_refs.append(img)
        return img

    def load_directory(self, path):
        """Load a directory into the tree."""
        self.tree.delete(*self.tree.get_children())
        self._icon_refs.clear()
        root_icon = self._get_icon("folder_open")
        self._insert_node(
            "", path, os.path.basename(path), icon=root_icon
        )

    def _insert_node(self, parent, path, name, depth=0, icon=None):
        if depth > 5:
            return

        if os.path.isdir(path):
            folder_icon_name = get_folder_icon_name(name, is_open=False)
            dir_icon = icon or self._get_icon(folder_icon_name)

            node = self.tree.insert(
                parent, "end",
                text=f" {name}",
                image=dir_icon,
                values=(path,),
            )

            try:
                entries = sorted(
                    os.listdir(path),
                    key=lambda x: (
                        not os.path.isdir(os.path.join(path, x)),
                        x.lower(),
                    ),
                )
                for entry in entries:
                    if entry in self.IGNORE or entry.startswith("."):
                        continue
                    full_path = os.path.join(path, entry)
                    self._insert_node(node, full_path, entry, depth + 1)
            except PermissionError:
                pass
        else:
            file_icon_name = get_file_icon_name(name)
            file_icon = self._get_icon(file_icon_name)

            self.tree.insert(
                parent, "end",
                text=f" {name}",
                image=file_icon,
                values=(path,),
            )

    def _on_double_click(self, event=None):
        selection = self.tree.selection()
        if not selection:
            return

        item = selection[0]
        values = self.tree.item(item, "values")
        if not values:
            return

        filepath = values[0]
        if os.path.isfile(filepath):
            self.app.file_manager.open_file(filepath)
        elif os.path.isdir(filepath):
            if self.tree.item(item, "open"):
                self.tree.item(item, open=False)
            else:
                self.tree.item(item, open=True)