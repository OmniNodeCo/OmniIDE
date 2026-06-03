"""Application menu bar with Git menu."""

import tkinter as tk


class MenuBar:
    """Main menu bar for OmniIDE."""

    def __init__(self, root, app):
        self.app = app
        self.menu = tk.Menu(root, tearoff=0)
        root.configure(menu=self.menu)

        self._build_file_menu()
        self._build_edit_menu()
        self._build_view_menu()
        self._build_git_menu()
        self._build_help_menu()

    def _build_file_menu(self):
        file_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="File", menu=file_menu)

        file_menu.add_command(
            label="New File", accelerator="Ctrl+N",
            command=self.app.file_manager.new_file,
        )
        file_menu.add_command(
            label="Open File...", accelerator="Ctrl+O",
            command=self.app.file_manager.open_file,
        )
        file_menu.add_command(
            label="Open Folder...",
            command=self.app.open_project,
        )
        file_menu.add_separator()
        file_menu.add_command(
            label="Save", accelerator="Ctrl+S",
            command=self.app.file_manager.save_file,
        )
        file_menu.add_command(
            label="Save As...", accelerator="Ctrl+Shift+S",
            command=self.app.file_manager.save_file_as,
        )
        file_menu.add_separator()
        file_menu.add_command(
            label="Close Tab", accelerator="Ctrl+W",
            command=self.app.tab_manager.close_active_tab,
        )
        file_menu.add_separator()

        # Recent files
        self.recent_menu = tk.Menu(file_menu, tearoff=0)
        file_menu.add_cascade(label="Recent Files", menu=self.recent_menu)
        self._update_recent_menu()

        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.app.root.quit)

    def _build_edit_menu(self):
        edit_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Edit", menu=edit_menu)

        edit_menu.add_command(
            label="Undo", accelerator="Ctrl+Z",
            command=lambda: self._editor_action("undo"),
        )
        edit_menu.add_command(
            label="Redo", accelerator="Ctrl+Y",
            command=lambda: self._editor_action("redo"),
        )
        edit_menu.add_separator()
        edit_menu.add_command(
            label="Cut", accelerator="Ctrl+X",
            command=lambda: self._editor_action("cut"),
        )
        edit_menu.add_command(
            label="Copy", accelerator="Ctrl+C",
            command=lambda: self._editor_action("copy"),
        )
        edit_menu.add_command(
            label="Paste", accelerator="Ctrl+V",
            command=lambda: self._editor_action("paste"),
        )
        edit_menu.add_separator()
        edit_menu.add_command(
            label="Select All", accelerator="Ctrl+A",
            command=lambda: self._editor_action("select_all"),
        )
        edit_menu.add_separator()
        edit_menu.add_command(
            label="Find & Replace", accelerator="Ctrl+F",
            command=self.app.toggle_search,
        )

    def _build_view_menu(self):
        view_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="View", menu=view_menu)

        view_menu.add_command(
            label="Toggle Sidebar", accelerator="Ctrl+B",
            command=self.app.toggle_sidebar,
        )
        view_menu.add_command(
            label="Toggle Terminal", accelerator="Ctrl+`",
            command=self.app.toggle_terminal,
        )
        view_menu.add_separator()
        view_menu.add_command(
            label="Switch Theme",
            command=self.app.switch_theme,
        )
        view_menu.add_separator()
        view_menu.add_command(
            label="Zoom In", accelerator="Ctrl++",
            command=self._zoom_in,
        )
        view_menu.add_command(
            label="Zoom Out", accelerator="Ctrl+-",
            command=self._zoom_out,
        )

    def _build_git_menu(self):
        git_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Git", menu=git_menu)

        gm = self.app.git_manager

        git_menu.add_command(label="Clone Repository...", command=gm.clone_repo)
        git_menu.add_command(label="Init Repository", command=gm.init_repo)
        git_menu.add_separator()
        git_menu.add_command(label="Status", command=gm.git_status)
        git_menu.add_command(label="Diff", command=gm.git_diff)
        git_menu.add_command(label="Log", command=gm.git_log)
        git_menu.add_command(label="Branches", command=gm.git_branch)
        git_menu.add_separator()
        git_menu.add_command(label="Stage All", command=gm.git_add_all)
        git_menu.add_command(label="Commit...", command=gm.git_commit)
        git_menu.add_separator()
        git_menu.add_command(label="Push", command=gm.git_push)
        git_menu.add_command(label="Pull", command=gm.git_pull)
        git_menu.add_separator()
        git_menu.add_command(label="Set Remote...", command=gm.add_remote)

    def _build_help_menu(self):
        help_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Help", menu=help_menu)

        help_menu.add_command(label="About OmniIDE", command=self._show_about)

    def _editor_action(self, action):
        editor = self.app.tab_manager.get_active_editor()
        if not editor:
            return
        try:
            if action == "undo":
                editor.edit_undo()
            elif action == "redo":
                editor.edit_redo()
            elif action == "cut":
                editor.event_generate("<<Cut>>")
            elif action == "copy":
                editor.event_generate("<<Copy>>")
            elif action == "paste":
                editor.event_generate("<<Paste>>")
            elif action == "select_all":
                editor.tag_add("sel", "1.0", "end")
        except tk.TclError:
            pass

    def _zoom_in(self):
        self.app.settings["font_size"] = min(32, self.app.settings["font_size"] + 1)
        self._apply_font_size()

    def _zoom_out(self):
        self.app.settings["font_size"] = max(8, self.app.settings["font_size"] - 1)
        self._apply_font_size()

    def _apply_font_size(self):
        size = self.app.settings["font_size"]
        family = self.app.settings["font_family"]
        for info in self.app.tab_manager.tabs.values():
            info["editor"].configure(font=(family, size))
            info["line_numbers"].set_font((family, size))
            info["line_numbers"].redraw()
        self.app.save_settings()
        self.app.set_status(f"Font size: {size}")

    def _update_recent_menu(self):
        self.recent_menu.delete(0, "end")
        files = self.app.recent_files_manager.get_all()
        if not files:
            self.recent_menu.add_command(
                label="(No recent files)", state="disabled"
            )
        else:
            for fp in files:
                self.recent_menu.add_command(
                    label=fp,
                    command=lambda f=fp: self.app.file_manager.open_file(f),
                )

    def _show_about(self):
        from tkinter import messagebox
        messagebox.showinfo(
            "About OmniIDE",
            "OmniIDE v1.0.0\n\n"
            "A fast, modern, lightweight desktop IDE.\n"
            "Built from scratch by OmniNodeCo.\n\n"
            "No Electron. No bloat. Pure speed.\n\n"
            "(c) 2024 OmniNodeCo",
        )