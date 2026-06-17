"""Command palette — Ctrl+Shift+P quick action launcher."""

import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *


class CommandPalette:
    """Fuzzy-searchable command palette overlay."""

    def __init__(self, app):
        self.app = app
        self.visible = False
        self.window = None
        self.commands = []
        self.filtered = []
        self.selected_idx = 0
        self.result_labels = []

        self._register_commands()

    def _register_commands(self):
        self.commands = [
            {"label": "File: New File", "detail": "Create a new untitled file", "category": "file", "shortcut": "Ctrl+N", "action": self.app.file_manager.new_file},
            {"label": "File: Open File", "detail": "Open a file from disk", "category": "file", "shortcut": "Ctrl+O", "action": self.app.file_manager.open_file},
            {"label": "File: Open Folder", "detail": "Open a project folder", "category": "file", "shortcut": "", "action": self.app.open_project},
            {"label": "File: Save", "detail": "Save the current file", "category": "file", "shortcut": "Ctrl+S", "action": self.app.file_manager.save_file},
            {"label": "File: Save As", "detail": "Save the current file with a new name", "category": "file", "shortcut": "Ctrl+Shift+S", "action": self.app.file_manager.save_file_as},
            {"label": "File: Close Tab", "detail": "Close the active editor tab", "category": "file", "shortcut": "Ctrl+W", "action": self.app.tab_manager.close_active_tab},
            {"label": "Edit: Undo", "detail": "Undo last action", "category": "edit", "shortcut": "Ctrl+Z", "action": lambda: self._editor_action("undo")},
            {"label": "Edit: Redo", "detail": "Redo last undone action", "category": "edit", "shortcut": "Ctrl+Y", "action": lambda: self._editor_action("redo")},
            {"label": "Edit: Cut", "detail": "Cut selected text", "category": "edit", "shortcut": "Ctrl+X", "action": lambda: self._editor_action("cut")},
            {"label": "Edit: Copy", "detail": "Copy selected text", "category": "edit", "shortcut": "Ctrl+C", "action": lambda: self._editor_action("copy")},
            {"label": "Edit: Paste", "detail": "Paste from clipboard", "category": "edit", "shortcut": "Ctrl+V", "action": lambda: self._editor_action("paste")},
            {"label": "Edit: Select All", "detail": "Select all text in editor", "category": "edit", "shortcut": "Ctrl+A", "action": lambda: self._editor_action("select_all")},
            {"label": "Edit: Find and Replace", "detail": "Open the find and replace bar", "category": "edit", "shortcut": "Ctrl+F", "action": self.app.toggle_search},
            {"label": "Edit: Go to Line", "detail": "Jump to a specific line number", "category": "edit", "shortcut": "Ctrl+G", "action": self._go_to_line},
            {"label": "Edit: Duplicate Line", "detail": "Duplicate the current line below", "category": "edit", "shortcut": "", "action": self._duplicate_line},
            {"label": "Edit: Delete Line", "detail": "Delete the entire current line", "category": "edit", "shortcut": "", "action": self._delete_line},
            {"label": "Edit: Move Line Up", "detail": "Move the current line up", "category": "edit", "shortcut": "Alt+Up", "action": lambda: self._move_line("up")},
            {"label": "Edit: Move Line Down", "detail": "Move the current line down", "category": "edit", "shortcut": "Alt+Down", "action": lambda: self._move_line("down")},
            {"label": "Edit: Toggle Comment", "detail": "Comment or uncomment the current line", "category": "edit", "shortcut": "Ctrl+/", "action": self._toggle_comment},
            {"label": "Edit: Indent Line", "detail": "Add indentation", "category": "edit", "shortcut": "Tab", "action": lambda: self._indent("right")},
            {"label": "Edit: Outdent Line", "detail": "Remove indentation", "category": "edit", "shortcut": "Shift+Tab", "action": lambda: self._indent("left")},
            {"label": "View: Toggle Sidebar", "detail": "Show or hide the sidebar", "category": "view", "shortcut": "Ctrl+B", "action": self.app.toggle_sidebar},
            {"label": "View: Toggle Terminal", "detail": "Show or hide the terminal", "category": "view", "shortcut": "Ctrl+`", "action": self.app.toggle_terminal},
            {"label": "View: Switch Theme", "detail": "Toggle dark and light theme", "category": "view", "shortcut": "", "action": self.app.switch_theme},
            {"label": "View: Zoom In", "detail": "Increase font size", "category": "view", "shortcut": "Ctrl++", "action": self._zoom_in},
            {"label": "View: Zoom Out", "detail": "Decrease font size", "category": "view", "shortcut": "Ctrl+-", "action": self._zoom_out},
            {"label": "View: Reset Zoom", "detail": "Reset font size to default", "category": "view", "shortcut": "Ctrl+0", "action": self._zoom_reset},
            {"label": "View: Toggle Word Wrap", "detail": "Toggle word wrapping", "category": "view", "shortcut": "", "action": self._toggle_word_wrap},
            {"label": "Sidebar: Show Explorer", "detail": "Switch to file explorer", "category": "view", "shortcut": "", "action": lambda: self.app.sidebar._switch_panel("explorer")},
            {"label": "Sidebar: Show Git", "detail": "Switch to source control", "category": "view", "shortcut": "", "action": lambda: self.app.sidebar._switch_panel("git")},
            {"label": "Sidebar: Show Extensions", "detail": "Switch to extensions", "category": "view", "shortcut": "", "action": lambda: self.app.sidebar._switch_panel("extensions")},
            {"label": "Git: Clone Repository", "detail": "Clone a remote repository", "category": "git", "shortcut": "", "action": self.app.git_manager.clone_repo},
            {"label": "Git: Init Repository", "detail": "Initialize a new repository", "category": "git", "shortcut": "", "action": self.app.git_manager.init_repo},
            {"label": "Git: Status", "detail": "Show current status", "category": "git", "shortcut": "", "action": self.app.git_manager.git_status},
            {"label": "Git: Diff", "detail": "Show changes", "category": "git", "shortcut": "", "action": self.app.git_manager.git_diff},
            {"label": "Git: Stage All", "detail": "Stage all changes", "category": "git", "shortcut": "", "action": self.app.git_manager.git_add_all},
            {"label": "Git: Commit", "detail": "Commit staged changes", "category": "git", "shortcut": "", "action": self.app.git_manager.git_commit},
            {"label": "Git: Push", "detail": "Push to remote", "category": "git", "shortcut": "", "action": self.app.git_manager.git_push},
            {"label": "Git: Pull", "detail": "Pull from remote", "category": "git", "shortcut": "", "action": self.app.git_manager.git_pull},
            {"label": "Git: Log", "detail": "Show commit history", "category": "git", "shortcut": "", "action": self.app.git_manager.git_log},
            {"label": "Git: Branches", "detail": "Show all branches", "category": "git", "shortcut": "", "action": self.app.git_manager.git_branch},
            {"label": "Git: Set Remote", "detail": "Set or update remote URL", "category": "git", "shortcut": "", "action": self.app.git_manager.add_remote},
            {"label": "Terminal: Clear", "detail": "Clear terminal output", "category": "terminal", "shortcut": "", "action": lambda: self.app.terminal.clear()},
            {"label": "Terminal: Restart Shell", "detail": "Kill and restart shell", "category": "terminal", "shortcut": "", "action": lambda: self.app.terminal.restart_shell()},
            {"label": "Preferences: Open Settings", "detail": "Open the settings panel", "category": "app", "shortcut": "Ctrl+,", "action": self.app.open_settings},
            {"label": "Preferences: Reset All Settings", "detail": "Reset all settings to defaults", "category": "app", "shortcut": "", "action": self._reset_settings},
            {"label": "Update: Check for Updates", "detail": "Check GitHub for newer version", "category": "app", "shortcut": "", "action": self.app.check_for_updates},
            {"label": "OmniIDE: About", "detail": "Show version and info", "category": "app", "shortcut": "", "action": self._show_about},
            {"label": "OmniIDE: Open Settings Folder", "detail": "Open config directory", "category": "app", "shortcut": "", "action": self._open_settings_folder},
            {"label": "OmniIDE: Reload Window", "detail": "Refresh all UI components", "category": "app", "shortcut": "", "action": self._reload_ui},
        ]

    def toggle(self):
        if self.visible:
            self.close()
        else:
            self.show()

    def show(self):
        if self.visible:
            self.close()

        self.visible = True
        self.selected_idx = 0

        self.window = tk.Toplevel(self.app.root)
        self.window.overrideredirect(True)
        self.window.attributes("-topmost", True)

        try:
            self.window.attributes("-alpha", 0.97)
        except Exception:
            pass

        palette_w = 560
        palette_h = 420

        root_x = self.app.root.winfo_rootx()
        root_y = self.app.root.winfo_rooty()
        root_w = self.app.root.winfo_width()

        x = root_x + (root_w - palette_w) // 2
        y = root_y + 60

        self.window.geometry(f"{palette_w}x{palette_h}+{x}+{y}")

        c = self.app.colors
        bg = c["bg_secondary"]
        fg = c["fg_primary"]
        border = c["border"]
        accent = c["accent"]

        outer = tk.Frame(self.window, bg=border, padx=1, pady=1)
        outer.pack(fill=BOTH, expand=True)

        main_frame = tk.Frame(outer, bg=bg)
        main_frame.pack(fill=BOTH, expand=True)

        header = tk.Frame(main_frame, bg=bg)
        header.pack(fill=X, padx=12, pady=(12, 0))

        tk.Label(header, text=">", font=("Consolas", 14, "bold"), fg=accent, bg=bg).pack(side=LEFT, padx=(0, 6))

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self._on_search_changed)

        self.search_entry = tk.Entry(
            header, textvariable=self.search_var, font=("Segoe UI", 13),
            bg=c["bg_tertiary"], fg=fg, insertbackground=accent,
            relief="flat", bd=0, highlightthickness=2,
            highlightbackground=border, highlightcolor=accent,
        )
        self.search_entry.pack(side=LEFT, fill=X, expand=True, ipady=6)
        self.search_entry.focus_set()

        self.search_entry.bind("<Escape>", lambda e: self.close())
        self.search_entry.bind("<Return>", lambda e: self._execute_selected())
        self.search_entry.bind("<Up>", lambda e: self._move_selection(-1))
        self.search_entry.bind("<Down>", lambda e: self._move_selection(1))
        self.window.bind("<FocusOut>", self._on_focus_out)

        tk.Frame(main_frame, bg=border, height=1).pack(fill=X, padx=8, pady=(8, 0))

        results_container = tk.Frame(main_frame, bg=bg)
        results_container.pack(fill=BOTH, expand=True, padx=4, pady=4)

        self.results_canvas = tk.Canvas(results_container, bg=bg, highlightthickness=0, bd=0)

        self.scrollbar = tk.Scrollbar(
            results_container, orient=tk.VERTICAL,
            command=self.results_canvas.yview, bg=bg, troughcolor=bg,
        )

        self.results_frame = tk.Frame(self.results_canvas, bg=bg)
        self.results_frame.bind(
            "<Configure>",
            lambda e: self.results_canvas.configure(scrollregion=self.results_canvas.bbox("all")),
        )

        self.canvas_window = self.results_canvas.create_window((0, 0), window=self.results_frame, anchor="nw")

        self.results_canvas.configure(yscrollcommand=self.scrollbar.set)
        self.results_canvas.pack(side=LEFT, fill=BOTH, expand=True)
        self.scrollbar.pack(side=RIGHT, fill=tk.Y)

        self.results_canvas.bind(
            "<Configure>",
            lambda e: self.results_canvas.itemconfig(self.canvas_window, width=e.width),
        )

        self.results_canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.results_canvas.bind("<Button-4>", self._on_mousewheel)
        self.results_canvas.bind("<Button-5>", self._on_mousewheel)

        footer = tk.Frame(main_frame, bg=c["bg_tertiary"])
        footer.pack(fill=X, side=BOTTOM)

        tk.Label(
            footer, text="  up/down navigate   enter run   esc close",
            font=("Segoe UI", 8), fg=c["fg_secondary"], bg=c["bg_tertiary"],
        ).pack(side=LEFT, padx=8, pady=4)

        self.count_label = tk.Label(
            footer, text="", font=("Segoe UI", 8),
            fg=c["fg_secondary"], bg=c["bg_tertiary"],
        )
        self.count_label.pack(side=RIGHT, padx=8, pady=4)

        self._filter_commands("")

    def close(self):
        if self.window:
            try:
                self.window.destroy()
            except Exception:
                pass
            self.window = None
        self.visible = False
        self.result_labels.clear()

    def _on_search_changed(self, *args):
        query = self.search_var.get()
        self._filter_commands(query)

    def _filter_commands(self, query):
        query_lower = query.lower().strip()

        if not query_lower:
            self.filtered = self.commands.copy()
        else:
            scored = []
            for cmd in self.commands:
                score = self._fuzzy_score(query_lower, cmd["label"].lower())
                if score > 0:
                    scored.append((score, cmd))
            scored.sort(key=lambda x: -x[0])
            self.filtered = [cmd for _, cmd in scored]

        self.selected_idx = 0
        self._render_results()

    def _fuzzy_score(self, query, text):
        if query in text:
            return 100 - text.find(query)

        qi = 0
        score = 0
        last_match = -1
        for ti, ch in enumerate(text):
            if qi < len(query) and ch == query[qi]:
                if last_match == ti - 1:
                    score += 5
                else:
                    score += 1
                if ti == 0 or text[ti - 1] in (" ", ":", ".", "_", "-"):
                    score += 3
                last_match = ti
                qi += 1

        if qi == len(query):
            return score
        return 0

    def _render_results(self):
        for widget in self.results_frame.winfo_children():
            widget.destroy()
        self.result_labels.clear()

        c = self.app.colors
        bg = c["bg_secondary"]
        fg = c["fg_primary"]
        fg_dim = c["fg_secondary"]
        accent = c["accent"]
        sel_bg = c["selection"]

        cat_colors = {
            "file": "#89b4fa", "edit": "#f9e2af", "view": "#cba6f7",
            "git": "#f38ba8", "terminal": "#a6e3a1", "app": "#89dceb",
        }

        max_show = min(len(self.filtered), 50)

        for i in range(max_show):
            cmd = self.filtered[i]
            is_selected = (i == self.selected_idx)
            row_bg = sel_bg if is_selected else bg

            row = tk.Frame(self.results_frame, bg=row_bg, cursor="hand2")
            row.pack(fill=X, padx=4, pady=1)

            cat_color = cat_colors.get(cmd["category"], fg_dim)

            tk.Label(row, text="*", font=("Segoe UI", 7), fg=cat_color, bg=row_bg).pack(side=LEFT, padx=(8, 4), pady=4)

            label_frame = tk.Frame(row, bg=row_bg)
            label_frame.pack(side=LEFT, fill=X, expand=True, pady=2)

            tk.Label(
                label_frame, text=cmd["label"],
                font=("Segoe UI", 10, "bold" if is_selected else "normal"),
                fg=accent if is_selected else fg, bg=row_bg, anchor="w",
            ).pack(anchor="w")

            if cmd["detail"]:
                tk.Label(
                    label_frame, text=cmd["detail"],
                    font=("Segoe UI", 8), fg=fg_dim, bg=row_bg, anchor="w",
                ).pack(anchor="w")

            if cmd["shortcut"]:
                shortcut_frame = tk.Frame(row, bg=row_bg)
                shortcut_frame.pack(side=RIGHT, padx=(4, 8))
                tk.Label(
                    shortcut_frame, text=f" {cmd['shortcut']} ",
                    font=("Consolas", 8), fg=fg_dim, bg=c["bg_tertiary"],
                    relief="flat", padx=4, pady=1,
                ).pack(pady=4)

            row.bind("<Button-1>", lambda e, idx=i: self._on_click(idx))
            for child in row.winfo_children():
                child.bind("<Button-1>", lambda e, idx=i: self._on_click(idx))
                for sub in child.winfo_children():
                    sub.bind("<Button-1>", lambda e, idx=i: self._on_click(idx))

            def on_enter(e, r=row, idx=i):
                if idx != self.selected_idx:
                    self._set_row_bg(r, c["bg_tertiary"])

            def on_leave(e, r=row, idx=i):
                if idx != self.selected_idx:
                    self._set_row_bg(r, bg)

            row.bind("<Enter>", on_enter)
            row.bind("<Leave>", on_leave)

            self.result_labels.append(row)

        try:
            self.count_label.configure(text=f"{max_show}/{len(self.filtered)} commands")
        except Exception:
            pass

    def _set_row_bg(self, row, color):
        row.configure(bg=color)
        for child in row.winfo_children():
            try:
                child.configure(bg=color)
            except Exception:
                pass
            for sub in child.winfo_children():
                try:
                    sub.configure(bg=color)
                except Exception:
                    pass

    def _move_selection(self, delta):
        if not self.filtered:
            return "break"
        old = self.selected_idx
        self.selected_idx = max(0, min(len(self.filtered) - 1, self.selected_idx + delta))
        if old != self.selected_idx:
            self._render_results()
            if self.result_labels:
                try:
                    self.results_canvas.yview_moveto(self.selected_idx / max(len(self.filtered), 1))
                except Exception:
                    pass
        return "break"

    def _on_click(self, idx):
        self.selected_idx = idx
        self._execute_selected()

    def _execute_selected(self):
        if not self.filtered:
            return
        if self.selected_idx >= len(self.filtered):
            self.selected_idx = 0
        cmd = self.filtered[self.selected_idx]
        self.close()
        self.app.root.after(50, cmd["action"])
        self.app.set_status(f"Executed: {cmd['label']}")

    def _on_focus_out(self, event=None):
        self.app.root.after(100, self._check_focus)

    def _check_focus(self):
        if not self.visible:
            return
        try:
            focused = self.app.root.focus_get()
            if focused and self.window:
                widget = focused
                while widget:
                    if widget == self.window:
                        return
                    widget = widget.master
            self.close()
        except Exception:
            self.close()

    def _on_mousewheel(self, event):
        if event.num == 4:
            self.results_canvas.yview_scroll(-3, "units")
        elif event.num == 5:
            self.results_canvas.yview_scroll(3, "units")
        else:
            self.results_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _editor_action(self, action):
        editor = self.app.tab_manager.get_active_editor()
        if not editor:
            return
        try:
            if action == "undo":
                editor.edit_undo()
            elif action == "redo":
                editor.edit_redo()
            elif action == "cut":
                editor.event_generate("<<Cut>>")
            elif action == "copy":
                editor.event_generate("<<Copy>>")
            elif action == "paste":
                editor.event_generate("<<Paste>>")
            elif action == "select_all":
                editor.tag_add("sel", "1.0", "end")
        except tk.TclError:
            pass

    def _go_to_line(self):
        from tkinter import simpledialog
        editor = self.app.tab_manager.get_active_editor()
        if not editor:
            return
        line = simpledialog.askinteger("Go to Line", "Enter line number:", parent=self.app.root, minvalue=1)
        if line:
            editor.mark_set("insert", f"{line}.0")
            editor.see(f"{line}.0")
            editor.focus_set()
            self.app.set_status(f"Line {line}")

    def _duplicate_line(self):
        editor = self.app.tab_manager.get_active_editor()
        if not editor:
            return
        line_start = editor.index("insert linestart")
        line_end = editor.index("insert lineend")
        line_text = editor.get(line_start, line_end)
        editor.insert(line_end, "\n" + line_text)

    def _delete_line(self):
        editor = self.app.tab_manager.get_active_editor()
        if not editor:
            return
        line_start = editor.index("insert linestart")
        next_start = editor.index("insert linestart +1line")
        editor.delete(line_start, next_start)

    def _move_line(self, direction):
        editor = self.app.tab_manager.get_active_editor()
        if not editor:
            return

        cursor = editor.index("insert")
        line_start = editor.index("insert linestart")
        line_end = editor.index("insert lineend")
        line_text = editor.get(line_start, line_end)

        if direction == "up":
            prev_start = editor.index(f"{line_start} -1line linestart")
            if prev_start == line_start:
                return
            editor.delete(line_start, f"{line_end}+1c")
            editor.insert(prev_start, line_text + "\n")
            new_line = int(prev_start.split(".")[0])
            col = cursor.split(".")[1]
            editor.mark_set("insert", f"{new_line}.{col}")
        elif direction == "down":
            next_end = editor.index(f"{line_end} +1line lineend")
            if next_end == line_end:
                return
            next_start = editor.index(f"{line_end}+1c linestart")
            next_text = editor.get(next_start, f"{next_start} lineend")
            editor.delete(line_start, f"{next_start} lineend")
            editor.insert(line_start, next_text + "\n" + line_text)
            new_line = int(line_start.split(".")[0]) + 1
            col = cursor.split(".")[1]
            editor.mark_set("insert", f"{new_line}.{col}")

    def _toggle_comment(self):
        editor = self.app.tab_manager.get_active_editor()
        if not editor:
            return

        info = self.app.tab_manager.get_active_tab_info()
        filepath = info.get("filepath", "") if info else ""

        import os
        ext = os.path.splitext(filepath)[1].lower() if filepath else ".py"

        comment_map = {
            ".py": "#", ".js": "//", ".ts": "//", ".jsx": "//", ".tsx": "//",
            ".c": "//", ".cpp": "//", ".h": "//", ".java": "//", ".go": "//",
            ".rs": "//", ".php": "//", ".rb": "#", ".sh": "#", ".bash": "#",
            ".yaml": "#", ".yml": "#", ".toml": "#", ".ini": ";", ".sql": "--",
        }
        comment_char = comment_map.get(ext, "#")

        line_start = editor.index("insert linestart")
        line_end = editor.index("insert lineend")
        line_text = editor.get(line_start, line_end)
        stripped = line_text.lstrip()

        if stripped.startswith(comment_char):
            idx = line_text.index(comment_char)
            remove_len = len(comment_char)
            if idx + remove_len < len(line_text) and line_text[idx + remove_len] == " ":
                remove_len += 1
            new_text = line_text[:idx] + line_text[idx + remove_len:]
            editor.delete(line_start, line_end)
            editor.insert(line_start, new_text)
        else:
            indent = len(line_text) - len(stripped)
            new_text = line_text[:indent] + comment_char + " " + line_text[indent:]
            editor.delete(line_start, line_end)
            editor.insert(line_start, new_text)

    def _indent(self, direction):
        editor = self.app.tab_manager.get_active_editor()
        if not editor:
            return

        tab_size = self.app.settings.get("tab_size", 4)
        line_start = editor.index("insert linestart")
        line_end = editor.index("insert lineend")
        line_text = editor.get(line_start, line_end)

        if direction == "right":
            new_text = " " * tab_size + line_text
        else:
            removed = 0
            for ch in line_text:
                if ch == " " and removed < tab_size:
                    removed += 1
                else:
                    break
            new_text = line_text[removed:]

        editor.delete(line_start, line_end)
        editor.insert(line_start, new_text)

    def _zoom_in(self):
        self.app.settings["font_size"] = min(32, self.app.settings["font_size"] + 1)
        self._apply_font()

    def _zoom_out(self):
        self.app.settings["font_size"] = max(8, self.app.settings["font_size"] - 1)
        self._apply_font()

    def _zoom_reset(self):
        self.app.settings["font_size"] = 13
        self._apply_font()

    def _apply_font(self):
        s = self.app.settings["font_size"]
        f = self.app.settings["font_family"]
        for info in self.app.tab_manager.tabs.values():
            info["editor"].configure(font=(f, s))
            info["line_numbers"].set_font((f, s))
            info["line_numbers"].redraw()
        self.app.save_settings()
        self.app.set_status(f"Font size: {s}")

    def _toggle_word_wrap(self):
        self.app.settings["word_wrap"] = not self.app.settings["word_wrap"]
        wrap = "word" if self.app.settings["word_wrap"] else "none"
        for info in self.app.tab_manager.tabs.values():
            info["editor"].configure(wrap=wrap)
        self.app.save_settings()
        state = "on" if self.app.settings["word_wrap"] else "off"
        self.app.set_status(f"Word wrap: {state}")

    def _reset_settings(self):
        from tkinter import messagebox
        from src.config import DEFAULT_SETTINGS
        confirm = messagebox.askyesno("Reset Settings", "Reset all settings to defaults?\nThis cannot be undone.")
        if confirm:
            self.app.settings = DEFAULT_SETTINGS.copy()
            self.app.save_settings()
            self.app.set_status("Settings reset to defaults")

    def _show_about(self):
        from tkinter import messagebox
        from src.config import APP_VERSION
        messagebox.showinfo(
            "About OmniIDE",
            f"OmniIDE v{APP_VERSION}\n\n"
            "A fast, modern, lightweight desktop IDE.\n"
            "Built from scratch by OmniNodeCo.\n\n"
            "No Electron. No bloat. Pure speed.\n\n"
            "(c) 2024 OmniNodeCo",
        )

    def _open_settings_folder(self):
        import subprocess
        import sys
        from src.config import CONFIG_DIR
        try:
            if sys.platform == "win32":
                subprocess.Popen(["explorer", CONFIG_DIR])
            elif sys.platform == "darwin":
                subprocess.Popen(["open", CONFIG_DIR])
            else:
                subprocess.Popen(["xdg-open", CONFIG_DIR])
        except Exception:
            self.app.set_status(f"Settings: {CONFIG_DIR}")

    def _reload_ui(self):
        from src.utils.styles import apply_global_styles
        apply_global_styles(self.app)
        self.app.tab_manager.refresh_all_highlighting()
        self.app.set_status("UI reloaded")