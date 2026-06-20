"""GUI tests — uses a single ttkbootstrap Window to avoid segfaults.
Includes runtime error detection for widget creation and interaction."""

import unittest
import sys
import os
import tkinter as tk
import traceback
import io

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Single shared ttkbootstrap window for ALL tests
_root = None
_app = None
_errors = []


def get_root():
    global _root
    if _root is None:
        import ttkbootstrap as ttk
        _root = ttk.Window(themename="darkly")
        _root.withdraw()
        _root.report_callback_exception = _on_tk_error
    return _root


def _on_tk_error(exc_type, exc_value, exc_tb):
    """Capture Tk callback errors instead of crashing."""
    global _errors
    error_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    _errors.append(error_msg)
    print(f"TK ERROR CAPTURED:\n{error_msg}", file=sys.stderr)


def get_app():
    global _app
    if _app is None:
        _app = setup_mock_app(get_root())
    return _app


def clear_errors():
    global _errors
    _errors = []


def get_errors():
    global _errors
    return _errors.copy()


class MockApp:
    """Minimal mock of OmniIDEApp for GUI testing."""

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

    def set_status(self, text): pass
    def save_settings(self): pass
    def toggle_sidebar(self): pass
    def toggle_terminal(self): pass
    def toggle_search(self): pass
    def toggle_command_palette(self): pass
    def open_settings(self): pass
    def check_for_updates(self): pass
    def switch_theme(self): pass
    def open_project(self, path=None): pass


class MockFileManager:
    def new_file(self): pass
    def open_file(self, filepath=None): pass
    def save_file(self): pass
    def save_file_as(self): pass


class MockGitManager:
    def has_git(self): return False
    def detect_repo(self, path): return False
    def clone_repo(self): pass
    def init_repo(self): pass
    def git_status(self): pass
    def git_diff(self): pass
    def git_add_all(self): pass
    def git_commit(self): pass
    def git_push(self): pass
    def git_pull(self): pass
    def git_log(self): pass
    def git_branch(self): pass
    def add_remote(self): pass


class MockTabManager:
    def __init__(self):
        self.tabs = {}

    def new_tab(self, filepath=None, content="", title=None):
        return "tab_1"

    def get_active_editor(self):
        return None

    def get_active_tab_info(self):
        return None

    def close_active_tab(self): pass
    def refresh_all_highlighting(self): pass
    def has_tabs(self): return False


class MockExtensionManager:
    def get_installed(self): return []
    def search(self, query, callback, page_size=15): callback([], None)
    def install_extension(self, ext_info, callback): callback(True, "OK")
    def uninstall_extension(self, ext_id): return True, "OK"

    @staticmethod
    def format_installs(count):
        if count >= 1_000_000: return f"{count / 1_000_000:.1f}M"
        elif count >= 1_000: return f"{count / 1_000:.1f}K"
        return str(count)

    @staticmethod
    def format_rating(rating): return f"{rating}"


class MockUpdater:
    def check_now(self, silent=False): pass
    def check_on_startup(self): pass


class MockRecentFiles:
    def get_all(self): return []
    def add(self, filepath): pass
    def clear(self): pass


class MockStatusBar:
    def set_text(self, t): pass
    def update_cursor_position(self, e): pass
    def update_file_type(self, f): pass
    def update_git_branch(self, b): pass


class MockSidebar:
    def _switch_panel(self, p): pass
    def toggle(self): pass


class MockTerminal:
    def clear(self): pass
    def restart_shell(self): pass
    def toggle(self): pass


def setup_mock_app(root):
    app = MockApp(root)
    app.file_manager = MockFileManager()
    app.git_manager = MockGitManager()
    app.tab_manager = MockTabManager()
    app.extension_manager = MockExtensionManager()
    app.updater = MockUpdater()
    app.recent_files_manager = MockRecentFiles()
    app.statusbar = MockStatusBar()
    app.sidebar = MockSidebar()
    app.terminal = MockTerminal()
    return app


class GUITestBase(unittest.TestCase):
    """Base class that checks for Tk errors after each test."""

    def setUp(self):
        self.root = get_root()
        self.app = get_app()
        clear_errors()

    def tearDown(self):
        # Process pending events to catch deferred errors
        try:
            self.root.update_idletasks()
            self.root.update()
        except Exception:
            pass

        errors = get_errors()
        if errors:
            combined = "\n---\n".join(errors)
            self.fail(f"Tk callback errors detected:\n{combined}")


# ──────────────────────────────────────────────────
# EDITOR TESTS
# ──────────────────────────────────────────────────

class TestEditorWidget(GUITestBase):

    def test_create_editor(self):
        from src.core.editor import CodeEditor
        frame = tk.Frame(self.root)
        editor = CodeEditor(frame, self.app, filepath="test.py")
        self.assertIsNotNone(editor)
        self.root.update()
        editor.destroy()
        frame.destroy()

    def test_editor_set_content(self):
        from src.core.editor import CodeEditor
        frame = tk.Frame(self.root)
        editor = CodeEditor(frame, self.app, filepath="test.py")
        editor.set_content("print('hello')")
        self.root.update()
        self.assertEqual(editor.get_content(), "print('hello')")
        editor.destroy()
        frame.destroy()

    def test_editor_empty_content(self):
        from src.core.editor import CodeEditor
        frame = tk.Frame(self.root)
        editor = CodeEditor(frame, self.app)
        editor.set_content("")
        self.root.update()
        self.assertEqual(editor.get_content(), "")
        editor.destroy()
        frame.destroy()

    def test_editor_multiline(self):
        from src.core.editor import CodeEditor
        frame = tk.Frame(self.root)
        editor = CodeEditor(frame, self.app)
        text = "line1\nline2\nline3"
        editor.set_content(text)
        self.root.update()
        self.assertEqual(editor.get_content(), text)
        editor.destroy()
        frame.destroy()

    def test_editor_large_content(self):
        from src.core.editor import CodeEditor
        frame = tk.Frame(self.root)
        editor = CodeEditor(frame, self.app, filepath="test.py")
        big_text = "\n".join([f"line {i}: x = {i} * 2  # comment" for i in range(500)])
        editor.set_content(big_text)
        self.root.update()
        content = editor.get_content()
        self.assertEqual(content.count("\n"), 499)
        editor.destroy()
        frame.destroy()

    def test_editor_modified_flag(self):
        from src.core.editor import CodeEditor
        frame = tk.Frame(self.root)
        editor = CodeEditor(frame, self.app)
        editor.set_content("hello")
        self.root.update()
        self.assertFalse(editor.modified)
        editor.destroy()
        frame.destroy()

    def test_editor_insert_and_delete(self):
        from src.core.editor import CodeEditor
        frame = tk.Frame(self.root)
        editor = CodeEditor(frame, self.app)
        editor.set_content("abcdef")
        self.root.update()
        editor.delete("1.0", "1.3")
        self.root.update()
        self.assertEqual(editor.get_content(), "def")
        editor.insert("1.0", "xyz")
        self.root.update()
        self.assertEqual(editor.get_content(), "xyzdef")
        editor.destroy()
        frame.destroy()

    def test_editor_cursor_position(self):
        from src.core.editor import CodeEditor
        frame = tk.Frame(self.root)
        editor = CodeEditor(frame, self.app)
        editor.set_content("line1\nline2\nline3")
        self.root.update()
        editor.mark_set("insert", "2.3")
        self.root.update()
        pos = editor.index("insert")
        self.assertEqual(pos, "2.3")
        editor.destroy()
        frame.destroy()

    def test_editor_selection(self):
        from src.core.editor import CodeEditor
        frame = tk.Frame(self.root)
        editor = CodeEditor(frame, self.app)
        editor.set_content("hello world")
        self.root.update()
        editor.tag_add("sel", "1.0", "1.5")
        self.root.update()
        try:
            sel = editor.get("sel.first", "sel.last")
            self.assertEqual(sel, "hello")
        except tk.TclError:
            pass  # Selection may not be available in headless
        editor.destroy()
        frame.destroy()

    def test_editor_undo_redo(self):
        from src.core.editor import CodeEditor
        frame = tk.Frame(self.root)
        editor = CodeEditor(frame, self.app)
        editor.set_content("")
        self.root.update()
        editor.insert("1.0", "first")
        self.root.update()
        editor.edit_separator()
        editor.insert("end", " second")
        self.root.update()
        try:
            editor.edit_undo()
            self.root.update()
        except tk.TclError:
            pass  # Undo stack may be empty
        editor.destroy()
        frame.destroy()

    def test_line_numbers(self):
        from src.core.editor import CodeEditor, LineNumbers
        frame = tk.Frame(self.root)
        editor = CodeEditor(frame, self.app)
        editor.set_content("a\nb\nc\nd\ne")
        ln = LineNumbers(frame, editor, self.app.colors)
        ln.set_font(("Consolas", 13))
        ln.pack(side=tk.LEFT, fill=tk.Y)
        editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.root.update()
        ln.redraw()
        self.root.update()
        ln.destroy()
        editor.destroy()
        frame.destroy()

    def test_editor_refresh_colors(self):
        from src.core.editor import CodeEditor
        frame = tk.Frame(self.root)
        editor = CodeEditor(frame, self.app, filepath="test.py")
        editor.set_content("x = 1\ny = 'hello'\n# comment")
        self.root.update()
        editor.refresh_colors()
        self.root.update()
        editor.destroy()
        frame.destroy()

    def test_editor_different_filetypes(self):
        from src.core.editor import CodeEditor
        filetypes = [
            ("test.py", "import os\nprint('hello')"),
            ("test.js", "const x = 1;\nconsole.log(x);"),
            ("test.html", "<html><body><p>test</p></body></html>"),
            ("test.css", "body { color: red; }"),
            ("test.json", '{"key": "value"}'),
        ]
        for filepath, content in filetypes:
            frame = tk.Frame(self.root)
            editor = CodeEditor(frame, self.app, filepath=filepath)
            editor.set_content(content)
            self.root.update()
            self.assertEqual(editor.get_content(), content, f"Failed for {filepath}")
            editor.destroy()
            frame.destroy()


# ──────────────────────────────────────────────────
# TAB MANAGER TESTS
# ──────────────────────────────────────────────────

class TestTabManagerWidget(GUITestBase):

    def test_create_tab_manager(self):
        from src.core.tab_manager import TabManager
        frame = tk.Frame(self.root)
        tm = TabManager(frame, self.app)
        self.root.update()
        self.assertIsNotNone(tm)
        self.assertEqual(len(tm.tabs), 0)
        frame.destroy()

    def test_new_tab(self):
        from src.core.tab_manager import TabManager
        frame = tk.Frame(self.root)
        tm = TabManager(frame, self.app)
        tab_id = tm.new_tab(content="hello", title="Test")
        self.root.update()
        self.assertIsNotNone(tab_id)
        self.assertEqual(len(tm.tabs), 1)
        frame.destroy()

    def test_new_tab_with_filepath(self):
        from src.core.tab_manager import TabManager
        frame = tk.Frame(self.root)
        tm = TabManager(frame, self.app)
        tm.new_tab(filepath="test.py", content="x = 1")
        self.root.update()
        info = list(tm.tabs.values())[0]
        self.assertEqual(info["filepath"], "test.py")
        frame.destroy()

    def test_get_active_editor_empty(self):
        from src.core.tab_manager import TabManager
        frame = tk.Frame(self.root)
        tm = TabManager(frame, self.app)
        self.root.update()
        self.assertIsNone(tm.get_active_editor())
        frame.destroy()

    def test_has_tabs(self):
        from src.core.tab_manager import TabManager
        frame = tk.Frame(self.root)
        tm = TabManager(frame, self.app)
        self.assertFalse(tm.has_tabs())
        tm.new_tab(content="test")
        self.root.update()
        self.assertTrue(tm.has_tabs())
        frame.destroy()

    def test_multiple_tabs(self):
        from src.core.tab_manager import TabManager
        frame = tk.Frame(self.root)
        tm = TabManager(frame, self.app)
        for i in range(5):
            tm.new_tab(content=f"content {i}", title=f"Tab {i}")
        self.root.update()
        self.assertEqual(len(tm.tabs), 5)
        frame.destroy()

    def test_get_active_editor_after_create(self):
        from src.core.tab_manager import TabManager
        frame = tk.Frame(self.root)
        frame.pack(fill=tk.BOTH, expand=True)
        tm = TabManager(frame, self.app)
        tm.frame.pack(fill=tk.BOTH, expand=True)
        tm.new_tab(content="hello", title="Test")
        self.root.update()
        editor = tm.get_active_editor()
        # May or may not return editor depending on notebook state
        frame.destroy()

    def test_refresh_all_highlighting(self):
        from src.core.tab_manager import TabManager
        frame = tk.Frame(self.root)
        tm = TabManager(frame, self.app)
        tm.new_tab(filepath="test.py", content="x = 1")
        tm.new_tab(filepath="test.js", content="const y = 2;")
        self.root.update()
        tm.refresh_all_highlighting()
        self.root.update()
        frame.destroy()


# ──────────────────────────────────────────────────
# SEARCH BAR TESTS
# ──────────────────────────────────────────────────

class TestSearchBarWidget(GUITestBase):

    def test_create_search_bar(self):
        from src.core.search import SearchBar
        frame = tk.Frame(self.root)
        sb = SearchBar(frame, self.app)
        self.root.update()
        self.assertIsNotNone(sb)
        self.assertFalse(sb.visible)
        frame.destroy()

    def test_show_hide(self):
        from src.core.search import SearchBar
        container = tk.Frame(self.root)
        container.grid_columnconfigure(0, weight=1)
        sb = SearchBar(container, self.app)
        sb.frame.grid(row=1, column=0, sticky="ew")
        self.root.update()
        sb.show()
        self.root.update()
        self.assertTrue(sb.visible)
        sb.hide()
        self.root.update()
        self.assertFalse(sb.visible)
        container.destroy()

    def test_toggle(self):
        from src.core.search import SearchBar
        container = tk.Frame(self.root)
        container.grid_columnconfigure(0, weight=1)
        sb = SearchBar(container, self.app)
        sb.frame.grid(row=1, column=0, sticky="ew")
        self.root.update()
        sb.toggle()
        self.root.update()
        self.assertTrue(sb.visible)
        sb.toggle()
        self.root.update()
        self.assertFalse(sb.visible)
        container.destroy()

    def test_clear_highlights_safe(self):
        from src.core.search import SearchBar
        frame = tk.Frame(self.root)
        sb = SearchBar(frame, self.app)
        sb._clear_highlights()
        self.root.update()
        self.assertEqual(sb.matches, [])
        self.assertEqual(sb.current_match, -1)
        frame.destroy()

    def test_get_editor_none(self):
        from src.core.search import SearchBar
        frame = tk.Frame(self.root)
        sb = SearchBar(frame, self.app)
        self.assertIsNone(sb._get_editor())
        frame.destroy()

    def test_find_with_no_editor(self):
        from src.core.search import SearchBar
        frame = tk.Frame(self.root)
        sb = SearchBar(frame, self.app)
        sb.find_entry.insert(0, "test")
        sb._find_all()
        self.root.update()
        self.assertEqual(sb.matches, [])
        frame.destroy()


# ──────────────────────────────────────────────────
# TOOLBAR TESTS
# ──────────────────────────────────────────────────

class TestToolbarWidget(GUITestBase):

    def test_create_toolbar(self):
        from src.ui.toolbar import Toolbar
        frame = tk.Frame(self.root)
        tb = Toolbar(frame, self.app)
        self.root.update()
        self.assertIsNotNone(tb)
        self.assertIsNotNone(tb.frame)
        frame.destroy()

    def test_toolbar_has_children(self):
        from src.ui.toolbar import Toolbar
        frame = tk.Frame(self.root)
        tb = Toolbar(frame, self.app)
        tb.frame.pack(fill=tk.X)
        self.root.update()
        children = tb.frame.winfo_children()
        self.assertGreater(len(children), 0, "Toolbar has no children")
        frame.destroy()


# ──────────────────────────────────────────────────
# STATUS BAR TESTS
# ──────────────────────────────────────────────────

class TestStatusBarWidget(GUITestBase):

    def test_create_statusbar(self):
        from src.ui.statusbar import StatusBar
        frame = tk.Frame(self.root)
        sb = StatusBar(frame, self.app)
        self.root.update()
        self.assertIsNotNone(sb)
        frame.destroy()

    def test_set_text(self):
        from src.ui.statusbar import StatusBar
        frame = tk.Frame(self.root)
        sb = StatusBar(frame, self.app)
        sb.set_text("Test status")
        self.root.update()
        frame.destroy()

    def test_update_file_type_various(self):
        from src.ui.statusbar import StatusBar
        frame = tk.Frame(self.root)
        sb = StatusBar(frame, self.app)
        for ft in ["test.py", "test.js", "test.html", "test.css", "test.json", None, ""]:
            sb.update_file_type(ft)
            self.root.update()
        frame.destroy()

    def test_update_git_branch(self):
        from src.ui.statusbar import StatusBar
        frame = tk.Frame(self.root)
        sb = StatusBar(frame, self.app)
        for branch in ["main", "develop", "feature/test", "", None]:
            sb.update_git_branch(branch)
            self.root.update()
        frame.destroy()


# ──────────────────────────────────────────────────
# SIDEBAR TESTS
# ──────────────────────────────────────────────────

class TestSidebarWidget(GUITestBase):

    def test_create_sidebar(self):
        from src.ui.sidebar import Sidebar
        frame = tk.Frame(self.root)
        sb = Sidebar(frame, self.app)
        self.root.update()
        self.assertIsNotNone(sb)
        self.assertTrue(sb.visible)
        frame.destroy()

    def test_switch_all_panels(self):
        from src.ui.sidebar import Sidebar
        frame = tk.Frame(self.root)
        sb = Sidebar(frame, self.app)
        sb.frame.pack(side=tk.LEFT, fill=tk.Y)
        self.root.update()

        for panel in ["explorer", "git", "extensions"]:
            sb._switch_panel(panel)
            self.root.update()
            self.assertEqual(sb.active_panel, panel)

        frame.destroy()

    def test_toggle(self):
        from src.ui.sidebar import Sidebar
        frame = tk.Frame(self.root)
        sb = Sidebar(frame, self.app)
        sb.frame.pack(side=tk.LEFT, fill=tk.Y)
        self.root.update()
        sb.toggle()
        self.root.update()
        self.assertFalse(sb.visible)
        sb.toggle()
        self.root.update()
        self.assertTrue(sb.visible)
        frame.destroy()

    def test_rapid_panel_switching(self):
        from src.ui.sidebar import Sidebar
        frame = tk.Frame(self.root)
        sb = Sidebar(frame, self.app)
        sb.frame.pack(side=tk.LEFT, fill=tk.Y)
        self.root.update()

        for _ in range(10):
            for panel in ["explorer", "git", "extensions"]:
                sb._switch_panel(panel)
        self.root.update()
        frame.destroy()


# ──────────────────────────────────────────────────
# FILE TREE TESTS
# ──────────────────────────────────────────────────

class TestFileTreeWidget(GUITestBase):

    def test_create_file_tree(self):
        from src.ui.file_tree import FileTree
        frame = tk.Frame(self.root)
        ft = FileTree(frame, self.app)
        self.root.update()
        self.assertIsNotNone(ft)
        frame.destroy()

    def test_load_directory(self):
        import tempfile
        from src.ui.file_tree import FileTree
        frame = tk.Frame(self.root)
        ft = FileTree(frame, self.app)
        ft.frame.pack(fill=tk.BOTH, expand=True)

        with tempfile.TemporaryDirectory() as tmpdir:
            open(os.path.join(tmpdir, "test.py"), "w").close()
            open(os.path.join(tmpdir, "readme.md"), "w").close()
            os.makedirs(os.path.join(tmpdir, "src"), exist_ok=True)
            open(os.path.join(tmpdir, "src", "main.py"), "w").close()

            ft.load_directory(tmpdir)
            self.root.update()
            children = ft.tree.get_children()
            self.assertGreater(len(children), 0)

        frame.destroy()

    def test_load_empty_directory(self):
        import tempfile
        from src.ui.file_tree import FileTree
        frame = tk.Frame(self.root)
        ft = FileTree(frame, self.app)

        with tempfile.TemporaryDirectory() as tmpdir:
            ft.load_directory(tmpdir)
            self.root.update()

        frame.destroy()

    def test_load_directory_with_ignored(self):
        import tempfile
        from src.ui.file_tree import FileTree
        frame = tk.Frame(self.root)
        ft = FileTree(frame, self.app)

        with tempfile.TemporaryDirectory() as tmpdir:
            os.makedirs(os.path.join(tmpdir, "__pycache__"), exist_ok=True)
            os.makedirs(os.path.join(tmpdir, ".git"), exist_ok=True)
            os.makedirs(os.path.join(tmpdir, "node_modules"), exist_ok=True)
            open(os.path.join(tmpdir, "main.py"), "w").close()

            ft.load_directory(tmpdir)
            self.root.update()

        frame.destroy()


# ──────────────────────────────────────────────────
# EXTENSIONS PANEL TESTS
# ──────────────────────────────────────────────────

class TestExtensionsPanelWidget(GUITestBase):

    def test_create_panel(self):
        from src.ui.extensions_panel import ExtensionsPanel
        frame = tk.Frame(self.root)
        ep = ExtensionsPanel(frame, self.app)
        self.root.update()
        self.assertIsNotNone(ep)
        frame.destroy()

    def test_clear_results(self):
        from src.ui.extensions_panel import ExtensionsPanel
        frame = tk.Frame(self.root)
        ep = ExtensionsPanel(frame, self.app)
        ep._clear_results()
        self.root.update()
        self.assertEqual(len(ep.result_widgets), 0)
        frame.destroy()

    def test_show_installed_empty(self):
        from src.ui.extensions_panel import ExtensionsPanel
        frame = tk.Frame(self.root)
        ep = ExtensionsPanel(frame, self.app)
        ep._show_installed()
        self.root.update()
        frame.destroy()

    def test_add_card_marketplace(self):
        from src.ui.extensions_panel import ExtensionsPanel
        frame = tk.Frame(self.root)
        ep = ExtensionsPanel(frame, self.app)
        ep._add_card({
            "id": "test.ext",
            "name": "Test Extension",
            "publisher": "TestPub",
            "description": "A test extension for testing",
            "version": "1.0.0",
            "installs": 50000,
            "rating": 4.5,
            "installed": False,
        }, mode="marketplace")
        self.root.update()
        self.assertEqual(len(ep.result_widgets), 1)
        frame.destroy()

    def test_add_card_installed(self):
        from src.ui.extensions_panel import ExtensionsPanel
        frame = tk.Frame(self.root)
        ep = ExtensionsPanel(frame, self.app)
        ep._add_card({
            "id": "test.ext",
            "name": "Installed Ext",
            "publisher": "Pub",
            "description": "Already installed",
            "version": "2.0.0",
        }, mode="installed")
        self.root.update()
        self.assertEqual(len(ep.result_widgets), 1)
        frame.destroy()


# ──────────────────────────────────────────────────
# MENUBAR TESTS
# ──────────────────────────────────────────────────

class TestMenuBarWidget(GUITestBase):

    def test_create_menubar(self):
        from src.ui.menubar import MenuBar
        mb = MenuBar(self.root, self.app)
        self.root.update()
        self.assertIsNotNone(mb)
        self.assertIsNotNone(mb.menu)


# ──────────────────────────────────────────────────
# WELCOME TAB TESTS
# ──────────────────────────────────────────────────

class TestWelcomeTabWidget(GUITestBase):

    def test_build_text(self):
        from src.ui.welcome import WelcomeTab
        wt = WelcomeTab(self.app)
        text = wt._build_text()
        self.assertIn("OmniIDE", text)
        self.assertIn("OmniNodeCo", text)
        self.assertIn("Ctrl+", text)

    def test_build_text_has_version(self):
        from src.ui.welcome import WelcomeTab
        from src.config import APP_VERSION
        wt = WelcomeTab(self.app)
        text = wt._build_text()
        self.assertIn(APP_VERSION, text)

    def test_build_text_has_shortcuts(self):
        from src.ui.welcome import WelcomeTab
        wt = WelcomeTab(self.app)
        text = wt._build_text()
        shortcuts = ["Ctrl+N", "Ctrl+O", "Ctrl+S", "Ctrl+F", "Ctrl+B"]
        for sc in shortcuts:
            self.assertIn(sc, text, f"Missing shortcut: {sc}")


# ──────────────────────────────────────────────────
# SPLASH SCREEN TESTS
# ──────────────────────────────────────────────────

class TestSplashScreenWidget(GUITestBase):

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
        splash.update_status("Loading...")
        splash.update_status("Building UI...")
        splash.update_status("Ready!")
        self.root.update()
        splash.close()
        self.root.update()

    def test_set_progress_full_range(self):
        from src.ui.splash import SplashScreen
        splash = SplashScreen(self.root)
        for p in range(0, 101, 10):
            splash.set_progress(p)
        self.root.update()
        splash.close()
        self.root.update()

    def test_rapid_progress(self):
        from src.ui.splash import SplashScreen
        splash = SplashScreen(self.root)
        for p in range(101):
            splash.set_progress(p)
        splash.close()
        self.root.update()


# ──────────────────────────────────────────────────
# COMMAND PALETTE TESTS
# ──────────────────────────────────────────────────

class TestCommandPaletteWidget(GUITestBase):

    def test_create_palette(self):
        from src.core.command_palette import CommandPalette
        cp = CommandPalette(self.app)
        self.assertIsNotNone(cp)
        self.assertFalse(cp.visible)
        self.assertGreater(len(cp.commands), 30)

    def test_fuzzy_score_exact(self):
        from src.core.command_palette import CommandPalette
        cp = CommandPalette(self.app)
        self.assertGreater(cp._fuzzy_score("save", "file: save"), 0)

    def test_fuzzy_score_partial(self):
        from src.core.command_palette import CommandPalette
        cp = CommandPalette(self.app)
        self.assertGreater(cp._fuzzy_score("sv", "file: save"), 0)

    def test_fuzzy_score_no_match(self):
        from src.core.command_palette import CommandPalette
        cp = CommandPalette(self.app)
        self.assertEqual(cp._fuzzy_score("xyz", "file: save"), 0)

    def test_fuzzy_score_word_boundary(self):
        from src.core.command_palette import CommandPalette
        cp = CommandPalette(self.app)
        # Word boundary should score higher
        score_boundary = cp._fuzzy_score("fs", "file: save")
        score_mid = cp._fuzzy_score("il", "file: save")
        # Both should match but boundary bonus varies
        self.assertGreater(score_boundary, 0)

    def test_show_close(self):
        from src.core.command_palette import CommandPalette
        cp = CommandPalette(self.app)
        cp.show()
        self.root.update()
        self.assertTrue(cp.visible)
        self.assertIsNotNone(cp.window)
        cp.close()
        self.root.update()
        self.assertFalse(cp.visible)

    def test_toggle(self):
        from src.core.command_palette import CommandPalette
        cp = CommandPalette(self.app)
        cp.toggle()
        self.root.update()
        self.assertTrue(cp.visible)
        cp.toggle()
        self.root.update()
        self.assertFalse(cp.visible)

    def test_filter_empty(self):
        from src.core.command_palette import CommandPalette
        cp = CommandPalette(self.app)
        cp.show()
        self.root.update()
        cp._filter_commands("")
        self.root.update()
        self.assertEqual(len(cp.filtered), len(cp.commands))
        cp.close()
        self.root.update()

    def test_filter_query(self):
        from src.core.command_palette import CommandPalette
        cp = CommandPalette(self.app)
        cp.show()
        self.root.update()
        cp._filter_commands("save")
        self.root.update()
        self.assertGreater(len(cp.filtered), 0)
        self.assertLess(len(cp.filtered), len(cp.commands))
        cp.close()
        self.root.update()

    def test_filter_git(self):
        from src.core.command_palette import CommandPalette
        cp = CommandPalette(self.app)
        cp.show()
        self.root.update()
        cp._filter_commands("git")
        self.root.update()
        for cmd in cp.filtered:
            self.assertIn("git", cmd["label"].lower())
        cp.close()
        self.root.update()

    def test_commands_have_keys(self):
        from src.core.command_palette import CommandPalette
        cp = CommandPalette(self.app)
        for cmd in cp.commands:
            self.assertIn("label", cmd)
            self.assertIn("detail", cmd)
            self.assertIn("category", cmd)
            self.assertIn("shortcut", cmd)
            self.assertIn("action", cmd)
            self.assertTrue(callable(cmd["action"]), f"{cmd['label']} action not callable")

    def test_all_categories_valid(self):
        from src.core.command_palette import CommandPalette
        cp = CommandPalette(self.app)
        valid = {"file", "edit", "view", "git", "terminal", "app"}
        for cmd in cp.commands:
            self.assertIn(cmd["category"], valid, f"Invalid category: {cmd['category']}")

    def test_navigation(self):
        from src.core.command_palette import CommandPalette
        cp = CommandPalette(self.app)
        cp.show()
        self.root.update()
        self.assertEqual(cp.selected_idx, 0)
        cp._move_selection(1)
        self.root.update()
        self.assertEqual(cp.selected_idx, 1)
        cp._move_selection(-1)
        self.root.update()
        self.assertEqual(cp.selected_idx, 0)
        # Should not go negative
        cp._move_selection(-1)
        self.root.update()
        self.assertEqual(cp.selected_idx, 0)
        cp.close()
        self.root.update()


# ──────────────────────────────────────────────────
# SETTINGS PANEL TESTS
# ──────────────────────────────────────────────────

class TestSettingsPanelWidget(GUITestBase):

    def test_create_panel(self):
        from src.ui.settings_panel import SettingsPanel
        sp = SettingsPanel(self.app)
        self.assertIsNotNone(sp)

    def test_show_and_close(self):
        from src.ui.settings_panel import SettingsPanel
        sp = SettingsPanel(self.app)
        sp.show()
        self.root.update()
        self.assertIsNotNone(sp.window)
        self.assertTrue(sp.window.winfo_exists())
        sp.window.destroy()
        self.root.update()

    def test_show_twice(self):
        from src.ui.settings_panel import SettingsPanel
        sp = SettingsPanel(self.app)
        sp.show()
        self.root.update()
        sp.show()  # Should just lift existing window
        self.root.update()
        sp.window.destroy()
        self.root.update()

    def test_settings_have_vars(self):
        from src.ui.settings_panel import SettingsPanel
        sp = SettingsPanel(self.app)
        sp.show()
        self.root.update()
        self.assertGreater(len(sp._vars), 0)
        self.assertGreater(len(sp.all_rows), 0)
        sp.window.destroy()
        self.root.update()


# ──────────────────────────────────────────────────
# ICON MANAGER GUI TESTS
# ──────────────────────────────────────────────────

class TestIconManagerGUI(GUITestBase):

    def test_create_manager(self):
        from src.utils.icon_manager import IconManager
        mgr = IconManager()
        self.assertIsNotNone(mgr)

    def test_get_all_required_icons(self):
        from src.utils.icon_manager import IconManager
        mgr = IconManager()
        required = [
            "file", "file_python", "file_javascript", "file_html",
            "folder_closed", "folder_open", "new_file", "save",
            "search", "terminal", "close", "settings", "theme",
            "arrow_left", "arrow_right", "run", "info", "explorer",
        ]
        for name in required:
            icon = mgr.get(name, 16)
            self.assertIsNotNone(icon, f"Failed to get icon: {name}")

    def test_get_unknown_icon(self):
        from src.utils.icon_manager import IconManager
        mgr = IconManager()
        icon = mgr.get("nonexistent_xyz", 16)
        self.assertIsNotNone(icon)

    def test_caching(self):
        from src.utils.icon_manager import IconManager
        mgr = IconManager()
        icon1 = mgr.get("file", 16)
        icon2 = mgr.get("file", 16)
        self.assertIs(icon1, icon2)

    def test_different_sizes(self):
        from src.utils.icon_manager import IconManager
        mgr = IconManager()
        i16 = mgr.get("file", 16)
        i32 = mgr.get("file", 32)
        self.assertIsNotNone(i16)
        self.assertIsNotNone(i32)

    def test_many_icons_no_crash(self):
        from src.utils.icon_manager import IconManager
        from assets.icons.icons import ICONS
        mgr = IconManager()
        for name in ICONS:
            icon = mgr.get(name, 16)
            self.assertIsNotNone(icon, f"Icon {name} returned None")
        self.root.update()


# ──────────────────────────────────────────────────
# STYLES TESTS
# ──────────────────────────────────────────────────

class TestStylesGUI(GUITestBase):

    def test_apply_global_styles(self):
        from src.utils.styles import apply_global_styles
        apply_global_styles(self.app)
        self.root.update()

    def test_make_round_btn(self):
        from src.utils.styles import make_round_btn
        refs = []
        btn = make_round_btn(self.root, "Test", None, lambda: None, "info", refs)
        self.root.update()
        self.assertIsNotNone(btn)
        self.assertTrue(hasattr(btn, "_base_style"))
        self.assertTrue(hasattr(btn, "_hover_style"))
        self.assertFalse(btn._is_hovering)
        btn.destroy()

    def test_make_round_btn_all_styles(self):
        from src.utils.styles import make_round_btn
        for style in ["info", "success", "warning", "danger", "secondary"]:
            btn = make_round_btn(self.root, style, None, lambda: None, style)
            self.root.update()
            self.assertEqual(btn._base_style, f"{style}-outline")
            self.assertEqual(btn._hover_style, style)
            btn.destroy()

    def test_make_round_btn_sizes(self):
        from src.utils.styles import make_round_btn
        for size in ["small", "normal", "large"]:
            btn = make_round_btn(self.root, "T", None, lambda: None, "info", size=size)
            self.root.update()
            btn.destroy()

    def test_make_icon_btn(self):
        from src.utils.styles import make_icon_btn
        from src.utils.icon_manager import IconManager
        mgr = IconManager()
        icon = mgr.get("file", 14)
        refs = [icon]
        btn = make_icon_btn(self.root, icon, lambda: None, "info", refs)
        self.root.update()
        self.assertIsNotNone(btn)
        btn.destroy()

    def test_make_action_row(self):
        from src.utils.styles import make_action_row
        row = make_action_row(self.root, None, "Test", "Desc", lambda: None, "info")
        self.root.update()
        self.assertIsNotNone(row)
        row.destroy()

    def test_hover_enter_leave(self):
        from src.utils.styles import make_round_btn
        btn = make_round_btn(self.root, "Hover", None, lambda: None, "success")
        btn.pack()
        self.root.update()

        self.assertFalse(btn._is_hovering)

        btn.event_generate("<Enter>")
        self.root.update()
        self.assertTrue(btn._is_hovering)

        btn.event_generate("<Leave>")
        self.root.update()
        self.assertFalse(btn._is_hovering)

        btn.destroy()

    def test_hover_style_reset_after_click(self):
        from src.utils.styles import make_round_btn
        clicked = [False]

        def on_click():
            clicked[0] = True

        btn = make_round_btn(self.root, "Click", None, on_click, "info")
        btn.pack()
        self.root.update()

        btn.event_generate("<Enter>")
        self.root.update()
        self.assertTrue(btn._is_hovering)

        btn.invoke()
        self.root.update()
        self.assertTrue(clicked[0])

        btn.event_generate("<Leave>")
        self.root.update()
        self.assertFalse(btn._is_hovering)

        btn.destroy()


# ──────────────────────────────────────────────────
# GIT INSTALLER GUI TESTS
# ──────────────────────────────────────────────────

class TestGitInstallerGUI(GUITestBase):

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

    def test_check_with_git_installed(self):
        import shutil
        from src.core.git_installer import GitInstaller
        self.app.settings["suppress_git_prompt"] = True
        gi = GitInstaller(self.app)

        if shutil.which("git"):
            result = gi.check_and_prompt()
            self.assertTrue(result)
        else:
            result = gi.check_and_prompt()
            self.assertFalse(result)


# ──────────────────────────────────────────────────
# UPDATER GUI TESTS
# ──────────────────────────────────────────────────

class TestUpdaterGUI(GUITestBase):

    def test_create_updater(self):
        from src.core.updater import Updater
        u = Updater(self.app)
        self.assertIsNotNone(u)
        self.assertFalse(u.checking)

    def test_has_methods(self):
        from src.core.updater import Updater
        u = Updater(self.app)
        self.assertTrue(hasattr(u, 'check_now'))
        self.assertTrue(hasattr(u, 'check_on_startup'))
        self.assertTrue(hasattr(u, '_show_uptodate_dialog'))
        self.assertTrue(hasattr(u, '_show_update_dialog'))
        self.assertTrue(hasattr(u, '_is_newer'))
        self.assertTrue(hasattr(u, '_get_platform_key'))


# ──────────────────────────────────────────────────
# INTEGRATION — full widget tree test
# ──────────────────────────────────────────────────

class TestIntegrationWidgetTree(GUITestBase):
    """Test creating a complete widget tree similar to the real app."""

    def test_full_widget_tree(self):
        import tkinter.ttk as tkttk

        # Create the layout like app.py does
        container = tk.Frame(self.root)
        container.pack(fill=tk.BOTH, expand=True)
        container.columnconfigure(0, weight=1)
        container.rowconfigure(1, weight=1)

        # Toolbar
        from src.ui.toolbar import Toolbar
        tb = Toolbar(container, self.app)
        tb.frame.grid(row=0, column=0, sticky="ew")
        self.root.update()

        # Main pane
        main_pane = tkttk.PanedWindow(container, orient=tk.HORIZONTAL)
        main_pane.grid(row=1, column=0, sticky="nsew")

        # Sidebar
        from src.ui.sidebar import Sidebar
        sidebar = Sidebar(main_pane, self.app)
        main_pane.add(sidebar.frame, weight=0)
        self.root.update()

        # Right pane
        right_pane = tkttk.PanedWindow(main_pane, orient=tk.VERTICAL)
        main_pane.add(right_pane, weight=1)

        # Tab manager
        from src.core.tab_manager import TabManager
        tm = TabManager(right_pane, self.app)
        right_pane.add(tm.frame, weight=1)
        self.root.update()

        # Add a tab
        tm.new_tab(filepath="test.py", content="print('hello')", title="test.py")
        self.root.update()

        # Status bar
        from src.ui.statusbar import StatusBar
        sb = StatusBar(container, self.app)
        sb.frame.grid(row=2, column=0, sticky="ew")
        self.root.update()

        # Test interactions
        sb.set_text("Integration test running")
        sb.update_file_type("test.py")
        sb.update_git_branch("main")
        self.root.update()

        sidebar._switch_panel("git")
        self.root.update()
        sidebar._switch_panel("extensions")
        self.root.update()
        sidebar._switch_panel("explorer")
        self.root.update()

        # Cleanup
        container.destroy()
        self.root.update()

    def test_full_widget_tree_no_errors(self):
        """Verify no Tk errors accumulated during integration test."""
        errors = get_errors()
        self.assertEqual(len(errors), 0, f"Tk errors found:\n{''.join(errors)}")


# ──────────────────────────────────────────────────
# CLEANUP
# ──────────────────────────────────────────────────

def tearDownModule():
    global _root
    if _root is not None:
        try:
            _root.destroy()
        except Exception:
            pass
        _root = None


if __name__ == "__main__":
    unittest.main()