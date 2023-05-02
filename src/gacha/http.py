import json

import requests


def fetch(url):
    res = requests.get(url)
    if 200 <= res.status_code < 300:
        content = res.content.decode('utf-8')
        payload = json.loads(content)
        return payload, res.status_code
