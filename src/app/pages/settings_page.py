from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFrame, QLabel, QHBoxLayout


class SettingsPage(QFrame):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("setting_page")

        self.label = QLabel("Settings Page", self)
        self.label.setAlignment(Qt.AlignCenter)

        self.hBoxLayout = QHBoxLayout(self)
        self.hBoxLayout.addWidget(self.label, 1, Qt.AlignCenter)

        # leave some space for title bar
        self.hBoxLayout.setContentsMargins(0, 32, 0, 0)
