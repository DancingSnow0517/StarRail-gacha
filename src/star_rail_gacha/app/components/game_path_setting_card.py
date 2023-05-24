from typing import Union

from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QIcon
from qfluentwidgets import SettingCard, FluentIconBase, PushButton, FluentIcon, ToolButton

from ...utils.files import get_game_path


class GamePathSettingCard(SettingCard):
    clicked = pyqtSignal()

    def __init__(self, button_text: str, icon: Union[str, QIcon, FluentIconBase], title, content=None, parent=None):
        super().__init__(icon, title, content, parent)

        # noinspection PyTypeChecker
        self.gamePathButton = ToolButton(FluentIcon.SYNC)
        self.gamePathButton.clicked.connect(lambda: self.setContent(get_game_path()))

        self.button = PushButton(button_text, self)
        self.hBoxLayout.addWidget(self.button, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(4)
        self.hBoxLayout.addWidget(self.gamePathButton, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(16)
        self.button.clicked.connect(self.clicked)
