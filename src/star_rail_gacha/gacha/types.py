from enum import Enum


class GachaType(Enum):
    """
    STELLAR 常驻池
    DEPARTURE 新手池
    CHARACTER 角色UP池
    LIGHT_CONE 光锥UP池
    """
    STELLAR = '1'
    DEPARTURE = '2'
    CHARACTER = '11'
    LIGHT_CONE = '12'
    ALL = '-1'


class ItemType(Enum):
    CHARACTER = "角色"
    LIGHT_CONE = "光锥"

