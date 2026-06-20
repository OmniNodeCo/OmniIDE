"""Menu bar — v1.0.4 with Settings and Check for Updates."""

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

    def _cp(self):
        return getattr(self.app, "command_palette", None)

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
        m.add_command(label="Settings", accelerator="Ctrl+,", command=lambda: self.app.open_settings())
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
        m.add_command(label="Go to Line", accelerator="Ctrl+G", command=lambda: self._cp() and self._cp()._go_to_line())
        m.add_command(label="Toggle Comment", accelerator="Ctrl+/", command=lambda: self._cp() and self._cp()._toggle_comment())
        m.add_command(label="Duplicate Line", command=lambda: self._cp() and self._cp()._duplicate_line())
        m.add_command(label="Delete Line", command=lambda: self._cp() and self._cp()._delete_line())

    def _build_view_menu(self):
        m = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="View", menu=m)

        m.add_command(label="Command Palette", accelerator="Ctrl+Shift+P", command=lambda: self.app.toggle_command_palette())
        m.add_separator()
        m.add_command(label="Toggle Sidebar", accelerator="Ctrl+B", command=self.app.toggle_sidebar)
        m.add_command(label="Toggle Terminal", accelerator="Ctrl+`", command=self.app.toggle_terminal)
        m.add_separator()
        m.add_command(label="Switch Theme", command=self.app.switch_theme)
        m.add_command(label="Toggle Word Wrap", command=lambda: self._cp() and self._cp()._toggle_word_wrap())
        m.add_separator()
        m.add_command(label="Zoom In", accelerator="Ctrl++", command=lambda: self._cp() and self._cp()._zoom_in())
        m.add_command(label="Zoom Out", accelerator="Ctrl+-", command=lambda: self._cp() and self._cp()._zoom_out())
        m.add_command(label="Reset Zoom", accelerator="Ctrl+0", command=lambda: self._cp() and self._cp()._zoom_reset())

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

        m.add_command(label="Browse Marketplace", command=lambda: self.app.sidebar._switch_panel("extensions"))
        m.add_command(label="View Installed", command=lambda: self.app.sidebar._switch_panel("extensions"))

    def _build_help_menu(self):
        m = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Help", menu=m)

        m.add_command(label="Check for Updates...", command=lambda: self.app.check_for_updates())
        m.add_separator()
        m.add_command(label="About OmniIDE", command=lambda: self._cp() and self._cp()._show_about())
        m.add_command(label="Open Settings Folder", command=lambda: self._cp() and self._cp()._open_settings_folder())

    def _ed(self, action):
        editor = self.app.tab_manager.get_active_editor()
        if not editor:
            return
        try:
            {
                "undo": lambda: editor.edit_undo(),
                "redo": lambda: editor.edit_redo(),
                "cut": lambda: editor.event_generate("<<Cut>>"),
                "copy": lambda: editor.event_generate("<<Copy>>"),
                "paste": lambda: editor.event_generate("<<Paste>>"),
                "select_all": lambda: editor.tag_add("sel", "1.0", "end"),
            }[action]()
        except tk.TclError:
            pass

    def _update_recent_menu(self):
        self.recent_menu.delete(0, "end")
        files = self.app.recent_files_manager.get_all()
        if not files:
            self.recent_menu.add_command(label="(No recent files)", state="disabled")
        else:
            for fp in files:
                self.recent_menu.add_command(label=fp, command=lambda f=fp: self.app.file_manager.open_file(f))