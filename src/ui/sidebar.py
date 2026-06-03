"""Sidebar with file tree, Git info, and modern buttons."""

import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from src.ui.file_tree import FileTree
from src.utils.icon_manager import IconManager


class Sidebar:
    """Left sidebar with explorer and Git panel."""

    def __init__(self, parent, app):
        self.app = app
        self.visible = True
        self.icon_mgr = IconManager()
        self._icon_refs = []

        self.frame = ttk.Frame(parent, width=app.settings["sidebar_width"])
        self.frame.pack_propagate(False)

        # ── Header ──
        header = ttk.Frame(self.frame)
        header.pack(fill=X, padx=8, pady=(8, 4))

        explorer_icon = self.icon_mgr.get("explorer", 16)
        self._icon_refs.append(explorer_icon)

        ttk.Label(
            header,
            text=" EXPLORER",
            image=explorer_icon,
            compound=LEFT,
            font=("Segoe UI", 10, "bold"),
        ).pack(side=LEFT)

        open_icon = self.icon_mgr.get("open_file", 16)
        self._icon_refs.append(open_icon)

        ttk.Button(
            header, image=open_icon,
            bootstyle="info-link",
            command=app.open_project,
        ).pack(side=RIGHT)

        ttk.Separator(self.frame).pack(fill=X, padx=8, pady=4)

        # ── Quick actions ──
        actions = ttk.Frame(self.frame)
        actions.pack(fill=X, padx=8, pady=(0, 4))

        new_icon = self.icon_mgr.get("new_file", 16)
        self._icon_refs.append(new_icon)

        self._modern_btn(
            actions, new_icon, " New File",
            app.file_manager.new_file, "success",
        ).pack(fill=X, pady=1)

        file_icon = self.icon_mgr.get("file", 16)
        self._icon_refs.append(file_icon)

        self._modern_btn(
            actions, file_icon, " Open File",
            app.file_manager.open_file, "info",
        ).pack(fill=X, pady=1)

        ttk.Separator(self.frame).pack(fill=X, padx=8, pady=4)

        # ── Git section ──
        git_header = ttk.Frame(self.frame)
        git_header.pack(fill=X, padx=8, pady=(0, 4))

        git_icon = self.icon_mgr.get("folder_git", 16)
        self._icon_refs.append(git_icon)

        ttk.Label(
            git_header,
            text=" GIT",
            image=git_icon,
            compound=LEFT,
            font=("Segoe UI", 9, "bold"),
        ).pack(side=LEFT)

        git_btns = ttk.Frame(self.frame)
        git_btns.pack(fill=X, padx=8, pady=(0, 4))

        clone_icon = self.icon_mgr.get("open_file", 16)
        self._icon_refs.append(clone_icon)

        self._modern_btn(
            git_btns, clone_icon, " Clone",
            app.git_manager.clone_repo, "danger",
        ).pack(fill=X, pady=1)

        self._modern_btn(
            git_btns, self.icon_mgr.get("info", 16), " Status",
            app.git_manager.git_status, "info",
        ).pack(fill=X, pady=1)
        self._icon_refs.append(self._icon_refs[-1])

        commit_icon = self.icon_mgr.get("success", 16)
        self._icon_refs.append(commit_icon)

        self._modern_btn(
            git_btns, commit_icon, " Commit",
            app.git_manager.git_commit, "success",
        ).pack(fill=X, pady=1)

        ttk.Separator(self.frame).pack(fill=X, padx=8, pady=4)

        # ── File tree ──
        self.file_tree = FileTree(self.frame, app)
        self.file_tree.frame.pack(fill=BOTH, expand=True, padx=4, pady=4)

    def _modern_btn(self, parent, icon, text, command, style):
        """Create a button with hover effect."""
        btn = ttk.Button(
            parent,
            text=text,
            image=icon,
            compound=LEFT,
            bootstyle=f"{style}-outline",
            command=command,
            padding=(8, 4),
        )

        original = f"{style}-outline"
        hover = style

        def on_enter(e, b=btn, s=hover):
            b.configure(bootstyle=s)

        def on_leave(e, b=btn, s=original):
            b.configure(bootstyle=s)

        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)

        return btn

    def toggle(self):
        if self.visible:
            self.frame.pack_forget()
            self.visible = False
        else:
            self.frame.pack(side=LEFT, fill=Y)
            self.visible = True