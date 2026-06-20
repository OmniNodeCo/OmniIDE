"""Tests for configuration module."""

import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestConfig(unittest.TestCase):

    def test_version(self):
        from src.config import APP_VERSION
        parts = APP_VERSION.split(".")
        self.assertEqual(len(parts), 3)
        for p in parts:
            self.assertTrue(p.isdigit())

    def test_app_name(self):
        from src.config import APP_NAME
        self.assertEqual(APP_NAME, "OmniIDE")

    def test_app_author(self):
        from src.config import APP_AUTHOR
        self.assertEqual(APP_AUTHOR, "OmniNodeCo")

    def test_default_settings_keys(self):
        from src.config import DEFAULT_SETTINGS
        required = [
            "theme", "font_family", "font_size", "tab_size",
            "show_line_numbers", "word_wrap", "auto_indent",
            "auto_save", "auto_check_updates", "window_width",
            "window_height", "sidebar_width", "terminal_height",
            "max_recent_files", "default_shell", "installed_extensions",
            "highlight_current_line", "show_whitespace", "cursor_blink",
            "minimap_enabled", "suppress_git_prompt",
        ]
        for key in required:
            self.assertIn(key, DEFAULT_SETTINGS, f"Missing key: {key}")

    def test_default_settings_types(self):
        from src.config import DEFAULT_SETTINGS
        self.assertIsInstance(DEFAULT_SETTINGS["theme"], str)
        self.assertIsInstance(DEFAULT_SETTINGS["font_size"], int)
        self.assertIsInstance(DEFAULT_SETTINGS["auto_indent"], bool)
        self.assertIsInstance(DEFAULT_SETTINGS["installed_extensions"], list)

    def test_supported_extensions(self):
        from src.config import SUPPORTED_EXTENSIONS
        self.assertIn(".py", SUPPORTED_EXTENSIONS)
        self.assertEqual(SUPPORTED_EXTENSIONS[".py"], "Python")
        self.assertIn(".js", SUPPORTED_EXTENSIONS)
        self.assertIn(".html", SUPPORTED_EXTENSIONS)

    def test_font_options(self):
        from src.config import FONT_OPTIONS
        self.assertIsInstance(FONT_OPTIONS, list)
        self.assertGreater(len(FONT_OPTIONS), 5)
        self.assertIn("Consolas", FONT_OPTIONS)

    def test_git_download_urls(self):
        from src.config import GIT_DOWNLOAD_URLS
        self.assertIn("win32", GIT_DOWNLOAD_URLS)
        self.assertIn("darwin", GIT_DOWNLOAD_URLS)
        self.assertIn("linux", GIT_DOWNLOAD_URLS)

    def test_directories_created(self):
        from src.config import CONFIG_DIR, EXTENSIONS_DIR
        self.assertTrue(os.path.isdir(CONFIG_DIR))
        self.assertTrue(os.path.isdir(EXTENSIONS_DIR))


if __name__ == "__main__":
    unittest.main()