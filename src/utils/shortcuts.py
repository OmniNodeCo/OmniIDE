"""Keyboard shortcut bindings — with command palette."""


class ShortcutManager:
    """Manages global keyboard shortcuts."""

    def __init__(self, app):
        self.app = app
        self.root = app.root

    def bind_all(self):
        """Bind all keyboard shortcuts."""
        bindings = {
            # File
            "<Control-n>": lambda e: self.app.file_manager.new_file(),
            "<Control-N>": lambda e: self.app.file_manager.new_file(),
            "<Control-o>": lambda e: self.app.file_manager.open_file(),
            "<Control-O>": lambda e: self.app.file_manager.open_file(),
            "<Control-s>": lambda e: self.app.file_manager.save_file(),
            "<Control-S>": lambda e: self.app.file_manager.save_file(),
            "<Control-Shift-S>": lambda e: self.app.file_manager.save_file_as(),
            "<Control-w>": lambda e: self.app.tab_manager.close_active_tab(),
            "<Control-W>": lambda e: self.app.tab_manager.close_active_tab(),

            # Search
            "<Control-f>": lambda e: self.app.toggle_search(),
            "<Control-F>": lambda e: self.app.toggle_search(),

            # View
            "<Control-b>": lambda e: self.app.toggle_sidebar(),
            "<Control-B>": lambda e: self.app.toggle_sidebar(),
            "<Control-grave>": lambda e: self.app.toggle_terminal(),

            # Zoom
            "<Control-plus>": lambda e: self._zoom_in(),
            "<Control-equal>": lambda e: self._zoom_in(),
            "<Control-minus>": lambda e: self._zoom_out(),
            "<Control-0>": lambda e: self._zoom_reset(),

            # Command palette
            "<Control-Shift-P>": lambda e: self.app.toggle_command_palette(),
            "<Control-Shift-p>": lambda e: self.app.toggle_command_palette(),

            # Go to line
            "<Control-g>": lambda e: self._go_to_line(),
            "<Control-G>": lambda e: self._go_to_line(),

            # Toggle comment
            "<Control-slash>": lambda e: self._toggle_comment(),
        }

        for key, callback in bindings.items():
            try:
                self.root.bind_all(key, callback)
            except Exception:
                pass

    def _zoom_in(self):
        self.app.settings["font_size"] = min(
            32, self.app.settings["font_size"] + 1
        )
        self._apply_font()

    def _zoom_out(self):
        self.app.settings["font_size"] = max(
            8, self.app.settings["font_size"] - 1
        )
        self._apply_font()

    def _zoom_reset(self):
        self.app.settings["font_size"] = 13
        self._apply_font()

    def _apply_font(self):
        s = self.app.settings["font_size"]
        f = self.app.settings["font_family"]
        for info in self.app.tab_manager.tabs.values():
            info["editor"].configure(font=(f, s))
            info["line_numbers"].set_font((f, s))
            info["line_numbers"].redraw()
        self.app.save_settings()
        self.app.set_status(f"Font size: {s}")

    def _go_to_line(self):
        self.app.command_palette._go_to_line()

    def _toggle_comment(self):
        self.app.command_palette._toggle_comment()