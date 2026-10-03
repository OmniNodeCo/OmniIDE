"""Tests for session save/restore and recent folders."""

import unittest
import sys
import os
import json
import tempfile
import shutil

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core import session
from src.utils.recent_folders import RecentFolders


class TestSession(unittest.TestCase):

    def setUp(self):
        self._orig_path = session.SESSION_PATH
        self.tmp = tempfile.mkdtemp()
        session.SESSION_PATH = os.path.join(self.tmp, "session.json")

    def tearDown(self):
        session.SESSION_PATH = self._orig_path
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_save_and_load(self):
        real1 = os.path.join(self.tmp, "b.py")
        real2 = os.path.join(self.tmp, "d.txt")
        for p in (real1, real2):
            with open(p, "w") as f:
                f.write("x")
        ok = session.save_session([real1, real2], active_index=1)
        self.assertTrue(ok)
        files, active = session.load_session()
        self.assertEqual(files, [real1, real2])
        self.assertEqual(active, 1)

    def test_load_missing(self):
        files, active = session.load_session()
        self.assertEqual(files, [])
        self.assertEqual(active, 0)

    def test_load_filters_missing_files(self):
        with tempfile.NamedTemporaryFile(delete=False) as f:
            real = f.name
        try:
            session.save_session([real, "/nonexistent/gone.py"])
            files, active = session.load_session()
            self.assertEqual(files, [os.path.abspath(real)])
            self.assertEqual(active, 0)  # clamped since index 0 is only valid
        finally:
            os.unlink(real)

    def test_clear(self):
        session.save_session(["/x.py"])
        self.assertTrue(session.clear_session())
        self.assertEqual(session.load_session(), ([], 0))

    def test_active_index_clamped(self):
        session.save_session(["/a.py", "/b.py"], active_index=99)
        _files, active = session.load_session()
        self.assertEqual(active, 0)


class TestRecentFolders(unittest.TestCase):

    def setUp(self):
        self._orig_path = os.environ.get("_RF_PATH")
        import src.utils.recent_folders as rf
        self._orig = rf.RECENT_FOLDERS_PATH
        self.tmp = tempfile.mkdtemp()
        rf.RECENT_FOLDERS_PATH = os.path.join(self.tmp, "recent_folders.json")

    def tearDown(self):
        import src.utils.recent_folders as rf
        rf.RECENT_FOLDERS_PATH = self._orig
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_add_and_get(self):
        d = tempfile.mkdtemp()
        try:
            rf = RecentFolders()
            rf.add(d)
            self.assertIn(d, rf.get_all())
        finally:
            shutil.rmtree(d, ignore_errors=True)

    def test_dedup_and_order(self):
        d1 = tempfile.mkdtemp()
        d2 = tempfile.mkdtemp()
        try:
            rf = RecentFolders()
            rf.add(d1)
            rf.add(d2)
            rf.add(d1)  # move to front
            self.assertEqual(rf.get_all(), [d1, d2])
        finally:
            shutil.rmtree(d1, ignore_errors=True)
            shutil.rmtree(d2, ignore_errors=True)

    def test_max_folders(self):
        rf = RecentFolders(max_folders=2)
        dirs = [tempfile.mkdtemp() for _ in range(4)]
        try:
            for d in dirs:
                rf.add(d)
            self.assertEqual(len(rf.get_all()), 2)
            # most recent two are kept
            self.assertEqual(rf.get_all(), [dirs[3], dirs[2]])
        finally:
            for d in dirs:
                shutil.rmtree(d, ignore_errors=True)

    def test_clear(self):
        d = tempfile.mkdtemp()
        try:
            rf = RecentFolders()
            rf.add(d)
            rf.clear()
            self.assertEqual(rf.get_all(), [])
        finally:
            shutil.rmtree(d, ignore_errors=True)

    def test_load_filters_missing(self):
        d = tempfile.mkdtemp()
        try:
            path = __import__("src.utils.recent_folders", fromlist=["RECENT_FOLDERS_PATH"]).RECENT_FOLDERS_PATH
            with open(path, "w") as f:
                json.dump([d, "/nonexistent/folder"], f)
            rf = RecentFolders()
            self.assertEqual(rf.get_all(), [d])
        finally:
            shutil.rmtree(d, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
