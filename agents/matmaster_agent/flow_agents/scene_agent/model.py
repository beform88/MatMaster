from enum import Enum


class SceneEnum(str, Enum):
    STRUCTURE_GENERATE = 'structure_generate'
    CONDITIONAL_GENERATE = 'conditional_generate'
    STRUCTURAL_INFORMATICS = 'structural_informatics'

    DATABASE_SEARCH = 'database_search'

    OPTIMIZE_STRUCTURE = 'optimize_structure'
    VACANCY_FORMATION_ENERGY = 'vacancy_formation_energy'
    INTERSTITIAL_FORMATION_ENERGY = 'interstitial_formation_energy'
    ELASTIC_CONSTANT = 'elastic_constant'
    MOLECULAR_DYNAMICS = 'molecular_dynamics'
    SURFACE_ENERGY = 'surface_energy'
    STACKING_FAULT_ENERGY = 'stacking_fault_energy'
    EOS = 'eos'
    PHONON = 'phonon'
    BAND = 'band'
    DENSITY_OF_STATES = 'density_of_states'
    REACTION = 'reaction'
    BADER_CHARGE_ANALYSIS = 'bader_charge_analysis'
    WORK_FUNCTION = 'work_function'

    CompositionOptimization = 'composition_optimization'

    VISUALIZE_DATA = 'visualize_data'

    SMILES = 'smiles'

    LITERATURE = 'literature'

    JobResultRetrieval = 'job_result_retrieval'

    DPA = 'DPA'
    APEX = 'APEX'
    ABACUS = 'ABACUS'
    LAMMPS = 'LAMMPS'

    HIGH_ENTROPY_ALLOY = 'high_entropy_alloy'
    POLYMER = 'polymer'
