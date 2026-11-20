"""Tests for text file helpers (EOL, BOM, encodings)."""

import unittest
import sys
import os
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.textfile import (
    detect_line_ending, convert_line_ending, detect_encoding,
    detect_bom, has_bom, read_text, write_text,
)


class TestLineEndings(unittest.TestCase):

    def test_detect_crlf(self):
        self.assertEqual(detect_line_ending("a\r\nb\nc"), "CRLF")

    def test_detect_lf(self):
        self.assertEqual(detect_line_ending("a\nb"), "LF")

    def test_detect_cr(self):
        self.assertEqual(detect_line_ending("a\rb"), "CR")

    def test_empty_is_lf(self):
        self.assertEqual(detect_line_ending(""), "LF")

    def test_convert_to_lf(self):
        self.assertEqual(convert_line_ending("a\r\nb\rc", "lf"), "a\nb\nc")

    def test_convert_to_crlf(self):
        self.assertEqual(convert_line_ending("a\nb", "crlf"), "a\r\nb")

    def test_convert_to_cr(self):
        self.assertEqual(convert_line_ending("a\nb", "cr"), "a\rb")

    def test_convert_idempotent(self):
        self.assertEqual(convert_line_ending("a\r\nb", "lf"), "a\nb")
        self.assertEqual(convert_line_ending("a\nb", "lf"), "a\nb")


class TestBomEncoding(unittest.TestCase):

    def test_utf8(self):
        self.assertEqual(detect_encoding("héllo".encode("utf-8")), "utf-8")

    def test_utf8_bom(self):
        self.assertEqual(detect_encoding(b"\xef\xbb\xbfx"), "utf-8-sig")

    def test_utf16_le_bom(self):
        data = "hi".encode("utf-16-le")
        self.assertEqual(detect_encoding(b"\xff\xfe" + data), "utf-16-le")

    def test_latin1_fallback(self):
        data = "café".encode("latin-1")
        self.assertEqual(detect_encoding(data), "latin-1")

    def test_has_bom(self):
        self.assertTrue(has_bom(b"\xef\xbb\xbfabc"))
        self.assertFalse(has_bom(b"abc"))

    def test_detect_bom(self):
        bom, enc = detect_bom(b"\xef\xbb\xbfabc")
        self.assertEqual(bom, b"\xef\xbb\xbf")
        self.assertEqual(enc, "utf-8-sig")
        self.assertEqual(detect_bom(b"abc"), (None, None))


class TestReadWrite(unittest.TestCase):

    def test_read_plain(self):
        path = os.path.join(tempfile.mkdtemp(), "f.py")
        with open(path, "w") as f:
            f.write("hello\nworld")
        text, enc, eol, bom = read_text(path)
        self.assertEqual(text, "hello\nworld")
        self.assertEqual(enc, "utf-8")
        self.assertEqual(eol, "LF")
        self.assertIsNone(bom)

    def test_read_bom(self):
        path = os.path.join(tempfile.mkdtemp(), "f.txt")
        with open(path, "wb") as f:
            f.write(b"\xef\xbb\xbfhello")
        text, enc, eol, bom = read_text(path)
        self.assertEqual(text, "hello")
        self.assertEqual(enc, "utf-8-sig")
        self.assertEqual(bom, b"\xef\xbb\xbf")

    def test_read_crlf(self):
        path = os.path.join(tempfile.mkdtemp(), "f.txt")
        with open(path, "wb") as f:
            f.write(b"a\r\nb")
        text, enc, eol, bom = read_text(path)
        self.assertEqual(eol, "CRLF")

    def test_write_lf(self):
        path = os.path.join(tempfile.mkdtemp(), "f.txt")
        write_text(path, "a\nb", line_ending="lf")
        with open(path, "rb") as f:
            self.assertEqual(f.read(), b"a\nb")

    def test_write_crlf(self):
        path = os.path.join(tempfile.mkdtemp(), "f.txt")
        write_text(path, "a\nb", line_ending="crlf")
        with open(path, "rb") as f:
            self.assertEqual(f.read(), b"a\r\nb")

    def test_write_bom(self):
        path = os.path.join(tempfile.mkdtemp(), "f.txt")
        write_text(path, "a", use_bom=True)
        with open(path, "rb") as f:
            self.assertEqual(f.read(), b"\xef\xbb\xbfa")


if __name__ == "__main__":
    unittest.main()
