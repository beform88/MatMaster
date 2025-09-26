import argparse
import json
import os
import sys

import requests
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())


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

    print()  # 换行


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

    api_url = f"https://openapi.test.dp.tech/openapi/v1/sandbox/job/{args.job_id}?accessKey={os.getenv('MATERIALS_ACCESS_KEY')}"

    # 删除已存在的输出文件
    if os.path.exists(args.output):
        os.remove(args.output)

    # 调用API获取job信息
    print(f"Fetching job information for ID: {args.job_id}")

    try:
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error: Failed to fetch data from API: {e}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Failed to parse JSON response: {e}")
        sys.exit(1)

    print(f"\n{json.dumps(data, indent=2, ensure_ascii=False)}\n")

    # 解析JSON获取resultUrl
    if data.get('code') == 0:
        result_url = data.get('data', {}).get('resultUrl', '')
    else:
        result_url = ''
        print(f"API returned error code: {data.get('code')}")

    # 获取log文件的token（可选操作）
    token_url = 'https://openapi.test.dp.tech/openapi/v1/sandbox/job/file/token?accessKey=7c4d4edd67284c2e9c62d8b9350baaa4'
    token_data = {'filePath': 'log', 'jobId': args.job_id}

    try:
        token_response = requests.post(token_url, json=token_data)
        token_response.raise_for_status()
        token_data = token_response.json()
    except requests.exceptions.RequestException:
        pass  # 忽略token获取错误，因为这不是主要功能

    print(f"\n{json.dumps(token_data, indent=2)}\n")

    log_token = token_data.get('data', {}).get('token', '')
    log_path = token_data.get('data', {}).get('path', '')
    log_host = token_data.get('data', {}).get('host', '')

    print(f"\nlog_path: {log_host}/api/download/{log_path}?token={log_token}\n")

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
        print('No resultUrl found or resultUrl is empty')
        sys.exit(1)


if __name__ == '__main__':
    main()
