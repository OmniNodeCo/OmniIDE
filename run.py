"""
OmniIDE by OmniNodeCo
Entry point — handles cleanup on exit.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    from src.app import OmniIDEApp

    app = OmniIDEApp()

    # Clean up terminal on exit
    def on_close():
        try:
            app.terminal.destroy()
        except Exception:
            pass
        try:
            app.save_settings()
        except Exception:
            pass
        app.root.destroy()

    app.root.protocol("WM_DELETE_WINDOW", on_close)
    app.run()


if __name__ == "__main__":
    main()