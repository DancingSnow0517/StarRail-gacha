import json
import os.path
from typing import List, Dict, Tuple

from .gacha import Gacha
from .types import GachaType


class GachaManager:

    def __init__(self, uid: str):
        self.uid = uid
        self.records: Dict[GachaType, List[Gacha]] = {}

    def get_gacha_list(self, gacha_type: GachaType) -> List[Gacha]:
        return self.records.get(gacha_type)

    def save_to_file(self):
        if not os.path.exists('userData'):
            os.mkdir('userData')
        with open(f'userData/gacha-list-{self.uid}.json', 'w', encoding='utf-8') as f:
            json.dump(self.record_dict, f, indent=4, ensure_ascii=False)

    def load_from_file(self):
        if not os.path.exists('userData'):
            os.mkdir('userData')
        if os.path.exists(f'userData/gacha-list-{self.uid}.json'):
            with open(f'userData/gacha-list-{self.uid}.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            for gacha_type in GachaType:
                self.records[gacha_type] = []
                for d in data.get(gacha_type.value, []):
                    self.records[gacha_type].append(Gacha(**d))
        else:
            for gacha_type in GachaType:
                self.records[gacha_type] = []
            self.save_to_file()

    def add_records(self, records: List[Gacha]) -> Tuple[bool, int]:
        flag = True
        count = 0
        for record in records:
            if self.add_record(record):
                count += 1
            else:
                flag = False
        return flag, count

    def add_record(self, record: Gacha) -> bool:
        if self.is_record_exist(record):
            return False
        self.records[record.gacha_type].append(record)
        sorted(self.records[record.gacha_type], key=lambda x: x.id, reverse=True)
        return True

    def is_record_exist(self, record: Gacha) -> bool:
        for r in self.records[record.gacha_type]:
            if r.id == record.id:
                return True
        return False

    def get_count(self, gacha_type: GachaType) -> int:
        return len(self.records[gacha_type])

    def get_5star_count(self, gacha_type: GachaType) -> int:
        count = 0
        for record in self.records[gacha_type]:
            if record.is_5star:
                count += 1
        return count

    def get_5star_character_count(self, gacha_type: GachaType) -> int:
        count = 0
        for record in self.records[gacha_type]:
            if record.is_5star and record.is_character:
                count += 1
        return count

    def get_5star_light_cone_count(self, gacha_type: GachaType) -> int:
        count = 0
        for record in self.records[gacha_type]:
            if record.is_5star and record.is_light_cone:
                count += 1
        return count

    def get_4star_count(self, gacha_type: GachaType) -> int:
        count = 0
        for record in self.records[gacha_type]:
            if record.is_4star:
                count += 1
        return count

    def get_4star_character_count(self, gacha_type: GachaType) -> int:
        count = 0
        for record in self.records[gacha_type]:
            if record.is_4star and record.is_character:
                count += 1
        return count

    def get_4star_light_cone_count(self, gacha_type: GachaType) -> int:
        count = 0
        for record in self.records[gacha_type]:
            if record.is_4star and record.is_light_cone:
                count += 1
        return count

    def get_3star_count(self, gacha_type: GachaType) -> int:
        count = 0
        for record in self.records[gacha_type]:
            if record.is_3star:
                count += 1
        return count

    def get_last_5star_count(self, gacha_type: GachaType) -> int:
        count = 0
        for record in self.records[gacha_type]:
            if record.is_5star:
                break
            count += 1
        return count

    def get_last_4star_count(self, gacha_type: GachaType) -> int:
        count = 0
        for record in self.records[gacha_type]:
            if record.is_4star:
                break
            count += 1
        return count

    def get_5star_history(self, gacha_type: GachaType) -> List[Tuple[str, int]]:
        rt = []
        cost = 0
        for record in reversed(self.records[gacha_type]):
            if not record.is_5star:
                cost += 1
            else:
                cost += 1
                rt.append((record.name, cost))
                cost = 0
        return rt

    def get_5star_average(self, gacha_type: GachaType) -> float:
        count = 0
        total = 0
        for _, cost in self.get_5star_history(gacha_type):
            count += 1
            total += cost
        if total == 0:
            return 0
        return total / count

    def clear(self):
        for gacha_type in GachaType:
            self.records[gacha_type] = []
        self.save_to_file()

    @classmethod
    def load_from_uid(cls, uid: str):
        rt = cls(uid)
        rt.load_from_file()
        return rt

    @property
    def record_dict(self):
        rt = {}
        for gacha_type in GachaType:
            rt[gacha_type.value] = []
            for record in self.records[gacha_type]:
                rt[gacha_type.value].append(record.dict)
        return rt
