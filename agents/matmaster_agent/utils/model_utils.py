from pydantic import BaseModel, create_model


def create_transfer_check_model(agent_type):
    """动态创建具有特定 agent 类型的 TransferCheck 模型"""
    return create_model(
        'DynamicTransferCheck',
        is_transfer=(bool, ...),
        target_agent=(agent_type, ...),
        reason=(str, ...),
        __base__=BaseModel,
    )
