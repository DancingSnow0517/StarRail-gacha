from typing import Union

from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QIcon
from qfluentwidgets import SettingCard, FluentIconBase, PrimaryPushButton


class PrimaryPushSettingCard(SettingCard):
    clicked = pyqtSignal()

    def __init__(self, button_text: str, icon: Union[str, QIcon, FluentIconBase], title, content=None, parent=None):
        super().__init__(icon, title, content, parent)

        self.button = PrimaryPushButton(button_text, self)
        self.button.setMinimumWidth(100)
        self.hBoxLayout.addWidget(self.button, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(16)

        self.button.clicked.connect(self.clicked)
