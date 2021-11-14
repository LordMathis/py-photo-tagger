import json


def read_json_file(filepath):
    with open(filepath) as json_data:
        file_data = json.load(json_data)
        return file_data


def write_json_file(filepath, data):
    with open(filepath, 'w') as json_file:
        json_file.write(json.dumps(data, indent=4))
