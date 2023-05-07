import os
import re

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QFrame, QVBoxLayout, QLabel, QHBoxLayout, QSpacerItem, QSizePolicy, QTableWidgetItem, \
    QAbstractItemView
from qfluentwidgets import ComboBox, PushButton, FluentIcon, TableWidget

from ...gacha.gachaManager import GachaManager
from ...gacha.types import GachaType
from ...utils.style_sheet import StyleSheet


class HistoryPage(QFrame):

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("history_page")

        self.vBoxLayout = QVBoxLayout(self)

        self.historyLabel = QLabel("跃迁记录", self)
        self.historyLabel.setContentsMargins(0, 8, 0, 0)
        self.historyLabel.setFont(QFont("Microsoft YaHei", 24, QFont.Bold))
        self.vBoxLayout.addWidget(self.historyLabel, 1, Qt.AlignTop)

        self.infoLayout = QHBoxLayout()
        self.uid_box = ComboBox(self)
        self.uid_box.setMinimumSize(QSize(140, 0))
        self.uid_box.currentTextChanged.connect(self.fill_table)

        self.pool_box = ComboBox(self)
        self.pool_box.setMinimumSize(QSize(140, 0))
        self.pool_box.addItems(['群星跃迁', '角色活动跃迁', '光锥活动跃迁', '始发跃迁'])
        self.pool_box.setCurrentIndex(0)
        self.pool_box.currentTextChanged.connect(self.fill_table)

        self.refresh_button = PushButton("刷新页面", self, FluentIcon.SYNC)
        self.refresh_button.clicked.connect(self.refresh)

        self.infoLayout.addWidget(self.uid_box)
        self.infoLayout.addWidget(self.pool_box)
        self.infoLayout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.infoLayout.addWidget(self.refresh_button)
        self.vBoxLayout.addLayout(self.infoLayout, Qt.AlignTop)

        self.tableFrame = TableFrame(self)
        self.vBoxLayout.addWidget(self.tableFrame, 1, Qt.AlignTop)

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
        uid = self.uid_box.currentText()  # type: str
        pool_type = self.pool_box.currentText()  # type: str

        if uid == '':
            return

        if pool_type == '群星跃迁':
            pool = GachaType.STELLAR
        elif pool_type == '角色活动跃迁':
            pool = GachaType.CHARACTER
        elif pool_type == '光锥活动跃迁':
            pool = GachaType.LIGHT_CONE
        elif pool_type == '始发跃迁':
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
            self.tableFrame.table.setItem(i, 2, QTableWidgetItem(gacha.item_type.value))
            self.tableFrame.table.setItem(i, 3, QTableWidgetItem(gacha.rank_type))
            self.tableFrame.table.setItem(i, 4, QTableWidgetItem(str(i + 1)))
            self.tableFrame.table.setItem(i, 5, QTableWidgetItem(str(cost)))
            if gacha.is_5star:
                cost = 0

        self.tableFrame.table.resizeRowsToContents()

    def refresh(self):
        self.update_uid_box()
        self.fill_table()


class TableFrame(QFrame):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.hBoxLayout = QHBoxLayout(self)
        self.hBoxLayout.setContentsMargins(0, 8, 0, 0)

        # 表格部分
        self.table = TableWidget(self)
        self.table.verticalHeader().hide()
        self.table.setColumnCount(6)
        self.table.setRowCount(0)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.table.setHorizontalHeaderLabels(['时间', '名称', '类别', '星级', '总跃迁次数', '保底内'])

        self.table.setColumnWidth(0, 250)
        self.table.setColumnWidth(1, 140)
        self.table.setColumnWidth(2, 80)
        self.table.setColumnWidth(3, 50)
        self.table.setColumnWidth(4, 100)
        self.table.setColumnWidth(5, 80)

        self.table.setMinimumHeight(650)

        self.hBoxLayout.addWidget(self.table)
