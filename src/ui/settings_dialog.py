"""Settings dialog — PyQt6."""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QSpinBox, QCheckBox, QPushButton, QScrollArea, QWidget,
    QFrame, QMessageBox, QLineEdit,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from src.config import APP_NAME, APP_VERSION, DEFAULT_SETTINGS, FONT_OPTIONS, CONFIG_DIR


class SettingsDialog(QDialog):
    """Settings editor dialog."""

    def __init__(self, app):
        super().__init__(app)
        self.app = app
        self.setWindowTitle(f"{APP_NAME} — Settings")
        self.setMinimumSize(600, 500)
        self.resize(650, 550)

        layout = QVBoxLayout(self)
        layout.setSpacing(0)

        # Header
        header = QLabel(f"Settings — v{APP_VERSION}")
        header.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        header.setContentsMargins(16, 12, 16, 8)
        layout.addWidget(header)

        # Search
        self.search = QLineEdit()
        self.search.setPlaceholderText("Filter settings...")
        self.search.setContentsMargins(16, 0, 16, 0)
        self.search.textChanged.connect(self._filter)
        layout.addWidget(self.search)

        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.settings_widget = QWidget()
        self.settings_layout = QVBoxLayout(self.settings_widget)
        self.settings_layout.setSpacing(4)
        self.settings_layout.setContentsMargins(16, 8, 16, 8)

        scroll.setWidget(self.settings_widget)
        layout.addWidget(scroll, 1)

        self.rows = []
        self._build()

        # Footer
        footer = QHBoxLayout()
        footer.setContentsMargins(16, 8, 16, 12)

        reset_btn = QPushButton("Reset Defaults")
        reset_btn.setProperty("cssClass", "danger")
        reset_btn.clicked.connect(self._reset)
        footer.addWidget(reset_btn)

        footer.addStretch()

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        footer.addWidget(close_btn)

        layout.addLayout(footer)

    def _build(self):
        s = self.app.settings

        self._section("Appearance")
        self._combo("Theme", "theme", s["theme"], ["dark", "light"])
        self._combo("Font", "font_family", s["font_family"], FONT_OPTIONS)
        self._spin("Font Size", "font_size", s["font_size"], 8, 32)
        self._check("Highlight Current Line", "highlight_current_line", s.get("highlight_current_line", True))
        self._check("Cursor Blink", "cursor_blink", s.get("cursor_blink", True))

        self._section("Editor")
        self._spin("Tab Size", "tab_size", s["tab_size"], 2, 8)
        self._check("Word Wrap", "word_wrap", s.get("word_wrap", False))
        self._check("Auto Indent", "auto_indent", s.get("auto_indent", True))
        self._check("Line Numbers", "show_line_numbers", s.get("show_line_numbers", True))
        self._check("Auto Save", "auto_save", s.get("auto_save", False))

        self._section("Terminal")
        self._combo("Shell", "default_shell", s.get("default_shell", "auto"),
                    ["auto", "bash", "zsh", "powershell", "cmd", "fish"])

        self._section("Updates")
        self._check("Auto Check Updates", "auto_check_updates", s.get("auto_check_updates", True))
        self._check("Suppress Git Prompt", "suppress_git_prompt", s.get("suppress_git_prompt", False))

        self.settings_layout.addStretch()

    def _section(self, title):
        label = QLabel(title.upper())
        label.setProperty("cssClass", "accent")
        label.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        label.setContentsMargins(0, 12, 0, 4)
        self.settings_layout.addWidget(label)

        sep = QFrame()
        sep.setProperty("cssClass", "separator")
        sep.setFixedHeight(1)
        self.settings_layout.addWidget(sep)

        self.rows.append(("section", title, label, sep))

    def _check(self, label, key, value):
        row = QHBoxLayout()
        lbl = QLabel(label)
        row.addWidget(lbl, 1)

        cb = QCheckBox()
        cb.setChecked(value)
        cb.stateChanged.connect(lambda state: self._on_change(key, bool(state)))
        row.addWidget(cb)

        container = QWidget()
        container.setLayout(row)
        self.settings_layout.addWidget(container)
        self.rows.append(("check", label, container, None))

    def _combo(self, label, key, value, options):
        row = QHBoxLayout()
        lbl = QLabel(label)
        row.addWidget(lbl, 1)

        combo = QComboBox()
        combo.addItems(options)
        combo.setCurrentText(str(value))
        combo.currentTextChanged.connect(lambda v: self._on_change(key, v))
        combo.setFixedWidth(180)
        row.addWidget(combo)

        container = QWidget()
        container.setLayout(row)
        self.settings_layout.addWidget(container)
        self.rows.append(("combo", label, container, None))

    def _spin(self, label, key, value, lo, hi):
        row = QHBoxLayout()
        lbl = QLabel(label)
        row.addWidget(lbl, 1)

        spin = QSpinBox()
        spin.setRange(lo, hi)
        spin.setValue(value)
        spin.valueChanged.connect(lambda v: self._on_change(key, v))
        spin.setFixedWidth(100)
        row.addWidget(spin)

        container = QWidget()
        container.setLayout(row)
        self.settings_layout.addWidget(container)
        self.rows.append(("spin", label, container, None))

    def _on_change(self, key, value):
        self.app.settings[key] = value

        if key == "theme":
            self.app.switch_theme()
        elif key in ("font_family", "font_size"):
            self.app.editor_tabs.apply_font()
        elif key == "word_wrap":
            from PyQt6.QtWidgets import QPlainTextEdit
            mode = (QPlainTextEdit.LineWrapMode.WidgetWidth if value
                    else QPlainTextEdit.LineWrapMode.NoWrap)
            for i in range(self.app.editor_tabs.tabs.count()):
                editor = self.app.editor_tabs.tabs.widget(i)
                if hasattr(editor, "setLineWrapMode"):
                    editor.setLineWrapMode(mode)

        self.app.save_settings()

    def _reset(self):
        result = QMessageBox.question(self, "Reset", "Reset all settings?")
        if result == QMessageBox.StandardButton.Yes:
            self.app.settings = DEFAULT_SETTINGS.copy()
            self.app.save_settings()
            self.app.set_status("Settings reset")
            self.accept()

    def _filter(self, query):
        q = query.lower()
        for rtype, label, widget, extra in self.rows:
            if rtype == "section":
                widget.setVisible(True)
                if extra:
                    extra.setVisible(True)
            elif q and q not in label.lower():
                widget.setVisible(False)
            else:
                widget.setVisible(True)