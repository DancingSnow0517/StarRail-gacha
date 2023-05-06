from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QHBoxLayout, QStackedWidget, QApplication
from qfluentwidgets import NavigationInterface, FluentIcon, NavigationItemPosition
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
            text="主页",
            onClick=lambda: self.switchTo(self.home_interface)
        )

        self.navigationInterface.addItem(
            routeKey=self.history_interface.objectName(),
            icon=FluentIcon.HISTORY,
            text="跃迁记录",
            onClick=lambda: self.switchTo(self.history_interface)
        )

        self.navigationInterface.addItem(
            routeKey=self.settings_interface.objectName(),
            icon=FluentIcon.SETTING,
            text="设置",
            onClick=lambda: self.switchTo(self.settings_interface),
            position=NavigationItemPosition.BOTTOM
        )

        self.navigationInterface.setDefaultRouteKey(self.home_interface.objectName())
        self.navigationInterface.setCurrentItem(self.home_interface.objectName())

        self.stackWidget.currentChanged.connect(self.onCurrentInterfaceChanged)
        self.stackWidget.setCurrentIndex(0)

    def initWindow(self):
        self.resize(900, 700)
        self.setWindowIcon(QIcon('resources/star_rail.ico'))
        self.setWindowTitle(f'崩坏：星穹铁道抽卡导出工具 - v{VERSION}')
        self.titleBar.setAttribute(Qt.WA_StyledBackground)

        desktop = QApplication.desktop().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)

        StyleSheet.MAIN_WINDOW.apply(self)

    def switchTo(self, widget):
        self.stackWidget.setCurrentWidget(widget)

    def onCurrentInterfaceChanged(self, index):
        widget = self.stackWidget.widget(index)
        self.navigationInterface.setCurrentItem(widget.objectName())

    def resizeEvent(self, e):
        self.titleBar.move(46, 0)
        self.titleBar.resize(self.width() - 46, self.titleBar.height())
