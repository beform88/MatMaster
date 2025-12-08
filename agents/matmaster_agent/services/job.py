import json
import logging

import aiohttp

from agents.matmaster_agent.constant import (
    MATMASTER_AGENT_NAME,
    OPENAPI_HOST,
)
from agents.matmaster_agent.logger import PrefixFilter
from agents.matmaster_agent.utils.callback_utils import _get_ak, _get_projectId

logger = logging.getLogger(__name__)
logger.addFilter(PrefixFilter(MATMASTER_AGENT_NAME))
logger.setLevel(logging.INFO)


async def check_job_create_service(ctx):
    job_create_url = f"{OPENAPI_HOST}/openapi/v1/sandbox/job/create"
    access_key = _get_ak(ctx)
    project_id = _get_projectId(ctx)
    payload = {
        'projectId': project_id,
        'name': 'check_job_create',
    }
    params = {'accessKey': access_key}
    logger.info(f"project_id = {project_id}, ak = {access_key}")

    async with aiohttp.ClientSession() as session:
        async with session.post(
            job_create_url, json=payload, params=params
        ) as response:
            res = json.loads(await response.text())
            if res['code'] != 0:
                if res['code'] == 140202:
                    res['error'][
                        'msg'
                    ] = '钱包余额不足，请在[此页面](https://www.bohrium.com/consume?menu=cash)充值后重试。'

                return res
