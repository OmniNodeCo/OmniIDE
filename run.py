"""OmniIDE by OmniNodeCo — PyQt6 entry point."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import Qt
    from src.app import OmniIDEApp

    app = QApplication(sys.argv)
    app.setApplicationName("OmniIDE")
    app.setOrganizationName("OmniNodeCo")

    window = OmniIDEApp()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()