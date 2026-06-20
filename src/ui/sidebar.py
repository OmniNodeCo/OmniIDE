"""Sidebar — VS Code style with tabbed panels, round buttons, organized sections."""

import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from src.ui.file_tree import FileTree
from src.ui.extensions_panel import ExtensionsPanel
from src.utils.icon_manager import IconManager
from src.utils.styles import make_round_btn, make_icon_btn, make_action_row


class Sidebar:
    """Left sidebar with tabbed panels."""

    def __init__(self, parent, app):
        self.app = app
        self.visible = True
        self.icon_mgr = IconManager()
        self._icon_refs = []
        self.active_panel = "explorer"

        self.frame = ttk.Frame(parent, width=app.settings["sidebar_width"])
        self.frame.pack_propagate(False)

        self._build_tab_bar()
        self._build_panels()
        self._switch_panel("explorer")

    def _build_tab_bar(self):
        """VS Code style vertical icon tab bar."""
        self.tab_bar = ttk.Frame(self.frame, padding=(2, 4, 2, 4))
        self.tab_bar.pack(fill=X, padx=0, pady=0)

        self.tab_buttons = {}

        tabs = [
            ("explorer", "explorer", "Explorer"),
            ("git", "folder_git", "Source Control"),
            ("extensions", "settings", "Extensions"),
        ]

        for tab_id, icon_name, tooltip in tabs:
            icon = self.icon_mgr.get(icon_name, 18)
            self._icon_refs.append(icon)

            btn = ttk.Button(
                self.tab_bar,
                image=icon,
                bootstyle="secondary-link",
                command=lambda t=tab_id: self._switch_panel(t),
                padding=(10, 7),
                cursor="hand2",
            )
            btn.pack(side=LEFT, padx=1)

            btn._base_style = "secondary-link"
            btn._active_style = "info"
            btn._tab_id = tab_id

            self.tab_buttons[tab_id] = btn

        ttk.Separator(self.frame).pack(fill=X, padx=0, pady=(2, 0))

    def _build_panels(self):
        """Build all sidebar panels."""
        self.panels = {}
        self.panels["explorer"] = self._build_explorer()
        self.panels["git"] = self._build_git()

        ext_panel = ExtensionsPanel(self.frame, self.app)
        self.panels["extensions"] = ext_panel.frame

    def _section_header(self, parent, icon_name, title):
        """Create a VS Code style section header."""
        header = ttk.Frame(parent, padding=(10, 6, 10, 4))
        header.pack(fill=X)

        icon = self.icon_mgr.get(icon_name, 14)
        self._icon_refs.append(icon)

        ttk.Label(
            header,
            text=f" {title.upper()}",
            image=icon,
            compound=LEFT,
            font=("Segoe UI", 9, "bold"),
            foreground="#a6adc8",
        ).pack(side=LEFT)

        return header

    def _build_explorer(self):
        """File explorer panel."""
        panel = ttk.Frame(self.frame)

        header = self._section_header(panel, "explorer", "Explorer")

        open_icon = self.icon_mgr.get("open_file", 14)
        make_icon_btn(
            header, open_icon,
            self.app.open_project, "info",
            self._icon_refs,
        ).pack(side=RIGHT, padx=2)

        # Action buttons
        actions = ttk.Frame(panel, padding=(8, 4, 8, 4))
        actions.pack(fill=X)

        new_icon = self.icon_mgr.get("new_file", 14)
        make_round_btn(
            actions, "New File", new_icon,
            self.app.file_manager.new_file, "success",
            self._icon_refs, size="small",
        ).pack(fill=X, pady=1)

        file_icon = self.icon_mgr.get("file", 14)
        make_round_btn(
            actions, "Open File", file_icon,
            self.app.file_manager.open_file, "info",
            self._icon_refs, size="small",
        ).pack(fill=X, pady=1)

        ttk.Separator(panel).pack(fill=X, padx=8, pady=4)

        # File tree
        self.file_tree = FileTree(panel, self.app)
        self.file_tree.frame.pack(fill=BOTH, expand=True, padx=2, pady=2)

        return panel

    def _build_git(self):
        """Git panel with VS Code style organized sections."""
        panel = ttk.Frame(self.frame)

        self._section_header(panel, "folder_git", "Source Control")

        gm = self.app.git_manager

        # Repository
        self._mini_header(panel, "Repository")
        repo = ttk.Frame(panel, padding=(8, 2, 8, 4))
        repo.pack(fill=X)

        make_round_btn(
            repo, "Clone", self.icon_mgr.get("open_file", 14),
            gm.clone_repo, "info", self._icon_refs, "small",
        ).pack(fill=X, pady=1)

        make_round_btn(
            repo, "Init", self.icon_mgr.get("new_file", 14),
            gm.init_repo, "success", self._icon_refs, "small",
        ).pack(fill=X, pady=1)

        make_round_btn(
            repo, "Remote", self.icon_mgr.get("settings", 14),
            gm.add_remote, "secondary", self._icon_refs, "small",
        ).pack(fill=X, pady=1)

        ttk.Separator(panel).pack(fill=X, padx=8, pady=4)

        # Changes
        self._mini_header(panel, "Changes")
        changes = ttk.Frame(panel, padding=(8, 2, 8, 4))
        changes.pack(fill=X)

        make_round_btn(
            changes, "Status", self.icon_mgr.get("info", 14),
            gm.git_status, "info", self._icon_refs, "small",
        ).pack(fill=X, pady=1)

        make_round_btn(
            changes, "Diff", self.icon_mgr.get("search", 14),
            gm.git_diff, "warning", self._icon_refs, "small",
        ).pack(fill=X, pady=1)

        make_round_btn(
            changes, "Stage All", self.icon_mgr.get("success", 14),
            gm.git_add_all, "success", self._icon_refs, "small",
        ).pack(fill=X, pady=1)

        ttk.Separator(panel).pack(fill=X, padx=8, pady=4)

        # Commit & Sync
        self._mini_header(panel, "Commit & Sync")
        sync = ttk.Frame(panel, padding=(8, 2, 8, 4))
        sync.pack(fill=X)

        make_round_btn(
            sync, "Commit", self.icon_mgr.get("success", 14),
            gm.git_commit, "success", self._icon_refs, "small",
        ).pack(fill=X, pady=1)

        row = ttk.Frame(sync)
        row.pack(fill=X, pady=1)

        make_round_btn(
            row, "Push", self.icon_mgr.get("arrow_right", 14),
            gm.git_push, "info", self._icon_refs, "small",
        ).pack(side=LEFT, fill=X, expand=True, padx=(0, 2))

        make_round_btn(
            row, "Pull", self.icon_mgr.get("arrow_left", 14),
            gm.git_pull, "info", self._icon_refs, "small",
        ).pack(side=LEFT, fill=X, expand=True, padx=(2, 0))

        ttk.Separator(panel).pack(fill=X, padx=8, pady=4)

        # History
        self._mini_header(panel, "History")
        hist = ttk.Frame(panel, padding=(8, 2, 8, 4))
        hist.pack(fill=X)

        make_round_btn(
            hist, "Log", self.icon_mgr.get("file_text", 14),
            gm.git_log, "secondary", self._icon_refs, "small",
        ).pack(fill=X, pady=1)

        make_round_btn(
            hist, "Branches", self.icon_mgr.get("folder_src", 14),
            gm.git_branch, "secondary", self._icon_refs, "small",
        ).pack(fill=X, pady=1)

        return panel

    def _mini_header(self, parent, text):
        """Small section divider label."""
        ttk.Label(
            parent,
            text=f"  {text}",
            font=("Segoe UI", 8, "bold"),
            foreground="#6c7086",
            padding=(8, 4, 8, 0),
        ).pack(anchor="w")

    def _switch_panel(self, panel_id):
        """Switch visible panel."""
        self.active_panel = panel_id

        for pid, panel in self.panels.items():
            panel.pack_forget()

        self.panels[panel_id].pack(fill=BOTH, expand=True)

        for tid, btn in self.tab_buttons.items():
            if tid == panel_id:
                btn.configure(bootstyle="info")
            else:
                btn.configure(bootstyle="secondary-link")

    def toggle(self):
        if self.visible:
            self.frame.pack_forget()
            self.visible = False
        else:
            self.frame.pack(side=LEFT, fill=Y)
            self.visible = True