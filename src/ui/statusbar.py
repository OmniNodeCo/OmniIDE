"""Status bar — PyQt6."""

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel


class StatusBar(QWidget):
    """Bottom status bar."""

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.setFixedHeight(28)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 0, 8, 0)
        layout.setSpacing(16)

        self.status_label = QLabel(f"OmniIDE v{app.settings.get('font_size', 13)} — Ready")
        layout.addWidget(self.status_label)

        layout.addStretch()

        self.git_label = QLabel("")
        self.git_label.setProperty("cssClass", "dim")
        layout.addWidget(self.git_label)

        self.encoding_label = QLabel("UTF-8")
        self.encoding_label.setProperty("cssClass", "dim")
        layout.addWidget(self.encoding_label)

        self.filetype_label = QLabel("Text")
        self.filetype_label.setProperty("cssClass", "dim")
        layout.addWidget(self.filetype_label)

        self.cursor_label = QLabel("Ln 1, Col 1")
        self.cursor_label.setProperty("cssClass", "dim")
        layout.addWidget(self.cursor_label)

        self.setStyleSheet(f"""
            QWidget {{
                background-color: {app.colors['bg_tertiary']};
            }}
        """)

    def set_text(self, text):
        self.status_label.setText(text)

    def update_file_type(self, lang):
        self.filetype_label.setText(lang or "Text")

    def update_git_branch(self, branch):
        self.git_label.setText(branch or "")

    def update_cursor(self, line, col):
        self.cursor_label.setText(f"Ln {line}, Col {col}")