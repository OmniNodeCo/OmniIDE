"""Main application — v1.0.3."""

import tkinter as tk
import tkinter.ttk as tkttk
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
            title=f"{APP_NAME} v{APP_VERSION} — {APP_AUTHOR}",
            themename=theme_name,
            size=(self.settings["window_width"], self.settings["window_height"]),
            minsize=(800, 500),
        )

        self.root.withdraw()

        from src.ui.splash import SplashScreen
        self.splash = SplashScreen(self.root)
        self.splash.update_status("Loading modules...")

        from src.utils.theme_loader import ThemeLoader
        from src.utils.recent_files import RecentFilesManager
        from src.utils.shortcuts import ShortcutManager
        from src.utils.styles import apply_global_styles
        from src.core.file_manager import FileManager
        from src.core.tab_manager import TabManager
        from src.core.terminal import Terminal
        from src.core.search import SearchBar
        from src.core.git_manager import GitManager
        from src.core.extension_manager import ExtensionManager
        from src.core.command_palette import CommandPalette
        from src.core.updater import Updater
        from src.ui.menubar import MenuBar
        from src.ui.sidebar import Sidebar
        from src.ui.statusbar import StatusBar
        from src.ui.toolbar import Toolbar
        from src.ui.welcome import WelcomeTab
        from src.ui.settings_panel import SettingsPanel

        self._WelcomeTab = WelcomeTab

        self.splash.update_status("Loading theme...")
        self.splash.set_progress(10)

        self.theme_loader = ThemeLoader(self.settings["theme"])
        self.colors = self.theme_loader.colors
        self.syntax_colors = self.theme_loader.syntax

        self.splash.update_status("Initializing managers...")
        self.splash.set_progress(25)

        self.recent_files_manager = RecentFilesManager()
        self.file_manager = FileManager(self)
        self.git_manager = GitManager(self)
        self.extension_manager = ExtensionManager(self)
        self.updater = Updater(self)
        self.settings_panel = SettingsPanel(self)
        self.current_project_path = None

        self.splash.update_status("Building interface...")
        self.splash.set_progress(45)

        self._build_ui(
            Toolbar, Sidebar, TabManager,
            Terminal, SearchBar, StatusBar, MenuBar,
        )

        self.splash.update_status("Initializing command palette...")
        self.splash.set_progress(60)

        self.command_palette = CommandPalette(self)

        self.splash.update_status("Applying styles...")
        self.splash.set_progress(75)

        apply_global_styles(self)

        self.splash.update_status("Binding shortcuts...")
        self.splash.set_progress(88)

        self.shortcut_manager = ShortcutManager(self)
        self.shortcut_manager.bind_all()

        self.splash.update_status("Ready!")
        self.splash.set_progress(100)

        self.root.after(600, self._finish_startup)

    def _finish_startup(self):
        self.splash.close()
        self.root.deiconify()
        self._show_welcome()
        self.root.focus_force()

        # Auto check for updates
        self.updater.check_on_startup()

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
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(2, weight=1)

        self.toolbar = Toolbar(self.root, self)
        self.toolbar.frame.grid(row=0, column=0, sticky="ew")

        self.search_bar = SearchBar(self.root, self)
        self.search_bar.frame.grid(row=1, column=0, sticky="ew")
        self.search_bar.hide()

        self.main_pane = tkttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.main_pane.grid(row=2, column=0, sticky="nsew")

        self.sidebar = Sidebar(self.main_pane, self)
        self.main_pane.add(self.sidebar.frame, weight=0)

        self.right_pane = tkttk.PanedWindow(self.main_pane, orient=tk.VERTICAL)
        self.main_pane.add(self.right_pane, weight=1)

        self.tab_manager = TabManager(self.right_pane, self)
        self.right_pane.add(self.tab_manager.frame, weight=1)

        self.terminal = Terminal(self.right_pane, self)
        self.right_pane.add(self.terminal.frame, weight=0)

        self.statusbar = StatusBar(self.root, self)
        self.statusbar.frame.grid(row=3, column=0, sticky="ew")

        self.menubar = MenuBar(self.root, self)

    def switch_theme(self):
        from src.utils.styles import apply_global_styles

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
        apply_global_styles(self)
        self.tab_manager.refresh_all_highlighting()
        self.save_settings()
        self.set_status(f"Theme: {self.settings['theme'].title()}")

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

    def toggle_command_palette(self):
        self.command_palette.toggle()

    def open_settings(self):
        self.settings_panel.show()

    def check_for_updates(self):
        self.updater.check_now(silent=False)

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
            self.git_manager.detect_repo(path)

    def run(self):
        self.root.mainloop()