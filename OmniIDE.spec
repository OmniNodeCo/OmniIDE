# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

hidden_imports = [
    "PyQt6", "PyQt6.QtWidgets", "PyQt6.QtCore", "PyQt6.QtGui",
    "PIL", "PIL.Image", "PIL.ImageDraw", "PIL.ImageTk",
    "src", "src.app", "src.config",
    "src.core", "src.core.editor", "src.core.file_manager",
    "src.core.git_manager", "src.core.git_installer",
    "src.core.extension_manager", "src.core.updater",
    "src.core.syntax_highlighter",
    "src.ui", "src.ui.editor_widget", "src.ui.sidebar",
    "src.ui.terminal_widget", "src.ui.toolbar", "src.ui.statusbar",
    "src.ui.menubar", "src.ui.command_palette",
    "src.ui.settings_dialog", "src.ui.splash",
    "src.ui.theme_stylesheet",
    "src.utils", "src.utils.theme_loader",
    "src.utils.recent_files",
    "json", "os", "re", "subprocess", "threading", "sys",
    "io", "shutil", "signal", "math",
    "urllib", "urllib.request", "urllib.error",
    "zipfile", "webbrowser",
]

datas = [
    ("assets", "assets"),
    ("src", "src"),
]

a = Analysis(
    ["run.py"],
    pathex=["."],
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["matplotlib", "numpy", "scipy", "pandas", "pytest", "setuptools"],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz, a.scripts, a.binaries, a.zipfiles, a.datas, [],
    name="OmniIDE",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)