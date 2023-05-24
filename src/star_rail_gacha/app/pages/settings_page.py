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

        self.settingLabel = QLabel(self.tr("Settings"), self)

        self.gachaSettingGroup = SettingCardGroup(self.tr("Gacha record fetch settings"), self.scrollWidget)
        self.gamePathCard = GamePathSettingCard(
            self.tr("Select folder"),
            FluentIcon.FOLDER,
            "Game Path",
            config.game_path,
            self.gachaSettingGroup
        )
        self.gamePathCard.clicked.connect(self.onGamePathCardClicked)
        self.getFullDataCard = SwitchSettingCard(
            FluentIcon.SYNC,
            self.tr("Fetch full data"),
            self.tr("When opening, clicking the 'Update Data' button will fully fetch all gacha records within 6 months, which may take a relatively long time."),
            parent=self.gachaSettingGroup
        )
        self.getFullDataCard.switchButton.setChecked(config.get_full_data)

        self.personalGroup = SettingCardGroup(self.tr("personalization"), self.scrollWidget)
        self.themeCard = SwitchSettingCard(
            FluentIcon.BRUSH,
            self.tr("Dark Theme"),
            self.tr("When opening, the interface will change to dark mode."),
            parent=self.personalGroup
        )
        self.themeCard.switchButton.setChecked(config.dark_mode)
        self.themeColorCard = ThemeColorSettingCard(
            "#009faa",
            config.theme_color,
            FluentIcon.PALETTE,
            self.tr("Theme Color"),
            parent=self.personalGroup
        )
        self.languageCard = LanguageSettingCard(
            config.language,
            FluentIcon.LANGUAGE,
            self.tr("Language"),
            self.tr("Select the software display language, which will take effect after restarting."),
            parent=self.personalGroup
        )
        self.showDepartureCard = SwitchSettingCard(
            FluentIcon.TAG,
            self.tr("Show Departure Warp"),
            "When opening，Departure warp will be displayed in the Home Page.",
            parent=self.personalGroup
        )
        self.showDepartureCard.switchButton.setChecked(config.show_departure)

        self.otherGroup = SettingCardGroup(self.tr("Other"), self.scrollWidget)
        self.logLevelCard = ComboBoxSettingCard(
            config.log_level,
            ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
            FluentIcon.BOOK_SHELF,
            self.tr("Log Level"),
            self.tr("Set the log level of the software. The higher the level, the more logs will be output, which will take effect after restarting."),
            parent=self.otherGroup
        )

        self.updateGroup = SettingCardGroup(self.tr("Software updates"), self.scrollWidget)
        self.updateCard = PrimaryPushSettingCard(
            self.tr("Check for updates"),
            FluentIcon.UPDATE,
            self.tr("Check for updates to StarRail Gacha Exporter."),
            self.tr("Current version: ") + VERSION,
            parent=self.updateGroup
        )
        self.updateCard.clicked.connect(self.onCheckUpdate)
        self.useProxyCard = SwitchSettingCard(
            FluentIcon.GLOBE,
            self.tr("Proxy"),
            self.tr("When opening, The software will use a proxy address to download new versions."),
            parent=self.updateGroup
        )
        self.useProxyCard.switchButton.setChecked(config.use_proxy)
        self.ghProxyCard = LineEditSettingCard(
            config.gh_proxy,
            FluentIcon.GLOBE,
            self.tr("GitHub Proxy"),
            self.tr("Set GitHub proxy address"),
            parent=self.updateGroup
        )

        self.aboutGroup = SettingCardGroup(self.tr("About"), self.scrollWidget)
        self.githubCard = HyperlinkCard(
            "https://github.com/DancingSnow0517/StarRail-gacha",
            self.tr("GitHub repository"),
            FluentIcon.GITHUB,
            self.tr("Open the GitHub repository"),
            self.tr("This project is already open source using the MIT license on Github!"),
            self.aboutGroup
        )
        self.feedbackCard = HyperlinkCard(
            "https://github.com/DancingSnow0517/StarRail-gacha/issues",
            self.tr("Feedback issues"),
            FluentIcon.FEEDBACK,
            self.tr("Open GitHub Issues"),
            self.tr("If you encounter any problems during use, please feel free to provide feedback on GitHub Issues!"),
            self.aboutGroup
        )
        self.qqGroupCard = HyperlinkCard(
            "https://qm.qq.com/cgi-bin/qm/qr?k=s61-P0XfzSf31k7U1DwEy9gwwZQZ1ibP&jump_from=webapi&authKey=rr2tKgtASGSdUZWfhmgd75Tz49BPyCELq20t4q4Qg9uiP8+aXM2BGonpssyeCxpp",
            self.tr("QQ Group"),
            FluentIcon.CHAT,
            self.tr("Join QQ group"),
            self.tr("Welcome to join the QQ group and discuss for improvement in this project together!"),
            self.aboutGroup
        )

        self.saveCard = PrimaryPushSettingCard(
            self.tr("Save Settings"),
            FluentIcon.SAVE,
            self.tr("Save the current settings"),
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
        directory = QFileDialog.getExistingDirectory(self.window(), self.tr("Choose a game path"), config.game_path)
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

        InfoBar.success("", self.tr("Configuration file saved successfully!"), parent=self, duration=2000)

    def onCheckUpdate(self):
        tag = check_update()
        if tag is None:
            InfoBar.success(self.tr("Check update"), self.tr("It is currently the latest version!"), parent=self.window(), duration=2000)
            return

        m = MessageBox(self.tr("Check update"),
                       self.tr("Discovering a new version: %s\nDo you want to download and install now?") % tag,
                       self.window())
        if m.exec_():
            download_update(self)
