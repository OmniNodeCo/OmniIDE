"""Bar-style minimap — a compact document overview. — PyQt6

Draws each line of the document as a thin bar (width proportional to
line length), highlights the current line, and overlays the visible
viewport. Click or drag to jump. Throttled redraws keep it fast on big
files.
"""

from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush


class Minimap(QWidget):
    """Compact overview of the attached editor's content."""

    LINE_SPACING = 1
    MIN_PX_PER_LINE = 1
    MAX_RENDER_LINES = 20000

    def __init__(self, app, parent=None):
        super().__init__(parent)
        self.app = app
        self.editor = None
        self._dirty = False
        self._press_line = None

        self.setFixedWidth(54)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setAutoFillBackground(True)

        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.setInterval(250)
        self._timer.timeout.connect(self._repaint_if_dirty)

    def attach(self, editor):
        """Attach to a CodeEditor (or None to detach)."""
        self._detach()
        self.editor = editor
        if editor is None:
            self.hide()
            return
        self._connect(editor)
        self.show()
        self.update()

    def _detach(self):
        if self.editor is None:
            return
        editor = self.editor
        self.editor = None
        try:
            editor.textChanged.disconnect(self._on_text_changed)
            editor.blockCountChanged.disconnect(self._on_block_count)
            sb = editor.verticalScrollBar()
            if sb:
                try:
                    sb.valueChanged.disconnect(self._on_scroll)
                except (TypeError, RuntimeError):
                    pass
        except (TypeError, RuntimeError):
            pass

    def _connect(self, editor):
        editor.textChanged.connect(self._on_text_changed)
        editor.blockCountChanged.connect(self._on_block_count)
        sb = editor.verticalScrollBar()
        if sb:
            try:
                sb.valueChanged.connect(self._on_scroll)
            except (TypeError, RuntimeError):
                pass

    def _on_text_changed(self):
        self._dirty = True
        self._timer.start()

    def _on_block_count(self, _):
        self._dirty = True
        self._timer.start()

    def _on_scroll(self, _value):
        if self.isVisible():
            self.update()

    def _repaint_if_dirty(self):
        if self._dirty:
            self._dirty = False
            self.update()

    # ── Geometry helpers ───────────────────────────────────────────
    def _px_per_line(self):
        count = self.editor.blockCount() if self.editor else 1
        if count <= 0:
            return self.MIN_PX_PER_LINE
        fit = self.height() / count
        return max(self.MIN_PX_PER_LINE, int(fit) or self.MIN_PX_PER_LINE)

    def _total_px(self):
        count = self.editor.blockCount() if self.editor else 1
        return count * self._px_per_line() + 8

    def line_at_y(self, y):
        if not self.editor:
            return 1
        p = self._px_per_line()
        return max(1, int((y - 4) / p) + 1)

    # ── Mouse ──────────────────────────────────────────────────────
    def mousePressEvent(self, event):
        if not self.editor or event.button() != Qt.MouseButton.LeftButton:
            return
        self._press_line = self.line_at_y(event.position().y())
        self._jump(self._press_line)

    def mouseMoveEvent(self, event):
        if self._press_line is not None and self.editor:
            self._jump(self.line_at_y(event.position().y()))

    def mouseReleaseEvent(self, _event):
        self._press_line = None

    def _jump(self, line_no):
        if not self.editor:
            return
        cursor = self.editor.textCursor()
        block = self.editor.document().findBlockByLineNumber(
            max(0, min(line_no, self.editor.blockCount()) - 1)
        )
        cursor.setPosition(block.position())
        self.editor.setTextCursor(cursor)
        self.editor.ensureCursorVisible()
        self.update()

    # ── Paint ──────────────────────────────────────────────────────
    def paintEvent(self, _event):
        if not self.editor:
            return
        painter = QPainter(self)
        c = self.app.colors
        painter.fillRect(self.rect(), QColor(c["editor_bg"]))
        painter.fillRect(0, 0, self.width(), 2, QColor(c["border"]))
        painter.fillRect(0, self.height() - 2, self.width(), 2,
                         QColor(c["border"]))

        p = self._px_per_line()
        doc = self.editor.document()
        count = min(doc.blockCount(), self.MAX_RENDER_LINES)

        fg = QColor(c["fg_secondary"])
        fg.setAlpha(150)
        accent = QColor(c["accent"])

        current_block = self.editor.textCursor().blockNumber()
        first_visible = self.editor.firstVisibleBlock().blockNumber()
        last_visible_block = self.editor.document().findBlock(
            self.editor.firstVisibleBlock().position()
            + self.editor.viewport().height()
        )
        last_visible = min(last_visible_block.blockNumber(), count - 1)

        bar_max = self.width() - 10
        for i in range(count):
            y = 4 + i * p
            if y > self.height():
                break
            block = doc.findBlockByLineNumber(i)
            text = block.text()
            stripped = text.lstrip()
            if not stripped:
                continue
            indent = len(text) - len(stripped)
            # Bar width ∝ visible chars, indented a little
            width = min(bar_max, max(2, int(len(stripped) * 1.1)))
            x = 5 + min(10, indent)
            if i == current_block:
                painter.fillRect(x, y, width, max(1, p), accent)
            else:
                painter.fillRect(x, y, width, max(1, p), fg)

        # Viewport overlay
        if count > 0:
            top = 4 + first_visible * p
            bottom = 4 + (last_visible + 1) * p
            pen = QPen(QColor(c["accent"]))
            pen.setWidth(1)
            painter.setPen(pen)
            brush_color = QColor(c["accent"])
            brush_color.setAlpha(30)
            painter.setBrush(QBrush(brush_color))
            painter.drawRect(2, top, self.width() - 4, max(2, bottom - top))

        painter.end()
