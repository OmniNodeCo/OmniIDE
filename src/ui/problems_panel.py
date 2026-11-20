"""Problems panel — sidebar view of syntax/JSON errors. — PyQt6"""

import os

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTreeWidget,
    QTreeWidgetItem, QPushButton,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor, QPen, QBrush, QPainter

from src.ui.icons import svg_icon


class SeverityIcon:
    """Draws a small colored dot as a QIcon-free pixmap for the tree."""

    @staticmethod
    def dot(color_hex):
        from PyQt6.QtGui import QPixmap
        pm = QPixmap(12, 12)
        pm.fill(Qt.GlobalColor.transparent)
        p = QPainter(pm)
        p.setBrush(QBrush(QColor(color_hex)))
        p.setPen(QPen(QColor(color_hex)))
        p.drawEllipse(2, 2, 8, 8)
        p.end()
        from PyQt6.QtGui import QIcon
        return QIcon(pm)


class ProblemsPanel(QWidget):
    """Sidebar panel listing problems for open files."""

    def __init__(self, app):
        super().__init__()
        self.app = app
        self._problems = {}  # path -> [(line, message)]

        c = app.colors
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        header_row = QHBoxLayout()
        header = QLabel("PROBLEMS")
        header.setProperty("cssClass", "header")
        header_row.addWidget(header, 1)

        self.count_label = QLabel("")
        self.count_label.setStyleSheet(f"color: {c['error']}; font-weight: bold;")
        header_row.addWidget(self.count_label)

        clear_btn = QPushButton("Clear")
        clear_btn.setFixedWidth(52)
        clear_btn.clicked.connect(self.clear)
        header_row.addWidget(clear_btn)
        layout.addLayout(header_row)

        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setIndentation(6)
        self.tree.setFont(QFont(app.settings["font_family"],
                                max(8, app.settings["font_size"] - 2)))
        self.tree.itemDoubleClicked.connect(self._open_item)
        layout.addWidget(self.tree, 1)

    # ── Data ─────────────────────────────────────────────────────
    def set_problems(self, path, problems):
        """problems: [(line, message)]. Empty list clears the file."""
        if problems:
            self._problems[path] = problems
        else:
            self._problems.pop(path, None)
        self._rebuild()

    def file_paths(self):
        return list(self._problems.keys())

    def clear(self):
        self._problems.clear()
        self._rebuild()

    def total_count(self):
        return sum(len(v) for v in self._problems.values())

    def _rebuild(self):
        self.tree.clear()
        for path in sorted(self._problems):
            problems = self._problems[path]
            node = QTreeWidgetItem([f"{os.path.basename(path)}  ({len(problems)})"])
            node.setFont(0, QFont(self.app.settings["font_family"],
                                  max(9, self.app.settings["font_size"] - 1),
                                  QFont.Weight.Bold))
            node.setIcon(0, SeverityIcon.dot(self.app.colors["error"]))
            node.setData(0, Qt.ItemDataRole.UserRole, None)
            for line, message in sorted(problems):
                item = QTreeWidgetItem([f"Ln {line}  —  {message}"])
                item.setData(0, Qt.ItemDataRole.UserRole, (path, line))
                node.addChild(item)
            self.tree.addTopLevelItem(node)
            node.setExpanded(len(problems) <= 10)
        self.count_label.setText(
            str(self.total_count()) if self.total_count() else ""
        )

    def _open_item(self, item, _column):
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if data:
            path, line = data
            self.app.file_manager.open_file_at(path, line)
        elif item.childCount() > 0:
            item.setExpanded(not item.isExpanded())
