#!/usr/bin/env python3
"""
快速测试脚本 - 验证简化后的人类模拟器
"""

from human_simulator import HumanSimulator, GoalTemplates

def test_abacus_nacl_scenario():
    """测试ABACUS NaCl计算场景"""
    print("=" * 60)
    print("测试ABACUS NaCl计算场景")
    print("=" * 60)
    
    # 创建人类模拟器
    simulator = HumanSimulator()
    
    # 设置对话目标
    goal = GoalTemplates.abacus_nacl_calculation()
    simulator.set_goal(goal)
    
    print(f"对话目标: {goal.initial_question}")
    print(f"最大轮次: 5")
    
    # 获取初始问题
    initial_question = simulator.get_initial_question()
    print(f"\n初始问题: {initial_question}")
    
    # 模拟对话过程
    agent_responses = [
        "您好！我可以帮助您使用ABACUS构建NaCl晶胞并进行DFT计算。请确认您需要的晶格常数是5.5 Å吗？",
        "好的，我将为您构建rocksalt型NaCl晶胞。您希望使用什么DFT方法？比如PBE、HSE06等？",
        "请告诉我您希望设置的截断能是多少？通常对于NaCl，建议使用50-60 Ry。",
        "我将为您生成ABACUS输入文件。您希望保存为什么文件名？",
        "完成！我已经为您构建了NaCl晶胞并生成了ABACUS输入文件。您可以开始计算了。"
    ]
    
    for i, agent_message in enumerate(agent_responses):
        print(f"\n[Agent] {agent_message}")
        
        # 生成用户响应
        user_response, should_continue = simulator.generate_response(agent_message)
        print(f"[用户] {user_response}")
        
        if not should_continue:
            print(f"\n[系统] 对话在第{i+1}轮结束")
            break
    
    # 获取对话摘要
    summary = simulator.get_conversation_summary()
    print(f"\n对话摘要:")
    print(f"- 总轮次: {summary['total_turns']}")
    print(f"- 最终状态: {summary['final_state']}")
    print(f"- 耗时: {summary['duration_minutes']:.1f} 分钟")

def test_fcc_copper_scenario():
    """测试FCC铜声子谱场景"""
    print("\n" + "=" * 60)
    print("测试FCC铜声子谱场景")
    print("=" * 60)
    
    # 创建人类模拟器
    simulator = HumanSimulator()
    
    # 设置对话目标
    goal = GoalTemplates.fcc_copper_phonon()
    simulator.set_goal(goal)
    
    print(f"对话目标: {goal.initial_question}")
    
    # 获取初始问题
    initial_question = simulator.get_initial_question()
    print(f"\n初始问题: {initial_question}")
    
    # 模拟对话过程
    agent_responses = [
        "您好！我可以帮助您构建FCC铜结构并计算声子谱。请确认您需要的是面心立方铜结构吗？",
        "好的，我将为您构建FCC铜晶胞。您希望使用什么晶格常数？通常铜的晶格常数约为3.61 Å。",
        "请告诉我您希望使用什么声子计算方法？比如有限位移法或密度泛函微扰理论？",
        "我将为您设置声子计算参数。您希望计算多少个q点？",
        "完成！我已经为您构建了FCC铜结构并设置了声子计算参数。"
    ]
    
    for i, agent_message in enumerate(agent_responses):
        print(f"\n[Agent] {agent_message}")
        
        # 生成用户响应
        user_response, should_continue = simulator.generate_response(agent_message)
        print(f"[用户] {user_response}")
        
        if not should_continue:
            print(f"\n[系统] 对话在第{i+1}轮结束")
            break
    
    # 获取对话摘要
    summary = simulator.get_conversation_summary()
    print(f"\n对话摘要:")
    print(f"- 总轮次: {summary['total_turns']}")
    print(f"- 最终状态: {summary['final_state']}")
    print(f"- 耗时: {summary['duration_minutes']:.1f} 分钟")

def test_band_gap_scenario():
    """测试小带隙结构搜索场景"""
    print("\n" + "=" * 60)
    print("测试小带隙结构搜索场景")
    print("=" * 60)
    
    # 创建人类模拟器
    simulator = HumanSimulator()
    
    # 设置对话目标
    goal = GoalTemplates.band_gap_structures()
    simulator.set_goal(goal)
    
    print(f"对话目标: {goal.initial_question}")
    
    # 获取初始问题
    initial_question = simulator.get_initial_question()
    print(f"\n初始问题: {initial_question}")
    
    # 模拟对话过程
    agent_responses = [
        "您好！我可以帮助您寻找带隙小于0.5eV的结构。请告诉我您希望搜索什么类型的材料？",
        "我将为您搜索候选结构。您希望使用什么计算方法？比如DFT、GW等？",
        "请告诉我您希望搜索的化学空间范围？比如特定元素组合或结构类型？",
        "我将为您筛选出符合条件的结构。您希望获得哪些具体信息？",
        "完成！我已经为您找到了4个带隙小于0.5eV的结构。"
    ]
    
    for i, agent_message in enumerate(agent_responses):
        print(f"\n[Agent] {agent_message}")
        
        # 生成用户响应
        user_response, should_continue = simulator.generate_response(agent_message)
        print(f"[用户] {user_response}")
        
        if not should_continue:
            print(f"\n[系统] 对话在第{i+1}轮结束")
            break
    
    # 获取对话摘要
    summary = simulator.get_conversation_summary()
    print(f"\n对话摘要:")
    print(f"- 总轮次: {summary['total_turns']}")
    print(f"- 最终状态: {summary['final_state']}")
    print(f"- 耗时: {summary['duration_minutes']:.1f} 分钟")

if __name__ == "__main__":
    print("开始快速测试人类模拟器...")
    
    # 测试三个主要场景
    test_abacus_nacl_scenario()
    test_fcc_copper_scenario()
    test_band_gap_scenario()
    
    print("\n" + "=" * 60)
    print("快速测试完成！")
    print("=" * 60)
