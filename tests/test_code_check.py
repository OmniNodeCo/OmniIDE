"""Tests for code_check and symbols (pure logic)."""

import unittest
import sys
import os
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.code_check import check_python, check_json, check_text, check_file
from src.core.symbols import extract_symbols, rank_symbols


class TestCodeCheck(unittest.TestCase):

    def test_python_valid(self):
        self.assertEqual(check_python("x = 1\nprint(x)\n"), [])

    def test_python_syntax_error(self):
        problems = check_python("def f(:\n    pass\n")
        self.assertEqual(len(problems), 1)
        self.assertEqual(problems[0][0], 1)
        self.assertTrue(problems[0][1].strip())

    def test_python_indent_error(self):
        problems = check_python("if True:\n    pass\n\tpass\n")
        self.assertGreaterEqual(len(problems), 1)

    def test_python_multiline_error_line(self):
        problems = check_python("x = 1\ny = 2\nz = (1 +\n")
        self.assertEqual(problems[0][0], 3)

    def test_json_valid(self):
        self.assertEqual(check_json('{"a": 1}\n'), [])

    def test_json_invalid(self):
        problems = check_json('{\n  "a": 1\n}\nextra\n')
        self.assertGreaterEqual(len(problems), 1)

    def test_json_trailing_comma(self):
        problems = check_json('{"a": 1,}\n')
        self.assertEqual(len(problems), 1)

    def test_check_text_dispatch(self):
        self.assertEqual(check_text("def f(:", "a.py"), check_python("def f(:"))
        self.assertEqual(check_text('{"a":', "a.json"), check_json('{"a":'))
        self.assertEqual(check_text("anything", "a.txt"), [])

    def test_check_file(self):
        with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as f:
            f.write("def broken(\n")
            path = f.name
        try:
            problems = check_file(path)
            self.assertEqual(len(problems), 1)
        finally:
            os.unlink(path)

    def test_check_file_missing(self):
        self.assertEqual(check_file("/nonexistent/x.py"), [])


class TestSymbols(unittest.TestCase):

    def test_python_functions_and_classes(self):
        text = (
            "import os\n\n\n"
            "class Foo:\n"
            "    def bar(self):\n"
            "        pass\n\n\n"
            "def baz():\n"
            "    return 1\n"
            "async def qux():\n"
            "    pass\n"
        )
        syms = extract_symbols(text, "a.py")
        names = [s[0] for s in syms]
        self.assertIn("Foo", names)
        self.assertIn("bar", names)
        self.assertIn("baz", names)
        self.assertIn("qux", names)
        kinds = dict((s[0], s[1]) for s in syms)
        self.assertEqual(kinds["Foo"], "class")
        self.assertEqual(kinds["baz"], "function")
        # line numbers are 1-based and correct
        lines = dict((s[0], s[2]) for s in syms)
        self.assertEqual(lines["Foo"], 4)
        self.assertEqual(lines["baz"], 9)

    def test_javascript(self):
        text = (
            "const x = 1\n"
            "function hello() {}\n"
            "class World {}\n"
            "const arrow = () => {}\n"
            "export function exported() {}\n"
        )
        syms = extract_symbols(text, "a.js")
        names = [s[0] for s in syms]
        self.assertIn("hello", names)
        self.assertIn("World", names)
        self.assertIn("arrow", names)
        self.assertIn("exported", names)

    def test_typescript(self):
        text = "interface I {}\ntype T = string\nclass C {}\nfunction f() {}\n"
        syms = extract_symbols(text, "a.ts")
        names = [s[0] for s in syms]
        for n in ("I", "T", "C", "f"):
            self.assertIn(n, names)

    def test_go(self):
        text = "func main() {}\ntype Config struct{}\nconst Pi = 3.14\n"
        syms = extract_symbols(text, "a.go")
        names = [s[0] for s in syms]
        self.assertIn("main", names)
        self.assertIn("Config", names)
        self.assertIn("Pi", names)

    def test_rust(self):
        text = "pub fn main() {}\nstruct Point {}\nenum Color {}\n"
        syms = extract_symbols(text, "a.rs")
        names = [s[0] for s in syms]
        self.assertIn("main", names)
        self.assertIn("Point", names)
        self.assertIn("Color", names)

    def test_no_symbols(self):
        self.assertEqual(extract_symbols("", "a.py"), [])
        self.assertEqual(extract_symbols("x = 1\ny = 2\n", "a.txt"), [])

    def test_ranking(self):
        syms = [("main", "function", 1), ("format_main", "function", 2),
                ("other", "function", 3)]
        ranked = rank_symbols("main", syms)
        self.assertGreaterEqual(len(ranked), 2)
        self.assertEqual(ranked[0][0], "main")  # exact-ish match first
        scores = [r[3] for r in ranked]
        self.assertEqual(scores, sorted(scores, reverse=True))

    def test_ranking_empty_query(self):
        syms = [("a", "function", 1), ("b", "class", 2)]
        ranked = rank_symbols("", syms)
        self.assertEqual(len(ranked), 2)


if __name__ == "__main__":
    unittest.main()
