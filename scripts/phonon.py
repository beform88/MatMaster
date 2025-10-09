import time

import requests

GOODS_API_BASE = 'https://goods-server.test.dp.tech'
FINANCE_API_BASE = 'https://finance-web.test.dp.tech'
user_id = 110680
sku_id = 10808


def sku_list():
    url = f"{GOODS_API_BASE}/api/v1/sku/list"
    payload = {'skuIds': [sku_id]}
    response = requests.post(
        url, json=payload, headers={'Content-Type': 'application/json'}
    )
    response.raise_for_status()
    data = response.json()

    print(data)


def info():
    url = f"{FINANCE_API_BASE}/api/integral/info"
    payload = {'userId': int(user_id)}

    response = requests.post(
        url, json=payload, headers={'Content-Type': 'application/json'}
    )
    response.raise_for_status()
    data = response.json()
    print(data)


def consume():
    url = f"{FINANCE_API_BASE}/api/integral/consume"
    payload = {
        'userId': int(user_id),
        'bizNo': int(time.time()),
        'changeType': 2,
        'eventValue': int(1),
        'skuId': int(sku_id),
    }
    response = requests.post(
        url, json=payload, headers={'Content-Type': 'application/json'}
    )
    response.raise_for_status()
    data = response.json()
    print(data)


if __name__ == '__main__':
    info()
