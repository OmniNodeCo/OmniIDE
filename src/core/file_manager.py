"""File operations — PyQt6."""

import os

from PyQt6.QtWidgets import QFileDialog, QMessageBox

from src.config import FILE_DIALOG_TYPES


class FileManager:
    """Handles file I/O."""

    def __init__(self, app):
        self.app = app

    def new_file(self):
        self.app.editor_tabs.new_tab()

    def open_file(self, filepath=None):
        if filepath is None:
            filepath, _ = QFileDialog.getOpenFileName(
                self.app, "Open File", "", FILE_DIALOG_TYPES,
            )
        if not filepath or not os.path.isfile(filepath):
            return

        try:
            with open(filepath, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
        except Exception as e:
            QMessageBox.critical(self.app, "Error", f"Cannot open:\n{e}")
            return

        self.app.editor_tabs.new_tab(filepath=filepath, content=content, title=os.path.basename(filepath))
        self.app.recent_files_manager.add(filepath)
        self.app.set_status(f"Opened: {filepath}")

    def save_file(self):
        editor = self.app.editor_tabs.get_current_editor()
        if not editor:
            return

        # Find filepath
        filepath = getattr(editor, "filepath", None)
        if not filepath:
            self.save_file_as()
            return

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(editor.get_content())
            self.app.editor_tabs.mark_saved(editor)
            self.app.set_status(f"Saved: {filepath}")
        except Exception as e:
            QMessageBox.critical(self.app, "Error", f"Cannot save:\n{e}")

    def save_file_as(self):
        editor = self.app.editor_tabs.get_current_editor()
        if not editor:
            return

        filepath, _ = QFileDialog.getSaveFileName(
            self.app, "Save As", "", FILE_DIALOG_TYPES,
        )
        if not filepath:
            return

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(editor.get_content())
            editor.filepath = filepath
            self.app.editor_tabs.mark_saved(editor, os.path.basename(filepath))
            self.app.recent_files_manager.add(filepath)
            self.app.set_status(f"Saved: {filepath}")
        except Exception as e:
            QMessageBox.critical(self.app, "Error", f"Cannot save:\n{e}")