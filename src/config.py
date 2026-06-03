"""Application configuration and constants."""

import os
import sys

APP_NAME = "OmniIDE"
APP_VERSION = "1.0.1"
APP_AUTHOR = "OmniNodeCo"

# Handle PyInstaller bundle paths
if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ASSETS_DIR = os.path.join(BASE_DIR, "assets")
THEMES_DIR = os.path.join(ASSETS_DIR, "themes")

CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".omniide")
RECENT_FILES_PATH = os.path.join(CONFIG_DIR, "recent_files.json")
SETTINGS_PATH = os.path.join(CONFIG_DIR, "settings.json")
EXTENSIONS_DIR = os.path.join(CONFIG_DIR, "extensions")

os.makedirs(CONFIG_DIR, exist_ok=True)
os.makedirs(EXTENSIONS_DIR, exist_ok=True)

# VS Code Marketplace API
VSCODE_MARKETPLACE_URL = "https://marketplace.visualstudio.com/_apis/public/gallery/extensionquery"
VSCODE_MARKETPLACE_VERSION = "7.2-preview.1"

DEFAULT_SETTINGS = {
    "theme": "dark",
    "font_family": "Consolas",
    "font_size": 13,
    "tab_size": 4,
    "show_line_numbers": True,
    "word_wrap": False,
    "auto_indent": True,
    "window_width": 1200,
    "window_height": 750,
    "sidebar_width": 280,
    "terminal_height": 200,
    "max_recent_files": 15,
    "default_shell": "auto",
    "installed_extensions": [],
}

SUPPORTED_EXTENSIONS = {
    ".py": "Python",
    ".js": "JavaScript",
    ".html": "HTML",
    ".htm": "HTML",
    ".css": "CSS",
    ".json": "JSON",
    ".md": "Markdown",
    ".txt": "Text",
    ".xml": "XML",
    ".yaml": "YAML",
    ".yml": "YAML",
    ".toml": "TOML",
    ".ini": "INI",
    ".cfg": "Config",
    ".sh": "Shell",
    ".bat": "Batch",
    ".sql": "SQL",
    ".c": "C",
    ".cpp": "C++",
    ".h": "C Header",
    ".java": "Java",
    ".rb": "Ruby",
    ".php": "PHP",
    ".go": "Go",
    ".rs": "Rust",
    ".ts": "TypeScript",
    ".tsx": "TypeScript React",
    ".jsx": "JavaScript React",
}

FILE_DIALOG_TYPES = [
    ("All Files", "*.*"),
    ("Python", "*.py"),
    ("JavaScript", "*.js"),
    ("HTML", "*.html *.htm"),
    ("CSS", "*.css"),
    ("JSON", "*.json"),
    ("Text", "*.txt"),
    ("Markdown", "*.md"),
]