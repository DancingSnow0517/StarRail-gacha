from enum import Enum

from qfluentwidgets import Theme, StyleSheetBase, qconfig

from .config import config


class StyleSheet(StyleSheetBase, Enum):
    MAIN_WINDOW = "main_window"
    HOME_PAGE = "home_page"
    SETTINGS_PAGE = "settings_page"
    HISTORY_PAGE = "history_page"

    def path(self, theme: Theme = Theme.AUTO):
        theme = qconfig.theme if theme == Theme.AUTO else theme
        return f"resources/qss/{theme.value.lower()}/{self.value}.qss"
