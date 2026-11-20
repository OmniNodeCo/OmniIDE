"""Tests for the ANSI SGR parser."""

import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.ansi import (
    parse_ansi, render_html, strip_ansi, color256, BASIC,
)


class TestParseAnsi(unittest.TestCase):

    def test_plain_text(self):
        self.assertEqual([s.text for s in parse_ansi("plain")], ["plain"])

    def test_empty(self):
        self.assertEqual(parse_ansi(""), [])

    def test_basic_color_and_reset(self):
        segs = parse_ansi("\x1b[31mred\x1b[0m plain ")
        self.assertEqual(segs[0].text, "red")
        self.assertEqual(segs[0].fg, BASIC[1])
        self.assertIsNone(segs[1].fg)
        self.assertEqual(segs[1].text, " plain ")

    def test_bold_combined(self):
        segs = parse_ansi("\x1b[1;32mbold green\x1b[0m")
        self.assertTrue(segs[0].bold)
        self.assertEqual(segs[0].fg, BASIC[2])

    def test_bright_colors(self):
        segs = parse_ansi("\x1b[91mbright\x1b[0m")
        self.assertEqual(segs[0].fg, BASIC[9])

    def test_256_color(self):
        segs = parse_ansi("\x1b[38;5;208morange\x1b[0m")
        self.assertEqual(segs[0].fg, "#ff8700")

    def test_truecolor(self):
        segs = parse_ansi("\x1b[38;2;255;128;0mrgb\x1b[0m")
        self.assertEqual(segs[0].fg, "#ff8000")

    def test_truecolor_clamped(self):
        segs = parse_ansi("\x1b[38;2;999;0;0mrgb\x1b[0m")
        self.assertEqual(segs[0].fg, "#ff0000")

    def test_reset_reapplied(self):
        # attributes must not leak after reset
        segs = parse_ansi("\x1b[1mbold\x1b[0mnormal")
        self.assertTrue(segs[0].bold)
        self.assertFalse(segs[1].bold)

    def test_non_color_escapes_stripped(self):
        segs = parse_ansi("\x1b[?25lhidden\x1b[?25h")
        self.assertEqual([s.text for s in segs], ["hidden"])

    def test_clear_line_stripped(self):
        self.assertEqual(strip_ansi("\x1b[2K\x1b[Hx"), "x")

    def test_osc_title_bell_stripped(self):
        # window-title sequence: ESC ] 0;user@host:/path BEL
        text = "\x1b]0;user@host:/tmp\x07colored"
        self.assertEqual("".join(s.text for s in parse_ansi(text)), "colored")

    def test_osc_title_st_stripped(self):
        text = "\x1b]2;title\x1b\\plain"
        self.assertEqual("".join(s.text for s in parse_ansi(text)), "plain")

    def test_single_char_escapes_stripped(self):
        text = "\x1bM\x1b8mid\x1b7"
        self.assertEqual("".join(s.text for s in parse_ansi(text)), "mid")

    def test_osc_then_color(self):
        text = "\x1b]0;title\x07" + "\x1b[1;31mERR\x1b[0m ok"
        segs = parse_ansi(text)
        self.assertEqual("".join(s.text for s in segs), "ERR ok")
        self.assertEqual(segs[0].fg, BASIC[1])
        self.assertTrue(segs[0].bold)

    def test_multiple_sequences(self):
        segs = parse_ansi("\x1b[31ma\x1b[32mb\x1b[0mc")
        self.assertEqual([s.fg for s in segs], [BASIC[1], BASIC[2], None])
        self.assertEqual("".join(s.text for s in segs), "abc")


class TestColor256(unittest.TestCase):

    def test_basic_range(self):
        self.assertEqual(color256(0), "#000000")
        self.assertEqual(color256(15), "#ffffff")

    def test_cube_range(self):
        self.assertEqual(color256(16), "#000000")
        self.assertEqual(color256(231), "#ffffff")

    def test_grayscale_range(self):
        self.assertEqual(color256(232), "#080808")
        self.assertEqual(color256(255), "#eeeeee")

    def test_out_of_range_clamped(self):
        self.assertEqual(color256(-5), "#000000")


class TestRenderHtml(unittest.TestCase):

    def test_bold_span(self):
        html = render_html(parse_ansi("\x1b[1;31mERR\x1b[0m ok"))
        self.assertIn("font-weight:bold", html)

    def test_newline_br(self):
        html = render_html(parse_ansi("a\nb"))
        self.assertIn("<br>", html)

    def test_spaces_preserved(self):
        html = render_html(parse_ansi("a  b"))
        self.assertIn("&nbsp;", html)

    def test_html_escaped(self):
        html = render_html(parse_ansi("<script>"))
        self.assertNotIn("<script>", html)
        self.assertIn("&lt;script&gt;", html)


if __name__ == "__main__":
    unittest.main()
