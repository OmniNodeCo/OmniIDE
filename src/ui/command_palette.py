"""Command palette dialog — PyQt6."""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLineEdit, QListWidget, QListWidgetItem, QLabel,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from src.core.fuzzy import score as fuzzy_score


class CommandPaletteDialog(QDialog):
    """Fuzzy-searchable command palette."""

    def __init__(self, app):
        super().__init__(app)
        self.app = app
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setFixedSize(550, 400)
        self.move_to_center()

        c = app.colors
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {c['bg_secondary']};
                border: 1px solid {c['border']};
                border-radius: 8px;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        self.search = QLineEdit()
        self.search.setPlaceholderText("Type a command...")
        self.search.setFont(QFont("Segoe UI", 13))
        self.search.textChanged.connect(self._filter)
        layout.addWidget(self.search)

        self.list = QListWidget()
        self.list.setFont(QFont("Segoe UI", 10))
        self.list.itemActivated.connect(self._execute)
        self.list.setStyleSheet(f"""
            QListWidget {{
                background-color: {c['bg_secondary']};
                border: none;
            }}
            QListWidget::item {{
                padding: 8px;
                border-radius: 4px;
            }}
            QListWidget::item:selected {{
                background-color: {c['selection']};
            }}
            QListWidget::item:hover {{
                background-color: {c['bg_tertiary']};
            }}
        """)
        layout.addWidget(self.list)

        self.commands = self._build_commands()
        self._filter("")

    def move_to_center(self):
        parent = self.app.geometry()
        x = parent.x() + (parent.width() - self.width()) // 2
        y = parent.y() + 80
        self.move(x, y)

    def _build_commands(self):
        app = self.app
        et = app.editor_tabs
        return [
            ("File: New File", "Ctrl+N", app.file_manager.new_file),
            ("File: Open File", "Ctrl+O", app.file_manager.open_file),
            ("File: Open Folder", "", lambda: app.open_project()),
            ("File: Quick Open", "Ctrl+P", app.open_quick_open),
            ("File: Save", "Ctrl+S", app.file_manager.save_file),
            ("File: Save As", "Ctrl+Shift+S", app.file_manager.save_file_as),
            ("File: Save All", "Ctrl+Alt+S", app.file_manager.save_all),
            ("File: Close Tab", "Ctrl+W", et.close_current_tab),
            ("File: Close Other Tabs", "", et.close_other_tabs),
            ("File: Close All Tabs", "", et.close_all_tabs),
            ("Edit: Find & Replace", "Ctrl+F", app.toggle_search),
            ("Edit: Go to Line", "Ctrl+G", app.go_to_line),
            ("Edit: Toggle Comment", "Ctrl+/", app.toggle_comment),
            ("Edit: Duplicate Line", "Ctrl+D", app.duplicate_line),
            ("Edit: Delete Line", "Ctrl+Shift+D", app.delete_line),
            ("Edit: Move Line Up", "Alt+Up", app.move_line_up),
            ("Edit: Move Line Down", "Alt+Down", app.move_line_down),
            ("Edit: Sort Lines", "Ctrl+Shift+O", app.sort_lines),
            ("Edit: Line Endings: LF", "", lambda: app.file_manager.convert_line_endings("lf")),
            ("Edit: Line Endings: CRLF", "", lambda: app.file_manager.convert_line_endings("crlf")),
            ("View: Command Palette", "Ctrl+Shift+P", lambda: None),
            ("View: Search in Files", "Ctrl+Shift+F", app.open_search),
            ("View: Toggle Sidebar", "Ctrl+B", app.toggle_sidebar),
            ("View: Toggle Terminal", "Ctrl+`", app.toggle_terminal),
            ("View: New Terminal", "Ctrl+Shift+T", app.new_terminal),
            ("View: Markdown Preview", "Ctrl+Shift+V", app.toggle_markdown_preview),
            ("View: Toggle Minimap", "", app.toggle_minimap),
            ("View: Toggle Hidden Files", "", app.toggle_hidden_files),
            ("View: Switch Theme", "", app.switch_theme),
            ("View: Zoom In", "Ctrl+=", lambda: app._zoom(1)),
            ("View: Zoom Out", "Ctrl+-", lambda: app._zoom(-1)),
            ("View: Reset Zoom", "Ctrl+0", lambda: app._zoom(0)),
            ("Settings: Open Settings", "Ctrl+,", app.open_settings),
            ("Git: Clone", "", app.git_manager.clone_repo),
            ("Git: Init", "", app.git_manager.init_repo),
            ("Git: Status", "", app.git_manager.git_status),
            ("Git: Diff", "", app.git_manager.git_diff),
            ("Git: Log", "", app.git_manager.git_log),
            ("Git: Branches", "", app.git_manager.git_branch),
            ("Git: Stage All", "", app.git_manager.git_add_all),
            ("Git: Commit", "", app.git_manager.git_commit),
            ("Git: Push", "", app.git_manager.git_push),
            ("Git: Pull", "", app.git_manager.git_pull),
            ("Git: Set Remote", "", app.git_manager.add_remote),
            ("Terminal: Clear", "", lambda: app.terminal.clear()),
            ("Terminal: New Terminal", "Ctrl+Shift+T", app.new_terminal),
            ("Terminal: Restart", "", lambda: app.terminal._restart()),
            ("Update: Check for Updates", "", app.check_for_updates),
            ("OmniIDE: About", "", self._about),
        ]

    def _about(self):
        from PyQt6.QtWidgets import QMessageBox
        from src.config import APP_VERSION
        QMessageBox.about(
            self.app, "About OmniIDE",
            f"OmniIDE v{APP_VERSION}\n\n"
            f"Built from scratch by OmniNodeCo.\n"
            f"No Electron. No bloat. Pure speed.",
        )

    def _filter(self, query):
        self.list.clear()
        q = query.strip()

        # Score every command; keep matches above a floor
        scored = []
        for label, shortcut, action in self.commands:
            if not q:
                scored.append((1, label, shortcut, action))
                continue
            s = fuzzy_score(q, label)
            if s > 6:
                scored.append((s, label, shortcut, action))

        scored.sort(key=lambda t: (-t[0], t[1].lower()))
        for _s, label, shortcut, action in scored[:40]:
            text = f"{label}    {shortcut}" if shortcut else label
            item = QListWidgetItem(text)
            item.setData(Qt.ItemDataRole.UserRole, action)
            self.list.addItem(item)

        if self.list.count() > 0:
            self.list.setCurrentRow(0)

    def _execute(self, item):
        action = item.data(Qt.ItemDataRole.UserRole)
        self.accept()
        if action:
            action()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.reject()
        elif event.key() in (Qt.Key.Key_Down, Qt.Key.Key_Up):
            self.list.keyPressEvent(event)
        elif event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            item = self.list.currentItem()
            if item:
                self._execute(item)
        else:
            super().keyPressEvent(event)
