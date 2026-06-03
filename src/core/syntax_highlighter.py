"""Syntax highlighting engine."""

import re
import os


class SyntaxHighlighter:
    """Applies syntax highlighting to a Text widget."""

    PYTHON_KEYWORDS = [
        "False", "None", "True", "and", "as", "assert", "async", "await",
        "break", "class", "continue", "def", "del", "elif", "else", "except",
        "finally", "for", "from", "global", "if", "import", "in", "is",
        "lambda", "nonlocal", "not", "or", "pass", "raise", "return",
        "try", "while", "with", "yield",
    ]

    PYTHON_BUILTINS = [
        "print", "len", "range", "int", "str", "float", "list", "dict",
        "set", "tuple", "bool", "type", "isinstance", "input", "open",
        "super", "map", "filter", "zip", "enumerate", "sorted", "reversed",
        "abs", "max", "min", "sum", "any", "all", "hasattr", "getattr",
    ]

    JS_KEYWORDS = [
        "var", "let", "const", "function", "return", "if", "else", "for",
        "while", "do", "switch", "case", "break", "continue", "new",
        "this", "class", "extends", "import", "export", "default", "from",
        "try", "catch", "finally", "throw", "async", "await", "yield",
        "typeof", "instanceof", "in", "of", "delete", "void",
        "true", "false", "null", "undefined",
    ]

    HTML_TAGS = [
        "html", "head", "body", "div", "span", "p", "a", "img", "br", "hr",
        "h1", "h2", "h3", "h4", "h5", "h6", "ul", "ol", "li", "table",
        "tr", "td", "th", "form", "input", "button", "select", "option",
        "textarea", "label", "script", "style", "link", "meta", "title",
        "header", "footer", "nav", "main", "section", "article", "aside",
    ]

    def __init__(self, text_widget, syntax_colors, filepath=None):
        self.text = text_widget
        self.syntax_colors = syntax_colors
        self.filepath = filepath
        self.language = self._detect_language()
        self._configure_tags()

    def _detect_language(self):
        if not self.filepath:
            return "python"
        ext = os.path.splitext(self.filepath)[1].lower()
        mapping = {
            ".py": "python",
            ".js": "javascript", ".jsx": "javascript",
            ".ts": "javascript", ".tsx": "javascript",
            ".html": "html", ".htm": "html",
            ".css": "css",
            ".json": "json",
        }
        return mapping.get(ext, "text")

    def _configure_tags(self):
        for tag in ["keyword", "string", "comment", "number", "function",
                     "class", "operator", "bracket", "builtin", "tag", "attribute"]:
            color = self.syntax_colors.get(tag, "#cccccc")
            self.text.tag_configure(tag, foreground=color)
            self.text.tag_lower(tag)

    def highlight(self):
        """Apply syntax highlighting to the entire document."""
        for tag in ["keyword", "string", "comment", "number", "function",
                     "class", "operator", "bracket", "builtin", "tag", "attribute"]:
            self.text.tag_remove(tag, "1.0", "end")

        content = self.text.get("1.0", "end")
        if not content.strip():
            return

        if self.language == "python":
            self._highlight_python(content)
        elif self.language == "javascript":
            self._highlight_javascript(content)
        elif self.language == "html":
            self._highlight_html(content)
        elif self.language == "css":
            self._highlight_css(content)
        elif self.language == "json":
            self._highlight_json(content)

    def _apply_pattern(self, pattern, tag, content, flags=0):
        for match in re.finditer(pattern, content, flags):
            start = f"1.0+{match.start()}c"
            end = f"1.0+{match.end()}c"
            self.text.tag_add(tag, start, end)

    def _highlight_python(self, content):
        # Strings (triple quotes first, then single/double)
        self._apply_pattern(r'"""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\'', "string", content)
        self._apply_pattern(r'"(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\'', "string", content)

        # Comments
        self._apply_pattern(r'#.*$', "comment", content, re.MULTILINE)

        # Numbers
        self._apply_pattern(r'\b\d+\.?\d*\b', "number", content)

        # Keywords
        kw_pattern = r'\b(' + '|'.join(self.PYTHON_KEYWORDS) + r')\b'
        self._apply_pattern(kw_pattern, "keyword", content)

        # Builtins
        bi_pattern = r'\b(' + '|'.join(self.PYTHON_BUILTINS) + r')\b'
        self._apply_pattern(bi_pattern, "builtin", content)

        # Function definitions
        self._apply_pattern(r'(?<=def\s)\w+', "function", content)

        # Class definitions
        self._apply_pattern(r'(?<=class\s)\w+', "class", content)

        # Decorators
        self._apply_pattern(r'@\w+', "builtin", content)

        # Brackets
        self._apply_pattern(r'[\[\](){}]', "bracket", content)

        # Operators
        self._apply_pattern(r'[+\-*/%=<>!&|^~]', "operator", content)

    def _highlight_javascript(self, content):
        self._apply_pattern(r'`[\s\S]*?`', "string", content)
        self._apply_pattern(r'"(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\'', "string", content)
        self._apply_pattern(r'//.*$', "comment", content, re.MULTILINE)
        self._apply_pattern(r'/\*[\s\S]*?\*/', "comment", content)
        self._apply_pattern(r'\b\d+\.?\d*\b', "number", content)

        kw_pattern = r'\b(' + '|'.join(self.JS_KEYWORDS) + r')\b'
        self._apply_pattern(kw_pattern, "keyword", content)

        self._apply_pattern(r'(?<=function\s)\w+', "function", content)
        self._apply_pattern(r'\w+(?=\s*\()', "function", content)
        self._apply_pattern(r'[\[\](){}]', "bracket", content)
        self._apply_pattern(r'[+\-*/%=<>!&|^~?:]', "operator", content)

    def _highlight_html(self, content):
        self._apply_pattern(r'<!--[\s\S]*?-->', "comment", content)
        self._apply_pattern(r'"[^"]*"|\'[^\']*\'', "string", content)

        tag_pattern = r'</?(' + '|'.join(self.HTML_TAGS) + r')\b'
        self._apply_pattern(tag_pattern, "tag", content, re.IGNORECASE)

        self._apply_pattern(r'\b\w+(?==)', "attribute", content)
        self._apply_pattern(r'[<>=/]', "bracket", content)

    def _highlight_css(self, content):
        self._apply_pattern(r'/\*[\s\S]*?\*/', "comment", content)
        self._apply_pattern(r'"[^"]*"|\'[^\']*\'', "string", content)
        self._apply_pattern(r'#[0-9a-fA-F]{3,8}\b', "number", content)
        self._apply_pattern(r'\b\d+\.?\d*(px|em|rem|%|vh|vw|s|ms)?\b', "number", content)
        self._apply_pattern(r'[.#]\w[\w-]*', "keyword", content)
        self._apply_pattern(r'[\w-]+(?=\s*:)', "attribute", content)
        self._apply_pattern(r'[{}();:,]', "bracket", content)

    def _highlight_json(self, content):
        self._apply_pattern(r'"(?:[^"\\]|\\.)*"\s*(?=:)', "keyword", content)
        self._apply_pattern(r':\s*"(?:[^"\\]|\\.)*"', "string", content)
        self._apply_pattern(r'\b\d+\.?\d*\b', "number", content)
        self._apply_pattern(r'\b(true|false|null)\b', "builtin", content)
        self._apply_pattern(r'[{}\[\]:,]', "bracket", content)