import json
from typing import Dict, Optional
from bidict import bidict

data_path = 'resources/starrail_all.json'

lang_map = {
    'zh-cn': 'chs',
    'zh-tw': 'cht',
    'de-de': 'de',
    'en-us': 'en',
    'es-es': 'es',
    'fr-fr': 'fr',
    'id-id': 'id',
    'ja-jp': 'jp',
    'ko-kr': 'kr',
    'pt-pt': 'pt',
    'ru-ru': 'ru',
    'th-th': 'th',
    'vi-vn': 'vi',
}


class ItemTranslateManager:
    data: Dict[str, bidict[str, int]]

    @classmethod
    def init(cls):
        rt = cls()
        rt.load()
        return rt

    def load(self):
        self.data = {}
        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        for lang, d in data.items():
            self.data[lang] = bidict(d)

    def translate_from_item_id(self, lang: str, item_id: int) -> Optional[str]:
        if item_id in self.data[lang_map[lang]].inverse:
            return self.data[lang_map[lang]].inverse[item_id]
        else:
            return None


translate_manager = ItemTranslateManager.init()
