"""Tab manager for multiple open files."""

import tkinter as tk
import tkinter.ttk as tkttk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import os

from src.core.editor import CodeEditor, LineNumbers


class TabManager:
    """Manages editor tabs."""

    def __init__(self, parent, app):
        self.app = app
        self.tabs = {}
        self.tab_counter = 0

        self.frame = ttk.Frame(parent)

        # Use ttkbootstrap Notebook — this one IS available
        self.notebook = ttk.Notebook(self.frame)
        self.notebook.pack(fill=BOTH, expand=True)
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)

    def new_tab(self, filepath=None, content="", title=None):
        """Create a new editor tab."""
        self.tab_counter += 1
        tab_id = f"tab_{self.tab_counter}"

        tab_frame = ttk.Frame(self.notebook)

        # Editor container
        editor_container = ttk.Frame(tab_frame)
        editor_container.pack(fill=BOTH, expand=True)

        # Scrollbars — use tkinter.ttk to be safe
        v_scroll = tkttk.Scrollbar(editor_container, orient=tk.VERTICAL)
        h_scroll = tkttk.Scrollbar(editor_container, orient=tk.HORIZONTAL)

        editor = CodeEditor(
            editor_container, self.app, filepath=filepath,
            yscrollcommand=v_scroll.set,
            xscrollcommand=h_scroll.set,
        )

        line_numbers = LineNumbers(
            editor_container, editor, self.app.colors
        )
        line_numbers.set_font((
            self.app.settings["font_family"],
            self.app.settings["font_size"],
        ))

        v_scroll.config(command=editor.yview)
        h_scroll.config(command=editor.xview)

        line_numbers.pack(side=LEFT, fill=tk.Y)
        editor.pack(side=LEFT, fill=BOTH, expand=True)
        v_scroll.pack(side=RIGHT, fill=tk.Y)
        h_scroll.pack(side=BOTTOM, fill=tk.X)

        # Sync line numbers on scroll
        def _on_yscroll(*args):
            line_numbers.redraw()
            v_scroll.set(*args)

        editor.configure(yscrollcommand=_on_yscroll)
        editor.bind("<Configure>", lambda e: line_numbers.redraw())
        editor.bind(
            "<KeyRelease>",
            lambda e: (line_numbers.redraw(), editor._on_key_release(e)),
        )

        if content:
            editor.set_content(content)

        if title is None:
            title = os.path.basename(filepath) if filepath else f"Untitled-{self.tab_counter}"

        self.notebook.add(tab_frame, text=f"  {title}  ")
        self.notebook.select(tab_frame)

        self.tabs[tab_id] = {
            "editor": editor,
            "line_numbers": line_numbers,
            "filepath": filepath,
            "frame": tab_frame,
            "title": title,
        }

        editor._tab_id = tab_id
        self.app.set_status(f"Opened: {title}")
        return tab_id

    def get_active_editor(self):
        """Return the currently active editor widget."""
        tab_frame = self._get_active_frame()
        if tab_frame is None:
            return None
        for info in self.tabs.values():
            if info["frame"] == tab_frame:
                return info["editor"]
        return None

    def get_active_tab_info(self):
        """Return info dict for the active tab."""
        tab_frame = self._get_active_frame()
        if tab_frame is None:
            return None
        for info in self.tabs.values():
            if info["frame"] == tab_frame:
                return info
        return None

    def _get_active_frame(self):
        try:
            selected = self.notebook.select()
            if not selected:
                return None
            return self.notebook.nametowidget(selected)
        except Exception:
            return None

    def close_active_tab(self):
        """Close the currently selected tab."""
        tab_frame = self._get_active_frame()
        if tab_frame is None:
            return

        tab_id_to_remove = None
        for tab_id, info in self.tabs.items():
            if info["frame"] == tab_frame:
                tab_id_to_remove = tab_id
                break

        if tab_id_to_remove:
            info = self.tabs[tab_id_to_remove]
            if info["editor"].modified:
                from tkinter import messagebox
                result = messagebox.askyesnocancel(
                    "Save?",
                    f"Save changes to {info['title']}?"
                )
                if result is True:
                    self.app.file_manager.save_file()
                elif result is None:
                    return

            self.notebook.forget(tab_frame)
            del self.tabs[tab_id_to_remove]
            self.app.set_status("Tab closed")

    def mark_modified(self, editor):
        """Add unsaved indicator to tab title."""
        for info in self.tabs.values():
            if info["editor"] == editor:
                try:
                    idx = self.notebook.index(info["frame"])
                    title = info["title"]
                    if not title.startswith("● "):
                        self.notebook.tab(idx, text=f"  ● {title}  ")
                except Exception:
                    pass
                break

    def mark_saved(self, editor, new_title=None):
        """Remove unsaved indicator from tab title."""
        for info in self.tabs.values():
            if info["editor"] == editor:
                if new_title:
                    info["title"] = new_title
                try:
                    idx = self.notebook.index(info["frame"])
                    self.notebook.tab(idx, text=f"  {info['title']}  ")
                except Exception:
                    pass
                editor.modified = False
                break

    def update_filepath(self, editor, filepath):
        """Update the stored filepath for a tab."""
        for info in self.tabs.values():
            if info["editor"] == editor:
                info["filepath"] = filepath
                info["title"] = os.path.basename(filepath)
                break

    def _on_tab_changed(self, event=None):
        info = self.get_active_tab_info()
        if info:
            editor = info["editor"]
            editor.focus_set()
            self.app.statusbar.update_cursor_position(editor)
            self.app.statusbar.update_file_type(info.get("filepath"))

    def has_tabs(self):
        return len(self.tabs) > 0

    def refresh_all_highlighting(self):
        """Re-apply colors and syntax on all open editors."""
        for info in self.tabs.values():
            info["editor"].refresh_colors()
            info["line_numbers"].colors = self.app.colors
            info["line_numbers"].redraw()