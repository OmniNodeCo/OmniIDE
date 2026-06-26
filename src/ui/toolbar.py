"""Toolbar with SVG icons — PyQt6."""

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QFrame
from src.ui.icons import svg_icon


class Toolbar(QWidget):
    """Top action toolbar."""

    def __init__(self, app):
        super().__init__()
        self.app = app

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(4)

        buttons = [
            ("New", "new_file", app.file_manager.new_file, None),
            ("Open", "open_file", app.file_manager.open_file, None),
            ("Save", "save", app.file_manager.save_file, "primary"),
            (None, None, None, None),
            ("Find", "search", lambda: app.toggle_search(), None),
            (None, None, None, None),
            ("Theme", "theme", app.switch_theme, None),
            ("Settings", "settings", lambda: app.open_settings(), None),
        ]

        for text, icon_name, callback, css_class in buttons:
            if text is None:
                sep = QFrame()
                sep.setFrameShape(QFrame.Shape.VLine)
                sep.setFixedWidth(1)
                sep.setStyleSheet(f"background-color: {app.colors['border']};")
                layout.addWidget(sep)
            else:
                btn = QPushButton(f"  {text}")
                btn.setIcon(svg_icon(icon_name, 14))
                if css_class:
                    btn.setProperty("cssClass", css_class)
                btn.clicked.connect(callback)
                layout.addWidget(btn)

        layout.addStretch()

        palette_btn = QPushButton("  Palette")
        palette_btn.setIcon(svg_icon("palette", 14))
        palette_btn.clicked.connect(lambda: app.open_command_palette())
        layout.addWidget(palette_btn)