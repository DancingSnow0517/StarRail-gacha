import itertools
import logging
import os
import re
import time
from urllib.parse import urlparse

from PyQt5.QtCore import Qt, QSize, QThread, pyqtSignal
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QVBoxLayout, QWidget, QHBoxLayout, QSpacerItem, QSizePolicy, QLabel, QFileDialog
from qfluentwidgets import ScrollArea, PushButton, FluentIcon, ComboBox, FlowLayout, StateToolTip, MessageBox, Theme, \
    setThemeColor, setTheme, InfoBar, InfoBarPosition

from ..components.pool_chart import PoolChart
from ..components.url_input_dialog import URLInputDialog
from ...gacha.gacha import Gacha
from ...gacha.gacha_manager import GachaManager
from ...gacha.types import GachaType
from ...gacha.url import get_url_template, get_api_url
from ...utils.alias import alias_utils
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

    def __init__(self, parent: 'HomePage' = None, api_url: str = None) -> None:
        super().__init__(parent)
        self.api_url = api_url

    def run(self) -> None:
        self.statusLabelSignal.emit(self.tr("Updating data..."))
        log.info("正在更新数据...")
        self.stateTooltipSignal.emit(self.tr("Updating data..."),
                                     self.tr("It may take some time, please be patient and wait"), True)
        if self.api_url is None:
            if config.game_path == "":
                api_url = get_local_api_url()
            else:
                api_url = get_local_api_url(config.game_path)
        else:
            api_url = self.api_url
        if api_url is None:
            self.statusLabelSignal.emit(
                self.tr("API address not found, please check if the gacha history of StarRail has been opened"))
            self.stateTooltipSignal.emit(self.tr("Data update failed, API address not found!"), "", False)
            self.updateButtonSignal.emit(True)
            return
        response, code = get(api_url)
        valid, msg = check_response(response, code)
        if not valid:
            log.error("得到预期之外的回应")
            self.statusLabelSignal.emit(msg)
            self.stateTooltipSignal.emit(self.tr("Data update failed!"), "", False)
            self.updateButtonSignal.emit(True)
            return

        api_template = get_url_template(api_url)
        uid = response['data']['list'][0]['uid']
        lang = response['data']['list'][0]['lang']
        region_time_zone = response['data']['region_time_zone']

        gm = GachaManager.load_from_uid(uid)
        gm.set_lang(lang)
        gm.set_region_time_zone(region_time_zone)

        count = 0
        for gacha_type in GachaType:
            if gacha_type == GachaType.ALL:
                continue
            end_id = '0'
            for page in itertools.count(1, 1):
                log.info(f'正在获取 {gacha_type.name} 第 {page} 页')
                self.statusLabelSignal.emit(
                    self.tr("Getting %s page %d") % (alias_utils.get_gacha_name_by_type(gacha_type), page)
                )
                url = get_api_url(
                    api_template, end_id, str(gacha_type.value),
                    str(page), '5',
                )
                response, code = get(url)
                valid, msg = check_response(response, code)
                if not valid:
                    self.msleep(350)
                    break
                gacha_list = [Gacha(region_time_zone=region_time_zone, **o) for o in response['data']['list']]
                should_next, add_count = gm.add_records(gacha_list)
                count += add_count
                if not should_next and not config.get_full_data:
                    self.msleep(300)
                    break
                end_id = gacha_list[-1].id
                self.msleep(300)
        log.info("数据更新成功, 共更新了 %d 条数据", count)
        gm.save_to_file()
        self.statusLabelSignal.emit(self.tr("Data update successful, a total of %d data were updated") % count)
        self.updateButtonSignal.emit(True)
        self.stateTooltipSignal.emit(self.tr("Data update completed!"), "", False)
        self.updateUidBoxSignal.emit()
        self.updateChartSignal.emit()


class HomePage(ScrollArea):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("chart_page")

        self.stateTooltip = None

        self.vBoxLayout = QVBoxLayout(self)
        self.update_button = PushButton(self.tr("Update data"), self, FluentIcon.SYNC)
        self.update_button.clicked.connect(self.__on_update_button_clicked)
        self.export_button = PushButton(self.tr("Export Data"), self, FluentIcon.FOLDER)
        self.export_button.clicked.connect(self.__on_export_button_clicked)
        self.manual_button = PushButton(self.tr("Manual import"), self, FluentIcon.COPY)
        self.manual_button.clicked.connect(self.__on_manual_button_clicked)

        self.uid_box = ComboBox(self)
        self.uid_box.setMinimumSize(QSize(140, 0))
        self.uid_box.currentTextChanged.connect(self.__on_uid_box_currentTextChanged)

        self.buttonLayout = QHBoxLayout()
        self.buttonLayout.setContentsMargins(8, 8, 8, 8)
        self.buttonLayout.addWidget(self.update_button)
        self.buttonLayout.addWidget(self.export_button)
        self.buttonLayout.addWidget(self.manual_button)
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
        self.update_button.setEnabled(False)
        update_thread = UpdateThread(self)
        update_thread.statusLabelSignal.connect(self.__update_data_statusLabel_signalReceive)
        update_thread.stateTooltipSignal.connect(self.__update_data_stateTooltip_signalReceive)
        update_thread.updateButtonSignal.connect(self.__update_data_updateButton_signalReceive)
        update_thread.updateUidBoxSignal.connect(self.update_uid_box)
        update_thread.updateChartSignal.connect(self.update_chart)
        update_thread.start()

    def __on_export_button_clicked(self):
        file_path, file_type = QFileDialog.getSaveFileName(self.window(), self.tr("Export Data"),
                                                           get_doc_path() + f'\\sr-gacha-data-{time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())}',
                                                           "Excel File (*.xlsx);;JSON File (*.json);;SRGF JSON File (*.json)")
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
        elif file_type == 'SRGF JSON File (*.json)':
            gm.save_srgf_to_file(file_path)
        else:
            m = MessageBox(self.tr("Gacha data export"), self.tr("Unsupported type"), self.window())
            m.exec_()
            return

        m = MessageBox(self.tr("Gacha data export"), self.tr("Export successful"), self.window())
        m.exec_()

    def __on_manual_button_clicked(self):
        dialog = URLInputDialog(self.window())
        if dialog.exec_():
            api_url = dialog.urlLineEdit.text()

            p = urlparse(api_url)
            if p.scheme == '' or p.netloc == '':
                InfoBar.error(self.tr("URL error"), self.tr("Incorrect URL format"), duration=3000, position=InfoBarPosition.TOP,
                              parent=self.window())
                return

            update_thread = UpdateThread(self, api_url=api_url)
            update_thread.statusLabelSignal.connect(self.__update_data_statusLabel_signalReceive)
            update_thread.stateTooltipSignal.connect(self.__update_data_stateTooltip_signalReceive)
            update_thread.updateButtonSignal.connect(self.__update_data_updateButton_signalReceive)
            update_thread.updateUidBoxSignal.connect(self.update_uid_box)
            update_thread.updateChartSignal.connect(self.update_chart)
            update_thread.start()

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
