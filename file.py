import os
import json
import constants


# load extracted block parameters from a json file, return a dictionary
def load_block_dictionary(block_filepath):
    with open(os.path.expanduser(block_filepath), "r") as f:
        block_dict = json.load(f)
        # print("loaded " + block_filepath)
    return block_dict


def reload_unpruned_block_dictionary(preset, dsp, any_slot_name):
    block_filename = preset["data"]["tone"][dsp][any_slot_name]["@model"] + ".json"
    block_folder = None
    for root, _, files in os.walk(constants.BLOCKS_PATH):
        if block_filename in files:
            block_folder = root
            break
    # print("Reloading " + block_folder + "/" + block_filename)
    block_dict = load_block_dictionary(block_folder + "/" + block_filename)
    return block_dict


def save_debug_hlx(preset):
    with open("debug.hlx", "w") as json_file:
        json.dump(preset, json_file, indent=4)
