import logging
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

from src.app.main_window import MainWindow
from constant import VERSION
from gacha.files import get_local_api_url
from gacha.service import export_gacha_from_api

log = logging.getLogger(__name__)


def main():
    # logging.basicConfig(
    #     format='[%(asctime)s] [%(threadName)s/%(levelname)s]: %(message)s',
    #     datefmt='%Y-%m-%d %H:%M:%S',
    #     level='INFO'
    # )
    #
    # log.info(f"欢迎使用 崩坏：星穹铁道 抽卡导出工具v.{VERSION}")
    # log.info(f"当前仅支持导出 json 格式文件")
    # log.info("请先打开游戏的抽卡历史记录")
    #
    # input("按下回车键继续")
    #
    # api_url = get_local_api_url()
    # export_gacha_from_api(api_url)
    #
    # input('按回车键退出...')

    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)
    main_app = MainWindow()
    main_app.show()

    app.exec_()


if __name__ == '__main__':
    sys.exit(main())
