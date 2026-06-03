"""Tests for file manager utilities."""

import unittest
import tempfile
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestRecentFiles(unittest.TestCase):
    """Test recent files manager."""

    def test_add_and_get(self):
        from src.utils.recent_files import RecentFilesManager
        manager = RecentFilesManager()
        
        # Create a temp file to add
        with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as f:
            temp_path = f.name
            f.write(b"# test")

        try:
            manager.add(temp_path)
            files = manager.get_all()
            self.assertIn(os.path.abspath(temp_path), files)
        finally:
            os.unlink(temp_path)

    def test_clear(self):
        from src.utils.recent_files import RecentFilesManager
        manager = RecentFilesManager()
        manager.clear()
        self.assertEqual(len(manager.get_all()), 0)


class TestThemeLoader(unittest.TestCase):
    """Test theme loading."""

    def test_dark_theme_loads(self):
        from src.utils.theme_loader import ThemeLoader
        loader = ThemeLoader("dark")
        self.assertIn("bg_primary", loader.colors)
        self.assertIn("keyword", loader.syntax)

    def test_light_theme_loads(self):
        from src.utils.theme_loader import ThemeLoader
        loader = ThemeLoader("light")
        self.assertIn("bg_primary", loader.colors)

    def test_fallback_theme(self):
        from src.utils.theme_loader import ThemeLoader
        loader = ThemeLoader("nonexistent")
        # Should fallback to defaults
        self.assertIn("bg_primary", loader.colors)


if __name__ == "__main__":
    unittest.main()