"""Built-in terminal emulator."""

import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import subprocess
import threading
import os
import sys


class Terminal:
    """Simple integrated terminal."""

    def __init__(self, parent, app):
        self.app = app
        self.process = None
        self.visible = True

        self.frame = ttk.Frame(parent)

        # Terminal header
        header = ttk.Frame(self.frame)
        header.pack(fill=X)

        ttk.Label(
            header, text="  ⌨ Terminal",
            font=("Segoe UI", 10, "bold"),
        ).pack(side=LEFT, padx=5)

        ttk.Button(
            header, text="✕", width=3,
            bootstyle="danger-link",
            command=self.toggle,
        ).pack(side=RIGHT)

        ttk.Button(
            header, text="Clear",
            bootstyle="secondary-link",
            command=self.clear,
        ).pack(side=RIGHT, padx=5)

        # Terminal output
        self.output = tk.Text(
            self.frame,
            height=8,
            bg=app.colors["terminal_bg"],
            fg=app.colors["terminal_fg"],
            insertbackground=app.colors["accent"],
            font=(app.settings["font_family"], app.settings["font_size"] - 1),
            relief="flat",
            borderwidth=0,
            padx=8,
            pady=4,
        )
        self.output.pack(fill=BOTH, expand=True)

        # Input line
        input_frame = ttk.Frame(self.frame)
        input_frame.pack(fill=X)

        cwd = os.path.basename(os.getcwd())
        self.prompt_label = ttk.Label(
            input_frame,
            text=f"  {cwd} $",
            font=(app.settings["font_family"], app.settings["font_size"] - 1),
        )
        self.prompt_label.pack(side=LEFT)

        self.input_entry = ttk.Entry(
            input_frame,
            font=(app.settings["font_family"], app.settings["font_size"] - 1),
        )
        self.input_entry.pack(side=LEFT, fill=X, expand=True, padx=(4, 8), pady=2)
        self.input_entry.bind("<Return>", self._execute_command)

        self._write_output("OmniIDE Terminal — Type commands below\n\n")

    def _execute_command(self, event=None):
        cmd = self.input_entry.get().strip()
        if not cmd:
            return

        self.input_entry.delete(0, "end")
        self._write_output(f"$ {cmd}\n")

        # Handle cd command
        if cmd.startswith("cd "):
            path = cmd[3:].strip()
            try:
                os.chdir(os.path.expanduser(path))
                cwd = os.path.basename(os.getcwd())
                self.prompt_label.configure(text=f"  {cwd} $")
                self._write_output(f"Changed to: {os.getcwd()}\n\n")
            except FileNotFoundError:
                self._write_output(f"Directory not found: {path}\n\n")
            return

        if cmd == "clear" or cmd == "cls":
            self.clear()
            return

        thread = threading.Thread(target=self._run_command, args=(cmd,), daemon=True)
        thread.start()

    def _run_command(self, cmd):
        try:
            shell = True
            if sys.platform == "win32":
                process = subprocess.Popen(
                    cmd, shell=shell, stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT, text=True, cwd=os.getcwd(),
                )
            else:
                process = subprocess.Popen(
                    cmd, shell=shell, stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT, text=True, cwd=os.getcwd(),
                )

            output, _ = process.communicate(timeout=30)
            self.output.after(0, self._write_output, output + "\n")

        except subprocess.TimeoutExpired:
            self.output.after(0, self._write_output, "Command timed out.\n\n")
        except Exception as e:
            self.output.after(0, self._write_output, f"Error: {e}\n\n")

    def _write_output(self, text):
        self.output.insert("end", text)
        self.output.see("end")

    def clear(self):
        self.output.delete("1.0", "end")

    def toggle(self):
        if self.visible:
            self.frame.pack_forget()
            self.visible = False
        else:
            self.frame.pack(fill=BOTH, expand=False)
            self.visible = True