import os
from pathlib import Path

import jsonpickle
import requests
from toolsy.logger import init_colored_logger

from agents.matmaster_agent.constant import (
    BOHRIUM_ACCESS_KEY,
    BOHRIUM_HOST,
    MATERIALS_ACCESS_KEY,
    MATERIALS_PROJECT_ID,
    OPENAPI_FILE_TOKEN_API,
    OPENAPI_HOST,
    OPENAPI_JOB_CREATE_API,
    OPENAPI_JOB_KILL_API,
    OPENAPI_JOB_LIST_API,
    OpenAPIJobAPI,
)

logger = init_colored_logger(__name__)


def get_token():
    url = f'{OPENAPI_HOST}/openapi/v1/storage/token'
    headers = {'x-app-key': 'agent'}
    params = {'projectId': MATERIALS_PROJECT_ID, 'accessKey': MATERIALS_ACCESS_KEY}
    response = requests.get(url, headers=headers, params=params)
    logger.info(response.json())


def get_ticket(authorization):
    headers = {'authorization': authorization}

    url = f'{BOHRIUM_HOST}/bohrapi/v1/ticket/get'
    response = requests.get(url, headers=headers)
    logger.info(response.json())

    return response.json()['data']['ticket']


def create_job():
    request_body_json = {'projectId': MATERIALS_PROJECT_ID, 'name': 'demo_job'}
    request_query_string = {'accessKey': MATERIALS_ACCESS_KEY}

    response = requests.post(
        OPENAPI_JOB_CREATE_API, json=request_body_json, params=request_query_string
    )
    print(response)


def kill_job(job_id, use_ticket=False, authorization=None):
    url = f'{OPENAPI_JOB_KILL_API}/{job_id}'
    if use_ticket and authorization:
        ticket = get_ticket(authorization)
        headers = {'Brm-Ticket': ticket}
        response = requests.post(url, headers=headers)
    else:
        request_query_string = {'accessKey': MATERIALS_ACCESS_KEY}
        response = requests.post(url, params=request_query_string)

    logger.info(response.json())


def get_job_detail(job_id, use_ticket=False, authorization=None):
    if use_ticket and authorization:
        ticket = get_ticket(authorization)
        headers = {'Brm-Ticket': ticket}
        response = requests.get(f"{OpenAPIJobAPI}/{job_id}", headers=headers)
        logger.info(response.json())


def get_job_list(
    job_ids, use_ticket=False, authorization=None, realUserId=None, sessionId=None
):
    if use_ticket and authorization:
        ticket = get_ticket(authorization)
        headers = {'Brm-Ticket': ticket}
        query_params = {
            'jobIds': job_ids,
            'realUserId': realUserId,
            'sessionId': sessionId,
        }
        response = requests.get(
            OPENAPI_JOB_LIST_API, headers=headers, params=query_params
        )
        logger.info(response.json())


def get_token_and_download_file(file_path, job_id):
    # 获取log文件的token
    request_body = {'filePath': file_path, 'jobId': job_id}
    response = requests.post(
        f"{OPENAPI_FILE_TOKEN_API}?accessKey={BOHRIUM_ACCESS_KEY}",
        json=request_body,
    )
    response.raise_for_status()
    response_data_json: dict = response.json().get('data', {})

    response_file_token = response_data_json.get('token', '')
    response_file_path = response_data_json.get('path', '')
    response_file_host = response_data_json.get('host', '')

    # 构建log文件URL并检查状态
    if response_file_host and response_file_path and response_file_token:
        file_url = f"{response_file_host}/api/download/{response_file_path}?token={response_file_token}"
        file_response = requests.get(file_url, timeout=10)
        check_status_and_download_file(file_response, file_path)
    else:
        logger.error(f'Incomplete {file_path} information - cannot construct file URL')


def check_status_and_download_file(response, file_download_path):
    def download_file(response, output_path):
        total_size = int(response.headers.get('content-length', 0))
        downloaded_size = 0

        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded_size += len(chunk)
                    if total_size > 0:
                        progress = (downloaded_size / total_size) * 100
                        print(
                            f"\rDownload progress: {progress:.1f}%", end='', flush=True
                        )

        print()

    status_code = response.status_code
    if status_code == 400:
        logger.error(f'`{file_download_path}` url returned 400 Bad Request')
    elif status_code == 200:
        download_file(response, file_download_path)
        if Path(file_download_path).exists():
            file_size = os.path.getsize(file_download_path)
            logger.info(
                f"Download `{file_download_path}` completed successfully! File size: {file_size} bytes"
            )
        else:
            logger.error(
                f"Error: Download `{file_download_path}` failed - file doesn't exist"
            )
    else:
        logger.error(f'`{file_download_path}` url returned status code: {status_code}')


def parse_results_txt(file_path='results.txt', job_id=''):
    get_token_and_download_file(file_path, job_id)
    with open(file_path) as f:
        result = jsonpickle.loads(f.read())
    os.remove(file_path)

    return result


if __name__ == '__main__':
    authorization = os.getenv('BEARER_TOKEN')
    job_id = '70d5f3d536c3461bba36d7c31902bc70'
    # use_ticket_get_job_list(['03b212ee76964c82bc58c1c2314fac79'], 110680, '19c1a7d4-2502-44fc-a58c-f29cce49986f')
    # kill_job(job_id, use_ticket=True, authorization=authorization)
    # get_job_detail(job_id, use_ticket=True, authorization=authorization)
    # get_token()
    file_path = '20251204072612.abacus_cal_elastic.d53401f9'
    get_token_and_download_file(file_path, job_id)
    result = parse_results_txt(job_id=job_id)
