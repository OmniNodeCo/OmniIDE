"""Sidebar — PyQt6 with SVG icons and organized panels."""

import os

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QTreeView, QScrollArea,
    QStackedWidget, QLineEdit, QMessageBox,
)
from PyQt6.QtCore import Qt, QDir, QModelIndex, pyqtSignal, QObject
from PyQt6.QtGui import QFont, QFileSystemModel

from src.ui.icons import svg_icon
from src.core.extension_manager import ExtensionManager


class FileTree(QWidget):
    """File tree explorer."""

    def __init__(self, app):
        super().__init__()
        self.app = app

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.model = QFileSystemModel()
        self.model.setRootPath("")
        self.model.setFilter(
            QDir.Filter.AllDirs | QDir.Filter.Files | QDir.Filter.NoDotAndDotDot
        )
        self.model.setNameFilterDisables(False)

        self.tree = QTreeView()
        self.tree.setModel(self.model)
        self.tree.setHeaderHidden(True)
        self.tree.hideColumn(1)
        self.tree.hideColumn(2)
        self.tree.hideColumn(3)
        self.tree.setAnimated(True)
        self.tree.setIndentation(16)
        self.tree.doubleClicked.connect(self._on_double_click)

        layout.addWidget(self.tree)

    def load_directory(self, path):
        self.model.setRootPath(path)
        self.tree.setRootIndex(self.model.index(path))

    def _on_double_click(self, index: QModelIndex):
        path = self.model.filePath(index)
        if os.path.isfile(path):
            self.app.file_manager.open_file(path)


def _sep():
    sep = QFrame()
    sep.setProperty("cssClass", "separator")
    sep.setFixedHeight(1)
    return sep


def _header(text):
    label = QLabel(text.upper())
    label.setProperty("cssClass", "header")
    return label


def _section_label(text):
    label = QLabel(f"  {text}")
    label.setProperty("cssClass", "dim")
    label.setFont(QFont("Segoe UI", 8))
    return label


def _icon_btn(text, icon_name, css_class=None, size=14):
    btn = QPushButton(f"  {text}")
    btn.setIcon(svg_icon(icon_name, size))
    if css_class:
        btn.setProperty("cssClass", css_class)
    return btn


class ExplorerPanel(QWidget):
    """File explorer panel."""

    def __init__(self, app):
        super().__init__()
        self.app = app

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        layout.addWidget(_header("Explorer"))
        layout.addWidget(_sep())

        btn_row = QHBoxLayout()

        new_btn = _icon_btn("New", "new_file", "primary")
        new_btn.clicked.connect(app.file_manager.new_file)
        btn_row.addWidget(new_btn)

        open_btn = _icon_btn("Open", "open_file")
        open_btn.clicked.connect(app.file_manager.open_file)
        btn_row.addWidget(open_btn)

        layout.addLayout(btn_row)

        folder_btn = _icon_btn("Open Folder", "files")
        folder_btn.clicked.connect(lambda: app.open_project())
        layout.addWidget(folder_btn)

        layout.addWidget(_sep())

        self.file_tree = FileTree(app)
        layout.addWidget(self.file_tree, 1)


class GitPanel(QWidget):
    """Git source control panel with icons."""

    def __init__(self, app):
        super().__init__()
        self.app = app
        gm = app.git_manager

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)

        layout.addWidget(_header("Source Control"))
        layout.addWidget(_sep())

        layout.addWidget(_section_label("Repository"))

        clone_btn = _icon_btn("Clone", "clone")
        clone_btn.clicked.connect(gm.clone_repo)
        layout.addWidget(clone_btn)

        init_btn = _icon_btn("Init", "new_file", "primary")
        init_btn.clicked.connect(gm.init_repo)
        layout.addWidget(init_btn)

        remote_btn = _icon_btn("Set Remote", "remote")
        remote_btn.clicked.connect(gm.add_remote)
        layout.addWidget(remote_btn)

        layout.addWidget(_sep())
        layout.addWidget(_section_label("Changes"))

        status_btn = _icon_btn("Status", "status")
        status_btn.clicked.connect(gm.git_status)
        layout.addWidget(status_btn)

        diff_btn = _icon_btn("Diff", "diff")
        diff_btn.clicked.connect(gm.git_diff)
        layout.addWidget(diff_btn)

        stage_btn = _icon_btn("Stage All", "stage", "success")
        stage_btn.clicked.connect(gm.git_add_all)
        layout.addWidget(stage_btn)

        layout.addWidget(_sep())
        layout.addWidget(_section_label("Commit & Sync"))

        commit_btn = _icon_btn("Commit", "commit", "success")
        commit_btn.clicked.connect(gm.git_commit)
        layout.addWidget(commit_btn)

        sync_row = QHBoxLayout()

        push_btn = _icon_btn("Push", "push")
        push_btn.clicked.connect(gm.git_push)
        sync_row.addWidget(push_btn)

        pull_btn = _icon_btn("Pull", "pull")
        pull_btn.clicked.connect(gm.git_pull)
        sync_row.addWidget(pull_btn)

        layout.addLayout(sync_row)

        layout.addWidget(_sep())
        layout.addWidget(_section_label("History"))

        log_btn = _icon_btn("Log", "log")
        log_btn.clicked.connect(gm.git_log)
        layout.addWidget(log_btn)

        branch_btn = _icon_btn("Branches", "branch")
        branch_btn.clicked.connect(gm.git_branch)
        layout.addWidget(branch_btn)

        layout.addStretch()


class ExtensionSignals(QObject):
    """Signals for thread-safe extension callbacks."""
    search_done = pyqtSignal(list, str)
    install_done = pyqtSignal(bool, str)


class ExtensionsPanel(QWidget):
    """Extensions marketplace panel with icons and thread-safe callbacks."""

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.ext_manager = app.extension_manager

        # Thread-safe signals
        self.signals = ExtensionSignals()
        self.signals.search_done.connect(self._handle_search_results)
        self.signals.install_done.connect(self._handle_install_done)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        layout.addWidget(_header("Extensions"))
        layout.addWidget(_sep())

        # Search
        search_row = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search marketplace...")
        self.search_input.returnPressed.connect(self._on_search)
        search_row.addWidget(self.search_input, 1)

        search_btn = _icon_btn("", "search", "primary")
        search_btn.setFixedWidth(36)
        search_btn.clicked.connect(self._on_search)
        search_row.addWidget(search_btn)

        layout.addLayout(search_row)

        self.status_label = QLabel("Search or view installed")
        self.status_label.setProperty("cssClass", "dim")
        layout.addWidget(self.status_label)

        # Tabs
        tab_row = QHBoxLayout()

        self.mp_btn = QPushButton("Marketplace")
        self.mp_btn.setProperty("cssClass", "primary")
        self.mp_btn.setCheckable(True)
        self.mp_btn.setChecked(True)
        self.mp_btn.clicked.connect(lambda: self._switch("marketplace"))
        tab_row.addWidget(self.mp_btn)

        self.inst_btn = QPushButton("Installed")
        self.inst_btn.setCheckable(True)
        self.inst_btn.clicked.connect(lambda: self._switch("installed"))
        tab_row.addWidget(self.inst_btn)

        layout.addLayout(tab_row)

        # Results
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.results_widget = QWidget()
        self.results_layout = QVBoxLayout(self.results_widget)
        self.results_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.results_layout.setSpacing(4)
        self.scroll.setWidget(self.results_widget)
        layout.addWidget(self.scroll, 1)

        self.tab = "marketplace"
        self._pending_install_name = ""
        self._last_query = ""

    def _switch(self, tab):
        self.tab = tab
        self.mp_btn.setChecked(tab == "marketplace")
        self.inst_btn.setChecked(tab == "installed")
        if tab == "installed":
            self._show_installed()
        else:
            self._clear()
            self.status_label.setText("Search marketplace above")

    def _on_search(self):
        query = self.search_input.text().strip()
        if not query:
            return
        self._last_query = query
        self.tab = "marketplace"
        self.mp_btn.setChecked(True)
        self.inst_btn.setChecked(False)
        self._clear()
        self.status_label.setText("Searching...")
        self.app.set_status(f"Searching: {query}")

        # Use signal-based callback for thread safety
        def _callback(results, error):
            # This runs in background thread — emit signal to main thread
            error_str = error if error else ""
            self.signals.search_done.emit(results, error_str)

        self.ext_manager.search(query, _callback)

    def _handle_search_results(self, results, error):
        """Called on main thread via signal."""
        self._clear()

        if error:
            self.status_label.setText(f"Error: {error}")
            self.app.set_status(f"Search error: {error}")
            return

        if not results:
            self.status_label.setText("No extensions found")
            self.app.set_status("No extensions found")
            return

        self.status_label.setText(f"{len(results)} found")
        self.app.set_status(f"Found {len(results)} extensions")

        for ext in results:
            self._add_card(ext, "marketplace")

    def _show_installed(self):
        self._clear()
        installed = self.ext_manager.get_installed()
        if not installed:
            self.status_label.setText("No extensions installed")
            return
        self.status_label.setText(f"{len(installed)} installed")
        for ext in installed:
            self._add_card(ext, "installed")

    def _add_card(self, info, mode):
        card = QFrame()
        card.setStyleSheet(
            f"QFrame {{ background-color: {self.app.colors['bg_secondary']}; "
            f"border-radius: 6px; padding: 2px; margin: 2px; }}"
        )

        cl = QVBoxLayout(card)
        cl.setContentsMargins(10, 8, 10, 8)
        cl.setSpacing(3)

        # Name + version row
        nr = QHBoxLayout()
        nr.setSpacing(8)

        name_text = info.get("name", info.get("id", "Unknown"))
        name_label = QLabel(name_text)
        name_label.setFont(QFont("Segoe UI", 10))
        name_label.setStyleSheet("font-weight: bold; background: transparent;")
        nr.addWidget(name_label)

        ver_text = info.get("version", "")
        if ver_text:
            ver_label = QLabel(f"v{ver_text}")
            ver_label.setProperty("cssClass", "dim")
            ver_label.setStyleSheet("background: transparent;")
            nr.addWidget(ver_label)

        nr.addStretch()
        cl.addLayout(nr)

        # Publisher
        pub = info.get("publisher", "")
        if pub:
            pub_label = QLabel(pub)
            pub_label.setProperty("cssClass", "accent")
            pub_label.setFont(QFont("Segoe UI", 8))
            pub_label.setStyleSheet("background: transparent;")
            cl.addWidget(pub_label)

        # Description
        desc = info.get("description", "")
        if desc:
            desc_text = desc[:100] + ("..." if len(desc) > 100 else "")
            desc_label = QLabel(desc_text)
            desc_label.setWordWrap(True)
            desc_label.setProperty("cssClass", "dim")
            desc_label.setStyleSheet("background: transparent;")
            cl.addWidget(desc_label)

        # Stats (marketplace only)
        if mode == "marketplace":
            installs = info.get("installs", 0)
            stats_label = QLabel(
                f"Downloads: {ExtensionManager.format_installs(installs)}"
            )
            stats_label.setProperty("cssClass", "dim")
            stats_label.setFont(QFont("Segoe UI", 8))
            stats_label.setStyleSheet("background: transparent;")
            cl.addWidget(stats_label)

        # Action button
        if mode == "marketplace":
            if info.get("installed", False):
                il = QLabel("  Installed")
                il.setStyleSheet(
                    f"color: {self.app.colors.get('success', '#a6e3a1')}; "
                    f"font-weight: bold; background: transparent;"
                )
                cl.addWidget(il)
            else:
                ib = _icon_btn("Install", "install", "success")
                ib.clicked.connect(lambda _, ei=info: self._install(ei))
                cl.addWidget(ib)
        else:
            ub = _icon_btn("Uninstall", "uninstall", "danger")
            ub.clicked.connect(lambda _, ei=info: self._uninstall(ei))
            cl.addWidget(ub)

        self.results_layout.addWidget(card)

    def _install(self, info):
        name = info.get("name", "extension")
        self._pending_install_name = name
        self.status_label.setText(f"Installing {name}...")
        self.app.set_status(f"Installing {name}...")

        def _callback(success, message):
            # Background thread — emit signal
            self.signals.install_done.emit(success, message)

        self.ext_manager.install_extension(info, _callback)

    def _handle_install_done(self, success, message):
        """Called on main thread via signal."""
        self.status_label.setText(message)
        self.app.set_status(message)

        if success:
            QMessageBox.information(self, "Installed", message)
            # Refresh search results
            if self._last_query:
                self._on_search()
        else:
            QMessageBox.warning(self, "Install Failed", message)

    def _uninstall(self, info):
        eid = info.get("id", "")
        name = info.get("name", eid)
        if QMessageBox.question(
            self, "Uninstall", f"Uninstall {name}?"
        ) != QMessageBox.StandardButton.Yes:
            return
        ok, msg = self.ext_manager.uninstall_extension(eid)
        if ok:
            self.app.set_status(msg)
            self._show_installed()
        else:
            QMessageBox.warning(self, "Failed", msg)

    def _clear(self):
        while self.results_layout.count():
            child = self.results_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()


class Sidebar(QWidget):
    """Sidebar with icon tab bar and stacked panels."""

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.setFixedWidth(app.settings["sidebar_width"])

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Tab bar with icons
        btn_row = QHBoxLayout()
        btn_row.setContentsMargins(4, 4, 4, 0)
        btn_row.setSpacing(2)

        self.tab_buttons = {}
        tabs = [
            ("explorer", "files", "Explorer"),
            ("git", "git", "Git"),
            ("extensions", "extensions", "Extensions"),
        ]

        for tab_id, icon_name, tooltip in tabs:
            btn = QPushButton()
            btn.setIcon(svg_icon(icon_name, 18))
            btn.setToolTip(tooltip)
            btn.setFixedSize(36, 32)
            btn.setCheckable(True)
            btn.setProperty("cssClass", "icon")
            btn.clicked.connect(lambda _, t=tab_id: self._switch(t))
            btn_row.addWidget(btn)
            self.tab_buttons[tab_id] = btn

        btn_row.addStretch()
        layout.addLayout(btn_row)
        layout.addWidget(_sep())

        # Panels
        self.stack = QStackedWidget()

        self.explorer_panel = ExplorerPanel(app)
        self.stack.addWidget(self.explorer_panel)

        self.git_panel = GitPanel(app)
        self.stack.addWidget(self.git_panel)

        self.extensions_panel = ExtensionsPanel(app)
        self.stack.addWidget(self.extensions_panel)

        layout.addWidget(self.stack, 1)

        self.file_tree = self.explorer_panel.file_tree
        self._switch("explorer")

    def _switch(self, panel_id):
        panels = {"explorer": 0, "git": 1, "extensions": 2}
        self.stack.setCurrentIndex(panels.get(panel_id, 0))
        for tid, btn in self.tab_buttons.items():
            btn.setChecked(tid == panel_id)