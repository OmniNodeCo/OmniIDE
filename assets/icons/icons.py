"""
SVG Icon definitions for OmniIDE.
Each icon is stored as an SVG string and converted to PhotoImage at runtime.
"""

# All icons are 16x16 viewBox, clean flat design, Catppuccin-inspired colors

ICONS = {

    # ── File types ──

    "file": """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="16" height="16">
        <path d="M3 1h7l4 4v10H3V1z" fill="none" stroke="#a6adc8" stroke-width="1.2" stroke-linejoin="round"/>
        <path d="M10 1v4h4" fill="none" stroke="#a6adc8" stroke-width="1.2" stroke-linejoin="round"/>
    </svg>
    """,

    "file_python": """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="16" height="16">
        <path d="M3 1h7l4 4v10H3V1z" fill="#1e1e2e" stroke="#89b4fa" stroke-width="1" stroke-linejoin="round"/>
        <path d="M10 1v4h4" fill="none" stroke="#89b4fa" stroke-width="1" stroke-linejoin="round"/>
        <text x="5" y="12" font-family="monospace" font-size="6" font-weight="bold" fill="#89b4fa">Py</text>
    </svg>
    """,

    "file_javascript": """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="16" height="16">
        <path d="M3 1h7l4 4v10H3V1z" fill="#1e1e2e" stroke="#f9e2af" stroke-width="1" stroke-linejoin="round"/>
        <path d="M10 1v4h4" fill="none" stroke="#f9e2af" stroke-width="1" stroke-linejoin="round"/>
        <text x="5" y="12" font-family="monospace" font-size="6" font-weight="bold" fill="#f9e2af">JS</text>
    </svg>
    """,

    "file_typescript": """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="16" height="16">
        <path d="M3 1h7l4 4v10H3V1z" fill="#1e1e2e" stroke="#74c7ec" stroke-width="1" stroke-linejoin="round"/>
        <path d="M10 1v4h4" fill="none" stroke="#74c7ec" stroke-width="1" stroke-linejoin="round"/>
        <text x="5" y="12" font-family="monospace" font-size="6" font-weight="bold" fill="#74c7ec">TS</text>
    </svg>
    """,

    "file_html": """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="16" height="16">
        <path d="M3 1h7l4 4v10H3V1z" fill="#1e1e2e" stroke="#f38ba8" stroke-width="1" stroke-linejoin="round"/>
        <path d="M10 1v4h4" fill="none" stroke="#f38ba8" stroke-width="1" stroke-linejoin="round"/>
        <text x="3.5" y="12.5" font-family="monospace" font-size="4.5" font-weight="bold" fill="#f38ba8">&lt;/&gt;</text>
    </svg>
    """,

    "file_css": """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="16" height="16">
        <path d="M3 1h7l4 4v10H3V1z" fill="#1e1e2e" stroke="#cba6f7" stroke-width="1" stroke-linejoin="round"/>
        <path d="M10 1v4h4" fill="none" stroke="#cba6f7" stroke-width="1" stroke-linejoin="round"/>
        <text x="4.5" y="12" font-family="monospace" font-size="5" font-weight="bold" fill="#cba6f7">#{ }</text>
    </svg>
    """,

    "file_json": """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="16" height="16">
        <path d="M3 1h7l4 4v10H3V1z" fill="#1e1e2e" stroke="#fab387" stroke-width="1" stroke-linejoin="round"/>
        <path d="M10 1v4h4" fill="none" stroke="#fab387" stroke-width="1" stroke-linejoin="round"/>
        <text x="5" y="12" font-family="monospace" font-size="5" font-weight="bold" fill="#fab387">{ }</text>
    </svg>
    """,

    "file_markdown": """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="16" height="16">
        <path d="M3 1h7l4 4v10H3V1z" fill="#1e1e2e" stroke="#a6e3a1" stroke-width="1" stroke-linejoin="round"/>
        <path d="M10 1v4h4" fill="none" stroke="#a6e3a1" stroke-width="1" stroke-linejoin="round"/>
        <text x="4" y="12" font-family="monospace" font-size="6" font-weight="bold" fill="#a6e3a1">M</text>
    </svg>
    """,

    "file_config": """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="16" height="16">
        <path d="M3 1h7l4 4v10H3V1z" fill="#1e1e2e" stroke="#6c7086" stroke-width="1" stroke-linejoin="round"/>
        <path d="M10 1v4h4" fill="none" stroke="#6c7086" stroke-width="1" stroke-linejoin="round"/>
        <circle cx="8" cy="10" r="2.5" fill="none" stroke="#6c7086" stroke-width="1"/>
        <line x1="8" y1="7" x2="8" y2="7.5" stroke="#6c7086" stroke-width="1"/>
        <line x1="8" y1="12.5" x2="8" y2="13" stroke="#6c7086" stroke-width="1"/>
    </svg>
    """,

    "file_shell": """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="16" height="16">
        <path d="M3 1h7l4 4v10H3V1z" fill="#1e1e2e" stroke="#a6e3a1" stroke-width="1" stroke-linejoin="round"/>
        <path d="M10 1v4h4" fill="none" stroke="#a6e3a1" stroke-width="1" stroke-linejoin="round"/>
        <text x="5" y="12" font-family="monospace" font-size="6" font-weight="bold" fill="#a6e3a1">$_</text>
    </svg>
    """,

    "file_c": """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="16" height="16">
        <path d="M3 1h7l4 4v10H3V1z" fill="#1e1e2e" stroke="#89dceb" stroke-width="1" stroke-linejoin="round"/>
        <path d="M10 1v4h4" fill="none" stroke="#89dceb" stroke-width="1" stroke-linejoin="round"/>
        <text x="5.5" y="12" font-family="monospace" font-size="7" font-weight="bold" fill="#89dceb">C</text>
    </svg>
    """,

    "file_java": """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="16" height="16">
        <path d="M3 1h7l4 4v10H3V1z" fill="#1e1e2e" stroke="#f38ba8" stroke-width="1" stroke-linejoin="round"/>
        <path d="M10 1v4h4" fill="none" stroke="#f38ba8" stroke-width="1" stroke-linejoin="round"/>
        <text x="5.5" y="12" font-family="monospace" font-size="6" font-weight="bold" fill="#f38ba8">J</text>
    </svg>
    """,

    "file_ruby": """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="16" height="16">
        <path d="M3 1h7l4 4v10H3V1z" fill="#1e1e2e" stroke="#f38ba8" stroke-width="1" stroke-linejoin="round"/>
        <path d="M10 1v4h4" fill="none" stroke="#f38ba8" stroke-width="1" stroke-linejoin="round"/>
        <polygon points="8,7 5,12 11,12" fill="#f38ba8" opacity="0.8"/>
    </svg>
    """,

    "file_go": """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="16" height="16">
        <path d="M3 1h7l4 4v10H3V1z" fill="#1e1e2e" stroke="#74c7ec" stroke-width="1" stroke-linejoin="round"/>
        <path d="M10 1v4h4" fill="none" stroke="#74c7ec" stroke-width="1" stroke-linejoin="round"/>
        <text x="4.5" y="12" font-family="monospace" font-size="6" font-weight="bold" fill="#74c7ec">Go</text>
    </svg>
    """,

    "file_rust": """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="16" height="16">
        <path d="M3 1h7l4 4v10H3V1z" fill="#1e1e2e" stroke="#fab387" stroke-width="1" stroke-linejoin="round"/>
        <path d="M10 1v4h4" fill="none" stroke="#fab387" stroke-width="1" stroke-linejoin="round"/>
        <text x="4.5" y="12" font-family="monospace" font-size="6" font-weight="bold" fill="#fab387">Rs</text>
    </svg>
    """,

    "file_php": """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="16" height="16">
        <path d="M3 1h7l4 4v10H3V1z" fill="#1e1e2e" stroke="#cba6f7" stroke-width="1" stroke-linejoin="round"/>
        <path d="M10 1v4h4" fill="none" stroke="#cba6f7" stroke-width="1" stroke-linejoin="round"/>
        <text x="3.5" y="12" font-family="monospace" font-size="5" font-weight="bold" fill="#cba6f7">PHP</text>
    </svg>
    """,

    "file_sql": """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="16" height="16">
        <path d="M3 1h7l4 4v10H3V1z" fill="#1e1e2e" stroke="#f9e2af" stroke-width="1" stroke-linejoin="round"/>
        <path d="M10 1v4h4" fill="none" stroke="#f9e2af" stroke-width="1" stroke-linejoin="round"/>
        <text x="3.5" y="12" font-family="monospace" font-size="5" font-weight="bold" fill="#f9e2af">SQL</text>
    </svg>
    """,

    "file_xml": """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="16" height="16">
        <path d="M3 1h7l4 4v10H3V1z" fill="#1e1e2e" stroke="#fab387" stroke-width="1" stroke-linejoin="round"/>
        <path d="M10 1v4h4" fill="none" stroke="#fab387" stroke-width="1" stroke-linejoin="round"/>
        <text x="3.5" y="12.5" font-family="monospace" font-size="4.5" font-weight="bold" fill="#fab387">&lt;/&gt;</text>
    </svg>
    """,

    "file_text": """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="16" height="16">
        <path d="M3 1h7l4 4v10H3V1z" fill="none" stroke="#6c7086" stroke-width="1.2" stroke-linejoin="round"/>
        <path d="M10 1v4h4" fill="none" stroke="#6c7086" stroke-width="1.2" stroke-linejoin="round"/>
        <line x1="5.5" y1="8" x2="11" y2="8" stroke="#6c7086" stroke-width="0.8"/>
        <line x1="5.5" y1="10" x2="10" y2="10" stroke="#6c7086" stroke-width="0.8"/>
        <line x1="5.5" y1="12" x2="8.5" y2="12" stroke="#6c7086" stroke-width="0.8"/>
    </svg>
    """,

    # ── Folders ──

    "folder_closed": """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="16" height="16">
        <path d="M1.5 3h4.5l1.5 1.5h7v9h-13V3z" fill="#313244" stroke="#f9e2af" stroke-width="1" stroke-linejoin="round"/>
        <path d="M1.5 4.5h13" stroke="#f9e2af" stroke-width="0.5" opacity="0.5"/>
    </svg>
    """,

    "folder_open": """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="16" height="16">
        <path d="M1.5 3h4.5l1.5 1.5h7v2h-11L1 13.5V3z" fill="#313244" stroke="#f9e2af" stroke-width="1" stroke-linejoin="round"/>
        <path d="M1.5 6.5h11l2 7h-11z" fill="#45475a" stroke="#f9e2af" stroke-width="1" stroke-linejoin="round"/>
    </svg>
    """,

    "folder_src": """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="16" height="16">
        <path d="M1.5 3h4.5l1.5 1.5h7v9h-13V3z" fill="#313244" stroke="#89b4fa" stroke-width="1" stroke-linejoin="round"/>
        <text x="4" y="11" font-family="monospace" font-size="4.5" font-weight="bold" fill="#89b4fa">&lt;/&gt;</text>
    </svg>
    """,

    "folder_node_modules": """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="16" height="16">
        <path d="M1.5 3h4.5l1.5 1.5h7v9h-13V3z" fill="#313244" stroke="#a6e3a1" stroke-width="1" stroke-linejoin="round"/>
        <text x="5" y="11" font-family="monospace" font-size="5" font-weight="bold" fill="#a6e3a1">N</text>
    </svg>
    """,

    "folder_git": """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="16" height="16">
        <path d="M1.5 3h4.5l1.5 1.5h7v9h-13V3z" fill="#313244" stroke="#f38ba8" stroke-width="1" stroke-linejoin="round"/>
        <circle cx="8" cy="9.5" r="2.5" fill="none" stroke="#f38ba8" stroke-width="1"/>
    </svg>
    """,

    # ── UI actions ──

    "new_file": """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="16" height="16">
        <path d="M3 1h7l4 4v10H3V1z" fill="none" stroke="#a6e3a1" stroke-width="1.2" stroke-linejoin="round"/>
        <path d="M10 1v4h4" fill="none" stroke="#a6e3a1" stroke-width="1.2" stroke-linejoin="round"/>
        <line x1="8" y1="7" x2="8" y2="13" stroke="#a6e3a1" stroke-width="1.5"/>
        <line x1="5" y1="10" x2="11" y2="10" stroke="#a6e3a1" stroke-width="1.5"/>
    </svg>
    """,

    "open_file": """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="16" height="16">
        <path d="M1.5 3h4.5l1.5 1.5h7v2h-11L1 13.5V3z" fill="none" stroke="#89b4fa" stroke-width="1.2" stroke-linejoin="round"/>
        <path d="M1.5 6.5h11l2 7h-11z" fill="none" stroke="#89b4fa" stroke-width="1.2" stroke-linejoin="round"/>
    </svg>
    """,

    "save": """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="16" height="16">
        <path d="M2 1h10l3 3v11H2V1z" fill="none" stroke="#a6e3a1" stroke-width="1.2" stroke-linejoin="round"/>
        <rect x="4" y="1" width="6" height="4" rx="0.5" fill="none" stroke="#a6e3a1" stroke-width="1"/>
        <rect x="4" y="9" width="8" height="5" rx="0.5" fill="none" stroke="#a6e3a1" stroke-width="1"/>
    </svg>
    """,

    "search": """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="16" height="16">
        <circle cx="6.5" cy="6.5" r="4.5" fill="none" stroke="#f9e2af" stroke-width="1.5"/>
        <line x1="10" y1="10" x2="14.5" y2="14.5" stroke="#f9e2af" stroke-width="1.5" stroke-linecap="round"/>
    </svg>
    """,

    "theme": """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="16" height="16">
        <circle cx="8" cy="8" r="6" fill="none" stroke="#cba6f7" stroke-width="1.2"/>
        <path d="M8 2a6 6 0 0 1 0 12V2z" fill="#cba6f7" opacity="0.7"/>
    </svg>
    """,

    "terminal": """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="16" height="16">
        <rect x="1" y="2" width="14" height="12" rx="2" fill="none" stroke="#a6e3a1" stroke-width="1.2"/>
        <polyline points="4,6 7,8.5 4,11" fill="none" stroke="#a6e3a1" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/>
        <line x1="9" y1="11" x2="12" y2="11" stroke="#a6e3a1" stroke-width="1.3" stroke-linecap="round"/>
    </svg>
    """,

    "close": """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="16" height="16">
        <line x1="4" y1="4" x2="12" y2="12" stroke="#f38ba8" stroke-width="1.5" stroke-linecap="round"/>
        <line x1="12" y1="4" x2="4" y2="12" stroke="#f38ba8" stroke-width="1.5" stroke-linecap="round"/>
    </svg>
    """,

    "clear": """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="16" height="16">
        <rect x="2" y="3" width="12" height="11" rx="1" fill="none" stroke="#a6adc8" stroke-width="1.2"/>
        <line x1="5" y1="7" x2="11" y2="7" stroke="#a6adc8" stroke-width="1" stroke-linecap="round"/>
        <line x1="5" y1="9.5" x2="9" y2="9.5" stroke="#a6adc8" stroke-width="1" stroke-linecap="round"/>
        <line x1="5" y1="12" x2="10" y2="12" stroke="#a6adc8" stroke-width="1" stroke-linecap="round"/>
    </svg>
    """,

    "sidebar": """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="16" height="16">
        <rect x="1" y="2" width="14" height="12" rx="1.5" fill="none" stroke="#89b4fa" stroke-width="1.2"/>
        <line x1="5.5" y1="2" x2="5.5" y2="14" stroke="#89b4fa" stroke-width="1"/>
        <line x1="2.5" y1="5" x2="4.5" y2="5" stroke="#89b4fa" stroke-width="0.8"/>
        <line x1="2.5" y1="7" x2="4.5" y2="7" stroke="#89b4fa" stroke-width="0.8"/>
        <line x1="2.5" y1="9" x2="4.5" y2="9" stroke="#89b4fa" stroke-width="0.8"/>
    </svg>
    """,

    "explorer": """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="16" height="16">
        <path d="M1.5 2h4l1 1.5h8v11h-13V2z" fill="none" stroke="#f9e2af" stroke-width="1.2" stroke-linejoin="round"/>
        <line x1="5" y1="7" x2="11" y2="7" stroke="#f9e2af" stroke-width="0.8"/>
        <line x1="5" y1="9" x2="10" y2="9" stroke="#f9e2af" stroke-width="0.8"/>
        <line x1="5" y1="11" x2="9" y2="11" stroke="#f9e2af" stroke-width="0.8"/>
    </svg>
    """,

    "arrow_left": """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="16" height="16">
        <polyline points="10,3 5,8 10,13" fill="none" stroke="#89b4fa" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>
    """,

    "arrow_right": """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="16" height="16">
        <polyline points="6,3 11,8 6,13" fill="none" stroke="#89b4fa" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>
    """,

    "replace": """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="16" height="16">
        <polyline points="3,5 6,2 9,5" fill="none" stroke="#fab387" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/>
        <line x1="6" y1="2" x2="6" y2="10" stroke="#fab387" stroke-width="1.3" stroke-linecap="round"/>
        <polyline points="13,11 10,14 7,11" fill="none" stroke="#fab387" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/>
        <line x1="10" y1="14" x2="10" y2="6" stroke="#fab387" stroke-width="1.3" stroke-linecap="round"/>
    </svg>
    """,

    "case_sensitive": """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="16" height="16">
        <text x="1" y="13" font-family="sans-serif" font-size="11" font-weight="bold" fill="#89b4fa">Aa</text>
    </svg>
    """,

    "chevron_right": """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="16" height="16">
        <polyline points="5,2 11,8 5,14" fill="none" stroke="#6c7086" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>
    """,

    "chevron_down": """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="16" height="16">
        <polyline points="2,5 8,11 14,5" fill="none" stroke="#6c7086" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>
    """,

    "modified": """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="16" height="16">
        <circle cx="8" cy="8" r="4" fill="#f9e2af"/>
    </svg>
    """,

    "run": """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="16" height="16">
        <polygon points="4,2 14,8 4,14" fill="#a6e3a1" stroke="#a6e3a1" stroke-width="0.5" stroke-linejoin="round"/>
    </svg>
    """,

    "settings": """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="16" height="16">
        <circle cx="8" cy="8" r="2.5" fill="none" stroke="#a6adc8" stroke-width="1.2"/>
        <path d="M8 1v2M8 13v2M1 8h2M13 8h2M3.05 3.05l1.4 1.4M11.55 11.55l1.4 1.4M3.05 12.95l1.4-1.4M11.55 4.45l1.4-1.4"
              stroke="#a6adc8" stroke-width="1.2" stroke-linecap="round"/>
    </svg>
    """,

    "info": """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="16" height="16">
        <circle cx="8" cy="8" r="6.5" fill="none" stroke="#89b4fa" stroke-width="1.2"/>
        <line x1="8" y1="7" x2="8" y2="12" stroke="#89b4fa" stroke-width="1.5" stroke-linecap="round"/>
        <circle cx="8" cy="4.5" r="1" fill="#89b4fa"/>
    </svg>
    """,

    "warning": """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="16" height="16">
        <polygon points="8,1 15,14 1,14" fill="none" stroke="#fab387" stroke-width="1.2" stroke-linejoin="round"/>
        <line x1="8" y1="6" x2="8" y2="10" stroke="#fab387" stroke-width="1.5" stroke-linecap="round"/>
        <circle cx="8" cy="12" r="0.8" fill="#fab387"/>
    </svg>
    """,

    "error": """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="16" height="16">
        <circle cx="8" cy="8" r="6.5" fill="none" stroke="#f38ba8" stroke-width="1.2"/>
        <line x1="5.5" y1="5.5" x2="10.5" y2="10.5" stroke="#f38ba8" stroke-width="1.5" stroke-linecap="round"/>
        <line x1="10.5" y1="5.5" x2="5.5" y2="10.5" stroke="#f38ba8" stroke-width="1.5" stroke-linecap="round"/>
    </svg>
    """,

    "success": """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="16" height="16">
        <circle cx="8" cy="8" r="6.5" fill="none" stroke="#a6e3a1" stroke-width="1.2"/>
        <polyline points="4.5,8 7,10.5 11.5,5.5" fill="none" stroke="#a6e3a1" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>
    """,

    "omni_logo": """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24">
        <circle cx="12" cy="12" r="10" fill="#1e1e2e" stroke="#89b4fa" stroke-width="1.5"/>
        <circle cx="12" cy="12" r="6.5" fill="none" stroke="#cba6f7" stroke-width="1.5"/>
        <text x="7" y="14.5" font-family="monospace" font-size="7" font-weight="bold" fill="#89b4fa">&lt;&gt;</text>
        <circle cx="12" cy="12" r="1.5" fill="#f5c2e7"/>
    </svg>
    """,
}