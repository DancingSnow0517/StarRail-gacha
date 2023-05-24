import sys

from PyQt5.QtCore import Qt, QTranslator
from PyQt5.QtWidgets import QApplication

from star_rail_gacha.utils.config import config
from star_rail_gacha.utils.logger import patch_getLogger, ColoredLogger

log = ColoredLogger('LittlePaimon', level=config.log_level)


def main():
    patch_getLogger(log)
    log.set_file('logs/latest.log')

    from star_rail_gacha.app.main_window import MainWindow
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)
    app.font().families().append("Microsoft YaHei UI")

    trans = QTranslator()
    trans.load("source", f"resources/i18n/{config.language}")
    app.installTranslator(trans)

    main_app = MainWindow()
    main_app.show()

    app.exec_()


if __name__ == '__main__':
    sys.exit(main())
