"""File operations: open, save, new."""

import os
from tkinter import filedialog, messagebox
from src.config import FILE_DIALOG_TYPES


class FileManager:
    """Handles file I/O operations."""

    def __init__(self, app):
        self.app = app

    def new_file(self):
        """Create a new untitled tab."""
        self.app.tab_manager.new_tab()

    def open_file(self, filepath=None):
        """Open a file into a new tab."""
        if filepath is None:
            filepath = filedialog.askopenfilename(
                title="Open File",
                filetypes=FILE_DIALOG_TYPES,
            )

        if not filepath or not os.path.isfile(filepath):
            return

        # Check if already open
        for info in self.app.tab_manager.tabs.values():
            if info["filepath"] == filepath:
                idx = self.app.tab_manager.notebook.index(info["frame"])
                self.app.tab_manager.notebook.select(idx)
                return

        try:
            with open(filepath, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
        except Exception as e:
            messagebox.showerror("Error", f"Cannot open file:\n{e}")
            return

        self.app.tab_manager.new_tab(
            filepath=filepath,
            content=content,
            title=os.path.basename(filepath),
        )

        self.app.recent_files_manager.add(filepath)
        self.app.set_status(f"Opened: {filepath}")

    def save_file(self):
        """Save the current file."""
        info = self.app.tab_manager.get_active_tab_info()
        if info is None:
            return

        editor = info["editor"]
        filepath = info["filepath"]

        if filepath is None:
            self.save_file_as()
            return

        try:
            content = editor.get_content()
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            self.app.tab_manager.mark_saved(editor)
            self.app.set_status(f"Saved: {filepath}")
        except Exception as e:
            messagebox.showerror("Error", f"Cannot save file:\n{e}")

    def save_file_as(self):
        """Save current file with a new name."""
        info = self.app.tab_manager.get_active_tab_info()
        if info is None:
            return

        editor = info["editor"]

        filepath = filedialog.asksaveasfilename(
            title="Save As",
            filetypes=FILE_DIALOG_TYPES,
            defaultextension=".py",
        )

        if not filepath:
            return

        try:
            content = editor.get_content()
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)

            self.app.tab_manager.update_filepath(editor, filepath)
            self.app.tab_manager.mark_saved(
                editor, new_title=os.path.basename(filepath)
            )
            self.app.recent_files_manager.add(filepath)
            self.app.set_status(f"Saved: {filepath}")

            # Update syntax highlighting for new file type
            editor.highlighter.filepath = filepath
            editor.highlighter.language = editor.highlighter._detect_language()
            editor.highlighter._configure_tags()
            editor.highlighter.highlight()

        except Exception as e:
            messagebox.showerror("Error", f"Cannot save file:\n{e}")