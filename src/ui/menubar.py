"""Menu bar — v1.0.1 with Extensions menu."""

import tkinter as tk


class MenuBar:
    """Main menu bar."""

    def __init__(self, root, app):
        self.app = app
        self.menu = tk.Menu(root, tearoff=0)
        root.configure(menu=self.menu)

        self._build_file_menu()
        self._build_edit_menu()
        self._build_view_menu()
        self._build_git_menu()
        self._build_extensions_menu()
        self._build_help_menu()

    def _build_file_menu(self):
        m = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="File", menu=m)

        m.add_command(label="New File", accelerator="Ctrl+N", command=self.app.file_manager.new_file)
        m.add_command(label="Open File...", accelerator="Ctrl+O", command=self.app.file_manager.open_file)
        m.add_command(label="Open Folder...", command=self.app.open_project)
        m.add_separator()
        m.add_command(label="Save", accelerator="Ctrl+S", command=self.app.file_manager.save_file)
        m.add_command(label="Save As...", accelerator="Ctrl+Shift+S", command=self.app.file_manager.save_file_as)
        m.add_separator()
        m.add_command(label="Close Tab", accelerator="Ctrl+W", command=self.app.tab_manager.close_active_tab)
        m.add_separator()

        self.recent_menu = tk.Menu(m, tearoff=0)
        m.add_cascade(label="Recent Files", menu=self.recent_menu)
        self._update_recent_menu()

        m.add_separator()
        m.add_command(label="Exit", command=self.app.root.quit)

    def _build_edit_menu(self):
        m = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Edit", menu=m)

        m.add_command(label="Undo", accelerator="Ctrl+Z", command=lambda: self._ed("undo"))
        m.add_command(label="Redo", accelerator="Ctrl+Y", command=lambda: self._ed("redo"))
        m.add_separator()
        m.add_command(label="Cut", accelerator="Ctrl+X", command=lambda: self._ed("cut"))
        m.add_command(label="Copy", accelerator="Ctrl+C", command=lambda: self._ed("copy"))
        m.add_command(label="Paste", accelerator="Ctrl+V", command=lambda: self._ed("paste"))
        m.add_separator()
        m.add_command(label="Select All", accelerator="Ctrl+A", command=lambda: self._ed("select_all"))
        m.add_separator()
        m.add_command(label="Find & Replace", accelerator="Ctrl+F", command=self.app.toggle_search)

    def _build_view_menu(self):
        m = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="View", menu=m)

        m.add_command(label="Toggle Sidebar", accelerator="Ctrl+B", command=self.app.toggle_sidebar)
        m.add_command(label="Toggle Terminal", accelerator="Ctrl+`", command=self.app.toggle_terminal)
        m.add_separator()
        m.add_command(label="Switch Theme", command=self.app.switch_theme)
        m.add_separator()
        m.add_command(label="Zoom In", accelerator="Ctrl++", command=self._zoom_in)
        m.add_command(label="Zoom Out", accelerator="Ctrl+-", command=self._zoom_out)

    def _build_git_menu(self):
        m = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Git", menu=m)

        gm = self.app.git_manager
        m.add_command(label="Clone Repository...", command=gm.clone_repo)
        m.add_command(label="Init Repository", command=gm.init_repo)
        m.add_separator()
        m.add_command(label="Status", command=gm.git_status)
        m.add_command(label="Diff", command=gm.git_diff)
        m.add_command(label="Log", command=gm.git_log)
        m.add_command(label="Branches", command=gm.git_branch)
        m.add_separator()
        m.add_command(label="Stage All", command=gm.git_add_all)
        m.add_command(label="Commit...", command=gm.git_commit)
        m.add_separator()
        m.add_command(label="Push", command=gm.git_push)
        m.add_command(label="Pull", command=gm.git_pull)
        m.add_separator()
        m.add_command(label="Set Remote...", command=gm.add_remote)

    def _build_extensions_menu(self):
        m = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Extensions", menu=m)

        m.add_command(
            label="Browse Marketplace",
            command=lambda: self.app.sidebar._switch_panel("extensions"),
        )
        m.add_command(
            label="View Installed",
            command=self._show_installed,
        )

    def _build_help_menu(self):
        m = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Help", menu=m)
        m.add_command(label="About OmniIDE", command=self._show_about)

    def _ed(self, action):
        editor = self.app.tab_manager.get_active_editor()
        if not editor:
            return
        try:
            actions = {
                "undo": lambda: editor.edit_undo(),
                "redo": lambda: editor.edit_redo(),
                "cut": lambda: editor.event_generate("<<Cut>>"),
                "copy": lambda: editor.event_generate("<<Copy>>"),
                "paste": lambda: editor.event_generate("<<Paste>>"),
                "select_all": lambda: editor.tag_add("sel", "1.0", "end"),
            }
            actions[action]()
        except tk.TclError:
            pass

    def _zoom_in(self):
        self.app.settings["font_size"] = min(32, self.app.settings["font_size"] + 1)
        self._apply_font()

    def _zoom_out(self):
        self.app.settings["font_size"] = max(8, self.app.settings["font_size"] - 1)
        self._apply_font()

    def _apply_font(self):
        s = self.app.settings["font_size"]
        f = self.app.settings["font_family"]
        for info in self.app.tab_manager.tabs.values():
            info["editor"].configure(font=(f, s))
            info["line_numbers"].set_font((f, s))
            info["line_numbers"].redraw()
        self.app.save_settings()
        self.app.set_status(f"Font size: {s}")

    def _update_recent_menu(self):
        self.recent_menu.delete(0, "end")
        files = self.app.recent_files_manager.get_all()
        if not files:
            self.recent_menu.add_command(label="(No recent files)", state="disabled")
        else:
            for fp in files:
                self.recent_menu.add_command(
                    label=fp,
                    command=lambda f=fp: self.app.file_manager.open_file(f),
                )

    def _show_installed(self):
        self.app.sidebar._switch_panel("extensions")
        # Find the extensions panel and show installed tab
        for pid, panel in self.app.sidebar.panels.items():
            if pid == "extensions":
                break

    def _show_about(self):
        from tkinter import messagebox
        from src.config import APP_VERSION
        messagebox.showinfo(
            "About OmniIDE",
            f"OmniIDE v{APP_VERSION}\n\n"
            "A fast, modern, lightweight desktop IDE.\n"
            "Built from scratch by OmniNodeCo.\n\n"
            "No Electron. No bloat. Pure speed.\n\n"
            "(c) 2024 OmniNodeCo",
        )