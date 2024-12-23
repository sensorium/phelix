""" 
extractBlocks.py
 
 This file is part of phelix.
 
 Copyright 2024 Tim Barrass
 
 phelix is licensed under the GNU General Public Licence (GPL) Version 3 or later. 
"""

# this script extracts the params from snapshots to a json file in the blocks folder
# snapshots provide the max and min values for each parameter
# the snapshotted params need to be set by hand in hxedit (unless there's an automatic way to snapshot all params)


import json
import os
import variables


def extractBlocksFromPath(preset_dict, dsp, category_path):
    if dsp in preset_dict["data"]["tone"]["controller"]:
        print(dsp)
        for slot in preset_dict["data"]["tone"]["controller"][dsp]:
            if slot.startswith("block") or slot.startswith("cab") or slot.startswith("split"):
                block_dict = {}
                block_dict["SnapshotParams"] = preset_dict["data"]["tone"]["snapshot0"]["controllers"][dsp][slot]
                block_dict["Controller_Dict"] = preset_dict["data"]["tone"]["controller"][dsp][slot]
                block_dict["Defaults"] = preset_dict["data"]["tone"][dsp][slot]
                block_filename = preset_dict["data"]["tone"][dsp][slot]["@model"] + ".json"
                with open(os.path.join(category_path, block_filename), "w") as json_file:
                    json.dump(block_dict, json_file, indent=4)
                print(os.path.join(category_path, block_filename))


# This code defines a function that creates a directory
# named "blocks" in the current working directory based on the provided folder and presetName,
# loads a JSON file, and then calls a function to extract blocks from the JSON data
# for "dsp0" and "dsp1" into the created directory.


def extractControls(preset_path, category, preset_name):
    full_path = os.path.join(variables.BLOCKS_PATH, category)
    os.makedirs(full_path, exist_ok=True)
    with open(os.path.join(preset_path, preset_name), "r") as f:
        preset_dict = json.load(f)
        extractBlocksFromPath(preset_dict, "dsp0", full_path)
        extractBlocksFromPath(preset_dict, "dsp1", full_path)


extractControls("../phelix-out/sources", "Cab", "Cabs3.80.hlx")
