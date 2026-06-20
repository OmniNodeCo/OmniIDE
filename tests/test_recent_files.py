"""Tests for recent files manager."""

import unittest
import tempfile
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestRecentFiles(unittest.TestCase):

    def test_add_and_get(self):
        from src.utils.recent_files import RecentFilesManager
        mgr = RecentFilesManager()

        with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as f:
            path = f.name
            f.write(b"# test")

        try:
            mgr.add(path)
            files = mgr.get_all()
            self.assertIn(os.path.abspath(path), files)
        finally:
            os.unlink(path)

    def test_clear(self):
        from src.utils.recent_files import RecentFilesManager
        mgr = RecentFilesManager()
        mgr.clear()
        self.assertEqual(len(mgr.get_all()), 0)

    def test_max_limit(self):
        from src.utils.recent_files import RecentFilesManager
        mgr = RecentFilesManager()
        mgr.clear()

        paths = []
        for i in range(20):
            with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{i}.py") as f:
                f.write(b"# test")
                paths.append(f.name)

        try:
            for p in paths:
                mgr.add(p)
            files = mgr.get_all()
            self.assertLessEqual(len(files), mgr.max_files)
        finally:
            for p in paths:
                try:
                    os.unlink(p)
                except FileNotFoundError:
                    pass
            mgr.clear()

    def test_deduplication(self):
        from src.utils.recent_files import RecentFilesManager
        mgr = RecentFilesManager()

        with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as f:
            path = f.name
            f.write(b"# test")

        try:
            mgr.add(path)
            mgr.add(path)
            mgr.add(path)
            files = mgr.get_all()
            abs_path = os.path.abspath(path)
            count = files.count(abs_path)
            self.assertEqual(count, 1)
        finally:
            os.unlink(path)


if __name__ == "__main__":
    unittest.main()