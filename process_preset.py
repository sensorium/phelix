"""
process_preset.py

 This file is part of phelix.

 Copyright 2024 Tim Barrass

 phelix is licensed under the GNU General Public Licence (GPL) Version 3 or later.
"""

import json
import sys
from datetime import datetime
import var


def process_multiple_presets(args, processor_func):
    """
    Handles the boilerplate of loading, looping, processing, and saving presets.

    :param args: Dictionary of arguments from the GUI.
    :param processor_func: A function that takes a preset dictionary and other
                           arguments, and returns a modified preset dictionary.
    """

    for i in range(args.get("num_presets")):
        with open(args.get("template_file"), "r") as f:
            preset = json.load(f)

        output_file = args.get("output_file")[:-4] + str(i + 1) + ".hlx"

        modified_preset = processor_func(preset, args, i + 1)

        with open(output_file, "w") as json_file:
            json.dump(modified_preset, json_file, indent=4)


def main(processor_func):
    args = json.loads(sys.argv[1])
    if "block_probabilities" in args:
        var.block_probabilities.update(args["block_probabilities"])
    if "runtime_settings" in args:
        runtime_settings = args["runtime_settings"]
        var.NUM_PEDAL2_PARAMS = int(runtime_settings.get("NUM_PEDAL2_PARAMS", var.NUM_PEDAL2_PARAMS))
        var.NUM_MIDICC_PARAMS = int(runtime_settings.get("NUM_MIDICC_PARAMS", var.NUM_MIDICC_PARAMS))
        var.NUM_SNAPSHOT_PARAMS = int(runtime_settings.get("NUM_SNAPSHOT_PARAMS", var.NUM_SNAPSHOT_PARAMS))
        var.BLOCKS_PATH = str(runtime_settings.get("BLOCKS_PATH", var.BLOCKS_PATH))
        var.MUTATION_RATE = float(runtime_settings.get("MUTATION_RATE", var.MUTATION_RATE))
        var.FRACTION_MOVE = float(runtime_settings.get("FRACTION_MOVE", var.FRACTION_MOVE))
        var.TOGGLE_RATE = float(runtime_settings.get("TOGGLE_RATE", var.TOGGLE_RATE))
    process_multiple_presets(args, processor_func)