import requests

from agents.matmaster_agent.constant import ICL_SERVICE_URL


def select_examples(query, logger):
    try:
        return requests.post(
            url=f"http://{ICL_SERVICE_URL}/api/v1/icl/select-examples",
            json={'query': query},
            timeout=10,
        ).json()['data']
    except Exception as e:
        logger.info(f"select_examples fallback due to error: {e}")
        return [{
        'input': '请为我构建一个铁的 bcc 结构',
        'update_input': '请构建铁的体心立方（bcc）晶体结构，空间群为Im-3m，晶格常数为2.87Å',
        'toolchain': ['build_bulk_structure_by_template', 'optimize_structure'],
        'scene_tags': ['structure_generate', 'optimize_structure'],
    }]
        


def select_update_examples(query, logger):
    try:
        return requests.post(
            url=f"http://{ICL_SERVICE_URL}/api/v1/icl/select-update-examples",
            json={'query': query},
            timeout=10,
        ).json()['data']
    except Exception as e:
        logger.info(f"select_update_examples fallback due to error: {e}")
        return [{
        'input': '请为我构建一个铁的 bcc 结构',
        'update_input': '请构建铁的体心立方（bcc）晶体结构，空间群为Im-3m，晶格常数为2.87Å',
        'toolchain': ['build_bulk_structure_by_template', 'optimize_structure'],
        'scene_tags': ['structure_generate', 'optimize_structure'],
    }]


def scene_tags_from_examples(examples):
    scene_prompts = ['\nSCENE_TAGS EXAMPLES:']
    for example in examples:
        if 'scene_tags' in example:
            scene_prompts.append(
                f"User Input: {example['update_input']}\nScenes: {', '.join(example['scene_tags'])}\n"
            )
    return '\n'.join(scene_prompts)

def toolchain_from_examples(examples):
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

def expand_input_examples(examples):
    expanded_inputs = ['\nEXPAND EXAMPLES:']
    for example in examples:
        if 'update_input' in example:
            expanded_inputs.append(
                f"Original Input: {example['input']}\nExpanded Input: {example['update_input']}\n"
            )
    return '\n'.join(expanded_inputs)
