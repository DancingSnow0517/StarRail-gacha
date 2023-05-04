from enum import Enum

from qfluentwidgets import Theme

from .config import config


class StyleSheet(Enum):
    MAIN_WINDOW = "main_window"
    HOME_PAGE = "home_page"
    SETTINGS_PAGE = "settings_page"

    def path(self):
        if config.dark_mode:
            theme = Theme.DARK
        else:
            theme = Theme.LIGHT
        return f"resources/qss/{theme.value.lower()}/{self.value}.qss"

    def apply(self, widget):
        widget.setStyleSheet(self.read())

    def read(self):
        with open(self.path(), "r", encoding="utf-8") as f:
            return f.read()
