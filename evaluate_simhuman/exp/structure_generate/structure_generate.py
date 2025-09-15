import asyncio
import os
import sys

from evaluate.base import test_with_adk_agent

# 添加agents目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'agents'))

# 使用示例
if __name__ == '__main__':
    # 运行测试
    print('🚀 人类模拟器启动')
    print('=' * 50)

    asyncio.run(test_with_adk_agent("structure_generate.json"))
