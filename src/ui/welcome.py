"""Welcome tab shown on startup."""

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from src.config import APP_NAME, APP_VERSION, APP_AUTHOR


class WelcomeTab:
    """Welcome screen displayed on first launch."""

    def __init__(self, app):
        self.app = app

    def show(self):
        welcome_content = self._build_welcome_text()
        tab_id = self.app.tab_manager.new_tab(
            title=f"Welcome to {APP_NAME}",
            content=welcome_content,
        )
        # Make welcome tab read-only feel
        editor = self.app.tab_manager.get_active_editor()
        if editor:
            editor.edit_modified(False)
            editor.modified = False

    def _build_welcome_text(self):
        recent = self.app.recent_files_manager.get_all()
        recent_text = ""
        if recent:
            recent_text = "\n  Recent Files:\n"
            for f in recent[:8]:
                recent_text += f"    • {f}\n"
        else:
            recent_text = "\n  No recent files yet.\n"

        return f"""
  ╔══════════════════════════════════════════════╗
  ║                                              ║
  ║        🚀  Welcome to {APP_NAME}              ║
  ║           v{APP_VERSION} by {APP_AUTHOR}            ║
  ║                                              ║
  ╚══════════════════════════════════════════════╝

  Fast. Modern. Lightweight.
  No Electron. No bloat. Pure speed.

  ─────────────────────────────────────────────

  🏁 Quick Start:

    • Ctrl+N        New File
    • Ctrl+O        Open File
    • Ctrl+S        Save
    • Ctrl+F        Find & Replace
    • Ctrl+B        Toggle Sidebar
    • Ctrl+`        Toggle Terminal
    • Ctrl++/-      Zoom In/Out

  ─────────────────────────────────────────────
{recent_text}
  ─────────────────────────────────────────────

  💡 Tips:

    • Open a folder to see it in the Explorer sidebar
    • Use the built-in terminal for quick commands
    • Switch between dark/light theme from View menu
    • Syntax highlighting for Python, JS, HTML, CSS, JSON

  ─────────────────────────────────────────────

  Made with ❤️ by {APP_AUTHOR}
  https://github.com/OmniNodeCo/OmniIDE

"""