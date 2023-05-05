import logging

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QFrame, QLabel, QVBoxLayout, QHBoxLayout, QSpacerItem, QSizePolicy
from qfluentwidgets import LineEdit, ToolButton, PushButton, HyperlinkButton, SwitchButton, FluentIcon, InfoBar, \
    qconfig, setTheme, Theme, ComboBox

from ...utils.files import get_game_path
from ...utils.config import config
from ...utils.style_sheet import StyleSheet


class SettingsPage(QFrame):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("setting_page")

        self.vBoxLayout = QVBoxLayout(self)

        self.settingLabel = QLabel("设置", self)
        self.settingLabel.setContentsMargins(0, 8, 0, 0)
        self.settingLabel.setFont(QFont("Microsoft YaHei", 24, QFont.Bold))
        self.vBoxLayout.addWidget(self.settingLabel, 1, Qt.AlignTop)

        self.gamePathLayout = QHBoxLayout()
        self.gamePathLabel = QLabel("游戏路径", self)
        self.gamePathLabel.setFont(QFont("Microsoft YaHei", 12))

        self.gamePathEdit = LineEdit(self)
        self.gamePathEdit.setPlaceholderText("请输入游戏路径")
        self.gamePathEdit.setFont(QFont("Microsoft YaHei", 12))
        self.gamePathEdit.setClearButtonEnabled(True)
        self.gamePathEdit.setText(config.game_path)

        # noinspection PyTypeChecker
        self.gamePathButton = ToolButton(FluentIcon.SYNC)
        self.gamePathButton.setToolTip("自动获取游戏路径")
        self.gamePathButton.clicked.connect(self.onGetInGamePathButtonClick)
        self.gamePathButton.resize(40, 40)

        self.gamePathDescLabel = QLabel(
            "这个路径是用于寻找日志的路径。留空为自动获取游戏路径。仅当无法自动找到游戏文件夹时使用！", self)
        self.gamePathDescLabel.setFont(QFont("Microsoft YaHei", 8))
        self.gamePathDescLabel.setStyleSheet("color: #666666;")

        self.gamePathLayout.addWidget(self.gamePathLabel)
        self.gamePathLayout.addWidget(self.gamePathEdit)
        self.gamePathLayout.addWidget(self.gamePathButton)
        self.vBoxLayout.addLayout(self.gamePathLayout)
        self.vBoxLayout.addWidget(self.gamePathDescLabel)

        self.vBoxLayout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        self.getFullDataLayout = QHBoxLayout()
        self.getFullDataLabel = QLabel("获取完整数据", self)
        self.getFullDataLabel.setFont(QFont("Microsoft YaHei", 12))
        # noinspection PyTypeChecker
        self.getFullDataButton = SwitchButton("关", self)
        self.getFullDataButton.checkedChanged.connect(self.onGetFullDataButtonSwitch)
        self.getFullDataButton.setChecked(config.get_full_data)
        self.getFullDataDescLabel = QLabel(
            "开启后，点击”更新数据“按钮会完整获取6个月内的所有的抽卡记录，可能会花费比较长的时间。", self)
        self.getFullDataDescLabel.setFont(QFont("Microsoft YaHei", 8))
        self.getFullDataDescLabel.setStyleSheet("color: #666666;")

        self.getFullDataLayout.addWidget(self.getFullDataLabel)
        self.getFullDataLayout.addWidget(self.getFullDataButton, 1, Qt.AlignRight)
        self.vBoxLayout.addLayout(self.getFullDataLayout)
        self.vBoxLayout.addWidget(self.getFullDataDescLabel)

        self.vBoxLayout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        self.darkModeLayout = QHBoxLayout()
        self.darkModeLabel = QLabel("黑暗模式", self)
        self.darkModeLabel.setFont(QFont("Microsoft YaHei", 12))
        # noinspection PyTypeChecker
        self.darkModeButton = SwitchButton("关", self)
        self.darkModeButton.checkedChanged.connect(self.onDarkModeButtonSwitch)
        self.darkModeButton.setChecked(config.dark_mode)
        self.darkModeDescLabel = QLabel("开启后，界面会变成黑暗模式。", self)
        self.darkModeDescLabel.setFont(QFont("Microsoft YaHei", 8))
        self.darkModeDescLabel.setStyleSheet("color: #666666;")

        self.darkModeLayout.addWidget(self.darkModeLabel)
        self.darkModeLayout.addWidget(self.darkModeButton, 1, Qt.AlignRight)
        self.vBoxLayout.addLayout(self.darkModeLayout)
        self.vBoxLayout.addWidget(self.darkModeDescLabel)

        self.vBoxLayout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        self.logValueLayout = QHBoxLayout()
        self.logValueLabel = QLabel("日志等级", self)
        self.logValueLabel.setFont(QFont("Microsoft YaHei", 12))
        self.logValueBox = ComboBox(self)
        self.logValueBox.addItems(["DEBUG", "INFO", "WARNING", "ERROR", "FATAL"])
        self.logValueBox.setCurrentText(config.log_level)
        self.logValueBox.setMinimumSize(QSize(140, 0))
        self.logValueDescLabel = QLabel("设置日志等级。重启后生效！", self)
        self.logValueDescLabel.setFont(QFont("Microsoft YaHei", 8))
        self.logValueDescLabel.setStyleSheet("color: #666666;")

        self.logValueLayout.addWidget(self.logValueLabel)
        self.logValueLayout.addWidget(self.logValueBox, 1, Qt.AlignRight)
        self.vBoxLayout.addLayout(self.logValueLayout)
        self.vBoxLayout.addWidget(self.logValueDescLabel)

        self.vBoxLayout.addItem(QSpacerItem(40, 250, QSizePolicy.Expanding, QSizePolicy.Minimum))

        self.aboutLabel = QLabel("关于", self)
        self.aboutLabel.setFont(QFont("Microsoft YaHei", 24, QFont.Bold))
        self.vBoxLayout.addWidget(self.aboutLabel, 1, Qt.AlignTop)

        self.aboutTextLabel = QLabel("本项目是一个基于Python的星穹铁道抽卡导出工具，使用PyQt5作为GUI框架。")
        self.aboutTextLabel.setFont(QFont("Microsoft YaHei", 12))
        self.vBoxLayout.addWidget(self.aboutTextLabel, 1, Qt.AlignTop)

        self.linkLayout = QHBoxLayout()
        self.githubLink = HyperlinkButton("https://github.com/DancingSnow0517/StarRail-gacha", "项目地址")
        self.githubLink.setFont(QFont("Microsoft YaHei", 12))
        self.githubLink.setMaximumWidth(100)
        self.issueLink = HyperlinkButton("https://github.com/DancingSnow0517/StarRail-gacha/issues", "问题反馈")
        self.issueLink.setFont(QFont("Microsoft YaHei", 12))
        self.issueLink.setMaximumWidth(100)
        self.linkLayout.addWidget(self.githubLink, Qt.AlignLeft)
        self.linkLayout.addWidget(self.issueLink, Qt.AlignRight)
        self.linkLayout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        self.vBoxLayout.addLayout(self.linkLayout)

        self.vBoxLayout.addItem(QSpacerItem(40, 30, QSizePolicy.Expanding, QSizePolicy.Minimum))

        self.saveButton = PushButton("保存", self, FluentIcon.SAVE)
        self.saveButton.setMinimumWidth(100)
        self.saveButton.setFont(QFont("Microsoft YaHei", 12))
        self.saveButton.clicked.connect(self.save_config)
        self.vBoxLayout.addWidget(self.saveButton, 1, Qt.AlignBottom | Qt.AlignRight)

        # leave some space for title bar
        self.vBoxLayout.setContentsMargins(16, 32, 16, 16)

        qconfig.themeChanged.connect(self.set_theme)

    def onGetInGamePathButtonClick(self):
        game_path = get_game_path()
        if game_path:
            self.gamePathEdit.setText(game_path)

    def onGetFullDataButtonSwitch(self):
        if self.getFullDataButton.isChecked():
            self.getFullDataButton.setText("开")
        else:
            self.getFullDataButton.setText("关")

    def onDarkModeButtonSwitch(self):
        if self.darkModeButton.isChecked():
            self.darkModeButton.setText("开")
        else:
            self.darkModeButton.setText("关")

    def save_config(self):
        config.game_path = self.gamePathEdit.text()
        config.get_full_data = self.getFullDataButton.isChecked()
        config.dark_mode = self.darkModeButton.isChecked()
        config.log_level = self.logValueBox.currentText()
        config.save()

        setTheme(Theme.DARK if config.dark_mode else Theme.LIGHT)

        InfoBar.success("", "配置文件保存成功！", parent=self, duration=2000)

    def set_theme(self):
        StyleSheet.HOME_PAGE.apply(self)
