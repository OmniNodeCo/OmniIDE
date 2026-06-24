"""Splash screen — PyQt6."""

from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QProgressBar
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class SplashScreen(QWidget):
    """Startup splash screen."""

    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setFixedSize(420, 280)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)

        # Center on screen
        from PyQt6.QtWidgets import QApplication
        screen = QApplication.primaryScreen().geometry()
        self.move(
            (screen.width() - self.width()) // 2,
            (screen.height() - self.height()) // 2,
        )

        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e2e;
                border: 2px solid #313244;
                border-radius: 12px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 24)
        layout.setSpacing(8)

        layout.addStretch()

        # Logo text
        logo = QLabel("<  >")
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo.setFont(QFont("Consolas", 28, QFont.Weight.Bold))
        logo.setStyleSheet("color: #89b4fa; border: none;")
        layout.addWidget(logo)

        title = QLabel("OmniIDE")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        title.setStyleSheet("color: #cdd6f4; border: none;")
        layout.addWidget(title)

        subtitle = QLabel("by OmniNodeCo")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setFont(QFont("Segoe UI", 10))
        subtitle.setStyleSheet("color: #6c7086; border: none;")
        layout.addWidget(subtitle)

        layout.addStretch()

        # Status
        self.status_label = QLabel("Starting up...")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setFont(QFont("Segoe UI", 9))
        self.status_label.setStyleSheet("color: #6c7086; border: none;")
        layout.addWidget(self.status_label)

        # Progress bar
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setTextVisible(False)
        self.progress.setFixedHeight(4)
        self.progress.setStyleSheet("""
            QProgressBar {
                background-color: #313244;
                border: none;
                border-radius: 2px;
            }
            QProgressBar::chunk {
                background-color: #89b4fa;
                border-radius: 2px;
            }
        """)
        layout.addWidget(self.progress)

        # Version
        version = QLabel("v1.0.4")
        version.setAlignment(Qt.AlignmentFlag.AlignRight)
        version.setFont(QFont("Consolas", 8))
        version.setStyleSheet("color: #6c7086; border: none;")
        layout.addWidget(version)

    def set_status(self, text):
        self.status_label.setText(text)

    def set_progress(self, value):
        self.progress.setValue(value)