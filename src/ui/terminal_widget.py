"""Interactive terminal with multiple shell tabs — PyQt6."""

import os
import sys
import shutil

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPlainTextEdit,
    QLineEdit, QPushButton, QComboBox, QLabel, QTabWidget, QMenu,
)
from PyQt6.QtCore import Qt, QProcess, QProcessEnvironment
from PyQt6.QtGui import QFont, QTextCursor


def detect_shells():
    shells = []
    if sys.platform == "win32":
        for name, cmd in [("PowerShell", "powershell"), ("CMD", "cmd")]:
            if shutil.which(cmd):
                shells.append((name, cmd))
        pwsh = shutil.which("pwsh")
        if pwsh:
            shells.insert(0, ("PowerShell 7", "pwsh"))
    elif sys.platform == "darwin":
        for name, cmd in [("Zsh", "zsh"), ("Bash", "bash")]:
            if shutil.which(cmd):
                shells.append((name, cmd))
    else:
        for name, cmd in [("Bash", "bash"), ("Zsh", "zsh"), ("sh", "sh")]:
            if shutil.which(cmd):
                shells.append((name, cmd))
    if not shells:
        shells.append(("sh", "sh"))
    return shells


class TerminalInstance(QWidget):
    """One interactive shell session."""

    def __init__(self, app, shells, shell_index=0, title="Shell"):
        super().__init__()
        self.app = app
        self.shells = shells
        self.process = None
        self.history = []
        self.history_idx = -1

        c = app.colors
        font = QFont(app.settings["font_family"], max(9, app.settings["font_size"] - 1))
        font.setFixedPitch(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.shell_combo = QComboBox()
        for name, _ in shells:
            self.shell_combo.addItem(name)
        if 0 <= shell_index < len(shells):
            self.shell_combo.setCurrentIndex(shell_index)
        self.shell_combo.currentIndexChanged.connect(self._restart)

        # Output
        self.output = QPlainTextEdit()
        self.output.setReadOnly(True)
        self.output.setFont(font)
        self.output.setStyleSheet(f"""
            QPlainTextEdit {{
                background-color: {c['terminal_bg']};
                color: {c['terminal_fg']};
                border: none;
                padding: 6px;
            }}
        """)

        # Input
        input_row = QHBoxLayout()
        input_row.setContentsMargins(8, 2, 8, 4)

        self.prompt = QLabel(">")
        self.prompt.setStyleSheet(f"color: {c['accent']}; font-weight: bold;")
        input_row.addWidget(self.prompt)

        self.input_field = QLineEdit()
        self.input_field.setFont(font)
        self.input_field.setPlaceholderText("Type a command...")
        self.input_field.returnPressed.connect(self._send)
        input_row.addWidget(self.input_field, 1)

        send_btn = QPushButton("Send")
        send_btn.setProperty("cssClass", "primary")
        send_btn.clicked.connect(self._send)
        input_row.addWidget(send_btn)

        layout.addWidget(self.output, 1)
        layout.addLayout(input_row)

        self._start_shell()

    def current_shell(self):
        idx = self.shell_combo.currentIndex()
        if 0 <= idx < len(self.shells):
            return self.shells[idx]
        return self.shells[0]

    def _start_shell(self):
        self.stop_shell()

        name, cmd = self.current_shell()
        shell_path = shutil.which(cmd) or cmd

        self._write(f"--- Starting {name} ---\n")

        self.process = QProcess(self)
        self.process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        self.process.readyReadStandardOutput.connect(self._read_output)
        self.process.finished.connect(self._on_finished)

        env = QProcessEnvironment.systemEnvironment()
        env.insert("TERM", "dumb")
        env.insert("NO_COLOR", "1")
        self.process.setProcessEnvironment(env)

        cwd = self.app.current_project_path or os.getcwd()
        self.process.setWorkingDirectory(cwd)

        if sys.platform == "win32":
            if "powershell" in cmd.lower() or "pwsh" in cmd.lower():
                self.process.start(shell_path, ["-NoLogo", "-NoExit", "-Command", "-"])
            else:
                self.process.start(shell_path)
        else:
            self.process.start(shell_path, ["-i"])

    def stop_shell(self):
        if self.process and self.process.state() != QProcess.ProcessState.NotRunning:
            self.process.kill()
            self.process.waitForFinished(2000)
            self.process = None

    def _restart(self):
        self.clear()
        self._start_shell()

    def _send(self):
        text = self.input_field.text()
        self.input_field.clear()

        if text.strip():
            self.history.append(text)
            self.history_idx = len(self.history)

        if self.process and self.process.state() == QProcess.ProcessState.Running:
            self.process.write((text + "\n").encode())
        else:
            self._write("Shell not running. Click Restart.\n")

    def _read_output(self):
        if self.process:
            data = self.process.readAllStandardOutput()
            text = bytes(data).decode("utf-8", errors="replace")
            self._write(text)

    def _on_finished(self):
        self._write("\n--- Shell exited ---\n")

    def _write(self, text):
        self.output.moveCursor(QTextCursor.MoveOperation.End)
        self.output.insertPlainText(text)
        self.output.moveCursor(QTextCursor.MoveOperation.End)

    def clear(self):
        self.output.clear()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Up:
            if self.history and self.history_idx > 0:
                self.history_idx -= 1
                self.input_field.setText(self.history[self.history_idx])
        elif event.key() == Qt.Key.Key_Down:
            if self.history_idx < len(self.history) - 1:
                self.history_idx += 1
                self.input_field.setText(self.history[self.history_idx])
            else:
                self.history_idx = len(self.history)
                self.input_field.clear()
        else:
            super().keyPressEvent(event)


class TerminalWidget(QWidget):
    """Terminal container hosting multiple shell tabs."""

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.shells = detect_shells()
        self.counter = 0

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header
        header = QHBoxLayout()
        header.setContentsMargins(8, 4, 8, 4)

        header.addWidget(QLabel("TERMINAL"))
        header.addStretch()

        new_btn = QPushButton("+")
        new_btn.setFixedWidth(28)
        new_btn.setToolTip("New Terminal (Ctrl+Shift+T)")
        new_btn.clicked.connect(self.new_terminal)
        header.addWidget(new_btn)

        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self.clear)
        header.addWidget(clear_btn)

        restart_btn = QPushButton("Restart")
        restart_btn.setProperty("cssClass", "primary")
        restart_btn.clicked.connect(self._restart)
        header.addWidget(restart_btn)

        layout.addLayout(header)

        # Tabs
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self._close_tab)
        self.tabs.tabBar().setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tabs.tabBar().customContextMenuRequested.connect(self._context_menu)
        layout.addWidget(self.tabs, 1)

        self.new_terminal()

    # ── Tab management ─────────────────────────────────────────────
    def new_terminal(self, shell_index=0):
        self.counter += 1
        inst = TerminalInstance(self.app, self.shells,
                                shell_index=shell_index,
                                title=f"Shell {self.counter}")
        idx = self.tabs.addTab(inst, f"Shell {self.counter}")
        self.tabs.setCurrentIndex(idx)
        return inst

    def current(self):
        return self.tabs.currentWidget()

    def _close_tab(self, index):
        inst = self.tabs.widget(index)
        if self.tabs.count() == 1:
            # Keep at least one: restart it instead
            inst._restart()
            return
        inst.stop_shell()
        self.tabs.removeTab(index)
        if hasattr(inst, "deleteLater"):
            inst.deleteLater()

    def _context_menu(self, pos):
        index = self.tabs.tabBar().tabAt(pos)
        if index < 0:
            return
        menu = QMenu(self)
        menu.addAction("New Terminal", self.new_terminal)
        menu.addSeparator()
        menu.addAction("Clear", lambda: self.tabs.widget(index).clear())
        menu.addAction("Restart", lambda: self.tabs.widget(index)._restart())
        menu.exec(self.tabs.tabBar().mapToGlobal(pos))

    # ── Backward-compatible single-terminal API ────────────────────
    def clear(self):
        inst = self.current()
        if inst:
            inst.clear()

    def _restart(self):
        inst = self.current()
        if inst:
            inst._restart()

    def restart_shell(self):
        self._restart()

    def stop_shell(self):
        for i in range(self.tabs.count()):
            self.tabs.widget(i).stop_shell()

    # Legacy attribute access for old code paths
    @property
    def output(self):
        inst = self.current()
        return inst.output if inst else None

    @property
    def input_field(self):
        inst = self.current()
        return inst.input_field if inst else None

    @property
    def shell_combo(self):
        inst = self.current()
        return inst.shell_combo if inst else None

    @property
    def process(self):
        inst = self.current()
        return inst.process if inst else None
