"""Tests for the Quick Open file index."""

import unittest
import sys
import os
import tempfile
import shutil

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.quick_open import QuickOpenIndex, IGNORED_DIRS, IGNORED_EXTS


class TestQuickOpenIndex(unittest.TestCase):

    def setUp(self):
        self.root = tempfile.mkdtemp(prefix="omni_qo_")
        self._make("src/app/main.py")
        self._make("src/app/utils.py")
        self._make("README.md")
        self._make("tests/test_main.py")
        self._make("node_modules/junk.js")
        self._make(".hidden_file")
        self._make("image.png")
        self._make(os.path.join("__pycache__", "x.pyc"))

    def _make(self, rel):
        path = os.path.join(self.root, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write("x")
        return path

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def test_refresh_collects_files(self):
        qi = QuickOpenIndex()
        qi.refresh(self.root)
        names = [os.path.basename(p) for p in qi.files]
        self.assertIn("main.py", names)
        self.assertIn("README.md", names)
        self.assertIn("utils.py", names)

    def test_refresh_skips_ignored_dirs(self):
        qi = QuickOpenIndex()
        qi.refresh(self.root)
        for p in qi.files:
            for d in IGNORED_DIRS:
                self.assertNotIn(os.sep + d + os.sep, p + os.sep)

    def test_refresh_skips_binary_exts(self):
        qi = QuickOpenIndex()
        qi.refresh(self.root)
        names = [os.path.basename(p) for p in qi.files]
        self.assertNotIn("image.png", names)
        self.assertNotIn("x.pyc", names)

    def test_refresh_skips_hidden(self):
        qi = QuickOpenIndex()
        qi.refresh(self.root)
        names = [os.path.basename(p) for p in qi.files]
        self.assertNotIn(".hidden_file", names)

    def test_needs_refresh(self):
        qi = QuickOpenIndex()
        self.assertTrue(qi.needs_refresh(self.root))
        qi.refresh(self.root)
        self.assertFalse(qi.needs_refresh(self.root))
        self.assertTrue(qi.needs_refresh(os.path.join(self.root, "src")))

    def test_query_ranks(self):
        qi = QuickOpenIndex()
        qi.refresh(self.root)
        results = qi.query("main")
        self.assertGreaterEqual(len(results), 2)
        top = results[0][0]
        self.assertTrue(top.endswith("main.py"))

    def test_query_empty_index(self):
        qi = QuickOpenIndex()
        qi.refresh(None)
        self.assertEqual(qi.files, [])
        self.assertEqual(qi.query("x"), [])

    def test_query_rel_paths(self):
        qi = QuickOpenIndex()
        qi.refresh(self.root)
        results = qi.query("utils")
        rel = results[0][1]
        self.assertFalse(rel.startswith(os.sep))
        self.assertIn("utils.py", rel)

    def test_skips_oversized_files(self):
        big = os.path.join(self.root, "big.txt")
        with open(big, "w") as f:
            f.write("a" * (2_000_001))
        qi = QuickOpenIndex()
        qi.refresh(self.root)
        names = [os.path.basename(p) for p in qi.files]
        self.assertNotIn("big.txt", names)


if __name__ == "__main__":
    unittest.main()
