import json
import logging
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from dotenv import find_dotenv, load_dotenv
from litellm import completion

logger = logging.getLogger(__name__)

load_dotenv(find_dotenv())


class ConversationState(Enum):
    """对话状态枚举"""

    INITIAL = 'initial'
    IN_PROGRESS = 'in_progress'
    SATISFIED = 'satisfied'
    TIMEOUT = 'timeout'


@dataclass
class ConversationGoal:
    """对话目标定义"""

    initial_question: str
    expected_outcomes: List[str]
    success_criteria: List[str]


class HumanSimulator:
    """
    简化的人类模拟器 - 用于多轮对话agent评估

    功能：
    1. 模拟真实用户行为
    2. 管理对话目标
    3. 生成上下文相关的响应
    """

    def __init__(self, model: str = 'azure/gpt-4o', max_turn_count=10):
        self.model = model
        self.max_turn_count = max_turn_count
        self.conversation_history: List[Dict[str, Any]] = []
        self.current_state = ConversationState.INITIAL
        self.turn_count = 0
        self.start_time = None
        self.goal: Optional[ConversationGoal] = None

    def set_goal(self, goal: ConversationGoal):
        """设置对话目标"""
        self.goal = goal
        self.current_state = ConversationState.INITIAL
        self.turn_count = 0
        self.start_time = time.time()
        logger.info(f"设置对话目标: {goal.initial_question}")

    def get_initial_question(self) -> str:
        """获取初始问题"""
        if not self.goal:
            raise ValueError('未设置对话目标')
        return self.goal.initial_question

    def generate_response(self, agent_message: str) -> Tuple[str, bool]:
        """
        基于agent的回复生成模拟用户的响应

        Args:
            agent_message: agent的回复内容

        Returns:
            Tuple[str, bool]: (用户响应, 是否继续对话)
        """
        if not self.goal:
            raise ValueError('未设置对话目标')

        self.turn_count += 1
        self.conversation_history.append(
            {'turn': self.turn_count, 'agent': agent_message, 'timestamp': time.time()}
        )

        if self.turn_count >= self.max_turn_count:
            self.current_state = ConversationState.TIMEOUT
            return f'我们已经聊了{self.max_turn_count}轮了，我想结束这个对话。', False

        # 生成用户响应
        if self.turn_count == 1:
            user_response = '好的，请按计划继续。'
            should_continue = True
        else:
            user_response, should_continue = self._generate_user_response(agent_message)

        # 更新对话状态
        if not should_continue:

            self.current_state = ConversationState.SATISFIED

        self.conversation_history.append(
            {'turn': self.turn_count, 'user': user_response, 'timestamp': time.time()}
        )

        return user_response, should_continue

    def _generate_user_response(self, agent_message: str) -> Tuple[str, bool]:
        """生成用户响应的核心逻辑"""

        prompt = self._build_response_prompt(agent_message)

        try:
            response = completion(
                model=self.model,
                messages=[{'role': 'user', 'content': prompt}],
                temperature=1.0,
            )

            result = json.loads(response.choices[0].message.content)
            user_response = result.get('response', '我理解了。')
            should_continue = result.get('continue', True)

            logger.info(
                f"用户响应生成 - 轮次: {self.turn_count}, 继续: {should_continue}"
            )

            return user_response, should_continue

        except Exception as e:
            logger.error(f"生成用户响应失败: {e}")
            return '我理解了，请继续。', True

    def _build_response_prompt(self, agent_message: str) -> str:
        """构建生成用户响应的提示词"""

        return f"""
你是一个模拟人类用户，正在与一个材料计算AI agent进行多轮对话。你的唯一目标是测试agent能否完成你给出的任务。请基于以下信息生成合适的响应：

## 任务目标：
- 目标任务: {self.goal.initial_question}
- 期望结果: {', '.join(self.goal.expected_outcomes)}
- 成功标准: {', '.join(self.goal.success_criteria)}

## 当前状态：
- 对话轮次: {self.turn_count}/{self.max_turn_count}

- Agent最新回复：
{agent_message}

## 对话规则：

- 输出格式
请严格按照以下JSON格式回复：
{{
  "response": "你的回复内容",
  "continue": true/false // 是否继续对话
}}

- 任务完成的判定原则
   1.如果 agent 只是给出 计划、思路、步骤、方法说明，你要认为 任务尚未完成，并要求 agent 继续。
   2.只有当 agent 给出 符合任务要求的最终输出（例如具体数值、结果表格、结论说明等），你才认为任务完成。
   3.任何时候都不要把“计划/步骤”误判为“结果”
   4.如果 agent 明确表示当前任务无法完成，你要礼貌地结束对话（"continue": false）。
   5.如果是第一轮回复，请要求 agent 继续。

- 行为规范
    1.只围绕最初任务进行，不扩展。回答要尽可能简洁明了，避免冗长。
    2.如果结果不完整/模糊，要求继续。
    3.如果结果完整且满足任务目标，结束对话（"continue": false）
    4.严禁提供虚构的信息，不能假装上传文件或代码。
    5.如果 agent 在询问具体参数或设置，提供简洁明确的回答。
    6.agent只能以文本形式回复，要求agent返回的结果也必须是文本形式，不能是图片、文件，但可以是文件URL。
    7.不要提出超出agent能力范围的要求，agent没有将结果整理成csv等格式的能力，也没有运行python代码的能力。
    8.你是模拟用户，没有检索网页或获取API权限的能力，禁止向agent提供URL或是API-key等信息。
    9.agent只能使用内置工具、初始问题中用户提供的数据、内置工具获取的数据来完成任务，不能使用或要求你使用任何外部工具。如果发现agent试图使用外部工具，或要求用户在本地运行/提供新数据，请拒绝并提醒agent只能使用内置工具完成任务。

现在请给出合理的回答
"""

    def get_bohr_results(
        self, agent_message: str, job_id: List[str]
    ) -> Tuple[str, bool]:
        """
        基于agent的回复生成模拟用户的响应

        Args:
            agent_message: agent的回复内容
            job_id: job_id

        Returns:
            Tuple[str, bool]: (用户响应, 是否继续对话)
        """
        if not self.goal:
            raise ValueError('未设置对话目标')

        self.turn_count += 1
        self.conversation_history.append(
            {'turn': self.turn_count, 'agent': agent_message, 'timestamp': time.time()}
        )

        # 生成用户响应
        user_response = f'查看id为{job_id}的任务结果'
        should_continue = True

        # 更新对话状态
        if not should_continue:
            self.current_state = ConversationState.SATISFIED

        self.conversation_history.append(
            {'turn': self.turn_count, 'user': user_response, 'timestamp': time.time()}
        )

        return user_response, should_continue

    def get_conversation_summary(self) -> Dict[str, Any]:
        """获取对话摘要"""
        return {
            'goal': self.goal.initial_question if self.goal else None,
            'total_turns': self.turn_count,
            'final_state': self.current_state.value,
            'duration_minutes': (
                ((time.time() - self.start_time) / 60) if self.start_time else 0
            ),
            'conversation_history': self.conversation_history,
        }

    def get_last_user_response(self) -> str:
        """获取最后的用户响应"""
        if not self.conversation_history:
            return self.get_initial_question()

        # 查找最后一个用户响应
        for entry in reversed(self.conversation_history):
            if 'user' in entry:
                return entry['user']

        # 如果没有找到用户响应，返回初始问题
        return self.get_initial_question()
