# Changelog

All notable changes to OmniIDE are documented here.

## [1.1.0] — 2026-08-23

### Added
- **Quick Open** (`Ctrl+P`) — fuzzy file finder for the current project with a cached, pruned index
- **Search in Files** (`Ctrl+Shift+F`) — dedicated sidebar panel: project-wide search with line numbers, match counts, case / whole-word / regex options, double-click to open at line
- **Line actions** — Duplicate (`Ctrl+D`), Delete (`Ctrl+Shift+D`), Move Up/Down (`Alt+Up` / `Alt+Down`), Sort Lines (`Ctrl+Shift+O`)
- **Toggle Comment** (`Ctrl+/`) — 30+ file types with correct per-language comment styles
- **Find & Replace upgrades** — whole-word (`W`) and regex (`.*`) options with live match counts
- **Markdown Preview** (`Ctrl+Shift+V`) — built-in dependency-free Markdown → HTML converter (headings, lists, tables, code fences, blockquotes, links, images) rendered in a read-only tab
- **Multi-terminal** — multiple shell tabs (`Ctrl+Shift+T`), per-session history, context menu
- **Breadcrumbs** — path bar above the editor; click a segment to expand the file tree there
- **Minimap** — bar-style document overview; current line + visible viewport; click or drag to jump (Settings → Show Minimap)
- **Smart brackets** — auto-close on typing, delete empty pair on backspace, matching-bracket highlight
- **JSON validation** — invalid JSON blocked on save with error marker and status bar position
- **File tree context menu** — New File, New Folder, Rename, Delete, Copy Path
- **Show hidden files** toggle (file tree + settings)
- **Auto save** — optional interval timer plus save on tab switch
- **Save All** (`Ctrl+Alt+S`), **Close Others / Close All Tabs** (File menu + tab context menu)
- **Line endings** — LF / CRLF / CR detection in the status bar, one-click conversion (Edit menu)
- **Drag & drop** files (or folders) onto the editor
- **Reorderable editor tabs** with context menu (close / close others / close all / copy path); double-click closes
- **Syntax highlighting** for Markdown, YAML, Rust, and Go
- **Command Palette** expanded to 50+ fuzzy-ranked commands
- Status bar selection info (word count of selection)

### Changed
- Welcome tab now lists recent files and the new shortcuts
- Settings dialog: new sections (Files), new options (indent with tabs, line ending, auto save interval, max search results, minimap, smart brackets)
- Editor welcome text and status bar wording

### Fixed
- Cursor resolution for line actions now targets the selected line correctly
- Search results open the file at the exact match line

## [1.0.7]
- Version bump with all v1.0.6 fixes verified
- Updated all CI workflows
- README badges and views fixed

## [1.0.6]
- SVG icons for sidebar, git, extensions (PyQt6.QtSvg)
- Thread-safe extension search (pyqtSignal)
- Fixed marketplace cards not appearing
- Styled extension cards

## [1.0.5]
- Fixed Ubuntu 24.04 CI (libgl1)
- QT_QPA_PLATFORM=offscreen for tests

## [1.0.4]
- Complete rewrite: Tkinter → PyQt6
- QProcess terminal, QSS theming
- Real VSIX extension installation
- Documentation website

## [1.0.3]
- Settings GUI, auto-update checker

## [1.0.2]
- Command Palette, Go to Line

## [1.0.1]
- Extensions, Git, terminal, SVG icons

## [1.0.0]
- Initial release
