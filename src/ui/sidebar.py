"""Sidebar with organized tabbed panels — fixed hover buttons."""

import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from src.ui.file_tree import FileTree
from src.ui.extensions_panel import ExtensionsPanel
from src.utils.icon_manager import IconManager
from src.utils.styles import make_round_btn, make_icon_btn


class Sidebar:
    """Left sidebar with tabbed panels."""

    def __init__(self, parent, app):
        self.app = app
        self.visible = True
        self.icon_mgr = IconManager()
        self._icon_refs = []

        self.frame = ttk.Frame(parent, width=app.settings["sidebar_width"])
        self.frame.pack_propagate(False)

        self._build_tab_bar()
        self._build_panels()
        self._switch_panel("explorer")

    def _build_tab_bar(self):
        """Icon tab bar at top."""
        self.tab_bar = ttk.Frame(self.frame)
        self.tab_bar.pack(fill=X, padx=4, pady=(4, 0))

        self.tab_buttons = {}

        tabs = [
            ("explorer", "explorer"),
            ("git", "folder_git"),
            ("extensions", "settings"),
        ]

        for tab_id, icon_name in tabs:
            icon = self.icon_mgr.get(icon_name, 16)
            self._icon_refs.append(icon)

            btn = ttk.Button(
                self.tab_bar,
                image=icon,
                bootstyle="secondary-link",
                command=lambda t=tab_id: self._switch_panel(t),
                padding=(8, 6),
                cursor="hand2",
            )
            btn.pack(side=LEFT, padx=1)

            # Store base style for tab buttons
            btn._base_style = "secondary-link"
            btn._active_style = "info"
            btn._tab_id = tab_id

            self.tab_buttons[tab_id] = btn

        ttk.Separator(self.frame).pack(fill=X, padx=4, pady=(4, 0))

    def _build_panels(self):
        """Build all sidebar panels."""
        self.panels = {}
        self.panels["explorer"] = self._build_explorer()
        self.panels["git"] = self._build_git()

        ext_panel = ExtensionsPanel(self.frame, self.app)
        self.panels["extensions"] = ext_panel.frame

    def _build_explorer(self):
        """File explorer panel."""
        panel = ttk.Frame(self.frame)

        header = ttk.Frame(panel)
        header.pack(fill=X, padx=8, pady=(8, 4))

        explorer_icon = self.icon_mgr.get("explorer", 14)
        self._icon_refs.append(explorer_icon)

        ttk.Label(
            header, text=" EXPLORER",
            image=explorer_icon, compound=LEFT,
            font=("Segoe UI", 9, "bold"),
        ).pack(side=LEFT)

        open_icon = self.icon_mgr.get("open_file", 14)
        make_icon_btn(
            header, open_icon,
            self.app.open_project, "info",
            self._icon_refs,
        ).pack(side=RIGHT)

        ttk.Separator(panel).pack(fill=X, padx=8, pady=4)

        actions = ttk.Frame(panel)
        actions.pack(fill=X, padx=8, pady=(0, 4))

        new_icon = self.icon_mgr.get("new_file", 14)
        make_round_btn(
            actions, "New File", new_icon,
            self.app.file_manager.new_file, "success",
            self._icon_refs,
        ).pack(fill=X, pady=1)

        file_icon = self.icon_mgr.get("file", 14)
        make_round_btn(
            actions, "Open File", file_icon,
            self.app.file_manager.open_file, "info",
            self._icon_refs,
        ).pack(fill=X, pady=1)

        ttk.Separator(panel).pack(fill=X, padx=8, pady=4)

        self.file_tree = FileTree(panel, self.app)
        self.file_tree.frame.pack(fill=BOTH, expand=True, padx=4, pady=4)

        return panel

    def _build_git(self):
        """Git panel with organized sections."""
        panel = ttk.Frame(self.frame)

        header = ttk.Frame(panel)
        header.pack(fill=X, padx=8, pady=(8, 4))

        git_icon = self.icon_mgr.get("folder_git", 14)
        self._icon_refs.append(git_icon)

        ttk.Label(
            header, text=" SOURCE CONTROL",
            image=git_icon, compound=LEFT,
            font=("Segoe UI", 9, "bold"),
        ).pack(side=LEFT)

        ttk.Separator(panel).pack(fill=X, padx=8, pady=4)

        gm = self.app.git_manager

        # Repository section
        ttk.Label(
            panel, text="  Repository",
            font=("Segoe UI", 9, "bold"),
        ).pack(anchor="w", padx=8, pady=(4, 2))

        repo_btns = ttk.Frame(panel)
        repo_btns.pack(fill=X, padx=8, pady=(0, 4))

        make_round_btn(
            repo_btns, "Clone", self.icon_mgr.get("open_file", 14),
            gm.clone_repo, "info", self._icon_refs,
        ).pack(fill=X, pady=1)

        make_round_btn(
            repo_btns, "Init", self.icon_mgr.get("new_file", 14),
            gm.init_repo, "success", self._icon_refs,
        ).pack(fill=X, pady=1)

        make_round_btn(
            repo_btns, "Set Remote", self.icon_mgr.get("settings", 14),
            gm.add_remote, "secondary", self._icon_refs,
        ).pack(fill=X, pady=1)

        ttk.Separator(panel).pack(fill=X, padx=8, pady=4)

        # Changes section
        ttk.Label(
            panel, text="  Changes",
            font=("Segoe UI", 9, "bold"),
        ).pack(anchor="w", padx=8, pady=(4, 2))

        changes_btns = ttk.Frame(panel)
        changes_btns.pack(fill=X, padx=8, pady=(0, 4))

        make_round_btn(
            changes_btns, "Status", self.icon_mgr.get("info", 14),
            gm.git_status, "info", self._icon_refs,
        ).pack(fill=X, pady=1)

        make_round_btn(
            changes_btns, "Diff", self.icon_mgr.get("search", 14),
            gm.git_diff, "warning", self._icon_refs,
        ).pack(fill=X, pady=1)

        make_round_btn(
            changes_btns, "Stage All", self.icon_mgr.get("success", 14),
            gm.git_add_all, "success", self._icon_refs,
        ).pack(fill=X, pady=1)

        ttk.Separator(panel).pack(fill=X, padx=8, pady=4)

        # Commit & Sync section
        ttk.Label(
            panel, text="  Commit & Sync",
            font=("Segoe UI", 9, "bold"),
        ).pack(anchor="w", padx=8, pady=(4, 2))

        commit_btns = ttk.Frame(panel)
        commit_btns.pack(fill=X, padx=8, pady=(0, 4))

        make_round_btn(
            commit_btns, "Commit", self.icon_mgr.get("success", 14),
            gm.git_commit, "success", self._icon_refs,
        ).pack(fill=X, pady=1)

        sync_row = ttk.Frame(commit_btns)
        sync_row.pack(fill=X, pady=1)

        make_round_btn(
            sync_row, "Push", self.icon_mgr.get("arrow_right", 14),
            gm.git_push, "info", self._icon_refs,
        ).pack(side=LEFT, fill=X, expand=True, padx=(0, 2))

        make_round_btn(
            sync_row, "Pull", self.icon_mgr.get("arrow_left", 14),
            gm.git_pull, "info", self._icon_refs,
        ).pack(side=LEFT, fill=X, expand=True, padx=(2, 0))

        ttk.Separator(panel).pack(fill=X, padx=8, pady=4)

        # History section
        ttk.Label(
            panel, text="  History",
            font=("Segoe UI", 9, "bold"),
        ).pack(anchor="w", padx=8, pady=(4, 2))

        history_btns = ttk.Frame(panel)
        history_btns.pack(fill=X, padx=8, pady=(0, 4))

        make_round_btn(
            history_btns, "Log", self.icon_mgr.get("file_text", 14),
            gm.git_log, "secondary", self._icon_refs,
        ).pack(fill=X, pady=1)

        make_round_btn(
            history_btns, "Branches", self.icon_mgr.get("folder_src", 14),
            gm.git_branch, "secondary", self._icon_refs,
        ).pack(fill=X, pady=1)

        return panel

    def _switch_panel(self, panel_id):
        """Switch visible panel and update tab highlights."""
        for pid, panel in self.panels.items():
            panel.pack_forget()

        self.panels[panel_id].pack(fill=BOTH, expand=True)

        # Reset ALL tab buttons to base style, then highlight active
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