from enum import Enum

MrDice_Agent_Name = 'MrDice_agent'


class MrDiceTargetAgentEnum(Enum):
    """MrDice 子代理枚举"""

    BOHRIUM_PUBLIC_AGENT = 'bohrium_public_agent'
    OPTIMADE_AGENT = 'optimade_agent'
    OPENLAM_AGENT = 'openlam_agent'
    MOFDB_AGENT = 'mofdb_agent'
