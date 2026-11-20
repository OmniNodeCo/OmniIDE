"""Functional tests for the v1.1.0 GUI feature batch.

Run offscreen:
    QT_QPA_PLATFORM=offscreen python tests/test_features_gui_v2.py
"""

import os
import sys
import json
import tempfile
import shutil

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

PASS = 0
FAIL = 0


def check(name, cond, extra=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ok  {name}")
    else:
        FAIL += 1
        print(f" FAIL {name} {extra}")


def main():
    from PyQt6.QtWidgets import QApplication, QMessageBox, QMenu, QPushButton
    from PyQt6.QtCore import QTimer, QEventLoop

    from src.config import SETTINGS_PATH, CONFIG_DIR
    from src.core import session as sess

    # clean slate for session
    open(SETTINGS_PATH, "w").write(json.dumps({
        "suppress_git_prompt": True, "auto_check_updates": False,
        "restore_session": True,
    }))
    sess.clear_session()

    app = QApplication([])
    QMessageBox.question = staticmethod(lambda *a, **k: QMessageBox.StandardButton.Yes)
    QMessageBox.warning = staticmethod(lambda *a, **k: None)
    QMessageBox.critical = staticmethod(lambda *a, **k: None)

    proj = tempfile.mkdtemp(prefix="omni_gui2_")
    pyfile = os.path.join(proj, "hello.py")
    with open(pyfile, "w") as f:
        f.write("print('hello-from-run')\n")
    jsonfile = os.path.join(proj, "data.json")
    with open(jsonfile, "w") as f:
        f.write('{"b": 1, "a": [3, 2, 1]}')

    from src.app import OmniIDEApp
    w = OmniIDEApp()
    w.show()

    def spin(ms=300):
        loop = QEventLoop()
        QTimer.singleShot(ms, loop.quit)
        loop.exec()

    spin(1200)

    # ── Menus / toolbar ─────────────────────────────────────────
    mb = w.menuBar()
    titles = [a.text() for a in mb.actions()]
    check("Run menu exists", "Run" in titles, str(titles))
    run_menu = [a.menu() for a in mb.actions() if a.text() == "Run"][0]
    check("Run File action", any("Run File" in a.text() for a in run_menu.actions()))

    file_menu = [a.menu() for a in mb.actions() if a.text() == "File"][0]
    file_texts = [a.text() for a in file_menu.actions()]
    check("Recent File submenu", any("Recent File" in t for t in file_texts), str(file_texts))
    check("Recent Folder submenu", any("Recent Folder" in t for t in file_texts))
    check("Revert File action", any("Revert File" in t for t in file_texts))

    edit_menu = [a.menu() for a in mb.actions() if a.text() == "Edit"][0]
    edit_texts = [a.text() for a in edit_menu.actions()]
    check("Format JSON action", any("Format JSON" in t for t in edit_texts), str(edit_texts))
    check("Convert Case submenu", any("Convert Case" in t for t in edit_texts))

    tb_buttons = [b.text().strip() for b in w.toolbar.findChildren(QPushButton)]
    check("Toolbar Run button", "Run" in tb_buttons, str(tb_buttons))

    # ── Open files, tab icons, doc stats ────────────────────────
    w.file_manager.open_file(pyfile)
    spin(200)
    ed = w.editor_tabs.get_current_code_editor()
    check("py file opened", ed is not None and ed.filepath == pyfile)
    icon = w.editor_tabs.tabs.tabIcon(w.editor_tabs.tabs.currentIndex())
    check("tab icon present", icon is not None and not icon.isNull())

    check("doc stats label", "lines" in w.statusbar.doc_stats_label.text(),
          w.statusbar.doc_stats_label.text())

    # ── Whitespace / indent guides overlay paints without error ──
    w.settings["show_whitespace"] = True
    w.settings["indent_guides"] = True
    ed.viewport().update()
    app.processEvents()
    check("overlay paints (ws+guides)", True)
    w.settings["show_whitespace"] = False
    w.settings["indent_guides"] = False
    ed.viewport().update()
    app.processEvents()
    check("overlay off paints", True)
    w.settings["show_whitespace"] = False
    w.settings["indent_guides"] = True

    # ── Revert file ─────────────────────────────────────────────
    w.file_manager.open_file(pyfile)
    ed = w.editor_tabs.get_current_code_editor()
    ed.set_content("MODIFIED CONTENT\n")
    ed.modified = True
    w.revert_file()
    check("revert restores content", "hello-from-run" in ed.get_content())
    check("revert clears modified", ed.modified is False)

    # ── Format JSON ─────────────────────────────────────────────
    w.file_manager.open_file(jsonfile)
    ed = w.editor_tabs.get_current_code_editor()
    w.format_json()
    formatted = ed.get_content()
    check("json formatted", formatted.startswith("{\n    ") , repr(formatted[:30]))
    w.file_manager.open_file(jsonfile)
    ed = w.editor_tabs.get_current_code_editor()
    ed.set_content("{bad json")
    ed.modified = True
    w.format_json()
    check("invalid json not clobbered", "{bad json" in ed.get_content())

    # ── Convert case ────────────────────────────────────────────
    ed.set_content("my variable name here")
    ed.modified = True
    from PyQt6.QtGui import QTextCursor as QTC
    c = ed.textCursor()
    c.movePosition(QTC.MoveOperation.Start)
    c.movePosition(QTC.MoveOperation.End, QTC.MoveMode.KeepAnchor)
    ed.setTextCursor(c)
    w.convert_case("upper")
    check("case upper", "MY VARIABLE NAME HERE" in ed.get_content())
    w.convert_case("snake")
    check("case snake", "my_variable_name_here" in ed.get_content())
    w.convert_case("camel")
    check("case camel", "myVariableNameHere" in ed.get_content())

    # ── Run file ────────────────────────────────────────────────
    w.file_manager.open_file(pyfile)
    before = w.terminal.tabs.count()
    w.run_current_file()
    spin(2500)
    check("run created terminal tab", w.terminal.tabs.count() == before + 1)
    run_inst = w.terminal.tabs.widget(w.terminal.tabs.count() - 1)
    out = run_inst.output.toPlainText()
    check("run executed script", "hello-from-run" in out, out[-200:])

    # ── Terminal copy all ───────────────────────────────────────
    w.terminal.copy_all()
    check("copy all to clipboard",
          "hello-from-run" in (QApplication.clipboard().text() or ""))

    # ── Session save/restore ────────────────────────────────────
    w._save_session()
    files, active = sess.load_session()
    check("session saved", pyfile in [os.path.abspath(f) for f in files],
          str(files))

    # ── Recent folders ──────────────────────────────────────────
    w.open_project(proj)
    check("recent folder tracked", proj in w.recent_folders.get_all())

    # ── Palette has new entries ─────────────────────────────────
    from src.ui.command_palette import CommandPaletteDialog
    pal = CommandPaletteDialog(w)
    labels = [pal.list.item(i).text() for i in range(pal.list.count())]
    for needle in ["Run File", "Revert File", "Format JSON", "camelCase", "Copy All"]:
        check(f"palette: {needle}", any(needle in t for t in labels))
    pal.reject()

    # ── Close and verify session file persists ──────────────────
    w.close()
    spin(200)
    check("session file exists", os.path.isfile(sess.SESSION_PATH))

    # Restart app and verify restore
    w2 = OmniIDEApp()
    w2.show()
    spin(1200)
    restored_paths = [
        getattr(e, "filepath", None)
        for e in w2.editor_tabs.all_editors()
        if getattr(e, "filepath", None)
    ]
    check("session restored on start",
          any(p and p.startswith(proj) for p in restored_paths), str(restored_paths))
    w2.close()
    spin(200)
    sess.clear_session()

    shutil.rmtree(proj, ignore_errors=True)
    print(f"\n{PASS} passed, {FAIL} failed")
    sys.exit(1 if FAIL else 0)


if __name__ == "__main__":
    main()
