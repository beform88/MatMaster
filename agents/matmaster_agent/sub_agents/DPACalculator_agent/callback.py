import logging
from urllib.parse import urlparse

from google.adk.tools import ToolContext

from agents.matmaster_agent.constant import MATMASTER_AGENT_NAME
from agents.matmaster_agent.logger import PrefixFilter
from agents.matmaster_agent.services.session_files import get_session_files

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
    'Metals_HfO2',
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


async def _replace_if_not_oss_url(file_path, actual_files, tool_name, arg_name):
    """
    Checks if the file_path is an OSS URL, if not, tries to match it with actual files
    and returns the matched OSS URL or the original file_path.
    """
    # Check if it's already an OSS/HTTP URL
    if file_path and isinstance(file_path, str):
        parsed = urlparse(file_path)
        if parsed.scheme in ['http', 'https']:
            # If it's a URL, check if it's in the session files
            if file_path in actual_files:
                logger.info(
                    f"[validate_file_urls] Found real file URL: {file_path} for {tool_name}.{arg_name}"
                )
                return file_path
            else:
                logger.info(
                    f"[validate_file_urls] LLM generated URL: {file_path} for {tool_name}.{arg_name}"
                )
                return file_path  # Return as is if it's a URL but not in session (maybe external)

        # If it's not a URL, try to match with actual files in the session using regex
        for actual_file_url in actual_files:
            # Check if the file_path is part of the URL or matches the filename at the end
            if file_path in actual_file_url or actual_file_url.endswith(
                '/' + file_path
            ):
                logger.info(
                    f"[validate_file_urls] Found real file match: {file_path} -> {actual_file_url} for {tool_name}.{arg_name}"
                )
                return actual_file_url

        # If no match found, return the original value
        logger.info(
            f"[validate_file_urls] No real file match for: {file_path} in {tool_name}.{arg_name}"
        )

    return file_path  # Return as is if it's not a string or None


async def validate_dpa_file_urls(tool, args, tool_context: ToolContext):
    """
    Validates file URLs from session to ensure they are actual session files (not hallucinated by LLM).
    If not an OSS URL, tries to match the filename against session files using regex matching.
    """
    session_id = tool_context.session.id

    # Get actual files from the session
    try:
        actual_files = await get_session_files(session_id)
        logger.info(f"Retrieved {len(actual_files)} files from session: {actual_files}")
    except Exception as e:
        logger.error(f"Failed to retrieve session files: {e}")
        return

    # Define the file path arguments that need to be validated for each tool
    file_path_args = {
        'optimize_structure': [('input_structure',), ('model_path',)],
        'calculate_phonon': [('input_structure',), ('model_path',)],
        'run_molecular_dynamics': [('initial_structure',), ('model_path',)],
        'calculate_elastic_constants': [('input_structure',), ('model_path',)],
        'run_neb': [('initial_structure',), ('final_structure',), ('model_path',)],
    }

    # Get the argument names that contain file paths for this tool
    args_to_check = file_path_args.get(tool.name, [])

    for arg_name_tuple in args_to_check:
        for arg_name in arg_name_tuple:
            if arg_name in args:
                original_value = args[arg_name]
                if isinstance(original_value, list):
                    # Handle list of file paths
                    updated_list = []
                    for item in original_value:
                        updated_item = await _replace_if_not_oss_url(
                            item, actual_files, tool.name, arg_name
                        )
                        updated_list.append(updated_item)
                    args[arg_name] = updated_list
                else:
                    # For single values, check and replace if needed
                    updated_value = await _replace_if_not_oss_url(
                        original_value, actual_files, tool.name, arg_name
                    )
                    args[arg_name] = updated_value


async def combined_before_tool_callback(tool, args, tool_context: ToolContext):
    # First run the file URL validation
    await validate_dpa_file_urls(tool, args, tool_context)

    # Then run the existing head validation
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


# Backwards compatibility alias
before_tool_callback = combined_before_tool_callback
