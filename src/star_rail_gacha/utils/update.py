import logging
import os.path
import subprocess
from typing import Optional

import requests
from PyQt5.QtWidgets import QApplication

from .config import config
from .http import get
from ..constant import VERSION

log = logging.getLogger(__name__)

RELEASE_URL = "https://api.github.com/repos/DancingSnow0517/StarRail-gacha/releases/latest"

update_script = """
powershell -command \"Start-Sleep -s 5\"
powershell -command \"Get-childitem -Path .. -exclude *.json,*.zip,*.bat,temp,userData -Recurse | Remove-Item -Force -Recurse\"
powershell -command \"Expand-Archive -Path .\\StarRail-Gacha-Exporter.zip -DestinationPath ..\\ -Force\"
powershell -command \"Remove-Item -Path .\\StarRail-Gacha-Exporter.zip\"
powershell -command \"Remove-Item -Path .\\update.bat\"
"""


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


def download_update():
    log.info("正在下载更新...")
    payload, code = get(RELEASE_URL)
    if code == 200:
        assets_url = payload['assets'][0]['browser_download_url']
        file_name = payload['assets'][0]['name']
    else:
        return False

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
    return True


def apply_update():
    if not os.path.exists('temp/StarRail-Gacha-Exporter.zip'):
        return False
    if not os.path.exists('temp'):
        os.mkdir('temp')
    with open('temp/update.bat', 'w') as f:
        f.write(update_script)

    subprocess.Popen(
        [
            "update.bat"
        ],
        cwd='temp',
        stdout=subprocess.PIPE,
        shell=True
    )
    QApplication.quit()
