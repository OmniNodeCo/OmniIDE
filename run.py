"""
OmniIDE by OmniNodeCo
Entry point for the application.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.app import OmniIDEApp


def main():
    app = OmniIDEApp()
    app.run()


if __name__ == "__main__":
    main()