import json
import os


class Config:
    game_path: str
    get_full_data: bool

    def __init__(self, **kwargs):
        self.game_path = kwargs.get('game_path', '')
        self.get_full_data = kwargs.get('get_full_data', False)

    @classmethod
    def load(cls):
        if not os.path.exists('config.json'):
            return cls()
        with open('config.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls(**data)

    @property
    def dict(self):
        return {
            'game_path': self.game_path,
            'get_full_data': self.get_full_data
        }

    def save(self):
        with open('config.json', 'w', encoding='utf-8') as f:
            json.dump(self.dict, f, indent=4, ensure_ascii=False)


config = Config.load()
