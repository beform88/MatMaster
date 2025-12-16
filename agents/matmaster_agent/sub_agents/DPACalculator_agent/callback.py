import logging

from google.adk.tools import ToolContext

from agents.matmaster_agent.constant import MATMASTER_AGENT_NAME
from agents.matmaster_agent.logger import PrefixFilter

logger = logging.getLogger(__name__)
logger.addFilter(PrefixFilter(MATMASTER_AGENT_NAME))
logger.setLevel(logging.INFO)

BUILTIN_DPA2_HEADS = [
    'Domains_Alloy',
    'Domains_Anode',
    'Domains_Cluster',
    'Domains_Drug',
    'Domains_FerroEle',
    'Domains_SSE_PBE',
    'Domains_SemiCond',
    'H2O_H2O_PD',
    'Metals_AlMgCu',
    'Metals_Cu',
    'Metals_Sn',
    'Metals_Ti',
    'Metals_V',
    'Metals_W',
    'Others_C12H26',
    'Others_HfO2',
    'Domains_SSE_PBESol',
    'Domains_Transition1x',
    'H2O_H2O_DPLR',
    'H2O_H2O_PBE0TS_MD',
    'H2O_H2O_PBE0TS',
    'H2O_H2O_SCAN0',
    'Metals_AgAu_PBED3',
    'Others_In2Se3',
    'MP_traj_v024_alldata_mixu',
    'Alloy_tongqi',
    'SSE_ABACUS',
    'Hybrid_Perovskite',
    'solvated_protein_fragments',
    'Electrolyte',
    'ODAC23',
    'Alex2D',
    'Omat24',
    'SPICE2',
    'OC20M',
    'OC22',
    'Organic_Reactions',
    'RANDOM',
]
BUILTIN_DPA3_HEADS = [
    'Domains_Alloy',
    'Domains_Anode',
    'Domains_Cluster',
    'Domains_Drug',
    'Domains_FerroEle',
    'Domains_SSE_PBE',
    'Domains_SemiCond',
    'H2O_H2O_PD',
    'Metals_AlMgCu',
    'Metals_Sn',
    'Metals_Ti',
    'Metals_V',
    'Metals_W',
    'Others_HfO2',
    'Domains_SSE_PBESol',
    'Domains_Transition1x',
    'Metals_AgAu_PBED3',
    'Others_In2Se3',
    'MP_traj_v024_alldata_mixu',
    'Alloy_tongqi',
    'SSE_ABACUS',
    'Hybrid_Perovskite',
    'solvated_protein_fragments',
    'Electrolyte',
    'ODAC23',
    'Alex2D',
    'Omat24',
    'SPICE2',
    'OC20M',
    'OC22',
    'Organic_Reactions',
    'RANDOM',
]


async def before_tool_callback(tool, args, tool_context: ToolContext):
    model_path = args.get('model_path')
    head = args.get('head')

    if (
        model_path
        and 'https://bohrium.oss-cn-zhangjiakou.aliyuncs.com/13756/27666/store/upload/cd12300a-d3e6-4de9-9783-dd9899376cae/dpa-2.4-7M.pt'
        in model_path
    ):
        if head not in BUILTIN_DPA2_HEADS:
            args['head'] = 'Omat24'
            logger.info(
                f"[before_tool_callback] Updated head to Omat24 for DPA2.4 model {head}, {args['head']}"
            )
    elif (
        model_path
        and 'https://bohrium.oss-cn-zhangjiakou.aliyuncs.com/13756/27666/store/upload/18b8f35e-69f5-47de-92ef-af8ef2c13f54/DPA-3.1-3M.pt'
        in model_path
    ):
        if head not in BUILTIN_DPA3_HEADS:
            args['head'] = 'Omat24'
            logger.info(
                f"[before_tool_callback] Updated head to Omat24 for DPA3.1 model {head}, {args['head']}"
            )
