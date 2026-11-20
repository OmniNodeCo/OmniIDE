"""Welcome screen — PyQt6 widget (replaces the plain-text welcome tab)."""

import os

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea,
    QFrame,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPixmap, QPainter

from src.config import APP_NAME, APP_VERSION, APP_AUTHOR, APP_WEBSITE
from src.ui.icons import svg_icon


def _load_logo(app, size=72):
    from PyQt6.QtSvg import QSvgRenderer
    from src.config import ASSETS_DIR
    path = os.path.join(ASSETS_DIR, "logo.svg")
    pm = QPixmap(size, size)
    pm.fill(Qt.GlobalColor.transparent)
    if os.path.exists(path):
        renderer = QSvgRenderer(path)
        p = QPainter(pm)
        renderer.render(p)
        p.end()
    return pm


class _SectionTitle(QLabel):
    def __init__(self, text, c):
        super().__init__(text.upper())
        self.setStyleSheet(
            f"color: {c['fg_secondary']}; font-size: 11px; font-weight: bold;")


class WelcomeWidget(QWidget):
    """Full welcome screen with actions, recent files and shortcuts."""

    def __init__(self, app):
        super().__init__()
        self.app = app
        c = app.colors

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet(
            f"QScrollArea {{ background-color: {c['bg_primary']}; border: none; }}")

        body = QWidget()
        body.setStyleSheet(f"background-color: {c['bg_primary']};")
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(40, 32, 40, 32)
        body_layout.setSpacing(14)

        # Header
        logo_row = QHBoxLayout()
        logo = QLabel()
        logo.setPixmap(_load_logo(app, 64))
        logo_row.addWidget(logo)
        title = QLabel(f"{APP_NAME} <span style='color:{c['accent']};'>v{APP_VERSION}</span>")
        title.setTextFormat(Qt.TextFormat.RichText)
        title.setFont(QFont("Segoe UI", 26, QFont.Weight.Light))
        title.setStyleSheet(f"color: {c['fg_primary']};")
        logo_row.addWidget(title)
        logo_row.addStretch()
        body_layout.addLayout(logo_row)

        sub = QLabel(f"by {APP_AUTHOR} — Fast. Modern. Lightweight. No Electron.")
        sub.setStyleSheet(f"color: {c['fg_secondary']}; font-size: 12px;")
        body_layout.addWidget(sub)

        body_layout.addSpacing(10)

        # Quick actions
        body_layout.addWidget(_SectionTitle("Get Started", c))
        actions = [
            ("New File", "Ctrl+N", app.file_manager.new_file),
            ("Open File", "Ctrl+O", app.file_manager.open_file),
            ("Open Folder", "", lambda: app.open_project()),
            ("Quick Open", "Ctrl+P", app.open_quick_open),
            ("Command Palette", "Ctrl+Shift+P", app.open_command_palette),
            ("Settings", "Ctrl+,", app.open_settings),
        ]
        grid = QHBoxLayout()
        grid.setSpacing(8)
        for text, shortcut, cb in actions:
            btn = QPushButton(f"  {text}")
            btn.setToolTip(shortcut)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {c['bg_tertiary']};
                    color: {c['fg_primary']};
                    border: 1px solid {c['border']};
                    border-radius: 6px;
                    padding: 8px 10px;
                    text-align: left;
                    font-size: 12px;
                }}
                QPushButton:hover {{ background-color: {c['selection']}; }}
            """)
            btn.clicked.connect(cb)
            grid.addWidget(btn, 1)
        body_layout.addLayout(grid)

        body_layout.addSpacing(6)

        # Recent files
        body_layout.addWidget(_SectionTitle("Recent Files", c))
        recent = app.recent_files_manager.get_all()[:8]
        if recent:
            for fp in recent:
                btn = QPushButton(f"  {fp}")
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background: transparent;
                        color: {c['fg_primary']};
                        border: none;
                        border-radius: 4px;
                        padding: 5px 8px;
                        text-align: left;
                        font-family: {app.settings['font_family']};
                        font-size: 11px;
                    }}
                    QPushButton:hover {{ background-color: {c['bg_tertiary']}; }}
                """)
                btn.clicked.connect(lambda _=False, p=fp: app.file_manager.open_file(p))
                body_layout.addWidget(btn)
        else:
            none = QLabel("  No recent files yet.")
            none.setStyleSheet(f"color: {c['fg_secondary']}; font-size: 11px;")
            body_layout.addWidget(none)

        body_layout.addSpacing(6)

        # Recent folders
        body_layout.addWidget(_SectionTitle("Recent Folders", c))
        folders = app.recent_folders.get_all()[:8]
        if folders:
            for fp in folders:
                btn = QPushButton(f"  {fp}")
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background: transparent;
                        color: {c['accent']};
                        border: none;
                        border-radius: 4px;
                        padding: 5px 8px;
                        text-align: left;
                        font-family: {app.settings['font_family']};
                        font-size: 11px;
                    }}
                    QPushButton:hover {{ background-color: {c['bg_tertiary']}; }}
                """)
                btn.clicked.connect(lambda _=False, p=fp: app.open_project(p))
                body_layout.addWidget(btn)
        else:
            none = QLabel("  No recent folders yet.")
            none.setStyleSheet(f"color: {c['fg_secondary']}; font-size: 11px;")
            body_layout.addWidget(none)

        body_layout.addSpacing(10)

        # Shortcuts cheatsheet
        body_layout.addWidget(_SectionTitle("Shortcuts", c))
        shortcuts = [
            ("Ctrl+P", "Quick Open"), ("Ctrl+Shift+F", "Search in Files"),
            ("Ctrl+T", "Go to Symbol"), ("Ctrl+G", "Go to Line"),
            ("Ctrl+/", "Toggle Comment"), ("Ctrl+D", "Duplicate Line"),
            ("Ctrl+Shift+O", "Sort Lines"), ("Ctrl+Shift+V", "Markdown Preview"),
            ("Ctrl+F5", "Run File"), ("Ctrl+Shift+T", "New Terminal"),
            ("Ctrl+Shift+P", "Command Palette"), ("Ctrl+,", "Settings"),
        ]
        grid = QHBoxLayout()
        grid.setSpacing(6)
        col1, col2 = QVBoxLayout(), QVBoxLayout()
        for sc, label in shortcuts[:6]:
            col1.addWidget(self._shortcut_row(sc, label, c))
        for sc, label in shortcuts[6:]:
            col2.addWidget(self._shortcut_row(sc, label, c))
        grid.addLayout(col1, 1)
        grid.addLayout(col2, 1)
        body_layout.addLayout(grid)

        body_layout.addStretch()

        foot = QLabel(
            f"<a href='{APP_WEBSITE}' style='color:{c['accent']};'>{APP_WEBSITE}</a>"
        )
        foot.setTextFormat(Qt.TextFormat.RichText)
        foot.setOpenExternalLinks(True)
        foot.setStyleSheet(f"color: {c['fg_secondary']}; font-size: 10px;")
        body_layout.addWidget(foot)

        scroll.setWidget(body)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

    def _shortcut_row(self, shortcut, label, c):
        row = QWidget()
        h = QHBoxLayout(row)
        h.setContentsMargins(6, 2, 6, 2)
        kbd = QLabel(shortcut)
        kbd.setStyleSheet(f"""
            background-color: {c['bg_tertiary']};
            color: {c['fg_primary']};
            border: 1px solid {c['border']};
            border-radius: 4px;
            padding: 2px 6px;
            font-family: Consolas, monospace;
            font-size: 10px;
        """)
        lbl = QLabel(label)
        lbl.setStyleSheet(f"color: {c['fg_secondary']}; font-size: 11px;")
        h.addWidget(kbd)
        h.addWidget(lbl, 1)
        return row
