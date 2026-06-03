"""Code editor widget with line numbers and syntax highlighting."""

import tkinter as tk
import ttkbootstrap as ttk
from src.core.syntax_highlighter import SyntaxHighlighter


class LineNumbers(tk.Canvas):
    """Line number gutter for the editor."""

    def __init__(self, parent, editor, colors, **kwargs):
        super().__init__(parent, width=50, highlightthickness=0, **kwargs)
        self.editor = editor
        self.colors = colors
        self.configure(bg=colors["bg_secondary"], bd=0)
        self.font = None

    def set_font(self, font):
        self.font = font

    def redraw(self, *args):
        self.delete("all")
        i = self.editor.index("@0,0")
        while True:
            dline = self.editor.dlineinfo(i)
            if dline is None:
                break
            y = dline[1]
            line_num = str(i).split(".")[0]
            self.create_text(
                45, y,
                anchor="ne",
                text=line_num,
                fill=self.colors["fg_secondary"],
                font=self.font or ("Consolas", 12),
            )
            i = self.editor.index(f"{i}+1line")


class CodeEditor(tk.Text):
    """Main code editor text widget."""

    def __init__(self, parent, app, filepath=None, **kwargs):
        self.app = app
        self.filepath = filepath
        self.colors = app.colors
        self.modified = False

        font_family = app.settings["font_family"]
        font_size = app.settings["font_size"]

        super().__init__(
            parent,
            font=(font_family, font_size),
            bg=self.colors["editor_bg"],
            fg=self.colors["editor_fg"],
            insertbackground=self.colors["accent"],
            selectbackground=self.colors["selection"],
            selectforeground=self.colors["fg_primary"],
            relief="flat",
            borderwidth=0,
            padx=8,
            pady=6,
            undo=True,
            maxundo=-1,
            wrap="none" if not app.settings["word_wrap"] else "word",
            tabs=(f'{app.settings["tab_size"]}c',),
            **kwargs,
        )

        self.highlighter = SyntaxHighlighter(self, app.syntax_colors, filepath)

        self.bind("<<Modified>>", self._on_modified)
        self.bind("<KeyRelease>", self._on_key_release)
        self.bind("<Return>", self._auto_indent)
        self.bind("<Tab>", self._insert_spaces)

    def _on_modified(self, event=None):
        if self.edit_modified():
            self.modified = True
            self.app.tab_manager.mark_modified(self)
            self.edit_modified(False)

    def _on_key_release(self, event=None):
        self.highlighter.highlight()
        self.app.statusbar.update_cursor_position(self)

    def _auto_indent(self, event=None):
        if not self.app.settings["auto_indent"]:
            return

        line = self.get("insert linestart", "insert lineend")
        indent = ""
        for ch in line:
            if ch in (" ", "\t"):
                indent += ch
            else:
                break

        if line.rstrip().endswith(":"):
            indent += " " * self.app.settings["tab_size"]

        self.insert("insert", "\n" + indent)
        return "break"

    def _insert_spaces(self, event=None):
        spaces = " " * self.app.settings["tab_size"]
        self.insert("insert", spaces)
        return "break"

    def get_content(self):
        return self.get("1.0", "end-1c")

    def set_content(self, text):
        self.delete("1.0", "end")
        self.insert("1.0", text)
        self.highlighter.highlight()
        self.edit_modified(False)
        self.modified = False

    def refresh_colors(self):
        self.colors = self.app.colors
        self.configure(
            bg=self.colors["editor_bg"],
            fg=self.colors["editor_fg"],
            insertbackground=self.colors["accent"],
            selectbackground=self.colors["selection"],
        )
        self.highlighter.syntax_colors = self.app.syntax_colors
        self.highlighter.highlight()