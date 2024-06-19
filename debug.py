import json


def save_debug_hlx(preset):
    with open("debug.hlx", "w") as json_file:
        json.dump(preset, json_file, indent=4)
