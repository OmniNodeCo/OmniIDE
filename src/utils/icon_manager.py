"""
Icon manager — converts SVG strings to tkinter PhotoImages.
Uses a simple SVG-to-bitmap renderer that works without any extra deps.
"""

import tkinter as tk
import io
import re
import base64
import os
import sys
import hashlib


class IconManager:
    """Loads SVG icons and converts them to PhotoImage for use in Tkinter."""

    def __init__(self, scale=1):
        self.scale = scale
        self._cache = {}
        self._icons_data = {}
        self._load_icon_data()

    def _load_icon_data(self):
        """Import icon SVG strings."""
        try:
            from assets.icons.icons import ICONS
            self._icons_data = ICONS
        except ImportError:
            # Fallback: try relative path for PyInstaller bundles
            try:
                base = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
                icons_path = os.path.join(base, "assets", "icons", "icons.py")
                if os.path.exists(icons_path):
                    import importlib.util
                    spec = importlib.util.spec_from_file_location("icons", icons_path)
                    mod = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(mod)
                    self._icons_data = mod.ICONS
            except Exception:
                pass

    def get(self, name, size=16):
        """
        Get a PhotoImage for the named icon.
        Returns a fallback blank image if the icon cannot be rendered.
        """
        cache_key = f"{name}_{size}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        svg_str = self._icons_data.get(name, "")
        if not svg_str:
            img = self._create_fallback(size)
            self._cache[cache_key] = img
            return img

        img = self._svg_to_photoimage(svg_str, size)
        self._cache[cache_key] = img
        return img

    def get_text(self, name):
        """
        Get a plain-text fallback label for the icon.
        Used when PhotoImage rendering is not possible.
        """
        text_map = {
            "file": "[ ]",
            "file_python": "[Py]",
            "file_javascript": "[JS]",
            "file_typescript": "[TS]",
            "file_html": "[<>]",
            "file_css": "[#]",
            "file_json": "[{}]",
            "file_markdown": "[Md]",
            "file_config": "[Cf]",
            "file_shell": "[$]",
            "file_c": "[C]",
            "file_java": "[Jv]",
            "file_ruby": "[Rb]",
            "file_go": "[Go]",
            "file_rust": "[Rs]",
            "file_php": "[Ph]",
            "file_sql": "[Sq]",
            "file_xml": "[Xm]",
            "file_text": "[Tx]",
            "folder_closed": "[+]",
            "folder_open": "[-]",
            "folder_src": "[<>]",
            "new_file": "[+F]",
            "open_file": "[Op]",
            "save": "[Sv]",
            "search": "[?]",
            "theme": "[Th]",
            "terminal": "[>_]",
            "close": "[X]",
            "clear": "[Cl]",
            "sidebar": "[||]",
            "explorer": "[Ex]",
            "arrow_left": "[<]",
            "arrow_right": "[>]",
            "replace": "[Rp]",
            "settings": "[St]",
            "run": "[>>]",
            "info": "[i]",
            "warning": "[!]",
            "error": "[x]",
            "success": "[ok]",
        }
        return text_map.get(name, f"[{name[:2]}]")

    def _svg_to_photoimage(self, svg_str, size):
        """
        Convert SVG string to PhotoImage.
        Tries PIL/Pillow first, falls back to PPM rendering.
        """
        try:
            return self._render_with_pillow(svg_str, size)
        except Exception:
            pass

        try:
            return self._render_with_cairosvg(svg_str, size)
        except Exception:
            pass

        # Final fallback: create a simple colored square
        return self._create_fallback(size)

    def _render_with_pillow(self, svg_str, size):
        """Render using Pillow — handles basic SVG via bitmap conversion."""
        from PIL import Image, ImageDraw

        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Parse basic shapes from SVG
        self._draw_svg_shapes(draw, svg_str, size)

        from PIL import ImageTk
        return ImageTk.PhotoImage(img)

    def _draw_svg_shapes(self, draw, svg_str, size):
        """Simple SVG shape parser — handles circle, rect, line, polyline."""
        scale = size / 16.0

        # Parse circles
        for match in re.finditer(
            r'<circle\s+([^>]+)/>', svg_str
        ):
            attrs = self._parse_attrs(match.group(1))
            cx = float(attrs.get("cx", 0)) * scale
            cy = float(attrs.get("cy", 0)) * scale
            r = float(attrs.get("r", 0)) * scale
            fill = attrs.get("fill", "none")
            stroke = attrs.get("stroke", "none")

            if fill and fill != "none":
                draw.ellipse(
                    [cx - r, cy - r, cx + r, cy + r],
                    fill=self._parse_color(fill),
                )
            if stroke and stroke != "none":
                draw.ellipse(
                    [cx - r, cy - r, cx + r, cy + r],
                    outline=self._parse_color(stroke),
                    width=max(1, int(float(attrs.get("stroke-width", 1)) * scale)),
                )

        # Parse rects
        for match in re.finditer(
            r'<rect\s+([^>]+)/>', svg_str
        ):
            attrs = self._parse_attrs(match.group(1))
            x = float(attrs.get("x", 0)) * scale
            y = float(attrs.get("y", 0)) * scale
            w = float(attrs.get("width", 0)) * scale
            h = float(attrs.get("height", 0)) * scale
            fill = attrs.get("fill", "none")
            stroke = attrs.get("stroke", "none")

            if fill and fill != "none":
                draw.rectangle([x, y, x + w, y + h], fill=self._parse_color(fill))
            if stroke and stroke != "none":
                draw.rectangle(
                    [x, y, x + w, y + h],
                    outline=self._parse_color(stroke),
                    width=max(1, int(float(attrs.get("stroke-width", 1)) * scale)),
                )

        # Parse lines
        for match in re.finditer(
            r'<line\s+([^>]+)/>', svg_str
        ):
            attrs = self._parse_attrs(match.group(1))
            x1 = float(attrs.get("x1", 0)) * scale
            y1 = float(attrs.get("y1", 0)) * scale
            x2 = float(attrs.get("x2", 0)) * scale
            y2 = float(attrs.get("y2", 0)) * scale
            stroke = attrs.get("stroke", "#aaaaaa")

            draw.line(
                [x1, y1, x2, y2],
                fill=self._parse_color(stroke),
                width=max(1, int(float(attrs.get("stroke-width", 1)) * scale)),
            )

        # Parse polylines
        for match in re.finditer(
            r'<polyline\s+([^>]+)/>', svg_str
        ):
            attrs = self._parse_attrs(match.group(1))
            points_str = attrs.get("points", "")
            stroke = attrs.get("stroke", "#aaaaaa")

            points = []
            for pair in points_str.split():
                parts = pair.split(",")
                if len(parts) == 2:
                    points.append((
                        float(parts[0]) * scale,
                        float(parts[1]) * scale,
                    ))

            if len(points) >= 2:
                draw.line(
                    points,
                    fill=self._parse_color(stroke),
                    width=max(1, int(float(attrs.get("stroke-width", 1)) * scale)),
                )

        # Parse polygons
        for match in re.finditer(
            r'<polygon\s+([^>]+)/>', svg_str
        ):
            attrs = self._parse_attrs(match.group(1))
            points_str = attrs.get("points", "")
            fill = attrs.get("fill", "none")
            stroke = attrs.get("stroke", "none")

            points = []
            for pair in points_str.split():
                parts = pair.split(",")
                if len(parts) == 2:
                    points.append((
                        float(parts[0]) * scale,
                        float(parts[1]) * scale,
                    ))

            if len(points) >= 3:
                if fill and fill != "none":
                    draw.polygon(points, fill=self._parse_color(fill))
                if stroke and stroke != "none":
                    draw.polygon(
                        points,
                        outline=self._parse_color(stroke),
                    )

    def _parse_attrs(self, attr_str):
        """Parse XML attributes from a string."""
        attrs = {}
        for match in re.finditer(r'(\w[\w-]*)=["\']([^"\']*)["\']', attr_str):
            attrs[match.group(1)] = match.group(2)
        return attrs

    def _parse_color(self, color_str):
        """Parse a color string, handling url() refs by returning a default."""
        if not color_str or color_str == "none":
            return None
        if color_str.startswith("url("):
            return "#89b4fa"  # default accent
        return color_str

    def _render_with_cairosvg(self, svg_str, size):
        """Render using cairosvg if available."""
        import cairosvg
        from PIL import Image, ImageTk

        png_data = cairosvg.svg2png(
            bytestring=svg_str.encode("utf-8"),
            output_width=size,
            output_height=size,
        )
        img = Image.open(io.BytesIO(png_data))
        return ImageTk.PhotoImage(img)

    def _create_fallback(self, size):
        """Create a minimal placeholder image."""
        try:
            from PIL import Image, ImageTk
            img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
            return ImageTk.PhotoImage(img)
        except ImportError:
            return tk.PhotoImage(width=size, height=size)


# ── Extension to icon name mapping ──

EXTENSION_ICON_MAP = {
    ".py": "file_python",
    ".pyw": "file_python",
    ".pyx": "file_python",
    ".js": "file_javascript",
    ".jsx": "file_javascript",
    ".mjs": "file_javascript",
    ".ts": "file_typescript",
    ".tsx": "file_typescript",
    ".html": "file_html",
    ".htm": "file_html",
    ".css": "file_css",
    ".scss": "file_css",
    ".sass": "file_css",
    ".less": "file_css",
    ".json": "file_json",
    ".md": "file_markdown",
    ".markdown": "file_markdown",
    ".txt": "file_text",
    ".log": "file_text",
    ".yaml": "file_config",
    ".yml": "file_config",
    ".toml": "file_config",
    ".ini": "file_config",
    ".cfg": "file_config",
    ".env": "file_config",
    ".xml": "file_xml",
    ".svg": "file_xml",
    ".sh": "file_shell",
    ".bash": "file_shell",
    ".zsh": "file_shell",
    ".bat": "file_shell",
    ".cmd": "file_shell",
    ".ps1": "file_shell",
    ".c": "file_c",
    ".cpp": "file_c",
    ".cc": "file_c",
    ".h": "file_c",
    ".hpp": "file_c",
    ".java": "file_java",
    ".rb": "file_ruby",
    ".go": "file_go",
    ".rs": "file_rust",
    ".php": "file_php",
    ".sql": "file_sql",
}

FOLDER_ICON_MAP = {
    "src": "folder_src",
    "lib": "folder_src",
    "app": "folder_src",
    "core": "folder_src",
    ".git": "folder_git",
    "node_modules": "folder_node_modules",
}


def get_file_icon_name(filename):
    """Return the icon name for a given filename."""
    ext = os.path.splitext(filename)[1].lower()
    return EXTENSION_ICON_MAP.get(ext, "file")


def get_folder_icon_name(dirname, is_open=False):
    """Return the icon name for a given folder name."""
    name = dirname.lower()
    if name in FOLDER_ICON_MAP:
        return FOLDER_ICON_MAP[name]
    return "folder_open" if is_open else "folder_closed"