"""SVG icon provider for PyQt6 widgets."""

from PyQt6.QtGui import QIcon, QPixmap, QPainter
from PyQt6.QtCore import Qt, QByteArray, QBuffer
from PyQt6.QtSvg import QSvgRenderer


SVGS = {
    "files": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16"><path d="M1.5 2h4l1.5 1.5h7.5v11h-13V2z" fill="none" stroke="#f9e2af" stroke-width="1.2" stroke-linejoin="round"/></svg>""",

    "git": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16"><circle cx="8" cy="4" r="2" fill="none" stroke="#f38ba8" stroke-width="1.2"/><circle cx="8" cy="12" r="2" fill="none" stroke="#f38ba8" stroke-width="1.2"/><line x1="8" y1="6" x2="8" y2="10" stroke="#f38ba8" stroke-width="1.2"/><circle cx="12" cy="8" r="2" fill="none" stroke="#f38ba8" stroke-width="1.2"/><line x1="9.4" y1="5.4" x2="10.6" y2="6.6" stroke="#f38ba8" stroke-width="1.2"/></svg>""",

    "extensions": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16"><rect x="1" y="6" width="5" height="5" rx="1" fill="none" stroke="#cba6f7" stroke-width="1.2"/><rect x="7" y="1" width="5" height="5" rx="1" fill="none" stroke="#cba6f7" stroke-width="1.2"/><rect x="7" y="10" width="5" height="5" rx="1" fill="none" stroke="#cba6f7" stroke-width="1.2"/><line x1="6" y1="8.5" x2="7" y2="8.5" stroke="#cba6f7" stroke-width="1.2"/><line x1="9.5" y1="6" x2="9.5" y2="10" stroke="#cba6f7" stroke-width="1.2"/></svg>""",

    "new_file": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16"><path d="M3 1h7l4 4v10H3V1z" fill="none" stroke="#a6e3a1" stroke-width="1.2" stroke-linejoin="round"/><path d="M10 1v4h4" fill="none" stroke="#a6e3a1" stroke-width="1.2"/><line x1="8" y1="7" x2="8" y2="13" stroke="#a6e3a1" stroke-width="1.5"/><line x1="5" y1="10" x2="11" y2="10" stroke="#a6e3a1" stroke-width="1.5"/></svg>""",

    "open_file": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16"><path d="M1.5 3h4.5l1.5 1.5h7v2h-11L1 13.5V3z" fill="none" stroke="#89b4fa" stroke-width="1.2" stroke-linejoin="round"/><path d="M1.5 6.5h11l2 7h-11z" fill="none" stroke="#89b4fa" stroke-width="1.2" stroke-linejoin="round"/></svg>""",

    "save": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16"><path d="M2 1h10l3 3v11H2V1z" fill="none" stroke="#a6e3a1" stroke-width="1.2" stroke-linejoin="round"/><rect x="4" y="1" width="6" height="4" rx="0.5" fill="none" stroke="#a6e3a1" stroke-width="1"/><rect x="4" y="9" width="8" height="5" rx="0.5" fill="none" stroke="#a6e3a1" stroke-width="1"/></svg>""",

    "search": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16"><circle cx="6.5" cy="6.5" r="4.5" fill="none" stroke="#f9e2af" stroke-width="1.5"/><line x1="10" y1="10" x2="14.5" y2="14.5" stroke="#f9e2af" stroke-width="1.5" stroke-linecap="round"/></svg>""",

    "settings": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16"><circle cx="8" cy="8" r="2.5" fill="none" stroke="#a6adc8" stroke-width="1.2"/><path d="M8 1v2M8 13v2M1 8h2M13 8h2M3.05 3.05l1.4 1.4M11.55 11.55l1.4 1.4M3.05 12.95l1.4-1.4M11.55 4.45l1.4-1.4" stroke="#a6adc8" stroke-width="1.2" stroke-linecap="round"/></svg>""",

    "theme": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16"><circle cx="8" cy="8" r="6" fill="none" stroke="#cba6f7" stroke-width="1.2"/><path d="M8 2a6 6 0 0 1 0 12V2z" fill="#cba6f7" opacity="0.6"/></svg>""",

    "terminal": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16"><rect x="1" y="2" width="14" height="12" rx="2" fill="none" stroke="#a6e3a1" stroke-width="1.2"/><polyline points="4,6 7,8.5 4,11" fill="none" stroke="#a6e3a1" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/><line x1="9" y1="11" x2="12" y2="11" stroke="#a6e3a1" stroke-width="1.3" stroke-linecap="round"/></svg>""",

    "palette": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16"><rect x="2" y="3" width="12" height="10" rx="2" fill="none" stroke="#89b4fa" stroke-width="1.2"/><line x1="5" y1="6" x2="11" y2="6" stroke="#89b4fa" stroke-width="1" stroke-linecap="round"/><line x1="5" y1="8.5" x2="9" y2="8.5" stroke="#89b4fa" stroke-width="1" stroke-linecap="round"/><line x1="5" y1="11" x2="7" y2="11" stroke="#89b4fa" stroke-width="1" stroke-linecap="round"/></svg>""",

    "clone": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16"><rect x="4" y="1" width="8" height="10" rx="1.5" fill="none" stroke="#89b4fa" stroke-width="1.2"/><rect x="2" y="4" width="8" height="10" rx="1.5" fill="none" stroke="#89b4fa" stroke-width="1.2" opacity="0.5"/></svg>""",

    "commit": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16"><circle cx="8" cy="8" r="3" fill="none" stroke="#a6e3a1" stroke-width="1.5"/><line x1="8" y1="1" x2="8" y2="5" stroke="#a6e3a1" stroke-width="1.2"/><line x1="8" y1="11" x2="8" y2="15" stroke="#a6e3a1" stroke-width="1.2"/></svg>""",

    "push": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16"><polyline points="8,2 12,6 8,10" fill="none" stroke="#89b4fa" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/><line x1="4" y1="6" x2="12" y2="6" stroke="#89b4fa" stroke-width="1.5" stroke-linecap="round"/><line x1="4" y1="10" x2="4" y2="14" stroke="#89b4fa" stroke-width="1.2"/><line x1="12" y1="10" x2="12" y2="14" stroke="#89b4fa" stroke-width="1.2"/></svg>""",

    "pull": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16"><polyline points="8,10 4,6 8,2" fill="none" stroke="#89b4fa" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/><line x1="4" y1="6" x2="12" y2="6" stroke="#89b4fa" stroke-width="1.5" stroke-linecap="round"/><line x1="4" y1="10" x2="4" y2="14" stroke="#89b4fa" stroke-width="1.2"/><line x1="12" y1="10" x2="12" y2="14" stroke="#89b4fa" stroke-width="1.2"/></svg>""",

    "diff": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16"><rect x="2" y="2" width="5" height="12" rx="1" fill="none" stroke="#fab387" stroke-width="1.2"/><rect x="9" y="2" width="5" height="12" rx="1" fill="none" stroke="#a6e3a1" stroke-width="1.2"/><line x1="4" y1="6" x2="4" y2="6" stroke="#fab387" stroke-width="2" stroke-linecap="round"/><line x1="12" y1="6" x2="12" y2="6" stroke="#a6e3a1" stroke-width="2" stroke-linecap="round"/></svg>""",

    "branch": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16"><line x1="5" y1="3" x2="5" y2="13" stroke="#cba6f7" stroke-width="1.2"/><line x1="11" y1="3" x2="11" y2="8" stroke="#cba6f7" stroke-width="1.2"/><circle cx="5" cy="3" r="1.5" fill="#cba6f7"/><circle cx="5" cy="13" r="1.5" fill="#cba6f7"/><circle cx="11" cy="3" r="1.5" fill="#cba6f7"/><path d="M11 8c0 3-6 3-6 5" fill="none" stroke="#cba6f7" stroke-width="1.2"/></svg>""",

    "log": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16"><line x1="4" y1="4" x2="12" y2="4" stroke="#a6adc8" stroke-width="1.2" stroke-linecap="round"/><line x1="4" y1="8" x2="10" y2="8" stroke="#a6adc8" stroke-width="1.2" stroke-linecap="round"/><line x1="4" y1="12" x2="8" y2="12" stroke="#a6adc8" stroke-width="1.2" stroke-linecap="round"/><circle cx="2" cy="4" r="1" fill="#89b4fa"/><circle cx="2" cy="8" r="1" fill="#a6e3a1"/><circle cx="2" cy="12" r="1" fill="#f9e2af"/></svg>""",

    "status": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16"><circle cx="8" cy="8" r="6" fill="none" stroke="#89b4fa" stroke-width="1.2"/><line x1="8" y1="5" x2="8" y2="9" stroke="#89b4fa" stroke-width="1.5" stroke-linecap="round"/><circle cx="8" cy="11.5" r="0.8" fill="#89b4fa"/></svg>""",

    "stage": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16"><polyline points="3,8 6.5,11.5 13,4.5" fill="none" stroke="#a6e3a1" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>""",

    "remote": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16"><circle cx="8" cy="8" r="6" fill="none" stroke="#89dceb" stroke-width="1.2"/><ellipse cx="8" cy="8" rx="3" ry="6" fill="none" stroke="#89dceb" stroke-width="1"/><line x1="2" y1="8" x2="14" y2="8" stroke="#89dceb" stroke-width="1"/></svg>""",

    "install": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16"><polyline points="8,2 8,10" fill="none" stroke="#a6e3a1" stroke-width="1.5" stroke-linecap="round"/><polyline points="5,7 8,10 11,7" fill="none" stroke="#a6e3a1" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/><line x1="3" y1="13" x2="13" y2="13" stroke="#a6e3a1" stroke-width="1.5" stroke-linecap="round"/></svg>""",

    "uninstall": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16"><line x1="4" y1="4" x2="12" y2="12" stroke="#f38ba8" stroke-width="1.5" stroke-linecap="round"/><line x1="12" y1="4" x2="4" y2="12" stroke="#f38ba8" stroke-width="1.5" stroke-linecap="round"/></svg>""",

    "refresh": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16"><path d="M13.5 8A5.5 5.5 0 1 1 8 2.5" fill="none" stroke="#89b4fa" stroke-width="1.5" stroke-linecap="round"/><polyline points="10,2.5 8,2.5 8,5" fill="none" stroke="#89b4fa" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>""",
}


def svg_icon(name, size=16):
    """Create a QIcon from an SVG string."""
    svg_str = SVGS.get(name, "")
    if not svg_str:
        return QIcon()

    renderer = QSvgRenderer(QByteArray(svg_str.encode()))
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()
    return QIcon(pixmap)