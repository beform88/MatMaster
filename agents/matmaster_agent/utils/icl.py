from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.example_selectors.semantic_similarity import (
    SemanticSimilarityExampleSelector,
)


class ICLExampleSelector:
    def __init__(
        self,
        examples,
        model_name='/internfs/ycjin/MatMaster/models/moka-ai/m3e-base',
        model_kwargs=None,
        encode_kwargs=None,
        k=2,
    ):
        if model_kwargs is None:
            model_kwargs = {'device': 'cpu'}
        if encode_kwargs is None:
            encode_kwargs = {'normalize_embeddings': False}
        self.embeddings = HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs=model_kwargs,
            encode_kwargs=encode_kwargs,
        )
        self.update_vector_store = FAISS.from_texts(
            [e['update_input'] for e in examples], self.embeddings, metadatas=examples
        )
        self.ori_vector_store = FAISS.from_texts(
            [e['input'] for e in examples], self.embeddings, metadatas=examples
        )
        self.ori_example_selector = SemanticSimilarityExampleSelector(
            vectorstore=self.ori_vector_store, k=k
        )
        self.update_example_selector = SemanticSimilarityExampleSelector(
            vectorstore=self.update_vector_store, k=k
        )

    def select_examples(self, query):
        return self.ori_example_selector.select_examples({'input': query})

    def select_update_examples(self, query):
        return self.update_example_selector.select_examples({'input': query})

    def scene_tags_from_examples(self, examples):
        scene_prompts = ['\nSCENE_TAGS EXAMPLES:']
        for example in examples:
            if 'scene_tags' in example:
                scene_prompts.append(
                    f"User Input: {example['update_input']}\nScenes: {', '.join(example['scene_tags'])}\n"
                )
        return '\n'.join(scene_prompts)

    def toolchain_from_examples(self, examples):
        toolchain_prompts = ['\nToolchain EXAMPLES:']
        for example in examples:
            if 'toolchain' in example:
                toolchain_ = ' | '.join(
                    [
                        f"step{idx+1}: {step}"
                        for idx, step in enumerate(example['toolchain'])
                    ]
                )
                toolchain_prompts.append(
                    f"Input: {example['update_input']}\nToolchain: {toolchain_}\n"
                )
        return '\n'.join(toolchain_prompts)

    def expand_input_examples(self, examples):
        expanded_inputs = ['\nEXPAND EXAMPLES:']
        for example in examples:
            if 'update_input' in example:
                expanded_inputs.append(
                    f"Original Input: {example['input']}\nExpanded Input: {example['update_input']}\n"
                )
        return '\n'.join(expanded_inputs)


def icl_example_selector():
    return ICLExampleSelector(examples=examples, k=2)


examples = [
    {
        'input': '请帮我找一个铁的 bcc 结构',
        'update_input': '从数据库中检索铁的bcc结构信息',
        'toolchain': ['database_search'],
        'scene_tags': ['fetch_structures_with_spg'],
    },
    {
        'input': '请为我构建一个铁的 bcc 结构',
        'update_input': '请构建铁的体心立方（bcc）晶体结构，空间群为Im-3m，晶格常数为2.87Å',
        'toolchain': ['build_bulk_structure_by_template', 'optimize_structure'],
        'scene_tags': ['structure_generate', 'optimize_structure'],
    },
    {
        'input': '帮我构建一个金属锡的常见 β 相结构',
        'update_input': '请构建金属锡的常见 β 相（白锡）晶体结构，空间群为I41/amd，晶格常数为a=5.831Å，c=3.181Å',
        'toolchain': ['build_bulk_structure_by_template', 'optimize_structure'],
        'scene_tags': ['structure_generate', 'optimize_structure'],
    },
    {
        'input': '构建Si的块体结构，将2%的Si替换为As。尝试计算该结构的声子谱',
        'update_input': '首先构造标准Si晶体（Fd-3m，a=5.43Å）并进行合理的扩胞以适应2%的As掺杂浓度，然后引入As掺杂并优化其结构，最后计算掺杂结构的声子谱',
        'toolchain': [
            'build_bulk_structure_by_template',
            'make_supercell_structure',
            'make_doped_structure',
            'optimize_structure',
            'calculate_phonon',
        ],
        'scene_tags': ['structure_generate', 'optimize_structure', 'phonon'],
    },
    {
        'input': '对比不同数据库中 Fe₂O₃ 的带隙数据',
        'update_input': '首先从各不同数据库中检索 Fe₂O₃ 的带隙数据，然后进行比较分析，并列出差异及可能的原因',
        'toolchain': [
            'fetch_structures_with_bandgap',
            'fetch_bohrium_crystals',
            'fetch_openlam_structures',
            'fetch_structures_with_filter',
            'visualize_data',
        ],
        'scene_tags': ['database_search', 'band', 'visualize_data'],
    },
    {
        'input': '从 hMOF 数据库中检索比表面积 > 2000 m²/g 且孔径在 6–8 Å 的 MOF 结构，并导出 10 个候选结构 ',
        'update_input': '从 hMOF 数据库中检索符合以下条件的MOF结构：比表面积大于2000m²/g且孔径在6-8Å范围，然后导出10个候选结构。',
        'toolchain': ['fetch_mofs_sql'],
        'scene_tags': ['database_search'],
    },
    {
        'input': '将两块 Cu(111) 表面叠加生成界面结构（堆叠轴为 z，界面间距 2.5 Å）',
        'update_input': '首先构建Cu的体相结构（空间群Fm-3m，a=3.61Å），然后生成单个Cu(111)表面模型，随后根据堆叠轴为z方向、界面间距为2.5Å的要求将两块Cu(111)表面叠加生成界面结构。',
        'toolchain': [
            'build_bulk_structure_by_template',
            'build_surface_slab',
            'build_surface_interface',
        ],
        'scene_tags': ['structure_generate'],
    },
    {
        'input': '帮我建一个H₂O在 TiO₂ 表面 (101) 吸附的结构',
        'update_input': '首先从数据库中获取TiO₂体相结构，然后生成(101)表面模型并进行适当扩胞以防止周期性拥挤。接着构建H₂O分子吸附构型（O-H键长0.96Å，H-O-H键角104.5°），最后完成吸附结构构建。',
        'toolchain': [
            'fetch_structures_with_filter',
            'build_surface_slab',
            'make_supercell_structure',
            'build_molecule_structures_from_smiles',
            'build_surface_adsorbate',
        ],
        'scene_tags': ['structure_generate', 'surface_energy', 'database_search'],
    },
    {
        'input': 'Generate Si(111) slab with 10Å thickness',
        'update_input': 'First build Si bulk structure (Fd-3m, a=5.43Å), then generate Si(111) slab with 10Å thickness',
        'toolchain': ['build_bulk_structure_by_template', 'build_surface_slab'],
        'scene_tags': ['structure_generate'],
    },
    {
        'input': '计算NaCl的能带结构',
        'update_input': '首先构建NaCl体相结构（空间群Fm-3m，a=5.64Å），然后计算能带结构',
        'toolchain': ['build_bulk_structure_by_template', 'abacus_cal_band'],
        'scene_tags': ['structure_generate', 'band'],
    },
    {
        'input': 'Calculate phonons for zinc blende ZnS',
        'update_input': 'First construct zinc blende ZnS bulk structure (F-43m, a=5.41Å), then calculate phonon spectrum',
        'toolchain': ['build_bulk_structure_by_template', 'calculate_phonon'],
        'scene_tags': ['structure_generate', 'phonon'],
    },
    {
        'input': '给我一个BaTiO3钙钛矿结构',
        'update_input': '从数据库中检索钙钛矿BaTiO3的结构',
        'toolchain': ['fetch_structures_with_spg'],
        'scene_tags': ['database_search'],
    },
    {
        'input': '生成氮气和氧气的混合气体盒子，比例为2:1，盒子大小为15×15×15 Å³',
        'update_input': '首先构建N₂分子结构（键长1.10Å）和O₂分子结构（键长1.21Å），然后在15×15×15 Å³晶胞中按2:1比例生成常压下的混合气体盒子',
        'toolchain': [
            'build_molecule_structures_from_smiles',
            'build_molecule_structures_from_smiles',
            'make_amorphous_structure ',
        ],
        'scene_tags': ['structure_generate'],
    },
    {
        'input': '为 NiFe2O4生成 (100)、(110) 与 (111) 三个表面模型，并在每个表面构建 H₂O 吸附构型',
        'update_input': '首先从数据库中检索NiFe2O4的bulk结构，然后分别生成 (100)、(110) 与 (111) 三个表面模型。在生成的每个表面模型中，通过适当的扩胞操作避免周期性拥挤现象，接着构建H₂O分子结构（O-H键长0.96Å，H-O-H键角104.5°），并在每个表面上构建H₂O吸附构型。',
        'toolchain': [
            'fetch_structures_with_filter ',
            'build_surface_slab',
            'make_supercell_structure',
            'build_surface_slab',
            'make_supercell_structure',
            'build_surface_slab',
            'make_supercell_structure',
            'build_molecule_structures_from_smiles',
            'build_surface_adsorbate',
            'build_surface_adsorbate',
            'build_surface_adsorbate',
        ],
        'scene_tags': ['database_search', 'surface_energy', 'structure_generate'],
    },
]
