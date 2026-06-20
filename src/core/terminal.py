"""Full interactive terminal — VS Code style with round buttons."""

import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import subprocess
import threading
import os
import sys
import signal
import shutil

from src.utils.icon_manager import IconManager
from src.utils.styles import make_round_btn, make_icon_btn


def detect_available_shells():
    shells = []

    if sys.platform == "win32":
        pwsh = shutil.which("pwsh")
        if pwsh:
            shells.append(("PowerShell 7", pwsh, [pwsh, "-NoLogo", "-NoExit", "-Command", "-"]))
        ps_path = shutil.which("powershell")
        if ps_path:
            shells.append(("PowerShell", ps_path, [ps_path, "-NoLogo", "-NoExit", "-Command", "-"]))
        cmd_path = shutil.which("cmd")
        if cmd_path:
            shells.append(("CMD", cmd_path, [cmd_path]))
        for gbp in [r"C:\Program Files\Git\bin\bash.exe", r"C:\Program Files (x86)\Git\bin\bash.exe"]:
            if os.path.exists(gbp):
                shells.append(("Git Bash", gbp, [gbp, "--login", "-i"]))
                break
        wsl_path = shutil.which("wsl")
        if wsl_path:
            shells.append(("WSL", wsl_path, [wsl_path]))
    elif sys.platform == "darwin":
        for name, cmd in [("Zsh", "zsh"), ("Bash", "bash"), ("Fish", "fish")]:
            p = shutil.which(cmd)
            if p:
                shells.append((name, p, [p, "-i"]))
    else:
        for name, cmd in [("Bash", "bash"), ("Zsh", "zsh"), ("Fish", "fish"), ("sh", "sh")]:
            p = shutil.which(cmd)
            if p:
                shells.append((name, p, [p, "-i"]))

    if not shells:
        if sys.platform == "win32":
            shells.append(("CMD", "cmd.exe", ["cmd.exe"]))
        else:
            shells.append(("sh", "/bin/sh", ["/bin/sh", "-i"]))

    return shells


class Terminal:
    """Full interactive terminal."""

    def __init__(self, parent, app):
        self.app = app
        self.process = None
        self.visible = True
        self.running = False
        self.icon_mgr = IconManager()
        self._icon_refs = []
        self.read_thread = None

        self.available_shells = detect_available_shells()
        self.current_shell_idx = 0

        self.frame = ttk.Frame(parent)
        self._build_ui()
        self._start_shell()

    def _build_ui(self):
        # Header
        header = ttk.Frame(self.frame, padding=(8, 4, 8, 4))
        header.pack(fill=X)

        term_icon = self.icon_mgr.get("terminal", 14)
        self._icon_refs.append(term_icon)

        ttk.Label(
            header,
            text=" TERMINAL",
            image=term_icon,
            compound=LEFT,
            font=("Segoe UI", 9, "bold"),
            foreground="#a6adc8",
        ).pack(side=LEFT)

        # Right buttons
        close_icon = self.icon_mgr.get("close", 14)
        make_icon_btn(
            header, close_icon,
            self.toggle, "danger",
            self._icon_refs,
        ).pack(side=RIGHT, padx=1)

        run_icon = self.icon_mgr.get("run", 14)
        make_round_btn(
            header, "Restart", run_icon,
            self.restart_shell, "success",
            self._icon_refs, "small",
        ).pack(side=RIGHT, padx=2)

        clear_icon = self.icon_mgr.get("clear", 14)
        make_round_btn(
            header, "Clear", clear_icon,
            self.clear, "secondary",
            self._icon_refs, "small",
        ).pack(side=RIGHT, padx=2)

        # Shell selector
        shell_names = [s[0] for s in self.available_shells]
        self.shell_var = tk.StringVar(value=shell_names[0])

        self.shell_selector = ttk.Combobox(
            header,
            textvariable=self.shell_var,
            values=shell_names,
            state="readonly",
            width=14,
            font=("Segoe UI", 9),
        )
        self.shell_selector.pack(side=RIGHT, padx=(0, 8))
        self.shell_selector.bind("<<ComboboxSelected>>", self._on_shell_changed)

        # Output
        output_frame = ttk.Frame(self.frame)
        output_frame.pack(fill=BOTH, expand=True)

        self.output = tk.Text(
            output_frame,
            height=10,
            bg=self.app.colors["terminal_bg"],
            fg=self.app.colors["terminal_fg"],
            insertbackground=self.app.colors["accent"],
            font=(self.app.settings["font_family"], self.app.settings["font_size"] - 1),
            relief="flat",
            borderwidth=0,
            padx=10,
            pady=6,
            wrap="word",
        )

        scrollbar = ttk.Scrollbar(
            output_frame, orient=tk.VERTICAL, command=self.output.yview
        )
        self.output.configure(yscrollcommand=scrollbar.set)

        self.output.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=tk.Y)

        self.output.tag_configure("error", foreground="#f38ba8")
        self.output.tag_configure("info", foreground="#89b4fa")
        self.output.tag_configure("success", foreground="#a6e3a1")

        # Input
        input_frame = ttk.Frame(self.frame, padding=(8, 2, 8, 4))
        input_frame.pack(fill=X)

        self.prompt_label = ttk.Label(
            input_frame,
            text=" > ",
            font=(self.app.settings["font_family"], self.app.settings["font_size"] - 1, "bold"),
            foreground=self.app.colors.get("accent", "#89b4fa"),
        )
        self.prompt_label.pack(side=LEFT)

        self.input_entry = ttk.Entry(
            input_frame,
            font=(self.app.settings["font_family"], self.app.settings["font_size"] - 1),
        )
        self.input_entry.pack(side=LEFT, fill=X, expand=True, padx=(0, 4))
        self.input_entry.bind("<Return>", self._send_input)
        self.input_entry.bind("<Up>", self._history_up)
        self.input_entry.bind("<Down>", self._history_down)
        self.input_entry.bind("<Control-c>", self._send_interrupt)

        send_icon = self.icon_mgr.get("arrow_right", 14)
        make_round_btn(
            input_frame, "Send", send_icon,
            self._send_input, "info",
            self._icon_refs, "small",
        ).pack(side=RIGHT)

        self.history = []
        self.history_idx = -1

    def _on_shell_changed(self, event=None):
        selected = self.shell_var.get()
        for i, (name, _, _) in enumerate(self.available_shells):
            if name == selected:
                self.current_shell_idx = i
                break
        self.restart_shell()

    def _start_shell(self):
        self._stop_shell()
        name, path, cmd = self.available_shells[self.current_shell_idx]
        self._write_output(f"--- Starting {name} ---\n", "info")

        try:
            env = os.environ.copy()
            env["TERM"] = "dumb"
            env["NO_COLOR"] = "1"
            cwd = self.app.current_project_path or os.getcwd()

            kwargs = {
                "stdin": subprocess.PIPE,
                "stdout": subprocess.PIPE,
                "stderr": subprocess.STDOUT,
                "cwd": cwd,
                "env": env,
                "bufsize": 0,
            }

            if sys.platform == "win32":
                kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW | subprocess.CREATE_NEW_PROCESS_GROUP
            else:
                kwargs["preexec_fn"] = os.setsid

            self.process = subprocess.Popen(cmd, **kwargs)
            self.running = True

            self.read_thread = threading.Thread(target=self._read_output, daemon=True)
            self.read_thread.start()

            self._write_output(f"{name} ready.\n\n", "success")
        except FileNotFoundError:
            self._write_output(f"Error: {name} not found\n", "error")
            self.running = False
        except Exception as e:
            self._write_output(f"Error: {e}\n", "error")
            self.running = False

    def _stop_shell(self):
        self.running = False
        if self.process:
            try:
                if sys.platform == "win32":
                    self.process.terminate()
                else:
                    os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
            except (ProcessLookupError, OSError):
                pass
            try:
                self.process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                try:
                    self.process.kill()
                except Exception:
                    pass
            self.process = None

    def restart_shell(self):
        self.clear()
        self._start_shell()

    def _read_output(self):
        try:
            while self.running and self.process and self.process.poll() is None:
                try:
                    data = self.process.stdout.read(4096)
                    if data:
                        text = data.decode("utf-8", errors="replace")
                        self.output.after(0, self._write_output, text)
                    else:
                        break
                except (ValueError, OSError):
                    break
        except Exception:
            pass
        self.output.after(0, self._on_shell_exit)

    def _on_shell_exit(self):
        self.running = False
        self._write_output("\n--- Shell exited ---\n", "error")

    def _send_input(self, event=None):
        cmd = self.input_entry.get()
        self.input_entry.delete(0, "end")

        if cmd.strip():
            self.history.append(cmd)
            self.history_idx = len(self.history)

        if not self.running or not self.process:
            self._write_output("Shell not running. Click Restart.\n", "error")
            return

        try:
            self.process.stdin.write((cmd + "\n").encode("utf-8"))
            self.process.stdin.flush()
        except (BrokenPipeError, OSError) as e:
            self._write_output(f"Error: {e}\n", "error")
            self.running = False

    def _send_interrupt(self, event=None):
        if self.process and self.running:
            try:
                if sys.platform == "win32":
                    self.process.send_signal(signal.CTRL_BREAK_EVENT)
                else:
                    os.killpg(os.getpgid(self.process.pid), signal.SIGINT)
            except (ProcessLookupError, OSError):
                pass
        return "break"

    def _history_up(self, event=None):
        if self.history and self.history_idx > 0:
            self.history_idx -= 1
            self.input_entry.delete(0, "end")
            self.input_entry.insert(0, self.history[self.history_idx])
        return "break"

    def _history_down(self, event=None):
        if self.history_idx < len(self.history) - 1:
            self.history_idx += 1
            self.input_entry.delete(0, "end")
            self.input_entry.insert(0, self.history[self.history_idx])
        elif self.history_idx == len(self.history) - 1:
            self.history_idx = len(self.history)
            self.input_entry.delete(0, "end")
        return "break"

    def _write_output(self, text, tag=None):
        try:
            self.output.configure(state="normal")
            if tag:
                self.output.insert("end", text, tag)
            else:
                self.output.insert("end", text)
            self.output.see("end")

            line_count = int(self.output.index("end-1c").split(".")[0])
            if line_count > 10000:
                self.output.delete("1.0", "1000.0")
        except Exception:
            pass

    def clear(self):
        self.output.configure(state="normal")
        self.output.delete("1.0", "end")

    def toggle(self):
        if self.visible:
            self.frame.pack_forget()
            self.visible = False
        else:
            self.frame.pack(fill=BOTH, expand=False)
            self.visible = True
            self.input_entry.focus_set()

    def destroy(self):
        self._stop_shell()