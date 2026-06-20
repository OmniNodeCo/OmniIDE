"""Tests for update checker."""

import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestUpdater(unittest.TestCase):

    def _make_updater(self):
        from src.core.updater import Updater
        u = Updater.__new__(Updater)
        return u

    def test_newer_version(self):
        u = self._make_updater()
        self.assertTrue(u._is_newer("1.0.5", "1.0.4"))
        self.assertTrue(u._is_newer("2.0.0", "1.9.9"))
        self.assertTrue(u._is_newer("1.1.0", "1.0.9"))

    def test_same_version(self):
        u = self._make_updater()
        self.assertFalse(u._is_newer("1.0.4", "1.0.4"))
        self.assertFalse(u._is_newer("2.0.0", "2.0.0"))

    def test_older_version(self):
        u = self._make_updater()
        self.assertFalse(u._is_newer("1.0.3", "1.0.4"))
        self.assertFalse(u._is_newer("0.9.9", "1.0.0"))

    def test_different_length_versions(self):
        u = self._make_updater()
        self.assertFalse(u._is_newer("1.0.0", "1.0.0.1"))
        self.assertTrue(u._is_newer("1.0.0.2", "1.0.0.1"))

    def test_invalid_versions(self):
        u = self._make_updater()
        self.assertFalse(u._is_newer("abc", "1.0.0"))
        self.assertFalse(u._is_newer("1.0.0", "xyz"))
        self.assertFalse(u._is_newer(None, "1.0.0"))

    def test_platform_key(self):
        u = self._make_updater()
        key = u._get_platform_key()
        self.assertIn(key, ("windows", "macos", "linux"))


if __name__ == "__main__":
    unittest.main()