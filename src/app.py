"""Main application window — PyQt6."""

import json
import os

from PyQt6.QtWidgets import (
    QMainWindow, QSplitter, QTabWidget, QWidget, QVBoxLayout,
    QHBoxLayout, QFileDialog, QMessageBox, QApplication,
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QFontDatabase, QIcon

from src.config import (
    APP_NAME, APP_VERSION, APP_AUTHOR,
    DEFAULT_SETTINGS, SETTINGS_PATH, ASSETS_DIR,
)
from src.utils.theme_loader import ThemeLoader
from src.utils.recent_files import RecentFilesManager
from src.core.file_manager import FileManager
from src.core.git_manager import GitManager
from src.core.git_installer import GitInstaller
from src.core.extension_manager import ExtensionManager
from src.core.updater import Updater
from src.ui.editor_widget import EditorTabWidget
from src.ui.sidebar import Sidebar
from src.ui.terminal_widget import TerminalWidget
from src.ui.toolbar import Toolbar
from src.ui.statusbar import StatusBar
from src.ui.menubar import MenuBarBuilder
from src.ui.command_palette import CommandPaletteDialog
from src.ui.settings_dialog import SettingsDialog
from src.ui.splash import SplashScreen
from src.ui.theme_stylesheet import build_stylesheet


class OmniIDEApp(QMainWindow):
    """Main IDE window."""

    def __init__(self):
        super().__init__()
        self.settings = self._load_settings()
        self.current_project_path = None

        # Show splash
        self.splash = SplashScreen()
        self.splash.show()
        self.splash.set_status("Loading theme...")
        QApplication.processEvents()

        # Theme
        self.theme_loader = ThemeLoader(self.settings["theme"])
        self.colors = self.theme_loader.colors
        self.syntax_colors = self.theme_loader.syntax

        self.splash.set_progress(15)
        self.splash.set_status("Initializing managers...")
        QApplication.processEvents()

        # Managers
        self.recent_files_manager = RecentFilesManager()
        self.file_manager = FileManager(self)
        self.git_manager = GitManager(self)
        self.git_installer = GitInstaller(self)
        self.extension_manager = ExtensionManager(self)
        self.updater = Updater(self)

        self.splash.set_progress(35)
        self.splash.set_status("Building interface...")
        QApplication.processEvents()

        # Window setup
        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION} — {APP_AUTHOR}")
        self.resize(self.settings["window_width"], self.settings["window_height"])
        self.setMinimumSize(800, 500)

        icon_path = os.path.join(ASSETS_DIR, "icon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self._build_ui()

        self.splash.set_progress(65)
        self.splash.set_status("Applying styles...")
        QApplication.processEvents()

        self._apply_theme()

        self.splash.set_progress(85)
        self.splash.set_status("Setting up shortcuts...")
        QApplication.processEvents()

        self._setup_shortcuts()

        self.splash.set_progress(100)
        self.splash.set_status("Ready!")
        QApplication.processEvents()

        # Close splash after delay
        QTimer.singleShot(500, self._finish_startup)

    def _finish_startup(self):
        self.splash.close()
        self.editor_tabs.add_welcome_tab()
        self.git_installer.check_and_prompt()
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

    def _build_ui(self):
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Toolbar
        self.toolbar = Toolbar(self)
        layout.addWidget(self.toolbar)

        # Main splitter (sidebar | editor+terminal)
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(self.main_splitter, 1)

        # Sidebar
        self.sidebar = Sidebar(self)
        self.main_splitter.addWidget(self.sidebar)

        # Right side (editor + terminal)
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        # Editor/terminal splitter
        self.editor_terminal_splitter = QSplitter(Qt.Orientation.Vertical)
        right_layout.addWidget(self.editor_terminal_splitter)

        # Editor tabs
        self.editor_tabs = EditorTabWidget(self)
        self.editor_terminal_splitter.addWidget(self.editor_tabs)

        # Terminal
        self.terminal = TerminalWidget(self)
        self.editor_terminal_splitter.addWidget(self.terminal)

        self.editor_terminal_splitter.setSizes([500, 200])

        self.main_splitter.addWidget(right_widget)
        self.main_splitter.setSizes([self.settings["sidebar_width"], 900])

        # Status bar
        self.statusbar = StatusBar(self)
        layout.addWidget(self.statusbar)

        # Menu bar
        MenuBarBuilder(self)

    def _apply_theme(self):
        stylesheet = build_stylesheet(self.colors)
        self.setStyleSheet(stylesheet)

    def switch_theme(self):
        if self.settings["theme"] == "dark":
            self.settings["theme"] = "light"
        else:
            self.settings["theme"] = "dark"

        self.theme_loader = ThemeLoader(self.settings["theme"])
        self.colors = self.theme_loader.colors
        self.syntax_colors = self.theme_loader.syntax
        self._apply_theme()
        self.editor_tabs.refresh_all()
        self.save_settings()
        self.set_status(f"Theme: {self.settings['theme'].title()}")

    def _setup_shortcuts(self):
        from PyQt6.QtGui import QShortcut, QKeySequence

        shortcuts = {
            "Ctrl+N": self.file_manager.new_file,
            "Ctrl+O": self.file_manager.open_file,
            "Ctrl+S": self.file_manager.save_file,
            "Ctrl+Shift+S": self.file_manager.save_file_as,
            "Ctrl+W": self.editor_tabs.close_current_tab,
            "Ctrl+F": self.toggle_search,
            "Ctrl+B": self.toggle_sidebar,
            "Ctrl+`": self.toggle_terminal,
            "Ctrl+Shift+P": self.open_command_palette,
            "Ctrl+,": self.open_settings,
            "Ctrl+G": self.go_to_line,
            "Ctrl+=": lambda: self._zoom(1),
            "Ctrl+-": lambda: self._zoom(-1),
            "Ctrl+0": lambda: self._zoom(0),
        }

        for key, func in shortcuts.items():
            shortcut = QShortcut(QKeySequence(key), self)
            shortcut.activated.connect(func)

    def set_status(self, text):
        self.statusbar.set_text(text)

    def toggle_sidebar(self):
        self.sidebar.setVisible(not self.sidebar.isVisible())

    def toggle_terminal(self):
        self.terminal.setVisible(not self.terminal.isVisible())

    def toggle_search(self):
        self.editor_tabs.toggle_search()

    def open_command_palette(self):
        dialog = CommandPaletteDialog(self)
        dialog.exec()

    def open_settings(self):
        dialog = SettingsDialog(self)
        dialog.exec()

    def go_to_line(self):
        from PyQt6.QtWidgets import QInputDialog
        editor = self.editor_tabs.get_current_editor()
        if not editor:
            return
        line, ok = QInputDialog.getInt(self, "Go to Line", "Line:", 1, 1, 999999)
        if ok:
            cursor = editor.textCursor()
            block = editor.document().findBlockByLineNumber(line - 1)
            cursor.setPosition(block.position())
            editor.setTextCursor(cursor)
            editor.centerCursor()
            self.set_status(f"Line {line}")

    def open_project(self, path=None):
        if path is None:
            path = QFileDialog.getExistingDirectory(self, "Open Project Folder")
        if path and os.path.isdir(path):
            self.current_project_path = path
            self.sidebar.file_tree.load_directory(path)
            self.setWindowTitle(f"{APP_NAME} — {os.path.basename(path)} — {APP_AUTHOR}")
            self.set_status(f"Project: {path}")
            self.git_manager.detect_repo(path)

    def check_for_updates(self):
        self.updater.check_now(silent=False)

    def _zoom(self, direction):
        if direction == 0:
            self.settings["font_size"] = 13
        elif direction > 0:
            self.settings["font_size"] = min(32, self.settings["font_size"] + 1)
        else:
            self.settings["font_size"] = max(8, self.settings["font_size"] - 1)

        self.editor_tabs.apply_font()
        self.save_settings()
        self.set_status(f"Font size: {self.settings['font_size']}")

    def closeEvent(self, event):
        self.terminal.stop_shell()
        self.save_settings()
        event.accept()