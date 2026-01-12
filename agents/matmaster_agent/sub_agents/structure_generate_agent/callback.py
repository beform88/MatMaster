import logging
from urllib.parse import urlparse

from google.adk.tools import ToolContext

from agents.matmaster_agent.constant import MATMASTER_AGENT_NAME
from agents.matmaster_agent.logger import PrefixFilter
from agents.matmaster_agent.services.session_files import get_session_files

logger = logging.getLogger(__name__)
logger.addFilter(PrefixFilter(MATMASTER_AGENT_NAME))
logger.setLevel(logging.INFO)

BUILD_PERIODIC_TOOS = [
    'build_bulk_structure_by_template',
    'build_bulk_structure_by_wyckoff',
    'make_supercell_structure',
    'make_doped_structure',
    'make_amorphous_structure',
    'add_cell_for_molecules',
    'build_surface_slab',
    'build_surface_adsorbate',
    'build_surface_interface',
]
BUILD_NONPERIODIC_TOOLS = [
    'build_molecule_structures_from_smiles',
]
AVAILABLE_PERIODIC_SUFFIX = ['cif', 'vasp', 'poscar']
AVAILABLE_NONPERIODIC_SUFFIX = ['xyz']


def get_suffix(args):
    if 'output_file' in args:
        output_file = args['output_file']
        if isinstance(output_file, str):
            if '.' in output_file:
                return output_file.split('.')[-1].lower()
            else:
                return ''
    return None


async def validate_file_urls(tool, args, tool_context: ToolContext):
    """
    Validates file URLs from session to ensure they are actual session files (not hallucinated by LLM).
    If not an OSS URL, tries to match the filename against session files.
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
        'get_structure_info': ['structure_path'],
        'get_molecule_info': ['molecule_path'],
        'make_supercell_structure': ['structure_path'],
        'add_cell_for_molecules': ['molecule_path'],
        'build_surface_slab': ['material_path'],
        'build_surface_adsorbate': ['surface_path', 'adsorbate_path'],
        'build_surface_interface': ['material1_path', 'material2_path'],
        'make_defect_structure': ['structure_path'],
        'make_doped_structure': ['structure_path'],
        'make_amorphous_structure': ['molecule_paths'],  # This one might be a list
        'add_hydrogens': ['structure_path'],
        'generate_ordered_replicas': ['structure_path'],
    }

    # Get the argument names that contain file paths for this tool
    args_to_check = file_path_args.get(tool.name, [])

    for arg_name in args_to_check:
        if arg_name in args:
            value = args[arg_name]

            # If the value is a list (like molecule_paths), process each item
            if isinstance(value, list):
                updated_list = []
                for item in value:
                    updated_item = await _replace_if_not_oss_url(item, actual_files)
                    updated_list.append(updated_item)
                args[arg_name] = updated_list
            else:
                # For single values, check and replace if needed
                updated_value = await _replace_if_not_oss_url(value, actual_files)
                args[arg_name] = updated_value


async def _replace_if_not_oss_url(file_path, actual_files):
    """
    Checks if the file_path is an OSS URL, if not, tries to match it with actual files
    and returns the matched OSS URL or the original file_path.
    """
    # Check if it's already an OSS/HTTP URL
    parsed = urlparse(file_path)
    if parsed.scheme in ['http', 'https']:
        # If it's a URL, check if it's in the session files
        if file_path in actual_files:
            logger.info(f"[validate_file_urls] Found real file URL: {file_path}")
            return file_path
        else:
            logger.info(f"[validate_file_urls] LLM generated URL: {file_path}")
            return file_path  # Return as is if it's a URL but not in session (maybe external)

    # If it's not a URL, try to match with actual files in the session
    for actual_file_url in actual_files:
        # Check if the file_path is part of the URL or matches the filename at the end
        if file_path in actual_file_url or actual_file_url.endswith('/' + file_path):
            logger.info(
                f"[validate_file_urls] Found real file match: {file_path} -> {actual_file_url}"
            )
            return actual_file_url

    # If no match found, return the original value
    logger.info(f"[validate_file_urls] No real file match for: {file_path}")
    return file_path


async def regulate_savename_suffix(tool, args, tool_context: ToolContext):
    output_file_suffix = get_suffix(args)
    tool_name = tool.name
    if output_file_suffix is None:
        return
    if tool_name in BUILD_PERIODIC_TOOS:
        if output_file_suffix not in AVAILABLE_PERIODIC_SUFFIX:
            raw_output_file = args.get('output_file')
            if len(raw_output_file) == 0 or raw_output_file is None:
                raw_output_file = 'structure'
            new_output_file = f"{raw_output_file.split('.')[0]}.cif"
            args['output_file'] = new_output_file
            logger.info(
                f"[regulate_savename_suffix] Updated output_file to {new_output_file}"
            )
    elif tool_name in BUILD_NONPERIODIC_TOOLS:
        if output_file_suffix not in AVAILABLE_NONPERIODIC_SUFFIX:
            raw_output_file = args.get('output_file')
            if len(raw_output_file) == 0 or raw_output_file is None:
                raw_output_file = 'structure'
            new_output_file = f"{raw_output_file.split('.')[0]}.xyz"
            args['output_file'] = new_output_file
            logger.info(
                f"[regulate_savename_suffix] Updated output_file to {new_output_file}"
            )


async def before_tool_callback(tool, args, tool_context: ToolContext):
    # First run the file URL validation
    await validate_file_urls(tool, args, tool_context)

    # Then run the existing suffix regulation
    await regulate_savename_suffix(tool, args, tool_context)


if __name__ == '__main__':
    import asyncio

    asyncio.run(regulate_savename_suffix(None, {}, None))
