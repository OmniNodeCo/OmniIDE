"""Fuzzy matching engine for Quick Open and the command palette.

Pure Python — no Qt imports so it can be unit-tested headless.
"""

from __future__ import annotations


def score(query: str, target: str) -> int:
    """Score how well ``query`` matches ``target``.

    Returns a non-negative int where higher is better. 0 means no match.
    Matches starting at a word boundary / path separator score higher,
    consecutive matches score higher than scattered chars, and tight
    matches (little trailing text) are preferred.
    """
    if not query:
        return 1
    if not target:
        return 0

    q = query.lower()
    t = target.lower()
    n, m = len(t), len(q)

    # Single pass: find the earliest subsequence match and gather bonuses.
    qi = 0
    total = 0
    run = 0
    matched = 0
    for ti in range(n):
        if qi < m and t[ti] == q[qi]:
            qi += 1
            matched += 1
            total += 2
            # Consecutive match chain bonus
            if run:
                total += 4
            run += 1
            # Boundary bonus for where this match started
            if run == 1:
                if ti == 0:
                    total += 10
                else:
                    prev = t[ti - 1]
                    if prev in "./\\-_ ":
                        total += 8
                    elif q[qi - 1].isupper() and t[ti].isupper():
                        total += 5
            if matched == m:
                total += max(0, 10 - (n - ti))
                break
        else:
            run = 0

    return total if matched == m else 0


def is_match(query: str, target: str) -> bool:
    """True if every char of query appears in target in order."""
    if not query:
        return True
    q = query.lower()
    t = target.lower()
    qi = 0
    for ch in t:
        if qi < len(q) and ch == q[qi]:
            qi += 1
            if qi == len(q):
                return True
    return False


def rank(items, get_text, query: str, limit: int = 50):
    """Rank ``items`` by fuzzy score against ``query``.

    ``get_text(item)`` returns the string to match (e.g. the file path).
    Returns a list of ``(item, score)`` tuples, best first, capped at
    ``limit``. Items that do not match are dropped.
    """
    scored = []
    for item in items:
        text = get_text(item)
        s = score(query, text)
        if s > 0:
            scored.append((item, s))
    scored.sort(key=lambda pair: (-pair[1], get_text(pair[0]).lower()))
    return scored[:limit]
