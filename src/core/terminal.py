"""Full interactive terminal with shell selection."""

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


def detect_available_shells():
    """Detect available shells on the current OS."""
    shells = []

    if sys.platform == "win32":
        # PowerShell 7+ (pwsh)
        pwsh = shutil.which("pwsh")
        if pwsh:
            shells.append(("PowerShell 7", pwsh, [pwsh, "-NoLogo", "-NoExit", "-Command", "-"]))

        # Windows PowerShell
        ps_path = shutil.which("powershell")
        if ps_path:
            shells.append(("PowerShell", ps_path, [ps_path, "-NoLogo", "-NoExit", "-Command", "-"]))

        # CMD
        cmd_path = shutil.which("cmd")
        if cmd_path:
            shells.append(("CMD", cmd_path, [cmd_path]))

        # Git Bash
        git_bash_paths = [
            r"C:\Program Files\Git\bin\bash.exe",
            r"C:\Program Files (x86)\Git\bin\bash.exe",
        ]
        for gbp in git_bash_paths:
            if os.path.exists(gbp):
                shells.append(("Git Bash", gbp, [gbp, "--login", "-i"]))
                break

        # WSL
        wsl_path = shutil.which("wsl")
        if wsl_path:
            shells.append(("WSL", wsl_path, [wsl_path]))

    elif sys.platform == "darwin":
        # macOS
        zsh = shutil.which("zsh")
        if zsh:
            shells.append(("Zsh", zsh, [zsh, "-i"]))

        bash = shutil.which("bash")
        if bash:
            shells.append(("Bash", bash, [bash, "-i"]))

        fish = shutil.which("fish")
        if fish:
            shells.append(("Fish", fish, [fish, "-i"]))

    else:
        # Linux
        bash = shutil.which("bash")
        if bash:
            shells.append(("Bash", bash, [bash, "-i"]))

        zsh = shutil.which("zsh")
        if zsh:
            shells.append(("Zsh", zsh, [zsh, "-i"]))

        fish = shutil.which("fish")
        if fish:
            shells.append(("Fish", fish, [fish, "-i"]))

        sh = shutil.which("sh")
        if sh:
            shells.append(("sh", sh, [sh, "-i"]))

    # Fallback
    if not shells:
        if sys.platform == "win32":
            shells.append(("CMD", "cmd.exe", ["cmd.exe"]))
        else:
            shells.append(("sh", "/bin/sh", ["/bin/sh", "-i"]))

    return shells


class Terminal:
    """Full interactive terminal with real shell process."""

    def __init__(self, parent, app):
        self.app = app
        self.process = None
        self.visible = True
        self.running = False
        self.icon_mgr = IconManager()
        self._icon_refs = []
        self.read_thread = None

        # Detect shells
        self.available_shells = detect_available_shells()
        self.current_shell_idx = 0

        self.frame = ttk.Frame(parent)
        self._build_ui()
        self._start_shell()

    def _build_ui(self):
        """Build terminal UI."""
        # Header bar
        header = ttk.Frame(self.frame)
        header.pack(fill=X, padx=0, pady=0)

        term_icon = self.icon_mgr.get("terminal", 16)
        self._icon_refs.append(term_icon)

        ttk.Label(
            header,
            text=" Terminal",
            image=term_icon,
            compound=LEFT,
            font=("Segoe UI", 10, "bold"),
        ).pack(side=LEFT, padx=(8, 4))

        # Shell selector dropdown
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
        self.shell_selector.pack(side=LEFT, padx=4)
        self.shell_selector.bind("<<ComboboxSelected>>", self._on_shell_changed)

        # Right side buttons
        close_icon = self.icon_mgr.get("close", 16)
        self._icon_refs.append(close_icon)

        ttk.Button(
            header, image=close_icon,
            bootstyle="danger-link",
            command=self.toggle,
        ).pack(side=RIGHT, padx=2)

        # Restart button
        run_icon = self.icon_mgr.get("run", 16)
        self._icon_refs.append(run_icon)

        ttk.Button(
            header,
            text=" Restart",
            image=run_icon,
            compound=LEFT,
            bootstyle="success-outline",
            command=self.restart_shell,
            padding=(6, 2),
        ).pack(side=RIGHT, padx=2)

        clear_icon = self.icon_mgr.get("clear", 16)
        self._icon_refs.append(clear_icon)

        ttk.Button(
            header,
            text=" Clear",
            image=clear_icon,
            compound=LEFT,
            bootstyle="secondary-outline",
            command=self.clear,
            padding=(6, 2),
        ).pack(side=RIGHT, padx=2)

        # Terminal output area
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
            padx=8,
            pady=4,
            wrap="word",
        )

        scrollbar = ttk.Scrollbar(
            output_frame, orient=tk.VERTICAL, command=self.output.yview
        )
        self.output.configure(yscrollcommand=scrollbar.set)

        self.output.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=tk.Y)

        # Configure output tags for colors
        self.output.tag_configure("error", foreground="#f38ba8")
        self.output.tag_configure("info", foreground="#89b4fa")
        self.output.tag_configure("success", foreground="#a6e3a1")
        self.output.tag_configure("prompt", foreground="#cba6f7")

        # Input area
        input_frame = ttk.Frame(self.frame)
        input_frame.pack(fill=X, padx=0, pady=(0, 2))

        self.prompt_label = ttk.Label(
            input_frame,
            text="  > ",
            font=(self.app.settings["font_family"], self.app.settings["font_size"] - 1, "bold"),
            foreground=self.app.colors.get("accent", "#89b4fa"),
        )
        self.prompt_label.pack(side=LEFT)

        self.input_entry = ttk.Entry(
            input_frame,
            font=(self.app.settings["font_family"], self.app.settings["font_size"] - 1),
        )
        self.input_entry.pack(side=LEFT, fill=X, expand=True, padx=(0, 4), pady=2)
        self.input_entry.bind("<Return>", self._send_input)
        self.input_entry.bind("<Up>", self._history_up)
        self.input_entry.bind("<Down>", self._history_down)
        self.input_entry.bind("<Control-c>", self._send_interrupt)

        # Send button
        ttk.Button(
            input_frame,
            text="Send",
            bootstyle="info",
            command=self._send_input,
            padding=(10, 2),
        ).pack(side=RIGHT, padx=(0, 4))

        # Command history
        self.history = []
        self.history_idx = -1

    def _on_shell_changed(self, event=None):
        """Handle shell selection change."""
        selected = self.shell_var.get()
        for i, (name, _, _) in enumerate(self.available_shells):
            if name == selected:
                self.current_shell_idx = i
                break
        self.restart_shell()

    def _start_shell(self):
        """Start the selected shell process."""
        self._stop_shell()

        name, path, cmd = self.available_shells[self.current_shell_idx]

        self._write_output(f"--- Starting {name} ({path}) ---\n", "info")

        try:
            # Environment setup
            env = os.environ.copy()
            env["TERM"] = "dumb"
            env["NO_COLOR"] = "1"

            cwd = self.app.current_project_path or os.getcwd()

            # Platform-specific process creation
            kwargs = {
                "stdin": subprocess.PIPE,
                "stdout": subprocess.PIPE,
                "stderr": subprocess.STDOUT,
                "cwd": cwd,
                "env": env,
                "bufsize": 0,
            }

            if sys.platform == "win32":
                kwargs["creationflags"] = (
                    subprocess.CREATE_NO_WINDOW |
                    subprocess.CREATE_NEW_PROCESS_GROUP
                )
            else:
                kwargs["preexec_fn"] = os.setsid

            self.process = subprocess.Popen(cmd, **kwargs)
            self.running = True

            # Start reading thread
            self.read_thread = threading.Thread(
                target=self._read_output, daemon=True
            )
            self.read_thread.start()

            self._write_output(f"{name} ready.\n\n", "success")

        except FileNotFoundError:
            self._write_output(f"Error: {name} not found at {path}\n", "error")
            self.running = False
        except Exception as e:
            self._write_output(f"Error starting shell: {e}\n", "error")
            self.running = False

    def _stop_shell(self):
        """Stop the current shell process."""
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
        """Restart the shell."""
        self.clear()
        self._start_shell()

    def _read_output(self):
        """Background thread: read shell stdout and display it."""
        try:
            while self.running and self.process and self.process.poll() is None:
                try:
                    data = self.process.stdout.read(4096)
                    if data:
                        text = data.decode("utf-8", errors="replace")
                        # Schedule UI update on main thread
                        self.output.after(0, self._write_output, text)
                    else:
                        break
                except (ValueError, OSError):
                    break
        except Exception:
            pass

        self.output.after(0, self._on_shell_exit)

    def _on_shell_exit(self):
        """Called when shell process exits."""
        self.running = False
        self._write_output("\n--- Shell exited ---\n", "error")

    def _send_input(self, event=None):
        """Send input to the shell process."""
        cmd = self.input_entry.get()
        if not cmd and event:
            # Send empty line
            cmd = ""

        self.input_entry.delete(0, "end")

        # Add to history
        if cmd.strip():
            self.history.append(cmd)
            self.history_idx = len(self.history)

        if not self.running or not self.process:
            self._write_output(
                "Shell not running. Click 'Restart' to start.\n", "error"
            )
            return

        try:
            line = cmd + "\n"
            self.process.stdin.write(line.encode("utf-8"))
            self.process.stdin.flush()
        except (BrokenPipeError, OSError) as e:
            self._write_output(f"Error sending input: {e}\n", "error")
            self.running = False

    def _send_interrupt(self, event=None):
        """Send Ctrl+C to the shell."""
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
        """Navigate command history up."""
        if self.history and self.history_idx > 0:
            self.history_idx -= 1
            self.input_entry.delete(0, "end")
            self.input_entry.insert(0, self.history[self.history_idx])
        return "break"

    def _history_down(self, event=None):
        """Navigate command history down."""
        if self.history_idx < len(self.history) - 1:
            self.history_idx += 1
            self.input_entry.delete(0, "end")
            self.input_entry.insert(0, self.history[self.history_idx])
        elif self.history_idx == len(self.history) - 1:
            self.history_idx = len(self.history)
            self.input_entry.delete(0, "end")
        return "break"

    def _write_output(self, text, tag=None):
        """Write text to terminal output."""
        try:
            self.output.configure(state="normal")
            if tag:
                self.output.insert("end", text, tag)
            else:
                self.output.insert("end", text)
            self.output.see("end")

            # Limit buffer to ~10000 lines
            line_count = int(self.output.index("end-1c").split(".")[0])
            if line_count > 10000:
                self.output.delete("1.0", "1000.0")
        except Exception:
            pass

    def clear(self):
        """Clear terminal output."""
        self.output.configure(state="normal")
        self.output.delete("1.0", "end")

    def toggle(self):
        """Show/hide the terminal."""
        if self.visible:
            self.frame.pack_forget()
            self.visible = False
        else:
            self.frame.pack(fill=BOTH, expand=False)
            self.visible = True
            self.input_entry.focus_set()

    def destroy(self):
        """Clean up on app exit."""
        self._stop_shell()