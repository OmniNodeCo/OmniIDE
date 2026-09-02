"""File operations — PyQt6."""

import json
import os
import shutil

from PyQt6.QtWidgets import QFileDialog, QMessageBox, QInputDialog
from PyQt6.QtGui import QClipboard

from src.config import FILE_DIALOG_TYPES
from src.core.textfile import (
    read_text, write_text, convert_line_ending, detect_line_ending,
)


def validate_json(text: str):
    """Return (ok, error_message, line, col)."""
    try:
        json.loads(text)
        return True, None, 0, 0
    except json.JSONDecodeError as e:
        return False, f"JSON error: {e.msg}", e.lineno, e.colno
    except Exception as e:  # pragma: no cover
        return False, f"JSON error: {e}", 0, 0


class FileManager:
    """Handles file I/O."""

    def __init__(self, app):
        self.app = app

    # ── Open / Save ────────────────────────────────────────────────
    def new_file(self):
        self.app.editor_tabs.new_tab()

    def open_file(self, filepath=None, line=None):
        if filepath is None:
            filepath, _ = QFileDialog.getOpenFileName(
                self.app, "Open File", "", FILE_DIALOG_TYPES,
            )
        if not filepath or not os.path.isfile(filepath):
            return

        try:
            text, encoding, eol, bom = read_text(filepath)
        except Exception as e:
            QMessageBox.critical(self.app, "Error", f"Cannot open:\n{e}")
            return

        self.app.editor_tabs.new_tab(
            filepath=filepath, content=text, title=os.path.basename(filepath)
        )
        editor = self.app.editor_tabs.get_current_code_editor()
        self.app.recent_files_manager.add(filepath)
        self._update_file_status(filepath, encoding, eol)
        if line and editor:
            self._jump_to_line(editor, line)
        self.app.set_status(f"Opened: {filepath}")

    def _update_file_status(self, filepath, encoding, eol):
        sb = self.app.statusbar
        sb.update_encoding(encoding)
        sb.update_line_ending(eol)
        ext = os.path.splitext(filepath)[1].lower()
        from src.config import SUPPORTED_EXTENSIONS
        sb.update_file_type(SUPPORTED_EXTENSIONS.get(ext, "Text"))

    def _jump_to_line(self, editor, line):
        from PyQt6.QtGui import QTextCursor
        cursor = editor.textCursor()
        block = editor.document().findBlockByLineNumber(max(0, line - 1))
        cursor.setPosition(block.position())
        cursor.movePosition(QTextCursor.MoveOperation.Down, QTextCursor.MoveMode.KeepAnchor)
        editor.setTextCursor(cursor)
        editor.centerCursor()

    def open_file_at(self, filepath, line=None):
        """Open a file (if not already open) and jump to a line."""
        existing = self.app.editor_tabs.find_editor_for_file(filepath)
        if existing:
            self.app.editor_tabs.set_editor(existing)
            if line:
                self._jump_to_line(existing, line)
            return
        self.open_file(filepath, line=line)

    def save_file(self):
        editor = self.app.editor_tabs.get_current_editor()
        if not editor:
            return
        if not getattr(editor, "filepath", None):
            self.save_file_as()
            return
        return self._save_editor(editor)

    def save_file_as(self):
        editor = self.app.editor_tabs.get_current_editor()
        if not editor:
            return

        filepath, _ = QFileDialog.getSaveFileName(
            self.app, "Save As", "", FILE_DIALOG_TYPES,
        )
        if not filepath:
            return

        editor.filepath = filepath
        self._save_editor(editor)
        self.app.editor_tabs.mark_saved(editor, os.path.basename(filepath))
        self.app.recent_files_manager.add(filepath)
        self._update_file_status(filepath, "utf-8",
                                 self.app.settings.get("line_ending", "lf"))

    def save_all(self):
        saved = 0
        for editor in self.app.editor_tabs.all_editors():
            if not isinstance(editor, self._code_editor_class()):
                continue
            if not getattr(editor, "filepath", None):
                continue
            try:
                with open(editor.filepath, "w", encoding="utf-8") as f:
                    f.write(editor.get_content())
                self.app.editor_tabs.mark_saved(editor)
                saved += 1
            except Exception:
                continue
        if saved:
            self.app.set_status(f"Saved {saved} file{'s' if saved != 1 else ''}")

    def _code_editor_class(self):
        from src.ui.editor_widget import CodeEditor
        return CodeEditor

    def _save_editor(self, editor):
        filepath = editor.filepath
        text = editor.get_content()

        # JSON validation — warn but don't block
        if os.path.splitext(filepath)[1].lower() == ".json":
            ok, msg, lineno, col = validate_json(text)
            if not ok:
                self.app.set_status(f"Ln {lineno}, Col {col} — {msg}")
                self.app.statusbar.set_json_error(lineno, col)
                self._confirm_invalid(filepath, msg)
                return False
            else:
                self.app.statusbar.set_json_error(None, None)

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(text)
        except Exception as e:
            QMessageBox.critical(self.app, "Error", f"Cannot save:\n{e}")
            return False

        self.app.editor_tabs.mark_saved(editor)
        self.app.set_status(f"Saved: {filepath}")
        return True

    def _confirm_invalid(self, filepath, msg):
        result = QMessageBox.question(
            self.app, "Invalid JSON",
            f"{msg}\n\nSave anyway?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if result == QMessageBox.StandardButton.Yes:
            try:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(self.app.editor_tabs.get_current_editor().get_content())
                self.app.editor_tabs.mark_saved(
                    self.app.editor_tabs.get_current_editor()
                )
            except Exception as e:
                QMessageBox.critical(self.app, "Error", f"Cannot save:\n{e}")

    # ── Auto save ──────────────────────────────────────────────────
    def autosave_tick(self):
        """Called on a timer when auto_save is enabled."""
        editor = self.app.editor_tabs.get_current_editor()
        if editor and getattr(editor, "modified", False) and getattr(editor, "filepath", None):
            self._save_editor(editor)

    # ── Filesystem operations (used by the file tree) ─────────────
    def new_file_in(self, directory):
        name, ok = QInputDialog.getText(
            self.app, "New File", "File name:",
        )
        if not ok or not name.strip():
            return
        path = os.path.join(directory, name.strip())
        if os.path.exists(path):
            QMessageBox.warning(self.app, "New File", "Already exists.")
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write("")
            self.app.sidebar.file_tree.refresh()
            self.open_file(path)
        except Exception as e:
            QMessageBox.critical(self.app, "New File", f"Cannot create:\n{e}")

    def new_folder_in(self, directory):
        name, ok = QInputDialog.getText(
            self.app, "New Folder", "Folder name:",
        )
        if not ok or not name.strip():
            return
        path = os.path.join(directory, name.strip())
        if os.path.exists(path):
            QMessageBox.warning(self.app, "New Folder", "Already exists.")
            return
        try:
            os.makedirs(path)
            self.app.sidebar.file_tree.refresh()
        except Exception as e:
            QMessageBox.critical(self.app, "New Folder", f"Cannot create:\n{e}")

    def rename_path(self, path):
        new_name, ok = QInputDialog.getText(
            self.app, "Rename", "New name:",
            text=os.path.basename(path),
        )
        if not ok or not new_name.strip():
            return
        target = os.path.join(os.path.dirname(path), new_name.strip())
        if os.path.exists(target):
            QMessageBox.warning(self.app, "Rename", "Already exists.")
            return
        try:
            os.rename(path, target)
            self.app.sidebar.file_tree.refresh()
        except Exception as e:
            QMessageBox.critical(self.app, "Rename", f"Cannot rename:\n{e}")

    def delete_path(self, path):
        name = os.path.basename(path)
        result = QMessageBox.question(
            self.app, "Delete",
            f"Delete '{name}'? This cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if result != QMessageBox.StandardButton.Yes:
            return
        try:
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)
            self.app.sidebar.file_tree.refresh()
            self.app.set_status(f"Deleted: {name}")
        except Exception as e:
            QMessageBox.critical(self.app, "Delete", f"Cannot delete:\n{e}")

    def copy_path_to_clipboard(self, path):
        clip = self.app.clipboard()
        if clip:
            clip.setText(path)
            self.app.set_status(f"Copied: {path}")

    # ── Line ending conversion ─────────────────────────────────────
    def convert_line_endings(self, target):
        editor = self.app.editor_tabs.get_current_editor()
        if not editor:
            return
        text = editor.get_content()
        editor.set_content(convert_line_ending(text, target))
        self.app.set_status(f"Line endings: {target.upper()}")
