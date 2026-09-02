"""Status bar — PyQt6."""

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel


class StatusBar(QWidget):
    """Bottom status bar."""

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.setFixedHeight(28)
        self.json_error = None  # (line, col) or None

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 0, 8, 0)
        layout.setSpacing(16)

        self.status_label = QLabel("Ready")
        layout.addWidget(self.status_label)

        layout.addStretch()

        self.git_label = QLabel("")
        self.git_label.setProperty("cssClass", "dim")
        layout.addWidget(self.git_label)

        self.encoding_label = QLabel("UTF-8")
        self.encoding_label.setProperty("cssClass", "dim")
        layout.addWidget(self.encoding_label)

        self.eol_label = QLabel("LF")
        self.eol_label.setProperty("cssClass", "dim")
        layout.addWidget(self.eol_label)

        self.filetype_label = QLabel("Text")
        self.filetype_label.setProperty("cssClass", "dim")
        layout.addWidget(self.filetype_label)

        self.cursor_label = QLabel("Ln 1, Col 1")
        self.cursor_label.setProperty("cssClass", "dim")
        layout.addWidget(self.cursor_label)

        self.selection_label = QLabel("")
        self.selection_label.setProperty("cssClass", "dim")
        layout.addWidget(self.selection_label)

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
        self.git_label.setText(f"⎇ {branch}" if branch else "")

    def update_encoding(self, encoding):
        if not encoding:
            return
        self.encoding_label.setText(encoding.upper() if len(encoding) <= 4
                                    else encoding)

    def update_line_ending(self, eol):
        if eol:
            self.eol_label.setText(eol.upper())

    def set_json_error(self, line, col):
        self.json_error = (line, col) if line else None
        if self.json_error:
            self.status_label.setText(f"JSON error at Ln {line}, Col {col}")
        self.app.editor_tabs.refresh_all()

    def update_cursor(self, editor):
        """Update cursor label from an editor instance."""
        self.update_cursor_position_for(editor)

    def update_cursor_position_for(self, widget):
        cursor = getattr(widget, "textCursor", None)
        if not callable(cursor):
            return
        c = cursor()
        line = c.blockNumber() + 1
        col = c.columnNumber() + 1
        self.cursor_label.setText(f"Ln {line}, Col {col}")

        sel_len = c.selectionEnd() - c.selectionStart()
        if sel_len > 0:
            words = len(widget.toPlainText()[c.selectionStart():c.selectionEnd()].split())
            self.selection_label.setText(f"{words} selected")
        else:
            self.selection_label.setText("")
