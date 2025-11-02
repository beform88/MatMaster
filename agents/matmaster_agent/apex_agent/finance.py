import logging
from typing import Any, Dict, Optional

from agents.matmaster_agent.constant import SKU_MAPPING
from agents.matmaster_agent.services.structure import get_info_by_path

logger = logging.getLogger(__name__)


def _get_structure_format(structure_url: str) -> str:
    """
    根据文件扩展名判断结构文件格式

    Args:
        structure_url: 结构文件的URL或路径

    Returns:
        文件格式字符串 (cif, poscar, stru, xyz等)
    """
    url_lower = structure_url.lower()

    if url_lower.endswith('.cif'):
        return 'cif'
    elif url_lower.endswith(('.poscar', '.vasp', '.contcar')):
        return 'poscar'
    elif url_lower.endswith(('.stru', '.abacus')):
        return 'stru'
    elif url_lower.endswith('.xyz'):
        return 'xyz'
    else:
        # 默认尝试poscar格式
        logger.warning(f"无法识别文件格式，默认使用poscar: {structure_url}")
        return 'poscar'


async def _get_structure_info(structure_url: str) -> Optional[Dict[str, Any]]:
    """
    获取结构文件的详细信息

    Args:
        structure_url: 结构文件的URL或路径

    Returns:
        包含原子类型、原子数量、晶胞信息的字典，失败返回None
    """
    try:
        # 判断文件格式
        file_format = _get_structure_format(structure_url)

        # 调用服务获取结构信息
        structure_info = await get_info_by_path(structure_url, file_format)

        if structure_info and 'data' in structure_info:
            data = structure_info['data']
            logger.info(f"成功获取结构信息: {structure_info}")
            return {
                'atom_types': data.get('elements', []),  # 原子类型列表
                'atom_counts': data.get('elementCount', {}),  # 各原子数量
                'total_atoms': sum(data.get('elementCount', {}).values()),  # 总原子数
                'lattice': data.get('lattice', {}),  # 晶胞参数
                'lattice_volume': data.get('volume', 0.0),  # 晶胞体积
            }
        else:
            logger.error(f"获取结构信息失败: {structure_info}")
            return None

    except Exception as e:
        logger.error(f"获取结构信息时出错: {str(e)}")
        return None


def _calculate_cost_by_structure(
    tool_name: str, atom_types: list, total_atoms: int, lattice_volume: float
) -> int:
    """
    根据结构信息和计算类型计算费用

    Args:
        tool_name: 工具名称
        atom_types: 原子类型列表
        total_atoms: 总原子数
        lattice_volume: 晶胞体积

    Returns:
        计算费用（photon）
    """
    # 基础费用（根据计算类型）
    base_costs = {
        'apex_calculate_vacancy': 100,
        'apex_calculate_interstitial': 100,
        'apex_calculate_elastic': 150,
        'apex_calculate_surface': 500,
        'apex_calculate_eos': 100,
        'apex_calculate_phonon': 300,
        'apex_calculate_gamma': 150,
        'apex_optimize_structure': 80,
    }

    base_cost = base_costs.get(tool_name, 100)

    # 根据原子数量调整费用
    # 原子数越多，计算量越大
    if total_atoms <= 10:
        atom_factor = 1.0
    elif total_atoms <= 30:
        atom_factor = 1.5
    elif total_atoms <= 50:
        atom_factor = 2.0
    elif total_atoms <= 100:
        atom_factor = 3.0
    else:
        atom_factor = 4.0

    # 根据元素种类调整费用
    # 元素种类越多，计算复杂度越高
    element_count = len(atom_types)
    if element_count <= 1:
        element_factor = 1.0
    elif element_count == 2:
        element_factor = 1.2
    elif element_count == 3:
        element_factor = 1.4
    else:
        element_factor = 1.6

    # 计算最终费用
    final_cost = int(base_cost * atom_factor * element_factor)

    logger.info(
        f"费用计算: 工具={tool_name}, 基础={base_cost}, "
        f"原子数={total_atoms}, 原子系数={atom_factor}, "
        f"元素数={element_count}, 元素系数={element_factor}, "
        f"最终费用={final_cost}"
    )

    return final_cost


async def apex_cost_func(tool, args) -> tuple[int, int]:
    """
    APEX计算费用函数

    Args:
        tool: 工具对象
        args: 工具参数字典，包含structure_file等

    Returns:
        (photon费用, SKU_ID)元组
    """
    photon_cost = 0

    try:
        # 获取结构文件URL
        structure_url = args.get('structure_file')

        if not structure_url:
            logger.warning('未提供结构文件URL，使用默认费用')
            # 使用默认费用
            default_costs = {
                'apex_calculate_vacancy': 200,
                'apex_calculate_interstitial': 200,
                'apex_calculate_elastic': 300,
                'apex_calculate_surface': 1000,
                'apex_calculate_eos': 200,
                'apex_calculate_phonon': 500,
                'apex_calculate_gamma': 300,
                'apex_optimize_structure': 150,
            }
            photon_cost = default_costs.get(tool.name, 200)
        else:
            # 获取结构信息
            structure_info = await _get_structure_info(structure_url)

            if structure_info:
                # 根据结构信息计算费用
                photon_cost = _calculate_cost_by_structure(
                    tool.name,
                    structure_info['atom_types'],
                    structure_info['total_atoms'],
                    structure_info['lattice_volume'],
                )
            else:
                # 无法获取结构信息，使用默认费用
                logger.warning('无法获取结构信息，使用默认费用')
                default_costs = {
                    'apex_calculate_vacancy': 200,
                    'apex_calculate_interstitial': 200,
                    'apex_calculate_elastic': 300,
                    'apex_calculate_surface': 1000,
                    'apex_calculate_eos': 200,
                    'apex_calculate_phonon': 500,
                    'apex_calculate_gamma': 300,
                    'apex_optimize_structure': 150,
                }
                photon_cost = default_costs.get(tool.name, 200)

    except Exception as e:
        logger.error(f"计算费用时出错: {str(e)}")
        # 发生错误时使用默认费用
        default_costs = {
            'apex_calculate_vacancy': 200,
            'apex_calculate_interstitial': 200,
            'apex_calculate_elastic': 300,
            'apex_calculate_surface': 1000,
            'apex_calculate_eos': 200,
            'apex_calculate_phonon': 500,
            'apex_calculate_gamma': 300,
            'apex_optimize_structure': 150,
        }
        photon_cost = default_costs.get(tool.name, 200)

    return photon_cost, SKU_MAPPING['matmaster']
