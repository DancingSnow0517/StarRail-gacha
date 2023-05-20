import json
import logging

import requests

log = logging.getLogger(__name__)


def get(url):
    res = requests.get(url)
    if 200 <= res.status_code < 300:
        content = res.content.decode('utf-8')
        payload = json.loads(content)
        return payload, res.status_code


def check_response(payload, code):
    if payload is None or not 200 <= code < 300:
        log.warning(f'回应是否为空: {payload is None}')
        log.warning(f'状态码: {code}')
        return False, f"HTTP 错误: 得到了预期之外的状态码: {code}"
    if payload['retcode'] != 0:
        log.warning(f"回应的状态码: {payload['retcode']}")
        log.warning(f"回应的信息: {payload['message']}")
        return False, f"HTTP 错误: 得到了错误的http回应{'' if 'message' not in payload else ': ' + payload['message']}"

    if not payload['data']['list']:
        log.warning(
            f'回应的数据列表长度: {len(payload["data"]["list"])}',
        )
        return False, ""
    return True, ""
