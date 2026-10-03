"""Tests for the VS Code source cloner (pure-logic parts)."""

import unittest
import sys
import os
import tempfile
import shutil

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.source_cloner import (
    SOURCE_REPOS, build_clone_command, validate_destination, SourceCloner,
)


class TestBuildCloneCommand(unittest.TestCase):

    def test_shallow_clone(self):
        cmd = build_clone_command("git", "https://x/y.git", "/dest/y")
        self.assertEqual(cmd, ["git", "clone", "--depth", "1", "https://x/y.git", "/dest/y"])

    def test_custom_depth(self):
        cmd = build_clone_command("git", "u", "d", depth=3)
        self.assertIn("--depth", cmd)
        self.assertIn("3", cmd)


class TestValidateDestination(unittest.TestCase):

    def test_ok(self):
        d = tempfile.mkdtemp()
        try:
            ok, dest, err = validate_destination(d, "vscode")
            self.assertTrue(ok)
            self.assertEqual(dest, os.path.join(d, "vscode"))
            self.assertIsNone(err)
        finally:
            shutil.rmtree(d, ignore_errors=True)

    def test_missing_base(self):
        ok, dest, err = validate_destination("/nonexistent/path/xyz", "vscode")
        self.assertFalse(ok)
        self.assertIsNotNone(err)

    def test_empty_base(self):
        ok, dest, err = validate_destination("", "vscode")
        self.assertFalse(ok)

    def test_existing_destination(self):
        d = tempfile.mkdtemp()
        try:
            os.makedirs(os.path.join(d, "vscode"))
            ok, dest, err = validate_destination(d, "vscode")
            self.assertFalse(ok)
            self.assertIn("already exists", err)
        finally:
            shutil.rmtree(d, ignore_errors=True)


class TestSourceRepos(unittest.TestCase):

    def test_vscode_entry(self):
        self.assertIn("vscode", SOURCE_REPOS)
        repo = SOURCE_REPOS["vscode"]
        self.assertIn("microsoft/vscode", repo["url"])
        self.assertTrue(repo["url"].startswith("https://"))
        self.assertEqual(repo["default_name"], "vscode")


class TestSourceCloner(unittest.TestCase):

    def test_has_git_without_binary(self):
        c = SourceCloner(git_path=None)
        # may or may not find git on PATH; either is fine
        self.assertIn(c.has_git(), (True, False))

    def test_unknown_repo_emits_failure(self):
        from PyQt6.QtWidgets import QApplication
        app = QApplication.instance() or QApplication([])
        c = SourceCloner(git_path="/usr/bin/git")
        results = []
        c.signals.finished.connect(lambda ok, msg: results.append((ok, msg)))
        started = c.start("does-not-exist", "/tmp")
        self.assertFalse(started)
        self.assertEqual(len(results), 1)
        self.assertFalse(results[0][0])

    def test_start_with_bad_destination_emits_failure(self):
        from PyQt6.QtWidgets import QApplication
        QApplication.instance() or QApplication([])
        c = SourceCloner(git_path="/usr/bin/git")
        results = []
        c.signals.finished.connect(lambda ok, msg: results.append((ok, msg)))
        started = c.start("vscode", "/nonexistent/base/xyz")
        self.assertFalse(started)
        self.assertEqual(len(results), 1)
        self.assertFalse(results[0][0])

    def test_human_size(self):
        self.assertEqual(SourceCloner._human(512), "512 B")
        self.assertEqual(SourceCloner._human(2048), "2.0 KB")
        self.assertEqual(SourceCloner._human(5 * 1024 * 1024), "5.0 MB")
        self.assertEqual(SourceCloner._human(3 * 1024 * 1024 * 1024), "3.0 GB")


if __name__ == "__main__":
    unittest.main()
