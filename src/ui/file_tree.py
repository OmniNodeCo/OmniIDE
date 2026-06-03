"""File tree explorer widget."""

import os
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *


class FileTree:
    """Treeview file explorer."""

    IGNORE_DIRS = {
        "__pycache__", ".git", ".svn", "node_modules",
        ".venv", "venv", ".idea", ".vscode", ".DS_Store",
        "dist", "build", ".eggs", "*.egg-info",
    }

    FILE_ICONS = {
        ".py": "🐍", ".js": "📜", ".ts": "📘", ".html": "🌐",
        ".css": "🎨", ".json": "📋", ".md": "📝", ".txt": "📄",
        ".yml": "⚙️", ".yaml": "⚙️", ".xml": "📰", ".sql": "🗃️",
        ".sh": "⚡", ".bat": "⚡", ".c": "©️", ".cpp": "©️",
        ".java": "☕", ".rb": "💎", ".go": "🔵", ".rs": "🦀",
        ".php": "🐘", ".toml": "⚙️", ".ini": "⚙️", ".cfg": "⚙️",
    }

    def __init__(self, parent, app):
        self.app = app
        self.frame = ttk.Frame(parent)

        self.tree = ttk.Treeview(
            self.frame,
            show="tree",
            selectmode="browse",
        )
        self.tree.pack(fill=BOTH, expand=True)

        scrollbar = ttk.Scrollbar(self.frame, orient=VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=RIGHT, fill=Y)

        self.tree.bind("<Double-1>", self._on_double_click)
        self.tree.bind("<Return>", self._on_double_click)

    def load_directory(self, path):
        """Load a directory into the tree."""
        self.tree.delete(*self.tree.get_children())
        self._insert_node("", path, os.path.basename(path))

    def _insert_node(self, parent, path, name, depth=0):
        if depth > 5:  # Limit recursion depth
            return

        if os.path.isdir(path):
            node = self.tree.insert(parent, "end", text=f"📁 {name}", values=(path,))
            try:
                entries = sorted(
                    os.listdir(path),
                    key=lambda x: (not os.path.isdir(os.path.join(path, x)), x.lower()),
                )
                for entry in entries:
                    if entry in self.IGNORE_DIRS or entry.startswith("."):
                        continue
                    full_path = os.path.join(path, entry)
                    self._insert_node(node, full_path, entry, depth + 1)
            except PermissionError:
                pass
        else:
            ext = os.path.splitext(name)[1].lower()
            icon = self.FILE_ICONS.get(ext, "📄")
            self.tree.insert(parent, "end", text=f"{icon} {name}", values=(path,))

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
            # Toggle open/close
            if self.tree.item(item, "open"):
                self.tree.item(item, open=False)
            else:
                self.tree.item(item, open=True)