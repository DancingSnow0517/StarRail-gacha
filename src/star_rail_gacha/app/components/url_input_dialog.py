from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QLabel, QFrame, QVBoxLayout, QHBoxLayout
from qfluentwidgets import LineEdit, PrimaryPushButton, PushButton
from qfluentwidgets.components.dialog_box.mask_dialog_base import MaskDialogBase

from ...utils.style_sheet import StyleSheet


class URLInputDialog(MaskDialogBase):
    yesSignal = pyqtSignal()
    cancelSignal = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.titleLabel = QLabel(self.tr("Please enter gacha record URL:"), self.widget)
        self.urlLineEdit = LineEdit(self.widget)
        self.urlLineEdit.setPlaceholderText("https://api-takumi.mihoyo.com/")
        self.urlLineEdit.setClearButtonEnabled(True)
        self.urlLineEdit.setMinimumWidth(650)

        self.buttonGroup = QFrame(self.widget)
        self.yesButton = PrimaryPushButton(self.tr("OK"), self.buttonGroup)
        self.yesButton.clicked.connect(self.__yes_button_clicked)
        self.yesButton.setAttribute(Qt.WA_LayoutUsesWidgetRect)
        self.cancelButton = PushButton(self.tr("Cancel"), self.buttonGroup)
        self.cancelButton.clicked.connect(self.__cancel_button_clicked)
        self.cancelButton.setAttribute(Qt.WA_LayoutUsesWidgetRect)

        self.titleLabel.setObjectName("titleLabel")
        self.buttonGroup.setObjectName('buttonGroup')
        self.cancelButton.setObjectName('cancelButton')

        StyleSheet.URL_INPUT_DIALOG.apply(self)

        self.yesButton.adjustSize()
        self.cancelButton.adjustSize()

        self.yesButton.setFocus()
        self.buttonGroup.setFixedHeight(81)

        self.vBoxLayout = QVBoxLayout(self.widget)
        self.textLayout = QVBoxLayout()
        self.buttonLayout = QHBoxLayout(self.buttonGroup)

        self.vBoxLayout.setSpacing(0)
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.addLayout(self.textLayout, 1)
        self.vBoxLayout.addWidget(self.buttonGroup, 0, Qt.AlignBottom)
        self.vBoxLayout.setSizeConstraint(QVBoxLayout.SetMinimumSize)

        self.textLayout.setSpacing(12)
        self.textLayout.setContentsMargins(24, 24, 24, 24)
        self.textLayout.addWidget(self.titleLabel, 0, Qt.AlignTop)
        self.textLayout.addWidget(self.urlLineEdit, 0, Qt.AlignTop)

        self.buttonLayout.setSpacing(12)
        self.buttonLayout.setContentsMargins(24, 24, 24, 24)
        self.buttonLayout.addWidget(self.yesButton, 1, Qt.AlignVCenter)
        self.buttonLayout.addWidget(self.cancelButton, 1, Qt.AlignVCenter)

        self.setShadowEffect(60, (0, 10), QColor(0, 0, 0, 50))
        self.setMaskColor(QColor(0, 0, 0, 76))
        self._hBoxLayout.removeWidget(self.widget)
        self._hBoxLayout.addWidget(self.widget, 1, Qt.AlignCenter)

        self.buttonGroup.setMinimumWidth(280)
        self.widget.setFixedSize(500, 300)

    def __yes_button_clicked(self):
        self.accept()
        self.yesSignal.emit()

    def __cancel_button_clicked(self):
        self.reject()
        self.cancelSignal.emit()

    ...
