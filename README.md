<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/logo.svg">
  <source media="(prefers-color-scheme: light)" srcset="assets/logo.svg">
  <img src="assets/logo.svg" alt="OmniIDE Logo" width="400">
</picture>

<br><br>

[![Version](https://img.shields.io/badge/version-1.1.0-89b4fa?style=for-the-badge)](https://github.com/OmniNodeCo/OmniIDE/releases/latest)
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

[![Download](https://img.shields.io/badge/Download_v1.1.0-89b4fa?style=for-the-badge)](https://github.com/OmniNodeCo/OmniIDE/releases/latest)
[![Website](https://img.shields.io/badge/Website-omninodeco.github.io-cba6f7?style=for-the-badge)](https://omninodeco.github.io/OmniIDE)

---

</div>

## Features

<table>
<tr>
<td width="50%">

### Editor
- Multi-tab code editor (QPlainTextEdit)
- Syntax highlighting (QSyntaxHighlighter) — Python, JS/TS, HTML, CSS, JSON, Markdown, YAML, Rust, Go
- Line numbers with gutter
- Auto-indent, smart brackets (auto-close + empty-pair delete)
- Bracket matching with highlight
- Find & Replace with case / whole-word / regex options
- Duplicate / delete / move / sort lines
- Toggle comment (`Ctrl+/`) — 30+ languages
- Go to Line (`Ctrl+G`)
- Markdown preview (`Ctrl+Shift+V`) — built-in converter
- JSON validation with error marker on save
- Word wrap toggle, zoom in/out/reset
- Current line highlight, drag & drop files
- Tab context menu: close / close others / close all / copy path
- Reorderable tabs (double-click closes)

</td>
<td width="50%">

### Navigation & Search
- **Quick Open** (`Ctrl+P`) — fuzzy file finder
- **Search in Files** (`Ctrl+Shift+F`) — project-wide search panel with line numbers, case / whole-word / regex
- Breadcrumbs bar (click to expand tree)
- Command Palette (`Ctrl+Shift+P`) — 50+ fuzzy-ranked commands
- Resizable panels (QSplitter)

</td>
</tr>
<tr>
<td>

### Terminal
- Multiple terminal tabs (`Ctrl+Shift+T`)
- Real interactive shell (QProcess)
- Auto-detects shells per OS
- Shell selector dropdown
- Per-session command history
- Restart and clear

</td>
<td>

### Files, Git & More
- File tree with context menu: new file/folder, rename, delete, copy path
- Show hidden files toggle, refresh
- Auto save (interval + on tab switch)
- Save All / Close All / Close Others
- Line ending detection (LF/CRLF/CR) + convert
- Minimap (bar-style document overview)
- VS Code Marketplace browser, VSIX install
- Git: clone, commit, push, pull, diff, log, branches
- Dark & light Catppuccin themes
- Auto-update checker (GitHub Releases)

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
```

## Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| New File | `Ctrl+N` |
| Open File | `Ctrl+O` |
| Quick Open | `Ctrl+P` |
| Save | `Ctrl+S` |
| Save As | `Ctrl+Shift+S` |
| Save All | `Ctrl+Alt+S` |
| Close Tab | `Ctrl+W` |
| Find & Replace | `Ctrl+F` |
| Search in Files | `Ctrl+Shift+F` |
| Go to Line | `Ctrl+G` |
| Toggle Comment | `Ctrl+/` |
| Duplicate Line | `Ctrl+D` |
| Delete Line | `Ctrl+Shift+D` |
| Move Line Up / Down | `Alt+Up` / `Alt+Down` |
| Sort Lines | `Ctrl+Shift+O` |
| Markdown Preview | `Ctrl+Shift+V` |
| New Terminal | `Ctrl+Shift+T` |
| Toggle Sidebar | `Ctrl+B` |
| Toggle Terminal | `` Ctrl+` `` |
| Command Palette | `Ctrl+Shift+P` |
| Settings | `Ctrl+,` |
| Zoom In / Out / Reset | `Ctrl+=` / `Ctrl+-` / `Ctrl+0` |

## Development

```bash
pip install PyQt6
python run.py
```

Run tests:

```bash
python -m unittest discover tests
```

## Changelog

**v1.1.0 (Latest)**
- Quick Open (`Ctrl+P`) with fuzzy file ranking
- Search in Files panel (`Ctrl+Shift+F`) — case / whole-word / regex, open result at line
- Line actions: duplicate, delete, move up/down, sort lines
- Toggle comment for 30+ file types (`Ctrl+/`)
- Find & Replace: whole-word and regex options
- Markdown preview tab (`Ctrl+Shift+V`) with built-in converter
- Multi-terminal tabs (`Ctrl+Shift+T`)
- Breadcrumbs bar for current file path
- File tree context menu: new file/folder, rename, delete, copy path
- Show hidden files toggle
- Auto save (interval + on tab switch), Save All
- Line ending detection (LF/CRLF/CR) and conversion
- Minimap (bar-style overview, click to jump)
- Smart brackets: auto-close and empty-pair delete
- Bracket matching, JSON validation with error marker
- Drag & drop files into the editor
- Tab context menu: close others/all, copy path; reorderable tabs
- Syntax highlighting for Markdown, YAML, Rust, Go
- 50+ command palette entries, 94+ automated tests

**v1.0.7**
- Version bump with all v1.0.6 fixes verified
- Updated all CI workflows
- README badges and views fixed

**v1.0.6**
- SVG icons for sidebar, git, extensions (PyQt6.QtSvg)
- Thread-safe extension search (pyqtSignal)
- Fixed marketplace cards not appearing
- Styled extension cards

**v1.0.5**
- Fixed Ubuntu 24.04 CI (libgl1)
- QT_QPA_PLATFORM=offscreen for tests

**v1.0.4**
- Complete rewrite: Tkinter → PyQt6
- QProcess terminal, QSS theming
- Real VSIX extension installation
- Documentation website

**v1.0.3**
- Settings GUI, auto-update checker

**v1.0.2**
- Command Palette, Go to Line

**v1.0.1**
- Extensions, Git, terminal, SVG icons

**v1.0.0**
- Initial release

## License

MIT — see [LICENSE](LICENSE)

<div align="center">

Made with care by **OmniNodeCo**

[Stars](https://github.com/OmniNodeCo/OmniIDE/stargazers) ·
[Forks](https://github.com/OmniNodeCo/OmniIDE/network/members) ·
[Issues](https://github.com/OmniNodeCo/OmniIDE/issues)

</div>
