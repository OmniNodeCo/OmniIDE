"""Toolbar — PyQt6."""

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QFrame


class Toolbar(QWidget):
    """Top action toolbar."""

    def __init__(self, app):
        super().__init__()
        self.app = app

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(4)

        buttons = [
            ("New", app.file_manager.new_file, None),
            ("Open", app.file_manager.open_file, None),
            ("Save", app.file_manager.save_file, "primary"),
            (None, None, None),
            ("Find", lambda: app.toggle_search(), None),
            (None, None, None),
            ("Theme", app.switch_theme, None),
            ("Settings", lambda: app.open_settings(), None),
        ]

        for text, callback, css_class in buttons:
            if text is None:
                sep = QFrame()
                sep.setFrameShape(QFrame.Shape.VLine)
                sep.setFixedWidth(1)
                sep.setStyleSheet(f"background-color: {app.colors['border']};")
                layout.addWidget(sep)
            else:
                btn = QPushButton(text)
                if css_class:
                    btn.setProperty("cssClass", css_class)
                btn.clicked.connect(callback)
                layout.addWidget(btn)

        layout.addStretch()

        palette_btn = QPushButton("Palette")
        palette_btn.clicked.connect(lambda: app.open_command_palette())
        layout.addWidget(palette_btn)