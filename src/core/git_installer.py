"""Detect missing Git and prompt user to install it."""

import sys
import shutil
import webbrowser
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from src.config import GIT_DOWNLOAD_URLS


class GitInstaller:
    """Checks if Git is installed and offers to help install it."""

    def __init__(self, app):
        self.app = app

    def check_and_prompt(self):
        """Check if Git exists. If not, show install prompt."""
        if shutil.which("git"):
            return True

        if self.app.settings.get("suppress_git_prompt", False):
            return False

        self._show_install_dialog()
        return False

    def _show_install_dialog(self):
        """Show a dialog offering to install Git."""
        dialog = tk.Toplevel(self.app.root)
        dialog.title("Git Not Found")
        dialog.geometry("480x380")
        dialog.transient(self.app.root)
        dialog.grab_set()
        dialog.resizable(False, False)

        dialog.update_idletasks()
        x = self.app.root.winfo_rootx() + (self.app.root.winfo_width() - 480) // 2
        y = self.app.root.winfo_rooty() + (self.app.root.winfo_height() - 380) // 2
        dialog.geometry(f"+{x}+{y}")

        c = self.app.colors

        # Header
        header = ttk.Frame(dialog, padding=(24, 20))
        header.pack(fill=X)

        ttk.Label(
            header,
            text="Git is not installed",
            font=("Segoe UI", 18, "bold"),
            foreground=c.get("warning", "#fab387"),
        ).pack(anchor="w")

        ttk.Label(
            header,
            text="Git is required for source control features like\n"
                 "clone, commit, push, pull, and branch management.",
            font=("Segoe UI", 10),
            wraplength=420,
        ).pack(anchor="w", pady=(8, 0))

        ttk.Separator(dialog).pack(fill=X, padx=24)

        # Platform info
        info_frame = ttk.Frame(dialog, padding=(24, 16))
        info_frame.pack(fill=X)

        platform_name = self._get_platform_name()
        platform_key = self._get_platform_key()

        ttk.Label(
            info_frame,
            text=f"Detected platform: {platform_name}",
            font=("Consolas", 10),
            foreground=c.get("accent", "#89b4fa"),
        ).pack(anchor="w")

        if platform_key == "linux":
            ttk.Label(
                info_frame,
                text="Install via your package manager:",
                font=("Segoe UI", 10),
            ).pack(anchor="w", pady=(8, 4))

            commands_frame = ttk.Frame(info_frame)
            commands_frame.pack(fill=X, pady=(0, 4))

            commands = [
                ("Ubuntu/Debian:", "sudo apt install git"),
                ("Fedora:", "sudo dnf install git"),
                ("Arch:", "sudo pacman -S git"),
                ("openSUSE:", "sudo zypper install git"),
            ]

            for label, cmd in commands:
                row = ttk.Frame(commands_frame)
                row.pack(fill=X, pady=1)

                ttk.Label(
                    row, text=label,
                    font=("Segoe UI", 9),
                    foreground=c.get("fg_secondary", "#888"),
                    width=16,
                ).pack(side=LEFT)

                ttk.Label(
                    row, text=cmd,
                    font=("Consolas", 9),
                    foreground=c.get("success", "#a6e3a1"),
                ).pack(side=LEFT)
        else:
            ttk.Label(
                info_frame,
                text="Click the button below to open the download page.",
                font=("Segoe UI", 10),
            ).pack(anchor="w", pady=(8, 0))

        ttk.Separator(dialog).pack(fill=X, padx=24, pady=(4, 0))

        # Suppress checkbox
        check_frame = ttk.Frame(dialog, padding=(24, 8))
        check_frame.pack(fill=X)

        self.suppress_var = tk.BooleanVar(value=False)

        ttk.Checkbutton(
            check_frame,
            text="Don't ask me again",
            variable=self.suppress_var,
            bootstyle="warning-round-toggle",
        ).pack(anchor="w")

        # Buttons
        btn_frame = ttk.Frame(dialog, padding=(24, 12))
        btn_frame.pack(fill=X, side=BOTTOM)

        download_url = GIT_DOWNLOAD_URLS.get(platform_key, "https://git-scm.com/downloads")

        ttk.Button(
            btn_frame,
            text="Download Git",
            bootstyle="success",
            command=lambda: self._on_download(download_url, dialog),
            padding=(16, 8),
            cursor="hand2",
        ).pack(side=LEFT, padx=(0, 8))

        ttk.Button(
            btn_frame,
            text="Open git-scm.com",
            bootstyle="info-outline",
            command=lambda: webbrowser.open("https://git-scm.com"),
            padding=(16, 8),
            cursor="hand2",
        ).pack(side=LEFT, padx=(0, 8))

        ttk.Button(
            btn_frame,
            text="Skip",
            bootstyle="secondary-outline",
            command=lambda: self._on_skip(dialog),
            padding=(16, 8),
            cursor="hand2",
        ).pack(side=RIGHT)

    def _on_download(self, url, dialog):
        """Open download URL and close dialog."""
        webbrowser.open(url)
        self._save_suppress()
        dialog.destroy()
        self.app.set_status("Opening Git download page...")

    def _on_skip(self, dialog):
        """Close dialog without downloading."""
        self._save_suppress()
        dialog.destroy()
        self.app.set_status("Git not installed — some features unavailable")

    def _save_suppress(self):
        """Save the suppress preference."""
        if self.suppress_var.get():
            self.app.settings["suppress_git_prompt"] = True
            self.app.save_settings()

    def _get_platform_key(self):
        if sys.platform == "win32":
            return "win32"
        elif sys.platform == "darwin":
            return "darwin"
        else:
            return "linux"

    def _get_platform_name(self):
        if sys.platform == "win32":
            return "Windows"
        elif sys.platform == "darwin":
            return "macOS"
        else:
            return "Linux"