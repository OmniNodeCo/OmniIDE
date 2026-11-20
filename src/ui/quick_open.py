"""Quick Open dialog (Ctrl+P) — fuzzy file finder. — PyQt6."""

import os

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLineEdit, QListWidget, QListWidgetItem, QLabel,
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QKeySequence

from src.core.quick_open import QuickOpenIndex
from src.core.fuzzy import score as fuzzy_score


class QuickOpenDialog(QDialog):
    """Fuzzy file picker for the current project."""

    def __init__(self, app):
        super().__init__(app)
        self.app = app
        self.index = QuickOpenIndex()
        self._results = []

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setFixedSize(580, 380)
        self.move_to_center()

        c = app.colors
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {c['bg_secondary']};
                border: 1px solid {c['border']};
                border-radius: 8px;
            }}
            QLabel {{ color: {c['fg_secondary']}; }}
            QLineEdit {{
                background-color: {c['bg_primary']};
                color: {c['fg_primary']};
                border: 1px solid {c['border']};
                border-radius: 6px;
                padding: 6px 10px;
                font-size: 14px;
            }}
            QListWidget {{
                background-color: {c['bg_secondary']};
                border: none;
            }}
            QListWidget::item {{
                padding: 7px 10px;
                border-radius: 4px;
                color: {c['fg_primary']};
            }}
            QListWidget::item:selected {{
                background-color: {c['selection']};
            }}
            QListWidget::item:hover {{
                background-color: {c['bg_tertiary']};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        hint = QLabel("Quick Open — type a file name (fuzzy)")
        hint.setFont(QFont("Segoe UI", 9))
        layout.addWidget(hint)

        self.search = QLineEdit()
        self.search.setPlaceholderText("File name... (Enter to open, Esc to close)")
        self.search.textChanged.connect(self._query)
        layout.addWidget(self.search)

        self.list = QListWidget()
        self.list.itemActivated.connect(self._open_item)
        layout.addWidget(self.list, 1)

        self._refresh_index()
        self.search.setFocus()

    def move_to_center(self):
        parent = self.app.geometry()
        x = parent.x() + (parent.width() - self.width()) // 2
        y = parent.y() + 70
        self.move(x, y)

    def _refresh_index(self):
        root = self.app.current_project_path
        if self.index.needs_refresh(root):
            self.index.refresh(root)

    def _query(self, text):
        self._refresh_index()
        self.list.clear()
        q = text.strip()
        if not q:
            # No query: show most recent files from the project root
            files = list(self.index.files)[:30]
            for path in files:
                rel = os.path.relpath(path, self.index.root or "")
                self._add_item(path, rel)
            self._results = [(p, os.path.relpath(p, self.index.root or ""))
                             for p in files]
        else:
            results = self.index.query(q, limit=60)
            for path, rel, s in results:
                self._add_item(path, rel)
            self._results = [(p, r) for p, r, _ in results]

        if self.list.count() > 0:
            self.list.setCurrentRow(0)

    def _add_item(self, path, rel):
        name = os.path.basename(path)
        item = QListWidgetItem(f" {name}")
        item.setToolTip(rel)
        item.setData(Qt.ItemDataRole.UserRole, path)
        parent, child = os.path.split(rel)
        if parent:
            item.setToolTip(f"{rel}")
        self.list.addItem(item)

    def _open_item(self, item):
        path = item.data(Qt.ItemDataRole.UserRole)
        if not path:
            return
        self.accept()
        self.app.file_manager.open_file(path)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.reject()
        elif event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            item = self.list.currentItem()
            if item:
                self._open_item(item)
        else:
            super().keyPressEvent(event)
