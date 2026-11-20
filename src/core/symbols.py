"""Symbol (function/class/const) extraction for Go-to-Symbol.

Pure Python — no Qt imports so it can be unit-tested headless.
"""

import os
import re

from src.core.fuzzy import score as fuzzy_score


# Per-language line patterns: (regex, kind)
PATTERNS = {
    "python": [
        (re.compile(r"^\s*(?:async\s+)?def\s+(\w+)"), "function"),
        (re.compile(r"^\s*class\s+(\w+)"), "class"),
    ],
    "javascript": [
        (re.compile(r"^\s*(?:export\s+)?(?:default\s+)?function\s*\*?\s*(\w+)"), "function"),
        (re.compile(r"^\s*(?:export\s+)?class\s+(\w+)"), "class"),
        (re.compile(r"^\s*(?:export\s+)?(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?\("), "function"),
        (re.compile(r"^\s*(?:export\s+)?(?:const|let|var)\s+(\w+)\s*="), "constant"),
    ],
    "typescript": [
        (re.compile(r"^\s*(?:export\s+)?(?:default\s+)?(?:async\s+)?function\s*\*?\s*(\w+)"), "function"),
        (re.compile(r"^\s*(?:export\s+)?class\s+(\w+)"), "class"),
        (re.compile(r"^\s*(?:export\s+)?interface\s+(\w+)"), "interface"),
        (re.compile(r"^\s*(?:export\s+)?type\s+(\w+)\s*="), "type"),
        (re.compile(r"^\s*(?:export\s+)?(?:const|let|var)\s+(\w+)\s*="), "constant"),
    ],
    "rust": [
        (re.compile(r"^\s*(?:pub\s+)?(?:async\s+)?fn\s+(\w+)"), "function"),
        (re.compile(r"^\s*(?:pub\s+)?struct\s+(\w+)"), "struct"),
        (re.compile(r"^\s*(?:pub\s+)?enum\s+(\w+)"), "enum"),
        (re.compile(r"^\s*(?:pub\s+)?trait\s+(\w+)"), "trait"),
    ],
    "go": [
        (re.compile(r"^\s*func\s*(?:\(\w+\s+\*?\w+\)\s*)?(\w+)"), "function"),
        (re.compile(r"^\s*type\s+(\w+)\s+(?:struct|interface)"), "type"),
        (re.compile(r"^\s*const\s+(\w+)"), "constant"),
        (re.compile(r"^\s*var\s+(\w+)"), "variable"),
    ],
    "c": [
        (re.compile(r"^\s*[\w\*&\s]+?(\w+)\s*\([^;{]*\)\s*(?:const\s*)?\{"), "function"),
        (re.compile(r"^\s*typedef\s+struct\s*\{[^}]*\}\s*(\w+)"), "type"),
    ],
    "ruby": [
        (re.compile(r"^\s*def(?:\s+self)?\s*(\w+)"), "function"),
        (re.compile(r"^\s*(?:class|module)\s+(\w+)"), "class"),
    ],
    "php": [
        (re.compile(r"^\s*(?:public\s+|private\s+|protected\s+|static\s+)*function\s+(\w+)"), "function"),
        (re.compile(r"^\s*(?:abstract\s+|final\s+)?class\s+(\w+)"), "class"),
        (re.compile(r"^\s*(?:const|define)\s*\(?\s*['\"]?(\w+)"), "constant"),
    ],
    "java": [
        (re.compile(r"^\s*(?:public|private|protected|static|final|\s)+[\w<>\[\],\s]+\s+(\w+)\s*\([^)]*\)\s*\{"), "function"),
        (re.compile(r"^\s*(?:public|private|protected|\s)*(?:abstract\s+|final\s+)?class\s+(\w+)"), "class"),
        (re.compile(r"^\s*(?:public|private|protected|\s)*(?:abstract\s+|final\s+)?(interface|enum)\s+(\w+)"), "interface"),
    ],
}

LANGUAGE_BY_EXT = {
    ".py": "python", ".pyw": "python",
    ".js": "javascript", ".jsx": "javascript", ".mjs": "javascript",
    ".ts": "typescript", ".tsx": "typescript",
    ".rs": "rust", ".go": "go",
    ".c": "c", ".h": "c", ".cpp": "c", ".cc": "c",
    ".rb": "ruby", ".php": "php", ".java": "java",
}


def extract_symbols(text, filepath):
    """Extract (name, kind, line_no) symbols from source text."""
    if not text:
        return []
    lang = LANGUAGE_BY_EXT.get(
        os.path.splitext(filepath or "")[1].lower(), "javascript"
    )
    patterns = PATTERNS.get(lang, PATTERNS["javascript"])

    seen = set()
    out = []
    for i, line in enumerate(text.split("\n"), 1):
        for regex, kind in patterns:
            m = regex.match(line)
            if m:
                name = m.group(1)
                if name in seen:
                    continue
                seen.add(name)
                out.append((name, kind, i))
                break
    return out


def rank_symbols(query, symbols, limit=50):
    """Fuzzy-rank symbols. Returns (name, kind, line, score) best-first."""
    if not symbols:
        return []
    scored = []
    for name, kind, line in symbols:
        s = fuzzy_score(query, f"{kind} {name}")
        if s > 0:
            scored.append((name, kind, line, s))
    scored.sort(key=lambda t: (-t[3], t[0].lower()))
    return scored[:limit]
