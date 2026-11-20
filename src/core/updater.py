"""Update checker — PyQt6.

Thread-safe: network work happens in a daemon thread, all UI updates are
posted back to the main thread via Qt signals.
"""

import json
import threading
import urllib.request
import webbrowser

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QPlainTextEdit

from src.config import APP_NAME, APP_VERSION, APP_GITHUB_API, APP_RELEASES_URL


class UpdateSignals(QObject):
    """Signals emitted by the updater (safe across threads)."""

    started = pyqtSignal()
    checking = pyqtSignal()
    up_to_date = pyqtSignal()
    update_available = pyqtSignal(dict)   # {version, url, notes, published_at}
    error = pyqtSignal(str)
    finished = pyqtSignal()


class Updater:
    """Checks GitHub Releases for a newer version."""

    def __init__(self, app):
        self.app = app
        self.checking = False
        self.signals = UpdateSignals()
        self.signals.started.connect(self._on_started)
        self.signals.checking.connect(lambda: self.app.set_status("Checking for updates..."))
        self.signals.up_to_date.connect(self._on_up_to_date)
        self.signals.update_available.connect(self._on_update_available)
        self.signals.error.connect(self._on_error)
        self._last_result = None

    # ── Public API ─────────────────────────────────────────────────
    def check_now(self, silent=False):
        if self.checking:
            return
        self.checking = True
        self.signals.started.emit()

        def _do():
            try:
                result = self._fetch()
                self._last_result = result
                if self._is_newer(result["version"], APP_VERSION):
                    self.signals.update_available.emit(result)
                else:
                    self.signals.up_to_date.emit()
            except Exception as e:
                self.signals.error.emit(str(e))
            finally:
                self.checking = False
                self.signals.finished.emit()

        threading.Thread(target=_do, daemon=True).start()

    def check_on_startup(self):
        if self.app.settings.get("auto_check_updates", True):
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(3000, lambda: self.check_now(silent=True))

    def show_release_notes(self):
        """Open the latest release notes dialog (even when up to date)."""
        if self._last_result:
            UpdateDialog(self.app, self._last_result).exec()
        else:
            self.check_now(silent=True)
            self.app.set_status("Fetching latest release notes...")

    # ── Thread-safe UI handlers (main thread) ──────────────────────
    def _on_started(self):
        pass

    def _on_up_to_date(self):
        self.app.set_status(f"Up to date (v{APP_VERSION})")
        self.app.statusbar.set_text(f"Up to date — v{APP_VERSION}")

    def _on_update_available(self, result):
        self.app.set_status(f"Update available: v{result['version']}")
        UpdateDialog(self.app, result).exec()

    def _on_error(self, message):
        self.app.set_status("Update check failed")
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.warning(self.app, "Update Check",
                            f"Could not check for updates:\n{message}")

    # ── Fetching ───────────────────────────────────────────────────
    def _fetch(self):
        headers = {"User-Agent": f"{APP_NAME}/{APP_VERSION}",
                   "Accept": "application/vnd.github.v3+json"}
        req = urllib.request.Request(APP_GITHUB_API, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        tag = data.get("tag_name", "").lstrip("v")
        return {
            "version": tag,
            "url": data.get("html_url", APP_RELEASES_URL),
            "notes": data.get("body", "") or "",
            "published_at": data.get("published_at", ""),
        }

    def _is_newer(self, remote, local):
        try:
            r = [int(x) for x in remote.split(".")]
            l = [int(x) for x in local.split(".")]
            while len(r) < len(l):
                r.append(0)
            while len(l) < len(r):
                l.append(0)
            return r > l
        except Exception:
            return False

    @staticmethod
    def _get_platform_key():
        import sys
        if sys.platform == "win32":
            return "win32"
        if sys.platform == "darwin":
            return "darwin"
        return "linux"


class UpdateDialog(QDialog):
    """Shows an available update with release notes."""

    def __init__(self, app, result):
        super().__init__(app)
        self.app = app
        c = app.colors
        self.setWindowTitle(f"{APP_NAME} — Update Available")
        self.resize(560, 460)

        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        title = QLabel(f"Update to v{result['version']}")
        from PyQt6.QtGui import QFont
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {c['fg_primary']};")
        layout.addWidget(title)

        meta = QLabel(
            f"Current: v{APP_VERSION}   →   Latest: v{result['version']}"
        )
        meta.setStyleSheet(f"color: {c['fg_secondary']}; font-size: 12px;")
        layout.addWidget(meta)

        notes_label = QLabel("Release notes:")
        notes_label.setStyleSheet(f"color: {c['fg_secondary']};")
        layout.addWidget(notes_label)

        self.notes = QPlainTextEdit()
        self.notes.setReadOnly(True)
        self.notes.setPlainText(result.get("notes", "(no notes)") or "(no notes)")
        font = QFont(app.settings.get("font_family", "Consolas"), 11)
        font.setFixedPitch(True)
        self.notes.setFont(font)
        self.notes.setStyleSheet(f"""
            QPlainTextEdit {{
                background-color: {c['bg_primary']};
                color: {c['fg_primary']};
                border: 1px solid {c['border']};
                border-radius: 6px;
                padding: 8px;
            }}
        """)
        layout.addWidget(self.notes, 1)

        row = QHBoxLayout()
        row.addStretch()
        self.download_btn = QPushButton("Open Download Page")
        self.download_btn.setProperty("cssClass", "primary")
        self.download_btn.clicked.connect(lambda: self._open_download(result))
        row.addWidget(self.download_btn)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        row.addWidget(close_btn)
        layout.addLayout(row)

    def _open_download(self, result):
        webbrowser.open(result.get("url", APP_RELEASES_URL))
        self.accept()
