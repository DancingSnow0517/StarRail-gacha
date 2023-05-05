import logging
import os
import re
import sys
import time
import weakref
import zipfile
from threading import RLock
from typing import Set

from colorlog import ColoredFormatter


class SyncStdoutStreamHandler(logging.StreamHandler):
    __write_lock = RLock()
    __instance_lock = RLock()
    __instances = weakref.WeakSet()  # type: Set[SyncStdoutStreamHandler]

    def __init__(self):
        super().__init__(sys.stdout)
        with self.__instance_lock:
            self.__instances.add(self)

    def emit(self, record) -> None:
        with self.__write_lock:
            super().emit(record)

    @classmethod
    def update_stdout(cls, stream=None):
        if stream is None:
            stream = sys.stdout
        with cls.__instance_lock:
            instances = list(cls.__instances)
        for inst in instances:
            inst.acquire()  # use Handler's lock
            try:
                inst.stream = stream
            finally:
                inst.release()


class NoColorFormatter(logging.Formatter):
    def formatMessage(self, record):
        return clean_console_color_code(super().formatMessage(record))


class ColoredLogger(logging.Logger):
    DEFAULT_NAME = 'StarRail Gacha Exporter'
    LOG_COLORS = {
        'DEBUG': 'blue',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'bold_red',
    }
    SECONDARY_LOG_COLORS = {
        'message': {
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red'
        }
    }
    FILE_FMT = NoColorFormatter(
        '[%(asctime)s] [%(threadName)s/%(levelname)s]: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    def __init__(self, name=DEFAULT_NAME, level=logging.DEBUG) -> None:
        super().__init__(name)
        self.file_handler = None

        self.console_handler = SyncStdoutStreamHandler()
        self.console_handler.setFormatter(self.get_console_formatter())

        self.addHandler(self.console_handler)
        self.setLevel(level)

    @classmethod
    def get_console_formatter(cls):
        return ColoredFormatter(
            f'[%(asctime)s] [%(threadName)s/%(log_color)s%(levelname)s%(reset)s]: %('
            f'message_log_color)s%(message)s%(reset)s',
            log_colors=cls.LOG_COLORS,
            secondary_log_colors=cls.SECONDARY_LOG_COLORS,
            datefmt='%H:%M:%S'
        )

    def set_file(self, file_name: str):
        if self.file_handler is not None:
            self.removeHandler(self.file_handler)
        touch_directory(os.path.dirname(file_name))
        if os.path.isfile(file_name):
            modify_time = time.strftime('%Y-%m-%d', time.localtime(os.stat(file_name).st_mtime))
            counter = 0
            while True:
                counter += 1
                zip_file_name = '{}/{}-{}.zip'.format(os.path.dirname(file_name), modify_time, counter)
                if not os.path.isfile(zip_file_name):
                    break
            zipf = zipfile.ZipFile(zip_file_name, 'w')
            zipf.write(file_name, arcname=os.path.basename(file_name), compress_type=zipfile.ZIP_DEFLATED)
            zipf.close()
            os.remove(file_name)
        self.file_handler = logging.FileHandler(file_name, encoding='utf8')
        self.file_handler.setFormatter(self.FILE_FMT)
        self.addHandler(self.file_handler)


def clean_console_color_code(text):
    return re.sub(r'\033\[(\d+(;\d+)?)?m', '', text)


def touch_directory(directory_path: str):
    if not os.path.isdir(directory_path):
        os.makedirs(directory_path)


def patch_getLogger(logger):
    logging.getLogger = lambda name: logger
