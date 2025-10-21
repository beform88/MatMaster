import os
import re
import sys
from collections import Counter

import pandas as pd


def extract_function_calls_with_count(csv_file_path):
    """
    从CSV文件的message列中提取函数调用名称及其出现次数

    参数:
    csv_file_path (str): CSV文件路径

    返回:
    list: 包含(函数名, 次数)的元组列表，按次数降序排列
    """
    try:
        # 检查文件是否存在
        if not os.path.exists(csv_file_path):
            print(f"错误: 文件 {csv_file_path} 不存在")
            return []

        # 读取CSV文件
        df = pd.read_csv(csv_file_path)

        # 检查message列是否存在
        if 'message' not in df.columns:
            print("错误: CSV文件中没有'message'列")
            return []

        function_counter = Counter()

        # 正则表达式匹配函数调用模式
        # 匹配类似 run_piloteye({...}) 这样的结构
        pattern = r'(\w+)\s*\(\s*\{'

        for message in df['message']:
            if pd.isna(message):
                continue

            # 在message中查找匹配的函数调用
            matches = re.findall(pattern, str(message))
            function_counter.update(matches)

        # 按次数降序排序
        sorted_functions = sorted(
            function_counter.items(), key=lambda x: x[1], reverse=True
        )
        return sorted_functions

    except Exception as e:
        print(f"读取文件时出错: {e}")
        return []


def main():
    """主函数，处理命令行参数"""
    # 检查是否提供了文件路径参数
    if len(sys.argv) < 2:
        print('用法: python script.py <csv文件路径>')
        print('示例: python script.py /path/to/your/file.csv')
        sys.exit(1)

    # 获取第一个参数作为文件路径
    csv_file_path = sys.argv[1]

    # 提取函数调用名称及次数
    functions_with_count = extract_function_calls_with_count(csv_file_path)

    if functions_with_count:
        print('函数调用统计 (按次数降序排序):')
        print('-' * 40)
        for i, (func_name, count) in enumerate(functions_with_count, 1):
            print(f"{i:2d}. {func_name:<20} 出现次数: {count}")

        # 输出总计
        total_calls = sum(count for _, count in functions_with_count)
        print('-' * 40)
        print(f"总计: {len(functions_with_count)} 个不同的函数, {total_calls} 次调用")
    else:
        print('未找到任何函数调用')


if __name__ == '__main__':
    main()
