from PyQt5.QtChart import QPieSeries, QChart, QChartView, QPieSlice
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QPainter, QColor, QFont
from PyQt5.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout, QSpacerItem, QSizePolicy, QLabel
from qfluentwidgets import PushButton, FluentIcon, ComboBox, ToggleButton

from src.utils.QtStringUtil import coloredText


class HomePage(QFrame):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("home_page")

        self.update_button = PushButton("更新数据", self, FluentIcon.SYNC)
        self.update_button.clicked.connect(self.update_data)

        self.export_button = PushButton("导出数据", self, FluentIcon.FOLDER)
        self.export_button.clicked.connect(self.update_data)

        self.uid_box = ComboBox(self)
        self.uid_box.setMinimumSize(QSize(140, 0))
        self.uid_box.addItems(['101119319', '1234567890'])
        self.uid_box.setCurrentIndex(0)

        self.pool_box = ComboBox(self)
        self.pool_box.setMinimumSize(QSize(140, 0))
        self.pool_box.addItems(['群星跃迁', '角色活动跃迁', '光锥活动跃迁', '始发跃迁'])
        self.pool_box.setCurrentIndex(0)

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

        # 饼图数据布局
        self.dataLayout = QHBoxLayout()

        # 抽卡池子布局
        self.poolLayout = QVBoxLayout()
        self.poolSeries = QPieSeries()
        self.poolSeries.append("五星角色", 2)
        self.poolSeries.append("五星光锥", 1)
        self.poolSeries.append("四星角色", 13)
        self.poolSeries.append("四星光锥", 8)
        self.poolSeries.append("三星光锥", 90)
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
        self.character5StarButton.toggle()
        # self.character5StarButton.setStyleSheet("background-color: #F1C964")

        self.character4StarButton = ToggleButton("4星角色", self)
        self.character4StarButton.setMinimumSize(QSize(80, 0))
        self.character4StarButton.toggle()
        # self.character4StarButton.setStyleSheet("background-color: #5B71C2")

        self.lightCone5StarButton = ToggleButton("5星光锥", self)
        self.lightCone5StarButton.setMinimumSize(QSize(80, 0))
        self.lightCone5StarButton.toggle()
        # self.lightCone5StarButton.setStyleSheet("background-color: #DB6F67")

        self.lightCone4StarButton = ToggleButton("4星光锥", self)
        self.lightCone4StarButton.setMinimumSize(QSize(80, 0))
        self.lightCone4StarButton.toggle()
        # self.lightCone4StarButton.setStyleSheet("background-color: #9FC97C")

        self.lightCone3StarButton = ToggleButton("3星光锥", self)
        self.lightCone3StarButton.setMinimumSize(QSize(80, 0))
        # self.lightCone3StarButton.setStyleSheet("background-color: #88C0DF")

        self.dataButtonLayout.addWidget(self.character5StarButton)
        self.dataButtonLayout.addWidget(self.character4StarButton)
        self.dataButtonLayout.addWidget(self.lightCone5StarButton)
        self.dataButtonLayout.addWidget(self.lightCone4StarButton)
        self.dataButtonLayout.addWidget(self.lightCone3StarButton)

        self.poolLayout.addLayout(self.dataButtonLayout)

        self.poolTextLayout = QVBoxLayout()
        self.poolTextLayout.setContentsMargins(8, 16, 8, 24)

        self.poolLabelTotal = QLabel(
            f"一共 {coloredText('124', '#00BFFF')} 抽 已累计 {coloredText('36', '#32CD32')} 未出5星")
        self.poolLabelTotal.setFont(QFont("Microsoft YaHei", 10))
        self.poolLabel5Star = QLabel(coloredText('5星: 3'.ljust(10, '-') + '[2.41%]', '#FFD700'))
        self.poolLabel5Star.setFont(QFont("Microsoft YaHei", 10))
        self.poolLabel4Star = QLabel(coloredText('4星: 21'.ljust(10, '-') + '[16.93%]', '#BA55D3'))
        self.poolLabel4Star.setFont(QFont("Microsoft YaHei", 10))
        self.poolLabel3Star = QLabel(coloredText('3星: 90'.ljust(10, '-') + '[72.58%]', '#1E90FF'))
        self.poolLabel3Star.setFont(QFont("Microsoft YaHei", 10))
        self.poolLabel5StarHistory = QLabel(
            coloredText('瓦尔特[15] ', '#C71585') +
            coloredText('希儿[60] ', '#00FA9A') +
            coloredText('如泥酣眠[33]', '	#EE82EE')
        )
        self.poolLabel5StarHistory.setFont(QFont("Microsoft YaHei", 10))
        self.poolLabel5StarAverage = QLabel('5星平均出货次数: ' + coloredText('36.00', '#6FB172'))
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

    def update_data(self):
        print("update data")
        pass

    @staticmethod
    def on_hovered(pieSlice: QPieSlice, state: bool):
        if state:
            pieSlice.setExploded(True)
            pieSlice.setLabelVisible(True)
        else:
            pieSlice.setExploded(False)
            pieSlice.setLabelVisible(False)
