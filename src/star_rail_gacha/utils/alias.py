from typing import Optional

from ..gacha.types import GachaType


def get_gacha_name_by_type(gacha_type: GachaType) -> Optional[str]:
    if gacha_type == GachaType.ALL:
        return "跃迁总览"
    elif gacha_type == GachaType.CHARACTER:
        return "角色活动跃迁"
    elif gacha_type == GachaType.LIGHT_CONE:
        return "光锥活动跃迁"
    elif gacha_type == GachaType.DEPARTURE:
        return "始发跃迁"
    elif gacha_type == GachaType.STELLAR:
        return "群星跃迁"
    else:
        return None