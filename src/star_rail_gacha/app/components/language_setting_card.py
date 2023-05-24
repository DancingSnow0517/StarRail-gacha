import os
from typing import Union

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from qfluentwidgets import SettingCard, FluentIconBase, ComboBox

language_map = {
    "zh-CN": "简体中文",
    "zh-TW": "繁體中文",
    "en-US": "English",
    "ja-JP": "日本語",
    "de-DE": "Deutsch",
    "es-ES": "Español",
    "fr-FR": "Français",
    "id-ID": "Indonesia",
    "ko-KR": "한국어",
    "pt-PT": "Português",
    "ru-RU": "Русский",
    "th-TH": "ภาษาไทย",
    "vi-VN": "Tiếng Việt"
}


class LanguageSettingCard(SettingCard):

    def __init__(self, value: str, icon: Union[str, QIcon, FluentIconBase], title, content=None, parent=None):
        super().__init__(icon, title, content, parent)

        self.comboBox = ComboBox(self)
        self.hBoxLayout.addWidget(self.comboBox, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(16)

        language_list = os.listdir("resources/i18n")
        language_list.append("en-US")
        item_list = []
        for language in language_list:
            if os.path.isdir(f"resources/i18n/{language}"):
                item_list.append(f"{language_map[language]} ({language})" if language in language_map else language)

        self.comboBox.addItems(item_list)
        self.comboBox.setCurrentText(f"{language_map[value]} ({value})" if value in language_map else value)
        self.comboBox.setMinimumWidth(180)
