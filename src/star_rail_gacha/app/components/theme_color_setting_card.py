from typing import Union

from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QLabel, QWidget, QVBoxLayout, QButtonGroup, QHBoxLayout, QPushButton, QSizePolicy, \
    QSpacerItem
from qfluentwidgets import ExpandGroupSettingCard, FluentIcon, RadioButton, ColorDialog, LineEdit


class ThemeColorSettingCard(ExpandGroupSettingCard):

    def __init__(self, default_color: str, color: str, icon: Union[str, QIcon, FluentIcon], title: str,
                 content: str = None, parent=None):
        super().__init__(icon, title, content, parent)
        self.choiceLabel = QLabel(self)

        self.radioWidget = QWidget(self.view)
        self.radioLayout = QVBoxLayout(self.radioWidget)
        self.defaultRadioButton = RadioButton("默认颜色", self.radioWidget)
        self.customRadioButton = RadioButton("自定义颜色", self.radioWidget)
        self.buttonGroup = QButtonGroup(self)

        self.customColorWidget = QWidget(self.view)
        self.customColorLayout = QHBoxLayout(self.customColorWidget)

        self.customLabel = QLabel("自定义颜色", self.customColorWidget)
        self.customColorLineEdit = LineEdit(self.customColorWidget)
        self.customColorLineEdit.setMaximumWidth(100)
        self.chooseColorButton = QPushButton("选择颜色", self.customColorWidget)

        self.addWidget(self.choiceLabel)

        self.radioLayout.setSpacing(19)
        self.radioLayout.setAlignment(Qt.AlignTop)
        self.radioLayout.setContentsMargins(48, 18, 0, 18)
        self.buttonGroup.addButton(self.customRadioButton)
        self.buttonGroup.addButton(self.defaultRadioButton)
        self.radioLayout.addWidget(self.customRadioButton)
        self.radioLayout.addWidget(self.defaultRadioButton)
        self.radioLayout.setSizeConstraint(QVBoxLayout.SetMinimumSize)

        self.customColorLayout.setContentsMargins(48, 18, 44, 18)
        self.customColorLayout.addWidget(self.customLabel, 0, Qt.AlignLeft)
        self.customColorLayout.addWidget(self.customColorLineEdit, 0, Qt.AlignLeft)
        self.customColorLayout.addItem(QSpacerItem(300, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.customColorLayout.addWidget(self.chooseColorButton, 0, Qt.AlignRight)
        self.customColorLayout.setSizeConstraint(QHBoxLayout.SetMinimumSize)

        self.viewLayout.setSpacing(0)
        self.viewLayout.setContentsMargins(0, 0, 0, 0)
        self.addGroupWidget(self.radioWidget)
        self.addGroupWidget(self.customColorWidget)

        self._adjustViewSize()

        if default_color != color:
            self.customRadioButton.setChecked(True)
            self.chooseColorButton.setEnabled(True)
        else:
            self.defaultRadioButton.setChecked(True)
            self.chooseColorButton.setEnabled(False)
            self.customColorLineEdit.setEnabled(False)

        self.choiceLabel.setText(self.buttonGroup.checkedButton().text())
        self.choiceLabel.adjustSize()

        self.chooseColorButton.setObjectName('chooseColorButton')

        self.buttonGroup.buttonClicked.connect(self.__onRadioButtonClicked)
        self.chooseColorButton.clicked.connect(self.__showColorDialog)
        self.customColorLineEdit.setText(color)

    def __onRadioButtonClicked(self, button: RadioButton):
        """ radio button clicked slot """
        if button.text() == self.choiceLabel.text():
            return

        self.choiceLabel.setText(button.text())
        self.choiceLabel.adjustSize()

        if button is self.defaultRadioButton:
            self.chooseColorButton.setDisabled(True)
            self.customColorLineEdit.setDisabled(True)
        else:
            self.chooseColorButton.setDisabled(False)
            self.customColorLineEdit.setDisabled(False)

    def __showColorDialog(self):
        w = ColorDialog(self.customColorLineEdit.text(), "选择颜色", self.window())
        w.colorChanged.connect(lambda x: self.customColorLineEdit.setText(x.name()))
        w.exec()
