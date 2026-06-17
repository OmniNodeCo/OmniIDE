"""Welcome tab — v1.0.3."""

from src.config import APP_NAME, APP_VERSION, APP_AUTHOR


class WelcomeTab:
    """Welcome screen."""

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

        git_ok = "installed" if self.app.git_manager.has_git() else "NOT FOUND"
        ext_count = len(self.app.extension_manager.get_installed())

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
      Ctrl+G          Go to Line
      Ctrl+/          Toggle Comment
      Ctrl+B          Toggle Sidebar
      Ctrl+`          Toggle Terminal
      Ctrl+Shift+P    Command Palette
      Ctrl+,          Settings
      Ctrl++/-        Zoom In / Out
      Ctrl+0          Reset Zoom
      Ctrl+W          Close Tab

    ---------------------------------------------
{recent_text}
    ---------------------------------------------

    Sidebar Panels:

      [Explorer]      File tree and project browser
      [Git]           Source control (git {git_ok})
      [Extensions]    Browse VS Code Marketplace

    Extensions:       {ext_count} installed

    Terminal:

      Select shell: Bash / PowerShell / CMD / Zsh
      Full interactive shell with history
      Ctrl+C sends interrupt

    Settings:

      File > Settings or Ctrl+,
      Change theme, font, tab size, and more
      Auto-check for updates on startup

    Updates:

      Help > Check for Updates
      Auto-checks on startup (configurable)

    ---------------------------------------------

    Made with care by {APP_AUTHOR}
    https://github.com/OmniNodeCo/OmniIDE

"""