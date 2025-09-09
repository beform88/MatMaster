import json


def load_dataset_json(json_file):
    with open(json_file, "r") as f:
        dataset_json = json.dumps(json.load(f))

    return dataset_json
