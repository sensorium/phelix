import os
import json
import constants
import debug
import util


# load extracted block parameters from a json file, return a dictionary
def load_block_dictionary(block_filepath):
    with open(os.path.expanduser(block_filepath), "r") as f:
        block_dict = json.load(f)
        # print("loaded " + block_filepath)
    return block_dict


def reload_raw_block_dictionary(preset, dsp, slot):
    # debug.save_debug_hlx(preset)
    block_filename = f"{util.get_model_name(preset, dsp, slot)}.json"
    # print(f"loading {block_filename}")
    block_folder = None
    for root, _, files in os.walk(constants.BLOCKS_PATH):
        if block_filename in files:
            block_folder = root
            break
    return load_block_dictionary(f"{block_folder}/{block_filename}")
