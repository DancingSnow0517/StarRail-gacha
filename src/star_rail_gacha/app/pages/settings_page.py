import re

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QLabel, QWidget, QFileDialog
from qfluentwidgets import FluentIcon, InfoBar, setTheme, setThemeColor, Theme, SettingCardGroup, \
    SwitchSettingCard, ExpandLayout, ScrollArea, HyperlinkCard, MessageBox, StateToolTip

from ..components.combo_box_setting_card import ComboBoxSettingCard
from ..components.game_path_setting_card import GamePathSettingCard
from ..components.language_setting_card import LanguageSettingCard
from ..components.line_edit_setting_card import LineEditSettingCard
from ..components.save_setting_card import PrimaryPushSettingCard
from ..components.theme_color_setting_card import ThemeColorSettingCard
from ...constant import VERSION
from ...utils.config import config
from ...utils.style_sheet import StyleSheet
from ...utils.update import check_update, download_update, apply_update


class SettingsPage(ScrollArea):
    stateTooltipSignal = pyqtSignal(str, str, bool)
    downloadedUpdateSignal = pyqtSignal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("setting_page")

        self.stateTooltip = None
        self.stateTooltipSignal.connect(self.onStateTooltip)
        self.downloadedUpdateSignal.connect(apply_update)

        self.scrollWidget = QWidget()
        self.expandLayout = ExpandLayout(self.scrollWidget)

        self.settingLabel = QLabel("设置", self)

        self.gachaSettingGroup = SettingCardGroup("抽卡记录获取设置", self.scrollWidget)
        self.gamePathCard = GamePathSettingCard(
            "选择文件夹",
            FluentIcon.FOLDER,
            "游戏路径",
            config.game_path,
            self.gachaSettingGroup
        )
        self.gamePathCard.clicked.connect(self.onGamePathCardClicked)
        self.getFullDataCard = SwitchSettingCard(
            FluentIcon.SYNC,
            "获取完整数据",
            "开启后，点击”更新数据“按钮会完整获取6个月内的所有的抽卡记录，可能会花费比较长的时间。",
            parent=self.gachaSettingGroup
        )
        self.getFullDataCard.switchButton.setChecked(config.get_full_data)

        self.personalGroup = SettingCardGroup("个性化", self.scrollWidget)
        self.themeCard = SwitchSettingCard(
            FluentIcon.BRUSH,
            "深色主题",
            "开启后，界面会变成深色模式。",
            parent=self.personalGroup
        )
        self.themeCard.switchButton.setChecked(config.dark_mode)
        self.themeColorCard = ThemeColorSettingCard(
            "#009faa",
            config.theme_color,
            FluentIcon.PALETTE,
            "主题颜色",
            parent=self.personalGroup
        )
        self.languageCard = LanguageSettingCard(
            config.language,
            FluentIcon.LANGUAGE,
            "语言",
            "选择软件软件显示语言，重启后生效。",
            parent=self.personalGroup
        )
        self.showDepartureCard = SwitchSettingCard(
            FluentIcon.TAG,
            "显示始发跃迁",
            "开启后，抽卡记录中会显示始发跃迁。",
            parent=self.personalGroup
        )
        self.showDepartureCard.switchButton.setChecked(config.show_departure)

        self.otherGroup = SettingCardGroup("其他", self.scrollWidget)
        self.logLevelCard = ComboBoxSettingCard(
            config.log_level,
            ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
            FluentIcon.BOOK_SHELF,
            "日志等级",
            "设置写入文件日志等级，重启后生效。",
            parent=self.otherGroup
        )

        self.updateGroup = SettingCardGroup("软件更新", self.scrollWidget)
        self.updateCard = PrimaryPushSettingCard(
            "检查更新",
            FluentIcon.UPDATE,
            "检查 StarRail Gacha Exporter 更新",
            "当前版本：" + VERSION,
            parent=self.updateGroup
        )
        self.updateCard.clicked.connect(self.onCheckUpdate)
        self.useProxyCard = SwitchSettingCard(
            FluentIcon.GLOBE,
            "代理",
            "开启后，软件会使用代理地址来下载新版本。",
            parent=self.updateGroup
        )
        self.useProxyCard.switchButton.setChecked(config.use_proxy)
        self.ghProxyCard = LineEditSettingCard(
            config.gh_proxy,
            FluentIcon.GLOBE,
            "GitHub 代理",
            "设置 GitHub 代理地址",
            parent=self.updateGroup
        )

        self.aboutGroup = SettingCardGroup("关于", self.scrollWidget)
        self.githubCard = HyperlinkCard(
            "https://github.com/DancingSnow0517/StarRail-gacha",
            "GitHub 仓库",
            FluentIcon.GITHUB,
            "打开 GitHub 仓库",
            "本项目已经在github使用 MIT 许可证开源！",
            self.aboutGroup
        )
        self.feedbackCard = HyperlinkCard(
            "https://github.com/DancingSnow0517/StarRail-gacha/issues",
            "反馈问题",
            FluentIcon.FEEDBACK,
            "打开 GitHub Issues",
            "如果你在使用过程中遇到了问题，欢迎在 GitHub Issues 中反馈！",
            self.aboutGroup
        )
        self.qqGroupCard = HyperlinkCard(
            "https://qm.qq.com/cgi-bin/qm/qr?k=s61-P0XfzSf31k7U1DwEy9gwwZQZ1ibP&jump_from=webapi&authKey=rr2tKgtASGSdUZWfhmgd75Tz49BPyCELq20t4q4Qg9uiP8+aXM2BGonpssyeCxpp",
            "QQ群",
            FluentIcon.CHAT,
            "加入QQ群",
            "欢迎加入QQ群，一起讨论本项目可以改进的地方！",
            self.aboutGroup
        )

        self.saveCard = PrimaryPushSettingCard(
            "保存",
            FluentIcon.SAVE,
            "保存设置",
            parent=self.scrollWidget
        )

        self.__initWidget()

    def __initWidget(self):
        self.resize(1000, 800)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setViewportMargins(0, 80, 0, 20)
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)

        # initialize style sheet
        self.scrollWidget.setObjectName('scrollWidget')
        self.settingLabel.setObjectName('settingLabel')
        StyleSheet.SETTINGS_PAGE.apply(self)

        self.saveCard.clicked.connect(self.save_config)

        # initialize layout
        self.__initLayout()

    def __initLayout(self):
        self.settingLabel.move(36, 30)

        self.gachaSettingGroup.addSettingCard(self.gamePathCard)
        self.gachaSettingGroup.addSettingCard(self.getFullDataCard)

        self.personalGroup.addSettingCard(self.themeCard)
        self.personalGroup.addSettingCard(self.themeColorCard)
        self.personalGroup.addSettingCard(self.languageCard)
        self.personalGroup.addSettingCard(self.showDepartureCard)

        self.otherGroup.addSettingCard(self.logLevelCard)

        self.updateGroup.addSettingCard(self.updateCard)
        self.updateGroup.addSettingCard(self.useProxyCard)
        self.updateGroup.addSettingCard(self.ghProxyCard)

        self.aboutGroup.addSettingCard(self.githubCard)
        self.aboutGroup.addSettingCard(self.feedbackCard)
        self.aboutGroup.addSettingCard(self.qqGroupCard)

        self.expandLayout.setSpacing(28)
        self.expandLayout.setContentsMargins(36, 10, 36, 0)
        self.expandLayout.addWidget(self.gachaSettingGroup)
        self.expandLayout.addWidget(self.personalGroup)
        self.expandLayout.addWidget(self.otherGroup)
        self.expandLayout.addWidget(self.updateGroup)
        self.expandLayout.addWidget(self.aboutGroup)
        self.expandLayout.addWidget(self.saveCard)

    def onGamePathCardClicked(self):
        directory = QFileDialog.getExistingDirectory(self.window(), "选择游戏路径", config.game_path)
        if directory:
            self.gamePathCard.setContent(directory + "/")

    def onStateTooltip(self, title: str, subTitle: str, show: bool):
        if show:
            self.stateTooltip = StateToolTip(title, subTitle, self.window())
            self.stateTooltip.move(self.stateTooltip.getSuitablePos())
            self.stateTooltip.show()
        else:
            self.stateTooltip.setContent(title)
            self.stateTooltip.setState(True)
            self.stateTooltip = None

    def save_config(self):
        config.game_path = self.gamePathCard.contentLabel.text()
        config.get_full_data = self.getFullDataCard.switchButton.isChecked()
        config.dark_mode = self.themeCard.switchButton.isChecked()
        config.theme_color = self.themeColorCard.customColorLineEdit.text() if \
            self.themeColorCard.customRadioButton.isChecked() else \
            "#009faa"
        language_text = self.languageCard.comboBox.currentText()
        match = re.match(r".*\((.*)\)", language_text)
        if match:
            config.language = match.group(1)
        else:
            config.language = language_text
        config.log_level = self.logLevelCard.comboBox.text()
        config.gh_proxy = self.ghProxyCard.lineEdit.text()
        config.use_proxy = self.useProxyCard.switchButton.isChecked()
        config.show_departure = self.showDepartureCard.switchButton.isChecked()
        config.showDepartureChanged.emit(config.show_departure)
        config.save()
        setTheme(Theme.DARK if config.dark_mode else Theme.LIGHT)
        setThemeColor(config.theme_color)

        InfoBar.success("", "配置文件保存成功！", parent=self, duration=2000)

    def onCheckUpdate(self):
        tag = check_update()
        if tag is None:
            InfoBar.success("检查更新", "当前已经是最新版本！", parent=self.window(), duration=2000)
            return

        m = MessageBox("检查更新", "发现新版本：" + tag + "\n是否现在下载安装？", self.window())
        if m.exec_():
            download_update(self)
