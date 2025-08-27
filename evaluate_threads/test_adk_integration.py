#!/usr/bin/env python3
"""
测试与ADK agent的集成
"""

import asyncio
import sys
import os

# 添加agents目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'agents'))

def test_human_simulator_basic():
    """测试人类模拟器的基本功能"""
    print("🧪 测试人类模拟器基本功能")
    
    from human_simulator import HumanSimulator, GoalTemplates
    
    # 创建模拟器
    simulator = HumanSimulator()
    
    # 设置目标
    goal = GoalTemplates.abacus_nacl_calculation()
    simulator.set_goal(goal)
    
    print(f"✅ 初始问题: {simulator.get_initial_question()}")
    
    # 测试响应生成
    agent_message = "您好！我可以帮助您使用ABACUS构建NaCl晶胞。"
    user_response, should_continue = simulator.generate_response(agent_message)
    
    print(f"✅ 用户响应: {user_response}")
    print(f"✅ 继续对话: {should_continue}")
    
    # 测试获取最后响应
    last_response = simulator.get_last_user_response()
    print(f"✅ 最后响应: {last_response}")
    
    # 测试摘要
    summary = simulator.get_conversation_summary()
    print(f"✅ 对话摘要: {summary['total_turns']} 轮, {summary['final_state']}")

def test_adk_import():
    """测试ADK模块导入"""
    print("\n🧪 测试ADK模块导入")
    
    try:
        from google.adk import Runner
        from google.adk.agents import RunConfig
        from google.adk.agents.run_config import StreamingMode
        from google.adk.sessions import DatabaseSessionService
        from google.genai import types
        
        from matmaster_agent.agent import root_agent
        from matmaster_agent.constant import DBUrl
        from matmaster_agent.logger import logger
        
        print("✅ ADK模块导入成功")
        return True
    except ImportError as e:
        print(f"❌ ADK模块导入失败: {e}")
        return False

async def test_adk_agent_simple():
    """简单测试ADK agent"""
    print("\n🧪 简单测试ADK agent")
    
    if not test_adk_import():
        print("⚠️  跳过ADK agent测试")
        return
    
    try:
        from google.adk import Runner
        from google.adk.agents import RunConfig
        from google.adk.agents.run_config import StreamingMode
        from google.adk.sessions import DatabaseSessionService
        from google.genai import types
        
        from matmaster_agent.agent import root_agent
        from matmaster_agent.constant import DBUrl
        from matmaster_agent.logger import logger
        
        # 初始化ADK agent
        session_service = DatabaseSessionService(db_url=DBUrl)
        session = await session_service.create_session(
            app_name="matmaster_agent",
            user_id="test_user",
        )
        
        runner = Runner(
            app_name="matmaster_agent",
            agent=root_agent,
            session_service=session_service
        )
        
        # 简单测试
        test_message = "Hello, can you help me with material calculations?"
        content = types.Content(role="user", parts=[types.Part(text=test_message)])
        
        print(f"📤 发送消息: {test_message}")
        
        events = runner.run_async(
            user_id=session.user_id,
            session_id=session.id,
            new_message=content,
            run_config=RunConfig(streaming_mode=StreamingMode.SSE)
        )
        
        response = ""
        async for event in events:
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        response += part.text
        
        print(f"📥 收到响应: {response[:100]}...")
        print("✅ ADK agent测试成功")
        
        await runner.close()
        
    except Exception as e:
        print(f"❌ ADK agent测试失败: {e}")

def main():
    """主测试函数"""
    print("🚀 开始集成测试")
    print("=" * 50)
    
    # 测试人类模拟器
    test_human_simulator_basic()
    
    # 测试ADK导入
    adk_available = test_adk_import()
    
    # 测试ADK agent
    if adk_available:
        asyncio.run(test_adk_agent_simple())
    
    print("\n" + "=" * 50)
    print("🎉 集成测试完成")
    
    if adk_available:
        print("✅ 所有测试通过，可以运行完整的多轮对话测试")
        print("💡 运行命令: python human_simulator.py")
    else:
        print("⚠️  ADK环境不可用，将使用模拟agent进行测试")
        print("💡 运行命令: python human_simulator.py")

if __name__ == "__main__":
    main()
