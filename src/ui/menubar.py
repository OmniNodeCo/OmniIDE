"""Menu bar builder — PyQt6."""

from PyQt6.QtGui import QAction, QKeySequence, QShortcut


class MenuBarBuilder:
    """Build the application menu bar."""

    def __init__(self, app):
        self.app = app
        menubar = app.menuBar()

        # File
        file_menu = menubar.addMenu("File")
        self._add(file_menu, "New File", "Ctrl+N", app.file_manager.new_file)
        self._add(file_menu, "Open File", "Ctrl+O", app.file_manager.open_file)
        self._add(file_menu, "Open Folder", "", lambda: app.open_project())
        file_menu.addSeparator()
        self._add(file_menu, "Quick Open", "Ctrl+P", app.open_quick_open)
        self._add(file_menu, "Save", "Ctrl+S", app.file_manager.save_file)
        self._add(file_menu, "Save As", "Ctrl+Shift+S", app.file_manager.save_file_as)
        self._add(file_menu, "Save All", "Ctrl+Alt+S", app.file_manager.save_all)
        self._add(file_menu, "Revert File", "", app.revert_file)
        file_menu.addSeparator()
        self._add(file_menu, "Close Tab", "Ctrl+W", app.editor_tabs.close_current_tab)
        self._add(file_menu, "Close Other Tabs", "", app.editor_tabs.close_other_tabs)
        self._add(file_menu, "Close All Tabs", "", app.editor_tabs.close_all_tabs)
        file_menu.addSeparator()
        self._build_recent_menus(file_menu, app)
        file_menu.addSeparator()
        self._add(file_menu, "Settings", "Ctrl+,", lambda: app.open_settings())
        file_menu.addSeparator()
        self._add(file_menu, "Exit", "", app.close)

        # Run
        run_menu = menubar.addMenu("Run")
        self._add(run_menu, "Run File", "Ctrl+F5", app.run_current_file)

        # Edit
        edit_menu = menubar.addMenu("Edit")
        self._add(edit_menu, "Find & Replace", "Ctrl+F", app.toggle_search)
        self._add(edit_menu, "Go to Line", "Ctrl+G", app.go_to_line)
        self._add(edit_menu, "Format JSON", "", app.format_json)
        self._build_case_menu(edit_menu, app)
        edit_menu.addSeparator()
        self._add(edit_menu, "Toggle Comment", "Ctrl+/", app.toggle_comment)
        self._add(edit_menu, "Duplicate Line", "Ctrl+D", app.duplicate_line)
        self._add(edit_menu, "Delete Line", "Ctrl+Shift+D", app.delete_line)
        self._add(edit_menu, "Move Line Up", "Alt+Up", app.move_line_up)
        self._add(edit_menu, "Move Line Down", "Alt+Down", app.move_line_down)
        self._add(edit_menu, "Sort Lines", "Ctrl+Shift+O", app.sort_lines)
        edit_menu.addSeparator()
        self._add(edit_menu, "Line Endings: LF", "",
                  lambda: app.file_manager.convert_line_endings("lf"))
        self._add(edit_menu, "Line Endings: CRLF", "",
                  lambda: app.file_manager.convert_line_endings("crlf"))

        # View
        view_menu = menubar.addMenu("View")
        self._add(view_menu, "Command Palette", "Ctrl+Shift+P", app.open_command_palette)
        self._add(view_menu, "Search in Files", "Ctrl+Shift+F", app.open_search)
        view_menu.addSeparator()
        self._add(view_menu, "Toggle Sidebar", "Ctrl+B", app.toggle_sidebar)
        self._add(view_menu, "Toggle Terminal", "Ctrl+`", app.toggle_terminal)
        self._add(view_menu, "New Terminal", "Ctrl+Shift+T", app.new_terminal)
        view_menu.addSeparator()
        self._add(view_menu, "Markdown Preview", "Ctrl+Shift+V",
                  app.toggle_markdown_preview)
        self._add(view_menu, "Toggle Minimap", "", app.toggle_minimap)
        self._add(view_menu, "Toggle Hidden Files", "", app.toggle_hidden_files)
        self._add(view_menu, "Switch Theme", "", app.switch_theme)
        view_menu.addSeparator()
        self._add(view_menu, "Zoom In", "Ctrl+=", lambda: app._zoom(1))
        self._add(view_menu, "Zoom Out", "Ctrl+-", lambda: app._zoom(-1))
        self._add(view_menu, "Reset Zoom", "Ctrl+0", lambda: app._zoom(0))

        # Git
        git_menu = menubar.addMenu("Git")
        gm = app.git_manager
        self._add(git_menu, "Clone", "", gm.clone_repo)
        self._add(git_menu, "Init", "", gm.init_repo)
        git_menu.addSeparator()
        self._add(git_menu, "Status", "", gm.git_status)
        self._add(git_menu, "Diff", "", gm.git_diff)
        self._add(git_menu, "Log", "", gm.git_log)
        self._add(git_menu, "Branches", "", gm.git_branch)
        git_menu.addSeparator()
        self._add(git_menu, "Stage All", "", gm.git_add_all)
        self._add(git_menu, "Commit", "", gm.git_commit)
        git_menu.addSeparator()
        self._add(git_menu, "Push", "", gm.git_push)
        self._add(git_menu, "Pull", "", gm.git_pull)
        git_menu.addSeparator()
        self._add(git_menu, "Set Remote", "", gm.add_remote)

        # Tools
        tools_menu = menubar.addMenu("Tools")
        self._add(tools_menu, "Check for Updates", "", app.check_for_updates)
        self._add(tools_menu, "Release Notes", "", app.show_release_notes)

        # Help
        help_menu = menubar.addMenu("Help")
        self._add(help_menu, "Check for Updates", "", app.check_for_updates)
        self._add(help_menu, "Release Notes", "", app.show_release_notes)
        self._add(help_menu, "About", "", self._about)

    def _build_recent_menus(self, menu, app):
        # Recent Files
        recent_files_menu = menu.addMenu("Open Recent File")
        files = app.recent_files_manager.get_all()
        if files:
            for fp in files:
                act = QAction(fp, self.app)
                act.triggered.connect(lambda _=False, p=fp: app.file_manager.open_file(p))
                recent_files_menu.addAction(act)
            recent_files_menu.addSeparator()
            clear_act = QAction("Clear Recent Files", self.app)
            clear_act.triggered.connect(lambda: (
                app.recent_files_manager.clear(), self._rebuild_menubar(app)
            ))
            recent_files_menu.addAction(clear_act)
        else:
            act = QAction("(no recent files)", self.app)
            act.setEnabled(False)
            recent_files_menu.addAction(act)

        # Recent Folders
        recent_folders_menu = menu.addMenu("Open Recent Folder")
        folders = app.recent_folders.get_all()
        if folders:
            for fp in folders:
                act = QAction(fp, self.app)
                act.triggered.connect(lambda _=False, p=fp: app.open_recent_folder(p))
                recent_folders_menu.addAction(act)
            recent_folders_menu.addSeparator()
            clear_act = QAction("Clear Recent Folders", self.app)
            clear_act.triggered.connect(lambda: (
                app.recent_folders.clear(), self._rebuild_menubar(app)
            ))
            recent_folders_menu.addAction(clear_act)
        else:
            act = QAction("(no recent folders)", self.app)
            act.setEnabled(False)
            recent_folders_menu.addAction(act)

    def _rebuild_menubar(self, app):
        from PyQt6.QtWidgets import QMenuBar
        old = app.menuBar()
        app.setMenuBar(None)
        old.deleteLater()
        MenuBarBuilder(app)

    def _build_case_menu(self, menu, app):
        case_menu = menu.addMenu("Convert Case")
        options = [
            ("UPPERCASE", "upper"),
            ("lowercase", "lower"),
            ("Title Case", "title"),
            ("camelCase", "camel"),
            ("PascalCase", "pascal"),
            ("snake_case", "snake"),
            ("kebab-case", "kebab"),
        ]
        for label, mode in options:
            self._add(case_menu, label, "", lambda _=False, m=mode: app.convert_case(m))

    def _add(self, menu, text, shortcut, callback):
        action = QAction(text, self.app)
        if shortcut:
            action.setShortcut(QKeySequence(shortcut))
        action.triggered.connect(callback)
        menu.addAction(action)

    def _about(self):
        from PyQt6.QtWidgets import QMessageBox
        from src.config import APP_VERSION
        QMessageBox.about(
            self.app, "About OmniIDE",
            f"OmniIDE v{APP_VERSION}\n\n"
            f"Built from scratch by OmniNodeCo.\n"
            f"No Electron. No bloat. Pure speed.",
        )
