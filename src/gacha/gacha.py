import functools

from .types import GachaType, ItemType


@functools.total_ordering
class Gacha:
    uid: str
    gacha_id: str
    gacha_type: GachaType
    item_id: str
    count: str
    time: str
    name: str
    lang: str
    item_type: ItemType
    rank_type: str
    id: str

    def __init__(self, **kwargs) -> None:
        self.uid = kwargs.get('uid')
        self.gacha_id = kwargs.get('gacha_id')
        self.gacha_type = GachaType(kwargs.get('gacha_type'))
        self.item_id = kwargs.get('item_id')
        self.count = kwargs.get('count')
        self.time = kwargs.get('time')
        self.name = kwargs.get('name')
        self.lang = kwargs.get('lang')
        self.item_type = ItemType(kwargs.get('item_type'))
        self.rank_type = kwargs.get('rank_type')
        self.id = kwargs.get('id')

    def __eq__(self, other):
        return int(self.id) == int(other.id)

    def __le__(self, other):
        return int(self.id) < int(other.id)

    def __gt__(self, other):
        return int(self.id) > int(other.id)

    @property
    def dict(self):
        return {
            'uid': self.uid,
            'gacha_id': self.gacha_id,
            'gacha_type': self.gacha_type.value,
            'item_id': self.item_id,
            'count': self.count,
            'time': self.time,
            'name': self.name,
            'lang': self.lang,
            'item_type': self.item_type.value,
            'rank_type': self.rank_type,
            'id': self.id
        }

    @property
    def is_5star(self):
        return self.rank_type == '5'

    @property
    def is_4star(self):
        return self.rank_type == '4'

    @property
    def is_3star(self):
        return self.rank_type == '3'

    @property
    def is_character(self):
        return self.item_type == ItemType.CHARACTER

    @property
    def is_light_cone(self):
        return self.item_type == ItemType.LIGHT_CONE
