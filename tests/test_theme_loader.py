"""Tests for theme loader."""

import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestThemeLoader(unittest.TestCase):

    def test_dark_theme(self):
        from src.utils.theme_loader import ThemeLoader
        loader = ThemeLoader("dark")
        self.assertIn("bg_primary", loader.colors)
        self.assertIn("keyword", loader.syntax)
        self.assertTrue(loader.colors["bg_primary"].startswith("#"))

    def test_light_theme(self):
        from src.utils.theme_loader import ThemeLoader
        loader = ThemeLoader("light")
        self.assertIn("bg_primary", loader.colors)
        self.assertIn("keyword", loader.syntax)

    def test_themes_differ(self):
        from src.utils.theme_loader import ThemeLoader
        dark = ThemeLoader("dark")
        light = ThemeLoader("light")
        self.assertNotEqual(dark.colors["bg_primary"], light.colors["bg_primary"])

    def test_fallback_theme(self):
        from src.utils.theme_loader import ThemeLoader
        loader = ThemeLoader("nonexistent_theme")
        self.assertIn("bg_primary", loader.colors)
        self.assertIn("keyword", loader.syntax)

    def test_required_colors(self):
        from src.utils.theme_loader import ThemeLoader
        loader = ThemeLoader("dark")
        required = [
            "bg_primary", "bg_secondary", "bg_tertiary",
            "fg_primary", "fg_secondary", "accent",
            "editor_bg", "editor_fg", "sidebar_bg",
            "terminal_bg", "terminal_fg", "border", "selection",
        ]
        for key in required:
            self.assertIn(key, loader.colors, f"Missing color: {key}")

    def test_required_syntax(self):
        from src.utils.theme_loader import ThemeLoader
        loader = ThemeLoader("dark")
        required = ["keyword", "string", "comment", "number", "function", "class", "operator"]
        for key in required:
            self.assertIn(key, loader.syntax, f"Missing syntax: {key}")


if __name__ == "__main__":
    unittest.main()