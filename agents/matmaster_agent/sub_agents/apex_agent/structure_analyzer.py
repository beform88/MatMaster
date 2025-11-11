"""
APEX结构分析模块
用于分析材料结构的原子数量、晶胞大小等信息，为费用计算提供依据
"""

import logging
import math
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class StructureAnalyzer:
    """结构分析器，用于分析材料结构特征"""

    # 机器成本配置（元/小时）
    MACHINE_COST_SMALL = 2.56  # 原子数 < 200
    MACHINE_COST_LARGE = 5.12  # 原子数 >= 200

    # 基准结构：Cu4 (4个原子，晶胞3.6x3.6x3.6 Å³)
    REFERENCE_ATOMS = 4
    REFERENCE_CELL_SIZE = 3.6

    # 真空层阈值：如果晶胞体积 > 原子占据体积的130%，则视为有显著真空层
    VACUUM_THRESHOLD = 1.3

    def __init__(self, structure_info: Dict):
        """
        初始化结构分析器

        Args:
            structure_info: 从services.structure.get_info_by_path获取的结构信息
        """
        self.structure_info = structure_info
        self.atom_types = structure_info.get('atom_types', [])
        self.atom_counts = structure_info.get('atom_counts', {})
        self.total_atoms = structure_info.get('total_atoms', 0)
        self.lattice = structure_info.get('lattice', {})
        self.lattice_volume = structure_info.get('lattice_volume', 0.0)

        # 计算有效原子数（考虑真空层）
        self.effective_atoms = self._calculate_effective_atoms()

    def _calculate_effective_atoms(self) -> int:
        """
        计算有效原子数（考虑晶胞中的真空层）

        如果晶胞体积显著大于原子占据体积，说明存在真空层，
        需要将原子数乘以2来反映实际计算量

        Returns:
            有效原子数
        """
        try:
            # 估算原子占据的体积
            # 假设每个原子占据约10 Å³的空间（粗略估计）
            estimated_atom_volume = self.total_atoms * 10.0

            # 计算体积比
            if estimated_atom_volume > 0:
                volume_ratio = self.lattice_volume / estimated_atom_volume
                logger.info(
                    f"晶胞体积: {self.lattice_volume:.2f} Ų, "
                    f"估算原子体积: {estimated_atom_volume:.2f} Ų, "
                    f"体积比: {volume_ratio:.2f}"
                )

                # 如果晶胞体积 > 原子体积的130%，说明有显著真空层
                if volume_ratio > self.VACUUM_THRESHOLD:
                    effective_atoms = int(self.total_atoms * 2)
                    logger.info(
                        f"检测到显著真空层，有效原子数: {self.total_atoms} -> {effective_atoms}"
                    )
                    return effective_atoms

            return self.total_atoms

        except Exception as e:
            logger.error(f"计算有效原子数时出错: {str(e)}")
            return self.total_atoms

    def get_element_count(self) -> int:
        """获取元素种类数量"""
        return len(self.atom_types)

    def is_multi_element(self) -> bool:
        """判断是否为多元素体系"""
        return self.get_element_count() > 1

    def get_machine_cost_per_hour(self) -> float:
        """
        获取机器成本（元/小时）

        Returns:
            机器成本
        """
        if self.effective_atoms < 200:
            return self.MACHINE_COST_SMALL
        else:
            return self.MACHINE_COST_LARGE

    def estimate_time_scaling_factor(self) -> float:
        """
        估算时间缩放因子（相对于Cu4基准结构）

        单元素: 按原子数比例1:1.5逐步提升
        多元素: 按1:2比例提升

        Returns:
            时间缩放因子
        """
        atom_ratio = self.effective_atoms / self.REFERENCE_ATOMS

        # 所有体系统一采用 1:1 比例缩放
        scaling_factor = atom_ratio**1.0

        logger.info(
            f"时间缩放因子: {scaling_factor:.2f} "
            f"(有效原子数: {self.effective_atoms}, "
            f"元素种类: {self.get_element_count()})"
        )

        return scaling_factor

    def get_structure_summary(self) -> str:
        """获取结构摘要信息"""
        return (
            f"原子数: {self.total_atoms}, "
            f"有效原子数: {self.effective_atoms}, "
            f"元素种类: {self.get_element_count()} ({', '.join(self.atom_types)}), "
            f"晶胞体积: {self.lattice_volume:.2f} Ų"
        )


SURFACE_STRUCTURE_BLOCK_MESSAGE = (
    'The structure contains vacuum layers or adsorbates. Please run a geometry '
    'optimization first; '
    'Surface calculations work best with the minimal bulk unit cell.'
)


def _vector_length(vector: List[float]) -> float:
    return (vector[0] ** 2 + vector[1] ** 2 + vector[2] ** 2) ** 0.5


def _unit_vector(vector: List[float]) -> List[float]:
    length = _vector_length(vector)
    if length == 0:
        return [0.0, 0.0, 0.0]
    return [component / length for component in vector]


def _project(u: List[float], point: List[float]) -> float:
    return point[0] * u[0] + point[1] * u[1] + point[2] * u[2]


_ATOMIC_RADIUS: Dict[str, float] = {
    'H': 0.31,
    'C': 0.76,
    'N': 0.71,
    'O': 0.66,
    'F': 0.57,
    'P': 1.07,
    'S': 1.05,
    'Cl': 1.02,
    'Br': 1.20,
    'I': 1.39,
    'Cu': 1.28,
    'Ag': 1.34,
    'Au': 1.44,
    'Ni': 1.24,
    'Co': 1.25,
    'Fe': 1.24,
    'Mn': 1.21,
    'Cr': 1.18,
    'V': 1.22,
    'Ti': 1.47,
    'Zr': 1.60,
    'Hf': 1.58,
    'Nb': 1.64,
    'Ta': 1.70,
    'Mo': 1.54,
    'W': 1.62,
    'Pt': 1.36,
    'Pd': 1.39,
    'Rh': 1.34,
    'Ru': 1.34,
    'Re': 1.51,
    'Al': 1.21,
    'Ga': 1.22,
    'In': 1.42,
    'Sn': 1.39,
    'Pb': 1.44,
    'Si': 1.11,
    'Ge': 1.20,
    'Li': 1.28,
    'Na': 1.66,
    'K': 2.03,
    'Rb': 2.16,
    'Cs': 2.35,
    'Mg': 1.30,
    'Ca': 1.74,
    'Sr': 1.91,
    'Ba': 1.96,
}


def _normalize_symbol(symbol: str) -> str:
    if not symbol:
        return 'X'
    symbol = symbol.strip()
    if not symbol:
        return 'X'
    return symbol[0].upper() + symbol[1:].lower()


def _pair_bond_cut(sym_i: str, sym_j: str, default: float = 1.9) -> float:
    si = _normalize_symbol(sym_i)
    sj = _normalize_symbol(sym_j)
    ri = _ATOMIC_RADIUS.get(si)
    rj = _ATOMIC_RADIUS.get(sj)
    if ri and rj:
        return max(default, 1.1 * (ri + rj))
    if ri and not rj:
        return max(default, 1.1 * (ri + 1.0))
    if rj and not ri:
        return max(default, 1.1 * (rj + 1.0))
    return default


def _build_components(
    positions: List[List[float]],
    species: Optional[List[str]] = None,
    bond_cut: float = 1.9,
) -> List[List[int]]:
    n_atoms = len(positions)
    if n_atoms == 0:
        return []

    adjacency: List[List[int]] = [[] for _ in range(n_atoms)]
    for i in range(n_atoms):
        xi, yi, zi = positions[i]
        sym_i = species[i] if species and i < len(species) else 'X'
        for j in range(i + 1, n_atoms):
            xj, yj, zj = positions[j]
            dx = xi - xj
            dy = yi - yj
            dz = zi - zj
            d2 = dx * dx + dy * dy + dz * dz
            cutoff = bond_cut
            if species:
                sym_j = species[j] if j < len(species) else 'X'
                cutoff = _pair_bond_cut(sym_i, sym_j, bond_cut)
            if d2 <= cutoff * cutoff:
                adjacency[i].append(j)
                adjacency[j].append(i)

    visited = [False] * n_atoms
    components: List[List[int]] = []
    for atom_idx in range(n_atoms):
        if not visited[atom_idx]:
            stack = [atom_idx]
            visited[atom_idx] = True
            component: List[int] = []
            while stack:
                node = stack.pop()
                component.append(node)
                for neighbor in adjacency[node]:
                    if not visited[neighbor]:
                        visited[neighbor] = True
                        stack.append(neighbor)
            components.append(sorted(component))
    return components


def _component_composition(species: List[str], component: List[int]) -> Dict[str, int]:
    composition: Dict[str, int] = {}
    for idx in component:
        symbol = species[idx] if 0 <= idx < len(species) else 'X'
        composition[symbol] = composition.get(symbol, 0) + 1
    return composition


def _normalize_composition(composition: Dict[str, int]) -> Tuple[Tuple[str, int], ...]:
    return tuple(
        sorted((element, int(count)) for element, count in composition.items())
    )


def _known_adsorbate_set() -> set:
    known: List[Tuple[Tuple[str, int], ...]] = []

    def register(formula: Dict[str, int]) -> None:
        known.append(_normalize_composition(formula))

    register({'C': 1, 'O': 1})
    register({'N': 1, 'O': 1})
    register({'N': 1, 'H': 3})
    register({'H': 2})
    register({'O': 2})
    register({'N': 2})
    register({'H': 2, 'O': 1})
    register({'C': 1, 'H': 4})
    register({'C': 1, 'O': 2})
    register({'S': 1, 'O': 2})
    register({'N': 1, 'O': 2})
    register({'C': 5, 'H': 5, 'N': 1})
    return set(known)


def _nearest_neighbor_average_distance(points: List[List[float]]) -> float:
    if not points or len(points) == 1:
        return 0.0
    total = 0.0
    for i, (xi, yi, zi) in enumerate(points):
        nearest = None
        for j, (xj, yj, zj) in enumerate(points):
            if i == j:
                continue
            dx = xi - xj
            dy = yi - yj
            dz = zi - zj
            d = (dx * dx + dy * dy + dz * dz) ** 0.5
            if nearest is None or d < nearest:
                nearest = d
        total += nearest or 0.0
    return total / float(len(points))


def _detect_vacuum_and_adsorbate(
    lattice: List[List[float]], cart_positions: List[List[float]], species: List[str]
) -> Dict[str, Any]:
    components = _build_components(cart_positions, species, bond_cut=1.9)
    if not components:
        return {'has_vacuum': False, 'has_adsorbate': False, 'num_adsorbate_atoms': 0}

    main_component = max(components, key=len)
    main_positions = [cart_positions[idx] for idx in main_component]
    d_avg_main = _nearest_neighbor_average_distance(main_positions)

    known_set = _known_adsorbate_set()
    drop_components: List[List[int]] = []
    for comp in components:
        if comp is main_component:
            continue
        composition = _component_composition(species, comp)
        if _normalize_composition(composition) in known_set and len(comp) <= 15:
            drop_components.append(comp)

    def min_distance_to_main(comp: List[int]) -> float:
        min_dist = None
        for idx in comp:
            xi, yi, zi = cart_positions[idx]
            for main_idx in main_component:
                xj, yj, zj = cart_positions[main_idx]
                dx = xi - xj
                dy = yi - yj
                dz = zi - zj
                d = (dx * dx + dy * dy + dz * dz) ** 0.5
                if min_dist is None or d < min_dist:
                    min_dist = d
        return min_dist or 0.0

    for comp in components:
        if comp is main_component or comp in drop_components:
            continue
        if d_avg_main > 0.0 and min_distance_to_main(comp) > d_avg_main:
            drop_components.append(comp)

    dropped_indices = {idx for comp in drop_components for idx in comp}
    has_adsorbate = len(dropped_indices) > 0

    remaining_positions = [
        p for i, p in enumerate(cart_positions) if i not in dropped_indices
    ]
    remaining_species = [
        species[i] for i in range(len(cart_positions)) if i not in dropped_indices
    ]
    if not remaining_positions:
        return {
            'has_vacuum': False,
            'has_adsorbate': has_adsorbate,
            'num_adsorbate_atoms': len(dropped_indices),
        }

    components_after = _build_components(
        remaining_positions, remaining_species, bond_cut=1.9
    )
    if not components_after:
        return {
            'has_vacuum': False,
            'has_adsorbate': has_adsorbate,
            'num_adsorbate_atoms': len(dropped_indices),
        }
    main_component_after = max(components_after, key=len)
    slab_positions = [remaining_positions[idx] for idx in main_component_after]

    spans_fraction: List[float] = []
    for lattice_vector in lattice:
        length = _vector_length(lattice_vector)
        unit_vec = _unit_vector(lattice_vector)
        projections = [_project(unit_vec, pos) for pos in slab_positions]
        if length <= 1e-8:
            spans_fraction.append(1.0)
            continue
        span = max(projections) - min(projections)
        spans_fraction.append(span / length if length > 0 else 1.0)

    vacuum_threshold = 0.7
    has_vacuum = any(frac < vacuum_threshold for frac in spans_fraction)

    return {
        'has_vacuum': has_vacuum,
        'has_adsorbate': has_adsorbate,
        'num_adsorbate_atoms': len(dropped_indices),
    }


def analyze_surface_structure(structure_info: Dict[str, Any]) -> Dict[str, Any]:
    lattice = structure_info.get('lattice_matrix')
    if not lattice and structure_info.get('lattice'):
        lattice = structure_info['lattice'].get('matrix')

    cart_positions = structure_info.get('cart_positions') or []
    species = structure_info.get('species_per_atom') or []

    if not lattice or len(lattice) != 3 or not cart_positions:
        return {'has_vacuum': False, 'has_adsorbate': False, 'num_adsorbate_atoms': 0}

    return _detect_vacuum_and_adsorbate(lattice, cart_positions, species)


def should_block_surface_structure(
    structure_info: Dict[str, Any],
) -> Tuple[bool, Dict[str, Any]]:
    try:
        analysis = analyze_surface_structure(structure_info)
    except Exception as error:  # pragma: no cover - 验证失败时仅记录日志
        logger.error('Failed to analyze surface structure: %s', error, exc_info=True)
        return False, {'error': str(error)}

    has_issue = analysis.get('has_vacuum') or analysis.get('has_adsorbate')
    return bool(has_issue), analysis


class ApexTaskConfig:
    """APEX计算任务配置（基于Cu4基准）"""

    # Cu4基准计算时间（分钟）
    BASE_OPTIMIZE_TIME = 5  # 几何优化

    # 各性质计算的配置：(几何优化时间, 单个性质计算时间, 性质计算任务数)
    TASK_CONFIGS = {
        'apex_optimize_structure': (5, 0, 0),  # 只有几何优化
        'apex_calculate_vacancy': (5, 10, 1),  # 几何优化 + 空位计算×元素数
        'apex_calculate_eos': (5, 30, 8),  # 几何优化 + 8个性质计算
        'apex_calculate_phonon': (5, 180, 6),  # 几何优化 + 6个性质计算(3h=180min)
        'apex_calculate_surface': (5, 30, 3),  # 几何优化 + 3个表面计算
        'apex_calculate_gamma': (5, 10, 4),  # 几何优化 + 4个性质计算
        'apex_calculate_interstitial': (5, 10, 2),  # 几何优化 + 2个性质计算
        'apex_calculate_elastic': (5, 40, 24),  # 几何优化 + 24个性质计算
    }

    @classmethod
    def get_base_time(cls, tool_name: str, element_count: int = 1) -> float:
        """
        获取基准计算时间（分钟）

        Args:
            tool_name: 工具名称
            element_count: 元素种类数（对vacancy有影响）

        Returns:
            基准计算时间（分钟）
        """
        if tool_name not in cls.TASK_CONFIGS:
            logger.warning(f"未知的工具名称: {tool_name}，使用默认配置")
            return 30.0  # 默认30分钟

        opt_time, calc_time, calc_count = cls.TASK_CONFIGS[tool_name]

        # 对于vacancy，计算任务数量要乘以元素数
        if tool_name == 'apex_calculate_vacancy':
            calc_count = calc_count * element_count

        total_time = opt_time + calc_time * calc_count
        return float(total_time)


def calculate_apex_cost(
    tool_name: str, structure_analyzer: StructureAnalyzer
) -> Tuple[int, Dict]:
    """
    计算APEX任务的费用

    Args:
        tool_name: 工具名称
        structure_analyzer: 结构分析器

    Returns:
        (photon费用, 费用详情字典)
    """
    try:
        # 获取基准计算时间（Cu4）
        element_count = structure_analyzer.get_element_count()
        base_time_minutes = ApexTaskConfig.get_base_time(tool_name, element_count)

        # 获取时间缩放因子
        scaling_factor = structure_analyzer.estimate_time_scaling_factor()

        # 计算实际计算时间
        actual_time_minutes = base_time_minutes * scaling_factor
        actual_time_hours = actual_time_minutes / 60.0

        # 获取机器成本
        machine_cost_per_hour = structure_analyzer.get_machine_cost_per_hour()

        # 计算总成本（元）
        total_cost_yuan = actual_time_hours * machine_cost_per_hour

        # 转换为photon（100 photon = 1元）- 向上取整，保证开发者收益
        photon_cost = math.ceil(total_cost_yuan * 100)

        # 费用详情
        cost_details = {
            'structure_summary': structure_analyzer.get_structure_summary(),
            'base_time_minutes': base_time_minutes,
            'scaling_factor': scaling_factor,
            'actual_time_minutes': actual_time_minutes,
            'actual_time_hours': actual_time_hours,
            'machine_cost_per_hour': machine_cost_per_hour,
            'total_cost_yuan': total_cost_yuan,
            'photon_cost': photon_cost,
        }

        logger.info(
            f"[{tool_name}] 费用计算详情:\n"
            f"  结构: {cost_details['structure_summary']}\n"
            f"  基准时间: {base_time_minutes:.1f}分钟 (Cu4)\n"
            f"  缩放因子: {scaling_factor:.2f}\n"
            f"  预计时间: {actual_time_minutes:.1f}分钟 ({actual_time_hours:.2f}小时)\n"
            f"  机器成本: {machine_cost_per_hour:.2f}元/小时\n"
            f"  总费用: {total_cost_yuan:.2f}元 = {photon_cost} photon"
        )

        return photon_cost, cost_details

    except Exception as e:
        logger.error(f"计算费用时出错: {str(e)}")
        # 返回默认费用
        default_cost = 500  # 默认5元
        return default_cost, {'error': str(e), 'photon_cost': default_cost}
