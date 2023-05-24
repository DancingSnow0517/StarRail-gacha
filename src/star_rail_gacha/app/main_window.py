from PyQt5 import QtGui
from PyQt5.QtCore import Qt, QSettings, QSize, QPoint, QVariant, QTranslator
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QHBoxLayout, QStackedWidget, QApplication
from qfluentwidgets import NavigationInterface, FluentIcon, NavigationItemPosition, qrouter
from qframelesswindow import FramelessWindow, StandardTitleBar

from .pages.history_page import HistoryPage
from .pages.home_page import HomePage
from .pages.settings_page import SettingsPage
from ..constant import VERSION
from ..utils.style_sheet import StyleSheet


class MainWindow(FramelessWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.title = StandardTitleBar(self)
        self.title.titleLabel.setStyleSheet("""
            QLabel{
                background: transparent;
                font: 13px 'Microsoft YaHei';
                padding: 0 4px
            }
        """)
        self.setTitleBar(self.title)

        self.hBoxLayout = QHBoxLayout(self)
        self.navigationInterface = NavigationInterface(
            self, showMenuButton=True, showReturnButton=True)
        self.stackWidget = QStackedWidget(self)

        # create sub interface
        self.home_interface = HomePage(self)
        self.history_interface = HistoryPage(self)
        self.settings_interface = SettingsPage(self)

        self.stackWidget.addWidget(self.home_interface)
        self.stackWidget.addWidget(self.history_interface)
        self.stackWidget.addWidget(self.settings_interface)

        self.initLayout()
        self.initNavigation()
        self.initWindow()

    def initLayout(self):
        self.hBoxLayout.setSpacing(0)
        self.hBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.hBoxLayout.addWidget(self.navigationInterface)
        self.hBoxLayout.addWidget(self.stackWidget)
        self.hBoxLayout.setStretchFactor(self.stackWidget, 1)

        self.titleBar.raise_()
        self.navigationInterface.displayModeChanged.connect(self.titleBar.raise_)

    def initNavigation(self):
        self.navigationInterface.addItem(
            routeKey=self.home_interface.objectName(),
            icon=FluentIcon.HOME,
            text=self.tr("Home Page"),
            onClick=lambda: self.switchTo(self.home_interface)
        )

        self.navigationInterface.addItem(
            routeKey=self.history_interface.objectName(),
            icon=FluentIcon.HISTORY,
            text=self.tr("Warp Record"),
            onClick=lambda: self.switchTo(self.history_interface)
        )

        self.navigationInterface.addItem(
            routeKey=self.settings_interface.objectName(),
            icon=FluentIcon.SETTING,
            text=self.tr("Settings"),
            onClick=lambda: self.switchTo(self.settings_interface),
            position=NavigationItemPosition.BOTTOM
        )

        # self.navigationInterface.setDefaultRouteKey(self.home_interface.objectName())
        qrouter.setDefaultRouteKey(self.stackWidget, self.home_interface.objectName())
        self.navigationInterface.setCurrentItem(self.home_interface.objectName())

        self.stackWidget.currentChanged.connect(self.onCurrentInterfaceChanged)
        self.stackWidget.setCurrentIndex(0)

    def initWindow(self):
        self.readSettings()
        self.setWindowIcon(QIcon('resources/star_rail.ico'))
        self.setWindowTitle(self.tr("StarRail Gacha Exporter v%s") % VERSION)
        self.titleBar.setAttribute(Qt.WA_StyledBackground)

        StyleSheet.MAIN_WINDOW.apply(self)

    def switchTo(self, widget):
        self.stackWidget.setCurrentWidget(widget)

    def onCurrentInterfaceChanged(self, index):
        widget = self.stackWidget.widget(index)
        self.navigationInterface.setCurrentItem(widget.objectName())

    def resizeEvent(self, e):
        self.titleBar.move(46, 0)
        self.titleBar.resize(self.width() - 46, self.titleBar.height())

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        super().closeEvent(event)
        self.saveSettings()

    def readSettings(self):
        settings = QSettings("DancingSnow", "StarRailGachaExporter")
        size = settings.value("size", QVariant(QSize(900, 700)))
        pos = settings.value("pos", QVariant(QPoint(200, 200)))
        self.resize(size)
        self.move(pos)

    def saveSettings(self):
        settings = QSettings("DancingSnow", "StarRailGachaExporter")
        settings.setValue("size", QVariant(self.size()))
        settings.setValue("pos", QVariant(self.pos()))
