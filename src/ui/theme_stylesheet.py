"""Generate Qt stylesheet from theme colors."""


def build_stylesheet(c):
    """Build a complete QSS stylesheet from a colors dict."""
    return f"""
    /* ── Global ── */
    QMainWindow, QWidget {{
        background-color: {c['bg_primary']};
        color: {c['fg_primary']};
        font-family: 'Segoe UI', 'Inter', sans-serif;
        font-size: 10pt;
    }}

    /* ── Splitter ── */
    QSplitter::handle {{
        background-color: {c['border']};
    }}
    QSplitter::handle:horizontal {{
        width: 2px;
    }}
    QSplitter::handle:vertical {{
        height: 2px;
    }}

    /* ── Tab Widget ── */
    QTabWidget::pane {{
        border: none;
        background-color: {c['editor_bg']};
    }}
    QTabBar::tab {{
        background-color: {c['bg_secondary']};
        color: {c['fg_secondary']};
        padding: 8px 16px;
        border: none;
        border-bottom: 2px solid transparent;
        font-size: 10pt;
    }}
    QTabBar::tab:selected {{
        background-color: {c['editor_bg']};
        color: {c['fg_primary']};
        border-bottom: 2px solid {c['accent']};
    }}
    QTabBar::tab:hover {{
        background-color: {c['bg_tertiary']};
    }}

    /* ── Editor ── */
    QPlainTextEdit {{
        background-color: {c['editor_bg']};
        color: {c['editor_fg']};
        border: none;
        selection-background-color: {c['selection']};
        padding: 4px;
    }}

    /* ── Buttons ── */
    QPushButton {{
        background-color: {c['bg_tertiary']};
        color: {c['fg_primary']};
        border: 1px solid {c['border']};
        border-radius: 6px;
        padding: 6px 14px;
        font-size: 10pt;
        font-weight: 500;
    }}
    QPushButton:hover {{
        background-color: {c['accent']};
        color: {c['bg_primary']};
        border-color: {c['accent']};
    }}
    QPushButton:pressed {{
        background-color: {c['accent_hover']};
    }}
    QPushButton[cssClass="primary"] {{
        background-color: {c['accent']};
        color: {c['bg_primary']};
        border-color: {c['accent']};
    }}
    QPushButton[cssClass="primary"]:hover {{
        background-color: {c['accent_hover']};
    }}
    QPushButton[cssClass="success"] {{
        background-color: {c['success']};
        color: {c['bg_primary']};
        border-color: {c['success']};
    }}
    QPushButton[cssClass="danger"] {{
        background-color: {c['error']};
        color: {c['bg_primary']};
        border-color: {c['error']};
    }}
    QPushButton[cssClass="icon"] {{
        background-color: transparent;
        border: none;
        border-radius: 4px;
        padding: 4px;
    }}
    QPushButton[cssClass="icon"]:hover {{
        background-color: {c['bg_tertiary']};
    }}

    /* ── Line Edit ── */
    QLineEdit {{
        background-color: {c['bg_tertiary']};
        color: {c['fg_primary']};
        border: 1px solid {c['border']};
        border-radius: 6px;
        padding: 6px 10px;
        font-size: 10pt;
    }}
    QLineEdit:focus {{
        border-color: {c['accent']};
    }}

    /* ── ComboBox ── */
    QComboBox {{
        background-color: {c['bg_tertiary']};
        color: {c['fg_primary']};
        border: 1px solid {c['border']};
        border-radius: 6px;
        padding: 6px 10px;
        font-size: 10pt;
    }}
    QComboBox:hover {{
        border-color: {c['accent']};
    }}
    QComboBox::drop-down {{
        border: none;
        width: 24px;
    }}
    QComboBox QAbstractItemView {{
        background-color: {c['bg_secondary']};
        color: {c['fg_primary']};
        border: 1px solid {c['border']};
        selection-background-color: {c['selection']};
    }}

    /* ── Scrollbar ── */
    QScrollBar:vertical {{
        background-color: {c['bg_secondary']};
        width: 10px;
        border: none;
    }}
    QScrollBar::handle:vertical {{
        background-color: {c['bg_tertiary']};
        border-radius: 5px;
        min-height: 30px;
    }}
    QScrollBar::handle:vertical:hover {{
        background-color: {c['border']};
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}
    QScrollBar:horizontal {{
        background-color: {c['bg_secondary']};
        height: 10px;
        border: none;
    }}
    QScrollBar::handle:horizontal {{
        background-color: {c['bg_tertiary']};
        border-radius: 5px;
        min-width: 30px;
    }}
    QScrollBar::handle:horizontal:hover {{
        background-color: {c['border']};
    }}
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
        width: 0px;
    }}

    /* ── Tree View ── */
    QTreeView {{
        background-color: {c['sidebar_bg']};
        color: {c['fg_primary']};
        border: none;
        font-size: 10pt;
    }}
    QTreeView::item {{
        padding: 4px 8px;
        border-radius: 4px;
    }}
    QTreeView::item:selected {{
        background-color: {c['selection']};
    }}
    QTreeView::item:hover {{
        background-color: {c['bg_tertiary']};
    }}
    QTreeView::branch {{
        background-color: {c['sidebar_bg']};
    }}

    /* ── Labels ── */
    QLabel {{
        color: {c['fg_primary']};
    }}
    QLabel[cssClass="dim"] {{
        color: {c['fg_secondary']};
    }}
    QLabel[cssClass="accent"] {{
        color: {c['accent']};
    }}
    QLabel[cssClass="header"] {{
        font-weight: bold;
        font-size: 9pt;
        color: {c['fg_secondary']};
    }}

    /* ── Separator ── */
    QFrame[cssClass="separator"] {{
        background-color: {c['border']};
        max-height: 1px;
    }}

    /* ── Menu ── */
    QMenuBar {{
        background-color: {c['bg_secondary']};
        color: {c['fg_primary']};
        border-bottom: 1px solid {c['border']};
        font-size: 10pt;
    }}
    QMenuBar::item:selected {{
        background-color: {c['bg_tertiary']};
    }}
    QMenu {{
        background-color: {c['bg_secondary']};
        color: {c['fg_primary']};
        border: 1px solid {c['border']};
        padding: 4px;
    }}
    QMenu::item {{
        padding: 6px 24px;
        border-radius: 4px;
    }}
    QMenu::item:selected {{
        background-color: {c['selection']};
    }}
    QMenu::separator {{
        height: 1px;
        background-color: {c['border']};
        margin: 4px 8px;
    }}

    /* ── Dialog ── */
    QDialog {{
        background-color: {c['bg_primary']};
        color: {c['fg_primary']};
    }}

    /* ── Progress Bar ── */
    QProgressBar {{
        background-color: {c['bg_tertiary']};
        border: none;
        border-radius: 3px;
        height: 6px;
        text-align: center;
    }}
    QProgressBar::chunk {{
        background-color: {c['accent']};
        border-radius: 3px;
    }}

    /* ── CheckBox ── */
    QCheckBox {{
        color: {c['fg_primary']};
        spacing: 8px;
    }}
    QCheckBox::indicator {{
        width: 18px;
        height: 18px;
        border-radius: 4px;
        border: 2px solid {c['border']};
        background-color: {c['bg_tertiary']};
    }}
    QCheckBox::indicator:checked {{
        background-color: {c['accent']};
        border-color: {c['accent']};
    }}

    /* ── Slider ── */
    QSlider::groove:horizontal {{
        height: 4px;
        background-color: {c['bg_tertiary']};
        border-radius: 2px;
    }}
    QSlider::handle:horizontal {{
        background-color: {c['accent']};
        width: 16px;
        height: 16px;
        margin: -6px 0;
        border-radius: 8px;
    }}
    QSlider::handle:horizontal:hover {{
        background-color: {c['accent_hover']};
    }}

    /* ── ToolTip ── */
    QToolTip {{
        background-color: {c['bg_secondary']};
        color: {c['fg_primary']};
        border: 1px solid {c['border']};
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 9pt;
    }}
    """