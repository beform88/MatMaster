import argparse
import json
import os
import sys
from datetime import datetime

import requests
from dotenv import find_dotenv, load_dotenv
from toolsy.logger import init_colored_logger

from agents.matmaster_agent.utils.job_utils import mapping_status
from scripts.constant import FILE_TOKEN_API, JOB_DETAIL_API

load_dotenv(find_dotenv())

logger = init_colored_logger(__name__)


def get_duration(create_time, update_time):
    """
    计算两个时间戳之间的时间差，格式化为时-分-秒

    Args:
        create_time (str): 创建时间，ISO 8601格式
        update_time (str): 更新时间，ISO 8601格式

    Returns:
        str: 时间差，格式为"时-分-秒"
    """
    # 解析时间字符串为datetime对象
    create_dt = datetime.fromisoformat(create_time)
    update_dt = datetime.fromisoformat(update_time)

    # 计算时间差
    time_diff = update_dt - create_dt

    # 提取总秒数
    total_seconds = int(time_diff.total_seconds())

    # 计算小时、分钟、秒
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60

    # 格式化为时-分-秒
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


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
                    print(f"\rDownload progress: {progress:.1f}%", end='', flush=True)

    print()


def main():
    parser = argparse.ArgumentParser(description='Download job results from API')
    parser.add_argument('job_id', help='Job ID to fetch results for')
    parser.add_argument(
        '-o',
        '--output',
        default='output.zip',
        help='Output file path (default: output.zip)',
    )

    args = parser.parse_args()

    # 删除已存在的输出文件
    if os.path.exists(args.output):
        os.remove(args.output)

    # 调用API获取job信息
    logger.info(f"Job ID: {args.job_id}")

    try:
        response = requests.get(
            f"{JOB_DETAIL_API}/{args.job_id}?accessKey={os.getenv('MATERIALS_ACCESS_KEY')}"
        )
        response.raise_for_status()
        job_info = response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error: Failed to fetch data from API: {e}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        logger.error(f"Error: Failed to parse JSON response: {e}")
        sys.exit(1)

    logger.debug(f"\n{json.dumps(job_info, indent=2, ensure_ascii=False)}")

    create_time = job_info['data']['createTime']
    update_time = job_info['data']['updateTime']
    duration = get_duration(create_time, update_time)
    job_status = mapping_status(job_info['data']['status'])
    job_name = job_info['data']['jobName']
    logger.info(f"{job_name}[{job_status}] -- {duration}")
    # 解析JSON获取resultUrl
    if job_info.get('code') == 0:
        result_url = job_info.get('data', {}).get('resultUrl', '')
    elif job_info.get('code') == 6020:
        logger.error(f"API returned error code: {job_info.get('code')}")
        sys.exit(-1)
    else:
        result_url = ''
        logger.error(f"API returned error code: {job_info.get('code')}")

    # 获取log文件的token
    token_data = {'filePath': 'log', 'jobId': args.job_id}

    try:
        token_response = requests.post(
            f"{FILE_TOKEN_API}?accessKey={os.getenv('MATERIALS_ACCESS_KEY')}",
            json=token_data,
        )
        token_response.raise_for_status()
        token_data = token_response.json()
    except requests.exceptions.RequestException:
        pass  # 忽略token获取错误，因为这不是主要功能

    log_token = token_data.get('data', {}).get('token', '')
    log_path = token_data.get('data', {}).get('path', '')
    log_host = token_data.get('data', {}).get('host', '')

    # 构建log文件URL并检查状态
    if log_host and log_path and log_token:
        log_url = f"{log_host}/api/download/{log_path}?token={log_token}"

        log_response = requests.get(log_url, timeout=10)
        status_code = log_response.status_code

        if status_code:
            if status_code == 400:
                logger.error('Warning: Log URL returned 400 Bad Request')
            elif status_code == 200:
                download_file(log_response, 'log')
                logger.info('Download `log` completed successfully')
            else:
                logger.error(f"Log URL returned status code: {status_code}")
    else:
        print('\nIncomplete log information - cannot construct log URL')

    if job_status in ['Running', 'Finished']:
        return

    # 下载结果文件
    if result_url and result_url != 'null':
        logger.info(f"Job Result Downloading to: {args.output}")

        try:
            result_response = requests.get(result_url, stream=True)
            result_response.raise_for_status()
            download_file(result_response, args.output)

            if os.path.exists(args.output) and os.path.getsize(args.output) > 0:
                file_size = os.path.getsize(args.output)
                logger.info(
                    f"Download completed successfully! File size: {file_size} bytes"
                )
            else:
                print("Error: Download failed - file is empty or doesn't exist")
                sys.exit(1)

        except requests.exceptions.RequestException as e:
            print(f"Error: Download failed: {e}")
            sys.exit(1)
    else:
        logger.error('No resultUrl found or resultUrl is empty')
        sys.exit(1)


if __name__ == '__main__':
    main()
