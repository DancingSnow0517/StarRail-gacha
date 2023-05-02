import itertools
import json
import logging
import time

from .http import fetch
from .types import GachaType
from .url import get_url_template, get_api_url

log = logging.getLogger(__name__)


def check_response(payload, code):
    if payload is None or not 200 <= code < 300:
        log.warning(f'回应是否为空: {payload is None}')
        log.warning(f'状态码: {code}')
        return False
    if 'data' not in payload or 'list' not in payload['data']:
        log.warning(f'回应是否包含 `data`: {"data" in payload}')
        log.warning(
            f'回应 `data` 是否包含 `list`: {"list" in payload["data"]}',
        )
        return False
    if not payload['data']['list']:
        log.warning(
            f'回应的数据列表长度: {len(payload["data"]["list"])}',
        )
        return False
    return True


def export_gacha_type(api_template: str, gacha_type: GachaType):
    ret = []
    end_id = '0'
    for page in itertools.count(1, 1):
        log.info(f'正在获取 {gacha_type.name} 第 {page} 页')
        api_url = get_api_url(
            api_template, end_id, str(gacha_type.value),
            str(page), '5',
        )
        response, code = fetch(api_url)
        if not check_response(response, code):
            break
        data_list = response['data']['list']
        ret.extend(data_list)
        end_id = data_list[-1]['id']
        time.sleep(1)
    return ret


def export_gacha_from_api(api_url):
    response, code = fetch(api_url)
    valid = check_response(response, code)
    if not valid:
        log.fatal('Error while checking response from api URL, exitting')
        raise ValueError('Invalid api URL, please check your input')

    api_template = get_url_template(api_url)
    uid = response['data']['list'][0]['uid']

    gacha_records = {}
    total = 0
    for gacha_type in GachaType:
        records = export_gacha_type(api_template, gacha_type)
        total += len(records)
        gacha_records[gacha_type.name] = records

    log.info(f"记录获取完成，共获得 {total} 条记录。")
    log.info("正在尝试写入到文件")
    with open(f"gacha-list-{uid}.json", 'w', encoding='utf-8') as f:
        json.dump(gacha_records, f, ensure_ascii=False, indent=4)
    log.info(f"写入文件成功：gacha-list-{uid}.json")
