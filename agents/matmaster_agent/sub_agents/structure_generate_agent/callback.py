from google.adk.tools import ToolContext

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
            print(
                f"[regulate_savename_suffix] Updated output_file to {new_output_file}"
            )
    elif tool_name in BUILD_NONPERIODIC_TOOLS:
        if output_file_suffix not in AVAILABLE_NONPERIODIC_SUFFIX:
            raw_output_file = args.get('output_file')
            if len(raw_output_file) == 0 or raw_output_file is None:
                raw_output_file = 'structure'
            new_output_file = f"{raw_output_file.split('.')[0]}.xyz"
            args['output_file'] = new_output_file
            print(
                f"[regulate_savename_suffix] Updated output_file to {new_output_file}"
            )


if __name__ == '__main__':
    import asyncio

    asyncio.run(regulate_savename_suffix(None, {}, None))
