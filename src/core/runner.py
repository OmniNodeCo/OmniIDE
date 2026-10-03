"""Run current file — picks the right interpreter per file type.

Pure Python — no Qt imports so it can be unit-tested headless.
"""

import os
import shutil
import sys


def _python():
    """Best Python executable to run scripts with."""
    if sys.executable:
        return sys.executable
    return shutil.which("python3") or shutil.which("python") or "python3"


# extension -> (command builder, label)
RUNNERS = {
    ".py": lambda p: [_python(), p],
    ".pyw": lambda p: [_python(), p],
    ".js": lambda p: [shutil.which("node") or "node", p],
    ".mjs": lambda p: [shutil.which("node") or "node", p],
    ".sh": lambda p: [shutil.which("bash") or "bash", p],
    ".bash": lambda p: [shutil.which("bash") or "bash", p],
    ".zsh": lambda p: [shutil.which("zsh") or "zsh", p],
    ".rb": lambda p: [shutil.which("ruby") or "ruby", p],
    ".pl": lambda p: [shutil.which("perl") or "perl", p],
    ".php": lambda p: [shutil.which("php") or "php", p],
    ".lua": lambda p: [shutil.which("lua") or shutil.which("lua5.1") or "lua", p],
    ".ps1": lambda p: [shutil.which("pwsh") or shutil.which("powershell") or "powershell",
                       "-File", p],
    ".bat": lambda p: [p] if sys.platform == "win32" else ["cmd", "/c", p],
    ".cmd": lambda p: [p] if sys.platform == "win32" else ["cmd", "/c", p],
    ".go": lambda p: [shutil.which("go") or "go", "run", p],
    ".rs": lambda p: [shutil.which("cargo") or "cargo", "run", "--quiet"],
    ".ts": lambda p: [shutil.which("deno") or "deno", "run", p],
}


def runner_for(filepath):
    """Return the command list for running ``filepath``, or None if unsupported."""
    if not filepath:
        return None
    ext = os.path.splitext(filepath)[1].lower()
    builder = RUNNERS.get(ext)
    if builder is None:
        return None
    try:
        return builder(filepath)
    except Exception:
        return None


def build_run_command(filepath, cwd=None):
    """Return (command_list, workdir) for running a file, or (None, None)."""
    if not filepath or not os.path.isfile(filepath):
        return None, None
    cmd = runner_for(filepath)
    if cmd is None:
        return None, None
    if cwd is None:
        cwd = os.path.dirname(os.path.abspath(filepath))
    return cmd, cwd


def supported_runners():
    """Return sorted list of supported extensions."""
    return sorted(RUNNERS.keys())
