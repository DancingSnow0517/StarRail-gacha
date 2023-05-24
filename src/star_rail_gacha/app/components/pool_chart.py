from PyQt5.QtChart import QPieSeries, QPieSlice, QChart, QChartView
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QColor, QFont, QPainter
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from qfluentwidgets import ToggleButton, Theme, qconfig

from ...gacha.gacha_manager import GachaManager
from ...gacha.types import GachaType
from ...utils.QtStringUtil import coloredText
from ...utils.alias import get_gacha_name_by_type
from ...utils.colormap import reset_index, now_color, next_color
from ...utils.config import config
from ...utils.style_sheet import StyleSheet


class PoolChart(QWidget):
    def __init__(self, gacha_type: GachaType, parent=None) -> None:
        super().__init__(parent)

        self.setMinimumSize(300, 300)

        self.gacha_type = gacha_type
        self.uid = ''
        self.vBoxLayout = QVBoxLayout(self)

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
        self.poolChart.setTitle(get_gacha_name_by_type(self.gacha_type))
        self.poolChart.setTitleFont(QFont("Microsoft YaHei", 16, QFont.Bold))
        self.poolChart.setFont(QFont("Microsoft YaHei", 10))
        self.poolChart.setMinimumHeight(400)

        self.poolChartView = QChartView(self.poolChart)
        self.poolChartView.setRenderHint(QPainter.Antialiasing)
        self.vBoxLayout.addWidget(self.poolChartView)

        self.dataButtonLayout = QHBoxLayout()

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
        self.vBoxLayout.addLayout(self.dataButtonLayout)

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

        self.vBoxLayout.addWidget(self.poolLabelTotal)
        self.vBoxLayout.addWidget(self.poolLabel5Star)
        self.vBoxLayout.addWidget(self.poolLabel4Star)
        self.vBoxLayout.addWidget(self.poolLabel3Star)
        self.vBoxLayout.addWidget(self.poolLabel5StarHistory)
        self.vBoxLayout.addWidget(self.poolLabel5StarAverage)

        self.setMinimumSize(QSize(500, 600))

        qconfig.themeChanged.connect(self.set_theme)
        StyleSheet.HOME_PAGE.apply(self)

        self.set_theme()

    def set_uid(self, uid: str):
        self.uid = uid
        self.update_chart()

    def update_chart(self):
        reset_index()
        if self.uid == '':
            return
        gm = GachaManager.load_from_uid(self.uid)
        self.poolSlice1.setValue(
            gm.get_5star_character_count(self.gacha_type) if self.character5StarButton.isChecked() else 0)
        self.poolSlice2.setValue(
            gm.get_5star_light_cone_count(self.gacha_type) if self.lightCone5StarButton.isChecked() else 0)
        self.poolSlice3.setValue(
            gm.get_4star_character_count(self.gacha_type) if self.character4StarButton.isChecked() else 0)
        self.poolSlice4.setValue(
            gm.get_4star_light_cone_count(self.gacha_type) if self.lightCone4StarButton.isChecked() else 0)
        self.poolSlice5.setValue(gm.get_3star_count(self.gacha_type) if self.lightCone3StarButton.isChecked() else 0)

        self.poolSlice1.setLabel(
            f"5星角色: {gm.get_5star_character_count(self.gacha_type)}" if self.character5StarButton.isChecked() else "")
        self.poolSlice2.setLabel(
            f"5星光锥: {gm.get_5star_light_cone_count(self.gacha_type)}" if self.lightCone5StarButton.isChecked() else "")
        self.poolSlice3.setLabel(
            f"4星角色: {gm.get_4star_character_count(self.gacha_type)}" if self.character4StarButton.isChecked() else "")
        self.poolSlice4.setLabel(
            f"4星光锥: {gm.get_4star_light_cone_count(self.gacha_type)}" if self.lightCone4StarButton.isChecked() else "")
        self.poolSlice5.setLabel(
            f"3星光锥: {gm.get_3star_count(self.gacha_type)}" if self.lightCone3StarButton.isChecked() else "")
        count_text = gm.get_last_5star_count(self.gacha_type) if \
            self.gacha_type != GachaType.ALL else f"{gm.get_last_5star_count(GachaType.STELLAR)} + " \
                                                  f"{gm.get_last_5star_count(GachaType.CHARACTER)} + " \
                                                  f"{gm.get_last_5star_count(GachaType.LIGHT_CONE)} + " \
                                                  f"{gm.get_last_5star_count(GachaType.DEPARTURE)}" \
                                                  f" ({gm.get_last_5star_count(GachaType.STELLAR) + gm.get_last_5star_count(GachaType.CHARACTER) + gm.get_last_5star_count(GachaType.LIGHT_CONE) + gm.get_last_5star_count(GachaType.DEPARTURE)})"
        self.poolLabelTotal.setText(
            f"一共 {coloredText(gm.get_count(self.gacha_type), '#00BFFF')} 抽 "
            f"已累计 {coloredText(count_text, '#32CD32')} 未出5星")
        self.poolLabel5Star.setText(coloredText(f'5星: {gm.get_5star_count(self.gacha_type)}'.ljust(10, '-') +
                                                (
                                                    f'{(gm.get_5star_count(self.gacha_type) / gm.get_count(self.gacha_type) * 100):.2f}%'
                                                    if gm.get_5star_count(self.gacha_type) != 0 else "0%"), '#DAA520'))
        self.poolLabel4Star.setText(coloredText(f'4星: {gm.get_4star_count(self.gacha_type)}'.ljust(10, '-') +
                                                (
                                                    f'{(gm.get_4star_count(self.gacha_type) / gm.get_count(self.gacha_type) * 100):.2f}%'
                                                    if gm.get_4star_count(self.gacha_type) != 0 else "0%"), '#BA55D3'))
        self.poolLabel3Star.setText(coloredText(f'3星: {gm.get_3star_count(self.gacha_type)}'.ljust(10, '-') +
                                                (
                                                    f'{(gm.get_3star_count(self.gacha_type) / gm.get_count(self.gacha_type) * 100):.2f}%'
                                                    if gm.get_3star_count(self.gacha_type) != 0 else "0%"), '#00BFFF'))

        if self.gacha_type == GachaType.ALL:
            history_text = ''
        else:
            history_text = '5星历史记录: '
            his = gm.get_5star_history(self.gacha_type)
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
            '5星平均出货次数为: ' + coloredText(f'{gm.get_5star_average(self.gacha_type):.2f}', '#6FB172'))

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

        self.poolChart.setTitle(get_gacha_name_by_type(self.gacha_type))
        self.poolChart.setTitleFont(QFont("Microsoft YaHei", 12, QFont.Bold))
        self.poolChart.setFont(QFont("Microsoft YaHei", 10))

    @staticmethod
    def on_hovered(pieSlice: QPieSlice, state: bool):
        if state:
            pieSlice.setExploded(True)
            pieSlice.setLabelVisible(True)
        else:
            pieSlice.setExploded(False)
            pieSlice.setLabelVisible(False)
