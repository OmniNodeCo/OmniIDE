"""Tests for syntax highlighter."""

import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestSyntaxHighlighter(unittest.TestCase):

    def _make_highlighter(self):
        from src.core.syntax_highlighter import SyntaxHighlighter
        h = SyntaxHighlighter.__new__(SyntaxHighlighter)
        return h

    def test_detect_python(self):
        h = self._make_highlighter()
        h.filepath = "test.py"
        self.assertEqual(h._detect_language(), "python")

    def test_detect_javascript(self):
        h = self._make_highlighter()
        for ext in ["test.js", "test.jsx", "test.ts", "test.tsx"]:
            h.filepath = ext
            self.assertEqual(h._detect_language(), "javascript")

    def test_detect_html(self):
        h = self._make_highlighter()
        for ext in ["test.html", "test.htm"]:
            h.filepath = ext
            self.assertEqual(h._detect_language(), "html")

    def test_detect_css(self):
        h = self._make_highlighter()
        h.filepath = "style.css"
        self.assertEqual(h._detect_language(), "css")

    def test_detect_json(self):
        h = self._make_highlighter()
        h.filepath = "data.json"
        self.assertEqual(h._detect_language(), "json")

    def test_detect_unknown(self):
        h = self._make_highlighter()
        h.filepath = "file.xyz"
        self.assertEqual(h._detect_language(), "text")

    def test_detect_none(self):
        h = self._make_highlighter()
        h.filepath = None
        self.assertEqual(h._detect_language(), "python")

    def test_python_keywords(self):
        from src.core.syntax_highlighter import SyntaxHighlighter
        required = ["def", "class", "if", "else", "for", "while", "import", "return", "try", "except"]
        for kw in required:
            self.assertIn(kw, SyntaxHighlighter.PYTHON_KEYWORDS)

    def test_python_builtins(self):
        from src.core.syntax_highlighter import SyntaxHighlighter
        required = ["print", "len", "range", "int", "str", "list", "dict"]
        for bi in required:
            self.assertIn(bi, SyntaxHighlighter.PYTHON_BUILTINS)

    def test_js_keywords(self):
        from src.core.syntax_highlighter import SyntaxHighlighter
        required = ["function", "var", "let", "const", "return", "if", "else", "class"]
        for kw in required:
            self.assertIn(kw, SyntaxHighlighter.JS_KEYWORDS)


if __name__ == "__main__":
    unittest.main()