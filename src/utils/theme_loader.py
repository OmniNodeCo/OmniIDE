"""Loads theme JSON files."""

import json
import os
from src.config import THEMES_DIR


class ThemeLoader:
    """Loads and provides theme colors."""

    DEFAULT_DARK_COLORS = {
        "bg_primary": "#1e1e2e",
        "bg_secondary": "#181825",
        "bg_tertiary": "#313244",
        "fg_primary": "#cdd6f4",
        "fg_secondary": "#a6adc8",
        "accent": "#89b4fa",
        "accent_hover": "#74c7ec",
        "error": "#f38ba8",
        "warning": "#fab387",
        "success": "#a6e3a1",
        "border": "#45475a",
        "selection": "#45475a",
        "line_highlight": "#252536",
        "editor_bg": "#1e1e2e",
        "editor_fg": "#cdd6f4",
        "sidebar_bg": "#181825",
        "terminal_bg": "#11111b",
        "terminal_fg": "#a6e3a1",
        "tab_active": "#1e1e2e",
        "tab_inactive": "#181825",
        "scrollbar": "#45475a",
    }

    DEFAULT_DARK_SYNTAX = {
        "keyword": "#cba6f7",
        "string": "#a6e3a1",
        "comment": "#6c7086",
        "number": "#fab387",
        "function": "#89b4fa",
        "class": "#f9e2af",
        "operator": "#89dceb",
        "bracket": "#f5c2e7",
        "tag": "#f38ba8",
        "attribute": "#fab387",
        "builtin": "#f5c2e7",
    }

    def __init__(self, theme_name="dark"):
        self.colors = self.DEFAULT_DARK_COLORS.copy()
        self.syntax = self.DEFAULT_DARK_SYNTAX.copy()
        self._load_theme(theme_name)

    def _load_theme(self, theme_name):
        theme_file = os.path.join(THEMES_DIR, f"{theme_name}.json")
        if os.path.exists(theme_file):
            try:
                with open(theme_file, "r") as f:
                    data = json.load(f)
                if "colors" in data:
                    self.colors.update(data["colors"])
                if "syntax" in data:
                    self.syntax.update(data["syntax"])
            except Exception:
                pass