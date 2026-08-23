"""Tests for editor code actions (line ops + comment toggle)."""

import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core import code_actions as ca


class TestCommentToggle(unittest.TestCase):

    def test_comment_python(self):
        self.assertEqual(
            ca.toggle_comment_line("x = 1\ny = 2", 1, "a.py"),
            "# x = 1\ny = 2",
        )

    def test_uncomment_python(self):
        self.assertEqual(
            ca.toggle_comment_line("# x = 1\ny = 2", 1, "a.py"),
            "x = 1\ny = 2",
        )

    def test_comment_preserves_indent(self):
        self.assertEqual(
            ca.toggle_comment_line("  x = 1", 1, "a.py"),
            "  # x = 1",
        )
        self.assertEqual(
            ca.toggle_comment_line("  # x = 1", 1, "a.py"),
            "  x = 1",
        )

    def test_comment_js(self):
        self.assertEqual(
            ca.toggle_comment_line("let a = 1", 1, "a.js"),
            "// let a = 1",
        )

    def test_no_comment_json(self):
        self.assertEqual(ca.toggle_comment_line("{}", 1, "a.json"), "{}")

    def test_unknown_extension_unchanged(self):
        self.assertEqual(ca.toggle_comment_line("hello", 1, "a.unknown"), "hello")

    def test_out_of_range_unchanged(self):
        text = "x = 1"
        self.assertEqual(ca.toggle_comment_line(text, 99, "a.py"), text)


class TestLineOps(unittest.TestCase):

    def test_duplicate_line(self):
        self.assertEqual(ca.duplicate_line("a\nb\nc", 2), "a\nb\nb\nc")

    def test_duplicate_single_line(self):
        self.assertEqual(ca.duplicate_line("a", 1), "a\na")

    def test_delete_line(self):
        self.assertEqual(ca.delete_line("a\nb\nc", 2), "a\nc")

    def test_delete_only_line_keeps_it(self):
        # Deleting the only line would leave an empty file; keep it stable.
        self.assertEqual(ca.delete_line("a", 1), "a")

    def test_move_up(self):
        self.assertEqual(ca.move_line_up("a\nb\nc", 2), "b\na\nc")
        # First line can't move up
        self.assertEqual(ca.move_line_up("a\nb\nc", 1), "a\nb\nc")

    def test_move_down(self):
        self.assertEqual(ca.move_line_down("a\nb\nc", 1), "b\na\nc")
        # Last line can't move down
        self.assertEqual(ca.move_line_down("a\nb\nc", 3), "a\nb\nc")

    def test_sort_ascending(self):
        self.assertEqual(ca.sort_lines("banana\napple\ncherry", 1),
                         "apple\nbanana\ncherry")

    def test_sort_descending(self):
        self.assertEqual(ca.sort_lines("banana\napple\ncherry", 1, ascending=False),
                         "cherry\nbanana\napple")

    def test_sort_case_insensitive(self):
        self.assertEqual(ca.sort_lines("Banana\napple", 1), "apple\nBanana")


class TestIndent(unittest.TestCase):

    def test_indent_spaces(self):
        self.assertEqual(ca.indent_lines("x = 1", 1, tab_size=4), "    x = 1")

    def test_indent_tabs(self):
        self.assertEqual(ca.indent_lines("x = 1", 1, tab_size=4, tabs=True), "\tx = 1")

    def test_outdent_spaces(self):
        self.assertEqual(ca.outdent_lines("    x = 1", 1, tab_size=4), "x = 1")

    def test_outdent_tabs(self):
        self.assertEqual(ca.outdent_lines("\tx = 1", 1, tab_size=4, tabs=True), "x = 1")

    def test_outdent_partial(self):
        # Only up to tab_size spaces are removed
        self.assertEqual(ca.outdent_lines("  x", 1, tab_size=4), "x")


if __name__ == "__main__":
    unittest.main()
