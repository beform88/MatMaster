import logging
import time

import aiohttp

from agents.matmaster_agent.constant import (
    FINANCE_CONSUME_API,
    FINANCE_INFO_API,
)

logger = logging.getLogger(__name__)


async def get_user_photon_balance(user_id):
    payload = {'userId': int(user_id)}
    async with aiohttp.ClientSession() as session:
        async with session.post(
            FINANCE_INFO_API, json=payload, headers={'Content-Type': 'application/json'}
        ) as response:
            response.raise_for_status()
            res = await response.json()

            logger.info(f'[get_user_photon_balance] balance = {res['data']['balance']}')
            return res['data']['balance']


async def photon_consume(user_id, sku_id):
    payload = {
        'userId': int(user_id),
        'bizNo': int(time.time()),
        'changeType': 2,
        'eventValue': int(1),
        'skuId': int(sku_id),
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(
            FINANCE_CONSUME_API,
            json=payload,
            headers={'Content-Type': 'application/json'},
        ) as response:
            response.raise_for_status()
            res = await response.json()

            logger.info(f'[photon_consume] response = {res}')
            return res
