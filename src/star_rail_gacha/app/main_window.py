from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtWidgets import QHBoxLayout, QStackedWidget, QApplication, QVBoxLayout, QLabel
from qfluentwidgets import NavigationInterface, FluentIcon, NavigationItemPosition
from qframelesswindow import FramelessWindow, StandardTitleBar, TitleBar

from .pages.home_page import HomePage
from .pages.settings_page import SettingsPage
from ..constant import VERSION


class CustomTitleBar(TitleBar):
    """ Title bar with icon and title """

    def __init__(self, parent):
        super().__init__(parent)
        self.setFixedHeight(48)
        self.hBoxLayout.removeWidget(self.minBtn)
        self.hBoxLayout.removeWidget(self.maxBtn)
        self.hBoxLayout.removeWidget(self.closeBtn)

        # add window icon
        self.iconLabel = QLabel(self)
        self.iconLabel.setFixedSize(18, 18)
        self.hBoxLayout.insertSpacing(0, 10)
        self.hBoxLayout.insertWidget(1, self.iconLabel, 0, Qt.AlignLeft | Qt.AlignVCenter)
        self.window().windowIconChanged.connect(self.setIcon)

        # add title label
        self.titleLabel = QLabel(self)
        self.titleLabel.setFont(QFont('Microsoft YaHei', 10))
        self.titleLabel.setContentsMargins(4, 0, 0, 0)
        self.hBoxLayout.insertWidget(2, self.titleLabel, 0, Qt.AlignLeft | Qt.AlignVCenter)
        self.titleLabel.setObjectName('titleLabel')
        self.window().windowTitleChanged.connect(self.setTitle)

        self.vBoxLayout = QVBoxLayout()
        self.buttonLayout = QHBoxLayout()
        self.buttonLayout.setSpacing(0)
        self.buttonLayout.setContentsMargins(0, 0, 0, 0)
        self.buttonLayout.setAlignment(Qt.AlignTop)
        self.buttonLayout.addWidget(self.minBtn)
        self.buttonLayout.addWidget(self.maxBtn)
        self.buttonLayout.addWidget(self.closeBtn)
        self.vBoxLayout.addLayout(self.buttonLayout)
        self.vBoxLayout.addStretch(1)
        self.hBoxLayout.addLayout(self.vBoxLayout, 0)

    def setTitle(self, title):
        self.titleLabel.setText(title)
        self.titleLabel.adjustSize()

    def setIcon(self, icon):
        self.iconLabel.setPixmap(QIcon(icon).pixmap(18, 18))


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
        self.settings_interface = SettingsPage(self)

        self.stackWidget.addWidget(self.home_interface)
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

        # self.setQss()

    def switchTo(self, widget):
        self.stackWidget.setCurrentWidget(widget)

    def onCurrentInterfaceChanged(self, index):
        widget = self.stackWidget.widget(index)
        self.navigationInterface.setCurrentItem(widget.objectName())

    def resizeEvent(self, e):
        self.titleBar.move(46, 0)
        self.titleBar.resize(self.width() - 46, self.titleBar.height())
