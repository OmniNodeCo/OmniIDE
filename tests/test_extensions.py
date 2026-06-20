"""Tests for extension manager."""

import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestExtensionManager(unittest.TestCase):

    def test_format_installs_small(self):
        from src.core.extension_manager import ExtensionManager
        self.assertEqual(ExtensionManager.format_installs(0), "0")
        self.assertEqual(ExtensionManager.format_installs(500), "500")
        self.assertEqual(ExtensionManager.format_installs(999), "999")

    def test_format_installs_thousands(self):
        from src.core.extension_manager import ExtensionManager
        self.assertEqual(ExtensionManager.format_installs(1000), "1.0K")
        self.assertEqual(ExtensionManager.format_installs(1500), "1.5K")
        self.assertEqual(ExtensionManager.format_installs(50000), "50.0K")

    def test_format_installs_millions(self):
        from src.core.extension_manager import ExtensionManager
        self.assertEqual(ExtensionManager.format_installs(1000000), "1.0M")
        self.assertEqual(ExtensionManager.format_installs(2500000), "2.5M")

    def test_format_rating(self):
        from src.core.extension_manager import ExtensionManager
        result = ExtensionManager.format_rating(4.5)
        self.assertIn("4.5", result)

    def test_format_rating_zero(self):
        from src.core.extension_manager import ExtensionManager
        result = ExtensionManager.format_rating(0)
        self.assertIn("0", result)


if __name__ == "__main__":
    unittest.main()