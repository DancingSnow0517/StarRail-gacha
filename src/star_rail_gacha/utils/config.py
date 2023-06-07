import json
import os

from PyQt5.QtCore import QObject, pyqtSignal


class Config(QObject):
    game_path: str
    get_full_data: bool
    game_server: str
    dark_mode: bool
    theme_color: str
    language: str
    log_level: str
    use_proxy: bool
    gh_proxy: str
    show_departure: bool

    showDepartureChanged = pyqtSignal(bool)

    def __init__(self, **kwargs):
        super().__init__()
        self.game_path = kwargs.get('game_path', '')
        self.get_full_data = kwargs.get('get_full_data', False)
        self.game_server = kwargs.get('game_server', 'CN')
        self.dark_mode = kwargs.get('dark_mode', False)
        self.theme_color = kwargs.get('theme_color', '#009FAA')
        self.language = kwargs.get('language', 'en-US')
        self.log_level = kwargs.get('log_level', 'INFO')
        self.use_proxy = kwargs.get('use_proxy', False)
        self.gh_proxy = kwargs.get('gh_proxy', 'https://ghproxy.com/')
        self.show_departure = kwargs.get('show_departure', True)

    @classmethod
    def load(cls):
        if not os.path.exists('config.json'):
            rt = cls()
        else:
            with open('config.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            rt = cls(**data)
        rt.save()
        return rt

    @property
    def dict(self):
        return {
            'game_path': self.game_path,
            'get_full_data': self.get_full_data,
            'game_server': self.game_server,
            'dark_mode': self.dark_mode,
            'theme_color': self.theme_color,
            'language': self.language,
            'log_level': self.log_level,
            'use_proxy': self.use_proxy,
            'gh_proxy': self.gh_proxy,
            'show_departure': self.show_departure
        }

    def save(self):
        with open('config.json', 'w', encoding='utf-8') as f:
            json.dump(self.dict, f, indent=4, ensure_ascii=False)


config = Config.load()
