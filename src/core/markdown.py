"""Minimal, dependency-free Markdown → HTML converter.

Covers the common subset used in README files: headings, paragraphs,
code fences, inline code, bold/italic/strike, links, images, blockquotes,
ordered/unordered lists (with nesting) and GFM-style tables.
"""

from __future__ import annotations

import html
import re


_INLINE_CODE = re.compile(r"`([^`]+)`")
_BOLD = re.compile(r"\*\*([^*]+)\*\*|__([^_]+)__")
_ITALIC = re.compile(r"(?<!\*)\*(?!\*)([^*]+)\*(?!\*)|(?<!_)_(?!_)([^_]+)_(?![A-Za-z])")
_STRIKE = re.compile(r"~~([^~]+)~~")
_LINK = re.compile(r"!?\[([^\]]*)\]\(([^)\s]+)(?:\s+\"([^\"]*)\")?\)")
_AUTOLINK = re.compile(r"(?<![\(\[])(https?://[^\s<]+[^\s<.,;:!?)\]])")


def _escape(text):
    return html.escape(text, quote=False)


def _inline(text):
    """Convert inline markdown to HTML. ``text`` is already escaped."""
    placeholders = []

    def _stash(html_snippet):
        placeholders.append(html_snippet)
        return f"\x00{len(placeholders) - 1}\x00"

    # Protect inline code spans first (no markdown inside code)
    text = _INLINE_CODE.sub(lambda m: _stash(f"<code>{m.group(1)}</code>"), text)

    # Stash explicit links/images so autolinking can't double-convert them
    def _link(m):
        label, target, title = m.group(1), m.group(2), m.group(3)
        safe = html.escape(target, quote=True)
        t = f' title="{html.escape(title, quote=True)}"' if title else ""
        if m.group(0).startswith("!"):
            return _stash(f'<img src="{safe}" alt="{label}"{t}>')
        return _stash(f'<a href="{safe}"{t}>{label}</a>')

    text = _LINK.sub(_link, text)

    text = _BOLD.sub(r"<strong>\1\2</strong>", text)
    text = _ITALIC.sub(r"<em>\1\2</em>", text)
    text = _STRIKE.sub(r"<del>\1</del>", text)

    # Autolink bare URLs (protected snippets are \x00n\x00, no URLs left in them)
    text = _AUTOLINK.sub(lambda m: _stash(f'<a href="{m.group(1)}">{m.group(1)}</a>'), text)

    # Restore placeholders (links may contain code-stash placeholders)
    for _ in range(3):
        text = re.sub(
            r"\x00(\d+)\x00",
            lambda m: placeholders[int(m.group(1))],
            text,
        )
    return text


def _is_table_sep(line):
    s = line.strip()
    return bool(re.fullmatch(r"\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?", s))


def _split_row(line):
    s = line.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|"):
        s = s[:-1]
    return [c.strip() for c in s.split("|")]


def to_html(markdown: str, sanitize_scripts=True) -> str:
    """Convert a markdown document to an HTML fragment."""
    lines = markdown.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    out = []
    i = 0
    n = len(lines)

    while i < n:
        line = lines[i]
        stripped = line.strip()

        # Fenced code block
        m = re.match(r"^(```+|~~~+)", stripped)
        if m:
            fence = m.group(1)[0] * 3
            lang = stripped[m.end():].strip()
            buf = []
            i += 1
            while i < n and not lines[i].strip().startswith(fence):
                buf.append(lines[i])
                i += 1
            i += 1  # skip closing fence
            cls = f' class="language-{html.escape(lang, quote=True)}"' if lang else ""
            code_html = _escape("\n".join(buf))
            out.append(f"<pre><code{cls}>{code_html}</code></pre>")
            continue

        # Heading
        m = re.match(r"^(#{1,6})\s+(.*)$", stripped)
        if m:
            level = len(m.group(1))
            out.append(f"<h{level}>{_inline(_escape(m.group(2)))}</h{level}>")
            i += 1
            continue

        # Horizontal rule
        if re.fullmatch(r"(\*\s*){3,}|(-\s*){3,}|(_\s*){3,}", stripped):
            out.append("<hr>")
            i += 1
            continue

        # Blockquote
        if stripped.startswith(">"):
            buf = []
            while i < n and lines[i].strip().startswith(">"):
                buf.append(re.sub(r"^>\s?", "", lines[i].strip()))
                i += 1
            bq_html = to_html('\n'.join(buf))
            out.append(f"<blockquote>{bq_html}</blockquote>")
            continue

        # Table
        if "|" in line and i + 1 < n and _is_table_sep(lines[i + 1]):
            header = _split_row(line)
            aligns = []
            for cell in _split_row(lines[i + 1]):
                c = cell.strip()
                if c.startswith(":") and c.endswith(":"):
                    aligns.append("center")
                elif c.endswith(":"):
                    aligns.append("right")
                else:
                    aligns.append("left")
            i += 2
            rows = []
            while i < n and "|" in lines[i] and lines[i].strip():
                rows.append(_split_row(lines[i]))
                i += 1
            out.append("<table><thead><tr>")
            for j, cell in enumerate(header):
                a = aligns[j] if j < len(aligns) else "left"
                out.append(f'<th style="text-align:{a}">{_inline(_escape(cell))}</th>')
            out.append("</tr></thead><tbody>")
            for row in rows:
                out.append("<tr>")
                for j, cell in enumerate(row):
                    a = aligns[j] if j < len(aligns) else "left"
                    out.append(f'<td style="text-align:{a}">{_inline(_escape(cell))}</td>')
                out.append("</tr>")
            out.append("</tbody></table>")
            continue

        # Unordered list
        if re.match(r"^\s*[-*+]\s+", line):
            i = _list_block(lines, i, out, ordered=False)
            continue

        # Ordered list
        if re.match(r"^\s*\d+[.)]\s+", line):
            i = _list_block(lines, i, out, ordered=True)
            continue

        # Blank line
        if not stripped:
            i += 1
            continue

        # Paragraph (gather consecutive non-blank, non-special lines)
        buf = [line]
        i += 1
        while i < n:
            s2 = lines[i].strip()
            if (
                not s2
                or s2.startswith("#")
                or s2.startswith(">")
                or s2.startswith("```")
                or s2.startswith("~~~")
                or re.match(r"^[-*+]\s+", s2)
                or re.match(r"^\d+[.)]\s+", s2)
                or "|" in s2
                or re.fullmatch(r"(\*\s*){3,}|(-\s*){3,}|(_\s*){3,}", s2)
            ):
                break
            buf.append(lines[i])
            i += 1
        out.append(f"<p>{_inline(_escape(' '.join(b.strip() for b in buf)))}</p>")

    html_doc = "\n".join(out)
    if sanitize_scripts:
        html_doc = re.sub(r"(?is)<(script|iframe|object|embed)[^>]*>.*?</\1>", "", html_doc)
        html_doc = re.sub(r"\son\w+\s*=\s*(['\"]).*?\1", "", html_doc)
        html_doc = re.sub(r"\son\w+\s*=\s*([^\s>]+)", "", html_doc)
    return html_doc


def _list_block(lines, i, out, ordered):
    """Consume a list starting at lines[i]. Returns the next index."""
    pat = re.compile(r"^(\s*)([-*+]|\d+[.)])\s+(.*)$")
    items = []  # (indent, ordered_flag, content)
    while i < len(lines):
        m = pat.match(lines[i])
        if m and (m.group(2)[0].isdigit()) != ordered:
            # Marker kind changed (e.g. ul -> ol): stop this block
            break
        if not m:
            if not lines[i].strip():
                # Peek: list may continue after blank line
                j = i + 1
                while j < len(lines) and not lines[j].strip():
                    j += 1
                if j < len(lines) and pat.match(lines[j]):
                    i = j
                    continue
                break
            if lines[i].startswith("    ") or lines[i].startswith("\t"):
                # Continuation / nested content of previous item
                if items:
                    items[-1] = (items[-1][0], items[-1][1],
                                 items[-1][2] + " " + lines[i].strip())
                i += 1
                continue
            break
        indent = len(m.group(1).expandtabs(4))
        items.append((indent, ordered, m.group(3)))
        i += 1

    html_list, _ = _render_list(items, 0, 0)
    out.append(html_list)
    return i


def _render_list(items, pos, indent):
    """Render list items at ``indent`` and deeper, nested as needed."""
    ordered = items[pos][1]
    tag = "ol" if ordered else "ul"
    parts = [f"<{tag}>"]
    while pos < len(items) and items[pos][0] >= indent:
        it_indent, it_ordered, content = items[pos]
        if it_indent > indent:
            # Nested list: attach inside the previous <li>
            sub, pos = _render_list(items, pos, it_indent)
            if parts[-1].endswith("</li>"):
                parts[-1] = parts[-1][:-len("</li>")] + sub + "</li>"
            continue
        parts.append(f"<li>{_inline(_escape(content))}</li>")
        pos += 1
    parts.append(f"</{tag}>")
    return "".join(parts), pos


def wrap_page(body_html, title="Preview", css=None):
    """Wrap a fragment into a full HTML page for QTextBrowser."""
    css = css or """
        body { font-family: 'Segoe UI', sans-serif; font-size: 14px;
               line-height: 1.6; color: #cdd6f4; }
        pre { background: #11111b; padding: 12px; border-radius: 6px;
              overflow-x: auto; }
        code { background: #313244; padding: 2px 5px; border-radius: 4px;
               font-family: 'Consolas', monospace; }
        pre code { background: none; padding: 0; }
        a { color: #89b4fa; }
        table { border-collapse: collapse; margin: 8px 0; }
        th, td { border: 1px solid #45475a; padding: 6px 10px; }
        blockquote { border-left: 3px solid #89b4fa; margin: 8px 0;
                     padding: 4px 12px; color: #a6adc8; }
        img { max-width: 100%; }
        h1, h2, h3, h4 { margin-top: 1.2em; }
        hr { border: none; border-top: 1px solid #45475a; margin: 16px 0; }
    """
    return f"<!DOCTYPE html><html><head><meta charset='utf-8'>" \
           f"<title>{html.escape(title)}</title><style>{css}</style></head>" \
           f"<body>{body_html}</body></html>"
