"""
简化的人类模拟器测试脚本
演示如何使用人类模拟器进行多轮对话agent评估
"""

import json
import time
from human_simulator import (
    HumanSimulator,
    GoalTemplates,
    ConversationGoal
)

def simulate_conversation_with_agent():
    """模拟与agent的对话过程"""

    # 创建人类模拟器
    simulator = HumanSimulator()

    # 设置对话目标
    goal = GoalTemplates.abacus_nacl_calculation()
    simulator.set_goal(goal)

    print('=' * 60)
    print('多轮对话Agent评估测试')
    print('=' * 60)
    print(f"对话目标: {goal.initial_question}")
    print(f"最大轮次: 5")
    print('=' * 60)

    # 获取初始问题
    initial_question = simulator.get_initial_question()
    print(f"\n[用户] {initial_question}")

    # 模拟agent的回复（这里用简单的回复来演示）
    agent_responses = [
        '您好！我可以帮助您使用ABACUS构建NaCl晶胞并进行DFT计算。请确认您需要的晶格常数是5.5 Å吗？',
        '好的，我将为您构建rocksalt型NaCl晶胞。您希望使用什么DFT方法？比如PBE、HSE06等？',
        '请告诉我您希望设置的截断能是多少？通常对于NaCl，建议使用50-60 Ry。',
        '我将为您生成ABACUS输入文件。您希望保存为什么文件名？',
        '完成！我已经为您构建了NaCl晶胞并生成了ABACUS输入文件。您可以开始计算了。'
    ]

    conversation_ended = False
    turn = 0

    while not conversation_ended and turn < len(agent_responses):
        # 模拟agent回复
        agent_message = agent_responses[turn]
        print(f"\n[Agent] {agent_message}")

        # 生成用户响应
        user_response, should_continue = simulator.generate_response(agent_message)
        print(f"\n[用户] {user_response}")

        if not should_continue:
            conversation_ended = True
            print('\n[系统] 用户决定结束对话')
            break

        turn += 1
        time.sleep(1)  # 模拟真实对话的延迟

    # 获取对话摘要
    summary = simulator.get_conversation_summary()
    print(f"\n对话摘要:")
    print(f"- 总轮次: {summary['total_turns']}")
    print(f"- 最终状态: {summary['final_state']}")
    print(f"- 耗时: {summary['duration_minutes']:.1f} 分钟")

def test_different_scenarios():
    """测试不同的对话场景"""

    scenarios = [
        {
            'name': 'ABACUS NaCl计算',
            'goal': GoalTemplates.abacus_nacl_calculation()
        },
        {
            'name': 'FCC铜声子谱',
            'goal': GoalTemplates.fcc_copper_phonon()
        },
        {
            'name': '小带隙结构搜索',
            'goal': GoalTemplates.band_gap_structures()
        }
    ]

    for scenario in scenarios:
        print(f"\n{'='*20} {scenario['name']} {'='*20}")

        simulator = HumanSimulator()
        simulator.set_goal(scenario['goal'])

        print(f"初始问题: {simulator.get_initial_question()}")

def create_custom_goal():
    """创建自定义对话目标"""

    custom_goal = ConversationGoal(
        initial_question='我想使用VASP计算石墨烯的能带结构',
        expected_outcomes=['构建石墨烯结构', '计算能带结构', '获得能带图'],
        success_criteria=['结构构建完成', '能带计算完成', '获得能带图']
    )

    print(f"\n{'='*20} 自定义场景 {'='*20}")
    print(f"目标: {custom_goal.initial_question}")
    print(f"期望结果: {', '.join(custom_goal.expected_outcomes)}")

if __name__ == '__main__':
    print('人类模拟器测试开始...')

    # 测试基本对话场景
    simulate_conversation_with_agent()

    # 测试不同场景
    test_different_scenarios()

    # 测试自定义目标
    create_custom_goal()

    print('\n测试完成！')
