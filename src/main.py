import sys
import traceback
from types import TracebackType
from typing import Type, Optional

from PyQt5.QtCore import Qt, QTranslator
from PyQt5.QtWidgets import QApplication

from star_rail_gacha.utils.config import config
from star_rail_gacha.utils.logger import patch_getLogger, ColoredLogger

log = ColoredLogger('StarRail-Gacha', level=config.log_level)


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
    main_app.window()
    main_app.show()

    hook_sys_except()

    app.exec_()


def hook_sys_except():
    def exception_hook(exc_type: Type[BaseException], exc_value: BaseException, tb: Optional[TracebackType]):
        log.critical('Uncaught exception: ', exc_info=(exc_type, exc_value, tb))

        sys.__excepthook__(exc_type, exc_value, tb)

        err_msg = ''.join(traceback.format_exception(exc_type, exc_value, tb))
        err_msg += '\n'
        err_msg += 'An uncaught exception occurred. Place report it to github issue!'

        QApplication.exit(-500)

    sys.excepthook = exception_hook


if __name__ == '__main__':
    sys.exit(main())
