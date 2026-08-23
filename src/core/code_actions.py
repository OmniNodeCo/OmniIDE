"""Editor code actions implemented as pure text transforms.

Each function takes the full document text plus (for cursor-sensitive
ops) the current line number and returns the new text. Keeping them pure
makes them trivially unit-testable and reusable from menus, shortcuts and
the command palette.
"""

from __future__ import annotations

import os

# ── Comment styles per language ──────────────────────────────────────
LINE_COMMENT = {
    ".py": "# ",
    ".js": "// ",
    ".jsx": "// ",
    ".ts": "// ",
    ".tsx": "// ",
    ".c": "// ",
    ".cpp": "// ",
    ".cc": "// ",
    ".h": "// ",
    ".hpp": "// ",
    ".java": "// ",
    ".go": "// ",
    ".rs": "// ",
    ".cs": "// ",
    ".swift": "// ",
    ".kt": "// ",
    ".kts": "// ",
    ".dart": "// ",
    ".lua": "-- ",
    ".sh": "# ",
    ".bash": "# ",
    ".zsh": "# ",
    ".pl": "# ",
    ".pm": "# ",
    ".r": "# ",
    ".R": "# ",
    ".toml": "# ",
    ".ini": "; ",
    ".cfg": "; ",
    ".yml": "# ",
    ".yaml": "# ",
    ".sql": "-- ",
    ".ps1": "# ",
    ".ex": "# ",
    ".exs": "# ",
    ".erl": "% ",
    ".scala": "// ",
    ".groovy": "// ",
    ".vue": "<!-- ",
    ".svelte": "<!-- ",
    ".styl": "// ",
    ".scss": "// ",
}

# Block comment pairs for languages without line comments
BLOCK_COMMENT = {
    ".css": ("/* ", " */"),
    ".less": ("/* ", " */"),
    ".php": ("// ",),
    ".bat": ("rem ",),
    ".cmd": ("rem ",),
    ".clj": ("; ",),
}

# Extensions treated as "no comments"
NO_COMMENT = {".json", ".xml", ".svg", ".md", ".txt", ".lock"}


def comment_style(filepath):
    """Return (line_prefix, block_pair) for the file, or None to skip."""
    ext = os.path.splitext(filepath or "")[1]
    if ext in NO_COMMENT:
        return None
    if ext in LINE_COMMENT:
        return (LINE_COMMENT[ext], None)
    if ext in BLOCK_COMMENT:
        return (None, BLOCK_COMMENT[ext])
    return None


def _line_prefix(style):
    line_pref, block = style
    if line_pref is not None:
        return line_pref
    if block:
        return block[0]
    return None


def toggle_comment_line(text, line_no, filepath):
    """Comment or uncomment line ``line_no`` (1-based).

    Returns the new document text.
    """
    style = comment_style(filepath)
    if style is None:
        return text

    prefix = _line_prefix(style)
    lines = text.split("\n")
    if not (1 <= line_no <= len(lines)):
        return text

    line = lines[line_no - 1]
    stripped = line.lstrip()

    if stripped.startswith(prefix.rstrip()):
        # Uncomment: remove the prefix (keep the rest, dedent the prefix width)
        indent = line[: len(line) - len(stripped)]
        new_line = indent + stripped[len(prefix.rstrip()):].lstrip()
        lines[line_no - 1] = new_line
    else:
        indent = line[: len(line) - len(stripped)]
        lines[line_no - 1] = f"{indent}{prefix}{stripped}"

    return "\n".join(lines)


def duplicate_line(text, line_no, indent_copy=True):
    """Duplicate line ``line_no`` directly below it."""
    lines = text.split("\n")
    if not (1 <= line_no <= len(lines)):
        return text
    line = lines[line_no - 1]
    lines.insert(line_no, line)
    return "\n".join(lines)


def delete_line(text, line_no):
    """Delete line ``line_no`` entirely (merges nothing)."""
    lines = text.split("\n")
    if len(lines) == 1:
        return lines[0]
    if not (1 <= line_no <= len(lines)):
        return text
    del lines[line_no - 1]
    return "\n".join(lines)


def move_line_up(text, line_no):
    lines = text.split("\n")
    if line_no > 1:
        lines[line_no - 2], lines[line_no - 1] = lines[line_no - 1], lines[line_no - 2]
    return "\n".join(lines)


def move_line_down(text, line_no):
    lines = text.split("\n")
    if line_no < len(lines):
        lines[line_no - 1], lines[line_no] = lines[line_no], lines[line_no - 1]
    return "\n".join(lines)


def sort_lines(text, line_no, ascending=True):
    """Sort the line and its trailing identical-indent run (or just it).

    A practical "sort line": sorts the block of consecutive lines that
    share the same indent as the cursor line, case-insensitively.
    """
    lines = text.split("\n")
    if not (1 <= line_no <= len(lines)):
        return text
    anchor_indent = lines[line_no - 1][: len(lines[line_no - 1]) - len(lines[line_no - 1].lstrip())]

    start = line_no - 1
    while start > 0 and lines[start - 1].rstrip() and _indent_of(lines[start - 1]) == anchor_indent:
        start -= 1
    end = line_no
    while end < len(lines) and lines[end].rstrip() and _indent_of(lines[end]) == anchor_indent:
        end += 1

    block = lines[start:end]
    block.sort(key=str.lower, reverse=not ascending)
    lines[start:end] = block
    return "\n".join(lines)


def _indent_of(line):
    return line[: len(line) - len(line.lstrip())]


def indent_lines(text, line_no, tab_size=4, tabs=False):
    """Add one level of indentation to line ``line_no``."""
    fill = "\t" if tabs else " " * tab_size
    lines = text.split("\n")
    if 1 <= line_no <= len(lines):
        lines[line_no - 1] = fill + lines[line_no - 1]
    return "\n".join(lines)


def outdent_lines(text, line_no, tab_size=4, tabs=False):
    """Remove up to one level of indentation from line ``line_no``."""
    lines = text.split("\n")
    if 1 <= line_no <= len(lines):
        line = lines[line_no - 1]
        if tabs and line.startswith("\t"):
            lines[line_no - 1] = line[1:]
        else:
            n = 0
            while n < tab_size and n < len(line) and line[n] == " ":
                n += 1
            lines[line_no - 1] = line[n:]
    return "\n".join(lines)
