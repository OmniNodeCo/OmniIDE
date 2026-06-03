"""Welcome tab with Git quick start."""

from src.config import APP_NAME, APP_VERSION, APP_AUTHOR


class WelcomeTab:
    """Welcome screen on first launch."""

    def __init__(self, app):
        self.app = app

    def show(self):
        content = self._build_text()
        self.app.tab_manager.new_tab(
            title=f"Welcome to {APP_NAME}",
            content=content,
        )
        editor = self.app.tab_manager.get_active_editor()
        if editor:
            editor.edit_modified(False)
            editor.modified = False

    def _build_text(self):
        recent = self.app.recent_files_manager.get_all()
        if recent:
            recent_text = "\n  Recent Files:\n"
            for f in recent[:8]:
                recent_text += f"    - {f}\n"
        else:
            recent_text = "\n  No recent files yet.\n"

        git_status = "installed" if self.app.git_manager.has_git() else "NOT FOUND"

        return f"""

    =============================================
    
        Welcome to {APP_NAME}  v{APP_VERSION}
        by {APP_AUTHOR}
    
    =============================================

    Fast. Modern. Lightweight.
    No Electron. No bloat. Pure speed.

    ---------------------------------------------

    Keyboard Shortcuts:

      Ctrl+N          New File
      Ctrl+O          Open File
      Ctrl+S          Save
      Ctrl+F          Find & Replace
      Ctrl+B          Toggle Sidebar
      Ctrl+`          Toggle Terminal
      Ctrl++/-        Zoom In/Out
      Ctrl+W          Close Tab

    ---------------------------------------------
{recent_text}
    ---------------------------------------------

    Git Integration (git {git_status}):

      Menu > Git > Clone Repository
      Menu > Git > Init Repository
      Menu > Git > Commit / Push / Pull
      Menu > Git > Set Remote

    Terminal:

      Select shell from dropdown (Bash / PowerShell / CMD)
      Full interactive shell with command history
      Ctrl+C sends interrupt

    ---------------------------------------------

    Tips:

      - Open a folder to see it in Explorer sidebar
      - Use the built-in terminal for real shell commands
      - Switch dark/light theme from toolbar or View menu
      - Syntax highlighting: Python, JS, HTML, CSS, JSON
      - Git: clone, init, commit, push, pull from menu

    ---------------------------------------------

    Made with care by {APP_AUTHOR}
    https://github.com/OmniNodeCo/OmniIDE

"""