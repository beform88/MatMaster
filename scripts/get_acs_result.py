import argparse
import json
import os
import sys

import requests
from dotenv import find_dotenv, load_dotenv
from toolsy.logger import init_colored_logger

from scripts.constant import FILE_TOKEN_API, JOB_DETAIL_API

load_dotenv(find_dotenv())

logger = init_colored_logger(__name__)


def download_file(url, output_path):
    """下载文件并显示进度"""
    response = requests.get(url, stream=True)
    response.raise_for_status()

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


def check_url_status(url):
    """检查URL的HTTP状态码"""
    try:
        response = requests.head(url, timeout=10)  # 使用HEAD方法，只获取头部信息
        return response.status_code
    except requests.exceptions.RequestException as e:
        print(f"Warning: Failed to check URL status: {e}")
        return None


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
    logger.info(f"Fetching job information for ID: {args.job_id}")

    try:
        response = requests.get(
            f"{JOB_DETAIL_API}/{args.job_id}?accessKey={os.getenv('MATERIALS_ACCESS_KEY')}"
        )
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error: Failed to fetch data from API: {e}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        logger.error(f"Error: Failed to parse JSON response: {e}")
        sys.exit(1)

    logger.info(f"\n{json.dumps(data, indent=2, ensure_ascii=False)}")

    # 解析JSON获取resultUrl
    if data.get('code') == 0:
        result_url = data.get('data', {}).get('resultUrl', '')
    elif data.get('code') == 6020:
        logger.error(f"API returned error code: {data.get('code')}")
        sys.exit(-1)
    else:
        result_url = ''
        logger.error(f"API returned error code: {data.get('code')}")

    # 获取log文件的token（可选操作）
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

    logger.info(f"\n{json.dumps(token_data, indent=2)}")

    log_token = token_data.get('data', {}).get('token', '')
    log_path = token_data.get('data', {}).get('path', '')
    log_host = token_data.get('data', {}).get('host', '')

    # 构建log文件URL并检查状态
    if log_host and log_path and log_token:
        log_url = f"{log_host}/api/download/{log_path}?token={log_token}"

        # 检查log URL的状态
        status_code = check_url_status(log_url)
        if status_code:
            if status_code == 400:
                logger.error('Warning: Log URL returned 400 Bad Request')
            elif status_code == 200:
                logger.info(f"\nlog_url: {log_url}")
            else:
                logger.error(f"Log URL returned status code: {status_code}")
    else:
        print('\nIncomplete log information - cannot construct log URL')

    # 下载结果文件
    if result_url and result_url != 'null':
        print(f"\nFound resultUrl: {result_url}")
        print(f"\nDownloading to: {args.output}")

        try:
            download_file(result_url, args.output)

            if os.path.exists(args.output) and os.path.getsize(args.output) > 0:
                file_size = os.path.getsize(args.output)
                print(f"Download completed successfully! File size: {file_size} bytes")
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
