# 简化的人类模拟器

这是一个简化的人类模拟器，用于多轮对话agent评估，专注于材料计算领域。

## 系统概述

传统的单轮评估方法无法有效评估agent在多轮对话中的表现。本系统通过引入"人类模拟器"来解决这个问题：
- 设定明确的对话目标和成功标准
- 动态生成上下文相关的用户响应
- 限制最多5轮对话
- 专注于材料计算相关的问题

## 核心组件

### 1. HumanSimulator (人类模拟器)

`human_simulator.py` 中的核心类，负责：
- 模拟真实用户行为
- 管理对话目标
- 生成上下文相关的响应
- 限制最多5轮对话

#### 主要功能：
- `set_goal()`: 设置对话目标
- `get_initial_question()`: 获取初始问题
- `generate_response()`: 基于agent回复生成用户响应
- `get_conversation_summary()`: 获取对话摘要

### 2. 对话目标模板 (GoalTemplates)

预定义的对话目标模板：
- `abacus_nacl_calculation()`: ABACUS NaCl DFT计算
- `fcc_copper_phonon()`: FCC铜声子谱计算
- `band_gap_structures()`: 小带隙结构搜索

## 使用方法

### 1. 基本使用

```python
from human_simulator import HumanSimulator, GoalTemplates

# 创建人类模拟器
simulator = HumanSimulator()

# 设置对话目标
goal = GoalTemplates.abacus_nacl_calculation()
simulator.set_goal(goal)

# 获取初始问题
initial_question = simulator.get_initial_question()
print(f"初始问题: {initial_question}")

# 模拟对话过程
agent_message = "您好！我可以帮助您使用ABACUS构建NaCl晶胞。"
user_response, should_continue = simulator.generate_response(agent_message)
print(f"用户响应: {user_response}")
```

### 2. 与ADK Agent集成

```python
# 在human_simulator.py的main函数中已经包含了完整的ADK集成示例
# 运行以下命令开始多轮对话测试：

# 检查ADK环境
python test_adk_integration.py

# 运行完整测试（自动检测ADK环境）
python human_simulator.py
```

### 3. 创建自定义场景

```python
from human_simulator import ConversationGoal

# 创建自定义对话目标
custom_goal = ConversationGoal(
    initial_question="我想使用VASP计算石墨烯的能带结构",
    expected_outcomes=["构建石墨烯结构", "计算能带结构", "获得能带图"],
    success_criteria=["结构构建完成", "能带计算完成", "获得能带图"]
)
```

## 配置说明

### 环境变量

确保设置以下环境变量：
```bash
# Azure OpenAI配置
AZURE_OPENAI_API_KEY=your_api_key
AZURE_OPENAI_ENDPOINT=your_endpoint
AZURE_OPENAI_API_VERSION=2024-02-15-preview

# 其他LLM配置（如需要）
OPENAI_API_KEY=your_openai_key
```

### 模型配置

支持多种LLM模型：
- `azure/gpt-4o`: Azure OpenAI GPT-4o
- `gpt-4o`: OpenAI GPT-4o
- `claude-3-opus-20240229`: Anthropic Claude

## 测试脚本

### 运行基本测试

```bash
cd evaluate_threads
python test_human_simulator.py
```

### 运行快速测试

```bash
cd evaluate_threads
python quick_test.py
```

### 运行ADK集成测试

```bash
cd evaluate_threads
python test_adk_integration.py
```

### 运行完整的多轮对话测试

```bash
cd evaluate_threads
python human_simulator.py
```

## 输出结果

### 对话摘要

```json
{
  "goal": "我希望使用ABACUS对NaCl进行DFT计算，请帮我构建一个NaCl的晶胞",
  "total_turns": 5,
  "final_state": "satisfied",
  "duration_minutes": 8.5,
  "conversation_history": [...]
}
```

## 扩展和定制

### 1. 添加新的对话目标模板

```python
class GoalTemplates:
    @staticmethod
    def custom_goal() -> ConversationGoal:
        return ConversationGoal(
            initial_question="您的初始问题",
            expected_outcomes=["期望结果1", "期望结果2"],
            success_criteria=["成功标准1", "成功标准2"]
        )
```

### 4. 集成真实Agent API

```python
# 在您的代码中调用真实的agent API
async def simulate_conversation(simulator, agent_api_endpoint):
    initial_question = simulator.get_initial_question()
    
    # 调用真实agent API
    response = await call_agent_api(agent_api_endpoint, initial_question)
    
    # 生成用户响应
    user_response, should_continue = simulator.generate_response(response)
    
    # 继续对话...
```

## 重要限制

1. **对话轮次**: 最多5轮对话
2. **专注性**: 专注于材料计算相关的问题，不要偏离主题
3. **简洁性**: 除首轮对话外，其他轮次要简单回答agent的问题，不要发散
4. **目标导向**: 如果agent已经提供了所需的信息或完成了任务，可以结束对话

## 故障排除

### 常见问题

1. **API调用失败**: 检查环境变量和网络连接
2. **JSON解析错误**: 确保LLM返回格式正确的JSON
3. **对话轮次超限**: 系统会自动在第5轮后结束对话

### 调试模式

启用详细日志：
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 总结

这个简化的人类模拟器专注于材料计算领域，具有以下特点：
- 限制对话轮次为5轮
- 使用具体的材料计算场景
- 优化用户响应逻辑，避免发散
- 保持系统的简洁性和易用性
