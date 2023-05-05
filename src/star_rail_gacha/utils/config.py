import json
import os


class Config:
    game_path: str
    get_full_data: bool
    dark_mode: bool
    theme_color: str
    log_level: str

    def __init__(self, **kwargs):
        self.game_path = kwargs.get('game_path', '')
        self.get_full_data = kwargs.get('get_full_data', False)
        self.dark_mode = kwargs.get('dark_mode', False)
        self.theme_color = kwargs.get('theme_color', '#009FAA')
        self.log_level = kwargs.get('log_level', 'INFO')

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
            'dark_mode': self.dark_mode,
            'theme_color': self.theme_color,
            'log_level': self.log_level
        }

    def save(self):
        with open('config.json', 'w', encoding='utf-8') as f:
            json.dump(self.dict, f, indent=4, ensure_ascii=False)


config = Config.load()
