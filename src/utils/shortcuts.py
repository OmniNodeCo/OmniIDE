"""Keyboard shortcut bindings."""


class ShortcutManager:
    """Manages global keyboard shortcuts."""

    def __init__(self, app):
        self.app = app
        self.root = app.root

    def bind_all(self):
        """Bind all keyboard shortcuts."""
        bindings = {
            "<Control-n>": lambda e: self.app.file_manager.new_file(),
            "<Control-N>": lambda e: self.app.file_manager.new_file(),
            "<Control-o>": lambda e: self.app.file_manager.open_file(),
            "<Control-O>": lambda e: self.app.file_manager.open_file(),
            "<Control-s>": lambda e: self.app.file_manager.save_file(),
            "<Control-S>": lambda e: self.app.file_manager.save_file(),
            "<Control-Shift-S>": lambda e: self.app.file_manager.save_file_as(),
            "<Control-w>": lambda e: self.app.tab_manager.close_active_tab(),
            "<Control-W>": lambda e: self.app.tab_manager.close_active_tab(),
            "<Control-f>": lambda e: self.app.toggle_search(),
            "<Control-F>": lambda e: self.app.toggle_search(),
            "<Control-b>": lambda e: self.app.toggle_sidebar(),
            "<Control-B>": lambda e: self.app.toggle_sidebar(),
            "<Control-grave>": lambda e: self.app.toggle_terminal(),
            "<Control-plus>": lambda e: self._zoom_in(),
            "<Control-equal>": lambda e: self._zoom_in(),
            "<Control-minus>": lambda e: self._zoom_out(),
        }

        for key, callback in bindings.items():
            try:
                self.root.bind_all(key, callback)
            except Exception:
                pass

    def _zoom_in(self):
        self.app.settings["font_size"] = min(32, self.app.settings["font_size"] + 1)
        self._apply_font()

    def _zoom_out(self):
        self.app.settings["font_size"] = max(8, self.app.settings["font_size"] - 1)
        self._apply_font()

    def _apply_font(self):
        size = self.app.settings["font_size"]
        family = self.app.settings["font_family"]
        for info in self.app.tab_manager.tabs.values():
            info["editor"].configure(font=(family, size))
            info["line_numbers"].set_font((family, size))
            info["line_numbers"].redraw()
        self.app.save_settings()
        self.app.set_status(f"Font size: {size}")