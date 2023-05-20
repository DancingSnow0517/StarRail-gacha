import itertools
import logging
import os
import re
import time

from PyQt5.QtCore import Qt, QSize, QThread, pyqtSignal
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QVBoxLayout, QWidget, QHBoxLayout, QSpacerItem, QSizePolicy, QLabel, QFileDialog
from qfluentwidgets import ScrollArea, PushButton, FluentIcon, ComboBox, FlowLayout, StateToolTip, MessageBox, Theme, \
    setThemeColor, setTheme

from ..components.pool_chart import PoolChart
from ...gacha.gacha import Gacha
from ...gacha.gachaManager import GachaManager
from ...gacha.types import GachaType
from ...gacha.url import get_url_template, get_api_url
from ...utils.config import config
from ...utils.files import get_local_api_url, get_doc_path
from ...utils.http import get, check_response
from ...utils.style_sheet import StyleSheet

log = logging.getLogger(__name__)


class UpdateThread(QThread):
    statusLabelSignal = pyqtSignal(str)
    stateTooltipSignal = pyqtSignal(str, str, bool)
    updateButtonSignal = pyqtSignal(bool)
    updateUidBoxSignal = pyqtSignal()
    updateChartSignal = pyqtSignal()

    def __init__(self, parent: 'HomePage' = ...) -> None:
        super().__init__(parent)

    def run(self) -> None:
        self.statusLabelSignal.emit("正在更新数据...")
        log.info("正在更新数据...")
        self.stateTooltipSignal.emit("正在更新数据...", "可能会花上一段时间，请耐心等待", True)
        if config.game_path == "":
            api_url = get_local_api_url()
        else:
            api_url = get_local_api_url(config.game_path)
        if api_url is None:
            self.statusLabelSignal.emit("未找到API地址, 请检查是否开启过星穹铁道的历史记录")
            self.stateTooltipSignal.emit("数据更新失败，未找到API地址！", "", False)
            self.updateButtonSignal.emit(True)
            return
        response, code = get(api_url)
        valid, msg = check_response(response, code)
        if not valid:
            log.error("得到预期之外的回应")
            self.statusLabelSignal.emit(msg)
            self.stateTooltipSignal.emit("数据更新失败！", "", False)
            self.updateButtonSignal.emit(True)
            return

        api_template = get_url_template(api_url)
        uid = response['data']['list'][0]['uid']
        gm = GachaManager.load_from_uid(uid)
        count = 0
        for gacha_type in GachaType:
            if gacha_type == GachaType.ALL:
                continue
            end_id = '0'
            for page in itertools.count(1, 1):
                log.info(f'正在获取 {gacha_type.name} 第 {page} 页')
                self.statusLabelSignal.emit(f"正在获取 {gacha_type.name} 第 {page} 页")
                url = get_api_url(
                    api_template, end_id, str(gacha_type.value),
                    str(page), '5',
                )
                response, code = get(url)
                valid, msg = check_response(response, code)
                if not valid:
                    self.msleep(350)
                    break
                gacha_list = [Gacha(**o) for o in response['data']['list']]
                should_next, add_count = gm.add_records(gacha_list)
                count += add_count
                if not should_next and not config.get_full_data:
                    self.msleep(300)
                    break
                end_id = gacha_list[-1].id
                self.msleep(300)
        log.info("数据更新成功, 共更新了 %d 条数据", count)
        gm.save_to_file()
        self.statusLabelSignal.emit(f"数据更新成功, 共更新了 {count} 条数据")
        self.updateButtonSignal.emit(True)
        self.stateTooltipSignal.emit("数据更新完成！", "", False)
        self.updateUidBoxSignal.emit()
        self.updateChartSignal.emit()


class HomePage(ScrollArea):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("chart_page")

        self.stateTooltip = None

        self.vBoxLayout = QVBoxLayout(self)
        self.update_button = PushButton("更新数据", self, FluentIcon.SYNC)
        self.update_button.clicked.connect(self.__on_update_button_clicked)
        self.export_button = PushButton("导出数据", self, FluentIcon.FOLDER)
        self.export_button.clicked.connect(self.__on_export_button_clicked)

        self.uid_box = ComboBox(self)
        self.uid_box.setMinimumSize(QSize(140, 0))
        self.uid_box.currentTextChanged.connect(self.__on_uid_box_currentTextChanged)

        self.buttonLayout = QHBoxLayout()
        self.buttonLayout.setContentsMargins(8, 8, 8, 8)
        self.buttonLayout.addWidget(self.update_button)
        self.buttonLayout.addWidget(self.export_button)
        self.buttonLayout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.buttonLayout.addWidget(self.uid_box)

        self.vBoxLayout.addLayout(self.buttonLayout)

        self.statusLabel = QLabel(self)
        self.statusLabel.setFont(QFont("Microsoft YaHei", 12))

        self.vBoxLayout.addWidget(self.statusLabel, Qt.AlignLeft)
        self.vBoxLayout.addItem(QSpacerItem(0, 1000, QSizePolicy.Expanding, QSizePolicy.Minimum))

        self.scrollWidget = QWidget()
        self.expandLayout = FlowLayout(self.scrollWidget, needAni=True)

        self.chart1 = PoolChart(GachaType.STELLAR, self.scrollWidget)
        self.chart2 = PoolChart(GachaType.CHARACTER, self.scrollWidget)
        self.chart3 = PoolChart(GachaType.LIGHT_CONE, self.scrollWidget)
        self.chart4 = PoolChart(GachaType.DEPARTURE, self.scrollWidget)
        self.chart4.setVisible(config.show_departure)
        config.showDepartureChanged.connect(self.chart4.setVisible)
        self.chart5 = PoolChart(GachaType.ALL, self.scrollWidget)

        self.expandLayout.setSpacing(28)
        self.expandLayout.setContentsMargins(36, 10, 36, 0)

        self.expandLayout.addWidget(self.chart1)
        self.expandLayout.addWidget(self.chart2)
        self.expandLayout.addWidget(self.chart3)
        self.expandLayout.addWidget(self.chart4)
        self.expandLayout.addWidget(self.chart5)
        self.vBoxLayout.addLayout(self.expandLayout)

        self.vBoxLayout.setContentsMargins(16, 32, 16, 16)

        self.resize(1000, 800)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setViewportMargins(0, 120, 0, 20)
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)

        # initialize style sheet
        self.scrollWidget.setObjectName('scrollWidget')

        self.update_uid_box()

        StyleSheet.HOME_PAGE.apply(self)

        setTheme(Theme.DARK if config.dark_mode else Theme.LIGHT)
        setThemeColor(config.theme_color)

    def set_uid(self, uid: str):
        self.chart1.set_uid(uid)
        self.chart2.set_uid(uid)
        self.chart3.set_uid(uid)
        self.chart4.set_uid(uid)
        self.chart5.set_uid(uid)

    def update_chart(self):
        self.chart1.update_chart()
        self.chart2.update_chart()
        self.chart3.update_chart()
        self.chart4.update_chart()
        self.chart5.update_chart()

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

    def __on_update_button_clicked(self):
        update_thread = UpdateThread(self)
        update_thread.statusLabelSignal.connect(self.__update_data_statusLabel_signalReceive)
        update_thread.stateTooltipSignal.connect(self.__update_data_stateTooltip_signalReceive)
        update_thread.updateButtonSignal.connect(self.__update_data_updateButton_signalReceive)
        update_thread.updateUidBoxSignal.connect(self.update_uid_box)
        update_thread.updateChartSignal.connect(self.update_chart)
        update_thread.start()

    def __on_export_button_clicked(self):
        file_path, file_type = QFileDialog.getSaveFileName(self.window(), "导出数据",
                                                           get_doc_path() + f'\\sr-gacha-data-{time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())}',
                                                           "Excel File (*.xlsx);;JSON File (*.json)")
        if file_path == '' and file_type == '':
            return
        uid = self.uid_box.currentText()
        if uid == '':
            return
        gm = GachaManager.load_from_uid(uid)
        if file_type == 'Excel File (*.xlsx)':
            gm.save_to_excel(file_path)
        elif file_type == 'JSON File (*.json)':
            gm.save_to_file(file_path)
        else:
            m = MessageBox("抽卡数据导出", "不支持的类型", self.window())
            m.exec_()
            return

        m = MessageBox("抽卡数据导出", "导出成功", self.window())
        m.exec_()

    def __update_data_statusLabel_signalReceive(self, text):
        self.statusLabel.setText(text)

    def __update_data_stateTooltip_signalReceive(self, title, content, status):
        if status:
            self.stateTooltip = StateToolTip(title, content, self.window())
            self.stateTooltip.move(self.stateTooltip.getSuitablePos())
            self.stateTooltip.show()
        else:
            self.stateTooltip.setContent(title)
            self.stateTooltip.setState(True)
            self.stateTooltip = None

    def __update_data_updateButton_signalReceive(self, status):
        self.update_button.setEnabled(status)

    def __on_uid_box_currentTextChanged(self):
        self.set_uid(self.uid_box.currentText())
        self.update_chart()
