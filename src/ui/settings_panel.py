"""Settings GUI panel — visual settings editor."""

import tkinter as tk
import tkinter.ttk as tkttk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox, font as tkfont

from src.config import (
    APP_NAME, APP_VERSION, APP_AUTHOR,
    DEFAULT_SETTINGS, FONT_OPTIONS, CONFIG_DIR,
)
from src.utils.icon_manager import IconManager
from src.utils.styles import make_round_btn


class SettingsPanel:
    """Full settings GUI as a dialog window."""

    def __init__(self, app):
        self.app = app
        self.icon_mgr = IconManager()
        self._icon_refs = []
        self.window = None
        self._vars = {}

    def show(self):
        """Open the settings window."""
        if self.window and self.window.winfo_exists():
            self.window.lift()
            self.window.focus_force()
            return

        self.window = tk.Toplevel(self.app.root)
        self.window.title(f"{APP_NAME} — Settings")
        self.window.geometry("680x600")
        self.window.transient(self.app.root)
        self.window.grab_set()
        self.window.resizable(True, True)
        self.window.minsize(500, 400)

        # Center
        self.window.update_idletasks()
        x = self.app.root.winfo_rootx() + (self.app.root.winfo_width() - 680) // 2
        y = self.app.root.winfo_rooty() + (self.app.root.winfo_height() - 600) // 2
        self.window.geometry(f"+{x}+{y}")

        c = self.app.colors

        # ── Header ──
        header = ttk.Frame(self.window, padding=(20, 12))
        header.pack(fill=X)

        settings_icon = self.icon_mgr.get("settings", 20)
        self._icon_refs.append(settings_icon)

        ttk.Label(
            header,
            text=" Settings",
            image=settings_icon,
            compound=LEFT,
            font=("Segoe UI", 18, "bold"),
        ).pack(side=LEFT)

        ttk.Label(
            header,
            text=f"v{APP_VERSION}",
            font=("Consolas", 9),
            foreground=c.get("fg_secondary", "#888"),
        ).pack(side=RIGHT)

        ttk.Separator(self.window).pack(fill=X, padx=16)

        # ── Search bar ──
        search_frame = ttk.Frame(self.window, padding=(20, 8))
        search_frame.pack(fill=X)

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self._on_search)

        search_entry = ttk.Entry(
            search_frame,
            textvariable=self.search_var,
            font=("Segoe UI", 11),
        )
        search_entry.pack(fill=X)
        search_entry.insert(0, "")

        ttk.Label(
            search_frame,
            text="Type to filter settings...",
            font=("Segoe UI", 8),
            foreground=c.get("fg_secondary", "#888"),
        ).pack(anchor="w", pady=(2, 0))

        # ── Scrollable content ──
        container = ttk.Frame(self.window)
        container.pack(fill=BOTH, expand=True, padx=4)

        self.canvas = tk.Canvas(
            container,
            highlightthickness=0,
            bd=0,
            bg=c.get("bg_primary", "#1e1e2e"),
        )

        scrollbar = tkttk.Scrollbar(
            container, orient=tk.VERTICAL, command=self.canvas.yview
        )

        self.settings_frame = ttk.Frame(self.canvas)
        self.settings_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            ),
        )

        self.canvas_window = self.canvas.create_window(
            (0, 0), window=self.settings_frame, anchor="nw"
        )

        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=tk.Y)

        self.canvas.bind(
            "<Configure>",
            lambda e: self.canvas.itemconfig(self.canvas_window, width=e.width),
        )

        # Mouse wheel
        self.canvas.bind("<Enter>", lambda e: self.canvas.bind_all("<MouseWheel>", self._wheel))
        self.canvas.bind("<Leave>", lambda e: self.canvas.unbind_all("<MouseWheel>"))

        # Build all sections
        self.all_rows = []
        self._build_sections()

        # ── Footer ──
        ttk.Separator(self.window).pack(fill=X, padx=16)

        footer = ttk.Frame(self.window, padding=(20, 10))
        footer.pack(fill=X)

        ttk.Button(
            footer,
            text="Reset All to Defaults",
            bootstyle="danger-outline",
            command=self._reset_all,
            padding=(12, 6),
            cursor="hand2",
        ).pack(side=LEFT)

        ttk.Label(
            footer,
            text=f"Config: {CONFIG_DIR}",
            font=("Segoe UI", 8),
            foreground=c.get("fg_secondary", "#888"),
        ).pack(side=LEFT, padx=(12, 0))

        ttk.Button(
            footer,
            text="Close",
            bootstyle="secondary",
            command=self.window.destroy,
            padding=(16, 6),
            cursor="hand2",
        ).pack(side=RIGHT)

        ttk.Button(
            footer,
            text="Apply",
            bootstyle="success",
            command=self._apply_all,
            padding=(16, 6),
            cursor="hand2",
        ).pack(side=RIGHT, padx=(0, 8))

    def _wheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _build_sections(self):
        """Build all settings sections."""
        s = self.app.settings

        # ── Appearance ──
        self._section("Appearance")

        self._dropdown(
            "Theme", "theme",
            s.get("theme", "dark"),
            ["dark", "light"],
            "Color theme for the entire IDE",
        )

        self._dropdown(
            "Font Family", "font_family",
            s.get("font_family", "Consolas"),
            self._get_available_fonts(),
            "Editor font family",
        )

        self._slider(
            "Font Size", "font_size",
            s.get("font_size", 13),
            8, 32,
            "Editor font size in pixels",
        )

        self._toggle(
            "Highlight Current Line", "highlight_current_line",
            s.get("highlight_current_line", True),
            "Highlight the line where the cursor is",
        )

        self._toggle(
            "Show Whitespace", "show_whitespace",
            s.get("show_whitespace", False),
            "Show spaces and tabs as visible characters",
        )

        self._toggle(
            "Cursor Blink", "cursor_blink",
            s.get("cursor_blink", True),
            "Enable cursor blinking in editor",
        )

        # ── Editor ──
        self._section("Editor")

        self._slider(
            "Tab Size", "tab_size",
            s.get("tab_size", 4),
            2, 8,
            "Number of spaces per tab",
        )

        self._toggle(
            "Word Wrap", "word_wrap",
            s.get("word_wrap", False),
            "Wrap long lines to fit the editor width",
        )

        self._toggle(
            "Auto Indent", "auto_indent",
            s.get("auto_indent", True),
            "Automatically indent new lines",
        )

        self._toggle(
            "Auto Save", "auto_save",
            s.get("auto_save", False),
            "Automatically save files after changes",
        )

        self._toggle(
            "Show Line Numbers", "show_line_numbers",
            s.get("show_line_numbers", True),
            "Show line numbers in the gutter",
        )

        # ── Window ──
        self._section("Window & Layout")

        self._slider(
            "Sidebar Width", "sidebar_width",
            s.get("sidebar_width", 280),
            200, 500,
            "Width of the sidebar panel in pixels",
        )

        self._slider(
            "Max Recent Files", "max_recent_files",
            s.get("max_recent_files", 15),
            5, 50,
            "Maximum number of recent files to remember",
        )

        # ── Terminal ──
        self._section("Terminal")

        self._dropdown(
            "Default Shell", "default_shell",
            s.get("default_shell", "auto"),
            ["auto", "bash", "zsh", "powershell", "cmd", "fish", "sh"],
            "Preferred shell (auto = detect best available)",
        )

        # ── Updates ──
        self._section("Updates")

        self._toggle(
            "Auto Check for Updates", "auto_check_updates",
            s.get("auto_check_updates", True),
            "Check for new versions on startup",
        )

        self._action_btn(
            "Check Now",
            "Check for updates right now",
            self._check_updates_now,
            "info",
        )

        # ── About ──
        self._section("About")

        self._info_row("Application", APP_NAME)
        self._info_row("Version", f"v{APP_VERSION}")
        self._info_row("Author", APP_AUTHOR)
        self._info_row("Config Path", CONFIG_DIR)

    def _get_available_fonts(self):
        """Get list of available monospace fonts."""
        try:
            available = list(tkfont.families())
            mono_fonts = [f for f in FONT_OPTIONS if f in available]
            if not mono_fonts:
                mono_fonts = FONT_OPTIONS[:5]
            return mono_fonts
        except Exception:
            return FONT_OPTIONS[:5]

    # ──────────────────────────────────────────────────
    # Widget builders
    # ──────────────────────────────────────────────────

    def _section(self, title):
        """Add a section header."""
        frame = ttk.Frame(self.settings_frame, padding=(16, 8, 16, 2))
        frame.pack(fill=X)

        ttk.Label(
            frame,
            text=title.upper(),
            font=("Segoe UI", 9, "bold"),
            foreground=self.app.colors.get("accent", "#89b4fa"),
        ).pack(anchor="w")

        sep = ttk.Separator(self.settings_frame)
        sep.pack(fill=X, padx=16, pady=(0, 4))

        self.all_rows.append(("section", title, frame, sep))

    def _toggle(self, label, key, value, description=""):
        """Add a toggle switch setting."""
        frame = ttk.Frame(self.settings_frame, padding=(20, 6, 20, 6))
        frame.pack(fill=X)

        left = ttk.Frame(frame)
        left.pack(side=LEFT, fill=X, expand=True)

        ttk.Label(
            left, text=label,
            font=("Segoe UI", 10),
        ).pack(anchor="w")

        if description:
            ttk.Label(
                left, text=description,
                font=("Segoe UI", 8),
                foreground=self.app.colors.get("fg_secondary", "#888"),
            ).pack(anchor="w")

        var = tk.BooleanVar(value=value)
        self._vars[key] = var

        switch = ttk.Checkbutton(
            frame,
            variable=var,
            bootstyle="success-round-toggle",
            command=lambda: self._on_change(key, var.get()),
        )
        switch.pack(side=RIGHT, padx=(8, 0))

        self.all_rows.append(("toggle", label, frame, None))

    def _dropdown(self, label, key, value, options, description=""):
        """Add a dropdown setting."""
        frame = ttk.Frame(self.settings_frame, padding=(20, 6, 20, 6))
        frame.pack(fill=X)

        left = ttk.Frame(frame)
        left.pack(side=LEFT, fill=X, expand=True)

        ttk.Label(
            left, text=label,
            font=("Segoe UI", 10),
        ).pack(anchor="w")

        if description:
            ttk.Label(
                left, text=description,
                font=("Segoe UI", 8),
                foreground=self.app.colors.get("fg_secondary", "#888"),
            ).pack(anchor="w")

        var = tk.StringVar(value=value)
        self._vars[key] = var

        combo = ttk.Combobox(
            frame,
            textvariable=var,
            values=options,
            state="readonly",
            width=18,
            font=("Segoe UI", 10),
        )
        combo.pack(side=RIGHT, padx=(8, 0))
        combo.bind(
            "<<ComboboxSelected>>",
            lambda e: self._on_change(key, var.get()),
        )

        self.all_rows.append(("dropdown", label, frame, None))

    def _slider(self, label, key, value, min_val, max_val, description=""):
        """Add a slider setting."""
        frame = ttk.Frame(self.settings_frame, padding=(20, 6, 20, 6))
        frame.pack(fill=X)

        top = ttk.Frame(frame)
        top.pack(fill=X)

        ttk.Label(
            top, text=label,
            font=("Segoe UI", 10),
        ).pack(side=LEFT)

        value_label = ttk.Label(
            top, text=str(value),
            font=("Consolas", 10, "bold"),
            foreground=self.app.colors.get("accent", "#89b4fa"),
        )
        value_label.pack(side=RIGHT)

        if description:
            ttk.Label(
                frame, text=description,
                font=("Segoe UI", 8),
                foreground=self.app.colors.get("fg_secondary", "#888"),
            ).pack(anchor="w")

        var = tk.IntVar(value=value)
        self._vars[key] = var

        scale = ttk.Scale(
            frame,
            from_=min_val,
            to=max_val,
            variable=var,
            orient=HORIZONTAL,
            bootstyle="info",
            command=lambda v, k=key, vl=value_label: (
                vl.configure(text=str(int(float(v)))),
                self._on_change(k, int(float(v))),
            ),
        )
        scale.pack(fill=X, pady=(4, 0))

        self.all_rows.append(("slider", label, frame, None))

    def _action_btn(self, label, description, command, style="info"):
        """Add an action button row."""
        frame = ttk.Frame(self.settings_frame, padding=(20, 6, 20, 6))
        frame.pack(fill=X)

        left = ttk.Frame(frame)
        left.pack(side=LEFT, fill=X, expand=True)

        if description:
            ttk.Label(
                left, text=description,
                font=("Segoe UI", 9),
            ).pack(anchor="w")

        ttk.Button(
            frame,
            text=label,
            bootstyle=f"{style}-outline",
            command=command,
            padding=(12, 5),
            cursor="hand2",
        ).pack(side=RIGHT, padx=(8, 0))

        self.all_rows.append(("action", label, frame, None))

    def _info_row(self, label, value):
        """Add a read-only info row."""
        frame = ttk.Frame(self.settings_frame, padding=(20, 4, 20, 4))
        frame.pack(fill=X)

        ttk.Label(
            frame, text=f"{label}:",
            font=("Segoe UI", 9),
            foreground=self.app.colors.get("fg_secondary", "#888"),
        ).pack(side=LEFT)

        ttk.Label(
            frame, text=value,
            font=("Consolas", 9),
        ).pack(side=RIGHT)

        self.all_rows.append(("info", label, frame, None))

    # ──────────────────────────────────────────────────
    # Change handlers
    # ──────────────────────────────────────────────────

    def _on_change(self, key, value):
        """Handle any setting change — apply live."""
        self.app.settings[key] = value

        # Live-apply specific settings
        if key == "theme":
            self.app.switch_theme()

        elif key == "font_family" or key == "font_size":
            self._apply_font()

        elif key == "word_wrap":
            wrap = "word" if value else "none"
            for info in self.app.tab_manager.tabs.values():
                info["editor"].configure(wrap=wrap)

        elif key == "tab_size":
            for info in self.app.tab_manager.tabs.values():
                info["editor"].configure(tabs=(f'{value}c',))

        elif key == "cursor_blink":
            for info in self.app.tab_manager.tabs.values():
                rate = 530 if value else 0
                info["editor"].configure(insertofftime=rate, insertontime=rate)

        self.app.save_settings()

    def _apply_font(self):
        """Apply font changes to all editors."""
        s = self.app.settings["font_size"]
        f = self.app.settings["font_family"]
        for info in self.app.tab_manager.tabs.values():
            info["editor"].configure(font=(f, s))
            info["line_numbers"].set_font((f, s))
            info["line_numbers"].redraw()

    def _apply_all(self):
        """Apply all current values and close."""
        for key, var in self._vars.items():
            val = var.get()
            self.app.settings[key] = val

        self.app.save_settings()
        self.app.set_status("Settings saved")

        # Apply font
        self._apply_font()

        # Apply wrap
        wrap = "word" if self.app.settings.get("word_wrap") else "none"
        for info in self.app.tab_manager.tabs.values():
            info["editor"].configure(wrap=wrap)

        self.window.destroy()

    def _reset_all(self):
        """Reset all settings to defaults."""
        confirm = messagebox.askyesno(
            "Reset Settings",
            "Reset all settings to defaults?\n\n"
            "This cannot be undone.",
            parent=self.window,
        )
        if not confirm:
            return

        self.app.settings = DEFAULT_SETTINGS.copy()
        self.app.save_settings()
        self.app.set_status("Settings reset to defaults")

        self.window.destroy()
        self.show()

    def _check_updates_now(self):
        """Trigger update check from settings."""
        self.window.destroy()

        updater = getattr(self.app, "updater", None)
        if updater:
            updater.check_now(silent=False)
        else:
            self.app.set_status("Updater not available")

    # ──────────────────────────────────────────────────
    # Search / filter
    # ──────────────────────────────────────────────────

    def _on_search(self, *args):
        """Filter visible settings by search query."""
        query = self.search_var.get().lower().strip()

        for row_type, label, frame, extra in self.all_rows:
            if not query:
                frame.pack(fill=X)
                if extra:
                    extra.pack(fill=X, padx=16, pady=(0, 4))
            else:
                if row_type == "section":
                    # Show section if any child matches
                    frame.pack(fill=X)
                    if extra:
                        extra.pack(fill=X, padx=16, pady=(0, 4))
                elif query in label.lower():
                    frame.pack(fill=X)
                else:
                    frame.pack_forget()