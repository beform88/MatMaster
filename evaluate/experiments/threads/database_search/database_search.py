import asyncio

from evaluate.base.evaluation import evaluation_threads_task

if __name__ == '__main__':
    # 运行测试
    print('🚀 人类模拟器启动')
    print('=' * 50)

    asyncio.run(evaluation_threads_task("database_search.json", max_turn_count=5))
