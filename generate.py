""" 
generate.py
 
 This file is part of phelix.
 
 Copyright 2024 Tim Barrass
 
 phelix is licensed under the GNU General Public Licence (GPL) Version 3 or later. 
"""

# this module takes a preset file and modifies it to be a valid preset for the pedalboard
# it loads and modifies the json, and then saves it back as a new file
from datetime import datetime
import json
import sys

import variables
import file
import util
import mutate
import choose


def add_cabs(preset):
    for dsp in ["dsp0", "dsp1"]:

        amp_blocks_list = []
        for slot in util.get_default_dsp(preset, dsp):
            if util.get_model_name(preset, dsp, slot).startswith("HD2_Amp"):
                amp_blocks_list.append(slot)

        cabs_used = 0
        for amp_slot in amp_blocks_list:
            print("Adding cab...")
            cab_slot = "cab" + str(cabs_used)
            cabs_used += 1
            util.get_default_dsp_slot(preset, dsp, amp_slot)["@cab"] = cab_slot
            # load a random cab
            raw_cab_dict = file.load_block_dictionary(choose.random_block_file_in_category("Cab"))
            util.add_raw_block_to_preset(preset, dsp, cab_slot, raw_cab_dict)


def load_random_block_dictionary_excluding_cabs_and_splits_checking_amps(num_amps):
    while True:
        block_dict = file.load_block_dictionary(choose.random_block_file_excluding_cab_or_split())
        # Only return an amp block if num_amps is 0
        if num_amps == 0 and block_dict["Defaults"]["@model"].startswith("HD2_Amp"):
            num_amps += 1
            # print("amp, numamps = ", num_amps)
            return block_dict, num_amps
        # Otherwise, return a non-amp block
        elif not block_dict["Defaults"]["@model"].startswith("HD2_Amp"):
            # print("no amp, numamps = ", num_amps)
            return block_dict, num_amps


def populate_preset_with_random_blocks(preset):
    for dsp in ["dsp0", "dsp1"]:
        print("\nPopulating " + dsp + "...")
        num_amps = 0
        for slot in util.get_default_dsp(preset, dsp):
            # if not slot.startswith(("block", "split")):
            #     continue
            if slot.startswith("block"):
                new_dict, num_amps = load_random_block_dictionary_excluding_cabs_and_splits_checking_amps(num_amps)
                util.add_raw_block_to_preset(preset, dsp, slot, new_dict)
            elif slot.startswith("split"):
                new_dict = file.load_block_dictionary(choose.random_block_file_in_category("Split"))
                util.add_raw_block_to_preset(preset, dsp, slot, new_dict)


def swap_some_snapshot_controls_to_pedal(preset, pedal_control_num):
    print("\nSwapping some snapshot controls to pedal...")
    for _ in range(variables.NUM_PEDAL_PARAMS):
        choose.random_controlled_parameter_and_ranges(preset, pedal_control_num)


# def test(template_name, preset_name):
#     with open(template_name, "r") as f:
#         preset = json.load(f)
#         print("\nGenerating preset from template " + template_name + "...")
#         util.set_preset_name(preset, preset_name)
#         util.add_dsp_controller_and_snapshot_keys_if_missing(preset)
#         populate_preset_with_random_blocks(preset)
#         add_cabs(preset)
#         choose.move_splits_and_joins(preset)
#         mutate.mutate_parameter_values_for_all_snapshots(preset, 1.0)
#         mutate.mutate_values_in_all_default_blocks(preset, 1.0)


def generate_preset_from_template_file(template_name, save_name, preset_name):
    with open(template_name, "r") as f:
        preset = json.load(f)
        print("\nGenerating preset from template " + template_name + "...")
        util.set_preset_name(preset, preset_name)
        util.add_dsp_controller_and_snapshot_keys_if_missing(preset)
        populate_preset_with_random_blocks(preset)
        print()
        add_cabs(preset)
        choose.move_splits_and_joins(preset)
        print()
        mutate.mutate_parameter_values_for_all_snapshots(preset, 1.0)
        print()
        mutate.mutate_values_in_all_default_blocks(preset, 1.0)
        print()
        mutate.rearrange_blocks(preset, 1.0)
        choose.random_series_or_parallel_dsp_configuration(preset)
        choose.prune_controllers(preset)
        util.remove_empty_controller_dsp_slots(preset)
        swap_some_snapshot_controls_to_pedal(preset, variables.PEDAL_2)
        mutate.toggle_some_block_states(preset, 0.5)
        util.set_led_colours(preset)
        with open(save_name, "w") as json_file:
            json.dump(preset, json_file, indent=4)


def generate_multiple_presets_from_template(args):
    if args.get("preset_name") == "":
        now = datetime.now()
        preset_name_base = now.strftime("%y%m%d-%H%M")
    else:
        preset_name_base = args.get("preset_name")
    for i in range(args.get("num_presets")):
        i_str = str(i + 1).zfill(2)
        preset_name = f"{preset_name_base}-{i_str}"
        generate_preset_from_template_file(
            args.get("template_file"),
            args.get("output_file")[:-4] + str(i + 1) + ".hlx",
            preset_name,
        )


def main():
    # Parse the JSON string argument
    args = json.loads(sys.argv[1])

    generate_multiple_presets_from_template(args)


if __name__ == "__main__":
    main()
