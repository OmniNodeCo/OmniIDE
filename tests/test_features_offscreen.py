"""Functional tests for the 1.1.0 feature set.

Run offscreen:
    QT_QPA_PLATFORM=offscreen python tests/test_features_offscreen.py

Requires PyQt6. Exits non-zero on failure.
"""

import os
import sys
import tempfile
import shutil
import traceback

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
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import QTimer, QEventLoop

    # Headless-safe settings: no git prompt, no network update check
    import json
    from src.config import SETTINGS_PATH
    _settings_backup = None
    if os.path.exists(SETTINGS_PATH):
        _settings_backup = open(SETTINGS_PATH).read()
    with open(SETTINGS_PATH, "w") as f:
        json.dump({"suppress_git_prompt": True, "auto_check_updates": False}, f)

    app = QApplication([])
    app.setApplicationName("OmniIDE")

    # Auto-discard any modal save-confirm dialogs so the test never blocks
    from PyQt6.QtWidgets import QMessageBox
    QMessageBox.question = staticmethod(
        lambda *a, **k: QMessageBox.StandardButton.No)
    QMessageBox.information = staticmethod(lambda *a, **k: QMessageBox.StandardButton.Ok)
    QMessageBox.warning = staticmethod(lambda *a, **k: QMessageBox.StandardButton.Ok)
    QMessageBox.critical = staticmethod(lambda *a, **k: QMessageBox.StandardButton.Ok)
    QMessageBox.about = staticmethod(lambda *a, **k: None)

    from src.app import OmniIDEApp

    # ── Sandbox project ─────────────────────────────────────────
    proj = tempfile.mkdtemp(prefix="omniide_test_")
    os.makedirs(os.path.join(proj, "src"), exist_ok=True)
    os.makedirs(os.path.join(proj, "docs"), exist_ok=True)
    with open(os.path.join(proj, "main.py"), "w") as f:
        f.write("import os\n\n\ndef hello():\n    print('world')\n\nif __name__ == '__main__':\n    hello()\n")
    with open(os.path.join(proj, "src", "utils.py"), "w") as f:
        f.write("def util():\n    return 42\n")
    with open(os.path.join(proj, "docs", "readme.md"), "w") as f:
        f.write("# Test Doc\n\nSome **bold** text.\n\n- a\n- b\n")
    with open(os.path.join(proj, "data.json"), "w") as f:
        f.write('{"key": "value"}')
    with open(os.path.join(proj, "searchme.txt"), "w") as f:
        f.write("needle one\nno match\nneedle two\n")

    w = OmniIDEApp()
    w.show()

    def spin(ms=300):
        loop = QEventLoop()
        QTimer.singleShot(ms, loop.quit)
        loop.exec()
    spin(1200)  # let splash finish

    # ── Project + file tree ─────────────────────────────────────
    try:
        w.open_project(proj)
        check("open_project sets path", w.current_project_path == proj)
        spin(500)
        idx = w.sidebar.file_tree.model.index(os.path.join(proj, "main.py"))
        check("file tree has main.py", idx.isValid())
    except Exception:
        traceback.print_exc()
        check("open_project", False)

    # ── Open file, cursor status ────────────────────────────────
    try:
        w.file_manager.open_file(os.path.join(proj, "main.py"))
        ed = w.editor_tabs.get_current_code_editor()
        check("editor opened", ed is not None and ed.filepath.endswith("main.py"))
        check("editor content", "def hello" in ed.get_content())
        w.statusbar.update_cursor_position_for(ed)
        check("status cursor label", "Ln 1" in w.statusbar.cursor_label.text())
    except Exception:
        traceback.print_exc()
        check("open_file", False)

    # ── Code actions ────────────────────────────────────────────
    try:
        ed.goto_line(4)  # "def hello():"
        before = ed.get_content()
        w.duplicate_line()
        after = ed.get_content()
        check("duplicate line", "def hello():\ndef hello():\n    print" in after)
        # reset
        ed.set_content(before)
        ed.modified = False

        ed.goto_line(5)  # "    print('world')"
        before = ed.get_content()
        w.toggle_comment()
        check("toggle comment on", "    # print('world')" in ed.get_content())
        w.toggle_comment()
        check("toggle comment off", ed.get_content() == before)

        ed.goto_line(1)
        before = ed.get_content()
        w.move_line_down()
        lines_before = before.split("\n")
        lines_after = ed.get_content().split("\n")
        check("move line down", lines_after[0] == lines_before[1]
              and lines_after[1] == lines_before[0])
        w.move_line_up()
        check("move line up restores", ed.get_content() == before)

        ed.goto_line(2)
        before = ed.get_content()
        w.delete_line()
        check("delete line", ed.get_content() == before.replace("\n\n", "\n", 1)
              or len(ed.get_content().split("\n")) == len(before.split("\n")) - 1)
        ed.set_content(before)
        ed.modified = False

        # sort lines
        w.editor_tabs.new_tab(content="banana\napple\ncherry")
        sort_ed = w.editor_tabs.get_current_code_editor()
        sort_ed.goto_line(2)
        w.sort_lines()
        check("sort lines", sort_ed.get_content() == "apple\nbanana\ncherry")
        w.editor_tabs.close_current_tab()
    except Exception:
        traceback.print_exc()
        check("code actions", False)

    # ── JSON validation ─────────────────────────────────────────
    try:
        w.file_manager.open_file(os.path.join(proj, "data.json"))
        ed = w.editor_tabs.get_current_code_editor()
        ed.set_content('{"key": "value"')  # invalid
        ed.modified = True
        ok = w.file_manager._save_editor(ed)
        check("json invalid blocked", ok is False)
        check("json error marker", w.statusbar.json_error is not None)
        ed.set_content('{"key": "value"}')
        ok = w.file_manager._save_editor(ed)
        check("json valid saved", ok is True)
        check("json error cleared", w.statusbar.json_error is None)
    except Exception:
        traceback.print_exc()
        check("json validation", False)

    # ── Quick Open ──────────────────────────────────────────────
    try:
        from src.ui.quick_open import QuickOpenDialog
        dlg = QuickOpenDialog(w)
        dlg.search.setText("utils")
        app.processEvents()
        check("quick open finds utils", dlg.list.count() >= 1
              and "utils.py" in dlg.list.item(0).text())
        dlg.reject()
    except Exception:
        traceback.print_exc()
        check("quick open", False)

    # ── Global search ───────────────────────────────────────────
    try:
        w.open_search()
        w.sidebar.search_panel.search_input.setText("needle")
        w.sidebar.search_panel.run_search()
        spin(1200)
        status = w.sidebar.search_panel.status.text()
        check("global search found 2", "2 results in 1 file" in status, status)
        # open result
        node = w.sidebar.search_panel.tree.topLevelItem(0)
        child = node.child(0)
        w.sidebar.search_panel._open_result(child, 0)
        spin(200)
        ed = w.editor_tabs.get_current_code_editor()
        check("search result opens file", ed is not None
              and ed.filepath.endswith("searchme.txt"))
        sel_start = ed.textCursor().selectionStart()
        check("search result at line",
              ed.document().findBlock(sel_start).blockNumber() == 0,
              str(ed.document().findBlock(sel_start).blockNumber() + 1))
    except Exception:
        traceback.print_exc()
        check("global search", False)

    # ── Markdown preview ────────────────────────────────────────
    try:
        w.file_manager.open_file(os.path.join(proj, "docs", "readme.md"))
        w.toggle_markdown_preview()
        spin(200)
        from src.ui.editor_widget import MarkdownPreview
        prev = w.editor_tabs.get_current_editor()
        check("markdown preview tab", isinstance(prev, MarkdownPreview))
        check("preview html", "bold" in prev.toHtml() and "Test Doc" in prev.toHtml())
        w.editor_tabs.close_current_tab()
    except Exception:
        traceback.print_exc()
        check("markdown preview", False)

    # ── Multi-terminal ──────────────────────────────────────────
    try:
        first = w.terminal.tabs.count()
        w.new_terminal()
        check("new terminal tab", w.terminal.tabs.count() == first + 1)
        w.terminal.clear()
        check("terminal clear works", w.terminal.tabs.count() >= 1)
    except Exception:
        traceback.print_exc()
        check("multi-terminal", False)

    # ── Breadcrumbs ─────────────────────────────────────────────
    try:
        w.file_manager.open_file(os.path.join(proj, "src", "utils.py"))
        w._on_editor_tab_changed(0)
        crumbs = [p.text() for p in w.breadcrumbs._crumbs if p.text()]
        check("breadcrumbs show file", "utils.py" in crumbs, str(crumbs))
        check("breadcrumbs show dir", "src" in crumbs, str(crumbs))
    except Exception:
        traceback.print_exc()
        check("breadcrumbs", False)

    # ── Minimap ─────────────────────────────────────────────────
    try:
        w.toggle_minimap()
        spin(300)
        check("minimap visible", w.minimap.isVisible())
        check("minimap attached", w.minimap.editor is not None)
        # paint it
        w.minimap.repaint()
        check("minimap paints", True)
        w.toggle_minimap()
        check("minimap hidden after toggle", not w.minimap.isVisible())
    except Exception:
        traceback.print_exc()
        check("minimap", False)

    # ── Save all / close others ─────────────────────────────────
    try:
        eds = w.editor_tabs.all_editors()
        code_eds = [e for e in eds
                    if e.__class__.__name__ == "CodeEditor" and e.filepath]
        check("multiple tabs open", len(code_eds) >= 2)
        w.file_manager.save_all()
        check("save all", True)
    except Exception:
        traceback.print_exc()
        check("save all", False)

    # ── Command palette ─────────────────────────────────────────
    try:
        from src.ui.command_palette import CommandPaletteDialog
        pal = CommandPaletteDialog(w)
        pal.search.setText("sort")
        app.processEvents()
        labels = [pal.list.item(i).text() for i in range(pal.list.count())]
        check("palette finds sort lines",
              any("Sort Lines" in t for t in labels), str(labels[:5]))
        pal.reject()
    except Exception:
        traceback.print_exc()
        check("command palette", False)

    # ── Settings persistence ────────────────────────────────────
    try:
        w.settings["show_hidden_files"] = True
        w.toggle_hidden_files()
        check("hidden files toggled off", w.settings["show_hidden_files"] is False)
    except Exception:
        traceback.print_exc()
        check("toggle hidden", False)

    # ── Close ───────────────────────────────────────────────────
    w.close()
    spin(300)

    shutil.rmtree(proj, ignore_errors=True)

    # Restore the user's settings file
    if _settings_backup is not None:
        with open(SETTINGS_PATH, "w") as f:
            f.write(_settings_backup)
    elif os.path.exists(SETTINGS_PATH):
        try:
            os.remove(SETTINGS_PATH)
        except OSError:
            pass

    print(f"\n{PASS} passed, {FAIL} failed")
    sys.exit(1 if FAIL else 0)


if __name__ == "__main__":
    main()
