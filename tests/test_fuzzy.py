"""Tests for the fuzzy matching engine."""

import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestFuzzy(unittest.TestCase):

    def test_empty_query_matches_all(self):
        from src.core.fuzzy import score, is_match
        self.assertEqual(score("", "anything"), 1)
        self.assertTrue(is_match("", "anything"))

    def test_no_match(self):
        from src.core.fuzzy import score, is_match
        self.assertEqual(score("zzz", "abc"), 0)
        self.assertFalse(is_match("z", "abc"))

    def test_exact_match_scores_high(self):
        from src.core.fuzzy import score
        self.assertGreater(
            score("main.py", "main.py"),
            score("main.py", "src/old/main.py.bak"),
        )

    def test_prefix_beats_midmatch(self):
        from src.core.fuzzy import score
        self.assertGreater(score("main", "main.js"), score("main", "maintenance"))

    def test_boundary_bonus(self):
        from src.core.fuzzy import score
        # match starting after a path separator should score well
        self.assertGreater(score("app", "src/app.py"), 0)

    def test_subsequence_order_matters(self):
        from src.core.fuzzy import is_match
        self.assertTrue(is_match("abc", "aXbXc"))
        self.assertFalse(is_match("abc", "aXcXb"))

    def test_rank_orders_best_first(self):
        from src.core.fuzzy import rank
        items = ["/a/src/app/main.py", "/a/tests/test_main.py",
                 "/a/main.js", "/a/README.md"]
        result = rank(items, lambda p: p, "main")
        self.assertGreaterEqual(len(result), 1)
        # main.js should be the top hit
        self.assertEqual(result[0][0], "/a/main.js")
        scores = [s for _, s in result]
        self.assertEqual(scores, sorted(scores, reverse=True))

    def test_rank_limit(self):
        from src.core.fuzzy import rank
        items = [f"file_{i}.txt" for i in range(100)]
        result = rank(items, lambda p: p, "file", limit=10)
        self.assertLessEqual(len(result), 10)

    def test_rank_drops_nonmatches(self):
        from src.core.fuzzy import rank
        result = rank(["foo.txt", "bar.txt"], lambda p: p, "zzz")
        self.assertEqual(result, [])


if __name__ == "__main__":
    unittest.main()
