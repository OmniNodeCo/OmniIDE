"""Editor tab widget with syntax highlighting — PyQt6."""

import os
import re

from PyQt6.QtWidgets import (
    QWidget, QTabWidget, QVBoxLayout, QHBoxLayout, QPlainTextEdit,
    QLabel, QFrame, QLineEdit, QPushButton, QCheckBox, QTextEdit,
    QMenu, QTextBrowser,
)
from PyQt6.QtCore import Qt, QRect, QSize, QRegularExpression, QTimer
from PyQt6.QtGui import (
    QFont, QColor, QPainter, QTextFormat, QSyntaxHighlighter,
    QTextCharFormat, QTextCursor, QDragEnterEvent, QAction,
)

from src.config import APP_NAME, APP_VERSION, APP_AUTHOR, SUPPORTED_EXTENSIONS
from src.core import code_actions


class LineNumberArea(QWidget):
    """Line number gutter."""

    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor

    def sizeHint(self):
        return QSize(self.editor.line_number_area_width(), 0)

    def paintEvent(self, event):
        self.editor.line_number_area_paint_event(event)


class MarkdownPreview(QTextBrowser):
    """Read-only HTML preview tab."""

    def __init__(self, app, html, title):
        super().__init__()
        self.app = app
        self.filepath = None
        self.modified = False
        self.setOpenExternalLinks(False)
        self.setHtml(html)
        self.anchorClicked.connect(self._on_anchor)
        c = app.colors
        self.setStyleSheet(f"""
            QTextBrowser {{
                background-color: {c['editor_bg']};
                color: {c['editor_fg']};
                border: none;
                padding: 12px;
            }}
        """)

    def _on_anchor(self, url):
        self.app.set_status(f"Link: {url.toString()}")


PAIRS = {"(": ")", "[": "]", "{": "}"}
PAIR_REVERSED = {v: k for k, v in PAIRS.items()}


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
        self.setTabStopDistance(
            app.settings["tab_size"] * self.fontMetrics().horizontalAdvance(" ")
        )

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
        self.cursorPositionChanged.connect(self._match_bracket)
        self.textChanged.connect(self._on_text_changed)

        # Bracket matching refresh (throttled)
        self._bracket_timer = QTimer(self)
        self._bracket_timer.setSingleShot(True)
        self._bracket_timer.setInterval(80)
        self._bracket_timer.timeout.connect(self._match_bracket)
        self.textChanged.connect(self._bracket_timer.start)

        self.update_line_number_area_width(0)
        self.highlight_current_line()

        # Syntax highlighter
        self.highlighter = SimpleSyntaxHighlighter(
            self.document(), app.syntax_colors, filepath
        )

    # ── Signals ────────────────────────────────────────────────────
    def _on_text_changed(self):
        self.modified = True
        editor_tabs = getattr(self.app, "editor_tabs", None)
        if editor_tabs is not None:
            editor_tabs.mark_modified(self)
        statusbar = getattr(self.app, "statusbar", None)
        if statusbar is not None:
            statusbar.update_cursor(self)

    # ── Line numbers ───────────────────────────────────────────────
    def line_number_area_width(self):
        digits = max(1, len(str(self.blockCount())))
        return 10 + self.fontMetrics().horizontalAdvance("9") * (digits + 1)

    def update_line_number_area_width(self, _):
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def update_line_number_area(self, rect, dy):
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(
                0, rect.y(), self.line_number_area.width(), rect.height()
            )
        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(
            QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height())
        )

    def line_number_area_paint_event(self, event):
        painter = QPainter(self.line_number_area)
        c = self.app.colors
        painter.fillRect(event.rect(), QColor(c["bg_secondary"]))

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = round(
            self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        )
        bottom = top + round(self.blockBoundingRect(block).height())

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.setPen(QColor(c["fg_secondary"]))
                painter.setFont(self.font())
                painter.drawText(
                    0, top,
                    self.line_number_area.width() - 6,
                    self.fontMetrics().height(),
                    Qt.AlignmentFlag.AlignRight, number,
                )
            block = block.next()
            top = bottom
            bottom = top + round(self.blockBoundingRect(block).height())
            block_number += 1

        painter.end()

    # ── Selections ─────────────────────────────────────────────────
    def highlight_current_line(self):
        extra_selections = self._base_extra_selections()

        if self.app.settings.get("highlight_current_line", True):
            selection = QTextEdit.ExtraSelection()
            color = QColor(self.app.colors.get("line_highlight", "#252536"))
            selection.format.setBackground(color)
            selection.format.setProperty(
                QTextFormat.Property.FullWidthSelection, True
            )
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extra_selections.append(selection)

        self.setExtraSelections(extra_selections)

    def _base_extra_selections(self):
        """JSON error marker + matched bracket highlight."""
        extra = []

        statusbar = getattr(self.app, "statusbar", None)
        err = getattr(statusbar, "json_error", None) if statusbar else None
        if err and self.filepath and \
                os.path.splitext(self.filepath)[1].lower() == ".json":
            lineno, _col = err
            block = self.document().findBlockByLineNumber(lineno - 1)
            sel = QTextEdit.ExtraSelection()
            err_color = QColor(self.app.colors.get("error", "#f38ba8"))
            err_color.setAlpha(90)
            sel.format.setBackground(err_color)
            sel.cursor = QTextCursor(block)
            sel.cursor.movePosition(QTextCursor.MoveOperation.EndOfBlock,
                                    QTextCursor.MoveMode.KeepAnchor)
            extra.append(sel)

        if self.app.settings.get("smart_brackets", True):
            pos = self.textCursor().position()
            ch = self.toPlainText()[pos - 1:pos] if pos else ""
            match_pos = -1
            if ch in PAIRS:
                idx = self._find_closing(ch, pos)
                if idx >= 0:
                    match_pos = idx
            elif ch in PAIR_REVERSED:
                idx = self._find_opening(PAIR_REVERSED[ch], pos - 1)
                if idx >= 0:
                    match_pos = idx

            if match_pos >= 0:
                sel = QTextEdit.ExtraSelection()
                sel.format.setBackground(
                    QColor(self.app.colors.get("selection", "#45475a"))
                )
                sel.cursor = self.textCursor()
                sel.cursor.setPosition(match_pos)
                sel.cursor.movePosition(QTextCursor.MoveOperation.Right,
                                        QTextCursor.MoveMode.KeepAnchor)
                extra.append(sel)
        return extra

    def _find_closing(self, open_ch, start):
        text = self.toPlainText()
        depth = 0
        for i in range(start, len(text)):
            c = text[i]
            if c == open_ch:
                depth += 1
            elif c == PAIRS[open_ch]:
                depth -= 1
                if depth == 0:
                    return i
        return -1

    def _find_opening(self, close_ch, end):
        text = self.toPlainText()
        depth = 0
        open_ch = PAIR_REVERSED[close_ch]
        for i in range(end, -1, -1):
            c = text[i]
            if c == close_ch:
                depth += 1
            elif c == open_ch:
                depth -= 1
                if depth == 0:
                    return i
        return -1

    def _match_bracket(self):
        self.highlight_current_line()

    # ── Content ────────────────────────────────────────────────────
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

    # ── Navigation ─────────────────────────────────────────────────
    def goto_line(self, line):
        cursor = self.textCursor()
        block = self.document().findBlockByLineNumber(max(0, line - 1))
        cursor.setPosition(block.position())
        cursor.movePosition(QTextCursor.MoveOperation.Down,
                            QTextCursor.MoveMode.KeepAnchor)
        self.setTextCursor(cursor)
        self.centerCursor()

    # ── Code actions (pure functions from src.core.code_actions) ──
    def _apply_action(self, func, *args, **kwargs):
        text = self.toPlainText()
        cursor = self.textCursor()
        # Resolve the line from the selection start so that line
        # selections (e.g. from Go to Line) still target the right line.
        start_pos = cursor.selectionStart()
        line_no = self.document().findBlock(start_pos).blockNumber() + 1
        new_text = func(text, line_no, *args, **kwargs)
        if new_text == text:
            return
        cursor = self.textCursor()
        pos = cursor.position()
        self.setPlainText(new_text)
        # Restore cursor near where it was
        new_cursor = self.textCursor()
        new_cursor.setPosition(min(pos, len(new_text)))
        self.setTextCursor(new_cursor)

    def duplicate_line(self):
        self._apply_action(code_actions.duplicate_line)

    def delete_line(self):
        self._apply_action(code_actions.delete_line)

    def move_line_up(self):
        self._apply_action(code_actions.move_line_up)

    def move_line_down(self):
        self._apply_action(code_actions.move_line_down)

    def toggle_comment(self):
        self._apply_action(code_actions.toggle_comment_line, self.filepath)

    def sort_lines(self):
        self._apply_action(code_actions.sort_lines)

    def indent_lines(self):
        self._apply_action(
            code_actions.indent_lines,
            self.app.settings["tab_size"],
            self.app.settings.get("indent_with_tabs", False),
        )

    def outdent_lines(self):
        self._apply_action(
            code_actions.outdent_lines,
            self.app.settings["tab_size"],
            self.app.settings.get("indent_with_tabs", False),
        )

    # ── Key handling ───────────────────────────────────────────────
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Tab:
            if self.textCursor().hasSelection():
                # Indent/outdent selected lines
                if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                    self.outdent_lines()
                else:
                    self.indent_lines()
            else:
                fill = "\t" if self.app.settings.get("indent_with_tabs") \
                    else " " * self.app.settings["tab_size"]
                self.insertPlainText(fill)
            return

        if event.key() == Qt.Key.Key_Backspace:
            # Smart brackets: delete empty pair when cursor is between them
            if self.app.settings.get("smart_brackets", True):
                cursor = self.textCursor()
                if not cursor.hasSelection():
                    text = self.toPlainText()
                    pos = cursor.position()
                    if 0 < pos < len(text):
                        left, right = text[pos - 1], text[pos]
                        if left in PAIRS and PAIRS[left] == right:
                            self.setPlainText(text[:pos - 1] + text[pos + 1:])
                            c = self.textCursor()
                            c.setPosition(pos - 1)
                            self.setTextCursor(c)
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
            if indent:
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
            ("attribute", r"\b\w+(?==)"),
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
        "markdown": [
            ("class", r"^#{1,6}\s.*$"),
            ("keyword", r"\*\*[^*]+\*\*"),
            ("string", r"`[^`]+`"),
            ("function", r"\[([^\]]*)\]\([^)]+\)"),
            ("builtin", r"^>.*$"),
            ("attribute", r"^[-*+]\s.*$"),
        ],
        "yaml": [
            ("keyword", r"^\s*[\w-]+(?=\s*:)"),
            ("string", r'".*?"|\'.*?\''),
            ("comment", r"#.*$"),
            ("number", r"\b\d+\.?\d*\b"),
            ("builtin", r"\b(true|false|null|yes|no)\b"),
        ],
        "rust": [
            ("keyword", r"\b(fn|let|mut|if|else|match|for|while|loop|impl|struct|enum|trait|use|mod|pub|return|const|static|where|async|await|move|ref|self|Self|crate|super)\b"),
            ("string", r'"(?:[^"\\]|\\.)*"'),
            ("comment", r"//.*$|/\*[\s\S]*?\*/"),
            ("number", r"\b\d+\.?\d*\b"),
            ("function", r"\w+(?=\s*\()"),
        ],
        "go": [
            ("keyword", r"\b(func|var|const|if|else|for|range|return|type|struct|interface|map|chan|go|defer|package|import|switch|case|break|continue|select|fallthrough|goto)\b"),
            ("string", r'"(?:[^"\\]|\\.)*"|`[^`]*`'),
            ("comment", r"//.*$|/\*[\s\S]*?\*/"),
            ("number", r"\b\d+\.?\d*\b"),
            ("function", r"\w+(?=\s*\()"),
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
            ".css": "css", ".json": "json", ".md": "markdown",
            ".yaml": "yaml", ".yml": "yaml", ".rs": "rust", ".go": "go",
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
            if token_type in ("comment", "class", "builtin", "attribute"):
                regex = QRegularExpression(
                    pattern, QRegularExpression.PatternOption.MultilineOption
                )
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
                self.setFormat(
                    match.capturedStart(), match.capturedLength(), fmt
                )


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

        self.word_check = QCheckBox("W")
        self.word_check.setToolTip("Whole word")
        self.word_check.stateChanged.connect(self._on_flags_changed)
        find_row.addWidget(self.word_check)

        self.regex_check = QCheckBox(".*")
        self.regex_check.setToolTip("Regular expression")
        self.regex_check.stateChanged.connect(self._on_flags_changed)
        find_row.addWidget(self.regex_check)

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

    def _on_flags_changed(self):
        self.find_all()

    def toggle(self):
        self.setVisible(not self.isVisible())
        if self.isVisible():
            self.find_input.setFocus()
            editor = self.editor_tabs.get_current_editor()
            if editor:
                cursor = editor.textCursor()
                if cursor.hasSelection():
                    self.find_input.setText(cursor.selectedText())

    def _query_text(self):
        query = self.find_input.text()
        if self.regex_check.isChecked():
            return query
        return re.escape(query)

    def find_all(self):
        editor = self.editor_tabs.get_current_editor()
        if not editor:
            self.match_label.setText("")
            return

        raw = self.find_input.text()
        if not raw:
            self.match_label.setText("")
            return

        try:
            rx = re.compile(self._query_text(),
                            re.IGNORECASE if not self.case_check.isChecked() else 0)
        except re.error:
            self.match_label.setText("bad regex")
            return
        if self.word_check.isChecked():
            rx = re.compile(rf"(?<!\w)({rx.pattern})(?!\w)",
                            re.IGNORECASE if not self.case_check.isChecked() else 0)

        count = 0
        for line in editor.toPlainText().split("\n"):
            count += len(rx.findall(line))
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

        find_flags = QTextEdit.FindFlag(0)
        if self.case_check.isChecked():
            find_flags |= QTextEdit.FindFlag.FindCaseSensitively
        if not forward:
            find_flags |= QTextEdit.FindFlag.FindBackward
        if self.word_check.isChecked():
            find_flags |= QTextEdit.FindFlag.FindWholeWords

        # Plain text search (regex matching in QPlainTextEdit.find is not
        # available; whole word + case cover most needs, and the status bar
        # shows regex match counts via find_all)
        if not self.regex_check.isChecked():
            if not editor.find(query, find_flags):
                cursor = editor.textCursor()
                if forward:
                    cursor.movePosition(QTextCursor.MoveOperation.Start)
                else:
                    cursor.movePosition(QTextCursor.MoveOperation.End)
                editor.setTextCursor(cursor)
                editor.find(query, find_flags)
            return

        # Regex search: scan the document ourselves
        try:
            rx = re.compile(query,
                            re.IGNORECASE if not self.case_check.isChecked() else 0)
        except re.error:
            return

        text = editor.toPlainText()
        cursor_pos = editor.textCursor().position()
        matches = [(m.start(), m.end()) for m in rx.finditer(text)]
        if not matches:
            return
        if forward:
            match = next(((s, e) for s, e in matches if e > cursor_pos), None) \
                or matches[0]
        else:
            match = next(((s, e) for s, e in reversed(matches) if s < cursor_pos), None) \
                or matches[-1]
        c = editor.textCursor()
        c.setPosition(match[0])
        c.setPosition(match[1], QTextCursor.MoveMode.KeepAnchor)
        editor.setTextCursor(c)
        editor.ensureCursorVisible()

    def replace_one(self):
        editor = self.editor_tabs.get_current_editor()
        if not editor:
            return
        cursor = editor.textCursor()
        if cursor.hasSelection():
            sel = cursor.selectedText()
            raw = self.find_input.text()
            try:
                rx = re.compile(self._query_text(),
                                re.IGNORECASE if not self.case_check.isChecked() else 0)
            except re.error:
                rx = None
            if rx and rx.fullmatch(sel) or (not rx and sel == raw):
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
        flags = 0 if self.case_check.isChecked() else re.IGNORECASE
        try:
            pattern = re.compile(self._query_text(), flags)
            if self.word_check.isChecked():
                pattern = re.compile(
                    rf"(?<!\w)({pattern.pattern})(?!\w)", flags
                )
            count = len(pattern.findall(text))
            text = pattern.sub(
                lambda m: replacement, text
            )
        except re.error:
            count = 0

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
        self.tabs.setMovable(True)
        self.tabs.setAcceptDrops(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self._on_tab_changed)
        self.tabs.tabBarDoubleClicked.connect(self._tab_double_click)
        self.tabs.tabBar().setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tabs.tabBar().customContextMenuRequested.connect(self._tab_context_menu)
        layout.addWidget(self.tabs)

        # Drag & drop
        self.setAcceptDrops(True)

    # ── Tabs ───────────────────────────────────────────────────────
    def add_welcome_tab(self):
        content = self._welcome_text()
        self.new_tab(title=f"Welcome to {APP_NAME}", content=content)
        editor = self.get_current_editor()
        if editor:
            editor.modified = False

    def _welcome_text(self):
        recent = self.app.recent_files_manager.get_all()
        recent_text = "\n".join(f"    {f}" for f in recent[:8]) or "    (none yet)"
        return f"""
    Welcome to {APP_NAME} v{APP_VERSION}
    by {APP_AUTHOR}

    Fast. Modern. Lightweight.
    No Electron. No bloat. Pure speed.

    Quick Start:
      Ctrl+O          Open File
      Ctrl+P          Quick Open (fuzzy file search)
      Ctrl+Shift+F    Search in Files
      Ctrl+N          New File
      Ctrl+S          Save
      Ctrl+Shift+V    Markdown Preview
      Ctrl+`          Toggle Terminal

    Shortcuts:
      Ctrl+F          Find & Replace  (Aa / W / .* options)
      Ctrl+G          Go to Line
      Ctrl+/          Toggle Comment
      Ctrl+D          Duplicate Line
      Ctrl+Shift+D    Delete Line
      Alt+Up/Down     Move Line
      Ctrl+Shift+O    Sort Lines
      Ctrl+B          Toggle Sidebar
      Ctrl+Shift+P    Command Palette
      Ctrl+,          Settings

    Recent Files:
{recent_text}
"""

    def new_tab(self, filepath=None, content="", title=None):
        self.tab_counter += 1
        tab_id = f"tab_{self.tab_counter}"

        editor = CodeEditor(self.app, filepath)
        if content:
            editor.set_content(content)

        if title is None:
            title = (
                os.path.basename(filepath) if filepath
                else f"Untitled-{self.tab_counter}"
            )

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

    def new_preview_tab(self, html, title):
        """Add a read-only HTML (markdown preview) tab."""
        self.tab_counter += 1
        tab_id = f"tab_{self.tab_counter}"
        preview = MarkdownPreview(self.app, html, title)
        idx = self.tabs.addTab(preview, title)
        self.tabs.setCurrentIndex(idx)
        self.editors[tab_id] = {"editor": preview, "filepath": None, "title": title}
        preview._tab_id = tab_id
        return tab_id

    def all_editors(self):
        return [self.tabs.widget(i) for i in range(self.tabs.count())]

    def get_current_editor(self):
        widget = self.tabs.currentWidget()
        if isinstance(widget, (CodeEditor, MarkdownPreview)):
            return widget
        return None

    def get_current_code_editor(self):
        widget = self.tabs.currentWidget()
        if isinstance(widget, CodeEditor):
            return widget
        return None

    def find_editor_for_file(self, filepath):
        if not filepath:
            return None
        filepath = os.path.abspath(filepath)
        for editor in self.all_editors():
            ep = getattr(editor, "filepath", None)
            if ep and os.path.abspath(ep) == filepath:
                return editor
        return None

    def set_editor(self, editor):
        for i in range(self.tabs.count()):
            if self.tabs.widget(i) is editor:
                self.tabs.setCurrentIndex(i)
                break

    def close_current_tab(self):
        idx = self.tabs.currentIndex()
        if idx >= 0:
            self.close_tab(idx)

    def close_all_tabs(self):
        while self.tabs.count() > 0:
            self.close_tab_silent(0)
        self.app.set_status("Closed all tabs")

    def close_other_tabs(self):
        keep = self.tabs.currentIndex()
        idx = 0
        while idx < self.tabs.count():
            if idx != keep:
                self.close_tab_silent(idx)
            else:
                idx += 1

    def close_tab_silent(self, index):
        """Close a tab without save prompts (used for close all)."""
        editor = self.tabs.widget(index)
        tab_id = getattr(editor, "_tab_id", None)
        if tab_id and tab_id in self.editors:
            del self.editors[tab_id]
        self.tabs.removeTab(index)
        if hasattr(editor, "deleteLater"):
            editor.deleteLater()

    def _confirm_save(self, index):
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
            return False
        return True

    def close_tab(self, index):
        editor = self.tabs.widget(index)
        if isinstance(editor, CodeEditor) and getattr(editor, "modified", False):
            if not self._confirm_save(index):
                return
        tab_id = getattr(editor, "_tab_id", None)
        if tab_id and tab_id in self.editors:
            del self.editors[tab_id]

        self.tabs.removeTab(index)
        if hasattr(editor, "deleteLater"):
            editor.deleteLater()
        self.app.set_status("Tab closed")

    def _tab_double_click(self, index):
        """Double-click tab to close it."""
        self.close_tab(index)

    def _tab_context_menu(self, pos):
        index = self.tabs.tabBar().tabAt(pos)
        if index < 0:
            return
        menu = QMenu(self)
        act_close = menu.addAction("Close")
        act_close.triggered.connect(lambda: self.close_tab(index))
        menu.addSeparator()
        act_others = menu.addAction("Close Others")
        act_others.triggered.connect(lambda: (
            self.tabs.setCurrentIndex(index), self.close_other_tabs()))
        act_all = menu.addAction("Close All")
        act_all.triggered.connect(self.close_all_tabs)
        act_copy = menu.addAction("Copy File Path")
        act_copy.triggered.connect(lambda: self._copy_tab_path(index))
        menu.exec(self.tabs.tabBar().mapToGlobal(pos))

    def _copy_tab_path(self, index):
        editor = self.tabs.widget(index)
        path = getattr(editor, "filepath", None)
        if path:
            self.app.clipboard().setText(path)
            self.app.set_status(f"Copied: {path}")

    # ── Search / font / theme ──────────────────────────────────────
    def toggle_search(self):
        self.search_widget.toggle()

    def apply_font(self):
        font = QFont(
            self.app.settings["font_family"],
            self.app.settings["font_size"],
        )
        font.setFixedPitch(True)

        for i in range(self.tabs.count()):
            editor = self.tabs.widget(i)
            if isinstance(editor, CodeEditor):
                editor.setFont(font)
                editor.setTabStopDistance(
                    self.app.settings["tab_size"]
                    * editor.fontMetrics().horizontalAdvance(" ")
                )
                editor.update_line_number_area_width(0)
                editor.line_number_area.update()

    def apply_word_wrap(self):
        for i in range(self.tabs.count()):
            editor = self.tabs.widget(i)
            if isinstance(editor, CodeEditor):
                editor.setLineWrapMode(
                    QPlainTextEdit.LineWrapMode.WidgetWidth
                    if self.app.settings["word_wrap"]
                    else QPlainTextEdit.LineWrapMode.NoWrap
                )

    def refresh_all(self):
        for i in range(self.tabs.count()):
            editor = self.tabs.widget(i)
            if isinstance(editor, CodeEditor):
                editor.refresh_colors()
                editor.highlight_current_line()

    def mark_modified(self, editor):
        for i in range(self.tabs.count()):
            if self.tabs.widget(i) is editor:
                title = self.tabs.tabText(i)
                if not title.startswith("● "):
                    self.tabs.setTabText(i, f"● {title}")
                break

    def mark_saved(self, editor, new_title=None):
        for i in range(self.tabs.count()):
            if self.tabs.widget(i) is editor:
                title = new_title or self.tabs.tabText(i)
                if title.startswith("● "):
                    title = title[2:]
                self.tabs.setTabText(i, title)
                editor.modified = False
                break

    def _on_tab_changed(self, index):
        widget = self.tabs.widget(index)
        statusbar = getattr(self.app, "statusbar", None)
        if statusbar is not None:
            statusbar.update_cursor_position_for(widget)
        if isinstance(widget, CodeEditor) and widget.filepath:
            ext = os.path.splitext(widget.filepath)[1].lower()
            self.app.statusbar.update_file_type(
                SUPPORTED_EXTENSIONS.get(ext, "Text")
            )
        # Auto save on tab switch
        if (self.app.settings.get("auto_save") and index >= 0):
            self.app.file_manager.autosave_tick()

    # ── Drag & drop ────────────────────────────────────────────────
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if os.path.isfile(path):
                self.app.file_manager.open_file(path)
            elif os.path.isdir(path):
                self.app.open_project(path)


class BreadcrumbBar(QWidget):
    """Breadcrumbs for the current file path."""

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.setFixedHeight(26)
        self._parts = []
        self._build()

    def _build(self):
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(10, 0, 10, 0)
        self.layout.setSpacing(2)
        c = self.app.colors
        self.setStyleSheet(f"""
            BreadcrumbBar {{ background-color: {c['bg_secondary']}; }}
        """)
        root_label = QLabel("No file")
        root_label.setStyleSheet(f"color: {c['fg_secondary']}; font-size: 11px;")
        self._crumbs = [root_label]
        self.layout.addWidget(root_label)
        self.layout.addStretch()

    def refresh(self):
        # Clear old crumbs
        for part in self._parts:
            self.layout.removeWidget(part)
            part.deleteLater()
        self._parts = []
        self._crumbs[0].setText("No file")
        self._crumbs[0].setStyleSheet(
            f"color: {self.app.colors['fg_secondary']};")

        editor = self.app.editor_tabs.get_current_code_editor()
        path = getattr(editor, "filepath", None) if editor else None
        if not path:
            return

        # Build the path segments (file name first, then parent dirs up)
        root = os.path.abspath(path)
        segments = [(os.path.basename(root) or root, root)]
        cur = os.path.dirname(root)
        while cur and len(segments) < 8:
            name = os.path.basename(cur) or cur
            segments.insert(0, (name, cur))
            parent = os.path.dirname(cur)
            if parent == cur:
                break
            cur = parent

        insert_at = 1  # after the fixed "No file"/root label
        for i, (name, p) in enumerate(segments):
            btn = QPushButton(name)
            btn.setFlat(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(
                f"QPushButton {{ border: none; color: {self.app.colors['fg_primary'] if i == len(segments) - 1 else self.app.colors['fg_secondary']}; "
                f"padding: 2px 6px; border-radius: 4px; font-size: 11px; }}"
                f"QPushButton:hover {{ background-color: {self.app.colors['bg_tertiary']}; "
                f"color: {self.app.colors['accent']}; }}"
            )
            btn.clicked.connect(lambda _=False, pp=p: self._jump_to(pp))
            self._crumbs.append(btn)
            self.layout.insertWidget(insert_at, btn)
            insert_at += 1
            if i < len(segments) - 1:
                sep = QLabel("›")
                sep.setStyleSheet(f"color: {self.app.colors['fg_secondary']};")
                self._crumbs.append(sep)
                self.layout.insertWidget(insert_at, sep)
                insert_at += 1
        self._crumbs[0].setVisible(False)

    def _jump_to(self, path):
        if os.path.isdir(path):
            self.app.sidebar.file_tree.expand_to(path)

    def refresh_colors(self):
        c = self.app.colors
        self.setStyleSheet(f"""
            BreadcrumbBar {{ background-color: {c['bg_secondary']}; }}
        """)
