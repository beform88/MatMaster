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

    # universal
    UNIVERSAL = ('universal', 'Applicable to all scenarios')

    # database
    DATABASE_SEARCH = ('database_search', '')

    # generate
    STRUCTURE_GENERATE = ('structure_generate', '')
    CONDITIONAL_GENERATE = ('conditional_generate', '')

    # calc
    DPA = ('DPA', 'Involving machine learning potentials and DPA')
    APEX = ('APEX', 'Involving first-principles calculation methods using APEX.')
    ABACUS = ('ABACUS', 'Involving first-principles calculation methods using ABACUS.')
    LAMMPS = ('LAMMPS', 'involving LAMMPS-based methods.')
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
    CONVEXHULL = ('convexhull', '')

    # tool&models
    NMR = (
        'NMR',
        'Involves predicting the NMR spectra of organic molecules or deducing molecular structures from NMR spectra',
    )
    XRD = ('XRD', 'Involving XRD raw data analysis and phase identification')

    # literatue
    LITERATURE = (
        'literature',
        'involving research papers retrieval, content extraction, or progress/trends analysis. e.g. Search for research papers on [topic], Extract key findings from the paper at [URL], Analyze research progress/trends in [field]',
    )
    WEB_SEARCH = (
        'general_web_search',
        'involving concept query or procedure query.e.g. `What is [concept]`, `How to do [procedure]`',
    )
    WEB_PARSING = (
        'webpage_parsing',
        'involving extracting specific information from a given webpage URL.e.g. `Extract key information from the webpage at [URL]`, `Summarize the main points from the article at [URL]` Suitable for detail retrieval tasks after WEB_SEARCH.',
    )

    # postprocess
    VISUALIZE_DATA = (
        'visualize_data',
        'Involves visualization or charting requirements',
    )
    POST_MD_ANALYSIS = (
        'post_md_analysis',
        'Based on molecular dynamics trajectory data, analyze the mean-squared displacement (MSD), radial distribution function (RDF), solvation structure analysis, bond evolution, reaction species and network analysis.',
    )

    # reaserch sence
    MOLECULAR = (
        'MOLECULE',
        'Involving the generation, analysis, and SMILES representation of organic molecules',
    )
    HIGH_ENTROPY_ALLOY = ('high_entropy_alloy', 'Involving high-entropy alloys')
    POLYMER = ('polymer', 'Involving polymers')
    SUPERCONDUCTOR = ('superconductor', 'Involving superconducting materials')
    THERMOELECTRIC = ('thermoelectric', 'Involving thermoelectric materials')
    Electron_Microscope = (
        'electron_microscope',
        'Involving microscopic image analysis',
    )
    Solid_State_Electrolyte = (
        'solid_state_electrolyte',
        'Involving solid-state electrolyte materials',
    )
    STEEL = ('steel', 'Involving steel materials')
    DOE = ('doe', '')
    PILOTEYE_ELECTRO = ('piloteye_electro', '')
    PEROVSKITE_RESEARCH = (
        'perovskite_research',
        'Research, literature/database search, and semantic mining focused on perovskite solar cells (efficiency, stability, additives, architectures, new molecules).',
    )
    PHYSICAL_ADSORPTION = ('physical_adsorption', '')
