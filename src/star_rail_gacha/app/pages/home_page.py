import itertools
import logging
import os
import re
import time

from PyQt5.QtChart import QPieSeries, QChart, QChartView, QPieSlice
from PyQt5.QtCore import QSize, Qt, QThread, pyqtSignal
from PyQt5.QtGui import QPainter, QColor, QFont
from PyQt5.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout, QSpacerItem, QSizePolicy, QLabel, QFileDialog
from qfluentwidgets import PushButton, FluentIcon, ComboBox, ToggleButton, MessageBox, Theme, StateToolTip, qconfig, \
    setTheme, setThemeColor

from ...gacha.gacha import Gacha
from ...gacha.gachaManager import GachaManager
from ...gacha.http import fetch
from ...gacha.types import GachaType
from ...gacha.url import get_url_template, get_api_url
from ...utils.QtStringUtil import coloredText
from ...utils.colormap import now_color, next_color, reset_index
from ...utils.config import config
from ...utils.files import get_local_api_url, get_doc_path
from ...utils.style_sheet import StyleSheet

log = logging.getLogger(__name__)


class UpdateThread(QThread):

    def __init__(self, parent: 'HomePage' = ...) -> None:
        super().__init__(parent)

    def run(self) -> None:
        self.parent().statusLabel.setText("正在更新数据...")
        log.info("正在更新数据...")
        self.parent().stateTooltipSignal.emit("正在更新数据...", "可能会花上一段时间，请耐心等待", True)
        api_url = get_local_api_url()
        if api_url is None:
            self.parent().statusLabel.setText("未找到API地址", "请检查是否开启过星穹铁道的历史记录")
            self.parent().stateTooltipSignal.emit("数据更新失败，未找到API地址！", "", False)
            return
        response, code = fetch(api_url)
        valid = self.parent().check_response(response, code)
        if not valid:
            log.error("得到预期之外的回应")
            self.parent().stateTooltipSignal.emit("数据更新失败！", "", False)
            return

        api_template = get_url_template(api_url)
        uid = response['data']['list'][0]['uid']
        gm = GachaManager.load_from_uid(uid)
        if config.get_full_data:
            gm.clear()
        count = 0
        for gacha_type in GachaType:
            if gacha_type == GachaType.ALL:
                continue
            end_id = '0'
            for page in itertools.count(1, 1):
                log.info(f'正在获取 {gacha_type.name} 第 {page} 页')
                self.parent().statusLabel.setText(f"正在获取 {gacha_type.name} 第 {page} 页")
                url = get_api_url(
                    api_template, end_id, str(gacha_type.value),
                    str(page), '5',
                )
                response, code = fetch(url)
                if not self.parent().check_response(response, code):
                    time.sleep(0.3)
                    break
                gacha_list = [Gacha(**o) for o in response['data']['list']]
                should_next, add_count = gm.add_records(gacha_list)
                count += add_count
                if not should_next:
                    time.sleep(0.3)
                    break
                end_id = gacha_list[-1].id
                time.sleep(0.3)
        log.info("数据更新成功, 共更新了 %d 条数据", count)
        gm.save_to_file()
        self.parent().statusLabel.setText(f"数据更新成功, 共更新了 {count} 条数据")
        self.parent().update_button.setEnabled(True)
        self.parent().update_uid_box()
        self.parent().stateTooltipSignal.emit("数据更新完成！", "", False)


class HomePage(QFrame):
    stateTooltipSignal = pyqtSignal(str, str, bool)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("home_page")

        self.stateTooltip = None
        self.stateTooltipSignal.connect(self.onStateTooltip)

        self.update_button = PushButton("更新数据", self, FluentIcon.SYNC)
        self.update_button.clicked.connect(self.update_data)

        self.export_button = PushButton("导出数据", self, FluentIcon.FOLDER)
        self.export_button.clicked.connect(self.export_data)

        self.uid_box = ComboBox(self)
        self.uid_box.setMinimumSize(QSize(140, 0))
        self.uid_box.currentTextChanged.connect(self.update_chart)

        self.pool_box = ComboBox(self)
        self.pool_box.setMinimumSize(QSize(140, 0))
        self.pool_box.addItems(['群星跃迁', '角色活动跃迁', '光锥活动跃迁', '始发跃迁', '跃迁总览'])
        self.pool_box.setCurrentIndex(0)
        self.pool_box.currentTextChanged.connect(self.update_chart)

        self.vBoxLayout = QVBoxLayout(self)

        # 数据按钮等布局
        self.buttonLayout = QHBoxLayout()
        self.buttonLayout.setContentsMargins(8, 8, 8, 8)
        self.buttonLayout.addWidget(self.update_button)
        self.buttonLayout.addWidget(self.export_button)
        self.buttonLayout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.buttonLayout.addWidget(self.uid_box)
        self.buttonLayout.addWidget(self.pool_box)

        self.vBoxLayout.addLayout(self.buttonLayout)

        self.statusLabel = QLabel(self)
        self.statusLabel.setFont(QFont("Microsoft YaHei", 12))
        self.statusLabel.setContentsMargins(10, 0, 0, 0)
        self.vBoxLayout.addWidget(self.statusLabel, alignment=Qt.AlignLeft)

        # 饼图数据布局
        self.dataLayout = QHBoxLayout()

        # 抽卡池子布局
        self.poolLayout = QVBoxLayout()
        self.poolSeries = QPieSeries()
        self.poolSeries.append("五星角色", 0)
        self.poolSeries.append("五星光锥", 0)
        self.poolSeries.append("四星角色", 0)
        self.poolSeries.append("四星光锥", 0)
        self.poolSeries.append("三星光锥", 0)
        self.poolSeries.hovered.connect(self.on_hovered)

        # add slice
        self.poolSlice1 = QPieSlice()
        self.poolSlice1 = self.poolSeries.slices()[0]
        self.poolSlice1.setBrush(QColor(248, 220, 109))
        self.poolSlice1.setLabelFont(QFont("Microsoft YaHei", 10))

        self.poolSlice2 = QPieSlice()
        self.poolSlice2 = self.poolSeries.slices()[1]
        self.poolSlice2.setBrush(QColor(219, 111, 103))
        self.poolSlice2.setLabelFont(QFont("Microsoft YaHei", 10))

        self.poolSlice3 = QPieSlice()
        self.poolSlice3 = self.poolSeries.slices()[2]
        self.poolSlice3.setBrush(QColor(91, 113, 194))
        self.poolSlice3.setLabelFont(QFont("Microsoft YaHei", 10))

        self.poolSlice4 = QPieSlice()
        self.poolSlice4 = self.poolSeries.slices()[3]
        self.poolSlice4.setBrush(QColor(159, 201, 124))
        self.poolSlice4.setLabelFont(QFont("Microsoft YaHei", 10))

        self.poolSlice5 = QPieSlice()
        self.poolSlice5 = self.poolSeries.slices()[4]
        self.poolSlice5.setBrush(QColor(136, 192, 223))
        self.poolSlice5.setLabelFont(QFont("Microsoft YaHei", 10))

        self.poolChart = QChart()
        self.poolChart.legend().hide()
        self.poolChart.addSeries(self.poolSeries)
        self.poolChart.createDefaultAxes()
        self.poolChart.setAnimationOptions(QChart.SeriesAnimations)
        self.poolChart.legend().setVisible(True)
        self.poolChart.legend().setAlignment(Qt.AlignBottom)
        self.poolChart.setTitle("群星跃迁")
        self.poolChart.setTitleFont(QFont("Microsoft YaHei", 16, QFont.Bold))
        self.poolChart.setFont(QFont("Microsoft YaHei", 10))

        self.poolChartView = QChartView(self.poolChart)
        self.poolChartView.setRenderHint(QPainter.Antialiasing)
        self.poolLayout.addWidget(self.poolChartView)

        self.dataButtonLayout = QHBoxLayout()
        self.dataButtonLayout.setContentsMargins(8, 0, 8, 0)

        self.character5StarButton = ToggleButton("5星角色", self)
        self.character5StarButton.setMinimumSize(QSize(80, 0))
        self.character5StarButton.setChecked(True)
        self.character5StarButton.clicked.connect(self.update_chart)
        # self.character5StarButton.setStyleSheet("background-color: #F1C964")

        self.character4StarButton = ToggleButton("4星角色", self)
        self.character4StarButton.setMinimumSize(QSize(80, 0))
        self.character4StarButton.setChecked(True)
        self.character4StarButton.clicked.connect(self.update_chart)
        # self.character4StarButton.setStyleSheet("background-color: #5B71C2")

        self.lightCone5StarButton = ToggleButton("5星光锥", self)
        self.lightCone5StarButton.setMinimumSize(QSize(80, 0))
        self.lightCone5StarButton.setChecked(True)
        self.lightCone5StarButton.clicked.connect(self.update_chart)
        # self.lightCone5StarButton.setStyleSheet("background-color: #DB6F67")

        self.lightCone4StarButton = ToggleButton("4星光锥", self)
        self.lightCone4StarButton.setMinimumSize(QSize(80, 0))
        self.lightCone4StarButton.setChecked(True)
        self.lightCone4StarButton.clicked.connect(self.update_chart)
        # self.lightCone4StarButton.setStyleSheet("background-color: #9FC97C")

        self.lightCone3StarButton = ToggleButton("3星光锥", self)
        self.lightCone3StarButton.setMinimumSize(QSize(80, 0))
        self.lightCone3StarButton.clicked.connect(self.update_chart)
        # self.lightCone3StarButton.setStyleSheet("background-color: #88C0DF")

        self.dataButtonLayout.addWidget(self.character5StarButton)
        self.dataButtonLayout.addWidget(self.character4StarButton)
        self.dataButtonLayout.addWidget(self.lightCone5StarButton)
        self.dataButtonLayout.addWidget(self.lightCone4StarButton)
        self.dataButtonLayout.addWidget(self.lightCone3StarButton)

        self.poolLayout.addLayout(self.dataButtonLayout)

        self.poolTextLayout = QVBoxLayout()
        self.poolTextLayout.setContentsMargins(8, 16, 8, 24)

        # f"一共 {coloredText('124', '#00BFFF')} 抽 已累计 {coloredText('36', '#32CD32')} 未出5星"
        self.poolLabelTotal = QLabel()
        self.poolLabelTotal.setFont(QFont("Microsoft YaHei", 10))

        # coloredText('5星: 3'.ljust(10, '-') + '[2.41%]', '#DAA520')
        self.poolLabel5Star = QLabel()
        self.poolLabel5Star.setFont(QFont("Microsoft YaHei", 10))

        # coloredText('4星: 21'.ljust(10, '-') + '[16.93%]', '#BA55D3')
        self.poolLabel4Star = QLabel()
        self.poolLabel4Star.setFont(QFont("Microsoft YaHei", 10))

        # coloredText('3星: 90'.ljust(10, '-') + '[72.58%]', '#1E90FF')
        self.poolLabel3Star = QLabel()
        self.poolLabel3Star.setFont(QFont("Microsoft YaHei", 10))

        self.poolLabel5StarHistory = QLabel()
        self.poolLabel5StarHistory.setFont(QFont("Microsoft YaHei", 10))
        self.poolLabel5StarHistory.setWordWrap(True)

        # '5星平均出货次数: ' + coloredText('36.00', '#6FB172')
        self.poolLabel5StarAverage = QLabel()
        self.poolLabel5StarAverage.setFont(QFont("Microsoft YaHei", 10))

        self.poolTextLayout.addWidget(self.poolLabelTotal)
        self.poolTextLayout.addWidget(self.poolLabel5Star)
        self.poolTextLayout.addWidget(self.poolLabel4Star)
        self.poolTextLayout.addWidget(self.poolLabel3Star)
        self.poolTextLayout.addWidget(self.poolLabel5StarHistory)
        self.poolTextLayout.addWidget(self.poolLabel5StarAverage)

        self.poolLayout.addLayout(self.poolTextLayout)
        self.dataLayout.addLayout(self.poolLayout)
        self.vBoxLayout.addLayout(self.dataLayout)

        # # leave some space for title bar
        self.vBoxLayout.setContentsMargins(0, 32, 0, 0)

        self.update_uid_box()
        self.update_chart()

        qconfig.themeChanged.connect(self.set_theme)
        StyleSheet.HOME_PAGE.apply(self)

        setTheme(Theme.DARK if config.dark_mode else Theme.LIGHT)
        setThemeColor(config.theme_color)

    def check_response(self, payload, code):
        if payload is None or not 200 <= code < 300:
            self.statusLabel.setText(f"HTTP 错误: 得到了预期之外的状态码: {code}")
            log.warning(f'回应是否为空: {payload is None}')
            log.warning(f'状态码: {code}')
            return False
        if 'data' not in payload:
            self.statusLabel.setText(
                "HTTP 错误: 得到了错误的http回应" + '' if 'message' not in payload else f": {payload['message']}")
            log.warning(f'回应是否包含 `data`: {"data" in payload}')
            log.warning(
                f'回应 `data` 是否包含 `list`: {"list" in payload["data"]}',
            )
            return False
        if 'list' not in payload['data']:
            self.statusLabel.setText(
                "HTTP 错误: 得到了错误的http回应" + '' if 'message' not in payload else f": {payload['message']}")
            return False
        if not payload['data']['list']:
            log.warning(
                f'回应的数据列表长度: {len(payload["data"]["list"])}',
            )
            return False
        return True

    def update_data(self):
        self.update_button.setEnabled(False)
        update_thread = UpdateThread(self)
        update_thread.start()

    def update_chart(self):
        reset_index()
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
        elif pool_type == '跃迁总览':
            pool = GachaType.ALL
        else:
            return

        gm = GachaManager.load_from_uid(uid)
        self.poolChart.setTitle(pool_type)
        self.poolSlice1.setValue(gm.get_5star_character_count(pool) if self.character5StarButton.isChecked() else 0)
        self.poolSlice2.setValue(gm.get_5star_light_cone_count(pool) if self.lightCone5StarButton.isChecked() else 0)
        self.poolSlice3.setValue(gm.get_4star_character_count(pool) if self.character4StarButton.isChecked() else 0)
        self.poolSlice4.setValue(gm.get_4star_light_cone_count(pool) if self.lightCone4StarButton.isChecked() else 0)
        self.poolSlice5.setValue(gm.get_3star_count(pool) if self.lightCone3StarButton.isChecked() else 0)

        self.poolSlice1.setLabel(
            f"5星角色: {gm.get_5star_character_count(pool)}" if self.character5StarButton.isChecked() else "")
        self.poolSlice2.setLabel(
            f"5星光锥: {gm.get_5star_light_cone_count(pool)}" if self.lightCone5StarButton.isChecked() else "")
        self.poolSlice3.setLabel(
            f"4星角色: {gm.get_4star_character_count(pool)}" if self.character4StarButton.isChecked() else "")
        self.poolSlice4.setLabel(
            f"4星光锥: {gm.get_4star_light_cone_count(pool)}" if self.lightCone4StarButton.isChecked() else "")
        self.poolSlice5.setLabel(
            f"3星光锥: {gm.get_3star_count(pool)}" if self.lightCone3StarButton.isChecked() else "")
        count_text = gm.get_last_5star_count(pool) if \
            pool != GachaType.ALL else f"{gm.get_last_5star_count(GachaType.STELLAR)} + " \
                                       f"{gm.get_last_5star_count(GachaType.CHARACTER)} + " \
                                       f"{gm.get_last_5star_count(GachaType.LIGHT_CONE)} + " \
                                       f"{gm.get_last_5star_count(GachaType.DEPARTURE)}" \
                                       f" ({gm.get_last_5star_count(GachaType.STELLAR) + gm.get_last_5star_count(GachaType.CHARACTER) + gm.get_last_5star_count(GachaType.LIGHT_CONE) + gm.get_last_5star_count(GachaType.DEPARTURE)})"
        self.poolLabelTotal.setText(
            f"一共 {coloredText(gm.get_count(pool), '#00BFFF')} 抽 "
            f"已累计 {coloredText(count_text, '#32CD32')} 未出5星")
        self.poolLabel5Star.setText(coloredText(f'5星: {gm.get_5star_count(pool)}'.ljust(10, '-') +
                                                (f'{(gm.get_5star_count(pool) / gm.get_count(pool) * 100):.2f}%'
                                                 if gm.get_5star_count(pool) != 0 else "0%"), '#DAA520'))
        self.poolLabel4Star.setText(coloredText(f'4星: {gm.get_4star_count(pool)}'.ljust(10, '-') +
                                                (f'{(gm.get_4star_count(pool) / gm.get_count(pool) * 100):.2f}%'
                                                 if gm.get_4star_count(pool) != 0 else "0%"), '#BA55D3'))
        self.poolLabel3Star.setText(coloredText(f'3星: {gm.get_3star_count(pool)}'.ljust(10, '-') +
                                                (f'{(gm.get_3star_count(pool) / gm.get_count(pool) * 100):.2f}%'
                                                 if gm.get_3star_count(pool) != 0 else "0%"), '#00BFFF'))

        if pool == GachaType.ALL:
            history_text = ''
        else:
            history_text = '5星历史记录: '
            his = gm.get_5star_history(pool)
            for i, history in enumerate(his):
                if i > 0:
                    if his[i - 1][0] == history[0]:
                        history_text += coloredText(f'{history[0]}[{history[1]}]', now_color()) + ' '
                    else:
                        history_text += coloredText(f'{history[0]}[{history[1]}]', next_color()) + ' '
                else:
                    history_text += coloredText(f'{history[0]}[{history[1]}]', now_color()) + ' '

        self.poolLabel5StarHistory.setText(history_text)

        self.poolLabel5StarAverage.setText(
            '5星平均出货次数为: ' + coloredText(f'{gm.get_5star_average(pool):.2f}', '#6FB172'))

    def export_data(self):
        file_path, file_type = QFileDialog.getSaveFileName(self.window(), "导出数据", get_doc_path() +
                                                           f'\\sr-gacha-data-{time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())}',
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

    @staticmethod
    def on_hovered(pieSlice: QPieSlice, state: bool):
        if state:
            pieSlice.setExploded(True)
            pieSlice.setLabelVisible(True)
        else:
            pieSlice.setExploded(False)
            pieSlice.setLabelVisible(False)

    def onStateTooltip(self, title: str, subTitle: str, show: bool):
        if show:
            self.stateTooltip = StateToolTip(title, subTitle, self.window())
            self.stateTooltip.move(self.stateTooltip.getSuitablePos())
            self.stateTooltip.show()
        else:
            self.stateTooltip.setContent(title)
            self.stateTooltip.setState(True)
            self.stateTooltip = None

    def set_theme(self):
        theme = Theme.DARK if config.dark_mode else Theme.LIGHT
        if theme == Theme.DARK:
            self.poolChart.setTheme(QChart.ChartThemeDark)
            self.poolChartView.setBackgroundBrush(QColor(32, 32, 32))
            self.poolChart.setBackgroundBrush(QColor(39, 39, 39))

            self.poolSlice1.setPen(QColor(39, 39, 39))
            self.poolSlice2.setPen(QColor(39, 39, 39))
            self.poolSlice3.setPen(QColor(39, 39, 39))
            self.poolSlice4.setPen(QColor(39, 39, 39))
            self.poolSlice5.setPen(QColor(39, 39, 39))

        else:
            self.poolChart.setTheme(QChart.ChartThemeLight)
            self.poolChartView.setBackgroundBrush(QColor(240, 240, 240))
            self.poolChart.setBackgroundBrush(QColor(255, 255, 255))

            self.poolSlice1.setPen(QColor(255, 255, 255))
            self.poolSlice2.setPen(QColor(255, 255, 255))
            self.poolSlice3.setPen(QColor(255, 255, 255))
            self.poolSlice4.setPen(QColor(255, 255, 255))
            self.poolSlice5.setPen(QColor(255, 255, 255))

        self.poolSlice1.setBrush(QColor(248, 220, 109))
        self.poolSlice1.setLabelFont(QFont("Microsoft YaHei", 10))

        self.poolSlice2.setBrush(QColor(219, 111, 103))
        self.poolSlice2.setLabelFont(QFont("Microsoft YaHei", 10))

        self.poolSlice3.setBrush(QColor(91, 113, 194))
        self.poolSlice3.setLabelFont(QFont("Microsoft YaHei", 10))

        self.poolSlice4.setBrush(QColor(159, 201, 124))
        self.poolSlice4.setLabelFont(QFont("Microsoft YaHei", 10))

        self.poolSlice5.setBrush(QColor(136, 192, 223))
        self.poolSlice5.setLabelFont(QFont("Microsoft YaHei", 10))

        self.poolChart.setTitle("群星跃迁")
        self.poolChart.setTitleFont(QFont("Microsoft YaHei", 12, QFont.Bold))
        self.poolChart.setFont(QFont("Microsoft YaHei", 10))
