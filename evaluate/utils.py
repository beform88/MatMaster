import json


def load_dataset_json(json_file):
    with open(json_file, encoding='utf-8') as f:
        dataset_json = json.dumps(json.load(f))

    return dataset_json
