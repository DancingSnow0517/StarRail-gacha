import functools
from datetime import datetime, timedelta

from .types import GachaType, ItemType


@functools.total_ordering
class Gacha:
    gacha_id: str
    gacha_type: GachaType
    item_id: str
    count: str
    name: str
    item_type: ItemType
    rank_type: str
    id: str

    _timestamp: float
    _region_time_zone: int

    def __init__(self, region_time_zone, **kwargs) -> None:
        self.gacha_id = kwargs.get('gacha_id')
        self.gacha_type = GachaType(kwargs.get('gacha_type'))
        self.item_id = kwargs.get('item_id')
        self.count = kwargs.get('count')
        self.name = kwargs.get('name')
        self.item_type = ItemType.CHARACTER if self.item_id.startswith('1') else ItemType.LIGHT_CONE
        self.rank_type = kwargs.get('rank_type')
        self.id = kwargs.get('id')

        self._region_time_zone = region_time_zone
        _iso_format = kwargs.get('time', '').replace(' ', 'T') + \
                           ('+%02d' if self._region_time_zone >= 0 else '%03d') % self._region_time_zone + ':00'
        self._timestamp = datetime.fromisoformat(_iso_format).timestamp()

    def __eq__(self, other):
        return int(self.id) == int(other.id)

    def __le__(self, other):
        return int(self.id) < int(other.id)

    def __gt__(self, other):
        return int(self.id) > int(other.id)

    def set_region_time_zone(self, region_time_zone: int):
        self._region_time_zone = region_time_zone

    @property
    def time(self) -> str:
        return (datetime.utcfromtimestamp(self._timestamp) + timedelta(hours=self._region_time_zone)) \
            .strftime("%Y-%m-%d %H:%M:%S")

    @property
    def dict(self):
        return {
            'gacha_id': self.gacha_id,
            'gacha_type': self.gacha_type.value,
            'item_id': self.item_id,
            'count': self.count,
            'time': self.time,
            'name': self.name,
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
