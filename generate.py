""" 
generate.py
 
 This file is part of phelix.
 
 Copyright 2024 Tim Barrass
 
 phelix is licensed under the GNU General Public Licence (GPL) Version 3 or later. 
"""

# this module takes a preset file and modifies it to be a valid preset for the pedalboard
# it loads and modifies the json, and then saves it back as a new file
import variables
import file
import util
import mutate
import choose
import process_preset


def add_cabs(preset):
    for dsp in ["dsp0", "dsp1"]:
        amp_blocks_list = []
        amp_blocks_list.extend(
            slot
            for slot in util.get_default_dsp(preset, dsp)
            if util.get_model_name(preset, dsp, slot).startswith("HD2_Amp")
        )
        for cabs_used, amp_slot in enumerate(amp_blocks_list):
            print("Adding cab...")
            cab_slot = f"cab{str(cabs_used)}"
            util.get_default_dsp_slot(preset, dsp, amp_slot)["@cab"] = cab_slot
            # load a random cab
            raw_cab_dict = file.load_block_dictionary(choose.random_block_file_in_category("Cab"))
            util.add_raw_block_to_preset(preset, dsp, cab_slot, raw_cab_dict)


def load_probabilities_block_dictionary_excluding_cabs_and_splits_checking_amps(num_amps):
    while True:
        block_dict = file.load_block_dictionary(choose.probabilities_block_file_excluding_cab_or_split())
        # Only return an amp block if num_amps is 0
        if num_amps == 0 and block_dict["Defaults"]["@model"].startswith("HD2_Amp"):
            num_amps += 1
            # print("amp, numamps = ", num_amps)
            return block_dict, num_amps
        # Otherwise, return a non-amp block
        elif not block_dict["Defaults"]["@model"].startswith("HD2_Amp"):
            # print("no amp, numamps = ", num_amps)
            return block_dict, num_amps


def swap_all_blocks_and_splits_from_files_using_probabilities(preset):
    for dsp in ["dsp0", "dsp1"]:
        print("\nPopulating " + dsp + "...")
        num_amps = 0
        for slot in util.get_default_dsp(preset, dsp):
            if slot.startswith("block"):
                path = util.get_default_dsp_slot(preset, dsp, slot)["@path"]
                pos = util.get_default_dsp_slot(preset, dsp, slot)["@position"]
                new_dict, num_amps = load_probabilities_block_dictionary_excluding_cabs_and_splits_checking_amps(num_amps)
                util.add_raw_block_to_preset(preset, dsp, slot, new_dict)
                util.get_default_dsp_slot(preset, dsp, slot)["@path"] = path
                util.get_default_dsp_slot(preset, dsp, slot)["@position"] = pos
            elif slot.startswith("split"):
                new_dict = file.load_block_dictionary(choose.random_block_file_in_category("Split"))
                util.add_raw_block_to_preset(preset, dsp, slot, new_dict)


def generate_preset_processor(preset, args, postfix_num):
    util.set_preset_name_for_generate(preset, args, postfix_num)
    util.add_dsp_controller_and_snapshot_keys_if_missing(preset)
    util.set_led_colours(preset)
    swap_all_blocks_and_splits_from_files_using_probabilities(preset)
    add_cabs(preset)
    mutate.change_topology(preset)
    choose.prune_controllers(preset)
    util.remove_empty_controller_dsp_slots(preset)
    mutate.change_some_controller_types(preset, variables.PEDAL_CONTROL, variables.NUM_PEDAL2_PARAMS)
    util.reinit_available_ccs()
    mutate.change_some_controller_types(preset, variables.CONTROLLER_MIDICC, variables.NUM_CC_PARAMS)
    mutate.mutate_values_ranges_and_states(preset, 1.0, 0.5)
    return preset

def main():
    process_preset.main(generate_preset_processor)


if __name__ == "__main__":
    main()
