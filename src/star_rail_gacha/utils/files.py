import ctypes.wintypes
import logging
import os
import re
import subprocess
from typing import Optional

from .config import config

GAME_LOG_PATH = {
    'CN': 'miHoYo/崩坏：星穹铁道',
    'OS': 'Cognosphere/Star Rail'
}
PLAYER_LOG_PATH = os.environ["userprofile"] + '/AppData/LocalLow/{0}/Player.log'

log = logging.getLogger(__name__)


def get_game_path() -> Optional[str]:
    print(config.game_server)
    PATH = GAME_LOG_PATH.get(config.game_server)
    log_path = PLAYER_LOG_PATH.format(PATH)
    log.info(f'尝试查找日志位置：{log_path}')
    if not os.path.exists(log_path):
        log.warning(f"在目录: {log_path} 中未找到\"崩坏：星穹铁道\"日志")
        return
    log.info("正在读取 \"Player.log\"...")
    with open(log_path, 'r', encoding='utf-8') as f:
        log_content = f.read()
    match = re.search(r'Loading player data from (.*)StarRail_Data.*', log_content)
    if match:
        return match.group(1)
    log.error("未找到\"崩坏：星穹铁道\"日志")
    return None


def get_local_api_url(game_path: Optional[str] = None) -> Optional[str]:
    if not os.path.exists("temp"):
        os.mkdir("temp")
    if game_path is None:
        log.info("尝试获取游戏目录")
        game_path = get_game_path()
        if game_path is None:
            log.error("未找到游戏目录")
            return None

        log.info("游戏目录获取成功")
    log.info("尝试复制\"data_2\"到临时文件夹")
    p = subprocess.Popen(
        [
            "powershell", "Copy-Item",
            rf'"{game_path}StarRail_Data/webCaches/Cache/Cache_Data/data_2"',
            "-Destination", "temp"
        ], stdout=subprocess.PIPE, shell=True)
    p.wait()

    if os.path.exists('temp/data_2'):
        log.info('复制\"data_2\"成功')
    else:
        log.error('复制\"data_2\"失败')
        return None

    log.info("尝试获取抽卡记录 API")
    with open('temp/data_2', 'r', encoding='ISO-8859-1') as f:
        data = f.read()

    split_url = data.split('1/0/')
    api_url = None
    for s in split_url:
        match = re.match(r'https?.+getGachaLog.*(?:begin_id|end_id)=\d*', s)
        if match:
            api_url = match.group()
    if api_url:
        log.info("已获取到api地址：%s", api_url)
    else:
        log.error("未找到api地址！")
    return api_url


def get_doc_path(path_id=5):
    buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
    ctypes.windll.shell32.SHGetSpecialFolderPathW(None, buf, path_id, False)
    return buf.value
