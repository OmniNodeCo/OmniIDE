"""Sidebar — PyQt6 with tabbed panels."""

import os

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QTreeView, QScrollArea,
    QStackedWidget, QLineEdit, QMessageBox,
)
from PyQt6.QtCore import Qt, QDir, QModelIndex
from PyQt6.QtGui import QFont, QFileSystemModel

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


class SidebarPanel(QWidget):
    """Base class for sidebar panels."""

    def __init__(self, title, app):
        super().__init__()
        self.app = app
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        header = QLabel(title.upper())
        header.setProperty("cssClass", "header")
        layout.addWidget(header)

        sep = QFrame()
        sep.setProperty("cssClass", "separator")
        sep.setFixedHeight(1)
        layout.addWidget(sep)

        self.content_layout = layout


class ExplorerPanel(SidebarPanel):
    """File explorer panel."""

    def __init__(self, app):
        super().__init__("Explorer", app)

        btn_row = QHBoxLayout()

        new_btn = QPushButton("New File")
        new_btn.setProperty("cssClass", "primary")
        new_btn.clicked.connect(app.file_manager.new_file)
        btn_row.addWidget(new_btn)

        open_btn = QPushButton("Open File")
        open_btn.clicked.connect(app.file_manager.open_file)
        btn_row.addWidget(open_btn)

        self.content_layout.addLayout(btn_row)

        open_folder = QPushButton("Open Folder")
        open_folder.clicked.connect(lambda: app.open_project())
        self.content_layout.addWidget(open_folder)

        sep = QFrame()
        sep.setProperty("cssClass", "separator")
        sep.setFixedHeight(1)
        self.content_layout.addWidget(sep)

        self.file_tree = FileTree(app)
        self.content_layout.addWidget(self.file_tree, 1)


class GitPanel(SidebarPanel):
    """Git source control panel."""

    def __init__(self, app):
        super().__init__("Source Control", app)

        gm = app.git_manager

        sections = [
            ("Repository", [
                ("Clone", gm.clone_repo),
                ("Init", gm.init_repo),
                ("Set Remote", gm.add_remote),
            ]),
            ("Changes", [
                ("Status", gm.git_status),
                ("Diff", gm.git_diff),
                ("Stage All", gm.git_add_all),
            ]),
            ("Commit & Sync", [
                ("Commit", gm.git_commit),
                ("Push", gm.git_push),
                ("Pull", gm.git_pull),
            ]),
            ("History", [
                ("Log", gm.git_log),
                ("Branches", gm.git_branch),
            ]),
        ]

        for section_name, buttons in sections:
            label = QLabel(f"  {section_name}")
            label.setProperty("cssClass", "dim")
            label.setFont(QFont("Segoe UI", 8))
            self.content_layout.addWidget(label)

            for text, callback in buttons:
                btn = QPushButton(text)
                btn.clicked.connect(callback)
                self.content_layout.addWidget(btn)

            sep = QFrame()
            sep.setProperty("cssClass", "separator")
            sep.setFixedHeight(1)
            self.content_layout.addWidget(sep)

        self.content_layout.addStretch()


class ExtensionsPanel(SidebarPanel):
    """Extensions marketplace panel."""

    def __init__(self, app):
        super().__init__("Extensions", app)
        self.ext_manager = app.extension_manager

        # Search
        search_row = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search extensions...")
        self.search_input.returnPressed.connect(self._on_search)
        search_row.addWidget(self.search_input, 1)

        search_btn = QPushButton("Search")
        search_btn.setProperty("cssClass", "primary")
        search_btn.clicked.connect(self._on_search)
        search_row.addWidget(search_btn)

        self.content_layout.addLayout(search_row)

        # Status
        self.status_label = QLabel("Search for extensions above")
        self.status_label.setProperty("cssClass", "dim")
        self.content_layout.addWidget(self.status_label)

        # Tab buttons
        tab_row = QHBoxLayout()

        self.marketplace_btn = QPushButton("Marketplace")
        self.marketplace_btn.setProperty("cssClass", "primary")
        self.marketplace_btn.clicked.connect(lambda: self._switch_tab("marketplace"))
        tab_row.addWidget(self.marketplace_btn)

        self.installed_btn = QPushButton("Installed")
        self.installed_btn.clicked.connect(lambda: self._switch_tab("installed"))
        tab_row.addWidget(self.installed_btn)

        self.content_layout.addLayout(tab_row)

        # Results scroll area
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.results_widget = QWidget()
        self.results_layout = QVBoxLayout(self.results_widget)
        self.results_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll.setWidget(self.results_widget)
        self.content_layout.addWidget(self.scroll, 1)

        self.current_tab = "marketplace"

    def _switch_tab(self, tab):
        self.current_tab = tab
        if tab == "installed":
            self._show_installed()
        else:
            self._clear_results()
            self.status_label.setText("Search for extensions above")

    def _on_search(self):
        query = self.search_input.text().strip()
        if not query:
            return

        self.current_tab = "marketplace"
        self._clear_results()
        self.status_label.setText("Searching...")
        self.app.set_status(f"Searching: {query}")

        self.ext_manager.search(query, self._on_results)

    def _on_results(self, results, error):
        self._clear_results()

        if error:
            self.status_label.setText(f"Error: {error}")
            return
        if not results:
            self.status_label.setText("No extensions found.")
            return

        self.status_label.setText(f"{len(results)} found")
        for ext in results:
            self._add_card(ext, "marketplace")

    def _show_installed(self):
        self._clear_results()
        installed = self.ext_manager.get_installed()
        if not installed:
            self.status_label.setText("No extensions installed.")
            return
        self.status_label.setText(f"{len(installed)} installed")
        for ext in installed:
            self._add_card(ext, "installed")

    def _add_card(self, ext_info, mode):
        card = QFrame()
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(8, 6, 8, 6)
        card_layout.setSpacing(2)

        # Name + version
        name_row = QHBoxLayout()
        name = QLabel(ext_info.get("name", ext_info.get("id", "Unknown")))
        name.setFont(QFont("Segoe UI", 10))
        name.setStyleSheet("font-weight: bold;")
        name_row.addWidget(name)

        ver = QLabel(f"v{ext_info.get('version', '')}")
        ver.setProperty("cssClass", "dim")
        name_row.addWidget(ver)
        name_row.addStretch()
        card_layout.addLayout(name_row)

        # Publisher
        pub = ext_info.get("publisher", "")
        if pub:
            pub_label = QLabel(pub)
            pub_label.setProperty("cssClass", "accent")
            pub_label.setFont(QFont("Segoe UI", 8))
            card_layout.addWidget(pub_label)

        # Description
        desc = ext_info.get("description", "")
        if desc:
            desc_label = QLabel(
                desc[:120] + ("..." if len(desc) > 120 else "")
            )
            desc_label.setWordWrap(True)
            desc_label.setProperty("cssClass", "dim")
            card_layout.addWidget(desc_label)

        # Stats
        if mode == "marketplace":
            installs = ext_info.get("installs", 0)
            stats = QLabel(
                f"Downloads: {ExtensionManager.format_installs(installs)}"
            )
            stats.setProperty("cssClass", "dim")
            stats.setFont(QFont("Segoe UI", 8))
            card_layout.addWidget(stats)

        # Action button
        if mode == "marketplace":
            if ext_info.get("installed", False):
                installed_label = QLabel("Installed")
                installed_label.setStyleSheet(
                    f"color: {self.app.colors.get('success', '#a6e3a1')}; "
                    f"font-weight: bold;"
                )
                card_layout.addWidget(installed_label)
            else:
                install_btn = QPushButton("Install")
                install_btn.setProperty("cssClass", "success")
                install_btn.clicked.connect(
                    lambda checked, ei=ext_info: self._install(ei)
                )
                card_layout.addWidget(install_btn)
        else:
            uninstall_btn = QPushButton("Uninstall")
            uninstall_btn.setProperty("cssClass", "danger")
            uninstall_btn.clicked.connect(
                lambda checked, ei=ext_info: self._uninstall(ei)
            )
            card_layout.addWidget(uninstall_btn)

        self.results_layout.addWidget(card)

        sep = QFrame()
        sep.setProperty("cssClass", "separator")
        sep.setFixedHeight(1)
        self.results_layout.addWidget(sep)

    def _install(self, ext_info):
        name = ext_info.get("name", "extension")
        self.status_label.setText(f"Installing {name}...")
        self.app.set_status(f"Installing {name}...")

        def _on_done(success, message):
            self.status_label.setText(message)
            self.app.set_status(message)
            if success:
                QMessageBox.information(self, "Installed", message)
                self._on_search()
            else:
                QMessageBox.warning(self, "Failed", message)

        self.ext_manager.install_extension(ext_info, _on_done)

    def _uninstall(self, ext_info):
        ext_id = ext_info.get("id", "")
        name = ext_info.get("name", ext_id)

        result = QMessageBox.question(
            self, "Uninstall", f"Uninstall {name}?"
        )
        if result != QMessageBox.StandardButton.Yes:
            return

        ok, msg = self.ext_manager.uninstall_extension(ext_id)
        if ok:
            self.app.set_status(msg)
            self._show_installed()
        else:
            QMessageBox.warning(self, "Failed", msg)

    def _clear_results(self):
        while self.results_layout.count():
            child = self.results_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()


class Sidebar(QWidget):
    """Sidebar with tab buttons and stacked panels."""

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.setFixedWidth(app.settings["sidebar_width"])

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Tab buttons
        btn_row = QHBoxLayout()
        btn_row.setContentsMargins(4, 4, 4, 0)
        btn_row.setSpacing(2)

        self.tab_buttons = {}
        tabs = [
            ("explorer", "Explorer"),
            ("git", "Git"),
            ("extensions", "Ext"),
        ]

        for tab_id, label in tabs:
            btn = QPushButton(label)
            btn.setCheckable(True)
            btn.clicked.connect(
                lambda checked, t=tab_id: self._switch(t)
            )
            btn_row.addWidget(btn)
            self.tab_buttons[tab_id] = btn

        layout.addLayout(btn_row)

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