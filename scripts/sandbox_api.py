import requests
from toolsy.logger import init_colored_logger

from agents.matmaster_agent.constant import (
    MATERIALS_ACCESS_KEY,
    MATERIALS_PROJECT_ID,
    OPENAPI_JOB_CREATE_API,
    OPENAPI_JOB_KILL_API,
)

logger = init_colored_logger(__name__)


def create_job():
    request_body_json = {'projectId': MATERIALS_PROJECT_ID, 'name': 'demo_job'}
    request_query_string = {'accessKey': MATERIALS_ACCESS_KEY}

    response = requests.post(
        OPENAPI_JOB_CREATE_API, json=request_body_json, params=request_query_string
    )
    print(response)


def kill_job(job_id):
    request_query_string = {'accessKey': MATERIALS_ACCESS_KEY}

    response = requests.post(
        f'{OPENAPI_JOB_KILL_API}/{job_id}', params=request_query_string
    )
    logger.info(response.json())
