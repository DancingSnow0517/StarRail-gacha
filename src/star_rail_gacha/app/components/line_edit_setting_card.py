from typing import Union

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from qfluentwidgets import SettingCard, LineEdit, FluentIconBase


class LineEditSettingCard(SettingCard):

    def __init__(self, value: str, icon: Union[str, QIcon, FluentIconBase], title, content=None, parent=None):
        super().__init__(icon, title, content, parent)

        self.lineEdit = LineEdit(self)
        self.lineEdit.setText(value)
        self.lineEdit.setMinimumWidth(300)

        self.hBoxLayout.addWidget(self.lineEdit, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(16)
