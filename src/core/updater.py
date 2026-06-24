"""Update checker — PyQt6."""

import json
import threading
import urllib.request
import webbrowser
import sys

from PyQt6.QtWidgets import QMessageBox

from src.config import APP_VERSION, APP_GITHUB_API, APP_RELEASES_URL


class Updater:
    def __init__(self, app):
        self.app = app
        self.checking = False

    def check_now(self, silent=False):
        if self.checking:
            return
        self.checking = True
        if not silent:
            self.app.set_status("Checking for updates...")

        def _do():
            try:
                result = self._fetch()
                self.checking = False
                if self._is_newer(result["version"], APP_VERSION):
                    self.app.set_status(f"Update: v{result['version']}")
                    if not silent:
                        self._show_update(result)
                else:
                    self.app.set_status("Up to date")
                    if not silent:
                        QMessageBox.information(self.app, "Up to Date", f"OmniIDE v{APP_VERSION}\nNo updates.")
            except Exception as e:
                self.checking = False
                if not silent:
                    QMessageBox.warning(self.app, "Error", f"Update check failed:\n{e}")

        threading.Thread(target=_do, daemon=True).start()

    def check_on_startup(self):
        if self.app.settings.get("auto_check_updates", True):
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(3000, lambda: self.check_now(silent=True))

    def _fetch(self):
        headers = {"User-Agent": f"OmniIDE/{APP_VERSION}", "Accept": "application/vnd.github.v3+json"}
        req = urllib.request.Request(APP_GITHUB_API, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        tag = data.get("tag_name", "").lstrip("v")
        return {
            "version": tag,
            "url": data.get("html_url", APP_RELEASES_URL),
            "notes": data.get("body", ""),
        }

    def _is_newer(self, remote, local):
        try:
            r = [int(x) for x in remote.split(".")]
            l = [int(x) for x in local.split(".")]
            while len(r) < len(l): r.append(0)
            while len(l) < len(r): l.append(0)
            return r > l
        except Exception:
            return False

    def _show_update(self, result):
        reply = QMessageBox.question(
            self.app, "Update Available",
            f"OmniIDE v{result['version']} is available.\n"
            f"Current: v{APP_VERSION}\n\n"
            f"Open download page?",
        )
        if reply == QMessageBox.StandardButton.Yes:
            webbrowser.open(result["url"])

    def _get_platform_key(self):
        if sys.platform == "win32": return "windows"
        elif sys.platform == "darwin": return "macos"
        return "linux"