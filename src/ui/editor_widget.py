"""Editor tab widget with syntax highlighting — PyQt6."""

import os

from PyQt6.QtWidgets import (
    QWidget, QTabWidget, QVBoxLayout, QHBoxLayout, QPlainTextEdit,
    QLabel, QFrame, QLineEdit, QPushButton, QCheckBox,
)
from PyQt6.QtCore import Qt, QRect, QSize, QRegularExpression
from PyQt6.QtGui import (
    QFont, QColor, QPainter, QTextFormat, QSyntaxHighlighter,
    QTextCharFormat, QTextCursor, QKeySequence, QShortcut,
)

from src.config import APP_NAME, APP_VERSION, APP_AUTHOR, SUPPORTED_EXTENSIONS


class LineNumberArea(QWidget):
    """Line number gutter for the editor."""

    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor

    def sizeHint(self):
        return QSize(self.editor.line_number_area_width(), 0)

    def paintEvent(self, event):
        self.editor.line_number_area_paint_event(event)


class CodeEditor(QPlainTextEdit):
    """Code editor with line numbers and syntax highlighting."""

    def __init__(self, app, filepath=None):
        super().__init__()
        self.app = app
        self.filepath = filepath
        self.modified = False

        font = QFont(app.settings["font_family"], app.settings["font_size"])
        font.setFixedPitch(True)
        self.setFont(font)
        self.setTabStopDistance(app.settings["tab_size"] * self.fontMetrics().horizontalAdvance(" "))

        self.setLineWrapMode(
            QPlainTextEdit.LineWrapMode.WidgetWidth if app.settings["word_wrap"]
            else QPlainTextEdit.LineWrapMode.NoWrap
        )

        c = app.colors
        self.setStyleSheet(f"""
            QPlainTextEdit {{
                background-color: {c['editor_bg']};
                color: {c['editor_fg']};
                border: none;
                selection-background-color: {c['selection']};
                padding: 4px;
            }}
        """)

        # Line numbers
        self.line_number_area = LineNumberArea(self)
        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.cursorPositionChanged.connect(self.highlight_current_line)
        self.textChanged.connect(self._on_text_changed)

        self.update_line_number_area_width(0)
        self.highlight_current_line()

        # Syntax highlighter
        self.highlighter = SimpleSyntaxHighlighter(self.document(), app.syntax_colors, filepath)

    def _on_text_changed(self):
        self.modified = True

    def line_number_area_width(self):
        digits = max(1, len(str(self.blockCount())))
        return 10 + self.fontMetrics().horizontalAdvance("9") * (digits + 1)

    def update_line_number_area_width(self, _):
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def update_line_number_area(self, rect, dy):
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height()))

    def line_number_area_paint_event(self, event):
        painter = QPainter(self.line_number_area)
        c = self.app.colors
        painter.fillRect(event.rect(), QColor(c["bg_secondary"]))

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = round(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + round(self.blockBoundingRect(block).height())

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.setPen(QColor(c["fg_secondary"]))
                painter.setFont(self.font())
                painter.drawText(
                    0, top, self.line_number_area.width() - 6,
                    self.fontMetrics().height(),
                    Qt.AlignmentFlag.AlignRight, number,
                )
            block = block.next()
            top = bottom
            bottom = top + round(self.blockBoundingRect(block).height())
            block_number += 1

        painter.end()

    def highlight_current_line(self):
        if not self.app.settings.get("highlight_current_line", True):
            return
        extra_selections = []
        selection = QPlainTextEdit.ExtraSelection()
        color = QColor(self.app.colors.get("line_highlight", "#252536"))
        selection.format.setBackground(color)
        selection.format.setProperty(QTextFormat.Property.FullWidthSelection, True)
        selection.cursor = self.textCursor()
        selection.cursor.clearSelection()
        extra_selections.append(selection)
        self.setExtraSelections(extra_selections)

    def get_content(self):
        return self.toPlainText()

    def set_content(self, text):
        self.setPlainText(text)
        self.modified = False

    def refresh_colors(self):
        c = self.app.colors
        self.setStyleSheet(f"""
            QPlainTextEdit {{
                background-color: {c['editor_bg']};
                color: {c['editor_fg']};
                border: none;
                selection-background-color: {c['selection']};
                padding: 4px;
            }}
        """)
        self.highlighter.update_colors(self.app.syntax_colors)
        self.highlight_current_line()
        self.line_number_area.update()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Tab:
            self.insertPlainText(" " * self.app.settings["tab_size"])
            return
        if event.key() == Qt.Key.Key_Return:
            cursor = self.textCursor()
            line = cursor.block().text()
            indent = ""
            for ch in line:
                if ch in (" ", "\t"):
                    indent += ch
                else:
                    break
            if line.rstrip().endswith(":"):
                indent += " " * self.app.settings["tab_size"]
            super().keyPressEvent(event)
            self.insertPlainText(indent)
            return
        super().keyPressEvent(event)


class SimpleSyntaxHighlighter(QSyntaxHighlighter):
    """Regex-based syntax highlighter."""

    RULES = {
        "python": [
            ("keyword", r"\b(False|None|True|and|as|assert|async|await|break|class|continue|def|del|elif|else|except|finally|for|from|global|if|import|in|is|lambda|nonlocal|not|or|pass|raise|return|try|while|with|yield)\b"),
            ("builtin", r"\b(print|len|range|int|str|float|list|dict|set|tuple|bool|type|isinstance|input|open|super|map|filter|zip|enumerate|sorted|reversed|abs|max|min|sum|any|all)\b"),
            ("string", r'"""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\'|"(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\''),
            ("comment", r"#.*$"),
            ("number", r"\b\d+\.?\d*\b"),
            ("function", r"(?<=def\s)\w+"),
            ("class", r"(?<=class\s)\w+"),
        ],
        "javascript": [
            ("keyword", r"\b(var|let|const|function|return|if|else|for|while|do|switch|case|break|continue|new|this|class|extends|import|export|default|from|try|catch|finally|throw|async|await|typeof|instanceof|true|false|null|undefined)\b"),
            ("string", r'`[\s\S]*?`|"(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\''),
            ("comment", r"//.*$|/\*[\s\S]*?\*/"),
            ("number", r"\b\d+\.?\d*\b"),
            ("function", r"\w+(?=\s*\()"),
        ],
        "html": [
            ("tag", r"</?[a-zA-Z][a-zA-Z0-9]*"),
            ("attribute", r'\b\w+(?==)'),
            ("string", r'"[^"]*"|\'[^\']*\''),
            ("comment", r"<!--[\s\S]*?-->"),
        ],
        "css": [
            ("keyword", r"[.#]\w[\w-]*"),
            ("attribute", r"[\w-]+(?=\s*:)"),
            ("string", r'"[^"]*"|\'[^\']*\''),
            ("number", r"\b\d+\.?\d*(px|em|rem|%|vh|vw|s|ms)?\b"),
            ("comment", r"/\*[\s\S]*?\*/"),
        ],
        "json": [
            ("keyword", r'"(?:[^"\\]|\\.)*"\s*(?=:)'),
            ("string", r':\s*"(?:[^"\\]|\\.)*"'),
            ("number", r"\b\d+\.?\d*\b"),
            ("builtin", r"\b(true|false|null)\b"),
        ],
    }

    def __init__(self, document, syntax_colors, filepath=None):
        super().__init__(document)
        self.syntax_colors = syntax_colors
        self.filepath = filepath
        self.language = self._detect_language()
        self._build_rules()

    def _detect_language(self):
        if not self.filepath:
            return "python"
        ext = os.path.splitext(self.filepath)[1].lower()
        mapping = {
            ".py": "python", ".js": "javascript", ".jsx": "javascript",
            ".ts": "javascript", ".tsx": "javascript",
            ".html": "html", ".htm": "html",
            ".css": "css", ".json": "json",
        }
        return mapping.get(ext, "text")

    def _build_rules(self):
        self.highlight_rules = []
        rules = self.RULES.get(self.language, [])
        for token_type, pattern in rules:
            fmt = QTextCharFormat()
            color = self.syntax_colors.get(token_type, "#cccccc")
            fmt.setForeground(QColor(color))
            if token_type in ("keyword", "builtin"):
                fmt.setFontWeight(QFont.Weight.Bold)
            regex = QRegularExpression(pattern)
            if token_type == "comment":
                regex = QRegularExpression(pattern, QRegularExpression.PatternOption.MultilineOption)
            self.highlight_rules.append((regex, fmt))

    def update_colors(self, syntax_colors):
        self.syntax_colors = syntax_colors
        self._build_rules()
        self.rehighlight()

    def highlightBlock(self, text):
        for regex, fmt in self.highlight_rules:
            iterator = regex.globalMatch(text)
            while iterator.hasNext():
                match = iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), fmt)


class SearchWidget(QWidget):
    """Find and replace bar."""

    def __init__(self, editor_tabs):
        super().__init__()
        self.editor_tabs = editor_tabs
        self.setVisible(False)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(4)

        # Find row
        find_row = QHBoxLayout()
        find_row.addWidget(QLabel("Find:"))
        self.find_input = QLineEdit()
        self.find_input.setPlaceholderText("Search...")
        self.find_input.returnPressed.connect(self.find_next)
        self.find_input.textChanged.connect(self.find_all)
        find_row.addWidget(self.find_input, 1)

        self.match_label = QLabel("")
        find_row.addWidget(self.match_label)

        self.case_check = QCheckBox("Aa")
        self.case_check.stateChanged.connect(self.find_all)
        find_row.addWidget(self.case_check)

        prev_btn = QPushButton("<")
        prev_btn.setFixedWidth(30)
        prev_btn.clicked.connect(self.find_prev)
        find_row.addWidget(prev_btn)

        next_btn = QPushButton(">")
        next_btn.setFixedWidth(30)
        next_btn.clicked.connect(self.find_next)
        find_row.addWidget(next_btn)

        close_btn = QPushButton("x")
        close_btn.setFixedWidth(30)
        close_btn.setProperty("cssClass", "icon")
        close_btn.clicked.connect(self.hide)
        find_row.addWidget(close_btn)

        layout.addLayout(find_row)

        # Replace row
        replace_row = QHBoxLayout()
        replace_row.addWidget(QLabel("Replace:"))
        self.replace_input = QLineEdit()
        self.replace_input.setPlaceholderText("Replace with...")
        replace_row.addWidget(self.replace_input, 1)

        replace_btn = QPushButton("Replace")
        replace_btn.clicked.connect(self.replace_one)
        replace_row.addWidget(replace_btn)

        replace_all_btn = QPushButton("All")
        replace_all_btn.clicked.connect(self.replace_all)
        replace_row.addWidget(replace_all_btn)

        layout.addLayout(replace_row)

    def toggle(self):
        self.setVisible(not self.isVisible())
        if self.isVisible():
            self.find_input.setFocus()
            editor = self.editor_tabs.get_current_editor()
            if editor:
                cursor = editor.textCursor()
                if cursor.hasSelection():
                    self.find_input.setText(cursor.selectedText())

    def find_all(self):
        editor = self.editor_tabs.get_current_editor()
        if not editor:
            self.match_label.setText("")
            return
        query = self.find_input.text()
        if not query:
            self.match_label.setText("")
            return

        flags = QTextCursor.MoveOperation.Start
        count = 0
        cursor = editor.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.Start)
        editor.setTextCursor(cursor)

        find_flags = QPlainTextEdit.FindFlag(0)
        if self.case_check.isChecked():
            find_flags |= QPlainTextEdit.FindFlag.FindCaseSensitively

        temp_cursor = QTextCursor(editor.document())
        while True:
            temp_cursor = editor.document().find(query, temp_cursor, find_flags)
            if temp_cursor.isNull():
                break
            count += 1

        self.match_label.setText(f"{count} match{'es' if count != 1 else ''}")

    def find_next(self):
        self._find(forward=True)

    def find_prev(self):
        self._find(forward=False)

    def _find(self, forward=True):
        editor = self.editor_tabs.get_current_editor()
        if not editor:
            return
        query = self.find_input.text()
        if not query:
            return

        flags = QPlainTextEdit.FindFlag(0)
        if self.case_check.isChecked():
            flags |= QPlainTextEdit.FindFlag.FindCaseSensitively
        if not forward:
            flags |= QPlainTextEdit.FindFlag.FindBackward

        if not editor.find(query, flags):
            cursor = editor.textCursor()
            if forward:
                cursor.movePosition(QTextCursor.MoveOperation.Start)
            else:
                cursor.movePosition(QTextCursor.MoveOperation.End)
            editor.setTextCursor(cursor)
            editor.find(query, flags)

    def replace_one(self):
        editor = self.editor_tabs.get_current_editor()
        if not editor:
            return
        cursor = editor.textCursor()
        if cursor.hasSelection() and cursor.selectedText() == self.find_input.text():
            cursor.insertText(self.replace_input.text())
        self.find_next()

    def replace_all(self):
        editor = self.editor_tabs.get_current_editor()
        if not editor:
            return
        query = self.find_input.text()
        replacement = self.replace_input.text()
        if not query:
            return
        text = editor.toPlainText()
        if self.case_check.isChecked():
            count = text.count(query)
            text = text.replace(query, replacement)
        else:
            import re
            count = len(re.findall(re.escape(query), text, re.IGNORECASE))
            text = re.sub(re.escape(query), replacement, text, flags=re.IGNORECASE)
        editor.setPlainText(text)
        self.editor_tabs.app.set_status(f"Replaced {count} occurrences")


class EditorTabWidget(QWidget):
    """Tab widget containing multiple editor tabs."""

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.editors = {}
        self.tab_counter = 0

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Search widget
        self.search_widget = SearchWidget(self)
        layout.addWidget(self.search_widget)

        # Tab bar
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self._on_tab_changed)
        layout.addWidget(self.tabs)

    def add_welcome_tab(self):
        content = self._welcome_text()
        self.new_tab(title=f"Welcome to {APP_NAME}", content=content)
        editor = self.get_current_editor()
        if editor:
            editor.modified = False

    def _welcome_text(self):
        return f"""
    Welcome to {APP_NAME} v{APP_VERSION}
    by {APP_AUTHOR}

    Fast. Modern. Lightweight.
    No Electron. No bloat. Pure speed.

    Shortcuts:
      Ctrl+N          New File
      Ctrl+O          Open File
      Ctrl+S          Save
      Ctrl+F          Find & Replace
      Ctrl+G          Go to Line
      Ctrl+B          Toggle Sidebar
      Ctrl+`          Toggle Terminal
      Ctrl+Shift+P    Command Palette
      Ctrl+,          Settings
"""

    def new_tab(self, filepath=None, content="", title=None):
        self.tab_counter += 1
        tab_id = f"tab_{self.tab_counter}"

        editor = CodeEditor(self.app, filepath)
        if content:
            editor.set_content(content)

        if title is None:
            title = os.path.basename(filepath) if filepath else f"Untitled-{self.tab_counter}"

        idx = self.tabs.addTab(editor, title)
        self.tabs.setCurrentIndex(idx)

        self.editors[tab_id] = {
            "editor": editor,
            "filepath": filepath,
            "title": title,
        }

        editor._tab_id = tab_id
        self.app.set_status(f"Opened: {title}")
        return tab_id

    def get_current_editor(self):
        return self.tabs.currentWidget()

    def close_current_tab(self):
        idx = self.tabs.currentIndex()
        if idx >= 0:
            self.close_tab(idx)

    def close_tab(self, index):
        editor = self.tabs.widget(index)
        if editor and editor.modified:
            from PyQt6.QtWidgets import QMessageBox
            result = QMessageBox.question(
                self, "Save?",
                f"Save changes to {self.tabs.tabText(index)}?",
                QMessageBox.StandardButton.Save |
                QMessageBox.StandardButton.Discard |
                QMessageBox.StandardButton.Cancel,
            )
            if result == QMessageBox.StandardButton.Save:
                self.app.file_manager.save_file()
            elif result == QMessageBox.StandardButton.Cancel:
                return

        # Remove from editors dict
        tab_id = getattr(editor, "_tab_id", None)
        if tab_id and tab_id in self.editors:
            del self.editors[tab_id]

        self.tabs.removeTab(index)
        self.app.set_status("Tab closed")

    def toggle_search(self):
        self.search_widget.toggle()

    def apply_font(self):
        font = QFont(self.app.settings["font_family"], self.app.settings["font_size"])
        font.setFixedPitch(True)
        for i in range(self.tabs.count()):
            editor = self.tabs.widget(i)
            if isinstance(editor, CodeEditor):
                editor.setFont(font)
                editor.setTabStopDistance(
                    self.app.settings["tab_size"] * editor.fontMetrics().horizontalAdvance(" ")
                )
                editor.update_line_number_area_width(0)
                editor.line_number_area.update()

    def refresh_all(self):
        for i in range(self.tabs.count()):
            editor = self.tabs.widget(i)
            if isinstance(editor, CodeEditor):
                editor.refresh_colors()

    def mark_modified(self, editor):
        for i in range(self.tabs.count()):
            if self.tabs.widget(i) == editor:
                title = self.tabs.tabText(i)
                if not title.startswith("● "):
                    self.tabs.setTabText(i, f"● {title}")
                break

    def mark_saved(self, editor, new_title=None):
        for i in range(self.tabs.count()):
            if self.tabs.widget(i) == editor:
                title = new_title or self.tabs.tabText(i).lstrip("● ")
                self.tabs.setTabText(i, title)
                editor.modified = False
                break

    def _on_tab_changed(self, index):
        editor = self.tabs.widget(index)
        if isinstance(editor, CodeEditor) and editor.filepath:
            ext = os.path.splitext(editor.filepath)[1].lower()
            lang = SUPPORTED_EXTENSIONS.get(ext, "Text")
            self.app.statusbar.update_file_type(lang)