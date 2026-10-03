"""Search in Files panel — global project search. — PyQt6"""

import os
import threading

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QTreeWidget, QTreeWidgetItem, QCheckBox, QLabel, QMessageBox,
)
from PyQt6.QtCore import pyqtSignal, QObject, Qt
from PyQt6.QtGui import QFont

from src.core.project_search import ProjectSearch


class _Signals(QObject):
    finished = pyqtSignal(object)  # list[SearchResult]
    error = pyqtSignal(str)


class SearchPanel(QWidget):
    """Sidebar panel: search across all project files."""

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.signals = _Signals()
        self.signals.finished.connect(self._show_results)
        self.signals.error.connect(self._show_error)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        header = QLabel("SEARCH IN FILES")
        header.setProperty("cssClass", "header")
        layout.addWidget(header)

        # Search row
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search...")
        self.search_input.textChanged.connect(self._on_text)
        self.search_input.returnPressed.connect(self.run_search)
        layout.addWidget(self.search_input)

        # Options row
        opts = QHBoxLayout()
        self.case_check = QCheckBox("Aa")
        self.case_check.setToolTip("Match case")
        self.case_check.toggled.connect(self._on_text)
        opts.addWidget(self.case_check)

        self.word_check = QCheckBox("W")
        self.word_check.setToolTip("Whole word")
        self.word_check.toggled.connect(self._on_text)
        opts.addWidget(self.word_check)

        self.regex_check = QCheckBox(".*")
        self.regex_check.setToolTip("Regular expression")
        self.regex_check.toggled.connect(self._on_text)
        opts.addWidget(self.regex_check)

        self.clear_btn = QPushButton("✕")
        self.clear_btn.setFixedWidth(26)
        self.clear_btn.setToolTip("Clear results")
        self.clear_btn.clicked.connect(self._clear)
        opts.addWidget(self.clear_btn)
        opts.addStretch()
        layout.addLayout(opts)

        self.status = QLabel("")
        self.status.setProperty("cssClass", "dim")
        self.status.setFont(QFont("Segoe UI", 8))
        layout.addWidget(self.status)

        # Results
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setIndentation(14)
        self.tree.setFont(QFont(self.app.settings["font_family"],
                                max(8, self.app.settings["font_size"] - 2)))
        self.tree.itemDoubleClicked.connect(self._open_result)
        layout.addWidget(self.tree, 1)

        # Debounce timer
        from PyQt6.QtCore import QTimer
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.setInterval(400)
        self._timer.timeout.connect(self.run_search)
        self._search = None

    def _on_text(self):
        if not self.search_input.text().strip():
            self._clear()
            return
        self._timer.start()

    def run_search(self):
        query = self.search_input.text().strip()
        root = self.app.current_project_path
        if not query:
            return
        if not root:
            self.status.setText("Open a folder first.")
            return

        if self._search:
            self._search.abort()

        self._search = ProjectSearch(
            root,
            max_results=self.app.settings.get("max_search_results", 1000),
        )
        s = self._search
        case = self.case_check.isChecked()
        regex = self.regex_check.isChecked()
        word = self.word_check.isChecked()

        def _worker():
            try:
                results = s.search(query, case, regex, word)
                self.signals.finished.emit(results)
            except Exception as e:
                self.signals.error.emit(str(e))

        self.status.setText("Searching...")
        threading.Thread(target=_worker, daemon=True).start()

    def _show_results(self, results):
        self.tree.clear()
        if not results:
            self.status.setText("No results found.")
            return

        counts = {}
        by_file = {}
        for r in results:
            counts[r.path] = counts.get(r.path, 0) + 1
            by_file.setdefault(r.path, []).append(r)

        self.status.setText(
            f"{len(results)} results in {len(counts)} file(s)"
        )

        for path in sorted(by_file):
            rel = os.path.relpath(path, self.app.current_project_path or path)
            node = QTreeWidgetItem([f"{rel}  ({counts[path]})"])
            node.setFont(0, QFont(self.app.settings["font_family"],
                                  max(9, self.app.settings["font_size"] - 1),
                                  QFont.Weight.Bold))
            node.setData(0, Qt.ItemDataRole.UserRole, None)
            node.setIcon(0, self.app.windowIcon())
            for r in by_file[path]:
                text = r.line_text.strip()
                if len(text) > 160:
                    text = text[:160] + "…"
                child = QTreeWidgetItem([f"{r.line_no:>5}  {text}"])
                child.setData(0, Qt.ItemDataRole.UserRole,
                              (path, r.line_no))
                node.addChild(child)
            self.tree.addTopLevelItem(node)
            node.setExpanded(len(by_file[path]) <= 5)

    def _show_error(self, message):
        self.status.setText(f"Error: {message}")

    def _open_result(self, item, _column):
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if not data:
            # File node — expand/collapse
            if item.childCount() > 0:
                item.setExpanded(not item.isExpanded())
            return
        path, line_no = data
        self.app.file_manager.open_file_at(path, line_no)

    def _clear(self):
        self.tree.clear()
        self.status.setText("")
        if self._search:
            self._search.abort()
