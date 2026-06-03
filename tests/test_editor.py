"""Tests for the code editor."""

import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestEditorConfig(unittest.TestCase):
    """Test editor configuration."""

    def test_default_settings(self):
        from src.config import DEFAULT_SETTINGS
        self.assertEqual(DEFAULT_SETTINGS["font_family"], "Consolas")
        self.assertEqual(DEFAULT_SETTINGS["font_size"], 13)
        self.assertEqual(DEFAULT_SETTINGS["tab_size"], 4)
        self.assertTrue(DEFAULT_SETTINGS["auto_indent"])

    def test_supported_extensions(self):
        from src.config import SUPPORTED_EXTENSIONS
        self.assertIn(".py", SUPPORTED_EXTENSIONS)
        self.assertIn(".js", SUPPORTED_EXTENSIONS)
        self.assertIn(".html", SUPPORTED_EXTENSIONS)
        self.assertEqual(SUPPORTED_EXTENSIONS[".py"], "Python")


class TestSyntaxHighlighter(unittest.TestCase):
    """Test syntax detection."""

    def test_language_detection(self):
        from src.core.syntax_highlighter import SyntaxHighlighter
        # Test without widget (just detection logic)
        highlighter = SyntaxHighlighter.__new__(SyntaxHighlighter)
        highlighter.filepath = "test.py"
        self.assertEqual(highlighter._detect_language(), "python")

        highlighter.filepath = "test.js"
        self.assertEqual(highlighter._detect_language(), "javascript")

        highlighter.filepath = "test.html"
        self.assertEqual(highlighter._detect_language(), "html")

        highlighter.filepath = "test.css"
        self.assertEqual(highlighter._detect_language(), "css")

        highlighter.filepath = "test.unknown"
        self.assertEqual(highlighter._detect_language(), "text")


if __name__ == "__main__":
    unittest.main()