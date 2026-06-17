"""Check for updates from GitHub Releases."""

import json
import threading
import urllib.request
import urllib.error
import webbrowser
import re
import sys

from src.config import APP_VERSION, APP_GITHUB_API, APP_RELEASES_URL, APP_REPO


class Updater:
    """Checks GitHub for new releases and prompts the user."""

    def __init__(self, app):
        self.app = app
        self.latest_version = None
        self.latest_url = None
        self.latest_notes = None
        self.checking = False

    def check_now(self, silent=False):
        """
        Check for updates.
        silent=True means don't show 'up to date' dialog.
        """
        if self.checking:
            return
        self.checking = True

        if not silent:
            self.app.set_status("Checking for updates...")

        def _do_check():
            try:
                result = self._fetch_latest()
                self.app.root.after(
                    0, self._on_check_done, result, silent
                )
            except Exception as e:
                self.app.root.after(
                    0, self._on_check_error, str(e), silent
                )

        threading.Thread(target=_do_check, daemon=True).start()

    def check_on_startup(self):
        """Auto-check on startup if enabled in settings."""
        if self.app.settings.get("auto_check_updates", True):
            # Delay to not block startup
            self.app.root.after(3000, lambda: self.check_now(silent=True))

    def _fetch_latest(self):
        """Fetch latest release info from GitHub API."""
        headers = {
            "User-Agent": f"OmniIDE/{APP_VERSION}",
            "Accept": "application/vnd.github.v3+json",
        }

        req = urllib.request.Request(
            APP_GITHUB_API,
            headers=headers,
        )

        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        tag = data.get("tag_name", "")
        version = tag.lstrip("v")
        html_url = data.get("html_url", APP_RELEASES_URL)
        body = data.get("body", "")
        published = data.get("published_at", "")

        # Get download URLs for each platform
        assets = {}
        for asset in data.get("assets", []):
            name = asset.get("name", "")
            url = asset.get("browser_download_url", "")
            size = asset.get("size", 0)

            if name.endswith(".exe"):
                assets["windows"] = {"url": url, "name": name, "size": size}
            elif "macOS" in name or "darwin" in name:
                assets["macos"] = {"url": url, "name": name, "size": size}
            elif "Linux" in name or "linux" in name:
                assets["linux"] = {"url": url, "name": name, "size": size}

        return {
            "version": version,
            "tag": tag,
            "url": html_url,
            "notes": body,
            "published": published,
            "assets": assets,
        }

    def _on_check_done(self, result, silent):
        """Handle successful update check."""
        self.checking = False
        self.latest_version = result["version"]
        self.latest_url = result["url"]
        self.latest_notes = result["notes"]

        if self._is_newer(result["version"], APP_VERSION):
            self.app.set_status(
                f"Update available: v{result['version']}"
            )
            self._show_update_dialog(result)
        else:
            self.app.set_status("OmniIDE is up to date")
            if not silent:
                self._show_uptodate_dialog()

    def _on_check_error(self, error, silent):
        """Handle update check failure."""
        self.checking = False
        self.app.set_status("Update check failed")

        if not silent:
            from tkinter import messagebox
            messagebox.showwarning(
                "Update Check Failed",
                f"Could not check for updates.\n\n{error}\n\n"
                f"You can check manually at:\n{APP_RELEASES_URL}",
            )

    def _is_newer(self, remote, local):
        """Compare version strings."""
        try:
            remote_parts = [int(x) for x in remote.split(".")]
            local_parts = [int(x) for x in local.split(".")]

            # Pad shorter list
            while len(remote_parts) < len(local_parts):
                remote_parts.append(0)
            while len(local_parts) < len(remote_parts):
                local_parts.append(0)

            return remote_parts > local_parts
        except (ValueError, AttributeError):
            return False

    def _show_update_dialog(self, result):
        """Show update available dialog."""
        import tkinter as tk
        import ttkbootstrap as ttk
        from ttkbootstrap.constants import BOTH, X, LEFT, RIGHT, BOTTOM, Y

        dialog = tk.Toplevel(self.app.root)
        dialog.title("Update Available")
        dialog.geometry("520x480")
        dialog.transient(self.app.root)
        dialog.grab_set()
        dialog.resizable(False, False)

        # Center
        dialog.update_idletasks()
        x = self.app.root.winfo_rootx() + (self.app.root.winfo_width() - 520) // 2
        y = self.app.root.winfo_rooty() + (self.app.root.winfo_height() - 480) // 2
        dialog.geometry(f"+{x}+{y}")

        c = self.app.colors

        # Header
        header = ttk.Frame(dialog, padding=(20, 16))
        header.pack(fill=X)

        ttk.Label(
            header,
            text="Update Available!",
            font=("Segoe UI", 18, "bold"),
            foreground=c.get("accent", "#89b4fa"),
        ).pack(anchor="w")

        ttk.Label(
            header,
            text=f"A new version of OmniIDE is available.",
            font=("Segoe UI", 10),
        ).pack(anchor="w", pady=(4, 0))

        ttk.Separator(dialog).pack(fill=X, padx=20)

        # Version comparison
        ver_frame = ttk.Frame(dialog, padding=(20, 12))
        ver_frame.pack(fill=X)

        ttk.Label(
            ver_frame,
            text=f"Current version:    v{APP_VERSION}",
            font=("Consolas", 11),
        ).pack(anchor="w")

        ttk.Label(
            ver_frame,
            text=f"Latest version:     v{result['version']}",
            font=("Consolas", 11, "bold"),
            foreground=c.get("success", "#a6e3a1"),
        ).pack(anchor="w", pady=(2, 0))

        if result.get("published"):
            pub = result["published"][:10]
            ttk.Label(
                ver_frame,
                text=f"Published:          {pub}",
                font=("Consolas", 10),
                foreground=c.get("fg_secondary", "#888"),
            ).pack(anchor="w", pady=(2, 0))

        ttk.Separator(dialog).pack(fill=X, padx=20, pady=(4, 0))

        # Release notes
        notes_label = ttk.Label(
            dialog,
            text="  Release Notes:",
            font=("Segoe UI", 10, "bold"),
            padding=(20, 8),
        )
        notes_label.pack(anchor="w")

        notes_frame = ttk.Frame(dialog, padding=(20, 0))
        notes_frame.pack(fill=BOTH, expand=True)

        notes_text = tk.Text(
            notes_frame,
            font=("Consolas", 9),
            bg=c.get("terminal_bg", "#11111b"),
            fg=c.get("terminal_fg", "#cdd6f4"),
            relief="flat",
            padx=10,
            pady=8,
            wrap="word",
            height=8,
        )
        notes_scroll = ttk.Scrollbar(
            notes_frame, orient=tk.VERTICAL, command=notes_text.yview
        )
        notes_text.configure(yscrollcommand=notes_scroll.set)
        notes_text.pack(side=LEFT, fill=BOTH, expand=True)
        notes_scroll.pack(side=RIGHT, fill=Y)

        notes_content = result.get("notes", "No release notes available.")
        notes_text.insert("1.0", notes_content)
        notes_text.configure(state="disabled")

        ttk.Separator(dialog).pack(fill=X, padx=20, pady=(8, 0))

        # Buttons
        btn_frame = ttk.Frame(dialog, padding=(20, 12))
        btn_frame.pack(fill=X, side=BOTTOM)

        # Detect current platform
        platform_key = self._get_platform_key()
        platform_asset = result.get("assets", {}).get(platform_key)

        if platform_asset:
            size_mb = platform_asset["size"] / (1024 * 1024)
            dl_text = f"Download ({size_mb:.1f} MB)"
        else:
            dl_text = "Download from GitHub"

        ttk.Button(
            btn_frame,
            text=dl_text,
            bootstyle="success",
            command=lambda: self._download_update(result, platform_asset, dialog),
            padding=(16, 8),
            cursor="hand2",
        ).pack(side=LEFT, padx=(0, 8))

        ttk.Button(
            btn_frame,
            text="View on GitHub",
            bootstyle="info-outline",
            command=lambda: webbrowser.open(result["url"]),
            padding=(16, 8),
            cursor="hand2",
        ).pack(side=LEFT, padx=(0, 8))

        ttk.Button(
            btn_frame,
            text="Later",
            bootstyle="secondary-outline",
            command=dialog.destroy,
            padding=(16, 8),
            cursor="hand2",
        ).pack(side=RIGHT)

    def _show_uptodate_dialog(self):
        """Show 'up to date' dialog."""
        from tkinter import messagebox
        messagebox.showinfo(
            "Up to Date",
            f"OmniIDE v{APP_VERSION}\n\n"
            f"You are running the latest version.\n\n"
            f"No updates available.",
        )

    def _get_platform_key(self):
        """Detect current platform."""
        if sys.platform == "win32":
            return "windows"
        elif sys.platform == "darwin":
            return "macos"
        else:
            return "linux"

    def _download_update(self, result, asset, dialog):
        """Open browser to download the update."""
        if asset and asset.get("url"):
            webbrowser.open(asset["url"])
        else:
            webbrowser.open(result["url"])

        dialog.destroy()
        self.app.set_status("Opening download page...")