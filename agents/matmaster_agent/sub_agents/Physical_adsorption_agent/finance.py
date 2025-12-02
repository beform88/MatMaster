from agents.matmaster_agent.constant import SKU_MAPPING


async def physical_adsorption_cost_func(tool, args) -> tuple[int, int]:
    """
    Physical Adsorption agent cost function - always returns 0 (free)
    """
    photon_cost = 0
    return photon_cost, SKU_MAPPING['matmaster']
