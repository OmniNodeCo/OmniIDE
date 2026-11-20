"""ANSI SGR (color) parser for terminal output.

Pure Python — no Qt imports so it can be unit-tested headless.

Supports the common subset emitted by shells and tools:
  0 reset, 1 bold, 4 underline,
  30-37 / 90-97 foreground (basic + bright),
  40-47 background (basic),
  38;5;n / 38;2;r;g;b (256 / truecolor foreground),
  48;5;n (256 background).

Other escape sequences (cursor movement, line clear, hide cursor, ...)
are stripped.
"""

import re

# Basic ANSI palette (indices 0-15)
BASIC = [
    "#000000", "#cd3131", "#0dbc79", "#e5e510",
    "#2472c8", "#bc3fbc", "#11a8cd", "#e5e5e5",
    "#666666", "#f14c4c", "#23d18b", "#f5f543",
    "#3b8eea", "#d670d6", "#29b8db", "#ffffff",
]


class Seg:
    """A run of text with associated attributes."""

    __slots__ = ("text", "fg", "bold", "underline")

    def __init__(self, text, fg=None, bold=False, underline=False):
        self.text = text
        self.fg = fg
        self.bold = bold
        self.underline = underline

    def __repr__(self):
        return f"Seg({self.text!r}, fg={self.fg}, bold={self.bold})"


def color256(n):
    """Convert a 0-255 index to a hex color string."""
    if n < 0:
        n = 0
    if n < 16:
        return BASIC[n]
    if n < 232:
        n -= 16
        r = (n // 36) % 6
        g = (n // 6) % 6
        b = n % 6
        vals = [0, 95, 135, 175, 215, 255]
        return "#%02x%02x%02x" % (vals[r], vals[g], vals[b])
    # grayscale ramp 232-255
    v = 8 + (n - 232) * 10
    return "#%02x%02x%02x" % (v, v, v)


# ESC [ ... <final byte>  (CSI — cursor/SGR/etc.)
_ESC_RE = re.compile(r"\x1b\[[0-9;?]*[ -/]*[@-~]")
# ESC ] ... (BEL | ESC \)  (OSC — window title etc.)
_OSC_RE = re.compile(r"\x1b\][^\x07\x1b]*(?:\x07|\x1b\\)")
# ESC + single char (reverse index, save/restore cursor, mode set/reset, ...)
_SINGLE_RE = re.compile(r"\x1b[78=@<>@-Z\\-_]")


def _split_params(m):
    inner = m.group(0)
    # strip ESC, [, trailing letter
    core = inner[2:-1]
    if not core:
        return [0]
    parts = []
    for p in core.split(";"):
        if p == "":
            parts.append(0)
        else:
            try:
                parts.append(int(p))
            except ValueError:
                parts.append(0)
    return parts


def parse_ansi(text):
    """Parse ANSI text into a list of Seg.

    Supports SGR colors (basic, bright, 256, truecolor) plus bold and
    underline. OSC (window title) and other non-CSI escape sequences are
    stripped.
    """
    segments = []
    fg = None
    bold = False
    underline = False
    buf = []

    def flush():
        if buf:
            t = "".join(buf)
            buf.clear()
            segments.append(Seg(t, fg, bold, underline))

    def apply_sgr(params):
        nonlocal fg, bold, underline
        j = 0
        while j < len(params):
            p = params[j]
            if p == 0:
                fg = None
                bold = False
                underline = False
            elif p == 1:
                bold = True
            elif p == 22:
                bold = False
            elif p == 4:
                underline = True
            elif p == 24:
                underline = False
            elif 30 <= p <= 37:
                fg = BASIC[p - 30]
            elif 90 <= p <= 97:
                fg = BASIC[p - 90 + 8]
            elif p == 39:
                fg = None
            elif p == 38:
                if j + 1 < len(params) and params[j + 1] == 5:
                    if j + 2 < len(params):
                        fg = color256(params[j + 2])
                    j += 2
                elif j + 1 < len(params) and params[j + 1] == 2:
                    if j + 4 < len(params):
                        r, g, b = params[j + 2], params[j + 3], params[j + 4]
                        fg = "#%02x%02x%02x" % (
                            max(0, min(255, r)),
                            max(0, min(255, g)),
                            max(0, min(255, b)),
                        )
                    j += 4
            # 48/40-47: backgrounds ignored by this renderer
            j += 1

    i = 0
    n = len(text)
    while i < n:
        ch = text[i]
        if ch == "\x1b":
            # Non-CSI escapes (OSC title, single-char) are stripped.
            osc = _OSC_RE.match(text, i)
            if osc:
                flush()
                i = osc.end()
                continue
            single = _SINGLE_RE.match(text, i)
            if single:
                flush()
                i = single.end()
                continue
            if i + 1 < n and text[i + 1] == "[":
                m = _ESC_RE.match(text, i)
                if m:
                    seq = m.group(0)
                    flush()  # commit buffered text with OLD attributes
                    if seq.endswith("m"):
                        apply_sgr(_split_params(m))
                    i = m.end()
                    continue
        buf.append(ch)
        i += 1
    flush()
    return segments


def render_html(segments, base_color=None):
    """Render Seg list to an HTML fragment for a plain-text widget.

    Spaces are converted to &nbsp; and newlines to <br> so the rich text
    layout preserves terminal formatting.
    """
    import html as _html
    parts = []
    for seg in segments:
        t = _html.escape(seg.text)
        t = t.replace(" ", "&nbsp;")
        t = t.replace("\t", "&nbsp;&nbsp;&nbsp;&nbsp;")
        t = t.replace("\r\n", "\n").replace("\r", "\n")
        t = t.replace("\n", "<br>")
        color = seg.fg or base_color or "#a6e3a1"
        style = f'color:{color};'
        if seg.bold:
            style += "font-weight:bold;"
        inner = f"<span style='{style}'>{t}</span>" if seg.text else ""
        if seg.underline and seg.text:
            inner = f"<span style='text-decoration:underline;{style}'>{t}</span>"
        parts.append(inner)
    return "".join(parts)


def strip_ansi(text):
    """Remove all ANSI escape sequences (CSI, OSC, single-char)."""
    text = _OSC_RE.sub("", text)
    text = _ESC_RE.sub("", text)
    text = _SINGLE_RE.sub("", text)
    return text
