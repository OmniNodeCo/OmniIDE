"""Main application window — PyQt6."""

import json
import os

from PyQt6.QtWidgets import (
    QMainWindow, QSplitter, QTabWidget, QWidget, QVBoxLayout,
    QHBoxLayout, QFileDialog, QMessageBox, QApplication,
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QFontDatabase, QIcon, QShortcut, QKeySequence

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
from src.ui.editor_widget import EditorTabWidget, BreadcrumbBar
from src.ui.minimap import Minimap
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
        self._setup_autosave()

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
                merged = {**DEFAULT_SETTINGS, **saved}
                return merged
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

        # Breadcrumbs
        self.breadcrumbs = BreadcrumbBar(self)
        right_layout.addWidget(self.breadcrumbs)

        # Editor/terminal splitter
        self.editor_terminal_splitter = QSplitter(Qt.Orientation.Vertical)
        right_layout.addWidget(self.editor_terminal_splitter)

        # Editor tabs + minimap (side by side)
        editor_row = QWidget()
        editor_row_layout = QHBoxLayout(editor_row)
        editor_row_layout.setContentsMargins(0, 0, 0, 0)
        editor_row_layout.setSpacing(0)

        self.editor_tabs = EditorTabWidget(self)
        editor_row_layout.addWidget(self.editor_tabs, 1)

        self.minimap = Minimap(self)
        editor_row_layout.addWidget(self.minimap, 0)
        self.minimap.setVisible(bool(self.settings.get("minimap_enabled")))

        self.editor_terminal_splitter.addWidget(editor_row)

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

        # Follow editor for breadcrumbs + minimap
        self.editor_tabs.tabs.currentChanged.connect(self._on_editor_tab_changed)

    def _on_editor_tab_changed(self, _index):
        self.breadcrumbs.refresh()
        editor = self.editor_tabs.get_current_code_editor()
        if self.settings.get("minimap_enabled"):
            self.minimap.attach(editor)
        else:
            self.minimap.attach(None)

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
        self.breadcrumbs.refresh_colors()
        self.save_settings()
        self.set_status(f"Theme: {self.settings['theme'].title()}")

    def _setup_shortcuts(self):
        shortcuts = {
            "Ctrl+N": self.file_manager.new_file,
            "Ctrl+O": self.file_manager.open_file,
            "Ctrl+S": self.file_manager.save_file,
            "Ctrl+Shift+S": self.file_manager.save_file_as,
            "Ctrl+Alt+S": self.file_manager.save_all,
            "Ctrl+W": self.editor_tabs.close_current_tab,
            "Ctrl+F": self.toggle_search,
            "Ctrl+B": self.toggle_sidebar,
            "Ctrl+`": self.toggle_terminal,
            "Ctrl+Shift+P": self.open_command_palette,
            "Ctrl+P": self.open_quick_open,
            "Ctrl+Shift+F": self.open_search,
            "Ctrl+Shift+T": self.new_terminal,
            "Ctrl+,": self.open_settings,
            "Ctrl+G": self.go_to_line,
            "Ctrl+/": self.toggle_comment,
            "Ctrl+D": self.duplicate_line,
            "Ctrl+Shift+D": self.delete_line,
            "Alt+Up": self.move_line_up,
            "Alt+Down": self.move_line_down,
            "Ctrl+Shift+O": self.sort_lines,
            "Ctrl+Shift+V": self.toggle_markdown_preview,
            "Ctrl+=": lambda: self._zoom(1),
            "Ctrl+-": lambda: self._zoom(-1),
            "Ctrl+0": lambda: self._zoom(0),
        }

        for key, func in shortcuts.items():
            shortcut = QShortcut(QKeySequence(key), self)
            shortcut.activated.connect(func)

    def _setup_autosave(self):
        self._autosave_timer = QTimer(self)
        self._autosave_timer.setInterval(
            max(5, self.settings.get("auto_save_interval", 30)) * 1000
        )
        self._autosave_timer.timeout.connect(self.file_manager.autosave_tick)
        if self.settings.get("auto_save"):
            self._autosave_timer.start()

    def set_status(self, text):
        self.statusbar.set_text(text)

    def toggle_sidebar(self):
        self.sidebar.setVisible(not self.sidebar.isVisible())

    def toggle_terminal(self):
        self.terminal.setVisible(not self.terminal.isVisible())

    def toggle_search(self):
        self.editor_tabs.toggle_search()

    def toggle_comment(self):
        editor = self.editor_tabs.get_current_code_editor()
        if editor:
            editor.toggle_comment()

    def duplicate_line(self):
        editor = self.editor_tabs.get_current_code_editor()
        if editor:
            editor.duplicate_line()

    def delete_line(self):
        editor = self.editor_tabs.get_current_code_editor()
        if editor:
            editor.delete_line()

    def move_line_up(self):
        editor = self.editor_tabs.get_current_code_editor()
        if editor:
            editor.move_line_up()

    def move_line_down(self):
        editor = self.editor_tabs.get_current_code_editor()
        if editor:
            editor.move_line_down()

    def sort_lines(self):
        editor = self.editor_tabs.get_current_code_editor()
        if editor:
            editor.sort_lines()

    def open_command_palette(self):
        dialog = CommandPaletteDialog(self)
        dialog.exec()

    def open_quick_open(self):
        if not self.current_project_path:
            self.set_status("Open a folder to use Quick Open")
            return
        from src.ui.quick_open import QuickOpenDialog
        dialog = QuickOpenDialog(self)
        dialog.exec()

    def open_search(self):
        self.sidebar._switch("search")
        self.sidebar.search_panel.search_input.setFocus()
        self.set_status("Search in Files")

    def new_terminal(self):
        self.terminal.new_terminal()
        self.set_status("New terminal")

    def open_settings(self):
        dialog = SettingsDialog(self)
        dialog.accepted.connect(self._on_settings_applied)
        dialog.exec()

    def _on_settings_applied(self):
        self._setup_autosave()
        if self.settings.get("auto_save"):
            self._autosave_timer.start()
        else:
            self._autosave_timer.stop()
        self.minimap.setVisible(bool(self.settings.get("minimap_enabled")))
        self.editor_tabs.apply_font()
        self.editor_tabs.apply_word_wrap()
        self.sidebar.file_tree.set_show_hidden(
            bool(self.settings.get("show_hidden_files")))

    def toggle_markdown_preview(self):
        editor = self.editor_tabs.get_current_code_editor()
        if not editor or not getattr(editor, "filepath", None):
            self.set_status("Open a .md file first")
            return
        path = editor.filepath
        if os.path.splitext(path)[1].lower() != ".md":
            self.set_status("Markdown preview works on .md files")
            return
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                md = f.read()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Cannot read file:\n{e}")
            return
        from src.core.markdown import to_html, wrap_page
        c = self.colors
        css = f"""
        body {{ font-family: 'Segoe UI', sans-serif; font-size: 14px;
               line-height: 1.6; color: {c['editor_fg']}; }}
        body {{ background-color: {c['editor_bg']}; }}
        pre {{ background: {c['terminal_bg']}; padding: 12px;
              border-radius: 6px; overflow-x: auto; }}
        code {{ background: {c['bg_tertiary']}; padding: 2px 5px;
               border-radius: 4px; font-family: 'Consolas', monospace; }}
        pre code {{ background: none; padding: 0; }}
        a {{ color: {c['accent']}; }}
        table {{ border-collapse: collapse; margin: 8px 0; }}
        th, td {{ border: 1px solid {c['border']}; padding: 6px 10px; }}
        blockquote {{ border-left: 3px solid {c['accent']}; margin: 8px 0;
                     padding: 4px 12px; color: {c['fg_secondary']}; }}
        img {{ max-width: 100%; }}
        h1, h2, h3, h4 {{ margin-top: 1.2em; }}
        hr {{ border: none; border-top: 1px solid {c['border']}; margin: 16px 0; }}
        """
        html = wrap_page(to_html(md), os.path.basename(path), css=css)
        self.editor_tabs.new_preview_tab(html, f"{os.path.basename(path)} (preview)")
        self.set_status("Markdown preview")

    def go_to_line(self):
        from PyQt6.QtWidgets import QInputDialog
        editor = self.editor_tabs.get_current_code_editor()
        if not editor:
            return
        line, ok = QInputDialog.getInt(self, "Go to Line", "Line:", 1, 1, 999999)
        if ok:
            editor.goto_line(line)
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

    def toggle_minimap(self):
        self.settings["minimap_enabled"] = not self.settings.get("minimap_enabled", False)
        self.minimap.setVisible(bool(self.settings["minimap_enabled"]))
        if self.settings["minimap_enabled"]:
            self.minimap.attach(self.editor_tabs.get_current_code_editor())
        self.save_settings()
        self.set_status(f"Minimap: {'on' if self.settings['minimap_enabled'] else 'off'}")

    def toggle_hidden_files(self):
        self.settings["show_hidden_files"] = not self.settings.get("show_hidden_files", False)
        self.sidebar.file_tree.set_show_hidden(self.settings["show_hidden_files"])
        self.save_settings()
        self.set_status(f"Hidden files: {'shown' if self.settings['show_hidden_files'] else 'hidden'}")

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
