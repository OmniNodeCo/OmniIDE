"""Project-wide search engine (Search in Files).

Walks the project, skips ignored/binary files, and collects matches with
line numbers. Pure Python — no Qt imports.
"""

from __future__ import annotations

import os
import re

from src.core.quick_open import IGNORED_DIRS

MAX_FILE_SIZE = 2_000_000  # bytes
MAX_RESULTS = 5000
MAX_LINE_LEN = 4000


def _is_binary(path, chunk_size=8192):
    try:
        with open(path, "rb") as f:
            chunk = f.read(chunk_size)
    except OSError:
        return True
    if b"\x00" in chunk:
        return True
    return False


class SearchResult:
    __slots__ = ("path", "line_no", "line_text")

    def __init__(self, path, line_no, line_text):
        self.path = path
        self.line_no = line_no
        self.line_text = line_text

    def __repr__(self):
        return f"SearchResult({self.path}:{self.line_no})"


class ProjectSearch:
    """Searches all files under a project root."""

    def __init__(self, root, max_results=MAX_RESULTS, max_file_size=MAX_FILE_SIZE):
        self.root = root
        self.max_results = max_results
        self.max_file_size = max_file_size
        self.aborted = False

    def abort(self):
        self.aborted = True

    def _compile(self, query, case_sensitive, use_regex, whole_word):
        if use_regex:
            pattern = query
            flags = 0 if case_sensitive else re.IGNORECASE
        else:
            pattern = re.escape(query)
            flags = re.IGNORECASE if not case_sensitive else 0
        if whole_word:
            pattern = rf"(?<!\w){pattern}(?!\w)"
        try:
            return re.compile(pattern, flags)
        except re.error:
            return None

    def search(self, query, case_sensitive=False, use_regex=False, whole_word=False,
               should_continue=None):
        """Run the search. Returns a list of SearchResult (capped)."""
        if not self.root or not os.path.isdir(self.root) or not query:
            return []

        rx = self._compile(query, case_sensitive, use_regex, whole_word)
        if rx is None:
            return []

        results = []
        for dirpath, dirnames, filenames in os.walk(self.root):
            if self.aborted:
                break
            dirnames[:] = [d for d in dirnames if d not in IGNORED_DIRS]
            for name in filenames:
                if self.aborted:
                    break
                if name.startswith(".") or name in IGNORED_DIRS:
                    continue
                path = os.path.join(dirpath, name)
                try:
                    if os.path.getsize(path) > self.max_file_size:
                        continue
                except OSError:
                    continue
                if _is_binary(path):
                    continue
                try:
                    with open(path, "r", encoding="utf-8", errors="replace") as f:
                        for i, line in enumerate(f, 1):
                            if self.aborted:
                                return results
                            if len(line) > MAX_LINE_LEN:
                                line = line[:MAX_LINE_LEN]
                            if rx.search(line):
                                results.append(SearchResult(path, i, line.rstrip("\n")))
                                if len(results) >= self.max_results:
                                    return results
                except OSError:
                    continue
                if should_continue and not should_continue():
                    break

        return results

    def file_count(self, results):
        """Return {path: match_count} for a list of SearchResult."""
        counts = {}
        for r in results:
            counts[r.path] = counts.get(r.path, 0) + 1
        return counts
