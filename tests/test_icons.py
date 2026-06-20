"""Tests for icon system."""

import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestIcons(unittest.TestCase):

    def test_icons_dict_exists(self):
        from assets.icons.icons import ICONS
        self.assertIsInstance(ICONS, dict)
        self.assertGreater(len(ICONS), 30)

    def test_required_icons(self):
        from assets.icons.icons import ICONS
        required = [
            "file", "file_python", "file_javascript", "file_html",
            "file_css", "file_json", "file_markdown", "file_text",
            "folder_closed", "folder_open", "folder_src", "folder_git",
            "new_file", "open_file", "save", "search", "theme",
            "terminal", "close", "clear", "sidebar", "explorer",
            "arrow_left", "arrow_right", "replace", "settings",
            "run", "info", "warning", "error", "success",
        ]
        for icon in required:
            self.assertIn(icon, ICONS, f"Missing icon: {icon}")

    def test_icons_are_svg(self):
        from assets.icons.icons import ICONS
        for name, svg in ICONS.items():
            self.assertIn("<svg", svg.strip(), f"Icon {name} is not SVG")

    def test_file_icon_mapping(self):
        from src.utils.icon_manager import get_file_icon_name
        self.assertEqual(get_file_icon_name("main.py"), "file_python")
        self.assertEqual(get_file_icon_name("app.js"), "file_javascript")
        self.assertEqual(get_file_icon_name("index.html"), "file_html")
        self.assertEqual(get_file_icon_name("unknown.xyz"), "file")

    def test_folder_icon_mapping(self):
        from src.utils.icon_manager import get_folder_icon_name
        self.assertEqual(get_folder_icon_name("src"), "folder_src")
        self.assertEqual(get_folder_icon_name(".git"), "folder_git")
        self.assertEqual(get_folder_icon_name("random"), "folder_closed")
        self.assertEqual(get_folder_icon_name("random", True), "folder_open")

    def test_icon_manager_text_fallback(self):
        from src.utils.icon_manager import IconManager
        mgr = IconManager()
        self.assertEqual(mgr.get_text("file_python"), "[Py]")
        self.assertEqual(mgr.get_text("folder_closed"), "[+]")
        self.assertEqual(mgr.get_text("terminal"), "[>_]")


if __name__ == "__main__":
    unittest.main()