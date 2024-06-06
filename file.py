import os
import json

BLOCKS_PATH = "blocks/test"


# load a template preset from a json file, return a dictionary
def load_preset_from_file(preset_file):
    with open(os.path.expanduser(preset_file), "r") as f:
        preset_dict = json.load(f)
    return preset_dict


# load extracted block parameters from a json file, return a dictionary
def load_block_dictionary(block_filename):
    with open(os.path.expanduser(block_filename), "r") as f:
        block_dict = json.load(f)
        print("loaded " + block_filename)
    return block_dict


def load_block_dictionary_from_file(preset_dict, dsp_name, any_slot_name):
    block_filename = preset_dict["data"]["tone"][dsp_name][any_slot_name]["@model"] + ".json"
    block_folder = None
    for root, _, files in os.walk(BLOCKS_PATH):
        if block_filename in files:
            block_folder = root
            break
    print("Loading " + block_folder + "/" + block_filename)
    block_dict = load_block_dictionary(block_folder + "/" + block_filename)
    return block_dict
