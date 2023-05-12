import logging
import os.path
import subprocess
from typing import Optional, TYPE_CHECKING

import requests
from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import QApplication

from .config import config
from .http import get
from ..constant import VERSION

if TYPE_CHECKING:
    from ..app.pages.settings_page import SettingsPage

log = logging.getLogger(__name__)

RELEASE_URL = "https://api.github.com/repos/DancingSnow0517/StarRail-gacha/releases/latest"

update_script = """
powershell -command \"Start-Sleep -s 5\"
powershell -command \"Get-childitem -Path .. -exclude *.json,*.zip,*.bat,temp,userData -Recurse | Remove-Item -Force -Recurse\"
powershell -command \"Expand-Archive -Path .\\StarRail-Gacha-Exporter.zip -DestinationPath ..\\ -Force\"
powershell -command \"Remove-Item -Path .\\StarRail-Gacha-Exporter.zip\"
start ..\\StarRail Gacha Exporter.exe
powershell -command \"Remove-Item -Path .\\update.bat\"
"""


class DownloadThread(QThread):

    def __init__(self, parent: 'SettingsPage') -> None:
        super().__init__(parent)

    def run(self) -> None:
        log.info("正在下载更新...")
        self.parent().stateTooltipSignal.emit("软件更新", "正在下载更新, 请耐心等待下载完成！", True)
        payload, code = get(RELEASE_URL)
        if code == 200:
            assets_url = payload['assets'][0]['browser_download_url']
            file_name = payload['assets'][0]['name']
        else:
            self.parent().stateTooltipSignal.emit("软件更新", "下载更新失败", False)
            return

        if config.use_proxy:
            url = config.gh_proxy + assets_url
        else:
            url = assets_url
        log.info("准备下载：%s", url)
        if not os.path.exists('temp'):
            os.mkdir('temp')
        resp = requests.get(url, stream=True)
        count = resp.headers.get('content-length')
        with open(f'temp/{file_name}', 'wb') as f:
            for chunk in resp.iter_content(chunk_size=2048):
                if chunk:
                    f.write(chunk)
                    log.info("已下载：%s/%s", str(f.tell()), count)
        log.info("下载完成")
        self.parent().stateTooltipSignal.emit("软件更新", "下载更新成功，即将开始安装更新！", False)
        self.parent().downloadedUpdateSignal.emit()
        return


def check_latest_tag() -> Optional[str]:
    log.info("正在检查更新...")
    payload, code = get(RELEASE_URL)
    if code == 200:
        return payload['tag_name']
    else:
        return None


def check_update():
    tag = check_latest_tag()
    log.info("最新版本：%s", tag)
    if VERSION != tag:
        return tag
    return None


def download_update(parent: 'SettingsPage'):
    thread = DownloadThread(parent)
    thread.start()


def apply_update():
    log.info("正在应用更新...")
    if not os.path.exists('temp/StarRail-Gacha-Exporter.zip'):
        return False
    if not os.path.exists('temp'):
        os.mkdir('temp')
    log.info("写入更新脚本")
    with open('temp/update.bat', 'w') as f:
        f.write(update_script)

    subprocess.Popen(
        [
            "start",
            "update.bat"
        ],
        cwd='temp',
        stdout=subprocess.PIPE,
        shell=True
    )
    QApplication.quit()
