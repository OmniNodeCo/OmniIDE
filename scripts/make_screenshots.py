"""Render real OmniIDE screenshots (offscreen) into docs/img/.

Usage:
    QT_QPA_PLATFORM=offscreen python scripts/make_screenshots.py
"""

import json
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

from src.config import SETTINGS_PATH
json.dump({"suppress_git_prompt": True, "auto_check_updates": False},
          open(SETTINGS_PATH, "w"))

from PyQt6.QtWidgets import QApplication, QMessageBox
QMessageBox.question = staticmethod(lambda *a, **k: QMessageBox.StandardButton.Yes)
QMessageBox.warning = staticmethod(lambda *a, **k: None)
QMessageBox.information = staticmethod(lambda *a, **k: None)

app = QApplication([])
from src.app import OmniIDEApp


def spin(w, ms=400):
    from PyQt6.QtCore import QTimer, QEventLoop
    loop = QEventLoop()
    QTimer.singleShot(ms, loop.quit)
    loop.exec()


OUT = os.path.join(ROOT, "docs", "img")
os.makedirs(OUT, exist_ok=True)


def grab(window, name, size=(1180, 700)):
    window.resize(*size)
    spin(window, 300)
    pm = window.grab()
    path = os.path.join(OUT, name)
    pm.save(path)
    print(f"saved {path} ({os.path.getsize(path) // 1024} KB)")


def main():
    w = OmniIDEApp()
    w.show()
    spin(w, 1600)
    w.editor_tabs.close_all_tabs()

    proj = tempfile.mkdtemp(prefix="omni_shot_")

    # ── editor screenshot ────────────────────────────────────────
    pyfile = os.path.join(proj, "main.py")
    with open(pyfile, "w") as f:
        f.write(
            '"""OmniIDE demo module."""\n'
            "import os\n"
            "import sys\n"
            "\n\n"
            "class Greeter:\n"
            "    def __init__(self, name):\n"
            "        self.name = name\n\n"
            "    def greet(self):\n"
            "        return f\"Hello, {self.name}!\"\n\n\n"
            "def main():\n"
            "    greeter = Greeter(\"OmniNodeCo\")\n"
            "    print(greeter.greet())\n\n\n"
            "if __name__ == \"__main__\":\n"
            "    main()\n"
        )
    w.open_project(proj)
    w.file_manager.open_file(pyfile)
    spin(w, 500)
    w.editor_tabs.get_current_code_editor().goto_line(11)
    spin(w, 300)
    grab(w, "editor.png")

    # ── problems screenshot ──────────────────────────────────────
    badfile = os.path.join(proj, "broken.py")
    with open(badfile, "w") as f:
        f.write(
            "import os\n"
            "\n\n"
            "def broken(:\n"
            "    return 1\n"
            "\n\n"
            "x = {\"a\": 1\n"
        )
    w.file_manager.open_file(badfile)
    spin(w, 700)
    w.sidebar._switch("problems")
    spin(w, 300)
    grab(w, "problems.png")
    w.editor_tabs.close_current_tab()
    spin(w, 200)

    # ── markdown preview screenshot ──────────────────────────────
    md = os.path.join(proj, "README.md")
    with open(md, "w") as f:
        f.write(
            "# OmniIDE\n\n"
            "A **fast, modern, lightweight** desktop IDE built with "
            "PyQt6. *No Electron.*\n\n"
            "## Features\n\n"
            "- Multi-tab editor with syntax highlighting\n"
            "- Real terminal with shell history\n"
            "- Git integration and VS Code extensions\n\n"
            "```python\n"
            "print('Hello from OmniIDE')\n"
            "```\n\n"
            "> Built with care by OmniNodeCo.\n\n"
            "| Platform | Status |\n"
            "|--------|--------|\n"
            "| Windows | Ready |\n"
            "| macOS | Ready |\n"
        )
    w.file_manager.open_file(md)
    spin(w, 400)
    w.toggle_markdown_preview()
    spin(w, 400)
    grab(w, "preview.png")
    w.editor_tabs.close_current_tab()
    spin(w, 200)

    # ── search screenshot ────────────────────────────────────────
    docs_dir = os.path.join(proj, "docs")
    os.makedirs(docs_dir, exist_ok=True)
    for i, name in enumerate(["guide.txt", "notes.txt", "faq.txt"]):
        with open(os.path.join(docs_dir, name), "w") as f:
            f.write(f"line one {name}\nneedle found here in {name}\nthird line\n")
    w.file_manager.open_file(pyfile)
    spin(w, 200)
    w.open_search()
    spin(w, 300)
    w.sidebar.search_panel.search_input.setText("needle")
    w.sidebar.search_panel.run_search()
    spin(w, 1200)
    grab(w, "search.png")

    # ── terminal screenshot (ANSI colors) ────────────────────────
    w.sidebar._switch("explorer")
    spin(w, 200)
    w.editor_terminal_splitter.setSizes([380, 330])
    inst = w.terminal.new_terminal()
    spin(w, 800)
    # Simulate a completed run for a clean screenshot (the live run_command
    # path is covered by the functional test suite)
    inst._write("\x1b[1;34m$\x1b[0m python main.py\n")
    inst._write("\x1b[32mHello from OmniIDE\x1b[0m\n")
    inst._write("\n")
    inst._write("\x1b[1;33mWarning:\x1b[0m \x1b[33mdeprecated flag --legacy\x1b[0m\n")
    inst._write("\x1b[1;31mError:\x1b[0m \x1b[31mconnection refused (port 8080)\x1b[0m\n")
    inst._write("\x1b[2mProcess finished with exit code 1\x1b[0m\n")
    spin(w, 500)
    grab(w, "terminal.png")

    # ── git screenshot ───────────────────────────────────────────
    subprocess.run(["git", "init", "-q", proj], check=True)
    subprocess.run(["git", "-C", proj, "-c", "user.email=d@o", "-c", "user.name=d",
                    "add", pyfile], check=True)
    subprocess.run(["git", "-C", proj, "-c", "user.email=d@o", "-c", "user.name=d",
                    "commit", "-qm", "init"], check=True)
    with open(pyfile, "a") as f:
        f.write("\n# new feature line\n")
    with open(os.path.join(proj, "feature.py"), "w") as f:
        f.write("NEW = True\n")
    w.git_manager.detect_repo(proj)
    w.sidebar._switch("git")
    spin(w, 400)
    grab(w, "git.png")

    w.close()
    spin(w, 300)
    print("done")


if __name__ == "__main__":
    main()
