"""GUI tests — creates a Tk root and tests all widgets can be instantiated."""

import unittest
import sys
import os
import tkinter as tk

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class MockApp:
    """Minimal mock of OmniIDEApp for GUI testing without full startup."""

    def __init__(self, root):
        self.root = root
        self.settings = {
            "theme": "dark",
            "font_family": "Consolas",
            "font_size": 13,
            "tab_size": 4,
            "show_line_numbers": True,
            "word_wrap": False,
            "auto_indent": True,
            "auto_save": False,
            "auto_check_updates": True,
            "window_width": 1200,
            "window_height": 750,
            "sidebar_width": 280,
            "terminal_height": 200,
            "max_recent_files": 15,
            "default_shell": "auto",
            "installed_extensions": [],
            "highlight_current_line": True,
            "show_whitespace": False,
            "cursor_blink": True,
            "minimap_enabled": False,
            "suppress_git_prompt": False,
        }

        from src.utils.theme_loader import ThemeLoader
        self.theme_loader = ThemeLoader("dark")
        self.colors = self.theme_loader.colors
        self.syntax_colors = self.theme_loader.syntax
        self.current_project_path = None

    def set_status(self, text):
        pass

    def save_settings(self):
        pass

    def toggle_sidebar(self):
        pass

    def toggle_terminal(self):
        pass

    def toggle_search(self):
        pass

    def toggle_command_palette(self):
        pass

    def open_settings(self):
        pass

    def check_for_updates(self):
        pass

    def switch_theme(self):
        pass

    def open_project(self, path=None):
        pass


class MockFileManager:
    """Mock file manager."""

    def new_file(self):
        pass

    def open_file(self, filepath=None):
        pass

    def save_file(self):
        pass

    def save_file_as(self):
        pass


class MockGitManager:
    """Mock git manager."""

    def has_git(self):
        return False

    def detect_repo(self, path):
        return False

    def clone_repo(self):
        pass

    def init_repo(self):
        pass

    def git_status(self):
        pass

    def git_diff(self):
        pass

    def git_add_all(self):
        pass

    def git_commit(self):
        pass

    def git_push(self):
        pass

    def git_pull(self):
        pass

    def git_log(self):
        pass

    def git_branch(self):
        pass

    def add_remote(self):
        pass


class MockTabManager:
    """Mock tab manager."""

    def __init__(self):
        self.tabs = {}

    def new_tab(self, filepath=None, content="", title=None):
        return "tab_1"

    def get_active_editor(self):
        return None

    def get_active_tab_info(self):
        return None

    def close_active_tab(self):
        pass

    def refresh_all_highlighting(self):
        pass

    def has_tabs(self):
        return False


class MockExtensionManager:
    """Mock extension manager."""

    def get_installed(self):
        return []

    def search(self, query, callback, page_size=15):
        callback([], None)

    def install_extension(self, ext_info, callback):
        callback(True, "Installed")

    def uninstall_extension(self, ext_id):
        return True, "Uninstalled"

    @staticmethod
    def format_installs(count):
        if count >= 1_000_000:
            return f"{count / 1_000_000:.1f}M"
        elif count >= 1_000:
            return f"{count / 1_000:.1f}K"
        return str(count)

    @staticmethod
    def format_rating(rating):
        return f"{rating}"


class MockUpdater:
    """Mock updater."""

    def check_now(self, silent=False):
        pass

    def check_on_startup(self):
        pass


class MockRecentFiles:
    """Mock recent files manager."""

    def get_all(self):
        return []

    def add(self, filepath):
        pass

    def clear(self):
        pass


def setup_mock_app(root):
    """Create a fully mocked app for widget testing."""
    app = MockApp(root)
    app.file_manager = MockFileManager()
    app.git_manager = MockGitManager()
    app.tab_manager = MockTabManager()
    app.extension_manager = MockExtensionManager()
    app.updater = MockUpdater()
    app.recent_files_manager = MockRecentFiles()
    return app


class TestEditorWidget(unittest.TestCase):
    """Test CodeEditor and LineNumbers can be created."""

    @classmethod
    def setUpClass(cls):
        cls.root = tk.Tk()
        cls.root.withdraw()
        cls.app = setup_mock_app(cls.root)

    @classmethod
    def tearDownClass(cls):
        cls.root.destroy()

    def test_create_editor(self):
        from src.core.editor import CodeEditor
        editor = CodeEditor(self.root, self.app, filepath="test.py")
        self.assertIsNotNone(editor)
        editor.destroy()

    def test_editor_set_content(self):
        from src.core.editor import CodeEditor
        editor = CodeEditor(self.root, self.app, filepath="test.py")
        editor.set_content("print('hello')")
        content = editor.get_content()
        self.assertEqual(content, "print('hello')")
        editor.destroy()

    def test_editor_empty_content(self):
        from src.core.editor import CodeEditor
        editor = CodeEditor(self.root, self.app, filepath="test.py")
        editor.set_content("")
        content = editor.get_content()
        self.assertEqual(content, "")
        editor.destroy()

    def test_editor_multiline(self):
        from src.core.editor import CodeEditor
        editor = CodeEditor(self.root, self.app, filepath="test.py")
        text = "line1\nline2\nline3"
        editor.set_content(text)
        content = editor.get_content()
        self.assertEqual(content, text)
        editor.destroy()

    def test_editor_modified_flag(self):
        from src.core.editor import CodeEditor
        editor = CodeEditor(self.root, self.app, filepath="test.py")
        editor.set_content("hello")
        self.assertFalse(editor.modified)
        editor.destroy()

    def test_line_numbers_create(self):
        from src.core.editor import CodeEditor, LineNumbers
        editor = CodeEditor(self.root, self.app)
        ln = LineNumbers(self.root, editor, self.app.colors)
        self.assertIsNotNone(ln)
        ln.set_font(("Consolas", 13))
        ln.redraw()
        ln.destroy()
        editor.destroy()

    def test_editor_refresh_colors(self):
        from src.core.editor import CodeEditor
        editor = CodeEditor(self.root, self.app, filepath="test.py")
        editor.set_content("x = 1")
        editor.refresh_colors()
        editor.destroy()


class TestTabManager(unittest.TestCase):
    """Test TabManager widget."""

    @classmethod
    def setUpClass(cls):
        cls.root = tk.Tk()
        cls.root.withdraw()
        cls.app = setup_mock_app(cls.root)

    @classmethod
    def tearDownClass(cls):
        cls.root.destroy()

    def test_create_tab_manager(self):
        from src.core.tab_manager import TabManager
        frame = tk.Frame(self.root)
        tm = TabManager(frame, self.app)
        self.assertIsNotNone(tm)
        self.assertEqual(len(tm.tabs), 0)
        frame.destroy()

    def test_new_tab(self):
        from src.core.tab_manager import TabManager
        frame = tk.Frame(self.root)
        self.app.statusbar = type("obj", (object,), {
            "set_text": lambda self, t: None,
            "update_cursor_position": lambda self, e: None,
            "update_file_type": lambda self, f: None,
        })()
        tm = TabManager(frame, self.app)
        tab_id = tm.new_tab(content="hello", title="Test")
        self.assertIsNotNone(tab_id)
        self.assertEqual(len(tm.tabs), 1)
        frame.destroy()

    def test_new_tab_with_filepath(self):
        from src.core.tab_manager import TabManager
        frame = tk.Frame(self.root)
        self.app.statusbar = type("obj", (object,), {
            "set_text": lambda self, t: None,
            "update_cursor_position": lambda self, e: None,
            "update_file_type": lambda self, f: None,
        })()
        tm = TabManager(frame, self.app)
        tab_id = tm.new_tab(filepath="test.py", content="x = 1")
        self.assertIsNotNone(tab_id)
        info = list(tm.tabs.values())[0]
        self.assertEqual(info["filepath"], "test.py")
        frame.destroy()

    def test_get_active_editor_empty(self):
        from src.core.tab_manager import TabManager
        frame = tk.Frame(self.root)
        tm = TabManager(frame, self.app)
        self.assertIsNone(tm.get_active_editor())
        frame.destroy()

    def test_has_tabs(self):
        from src.core.tab_manager import TabManager
        frame = tk.Frame(self.root)
        self.app.statusbar = type("obj", (object,), {
            "set_text": lambda self, t: None,
            "update_cursor_position": lambda self, e: None,
            "update_file_type": lambda self, f: None,
        })()
        tm = TabManager(frame, self.app)
        self.assertFalse(tm.has_tabs())
        tm.new_tab(content="test")
        self.assertTrue(tm.has_tabs())
        frame.destroy()


class TestSearchBar(unittest.TestCase):
    """Test SearchBar widget."""

    @classmethod
    def setUpClass(cls):
        cls.root = tk.Tk()
        cls.root.withdraw()
        cls.app = setup_mock_app(cls.root)

    @classmethod
    def tearDownClass(cls):
        cls.root.destroy()

    def test_create_search_bar(self):
        from src.core.search import SearchBar
        sb = SearchBar(self.root, self.app)
        self.assertIsNotNone(sb)
        self.assertFalse(sb.visible)

    def test_show_hide(self):
        from src.core.search import SearchBar
        sb = SearchBar(self.root, self.app)
        sb.frame.grid(row=0, column=0)
        sb.show()
        self.assertTrue(sb.visible)
        sb.hide()
        self.assertFalse(sb.visible)

    def test_toggle(self):
        from src.core.search import SearchBar
        sb = SearchBar(self.root, self.app)
        sb.frame.grid(row=0, column=0)
        sb.toggle()
        self.assertTrue(sb.visible)
        sb.toggle()
        self.assertFalse(sb.visible)

    def test_clear_highlights_safe(self):
        from src.core.search import SearchBar
        sb = SearchBar(self.root, self.app)
        sb._clear_highlights()
        self.assertEqual(sb.matches, [])
        self.assertEqual(sb.current_match, -1)

    def test_get_editor_none(self):
        from src.core.search import SearchBar
        sb = SearchBar(self.root, self.app)
        self.assertIsNone(sb._get_editor())


class TestToolbar(unittest.TestCase):
    """Test Toolbar widget."""

    @classmethod
    def setUpClass(cls):
        cls.root = tk.Tk()
        cls.root.withdraw()
        cls.app = setup_mock_app(cls.root)

    @classmethod
    def tearDownClass(cls):
        cls.root.destroy()

    def test_create_toolbar(self):
        from src.ui.toolbar import Toolbar
        tb = Toolbar(self.root, self.app)
        self.assertIsNotNone(tb)
        self.assertIsNotNone(tb.frame)


class TestStatusBar(unittest.TestCase):
    """Test StatusBar widget."""

    @classmethod
    def setUpClass(cls):
        cls.root = tk.Tk()
        cls.root.withdraw()
        cls.app = setup_mock_app(cls.root)

    @classmethod
    def tearDownClass(cls):
        cls.root.destroy()

    def test_create_statusbar(self):
        from src.ui.statusbar import StatusBar
        sb = StatusBar(self.root, self.app)
        self.assertIsNotNone(sb)

    def test_set_text(self):
        from src.ui.statusbar import StatusBar
        sb = StatusBar(self.root, self.app)
        sb.set_text("Test status")

    def test_update_file_type(self):
        from src.ui.statusbar import StatusBar
        sb = StatusBar(self.root, self.app)
        sb.update_file_type("test.py")
        sb.update_file_type("test.js")
        sb.update_file_type(None)

    def test_update_git_branch(self):
        from src.ui.statusbar import StatusBar
        sb = StatusBar(self.root, self.app)
        sb.update_git_branch("main")
        sb.update_git_branch("")
        sb.update_git_branch(None)


class TestSidebar(unittest.TestCase):
    """Test Sidebar widget with all panels."""

    @classmethod
    def setUpClass(cls):
        cls.root = tk.Tk()
        cls.root.withdraw()
        cls.app = setup_mock_app(cls.root)

    @classmethod
    def tearDownClass(cls):
        cls.root.destroy()

    def test_create_sidebar(self):
        from src.ui.sidebar import Sidebar
        frame = tk.Frame(self.root)
        sb = Sidebar(frame, self.app)
        self.assertIsNotNone(sb)
        self.assertTrue(sb.visible)
        frame.destroy()

    def test_switch_panels(self):
        from src.ui.sidebar import Sidebar
        frame = tk.Frame(self.root)
        sb = Sidebar(frame, self.app)
        sb._switch_panel("explorer")
        self.assertEqual(sb.active_panel, "explorer")
        sb._switch_panel("git")
        self.assertEqual(sb.active_panel, "git")
        sb._switch_panel("extensions")
        self.assertEqual(sb.active_panel, "extensions")
        frame.destroy()

    def test_toggle(self):
        from src.ui.sidebar import Sidebar
        frame = tk.Frame(self.root)
        sb = Sidebar(frame, self.app)
        sb.frame.pack(side=tk.LEFT, fill=tk.Y)
        sb.toggle()
        self.assertFalse(sb.visible)
        sb.toggle()
        self.assertTrue(sb.visible)
        frame.destroy()


class TestFileTree(unittest.TestCase):
    """Test FileTree widget."""

    @classmethod
    def setUpClass(cls):
        cls.root = tk.Tk()
        cls.root.withdraw()
        cls.app = setup_mock_app(cls.root)

    @classmethod
    def tearDownClass(cls):
        cls.root.destroy()

    def test_create_file_tree(self):
        from src.ui.file_tree import FileTree
        ft = FileTree(self.root, self.app)
        self.assertIsNotNone(ft)

    def test_load_directory(self):
        import tempfile
        from src.ui.file_tree import FileTree
        ft = FileTree(self.root, self.app)

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create some files
            open(os.path.join(tmpdir, "test.py"), "w").close()
            open(os.path.join(tmpdir, "readme.md"), "w").close()
            os.makedirs(os.path.join(tmpdir, "src"), exist_ok=True)
            open(os.path.join(tmpdir, "src", "main.py"), "w").close()

            ft.load_directory(tmpdir)
            children = ft.tree.get_children()
            self.assertGreater(len(children), 0)


class TestExtensionsPanel(unittest.TestCase):
    """Test ExtensionsPanel widget."""

    @classmethod
    def setUpClass(cls):
        cls.root = tk.Tk()
        cls.root.withdraw()
        cls.app = setup_mock_app(cls.root)

    @classmethod
    def tearDownClass(cls):
        cls.root.destroy()

    def test_create_panel(self):
        from src.ui.extensions_panel import ExtensionsPanel
        ep = ExtensionsPanel(self.root, self.app)
        self.assertIsNotNone(ep)

    def test_clear_results(self):
        from src.ui.extensions_panel import ExtensionsPanel
        ep = ExtensionsPanel(self.root, self.app)
        ep._clear_results()
        self.assertEqual(len(ep.result_widgets), 0)

    def test_show_installed_empty(self):
        from src.ui.extensions_panel import ExtensionsPanel
        ep = ExtensionsPanel(self.root, self.app)
        ep._show_installed()


class TestMenuBar(unittest.TestCase):
    """Test MenuBar creation."""

    @classmethod
    def setUpClass(cls):
        cls.root = tk.Tk()
        cls.root.withdraw()
        cls.app = setup_mock_app(cls.root)
        cls.app.tab_manager = MockTabManager()

    @classmethod
    def tearDownClass(cls):
        cls.root.destroy()

    def test_create_menubar(self):
        from src.ui.menubar import MenuBar
        mb = MenuBar(self.root, self.app)
        self.assertIsNotNone(mb)
        self.assertIsNotNone(mb.menu)


class TestWelcomeTab(unittest.TestCase):
    """Test WelcomeTab content generation."""

    @classmethod
    def setUpClass(cls):
        cls.root = tk.Tk()
        cls.root.withdraw()
        cls.app = setup_mock_app(cls.root)

    @classmethod
    def tearDownClass(cls):
        cls.root.destroy()

    def test_build_text(self):
        from src.ui.welcome import WelcomeTab
        wt = WelcomeTab(self.app)
        text = wt._build_text()
        self.assertIn("OmniIDE", text)
        self.assertIn("OmniNodeCo", text)
        self.assertIn("Ctrl+", text)

    def test_build_text_contains_version(self):
        from src.ui.welcome import WelcomeTab
        from src.config import APP_VERSION
        wt = WelcomeTab(self.app)
        text = wt._build_text()
        self.assertIn(APP_VERSION, text)


class TestSplashScreen(unittest.TestCase):
    """Test SplashScreen creation and methods."""

    @classmethod
    def setUpClass(cls):
        cls.root = tk.Tk()
        cls.root.withdraw()

    @classmethod
    def tearDownClass(cls):
        cls.root.destroy()

    def test_create_splash(self):
        from src.ui.splash import SplashScreen
        splash = SplashScreen(self.root)
        self.assertIsNotNone(splash)
        self.assertIsNotNone(splash.window)
        splash.close()
        self.root.update()

    def test_update_status(self):
        from src.ui.splash import SplashScreen
        splash = SplashScreen(self.root)
        splash.update_status("Testing...")
        splash.update_status("Done!")
        splash.close()
        self.root.update()

    def test_set_progress(self):
        from src.ui.splash import SplashScreen
        splash = SplashScreen(self.root)
        splash.set_progress(0)
        splash.set_progress(25)
        splash.set_progress(50)
        splash.set_progress(75)
        splash.set_progress(100)
        splash.close()
        self.root.update()


class TestCommandPalette(unittest.TestCase):
    """Test CommandPalette without full app."""

    @classmethod
    def setUpClass(cls):
        cls.root = tk.Tk()
        cls.root.withdraw()
        cls.app = setup_mock_app(cls.root)
        cls.app.tab_manager = MockTabManager()
        cls.app.sidebar = type("obj", (object,), {
            "_switch_panel": lambda self, p: None,
        })()
        cls.app.terminal = type("obj", (object,), {
            "clear": lambda self: None,
            "restart_shell": lambda self: None,
        })()

    @classmethod
    def tearDownClass(cls):
        cls.root.destroy()

    def test_create_palette(self):
        from src.core.command_palette import CommandPalette
        cp = CommandPalette(self.app)
        self.assertIsNotNone(cp)
        self.assertFalse(cp.visible)
        self.assertGreater(len(cp.commands), 30)

    def test_fuzzy_score_exact(self):
        from src.core.command_palette import CommandPalette
        cp = CommandPalette(self.app)
        score = cp._fuzzy_score("save", "file: save")
        self.assertGreater(score, 0)

    def test_fuzzy_score_partial(self):
        from src.core.command_palette import CommandPalette
        cp = CommandPalette(self.app)
        score = cp._fuzzy_score("sv", "file: save")
        self.assertGreater(score, 0)

    def test_fuzzy_score_no_match(self):
        from src.core.command_palette import CommandPalette
        cp = CommandPalette(self.app)
        score = cp._fuzzy_score("xyz", "file: save")
        self.assertEqual(score, 0)

    def test_show_close(self):
        from src.core.command_palette import CommandPalette
        cp = CommandPalette(self.app)
        cp.show()
        self.assertTrue(cp.visible)
        self.assertIsNotNone(cp.window)
        cp.close()
        self.assertFalse(cp.visible)

    def test_toggle(self):
        from src.core.command_palette import CommandPalette
        cp = CommandPalette(self.app)
        cp.toggle()
        self.assertTrue(cp.visible)
        cp.toggle()
        self.assertFalse(cp.visible)

    def test_filter_commands_empty(self):
        from src.core.command_palette import CommandPalette
        cp = CommandPalette(self.app)
        cp.show()
        cp._filter_commands("")
        self.assertEqual(len(cp.filtered), len(cp.commands))
        cp.close()

    def test_filter_commands_query(self):
        from src.core.command_palette import CommandPalette
        cp = CommandPalette(self.app)
        cp.show()
        cp._filter_commands("save")
        self.assertGreater(len(cp.filtered), 0)
        self.assertLess(len(cp.filtered), len(cp.commands))
        cp.close()

    def test_all_commands_have_required_keys(self):
        from src.core.command_palette import CommandPalette
        cp = CommandPalette(self.app)
        for cmd in cp.commands:
            self.assertIn("label", cmd)
            self.assertIn("detail", cmd)
            self.assertIn("category", cmd)
            self.assertIn("shortcut", cmd)
            self.assertIn("action", cmd)
            self.assertTrue(callable(cmd["action"]))


class TestSettingsPanel(unittest.TestCase):
    """Test SettingsPanel creation."""

    @classmethod
    def setUpClass(cls):
        cls.root = tk.Tk()
        cls.root.withdraw()
        cls.app = setup_mock_app(cls.root)
        cls.app.tab_manager = MockTabManager()

    @classmethod
    def tearDownClass(cls):
        cls.root.destroy()

    def test_create_panel(self):
        from src.ui.settings_panel import SettingsPanel
        sp = SettingsPanel(self.app)
        self.assertIsNotNone(sp)

    def test_show_and_close(self):
        from src.ui.settings_panel import SettingsPanel
        sp = SettingsPanel(self.app)
        sp.show()
        self.assertIsNotNone(sp.window)
        self.assertTrue(sp.window.winfo_exists())
        sp.window.destroy()


class TestIconManager(unittest.TestCase):
    """Test IconManager with a real Tk root."""

    @classmethod
    def setUpClass(cls):
        cls.root = tk.Tk()
        cls.root.withdraw()

    @classmethod
    def tearDownClass(cls):
        cls.root.destroy()

    def test_create_manager(self):
        from src.utils.icon_manager import IconManager
        mgr = IconManager()
        self.assertIsNotNone(mgr)

    def test_get_icon(self):
        from src.utils.icon_manager import IconManager
        mgr = IconManager()
        icon = mgr.get("file", 16)
        self.assertIsNotNone(icon)

    def test_get_unknown_icon(self):
        from src.utils.icon_manager import IconManager
        mgr = IconManager()
        icon = mgr.get("nonexistent_icon_xyz", 16)
        self.assertIsNotNone(icon)

    def test_icon_caching(self):
        from src.utils.icon_manager import IconManager
        mgr = IconManager()
        icon1 = mgr.get("file", 16)
        icon2 = mgr.get("file", 16)
        self.assertIs(icon1, icon2)

    def test_different_sizes(self):
        from src.utils.icon_manager import IconManager
        mgr = IconManager()
        icon16 = mgr.get("file", 16)
        icon32 = mgr.get("file", 32)
        self.assertIsNotNone(icon16)
        self.assertIsNotNone(icon32)


class TestStyles(unittest.TestCase):
    """Test style utilities with real Tk widgets."""

    @classmethod
    def setUpClass(cls):
        import ttkbootstrap as ttk
        cls.root = ttk.Window(themename="darkly")
        cls.root.withdraw()
        cls.app = setup_mock_app(cls.root)

    @classmethod
    def tearDownClass(cls):
        cls.root.destroy()

    def test_apply_global_styles(self):
        from src.utils.styles import apply_global_styles
        apply_global_styles(self.app)

    def test_make_round_btn(self):
        from src.utils.styles import make_round_btn
        refs = []
        btn = make_round_btn(
            self.root, "Test", None,
            lambda: None, "info", refs,
        )
        self.assertIsNotNone(btn)
        self.assertTrue(hasattr(btn, "_base_style"))
        self.assertTrue(hasattr(btn, "_hover_style"))
        self.assertTrue(hasattr(btn, "_is_hovering"))
        btn.destroy()

    def test_make_round_btn_sizes(self):
        from src.utils.styles import make_round_btn
        for size in ["small", "normal", "large"]:
            btn = make_round_btn(
                self.root, "Test", None,
                lambda: None, "info", size=size,
            )
            self.assertIsNotNone(btn)
            btn.destroy()

    def test_make_icon_btn(self):
        from src.utils.styles import make_icon_btn
        from src.utils.icon_manager import IconManager
        mgr = IconManager()
        icon = mgr.get("file", 14)
        refs = [icon]

        btn = make_icon_btn(
            self.root, icon,
            lambda: None, "info", refs,
        )
        self.assertIsNotNone(btn)
        btn.destroy()

    def test_make_action_row(self):
        from src.utils.styles import make_action_row
        row = make_action_row(
            self.root, None, "Test",
            "Description", lambda: None, "info",
        )
        self.assertIsNotNone(row)
        row.destroy()

    def test_hover_state_tracking(self):
        from src.utils.styles import make_round_btn
        btn = make_round_btn(
            self.root, "Hover", None,
            lambda: None, "success",
        )
        self.assertFalse(btn._is_hovering)
        btn.event_generate("<Enter>")
        self.root.update()
        self.assertTrue(btn._is_hovering)
        btn.event_generate("<Leave>")
        self.root.update()
        self.assertFalse(btn._is_hovering)
        btn.destroy()


class TestGitInstaller(unittest.TestCase):
    """Test GitInstaller GUI-related methods."""

    @classmethod
    def setUpClass(cls):
        cls.root = tk.Tk()
        cls.root.withdraw()
        cls.app = setup_mock_app(cls.root)

    @classmethod
    def tearDownClass(cls):
        cls.root.destroy()

    def test_create_installer(self):
        from src.core.git_installer import GitInstaller
        gi = GitInstaller(self.app)
        self.assertIsNotNone(gi)

    def test_check_returns_bool(self):
        from src.core.git_installer import GitInstaller
        self.app.settings["suppress_git_prompt"] = True
        gi = GitInstaller(self.app)
        result = gi.check_and_prompt()
        self.assertIsInstance(result, bool)


class TestUpdaterGUI(unittest.TestCase):
    """Test Updater GUI methods."""

    @classmethod
    def setUpClass(cls):
        cls.root = tk.Tk()
        cls.root.withdraw()
        cls.app = setup_mock_app(cls.root)

    @classmethod
    def tearDownClass(cls):
        cls.root.destroy()

    def test_create_updater(self):
        from src.core.updater import Updater
        u = Updater(self.app)
        self.assertIsNotNone(u)
        self.assertFalse(u.checking)

    def test_show_uptodate(self):
        from src.core.updater import Updater
        u = Updater(self.app)
        # Just verify the method exists and doesn't crash on import
        self.assertTrue(hasattr(u, '_show_uptodate_dialog'))


if __name__ == "__main__":
    unittest.main()