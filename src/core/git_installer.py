"""Git install prompt — PyQt6."""

import sys
import shutil
import webbrowser

from PyQt6.QtWidgets import QMessageBox, QCheckBox

from src.config import GIT_DOWNLOAD_URLS


class GitInstaller:
    """Check for Git and prompt to install."""

    def __init__(self, app):
        self.app = app

    def check_and_prompt(self):
        if shutil.which("git"):
            return True
        if self.app.settings.get("suppress_git_prompt", False):
            return False

        self._show_dialog()
        return False

    def _show_dialog(self):
        platform_key = self._get_platform_key()
        url = GIT_DOWNLOAD_URLS.get(platform_key, "https://git-scm.com")

        msg = QMessageBox(self.app)
        msg.setWindowTitle("Git Not Found")
        msg.setText("Git is not installed on this system.")
        msg.setInformativeText(
            "Git is required for source control features.\n\n"
            "Would you like to download Git?"
        )
        msg.setIcon(QMessageBox.Icon.Warning)

        download_btn = msg.addButton("Download Git", QMessageBox.ButtonRole.AcceptRole)
        skip_btn = msg.addButton("Skip", QMessageBox.ButtonRole.RejectRole)

        suppress = QCheckBox("Don't ask again")
        msg.setCheckBox(suppress)

        msg.exec()

        if suppress.isChecked():
            self.app.settings["suppress_git_prompt"] = True
            self.app.save_settings()

        if msg.clickedButton() == download_btn:
            webbrowser.open(url)

    def _get_platform_key(self):
        if sys.platform == "win32":
            return "win32"
        elif sys.platform == "darwin":
            return "darwin"
        return "linux"

    def _get_platform_name(self):
        return {"win32": "Windows", "darwin": "macOS"}.get(sys.platform, "Linux")