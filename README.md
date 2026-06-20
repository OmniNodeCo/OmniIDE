<div align="center">

<!-- Logo -->
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/logo.svg">
  <source media="(prefers-color-scheme: light)" srcset="assets/logo.svg">
  <img src="assets/logo.svg" alt="OmniIDE Logo" width="400">
</picture>

<br><br>

<!-- Badges -->
[![Version](https://img.shields.io/badge/version-1.0.4-89b4fa?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgd2lkdGg9IjI0IiBoZWlnaHQ9IjI0Ij48Y2lyY2xlIGN4PSIxMiIgY3k9IjEyIiByPSIxMCIgZmlsbD0iIzFlMWUyZSIgc3Ryb2tlPSIjODliNGZhIiBzdHJva2Utd2lkdGg9IjEuNSIvPjxjaXJjbGUgY3g9IjEyIiBjeT0iMTIiIHI9IjYuNSIgZmlsbD0ibm9uZSIgc3Ryb2tlPSIjY2JhNmY3IiBzdHJva2Utd2lkdGg9IjEuNSIvPjxjaXJjbGUgY3g9IjEyIiBjeT0iMTIiIHI9IjEuNSIgZmlsbD0iI2Y1YzJlNyIvPjwvc3ZnPg==&logoColor=white)](https://github.com/OmniNodeCo/OmniIDE/releases/latest)
[![License](https://img.shields.io/badge/license-MIT-a6e3a1?style=for-the-badge)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10+-cba6f7?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Platform](https://img.shields.io/badge/platform-Windows%20|%20macOS%20|%20Linux-f9e2af?style=for-the-badge)](#installation)
[![Build](https://img.shields.io/github/actions/workflow/status/OmniNodeCo/OmniIDE/build.yml?branch=main&style=for-the-badge&label=build&color=a6e3a1)](https://github.com/OmniNodeCo/OmniIDE/actions)
[![Release](https://img.shields.io/github/v/release/OmniNodeCo/OmniIDE?style=for-the-badge&color=89b4fa&label=latest)](https://github.com/OmniNodeCo/OmniIDE/releases/latest)

<!-- View Counter (excludes repo owner) -->
<br>

![Views](https://komarev.com/ghpvc/?username=OmniNodeCo-OmniIDE&label=Views&color=89b4fa&style=for-the-badge&abbreviated=true)

<br>

**A fast, modern, lightweight desktop IDE built from scratch.**
**No Electron. No bloat. Pure speed.**

<br>

[![Download](https://img.shields.io/badge/⬇_Download_Latest-89b4fa?style=for-the-badge&logoColor=white)](https://github.com/OmniNodeCo/OmniIDE/releases/latest)

---

</div>

## ✨ Features

<table>
<tr>
<td width="50%">

### 🖥️ Editor
- Multi-tab code editor
- Syntax highlighting (Python, JS, HTML, CSS, JSON + more)
- Line numbers with gutter
- Auto-indent and smart brackets
- Go to Line (`Ctrl+G`)
- Toggle Comment (`Ctrl+/`)
- Duplicate / Delete / Move lines
- Word wrap toggle
- Zoom in/out/reset

</td>
<td width="50%">

### 🎨 Interface
- Modern dark & light themes (Catppuccin-inspired)
- Animated startup splash screen
- Custom SVG icon system (no emoji)
- Round buttons with hover animations
- Command Palette (`Ctrl+Shift+P`)
- Tabbed sidebar (Explorer / Git / Extensions)
- Resizable panels
- Persistent settings

</td>
</tr>
<tr>
<td>

### 💻 Terminal
- Real interactive shell (not fake commands)
- Auto-detects available shells per OS
  - **Windows:** PowerShell 7, PowerShell, CMD, Git Bash, WSL
  - **macOS:** Zsh, Bash, Fish
  - **Linux:** Bash, Zsh, Fish, sh
- Shell selector dropdown
- Command history (Up/Down arrows)
- `Ctrl+C` sends interrupt
- Restart button

</td>
<td>

### 🔌 Extensions & Git
- Browse VS Code Marketplace
- Search, install, uninstall extensions
- Full Git integration:
  - Clone, Init, Status, Diff
  - Stage All, Commit, Push, Pull
  - Log, Branches, Set Remote
- Git branch in status bar
- Auto-detect `.git` on project open

</td>
</tr>
</table>

### ⚙️ Settings & Updates

- **Settings GUI** (`Ctrl+,`) — visual editor for all preferences
  - Theme, font, tab size, word wrap, auto-save
  - Terminal shell selection
  - Toggle line numbers, cursor blink, whitespace
  - Searchable settings with live preview
  - Reset to defaults
- **Auto-update checker** — checks GitHub Releases on startup
  - Shows changelog and platform-specific download
  - Configurable (can disable in settings)
  - Manual check: `Help > Check for Updates`

---

## 📸 Screenshots

<div align="center">
<i>Coming soon — contribute screenshots via PR!</i>
</div>

---

## 📦 Installation

### Option 1: Download Pre-built Binary (Recommended)

Go to [**Releases**](https://github.com/OmniNodeCo/OmniIDE/releases/latest) and download for your platform:

| Platform | File | Instructions |
|----------|------|-------------|
| 🪟 **Windows** | `OmniIDE.exe` | Download and double-click. No install needed. |
| 🍎 **macOS** | `OmniIDE-macOS.zip` | Unzip, then `open OmniIDE.app` or drag to Applications. |
| 🐧 **Linux** | `OmniIDE-Linux.tar.gz` | Extract, `chmod +x OmniIDE`, then `./OmniIDE` |

> **macOS note:** If blocked, go to System Preferences → Security → "Open Anyway"

---

### Option 2: Run from Source

#### Prerequisites

- [Python 3.10+](https://python.org/downloads/)
- [Git](https://git-scm.com/downloads)

#### Steps

```bash
# 1. Clone the repository
git clone https://github.com/OmniNodeCo/OmniIDE.git
cd OmniIDE

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run
python run.py
Option 3: Build Executable Yourself
Bash

# 1. Clone and install deps
git clone https://github.com/OmniNodeCo/OmniIDE.git
cd OmniIDE
pip install -r requirements.txt
pip install pyinstaller pillow

# 2. Generate icon (one-time)
python scripts/generate_icon.py

# 3. Build
pyinstaller OmniIDE.spec

# 4. Find your executable
# Windows: dist/OmniIDE.exe
# macOS:   dist/OmniIDE.app
# Linux:   dist/OmniIDE
⌨️ Keyboard Shortcuts
File
Action	Shortcut
New File	Ctrl+N
Open File	Ctrl+O
Save	Ctrl+S
Save As	Ctrl+Shift+S
Close Tab	Ctrl+W
Settings	Ctrl+,
Edit
Action	Shortcut
Undo	Ctrl+Z
Redo	Ctrl+Y
Cut / Copy / Paste	Ctrl+X/C/V
Select All	Ctrl+A
Find & Replace	Ctrl+F
Go to Line	Ctrl+G
Toggle Comment	Ctrl+/
Duplicate Line	via Command Palette
Delete Line	via Command Palette
Move Line Up/Down	Alt+Up/Down
View
Action	Shortcut
Command Palette	Ctrl+Shift+P
Toggle Sidebar	Ctrl+B
Toggle Terminal	Ctrl+`
Zoom In	Ctrl++
Zoom Out	Ctrl+-
Reset Zoom	Ctrl+0
🗂️ Project Structure
text

OmniIDE/
├── assets/
│   ├── icon.ico
│   ├── icon.png
│   ├── logo.svg
│   ├── icons/
│   │   ├── __init__.py
│   │   └── icons.py              # SVG icon definitions
│   └── themes/
│       ├── dark.json
│       └── light.json
├── src/
│   ├── __init__.py
│   ├── app.py                    # Main application window
│   ├── config.py                 # Settings, constants, paths
│   ├── core/
│   │   ├── editor.py             # Code editor + line numbers
│   │   ├── tab_manager.py        # Multi-tab management
│   │   ├── syntax_highlighter.py # Regex-based highlighting
│   │   ├── file_manager.py       # Open, save, new files
│   │   ├── terminal.py           # Real interactive shell
│   │   ├── search.py             # Find & replace
│   │   ├── git_manager.py        # Git operations
│   │   ├── extension_manager.py  # VS Code marketplace
│   │   ├── command_palette.py    # Ctrl+Shift+P launcher
│   │   └── updater.py            # GitHub release checker
│   ├── ui/
│   │   ├── menubar.py            # Menu bar
│   │   ├── sidebar.py            # Tabbed sidebar panels
│   │   ├── statusbar.py          # Bottom status bar
│   │   ├── toolbar.py            # Top toolbar buttons
│   │   ├── file_tree.py          # File explorer tree
│   │   ├── welcome.py            # Welcome tab
│   │   ├── splash.py             # Animated startup screen
│   │   ├── extensions_panel.py   # Extension browser UI
│   │   └── settings_panel.py     # Settings GUI
│   └── utils/
│       ├── icon_manager.py       # SVG to PhotoImage renderer
│       ├── theme_loader.py       # JSON theme loader
│       ├── recent_files.py       # Recent files tracker
│       ├── shortcuts.py          # Keyboard bindings
│       └── styles.py             # Round button factory
├── scripts/
│   └── generate_icon.py          # Generate icon.ico from code
├── tests/
│   ├── test_editor.py
│   └── test_file_manager.py
├── .github/
│   └── workflows/
│       ├── build.yml             # CI: test + build on push
│       └── release.yml           # CD: build + publish release
├── OmniIDE.spec                  # PyInstaller build config
├── requirements.txt
├── setup.py
├── run.py                        # Entry point
├── LICENSE
└── README.md
🛠️ Tech Stack
Component	Technology
Language	Python 3.10+
GUI Framework	Tkinter + ttkbootstrap
Icons	Custom SVG → PhotoImage renderer
Themes	JSON color schemes (Catppuccin)
Build	PyInstaller (single executable)
CI/CD	GitHub Actions
Extensions	VS Code Marketplace API
Terminal	subprocess.Popen (real shell)
No Electron. No Node.js. No heavy frameworks.
Starts in under 2 seconds. Executable under 30MB.

🤝 Contributing
Contributions are welcome! Here's how:

Bash

# 1. Fork the repository

# 2. Create a feature branch
git checkout -b feature/my-feature

# 3. Make your changes

# 4. Run tests
python -m pytest tests/ -v

# 5. Commit
git commit -m "feat: add my feature"

# 6. Push and create a PR
git push origin feature/my-feature
Contribution Ideas
🎨 New themes (Dracula, Nord, Solarized, Monokai)
🌐 More syntax highlighting languages
🧩 Extension system improvements
🐛 Bug fixes
📸 Screenshots for README
📖 Documentation improvements
🧪 More unit tests
📋 Changelog
v1.0.4 (Latest)
⚙️ Settings GUI panel (Ctrl+,)
🔄 Auto-update checker (GitHub Releases)
🎯 Live-apply settings (font, theme, wrap)
🔍 Searchable settings
v1.0.2
🎯 Command Palette (Ctrl+Shift+P) — 50+ commands
🔧 Fixed button hover staying highlighted
📝 Go to Line, Toggle Comment, Line operations
🔄 Zoom reset (Ctrl+0)
v1.0.1
📁 VS Code Extension marketplace browser
🔗 Full Git integration (clone, commit, push, pull)
💻 Real interactive terminal with shell selection
🚀 Animated startup splash screen
🎨 SVG icon system (replaced emojis)
🔘 Round modern buttons with hover effects
📑 Organized tabbed sidebar
v1.0.0
🖥️ Initial release
✏️ Multi-tab editor with syntax highlighting
📁 File explorer sidebar
🔍 Find & Replace
🌙 Dark/Light themes
⌨️ Keyboard shortcuts
📜 License
text

MIT License

Copyright (c) 2026 OmniNodeCo

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
<div align="center">
Made with ❤️ by OmniNodeCo