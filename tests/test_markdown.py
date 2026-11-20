"""Tests for the dependency-free Markdown converter."""

import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.markdown import to_html, wrap_page


class TestMarkdown(unittest.TestCase):

    def test_headings(self):
        self.assertEqual(to_html("# Hi"), "<h1>Hi</h1>")
        self.assertEqual(to_html("###### Deep"), "<h6>Deep</h6>")

    def test_paragraph(self):
        self.assertEqual(to_html("plain text"), "<p>plain text</p>")

    def test_inline_formatting(self):
        html = to_html("**bold** *italic* `code` ~~strike~~")
        self.assertIn("<strong>bold</strong>", html)
        self.assertIn("<em>italic</em>", html)
        self.assertIn("<code>code</code>", html)
        self.assertIn("<del>strike</del>", html)

    def test_link(self):
        html = to_html("[OmniIDE](https://example.com)")
        self.assertIn('<a href="https://example.com">OmniIDE</a>', html)

    def test_link_with_title(self):
        html = to_html('[x](https://a.io "My title")')
        self.assertIn('title="My title"', html)

    def test_autolink(self):
        html = to_html("visit https://a.io now")
        self.assertIn('<a href="https://a.io">https://a.io</a>', html)

    def test_image(self):
        html = to_html("![logo](x.png)")
        self.assertIn('<img src="x.png" alt="logo">', html)

    def test_code_fence_with_lang(self):
        html = to_html('```python\nprint("hi")\n```')
        self.assertIn('<pre><code class="language-python">', html)
        self.assertIn('print("hi")', html)

    def test_code_fence_plain(self):
        html = to_html("```\nraw <code> text\n```")
        self.assertIn("<pre><code>", html)
        self.assertIn("raw &lt;code&gt; text", html)

    def test_unordered_list(self):
        html = to_html("- one\n- two")
        self.assertIn("<ul>", html)
        self.assertIn("<li>one</li>", html)
        self.assertIn("<li>two</li>", html)

    def test_nested_list(self):
        html = to_html("- one\n- two\n  - nested")
        self.assertIn("<li>two<ul><li>nested</li></ul></li>", html)

    def test_ordered_list(self):
        html = to_html("1. first\n2. second")
        self.assertIn("<ol>", html)
        self.assertIn("<li>first</li>", html)

    def test_ordered_after_unordered(self):
        html = to_html("- a\n- b\n1. one\n2. two")
        self.assertIn("<ul>", html)
        self.assertIn("<ol>", html)

    def test_blockquote(self):
        html = to_html("> quoted")
        self.assertIn("<blockquote>", html)

    def test_horizontal_rule(self):
        self.assertIn("<hr>", to_html("---"))
        self.assertIn("<hr>", to_html("***"))

    def test_table(self):
        md = "| A | B |\n|---|---|\n| 1 | 2 |"
        html = to_html(md)
        self.assertIn("<table>", html)
        self.assertIn("<th style=\"text-align:left\">A</th>", html)
        self.assertIn('<td style="text-align:left">1</td>', html)

    def test_table_alignment(self):
        md = "| A | B | C |\n|:---:|---:|---|\n| 1 | 2 | 3 |"
        html = to_html(md)
        self.assertIn("text-align:center", html)
        self.assertIn("text-align:right", html)
        self.assertIn("text-align:left", html)

    def test_html_escaped(self):
        html = to_html("<script>alert(1)</script>")
        self.assertNotIn("<script", html.lower())
        self.assertIn("&lt;script&gt;", html)

    def test_code_span_not_interpreted(self):
        html = to_html("`code with [x](y) url`")
        self.assertEqual(html, "<p><code>code with [x](y) url</code></p>")

    def test_multiline_document(self):
        md = ("# Title\n\nSome **bold** text.\n\n"
              "- a\n- b\n\n> quote\n\n| H1 | H2 |\n|---|---|\n| c | d |\n")
        html = to_html(md)
        for frag in ["<h1>Title</h1>", "<strong>bold</strong>",
                     "<li>a</li>", "<blockquote>", "<table>"]:
            self.assertIn(frag, html)

    def test_wrap_page(self):
        page = wrap_page("<p>x</p>", "Doc")
        self.assertTrue(page.startswith("<!DOCTYPE html>"))
        self.assertIn("<title>Doc</title>", page)
        self.assertIn("<p>x</p>", page)

    def test_crlf_input(self):
        html = to_html("# A\r\n# B")
        self.assertIn("<h1>A</h1>", html)
        self.assertIn("<h1>B</h1>", html)


if __name__ == "__main__":
    unittest.main()
