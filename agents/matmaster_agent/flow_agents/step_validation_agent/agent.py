from agents.matmaster_agent.core_agents.base_agents.schema_agent import (
    DisallowTransferAndContentLimitSchemaAgent,
)
from agents.matmaster_agent.flow_agents.step_validation_agent.prompt import (
    STEP_VALIDATION_INSTRUCTION,
)
from agents.matmaster_agent.flow_agents.step_validation_agent.schema import (
    StepValidationSchema,
)
from agents.matmaster_agent.llm_config import MatMasterLlmConfig


class StepValidationAgent(DisallowTransferAndContentLimitSchemaAgent):
    def __init__(self, **kwargs):
        super().__init__(
            name='step_validation_agent',
            model=MatMasterLlmConfig.tool_schema_model,
            description='校验步骤执行结果是否合理',
            instruction=STEP_VALIDATION_INSTRUCTION,
            output_schema=StepValidationSchema,
            **kwargs,
        )
