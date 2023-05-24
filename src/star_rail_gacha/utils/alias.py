from typing import Optional

from PyQt5.QtCore import QObject

from ..gacha.types import GachaType


class AliasUtils(QObject):
    def get_gacha_name_by_type(self, gacha_type: GachaType) -> Optional[str]:
        if gacha_type == GachaType.ALL:
            return self.tr("Warp Overview")
        elif gacha_type == GachaType.CHARACTER:
            return self.tr("Character Event Warp")
        elif gacha_type == GachaType.LIGHT_CONE:
            return self.tr("Light Cone Event Warp")
        elif gacha_type == GachaType.DEPARTURE:
            return self.tr("Departure Warp")
        elif gacha_type == GachaType.STELLAR:
            return self.tr("Stellar Warp")
        else:
            return None


alias_utils = AliasUtils()
