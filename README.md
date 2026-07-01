<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/logo.svg">
  <source media="(prefers-color-scheme: light)" srcset="assets/logo.svg">
  <img src="assets/logo.svg" alt="OmniIDE Logo" width="400">
</picture>

<br><br>

[![Version](https://img.shields.io/badge/version-1.0.7-89b4fa?style=for-the-badge)](https://github.com/OmniNodeCo/OmniIDE/releases/latest)
[![License](https://img.shields.io/badge/license-MIT-a6e3a1?style=for-the-badge)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10+-cba6f7?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![PyQt6](https://img.shields.io/badge/PyQt6-native-89b4fa?style=for-the-badge&logo=qt&logoColor=white)](https://pypi.org/project/PyQt6/)
[![Platform](https://img.shields.io/badge/platform-Windows%20|%20macOS%20|%20Linux-f9e2af?style=for-the-badge)](#installation)
[![Build](https://img.shields.io/github/actions/workflow/status/OmniNodeCo/OmniIDE/test.yml?branch=main&style=for-the-badge&label=tests&color=a6e3a1)](https://github.com/OmniNodeCo/OmniIDE/actions)
[![Release](https://img.shields.io/github/v/release/OmniNodeCo/OmniIDE?style=for-the-badge&color=89b4fa&label=latest)](https://github.com/OmniNodeCo/OmniIDE/releases/latest)
[![Stars](https://img.shields.io/github/stars/OmniNodeCo/OmniIDE?style=for-the-badge&color=f9e2af)](https://github.com/OmniNodeCo/OmniIDE/stargazers)

<br>

![Profile Views](https://komarev.com/ghpvc/?username=OmniNodeCo&label=Profile+Views&color=89b4fa&style=for-the-badge)
![Watchers](https://img.shields.io/github/watchers/OmniNodeCo/OmniIDE?style=for-the-badge&color=cba6f7)

<br>

**A fast, modern, lightweight desktop IDE built with PyQt6.**
**No Electron. No bloat. Pure speed.**

<br>

[![Download](https://img.shields.io/badge/Download_v1.0.7-89b4fa?style=for-the-badge)](https://github.com/OmniNodeCo/OmniIDE/releases/latest)
[![Website](https://img.shields.io/badge/Website-omninodeco.github.io-cba6f7?style=for-the-badge)](https://omninodeco.github.io/OmniIDE)

---

</div>

## Features

<table>
<tr>
<td width="50%">

### Editor
- Multi-tab code editor (QPlainTextEdit)
- Syntax highlighting (QSyntaxHighlighter)
- Line numbers with gutter
- Auto-indent and smart brackets
- Go to Line (`Ctrl+G`)
- Word wrap toggle
- Zoom in/out/reset
- Current line highlight

</td>
<td width="50%">

### Interface
- Dark & light themes (Catppuccin QSS)
- Startup splash screen
- SVG icon system (PyQt6.QtSvg)
- Command Palette (`Ctrl+Shift+P`)
- Tabbed sidebar with icon tabs
- Resizable panels (QSplitter)
- Settings dialog (`Ctrl+,`)

</td>
</tr>
<tr>
<td>

### Terminal
- Real interactive shell (QProcess)
- Auto-detects shells per OS
- Shell selector dropdown
- Command history
- Restart and clear

</td>
<td>

### Extensions & Git
- VS Code Marketplace browser
- VSIX download and install
- Thread-safe search (pyqtSignal)
- Git: clone, commit, push, pull, diff, log
- SVG icon buttons for all git actions
- Git install prompt if missing

</td>
</tr>
</table>

---

## Installation

### Download Binary

| Platform | File |
|----------|------|
| Windows | [`OmniIDE.exe`](https://github.com/OmniNodeCo/OmniIDE/releases/latest/download/OmniIDE.exe) |
| macOS | [`OmniIDE-macOS.zip`](https://github.com/OmniNodeCo/OmniIDE/releases/latest/download/OmniIDE-macOS.zip) |
| Linux | [`OmniIDE-Linux.tar.gz`](https://github.com/OmniNodeCo/OmniIDE/releases/latest/download/OmniIDE-Linux.tar.gz) |

### Run from Source

```bash
git clone https://github.com/OmniNodeCo/OmniIDE.git
cd OmniIDE
pip install -r requirements.txt
python run.py
Keyboard Shortcuts
Action	Shortcut
New File	Ctrl+N
Open File	Ctrl+O
Save	Ctrl+S
Close Tab	Ctrl+W
Settings	Ctrl+,
Find	Ctrl+F
Go to Line	Ctrl+G
Command Palette	Ctrl+Shift+P
Sidebar	Ctrl+B
Terminal	Ctrl+`
Zoom In/Out	Ctrl+= / Ctrl+-
Reset Zoom	Ctrl+0
Changelog
v1.0.7 (Latest)
Version bump with all v1.0.6 fixes verified
Updated all CI workflows
README badges and views fixed
v1.0.6
SVG icons for sidebar, git, extensions (PyQt6.QtSvg)
Thread-safe extension search (pyqtSignal)
Fixed marketplace cards not appearing
Styled extension cards
v1.0.5
Fixed Ubuntu 24.04 CI (libgl1)
QT_QPA_PLATFORM=offscreen for tests
v1.0.4
Complete rewrite: Tkinter → PyQt6
QProcess terminal, QSS theming
Real VSIX extension installation
Documentation website
v1.0.3
Settings GUI, auto-update checker
v1.0.2
Command Palette, Go to Line
v1.0.1
Extensions, Git, terminal, SVG icons
v1.0.0
Initial release
License
MIT — see LICENSE

<div align="center">
Made with care by OmniNodeCo

Stars
Forks
Issues

</div> ```