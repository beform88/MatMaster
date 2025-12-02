from enum import Enum


class DescriptiveEnum(str, Enum):
    """带有描述的枚举基类"""

    def __new__(cls, value, description):
        obj = str.__new__(cls, value)
        obj._value_ = value
        obj.description = description
        return obj

    def __str__(self):
        return self.value


class SceneEnum(DescriptiveEnum):
    STRUCTURE_GENERATE = ('structure_generate', '')
    CONDITIONAL_GENERATE = ('conditional_generate', '')
    STRUCTURAL_INFORMATICS = ('structural_informatics', '')

    DATABASE_SEARCH = ('database_search', '')

    OPTIMIZE_STRUCTURE = ('optimize_structure', '')
    VACANCY_FORMATION_ENERGY = ('vacancy_formation_energy', '')
    INTERSTITIAL_FORMATION_ENERGY = ('interstitial_formation_energy', '')
    ELASTIC_CONSTANT = ('elastic_constant', '')
    MOLECULAR_DYNAMICS = ('molecular_dynamics', '')
    SURFACE_ENERGY = ('surface_energy', '')
    STACKING_FAULT_ENERGY = ('stacking_fault_energy', '')
    EOS = ('eos', '')
    PHONON = ('phonon', '')
    BAND = ('band', '')
    DENSITY_OF_STATES = ('density_of_states', '')
    REACTION = ('reaction', '')
    BADER_CHARGE_ANALYSIS = ('bader_charge_analysis', '')
    WORK_FUNCTION = ('work_function', '')

    COMPOSITION_OPTIMIZATION = ('composition_optimization', '')

    VISUALIZE_DATA = ('visualize_data', '')

    SMILES = ('smiles', '')

    LITERATURE = (
        'literature',
        'involving research papers retrieval, content extraction, or trend analysis.e.g. Search for research papers on [topic], Extract key findings from the paper at [URL], Analyze research trends in [field]',
    )

    WEB_SEARCH = (
        'general_web_search',
        'involving concept query or procedure query.e.g. `What is [concept]`, `How to do [procedure]`',
    )

    WEB_PARSING = (
        'webpage_parsing',
        'involving extracting specific information from a given webpage URL.e.g. `Extract key information from the webpage at [URL]`, `Summarize the main points from the article at [URL]` Suitable for detail retrieval tasks after WEB_SEARCH.',
    )

    JOB_RESULT_RETRIEVAL = ('job_result_retrieval', '')

    XRD = ('XRD', '')
    DPA = ('DPA', '')
    APEX = ('APEX', '')
    ABACUS = ('ABACUS', '')
    LAMMPS = ('LAMMPS', '')
    NMR = ('NMR', '')

    HIGH_ENTROPY_ALLOY = ('high_entropy_alloy', '')
    POLYMER = ('polymer', '')

    CONVEXHULL = ('convexhull', '')

    SUPERCONDUCTOR = ('superconductor', '')

    THERMOELECTRIC = ('thermoelectric', '')
    Electron_Microscope = ('electron_microscope', '')

    DOE = ('doe', '')
    PILOTEYE_ELECTRO = ('piloteye_electro', '')
    PEROVSKITE_RESEARCH = (
        'perovskite_research',
        'Research, literature/database search, and semantic mining focused on perovskite solar cells (efficiency, stability, additives, architectures, new molecules).',
    )
