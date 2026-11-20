"""Tests for the project-wide search engine."""

import unittest
import sys
import os
import tempfile
import shutil

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.project_search import ProjectSearch


class TestProjectSearch(unittest.TestCase):

    def setUp(self):
        self.root = tempfile.mkdtemp(prefix="omni_search_")
        os.makedirs(os.path.join(self.root, "sub"))
        self._write("a.py", "hello world\nfoo hello\nbar\n")
        self._write(os.path.join("sub", "b.txt"), "HELLO again\nnothing\n")
        self._write_bytes("bin.dat", b"\x00\x01\x02hello")
        self._write("ignore.txt", "hello in ignored\n")
        # An ignored dir that should be skipped
        os.makedirs(os.path.join(self.root, "node_modules"))
        self._write(os.path.join("node_modules", "c.js"), "hello in node_modules\n")

    def _write(self, name, content):
        path = os.path.join(self.root, name)
        with open(path, "w") as f:
            f.write(content)
        return path

    def _write_bytes(self, name, data):
        path = os.path.join(self.root, name)
        with open(path, "wb") as f:
            f.write(data)
        return path

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def test_basic_search(self):
        s = ProjectSearch(self.root)
        results = s.search("hello")
        # a.py has 2, sub/b.txt has 1, ignore.txt has 1 = 4 (binary skipped,
        # node_modules skipped)
        self.assertEqual(len(results), 4)

    def test_case_sensitive(self):
        s = ProjectSearch(self.root)
        results = s.search("hello", case_sensitive=True)
        # Only lowercase "hello" in a.py (2) and ignore.txt (1)
        self.assertEqual(len(results), 3)

    def test_regex(self):
        s = ProjectSearch(self.root)
        results = s.search(r"he+llo", use_regex=True)
        self.assertEqual(len(results), 4)

    def test_bad_regex_returns_empty(self):
        s = ProjectSearch(self.root)
        self.assertEqual(s.search("x{", use_regex=True), [])

    def test_whole_word(self):
        s = ProjectSearch(self.root)
        results = s.search("hello", whole_word=True)
        self.assertEqual(len(results), 4)

    def test_line_numbers(self):
        s = ProjectSearch(self.root)
        results = s.search("foo")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].line_no, 2)
        self.assertIn("foo hello", results[0].line_text)

    def test_skips_binary(self):
        s = ProjectSearch(self.root)
        results = s.search("hello")
        paths = [r.path for r in results]
        self.assertNotIn(os.path.join(self.root, "bin.dat"), paths)

    def test_skips_ignored_dirs(self):
        s = ProjectSearch(self.root)
        results = s.search("hello")
        paths = [r.path for r in results]
        self.assertFalse(any("node_modules" in p for p in paths))

    def test_max_results(self):
        s = ProjectSearch(self.root, max_results=2)
        results = s.search("hello")
        self.assertLessEqual(len(results), 2)

    def test_no_query(self):
        s = ProjectSearch(self.root)
        self.assertEqual(s.search(""), [])

    def test_missing_root(self):
        s = ProjectSearch(os.path.join(self.root, "does_not_exist"))
        self.assertEqual(s.search("hello"), [])

    def test_file_count(self):
        s = ProjectSearch(self.root)
        results = s.search("hello")
        counts = s.file_count(results)
        self.assertEqual(counts[os.path.join(self.root, "a.py")], 2)

    def test_abort(self):
        s = ProjectSearch(self.root)
        s.abort()
        results = s.search("hello")
        self.assertEqual(results, [])


if __name__ == "__main__":
    unittest.main()
