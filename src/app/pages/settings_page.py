from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QFrame, QLabel, QVBoxLayout, QHBoxLayout, QSpacerItem, QSizePolicy
from qfluentwidgets import LineEdit, ToolButton, PushButton, HyperlinkButton, SwitchButton, FluentIcon


class SettingsPage(QFrame):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("setting_page")

        self.vBoxLayout = QVBoxLayout(self)

        self.settingLabel = QLabel("设置", self)
        self.settingLabel.setFont(QFont("Microsoft YaHei", 24, QFont.Bold))
        self.vBoxLayout.addWidget(self.settingLabel, 1, Qt.AlignTop)

        self.gamePathLayout = QHBoxLayout()
        self.gamePathLabel = QLabel("游戏路径", self)
        self.gamePathLabel.setFont(QFont("Microsoft YaHei", 12))

        self.gamePathEdit = LineEdit(self)
        self.gamePathEdit.setPlaceholderText("请输入游戏路径")
        self.gamePathEdit.setFont(QFont("Microsoft YaHei", 12))
        self.gamePathEdit.setClearButtonEnabled(True)

        # noinspection PyTypeChecker
        self.gamePathButton = ToolButton(FluentIcon.SYNC)
        self.gamePathButton.setToolTip("自动获取游戏路径")
        self.gamePathButton.resize(40, 40)

        self.gamePathLayout.addWidget(self.gamePathLabel)
        self.gamePathLayout.addWidget(self.gamePathEdit)
        self.gamePathLayout.addWidget(self.gamePathButton)
        self.vBoxLayout.addLayout(self.gamePathLayout)

        self.vBoxLayout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        self.getFullDataLayout = QHBoxLayout()
        self.getFullDataLabel = QLabel("获取完整数据", self)
        self.getFullDataLabel.setFont(QFont("Microsoft YaHei", 12))
        # noinspection PyTypeChecker
        self.getFullDataButton = SwitchButton("关", self)
        self.getFullDataDescLabel = QLabel(
            "开启后，点击”更新数据“按钮会完整获取6个月内的所有的抽卡记录，可能会花费比较长的时间。", self)
        self.getFullDataDescLabel.setFont(QFont("Microsoft YaHei", 8))
        self.getFullDataDescLabel.setStyleSheet("color: #666666;")

        self.getFullDataLayout.addWidget(self.getFullDataLabel)
        self.getFullDataLayout.addWidget(self.getFullDataButton, 1, Qt.AlignRight)
        self.vBoxLayout.addLayout(self.getFullDataLayout)
        self.vBoxLayout.addWidget(self.getFullDataDescLabel)

        self.vBoxLayout.addItem(QSpacerItem(40, 340, QSizePolicy.Expanding, QSizePolicy.Minimum))

        self.aboutLabel = QLabel("关于", self)
        self.aboutLabel.setFont(QFont("Microsoft YaHei", 24, QFont.Bold))
        self.vBoxLayout.addWidget(self.aboutLabel, 1, Qt.AlignTop)

        self.aboutTextLabel = QLabel("本项目是一个基于Python的星穹铁道抽卡导出工具，使用PyQt5作为GUI框架。")
        self.aboutTextLabel.setFont(QFont("Microsoft YaHei", 12))
        self.vBoxLayout.addWidget(self.aboutTextLabel, 1, Qt.AlignTop)

        self.githubLink = HyperlinkButton("https://github.com/DancingSnow0517/StarRail-gacha", "项目地址")
        self.githubLink.setFont(QFont("Microsoft YaHei", 12))
        self.vBoxLayout.addWidget(self.githubLink, 1, Qt.AlignTop | Qt.AlignLeft)

        self.vBoxLayout.addItem(QSpacerItem(40, 30, QSizePolicy.Expanding, QSizePolicy.Minimum))

        self.saveButton = PushButton("保存", self, FluentIcon.SAVE)
        self.saveButton.setMinimumWidth(100)
        self.vBoxLayout.addWidget(self.saveButton, 1, Qt.AlignBottom | Qt.AlignRight)

        # leave some space for title bar
        self.vBoxLayout.setContentsMargins(16, 32, 16, 16)
