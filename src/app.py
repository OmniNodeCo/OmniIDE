"""Main application window."""

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import json
import os

from src.config import (
    APP_NAME, APP_VERSION, APP_AUTHOR,
    DEFAULT_SETTINGS, SETTINGS_PATH
)


class OmniIDEApp:
    """Main OmniIDE Application."""

    def __init__(self):
        self.settings = self._load_settings()
        theme_name = "darkly" if self.settings["theme"] == "dark" else "cosmo"

        self.root = ttk.Window(
            title=f"{APP_NAME} — {APP_AUTHOR}",
            themename=theme_name,
            size=(self.settings["window_width"], self.settings["window_height"]),
            minsize=(800, 500),
        )

        # ── lazy imports after window exists ──
        from src.utils.theme_loader import ThemeLoader
        from src.utils.recent_files import RecentFilesManager
        from src.utils.shortcuts import ShortcutManager
        from src.core.file_manager import FileManager
        from src.core.tab_manager import TabManager
        from src.core.terminal import Terminal
        from src.core.search import SearchBar
        from src.ui.menubar import MenuBar
        from src.ui.sidebar import Sidebar
        from src.ui.statusbar import StatusBar
        from src.ui.toolbar import Toolbar
        from src.ui.welcome import WelcomeTab

        self._WelcomeTab = WelcomeTab
        self._ShortcutManager = ShortcutManager

        self.theme_loader = ThemeLoader(self.settings["theme"])
        self.colors = self.theme_loader.colors
        self.syntax_colors = self.theme_loader.syntax

        self.recent_files_manager = RecentFilesManager()
        self.file_manager = FileManager(self)
        self.current_project_path = None

        self._build_ui(
            Toolbar, Sidebar, TabManager,
            Terminal, SearchBar, StatusBar, MenuBar,
        )

        self.shortcut_manager = ShortcutManager(self)
        self.shortcut_manager.bind_all()

        self._apply_custom_colors()
        self._show_welcome()

    def _load_settings(self):
        if os.path.exists(SETTINGS_PATH):
            try:
                with open(SETTINGS_PATH, "r") as f:
                    saved = json.load(f)
                return {**DEFAULT_SETTINGS, **saved}
            except Exception:
                pass
        return DEFAULT_SETTINGS.copy()

    def save_settings(self):
        try:
            with open(SETTINGS_PATH, "w") as f:
                json.dump(self.settings, f, indent=2)
        except Exception:
            pass

    def _build_ui(
        self, Toolbar, Sidebar, TabManager,
        Terminal, SearchBar, StatusBar, MenuBar,
    ):
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(2, weight=1)

        # Toolbar
        self.toolbar = Toolbar(self.root, self)
        self.toolbar.frame.grid(row=0, column=0, columnspan=2, sticky="ew")

        # Search bar (hidden by default)
        self.search_bar = SearchBar(self.root, self)
        self.search_bar.frame.grid(row=1, column=0, columnspan=2, sticky="ew")
        self.search_bar.hide()

        # Main content area
        self.main_pane = ttk.PanedWindow(self.root, orient=HORIZONTAL)
        self.main_pane.grid(row=2, column=0, columnspan=2, sticky="nsew")

        # Sidebar
        self.sidebar = Sidebar(self.main_pane, self)
        self.main_pane.add(self.sidebar.frame, weight=0)

        # Right side: editor + terminal
        self.right_pane = ttk.PanedWindow(self.main_pane, orient=VERTICAL)
        self.main_pane.add(self.right_pane, weight=1)

        # Tab manager
        self.tab_manager = TabManager(self.right_pane, self)
        self.right_pane.add(self.tab_manager.frame, weight=1)

        # Terminal
        self.terminal = Terminal(self.right_pane, self)
        self.right_pane.add(self.terminal.frame, weight=0)

        # Statusbar
        self.statusbar = StatusBar(self.root, self)
        self.statusbar.frame.grid(row=3, column=0, columnspan=2, sticky="ew")

        # Menubar
        self.menubar = MenuBar(self.root, self)

    def _apply_custom_colors(self):
        c = self.colors
        self.root.configure(bg=c["bg_primary"])
        style = ttk.Style()
        style.configure("Sidebar.TFrame", background=c["sidebar_bg"])
        style.configure("Editor.TFrame", background=c["editor_bg"])
        style.configure(
            "Status.TLabel",
            background=c["bg_tertiary"],
            foreground=c["fg_secondary"],
            font=("Segoe UI", 9),
        )

    def _show_welcome(self):
        welcome = self._WelcomeTab(self)
        welcome.show()

    def set_status(self, text):
        self.statusbar.set_text(text)

    def toggle_sidebar(self):
        self.sidebar.toggle()

    def toggle_terminal(self):
        self.terminal.toggle()

    def toggle_search(self):
        self.search_bar.toggle()

    def switch_theme(self):
        if self.settings["theme"] == "dark":
            self.settings["theme"] = "light"
            self.root.style.theme_use("cosmo")
        else:
            self.settings["theme"] = "dark"
            self.root.style.theme_use("darkly")

        from src.utils.theme_loader import ThemeLoader
        self.theme_loader = ThemeLoader(self.settings["theme"])
        self.colors = self.theme_loader.colors
        self.syntax_colors = self.theme_loader.syntax
        self._apply_custom_colors()
        self.tab_manager.refresh_all_highlighting()
        self.save_settings()
        self.set_status(f"Theme: {self.settings['theme'].title()}")

    def open_project(self, path=None):
        if path is None:
            from tkinter import filedialog
            path = filedialog.askdirectory(title="Open Project Folder")
        if path and os.path.isdir(path):
            self.current_project_path = path
            self.sidebar.file_tree.load_directory(path)
            self.root.title(
                f"{APP_NAME} — {os.path.basename(path)} — {APP_AUTHOR}"
            )
            self.set_status(f"Project: {path}")

    def run(self):
        self.root.mainloop()