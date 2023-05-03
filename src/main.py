import logging
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

from star_rail_gacha.app.main_window import MainWindow

log = logging.getLogger(__name__)


def main():
    logging.basicConfig(
        format='[%(asctime)s] [%(threadName)s/%(levelname)s]: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        level='INFO'
    )

    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)
    app.font().families().append("Microsoft YaHei UI")
    main_app = MainWindow()
    main_app.show()

    app.exec_()


if __name__ == '__main__':
    sys.exit(main())
