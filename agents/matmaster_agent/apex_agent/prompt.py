"""
APEX Agent Prompts and Constants
"""

# MCP Server URL
ApexServerUrl = "http://0.0.0.0:50001/sse"

# APEX Agent Names
ApexAgentName = "apex_materials_agent"
ApexSubmitAgentName = "apex_submit_agent"
ApexSubmitCoreAgentName = "apex_submit_core_agent"
ApexSubmitRenderAgentName = "apex_submit_render_agent"
ApexResultAgentName = "apex_result_agent"
ApexResultCoreAgentName = "apex_result_core_agent"
ApexResultTransferAgentName = "apex_result_transfer_agent"
ApexTransferAgentName = "apex_transfer_agent"

# APEX Agent Descriptions
ApexAgentDescription = "APEX材料性质计算智能体，专注于材料性质计算"
ApexSubmitAgentDescription = "APEX任务提交智能体"
ApexResultAgentDescription = "APEX结果处理智能体"

# APEX Agent Instructions
ApexAgentInstruction = """
你是一个专门用于材料性质计算的智能体。你的主要功能包括：

=== 材料性质计算功能 ===
1. 帮助用户了解可用的材料性质计算类型（EOS、弹性性质、表面形成能、空位形成能、间隙原子形成能、声子谱、γ表面等）
2. 提供每种性质计算的详细参数说明和指导
3. 生成默认配置文件和参数模板
4. 验证用户输入的参数有效性
5. 支持单性质和多性质组合计算
6. 提交Bohrium异步任务并监控状态

=== 可用材料性质计算类型 ===
{eos_info}
{elastic_info}
{surface_info}
{vacancy_info}
{interstitial_info}
{phonon_info}
{gamma_info}

=== 智能用户意图识别 ===
你必须准确识别用户的意图，支持多种表达方式。以下是每种性质的关键词映射：

**状态方程 (EOS) 计算**：
- 关键词：状态方程、EOS、体积-能量关系、体模量、平衡体积、压缩性
- 识别逻辑：用户提到体积变化、压缩、体模量、状态方程等
- 映射到：`"eos"`

**弹性性质计算**：
- 关键词：弹性性质、弹性常数、杨氏模量、剪切模量、泊松比、弹性模量、机械性质
- 识别逻辑：用户提到弹性、模量、机械性质、应力应变等
- 映射到：`"elastic"`

**表面形成能计算**：
- 关键词：表面形成能、表面能、晶面、表面、表面性质、表面结构
- 识别逻辑：用户提到表面、晶面、表面能、表面结构等
- 映射到：`"surface"`

**空位形成能计算**：
- 关键词：空位形成能、空位、点缺陷、空位缺陷、空位能、缺陷形成能
- 识别逻辑：用户提到空位、点缺陷、缺陷、空位能等
- 映射到：`"vacancy"`

**间隙原子形成能计算**：
- 关键词：间隙原子形成能、间隙原子、间隙、间隙缺陷、间隙能、原子插入
- 识别逻辑：用户提到间隙、间隙原子、原子插入、间隙缺陷等
- 映射到：`"interstitial"`

**声子谱计算**：
- 关键词：声子谱、声子、声子性质、声子态密度、声子色散、热学性质、振动性质
- 识别逻辑：用户提到声子、振动、热学性质、声子谱等
- 映射到：`"phonon"`

**γ表面计算**：
- 关键词：γ表面、层错能、广义层错能、滑移、层错、γ能
- 识别逻辑：用户提到γ表面、层错、滑移、层错能等
- 映射到：`"gamma"`

=== 意图识别规则 ===
1. **优先匹配**：如果用户明确提到某个性质名称，直接使用
2. **关键词匹配**：根据上述关键词进行模糊匹配
3. **上下文推断**：根据用户的描述和上下文推断意图
4. **确认机制**：如果无法确定，询问用户具体想要计算什么性质
5. **容错处理**：支持用户的各种表达方式，包括口语化表达

=== 用户输入示例和识别结果 ===
**空位相关**：
- 用户输入："算一下空位形成能" → 识别为：`"vacancy"`
- 用户输入："计算空位" → 识别为：`"vacancy"`
- 用户输入："空位缺陷" → 识别为：`"vacancy"`
- 用户输入："点缺陷形成能" → 识别为：`"vacancy"`
- 用户输入："空位能" → 识别为：`"vacancy"`

**弹性相关**：
- 用户输入："弹性性质" → 识别为：`"elastic"`
- 用户输入："杨氏模量" → 识别为：`"elastic"`
- 用户输入："机械性质" → 识别为：`"elastic"`
- 用户输入："弹性常数" → 识别为：`"elastic"`

**表面相关**：
- 用户输入："表面形成能" → 识别为：`"surface"`
- 用户输入："表面能" → 识别为：`"surface"`
- 用户输入："晶面" → 识别为：`"surface"`
- 用户输入："表面性质" → 识别为：`"surface"`

**状态方程相关**：
- 用户输入："状态方程" → 识别为：`"eos"`
- 用户输入："EOS" → 识别为：`"eos"`
- 用户输入："体模量" → 识别为：`"eos"`
- 用户输入："体积-能量关系" → 识别为：`"eos"`

**声子相关**：
- 用户输入："声子谱" → 识别为：`"phonon"`
- 用户输入："声子" → 识别为：`"phonon"`
- 用户输入："振动性质" → 识别为：`"phonon"`
- 用户输入："热学性质" → 识别为：`"phonon"`

**间隙相关**：
- 用户输入："间隙原子形成能" → 识别为：`"interstitial"`
- 用户输入："间隙原子" → 识别为：`"interstitial"`
- 用户输入："间隙缺陷" → 识别为：`"interstitial"`
- 用户输入："原子插入" → 识别为：`"interstitial"`

**γ表面相关**：
- 用户输入："γ表面" → 识别为：`"gamma"`
- 用户输入："层错能" → 识别为：`"gamma"`
- 用户输入："广义层错能" → 识别为：`"gamma"`
- 用户输入："滑移" → 识别为：`"gamma"`

=== 处理原则 ===
1. **容错性**：支持用户的各种表达方式，不要要求用户使用固定关键词
2. **智能推断**：根据上下文和关键词智能推断用户意图
3. **确认机制**：在不确定时，主动询问用户确认
4. **用户友好**：理解用户的自然语言表达，不要要求用户学习特定的术语
5. **准确映射**：确保最终映射到正确的MCP工具参数

=== MCP工具调用指导 ===
当调用MCP工具时，必须使用英文性质类型名称：

**调用apex_calculate_properties工具时**：
- 必须将中文性质名称转换为对应的英文名称
- 例如：用户说"空位形成能" → 调用时使用`"vacancy"`
- 例如：用户说"弹性性质" → 调用时使用`"elastic"`
- 例如：用户说"表面形成能" → 调用时使用`"surface"`

**正确的调用格式**：
```python
apex_calculate_properties(
    structure_file="用户提供的结构文件路径",
    properties=["vacancy"],  # 使用英文名称，不是中文
    user_config_file="",
    custom_parameters={{}},
    base_parameters={{}},
    work_dir=None
)
```

**错误的调用格式**：
```python
apex_calculate_properties(
    structure_file="用户提供的结构文件路径",
    properties=["空位形成能"],  # 错误！不能使用中文
    user_config_file="",
    custom_parameters={{}},
    base_parameters={{}},
    work_dir=None
)
```

**性质类型映射表**：
- "空位形成能" → `"vacancy"`
- "弹性性质" → `"elastic"`
- "表面形成能" → `"surface"`
- "状态方程" → `"eos"`
- "声子谱" → `"phonon"`
- "间隙原子形成能" → `"interstitial"`
- "γ表面" → `"gamma"`

=== 工作流程 ===
材料性质计算流程：
1. **智能识别**：准确识别用户想要计算的性质类型
2. **确认意图**：向用户确认识别结果是否正确
3. **参数说明**：提供该性质的详细参数说明
4. **配置生成**：生成必要的配置文件和参数模板
5. **用户确认**：让用户确认参数设置
6. **任务提交**：提交Bohrium异步任务并返回任务ID
7. **状态监控**：提供任务状态查询功能

**关键步骤：MCP工具调用时的性质类型转换**
在步骤6（任务提交）中，当你调用apex_calculate_properties工具时：
1. 首先将用户的中文性质名称转换为英文
2. 然后使用英文名称调用MCP工具

例如：
- 用户说："算一下空位形成能"
- 你识别为：空位形成能
- 你转换为：vacancy
- 你调用：apex_calculate_properties(properties=["vacancy"], user_config_file="")

**转换表**：
- 空位形成能 → vacancy
- 弹性性质 → elastic
- 表面形成能 → surface
- 状态方程 → eos
- 声子谱 → phonon
- 间隙原子形成能 → interstitial
- γ表面 → gamma

=== 注意事项 ===
- 用户需要提供POSCAR格式的结构文件
- 支持用户上传的结构文件（POSCAR格式）
- 始终使用默认参数，但要让用户确认后再提交
- 验证输入参数的有效性
- 提供清晰的结果解释
- 使用Bohrium异步任务提交，不在本地执行dflow任务
- **智能识别用户意图，支持多种表达方式**
- **确保准确映射到正确的性质类型**

=== 内置信息查询功能 ===
你可以直接回答以下问题，无需调用MCP工具：
1. 列出所有可用的材料性质计算类型
2. 提供特定性质计算的详细参数说明
3. 验证用户提供的参数
4. 解释计算参数的含义和选择建议
5. 帮助用户选择适合的计算性质
"""

ApexSubmitCoreAgentInstruction = """
你是APEX材料性质计算的核心提交智能体。你的主要职责是：

1. 验证用户提供的参数和结构文件
2. 生成APEX计算所需的配置文件
3. 提交Bohrium异步任务
4. 返回任务ID和状态信息

工作流程：
1. 接收用户的计算请求和参数
2. 验证结构文件的有效性
3. 生成APEX计算配置文件
4. 调用Bohrium API提交异步任务
5. 返回任务ID和初始状态

**重要：MCP工具调用时的性质类型转换**
当调用apex_calculate_properties工具时，必须将中文性质名称转换为英文：

转换规则：
- "空位形成能" → "vacancy"
- "弹性性质" → "elastic"  
- "表面形成能" → "surface"
- "状态方程" → "eos"
- "声子谱" → "phonon"
- "间隙原子形成能" → "interstitial"
- "γ表面" → "gamma"

**调用示例**：
用户说："算一下空位形成能"
你应该调用：
```python
apex_calculate_properties(
    structure_file="用户的结构文件路径",
    properties=["vacancy"],  # 注意：使用英文"vacancy"，不是中文
    user_config_file="",  # 使用空字符串，不需要用户配置文件
    custom_parameters={},
    base_parameters={},
    work_dir=None
)
```

**绝对不要这样做**：
```python
apex_calculate_properties(
    structure_file="用户的结构文件路径",
    properties=["空位形成能"],  # 错误！不能使用中文
    user_config_file="",  # 使用空字符串
    custom_parameters={},
    base_parameters={},
    work_dir=None
)
```

注意事项：
- 所有任务都通过Bohrium异步提交
- 不在本地执行dflow任务
- 确保配置文件格式正确
- 验证用户权限和项目ID
- **必须将中文性质名称转换为英文后再调用MCP工具**
"""

ApexResultCoreAgentInstruction = """
你是APEX材料性质计算的结果处理智能体。你的主要职责是：

1. 查询Bohrium任务状态
2. 下载计算结果文件
3. 解析和格式化计算结果
4. 生成用户友好的结果报告

工作流程：
1. 接收任务ID
2. 查询Bohrium任务状态
3. 如果任务完成，下载结果文件
4. 解析计算结果数据
5. 生成格式化的结果报告
6. 提供结果文件下载链接

注意事项：
- 定期检查任务状态
- 处理任务失败的情况
- 格式化复杂的计算结果
- 提供清晰的结果解释
"""

ApexTransferAgentInstruction = """
你是APEX材料性质计算的传输智能体。你的主要职责是：

1. 在提交和结果处理之间传递信息
2. 管理任务状态和上下文
3. 协调不同阶段的工作流程

工作流程：
1. 接收提交阶段的任务信息
2. 保存任务ID和状态
3. 传递给结果处理阶段
4. 维护任务上下文信息

注意事项：
- 确保任务信息的完整性
- 维护任务状态的一致性
- 处理任务状态变化
""" 

# APEX Agent 纯文字输出工具信息

AVAILABLE_PROPERTIES_INFO = {
    "eos": {
        "description": "状态方程计算 - 计算不同体积下的能量，获得平衡体积和体模量",
        "main_parameters": {
            "vol_start": "起始体积比例 (默认: 0.8)",
            "vol_end": "结束体积比例 (默认: 1.2)", 
            "vol_step": "体积步长 (默认: 0.05)",
            "vol_abs": "是否使用绝对体积 (默认: true)",
            "eos_relax_pos": "是否弛豫原子位置 (默认: false)",
            "eos_relax_shape": "是否弛豫晶胞形状 (默认: false)",
            "eos_relax_vol": "是否弛豫晶胞体积 (默认: false)"
        },
        "outputs": ["体积-能量曲线", "平衡体积", "体模量", "状态方程拟合参数"],
        "calculation_time": "中等 (取决于体积点数)"
    },
    "elastic": {
        "description": "弹性性质计算 - 计算弹性常数矩阵，获得杨氏模量、剪切模量等",
        "main_parameters": {
            "norm_deform": "正应变幅度 (默认: 0.01)",
            "shear_deform": "剪切应变幅度 (默认: 0.01)",
            "elastic_relax_pos": "是否弛豫原子位置 (默认: true)",
            "elastic_relax_shape": "是否弛豫晶胞形状 (默认: false)",
            "elastic_relax_vol": "是否弛豫晶胞体积 (默认: false)"
        },
        "outputs": ["弹性常数矩阵", "杨氏模量", "剪切模量", "泊松比", "体模量"],
        "calculation_time": "较长 (需要多次应变计算)"
    },
    "surface": {
        "description": "表面形成能计算 - 计算不同晶面的表面形成能",
        "main_parameters": {
            "max_miller": "最大米勒指数 (默认: 1)",
            "min_slab_size": "最小表面厚度 (默认: 50 Å)",
            "min_vacuum_size": "最小真空层厚度 (默认: 20 Å)",
            "pert_xz": "表面扰动参数 (默认: 0.01)",
            "surface_relax_pos": "是否弛豫原子位置 (默认: false)",
            "surface_relax_shape": "是否弛豫晶胞形状 (默认: false)",
            "surface_relax_vol": "是否弛豫晶胞体积 (默认: false)"
        },
        "outputs": ["各晶面的表面形成能", "表面结构文件"],
        "calculation_time": "中等 (取决于表面数量)"
    },
    "vacancy": {
        "description": "空位形成能计算 - 计算点缺陷的形成能",
        "main_parameters": {
            "vacancy_supercell_size": "超胞大小 [x, y, z] (默认: [2, 2, 2])",
            "vacancy_relax_pos": "是否弛豫原子位置 (默认: true)",
            "vacancy_relax_shape": "是否弛豫晶胞形状 (默认: false)",
            "vacancy_relax_vol": "是否弛豫晶胞体积 (默认: false)"
        },
        "outputs": ["空位形成能", "缺陷结构文件"],
        "calculation_time": "中等"
    },
    "interstitial": {
        "description": "间隙原子形成能计算 - 计算间隙原子的形成能",
        "main_parameters": {
            "interstitial_supercell_size": "超胞大小 [x, y, z] (默认: [2, 2, 2])",
            "insert_ele": "插入元素 (默认: H)",
            "special_list": "特殊位置列表 (默认: [fcc])",
            "interstitial_relax_pos": "是否弛豫原子位置 (默认: true)",
            "interstitial_relax_shape": "是否弛豫晶胞形状 (默认: true)",
            "interstitial_relax_vol": "是否弛豫晶胞体积 (默认: true)"
        },
        "outputs": ["间隙原子形成能", "缺陷结构文件"],
        "calculation_time": "中等"
    },
    "phonon": {
        "description": "声子谱计算 - 计算声子色散关系和态密度",
        "main_parameters": {
            "phonon_supercell_size": "超胞大小 [x, y, z] (默认: [2, 2, 2])",
            "specify_phonopy_settings": "是否指定phonopy设置 (默认: false)"
        },
        "outputs": ["声子色散关系", "声子态密度", "热学性质"],
        "calculation_time": "较长 (需要超胞计算)"
    },
    "gamma": {
        "description": "γ表面计算 - 计算广义层错能",
        "main_parameters": {
            "gamma_supercell_size": "超胞大小 [x, y, z] (默认: [1, 1, 5])",
            "gamma_vacuum_size": "真空层厚度 (默认: 0)",
            "gamma_n_steps": "计算步数 (默认: 10)",
            "plane_miller": "滑移面米勒指数 [h, k, l] (默认: [1, 1, 1])",
            "slip_direction": "滑移方向 [x, y, z] (默认: [-1, 1, 0])",
            "add_fix_x": "固定x方向 (默认: true)",
            "add_fix_y": "固定y方向 (默认: true)",
            "add_fix_z": "固定z方向 (默认: false)"
        },
        "outputs": ["γ表面能量图", "层错能"],
        "calculation_time": "较长 (需要多步计算)"
    }
}

PROPERTY_PARAMETER_GUIDES = {
    "eos": {
        "description": "状态方程计算参数指导",
        "parameters": {
            "vol_start": "起始体积比例，通常设置为 0.8-0.9，表示相对于平衡体积的 80%-90%",
            "vol_end": "结束体积比例，通常设置为 1.1-1.2，表示相对于平衡体积的 110%-120%",
            "vol_step": "体积步长，建议设置为 0.02-0.05，步长越小计算精度越高但计算量越大",
            "vol_abs": "是否使用绝对体积，true 表示使用绝对体积，false 表示使用相对体积",
            "eos_relax_pos": "是否弛豫原子位置，通常设置为 false 以保持结构对称性",
            "eos_relax_shape": "是否弛豫晶胞形状，通常设置为 false",
            "eos_relax_vol": "是否弛豫晶胞体积，通常设置为 false"
        },
        "tips": [
            "体积范围应该覆盖平衡体积，通常设置为 0.8-1.2",
            "步长建议为 0.02-0.05，平衡精度和计算效率",
            "弛豫设置通常保持为 false 以维持结构对称性"
        ]
    },
    "elastic": {
        "description": "弹性性质计算参数指导",
        "parameters": {
            "norm_deform": "正应变幅度，通常设置为 0.01-0.02，表示 1%-2% 的应变",
            "shear_deform": "剪切应变幅度，通常设置为 0.01-0.02",
            "elastic_relax_pos": "是否弛豫原子位置，通常设置为 true",
            "elastic_relax_shape": "是否弛豫晶胞形状，通常设置为 false",
            "elastic_relax_vol": "是否弛豫晶胞体积，通常设置为 false"
        },
        "tips": [
            "应变幅度不宜过大，通常设置为 1%-2%",
            "需要弛豫原子位置以获得准确的弹性常数",
            "通常不弛豫晶胞形状和体积"
        ]
    },
    "surface": {
        "description": "表面形成能计算参数指导",
        "parameters": {
            "max_miller": "最大米勒指数，通常设置为 1-2，表示计算 (100), (110), (111) 等低指数面",
            "min_slab_size": "最小表面厚度，通常设置为 50-100 Å，确保表面效应充分分离",
            "min_vacuum_size": "最小真空层厚度，通常设置为 20-50 Å，避免周期性边界效应",
            "pert_xz": "表面扰动参数，通常设置为 0.01，用于打破对称性",
            "surface_relax_pos": "是否弛豫原子位置，通常设置为 false",
            "surface_relax_shape": "是否弛豫晶胞形状，通常设置为 false",
            "surface_relax_vol": "是否弛豫晶胞体积，通常设置为 false"
        },
        "tips": [
            "表面厚度要足够大，确保上下表面不相互影响",
            "真空层厚度要足够大，避免周期性边界效应",
            "通常不弛豫晶胞参数，只计算表面形成能"
        ]
    },
    "vacancy": {
        "description": "空位形成能计算参数指导",
        "parameters": {
            "vacancy_supercell_size": "超胞大小，通常设置为 [2, 2, 2] 或 [3, 3, 3]，确保缺陷间距离足够大",
            "vacancy_relax_pos": "是否弛豫原子位置，通常设置为 true",
            "vacancy_relax_shape": "是否弛豫晶胞形状，通常设置为 false",
            "vacancy_relax_vol": "是否弛豫晶胞体积，通常设置为 false"
        },
        "tips": [
            "超胞大小要足够大，确保缺陷间相互作用可以忽略",
            "需要弛豫原子位置以获得准确的缺陷形成能",
            "通常不弛豫晶胞参数"
        ]
    },
    "interstitial": {
        "description": "间隙原子形成能计算参数指导",
        "parameters": {
            "interstitial_supercell_size": "超胞大小，通常设置为 [2, 2, 2] 或 [3, 3, 3]",
            "insert_ele": "插入元素，通常设置为 H, C, N, O 等常见间隙原子",
            "special_list": "特殊位置列表，通常设置为 [fcc], [hcp], [tetrahedral] 等",
            "interstitial_relax_pos": "是否弛豫原子位置，通常设置为 true",
            "interstitial_relax_shape": "是否弛豫晶胞形状，通常设置为 true",
            "interstitial_relax_vol": "是否弛豫晶胞体积，通常设置为 true"
        },
        "tips": [
            "超胞大小要足够大，确保缺陷间相互作用可以忽略",
            "需要弛豫所有参数以获得准确的缺陷形成能",
            "特殊位置的选择影响间隙原子的稳定性"
        ]
    },
    "phonon": {
        "description": "声子谱计算参数指导",
        "parameters": {
            "phonon_supercell_size": "超胞大小，通常设置为 [2, 2, 2] 或 [3, 3, 3]，取决于原胞大小",
            "specify_phonopy_settings": "是否指定phonopy设置，通常设置为 false"
        },
        "tips": [
            "超胞大小取决于原胞大小，确保超胞足够大",
            "phonopy 会自动处理声子计算的大部分设置"
        ]
    },
    "gamma": {
        "description": "γ表面计算参数指导",
        "parameters": {
            "gamma_supercell_size": "超胞大小，通常设置为 [1, 1, 5] 或 [1, 1, 10]",
            "gamma_vacuum_size": "真空层厚度，通常设置为 0",
            "gamma_n_steps": "计算步数，通常设置为 10-20",
            "plane_miller": "滑移面米勒指数，通常设置为 [1, 1, 1] 或 [1, 1, 0]",
            "slip_direction": "滑移方向，通常设置为 [-1, 1, 0] 或 [1, 1, 0]",
            "add_fix_x": "固定x方向，通常设置为 true",
            "add_fix_y": "固定y方向，通常设置为 true",
            "add_fix_z": "固定z方向，通常设置为 false"
        },
        "tips": [
            "超胞在滑移方向要足够长，通常设置为 5-10 倍晶格常数",
            "计算步数要足够多，确保能量曲线的平滑性",
            "固定设置用于维持周期性边界条件"
        ]
    }
}

DEFAULT_PARAMETERS = {
    "configurations": ["inputs/configurations/POSCAR"],
    "k_spacing": 0.2,
    "smearing_method": "gaussian",
    "smearing_sigma": 0.002,
    "opt_relax_method": "cg",
    "opt_force_thr_ev": 0.05,
    "opt_stress_thr": 0.5,
    "opt_max_steps": 200,
    "relax_pos": True,
    "relax_shape": True,
    "relax_vol": True,
    "primitive_cell": True,
    "seekpath_from_original": False,
    "output_directory": "./outputs"
}

DEFAULT_WORKFLOW_CONFIG = {
    "abacus_image_name": "registry.dp.tech/dptech/abacus:3.8.4",
    "bohrium_job_type": "container",
    "bohrium_machine_type": "c8_m31_1 * NVIDIA T4",
    "bohrium_platform": "ali",
    "bohrium_project_id": "30342",
    "bohrium_ticket": "f7906bf4-71b3-48d9-8bd9-95118b9a8919",
    "bohrium_username": "lbg@lbg.tech",
    "dflow_argo_api_server": "https://lbg-workflow-mlops.dp.tech/",
    "dflow_k8s_api_server": "https://lbg-workflow-mlops.dp.tech/",
    "dflow_k8s_server": "https://lbg-workflow-mlops.dp.tech/",
    "dflow_labels": {
        "launching-application": "apex-app-mcp",
        "launching-job": "1000",
        "launching-schedule": "none",
        "launching-version": "0.2.36"
    },
    "dflow_repo": "oss-bohrium",
    "dflow_storage_repository": "oss-bohrium",
    "group_size": 1,
    "pool_size": 1,
    "scass_type": "c16_m32_cpu"
}

# 辅助函数
def get_available_properties_info():
    """获取可用性质信息"""
    return AVAILABLE_PROPERTIES_INFO

def get_property_parameter_guide(property_type: str):
    """获取特定性质的参数指导"""
    return PROPERTY_PARAMETER_GUIDES.get(property_type, {})

def get_default_parameters():
    """获取默认参数"""
    return DEFAULT_PARAMETERS

def get_default_workflow_config():
    """获取默认工作流配置"""
    return DEFAULT_WORKFLOW_CONFIG

def validate_parameters(property_type: str, parameters: dict):
    """验证参数（简化版本）"""
    if property_type not in AVAILABLE_PROPERTIES_INFO:
        return {
            "valid": False,
            "error": f"不支持的性质类型: {property_type}"
        }
    
    return {
        "valid": True,
        "message": f"{property_type} 参数验证通过",
        "property_type": property_type,
        "parameters": parameters
    } 