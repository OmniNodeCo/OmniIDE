"""Go to Symbol dialog (Ctrl+T) — jump to a function/class in the file. — PyQt6"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLineEdit, QListWidget, QListWidgetItem, QLabel,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


KIND_GLYPHS = {
    "class": "ƒ→C",
    "function": "ƒ",
    "constant": "K",
    "interface": "I",
    "struct": "S",
    "enum": "E",
    "trait": "T",
    "type": "T",
    "variable": "v",
}


class SymbolDialog(QDialog):
    """Fuzzy go-to-symbol for the current file."""

    def __init__(self, app, symbols):
        super().__init__(app)
        self.app = app
        self.symbols = symbols

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setFixedSize(520, 360)
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
                font-size: 13px;
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

        hint = QLabel("Go to Symbol — current file")
        hint.setFont(QFont("Segoe UI", 9))
        layout.addWidget(hint)

        self.search = QLineEdit()
        self.search.setPlaceholderText("Symbol name... (Enter to jump, Esc to close)")
        self.search.textChanged.connect(self._query)
        layout.addWidget(self.search)

        self.list = QListWidget()
        self.list.itemActivated.connect(self._jump)
        layout.addWidget(self.list, 1)

        self._query("")
        self.search.setFocus()

    def move_to_center(self):
        parent = self.app.geometry()
        x = parent.x() + (parent.width() - self.width()) // 2
        y = parent.y() + 90
        self.move(x, y)

    def _query(self, text):
        from src.core.symbols import rank_symbols
        self.list.clear()
        ranked = rank_symbols(text.strip(), self.symbols, limit=50)
        for name, kind, line, _score in ranked:
            glyph = KIND_GLYPHS.get(kind, "•")
            item = QListWidgetItem(f" {glyph}  {name}")
            item.setToolTip(f"{kind} — line {line}")
            item.setData(Qt.ItemDataRole.UserRole, (name, kind, line))
            self.list.addItem(item)
        if self.list.count() > 0:
            self.list.setCurrentRow(0)

    def _jump(self, item):
        data = item.data(Qt.ItemDataRole.UserRole)
        if not data:
            return
        _name, _kind, line = data
        self.accept()
        editor = self.app.editor_tabs.get_current_code_editor()
        if editor:
            editor.goto_line(line)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.reject()
        elif event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            item = self.list.currentItem()
            if item:
                self._jump(item)
        else:
            super().keyPressEvent(event)
