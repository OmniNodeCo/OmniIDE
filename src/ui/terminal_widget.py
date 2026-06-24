"""Interactive terminal — PyQt6."""

import os
import sys
import shutil
import signal

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPlainTextEdit,
    QLineEdit, QPushButton, QComboBox, QLabel,
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


class TerminalWidget(QWidget):
    """Interactive terminal with real shell."""

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.process = None
        self.history = []
        self.history_idx = -1

        self.shells = detect_shells()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header
        header = QHBoxLayout()
        header.setContentsMargins(8, 4, 8, 4)

        header.addWidget(QLabel("TERMINAL"))

        self.shell_combo = QComboBox()
        for name, cmd in self.shells:
            self.shell_combo.addItem(name, cmd)
        self.shell_combo.currentIndexChanged.connect(self._restart)
        header.addWidget(self.shell_combo)

        header.addStretch()

        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self.clear)
        header.addWidget(clear_btn)

        restart_btn = QPushButton("Restart")
        restart_btn.setProperty("cssClass", "primary")
        restart_btn.clicked.connect(self._restart)
        header.addWidget(restart_btn)

        layout.addLayout(header)

        # Output
        self.output = QPlainTextEdit()
        self.output.setReadOnly(True)
        font = QFont(app.settings["font_family"], app.settings["font_size"] - 1)
        font.setFixedPitch(True)
        self.output.setFont(font)
        c = app.colors
        self.output.setStyleSheet(f"""
            QPlainTextEdit {{
                background-color: {c['terminal_bg']};
                color: {c['terminal_fg']};
                border: none;
                padding: 6px;
            }}
        """)
        layout.addWidget(self.output, 1)

        # Input
        input_row = QHBoxLayout()
        input_row.setContentsMargins(8, 2, 8, 4)

        self.prompt = QLabel(">")
        self.prompt.setStyleSheet(f"color: {c['accent']}; font-weight: bold;")
        input_row.addWidget(self.prompt)

        self.input_field = QLineEdit()
        self.input_field.setFont(font)
        self.input_field.returnPressed.connect(self._send)
        input_row.addWidget(self.input_field, 1)

        send_btn = QPushButton("Send")
        send_btn.setProperty("cssClass", "primary")
        send_btn.clicked.connect(self._send)
        input_row.addWidget(send_btn)

        layout.addLayout(input_row)

        self._start_shell()

    def _start_shell(self):
        self.stop_shell()

        idx = self.shell_combo.currentIndex()
        name, cmd = self.shells[idx]
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