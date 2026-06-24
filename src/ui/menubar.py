"""Menu bar builder — PyQt6."""

from PyQt6.QtGui import QAction


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
        self._add(file_menu, "Save", "Ctrl+S", app.file_manager.save_file)
        self._add(file_menu, "Save As", "Ctrl+Shift+S", app.file_manager.save_file_as)
        file_menu.addSeparator()
        self._add(file_menu, "Close Tab", "Ctrl+W", app.editor_tabs.close_current_tab)
        file_menu.addSeparator()
        self._add(file_menu, "Settings", "Ctrl+,", lambda: app.open_settings())
        file_menu.addSeparator()
        self._add(file_menu, "Exit", "", app.close)

        # Edit
        edit_menu = menubar.addMenu("Edit")
        self._add(edit_menu, "Find & Replace", "Ctrl+F", app.toggle_search)
        self._add(edit_menu, "Go to Line", "Ctrl+G", app.go_to_line)

        # View
        view_menu = menubar.addMenu("View")
        self._add(view_menu, "Command Palette", "Ctrl+Shift+P", app.open_command_palette)
        view_menu.addSeparator()
        self._add(view_menu, "Toggle Sidebar", "Ctrl+B", app.toggle_sidebar)
        self._add(view_menu, "Toggle Terminal", "Ctrl+`", app.toggle_terminal)
        view_menu.addSeparator()
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

        # Help
        help_menu = menubar.addMenu("Help")
        self._add(help_menu, "Check for Updates", "", app.check_for_updates)
        self._add(help_menu, "About", "", self._about)

    def _add(self, menu, text, shortcut, callback):
        action = QAction(text, self.app)
        if shortcut:
            action.setShortcut(shortcut)
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