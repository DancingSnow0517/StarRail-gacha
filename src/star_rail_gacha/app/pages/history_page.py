import os
import re

from PyQt5.QtCore import Qt, QSize, QModelIndex
from PyQt5.QtGui import QFont, QPalette, QColor
from PyQt5.QtWidgets import QFrame, QVBoxLayout, QLabel, QHBoxLayout, QSpacerItem, QSizePolicy, QTableWidgetItem, \
    QAbstractItemView, QStyleOptionViewItem, QHeaderView
from qfluentwidgets import ComboBox, PushButton, FluentIcon, TableWidget, TableItemDelegate

from ...gacha.gacha_manager import GachaManager
from ...gacha.types import GachaType, ItemType
from ...utils.style_sheet import StyleSheet

ITEM_COLOR_MAPPING = {"4": "#A256E1", "5": "#BD6932", "X": "#FF0000"}
rowColorMapping = {}


class HistoryPage(QFrame):

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("history_page")

        self.vBoxLayout = QVBoxLayout(self)

        self.historyLabel = QLabel(self.tr("Warp record"), self)
        self.historyLabel.setContentsMargins(0, 8, 0, 0)
        self.historyLabel.setFont(QFont("Microsoft YaHei", 24, QFont.Bold))
        self.vBoxLayout.addWidget(self.historyLabel)

        self.infoLayout = QHBoxLayout()
        self.uid_box = ComboBox(self)
        self.uid_box.setMinimumSize(QSize(140, 0))
        self.uid_box.currentTextChanged.connect(self.fill_table)

        self.pool_box = ComboBox(self)
        self.pool_box.setMinimumSize(QSize(140, 0))
        self.pool_box.addItems([
            self.tr("Stellar Warp"),
            self.tr("Character Event Warp"),
            self.tr("Light Cone Event Warp"),
            self.tr("Departure Warp")
        ])
        self.pool_box.setCurrentIndex(0)
        self.pool_box.currentTextChanged.connect(self.fill_table)

        self.refresh_button = PushButton(self.tr("Refresh Page"), self, FluentIcon.SYNC)
        self.refresh_button.clicked.connect(self.refresh)

        self.infoLayout.addWidget(self.uid_box)
        self.infoLayout.addWidget(self.pool_box)
        self.infoLayout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.infoLayout.addWidget(self.refresh_button)
        self.vBoxLayout.addLayout(self.infoLayout, Qt.AlignTop)

        self.tableFrame = TableFrame(self)
        self.vBoxLayout.addWidget(self.tableFrame)

        self.vBoxLayout.setContentsMargins(16, 32, 16, 16)

        self.update_uid_box()
        self.uid_box.setCurrentIndex(0)
        self.fill_table()

        StyleSheet.HISTORY_PAGE.apply(self)

    def update_uid_box(self):
        if not os.path.exists('userData'):
            os.mkdir('userData')
            return

        uids = [self.uid_box.itemText(i) for i in range(self.uid_box.count())]
        for file in os.listdir('userData'):
            match = re.match(r'^gacha-list-(\d{9})\.json$', file)
            if match:
                uid = match.group(1)
                if uid not in uids:
                    self.uid_box.addItem(uid)
        if self.uid_box.currentText() == '' and self.uid_box.count() > 0:
            self.uid_box.setCurrentIndex(0)
            self.uid_box.currentTextChanged.emit(self.uid_box.currentText())

    def fill_table(self):
        global rowColorMapping
        rowColorMapping = {}
        uid = self.uid_box.currentText()  # type: str
        pool_type = self.pool_box.currentText()  # type: str

        if uid == '':
            return

        if pool_type == self.tr("Stellar Warp"):
            pool = GachaType.STELLAR
        elif pool_type == self.tr("Character Event Warp"):
            pool = GachaType.CHARACTER
        elif pool_type == self.tr("Light Cone Event Warp"):
            pool = GachaType.LIGHT_CONE
        elif pool_type == self.tr("Departure Warp"):
            pool = GachaType.DEPARTURE
        else:
            return

        gm = GachaManager.load_from_uid(uid)
        self.tableFrame.table.setRowCount(gm.get_count(pool))
        cost = 0
        for i, gacha in enumerate(reversed(gm.get_gacha_list(pool))):
            cost += 1
            self.tableFrame.table.setItem(i, 0, QTableWidgetItem(gacha.time))
            self.tableFrame.table.setItem(i, 1, QTableWidgetItem(gacha.name))
            self.tableFrame.table.setItem(i, 2, QTableWidgetItem(
                self.tr("Character") if gacha.item_type == ItemType.CHARACTER else self.tr("Light Cone")))
            self.tableFrame.table.setItem(i, 3, QTableWidgetItem(gacha.rank_type))
            self.tableFrame.table.setItem(i, 4, QTableWidgetItem(str(i + 1)))
            self.tableFrame.table.setItem(i, 5, QTableWidgetItem(str(cost)))
            if gacha.is_5star:
                rowColorMapping.update({i: QColor(ITEM_COLOR_MAPPING["5"])})
                cost = 0
            elif gacha.is_4star:
                rowColorMapping.update({i: QColor(ITEM_COLOR_MAPPING["4"])})
        self.tableFrame.table.setItemDelegate(CustomTableItemDelegate(self.tableFrame.table))
        self.tableFrame.table.resizeRowsToContents()

    def refresh(self):
        self.update_uid_box()
        self.fill_table()


class CustomTableItemDelegate(TableItemDelegate):
    """ Custom table item delegate """

    def initStyleOption(self, option: QStyleOptionViewItem, index: QModelIndex):
        super().initStyleOption(option, index)
        if index.row() in rowColorMapping:
            option.palette.setColor(QPalette.Text, rowColorMapping[index.row()])
            option.palette.setColor(QPalette.HighlightedText, rowColorMapping[index.row()])


class TableFrame(QFrame):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setContentsMargins(0, 8, 0, 0)

        # 表格部分
        self.table = TableWidget(self)
        self.table.verticalHeader().hide()
        self.table.setColumnCount(6)
        self.table.setRowCount(0)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.table.setHorizontalHeaderLabels([
            self.tr("Warp Time"),
            self.tr("Warp Name"),
            self.tr("Entity Type"),
            self.tr("Entity Rank"),
            self.tr("Total number of Warp"),
            self.tr("In guarantees")
        ])

        self.table.setColumnWidth(0, 250)
        self.table.setColumnWidth(1, 140)
        self.table.setColumnWidth(2, 100)
        self.table.setColumnWidth(3, 100)
        self.table.setColumnWidth(4, 150)
        self.table.setColumnWidth(5, 150)

        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)

        self.vBoxLayout.addWidget(self.table, Qt.AlignLeft)
