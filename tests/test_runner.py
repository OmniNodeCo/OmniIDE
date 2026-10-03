"""Tests for the run-file command builder."""

import unittest
import sys
import os
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.runner import (
    build_run_command, runner_for, supported_runners,
)


class TestRunnerFor(unittest.TestCase):

    def test_python_file(self):
        cmd = runner_for("/tmp/x/script.py")
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd[-1], "/tmp/x/script.py")

    def test_unsupported_extension(self):
        self.assertIsNone(runner_for("/tmp/x/thing.xyz"))

    def test_no_path(self):
        self.assertIsNone(runner_for(None))
        self.assertIsNone(runner_for(""))

    def test_supported_runners_nonempty(self):
        runners = supported_runners()
        self.assertIn(".py", runners)
        self.assertIn(".js", runners)
        self.assertIn(".sh", runners)
        self.assertGreater(len(runners), 5)


class TestBuildRunCommand(unittest.TestCase):

    def test_returns_command_and_cwd(self):
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False) as f:
            f.write(b"print(1)")
            path = f.name
        try:
            cmd, cwd = build_run_command(path)
            self.assertIsNotNone(cmd)
            self.assertEqual(cwd, os.path.dirname(path))
            self.assertEqual(cmd[-1], path)
        finally:
            os.unlink(path)

    def test_missing_file(self):
        cmd, cwd = build_run_command("/nonexistent/nope.py")
        self.assertIsNone(cmd)
        self.assertIsNone(cwd)

    def test_unsupported_extension(self):
        with tempfile.NamedTemporaryFile(suffix=".abc", delete=False) as f:
            f.write(b"x")
            path = f.name
        try:
            cmd, cwd = build_run_command(path)
            self.assertIsNone(cmd)
        finally:
            os.unlink(path)

    def test_explicit_cwd(self):
        with tempfile.NamedTemporaryFile(suffix=".sh", delete=False) as f:
            f.write(b"echo hi")
            path = f.name
        try:
            cmd, cwd = build_run_command(path, cwd="/tmp")
            self.assertEqual(cwd, "/tmp")
        finally:
            os.unlink(path)


if __name__ == "__main__":
    unittest.main()
