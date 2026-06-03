# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for OmniIDE.
Use this instead of passing flags on the command line.

Build with:
    pyinstaller OmniIDE.spec
"""

import sys
import os

block_cipher = None

# All src submodules listed explicitly so PyInstaller never misses them
hidden_imports = [
    # ttkbootstrap
    "ttkbootstrap",
    "ttkbootstrap.constants",
    "ttkbootstrap.style",
    "ttkbootstrap.themes",
    "ttkbootstrap.dialogs",
    "ttkbootstrap.scrolled",
    "ttkbootstrap.tooltip",
    "ttkbootstrap.tableview",
    "ttkbootstrap.validation",
    # tkinter
    "tkinter",
    "tkinter.ttk",
    "tkinter.font",
    "tkinter.filedialog",
    "tkinter.messagebox",
    "tkinter.colorchooser",
    "tkinter.simpledialog",
    # PIL
    "PIL",
    "PIL.Image",
    "PIL.ImageDraw",
    "PIL.ImageFont",
    "PIL.ImageTk",
    # src core
    "src",
    "src.app",
    "src.config",
    "src.core",
    "src.core.editor",
    "src.core.tab_manager",
    "src.core.syntax_highlighter",
    "src.core.file_manager",
    "src.core.terminal",
    "src.core.search",
    # src ui
    "src.ui",
    "src.ui.menubar",
    "src.ui.sidebar",
    "src.ui.statusbar",
    "src.ui.toolbar",
    "src.ui.file_tree",
    "src.ui.welcome",
    # src utils
    "src.utils",
    "src.utils.theme_loader",
    "src.utils.recent_files",
    "src.utils.shortcuts",
    # stdlib
    "json",
    "os",
    "re",
    "subprocess",
    "threading",
    "sys",
]

# Collect all data files
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
    excludes=[
        "matplotlib",
        "numpy",
        "scipy",
        "pandas",
        "pytest",
        "setuptools",
        "distutils",
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher,
)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="OmniIDE",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,          # no black console window
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # icon is set per-platform in the workflow
)