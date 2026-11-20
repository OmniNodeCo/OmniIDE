"""Static code checks (syntax errors) — pure Python, no Qt.

Used by the Problems panel. Checks run on the *in-editor* text so
unsaved changes are validated too.
"""

import ast
import json
import os


def check_python(text):
    """Return a list of (line, message) syntax problems for Python code."""
    try:
        compile(text, "<editor>", "exec")
        return []
    except SyntaxError as e:
        line = e.lineno or 1
        return [(line, e.msg or "Syntax error")]
    except ValueError as e:  # e.g. null byte in input
        return [(1, str(e))]
    except Exception as e:  # pragma: no cover
        return [(1, f"Check failed: {e}")]


def check_json(text):
    """Return a list of (line, message) problems for JSON text."""
    try:
        json.loads(text)
        return []
    except json.JSONDecodeError as e:
        return [(e.lineno, f"JSON error: {e.msg}")]
    except Exception as e:  # pragma: no cover
        return [(1, f"JSON error: {e}")]


_CHECKERS = {
    ".py": check_python,
    ".pyw": check_python,
    ".json": check_json,
}


def check_text(text, filepath):
    """Check text for a given file path. Returns [(line, message)]."""
    ext = os.path.splitext(filepath or "")[1].lower()
    checker = _CHECKERS.get(ext)
    if checker is None:
        return []
    return checker(text)


def check_file(path):
    """Check a file on disk. Returns [(line, message)]."""
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            text = f.read()
    except OSError:
        return []
    return check_text(text, path)
