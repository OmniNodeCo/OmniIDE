"""Find and Replace with SVG icons."""

import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from src.utils.icon_manager import IconManager


class SearchBar:
    """Find and Replace bar with SVG icons."""

    def __init__(self, parent, app):
        self.app = app
        self.visible = False
        self.matches = []
        self.current_match = -1
        self.icon_mgr = IconManager()
        self._icon_refs = []

        self.frame = ttk.Frame(parent)

        # ── Find row ──
        find_row = ttk.Frame(self.frame)
        find_row.pack(fill=X, padx=8, pady=(4, 0))

        search_icon = self.icon_mgr.get("search", 16)
        self._icon_refs.append(search_icon)

        ttk.Label(
            find_row,
            text=" Find:",
            image=search_icon,
            compound=LEFT,
            font=("Segoe UI", 10),
        ).pack(side=LEFT)

        self.find_entry = ttk.Entry(find_row, width=30)
        self.find_entry.pack(side=LEFT, padx=(8, 4))
        self.find_entry.bind("<Return>", self._find_next)
        self.find_entry.bind("<KeyRelease>", self._on_find_changed)

        left_icon = self.icon_mgr.get("arrow_left", 16)
        self._icon_refs.append(left_icon)

        ttk.Button(
            find_row,
            image=left_icon,
            bootstyle="info-outline",
            command=self._find_prev,
        ).pack(side=LEFT, padx=1)

        right_icon = self.icon_mgr.get("arrow_right", 16)
        self._icon_refs.append(right_icon)

        ttk.Button(
            find_row,
            image=right_icon,
            bootstyle="info-outline",
            command=self._find_next,
        ).pack(side=LEFT, padx=1)

        self.match_label = ttk.Label(
            find_row, text="", font=("Segoe UI", 9)
        )
        self.match_label.pack(side=LEFT, padx=8)

        self.case_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            find_row, text="Aa", variable=self.case_var,
            bootstyle="info-round-toggle",
            command=self._on_find_changed,
        ).pack(side=LEFT, padx=4)

        close_icon = self.icon_mgr.get("close", 16)
        self._icon_refs.append(close_icon)

        ttk.Button(
            find_row,
            image=close_icon,
            bootstyle="danger-link",
            command=self.hide,
        ).pack(side=RIGHT)

        # ── Replace row ──
        replace_row = ttk.Frame(self.frame)
        replace_row.pack(fill=X, padx=8, pady=(2, 4))

        replace_icon = self.icon_mgr.get("replace", 16)
        self._icon_refs.append(replace_icon)

        ttk.Label(
            replace_row,
            text=" Replace:",
            image=replace_icon,
            compound=LEFT,
            font=("Segoe UI", 10),
        ).pack(side=LEFT)

        self.replace_entry = ttk.Entry(replace_row, width=30)
        self.replace_entry.pack(side=LEFT, padx=(8, 4))

        ttk.Button(
            replace_row, text="Replace",
            bootstyle="warning-outline",
            command=self._replace_one,
        ).pack(side=LEFT, padx=2)

        ttk.Button(
            replace_row, text="All",
            bootstyle="warning-outline",
            command=self._replace_all,
        ).pack(side=LEFT, padx=2)

    # ── Visibility ──

    def toggle(self):
        if self.visible:
            self.hide()
        else:
            self.show()

    def show(self):
        self.frame.grid(row=1, column=0, sticky="ew")
        self.visible = True
        self.find_entry.focus_set()

        editor = self._get_editor()
        if editor:
            try:
                selected = editor.get(tk.SEL_FIRST, tk.SEL_LAST)
                if selected:
                    self.find_entry.delete(0, "end")
                    self.find_entry.insert(0, selected)
            except tk.TclError:
                pass

    def hide(self):
        self.frame.grid_remove()
        self.visible = False
        self._clear_highlights()

    # ── Search logic ──

    def _on_find_changed(self, event=None):
        self._find_all()

    def _find_all(self):
        self._clear_highlights()
        editor = self._get_editor()
        if not editor:
            return

        query = self.find_entry.get()
        if not query:
            self.match_label.configure(text="")
            return

        self.matches = []
        nocase = not self.case_var.get()
        start = "1.0"

        while True:
            pos = editor.search(query, start, stopindex="end", nocase=nocase)
            if not pos:
                break
            end = f"{pos}+{len(query)}c"
            self.matches.append((pos, end))
            editor.tag_add("search_highlight", pos, end)
            start = end

        editor.tag_configure(
            "search_highlight",
            background=self.app.colors["accent"],
            foreground="#ffffff",
        )

        count = len(self.matches)
        self.match_label.configure(
            text=f"{count} match{'es' if count != 1 else ''}"
        )
        self.current_match = 0 if count > 0 else -1

    def _find_next(self, event=None):
        if not self.matches:
            self._find_all()
        if not self.matches:
            return
        self.current_match = (self.current_match + 1) % len(self.matches)
        self._jump_to_current()

    def _find_prev(self):
        if not self.matches:
            return
        self.current_match = (self.current_match - 1) % len(self.matches)
        self._jump_to_current()

    def _jump_to_current(self):
        editor = self._get_editor()
        if not editor or self.current_match < 0:
            return
        pos, end = self.matches[self.current_match]
        editor.see(pos)
        editor.tag_remove("current_match", "1.0", "end")
        editor.tag_add("current_match", pos, end)
        editor.tag_configure("current_match", background="#ff6600")
        self.match_label.configure(
            text=f"{self.current_match + 1}/{len(self.matches)}"
        )

    # ── Replace ──

    def _replace_one(self):
        editor = self._get_editor()
        if not editor or self.current_match < 0 or not self.matches:
            return
        pos, end = self.matches[self.current_match]
        editor.delete(pos, end)
        editor.insert(pos, self.replace_entry.get())
        self._find_all()

    def _replace_all(self):
        editor = self._get_editor()
        if not editor or not self.matches:
            return
        replacement = self.replace_entry.get()
        for pos, end in reversed(self.matches):
            editor.delete(pos, end)
            editor.insert(pos, replacement)
        count = len(self.matches)
        self._find_all()
        self.app.set_status(f"Replaced {count} occurrences")

    # ── Helpers ──

    def _get_editor(self):
        try:
            mgr = getattr(self.app, "tab_manager", None)
            if mgr is None:
                return None
            return mgr.get_active_editor()
        except Exception:
            return None

    def _clear_highlights(self):
        self.matches = []
        self.current_match = -1
        editor = self._get_editor()
        if editor is None:
            return
        try:
            editor.tag_remove("search_highlight", "1.0", "end")
            editor.tag_remove("current_match", "1.0", "end")
        except Exception:
            pass