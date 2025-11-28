from agents.matmaster_agent.constant import SKU_MAPPING


async def nmr_cost_func(tool, args) -> tuple[int, int]:
    """
    NMR agent cost function - always returns 0 (free)
    """
    photon_cost = 0
    return photon_cost, SKU_MAPPING['matmaster']
