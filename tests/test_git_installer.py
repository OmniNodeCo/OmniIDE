"""Tests for Git installer detection."""

import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestGitInstaller(unittest.TestCase):

    def _make_installer(self):
        from src.core.git_installer import GitInstaller
        gi = GitInstaller.__new__(GitInstaller)
        return gi

    def test_platform_key(self):
        gi = self._make_installer()
        key = gi._get_platform_key()
        self.assertIn(key, ("win32", "darwin", "linux"))

    def test_platform_name(self):
        gi = self._make_installer()
        name = gi._get_platform_name()
        self.assertIn(name, ("Windows", "macOS", "Linux"))

    def test_platform_key_matches_name(self):
        gi = self._make_installer()
        mapping = {"win32": "Windows", "darwin": "macOS", "linux": "Linux"}
        key = gi._get_platform_key()
        name = gi._get_platform_name()
        self.assertEqual(mapping[key], name)

    def test_git_download_url_exists(self):
        from src.config import GIT_DOWNLOAD_URLS
        gi = self._make_installer()
        key = gi._get_platform_key()
        self.assertIn(key, GIT_DOWNLOAD_URLS)
        url = GIT_DOWNLOAD_URLS[key]
        self.assertTrue(url.startswith("https://"))


if __name__ == "__main__":
    unittest.main()