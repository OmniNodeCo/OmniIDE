"""Text file helpers: line endings, BOM, encodings.

Pure Python — no Qt imports.
"""

from __future__ import annotations

import codecs
import os

BOM_UTF8 = codecs.BOM_UTF8
BOM_UTF16_LE = codecs.BOM_UTF16_LE
BOM_UTF16_BE = codecs.BOM_UTF16_BE

KNOWN_BOMS = [
    (BOM_UTF8, "utf-8-sig"),
    (BOM_UTF16_LE, "utf-16-le"),
    (BOM_UTF16_BE, "utf-16-be"),
]

# Fallback encodings tried when utf-8 fails
FALLBACK_ENCODINGS = ["utf-8", "latin-1", "cp1252", "utf-16"]


def detect_bom(data: bytes):
    """Return (bom_bytes, encoding_hint) or (None, None)."""
    for bom, enc in KNOWN_BOMS:
        if data.startswith(bom):
            return bom, enc
    return None, None


def detect_encoding(data: bytes):
    """Best-effort encoding name for raw bytes."""
    bom, enc = detect_bom(data)
    if bom:
        return enc
    try:
        data.decode("utf-8")
        return "utf-8"
    except UnicodeDecodeError:
        return "latin-1"


def has_bom(data: bytes) -> bool:
    return detect_bom(data)[0] is not None


def detect_line_ending(text: str) -> str:
    """Return 'CRLF', 'CR', or 'LF' for the dominant line ending."""
    crlf = text.count("\r\n")
    cr = text.count("\r") - crlf
    lf = text.count("\n") - crlf
    if crlf >= lf and crlf >= cr:
        return "CRLF" if crlf else ("CR" if cr else "LF")
    if cr >= lf:
        return "CR"
    return "LF"


def convert_line_ending(text: str, target: str) -> str:
    """Normalize ``text`` to 'lf', 'crlf' or 'cr' (case-insensitive)."""
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    t = target.lower()
    if t == "crlf":
        return normalized.replace("\n", "\r\n")
    if t == "cr":
        return normalized.replace("\n", "\r")
    return normalized


def read_text(path: str):
    """Read a text file robustly.

    Returns (text, encoding, line_ending, bom_bytes_or_None).
    """
    with open(path, "rb") as f:
        data = f.read()
    bom, bom_enc = detect_bom(data)
    if bom:
        try:
            text = data.decode(bom_enc)
            enc = "utf-8-sig" if bom == BOM_UTF8 else bom_enc
            # Strip the decoded BOM char if present
            if text.startswith("\ufeff"):
                text = text[1:]
            return text, enc or "utf-8", detect_line_ending(text), bom
        except (UnicodeDecodeError, LookupError):
            pass
    for enc in FALLBACK_ENCODINGS:
        try:
            text = data.decode(enc)
            break
        except (UnicodeDecodeError, LookupError):
            continue
    else:
        text = data.decode("utf-8", errors="replace")
        enc = "utf-8 (replaced)"
    return text, enc, detect_line_ending(text), None


def write_text(path: str, text: str, encoding: str = "utf-8",
               line_ending: str = "lf", use_bom: bool = False) -> None:
    text = convert_line_ending(text, line_ending)
    enc = encoding
    bom_bytes = b""
    if use_bom and enc == "utf-8":
        bom_bytes = BOM_UTF8
        enc = "utf-8"
    with open(path, "wb") as f:
        f.write(bom_bytes)
        f.write(text.encode(enc, errors="replace"))


def guess_mime(filepath: str) -> str:
    """Very small mime guess for content type display."""
    ext = os.path.splitext(filepath or "")[1].lower()
    return {
        ".py": "text/x-python", ".js": "text/javascript",
        ".ts": "text/typescript", ".html": "text/html",
        ".htm": "text/html", ".css": "text/css", ".json": "application/json",
        ".md": "text/markdown", ".xml": "application/xml",
        ".yaml": "application/yaml", ".yml": "application/yaml",
        ".sh": "text/x-shellscript", ".sql": "text/x-sql",
    }.get(ext, "text/plain")
