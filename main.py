# this module takes a preset file and modifies it to be a valid preset for the pedalboard
# it loads and modifies the json, and then saves it back as a new file
from datetime import datetime
import json
import random
import sys

import constants
import file
import utils
import mutate
import choose


def addCabs(preset):
    for dsp in ["dsp0", "dsp1"]:
        # keep track of how many cabs used
        cabs_used = 0

        amp_blocks_list = []
        for amp_slot in preset["data"]["tone"][dsp]:
            if preset["data"]["tone"][dsp][amp_slot]["@model"].startswith("HD2_Amp"):
                amp_blocks_list.append(amp_slot)

        for amp in amp_blocks_list:
            print("Adding cab...")
            cab_slot = "cab" + str(cabs_used)
            cabs_used += 1
            preset["data"]["tone"][dsp][amp]["@cab"] = cab_slot
            # load a random cab
            cab_dict = file.load_block_dictionary(choose.random_block_file_in_category("Cab"))
            # delete cab path and position, if they exist
            if "@path" in cab_dict["Defaults"]:
                del cab_dict["Defaults"]["@path"]
            if "@position" in cab_dict["Defaults"]:
                del cab_dict["Defaults"]["@position"]
            utils.add_block_to_preset(preset, dsp, cab_slot, cab_dict)


def load_random_block_dictionary_excluding_cabs_and_splits_checking_amps(num_amps):

    while True:
        block_dict = file.load_block_dictionary(choose.random_block_file_excluding_cab_or_split())
        if num_amps == 0 or not block_dict["Defaults"]["@model"].startswith("HD2_Amp"):
            if block_dict["Defaults"]["@model"].startswith("HD2_Amp"):
                num_amps += 1
            break
        # else:
        #     num_amps += 1
    print("num_amps = " + str(num_amps))
    return block_dict, num_amps


# insert param keys into each snapshot in preset
def populate_preset_with_random_blocks(preset):
    for dsp in ["dsp0", "dsp1"]:
        print("\nPopulating " + dsp + "...")
        num_amps = 0
        add_controller_and_snapshot_keys_if_missing(preset, dsp)

        for slot in preset["data"]["tone"][dsp]:
            if not slot.startswith(("block", "split")):
                continue
            if slot.startswith("block"):
                new_dict, num_amps = load_random_block_dictionary_excluding_cabs_and_splits_checking_amps(num_amps)
            elif slot.startswith("split"):
                new_dict = file.load_block_dictionary(choose.random_block_file_in_category("Split"))

            utils.add_block_to_preset(preset, dsp, slot, new_dict)

        join_position = random.randint(constants.LAST_SLOT_POSITION - 3, constants.LAST_SLOT_POSITION)
        split_position = random.randint(0, join_position - 3)

        preset["data"]["tone"][dsp]["join"]["@position"] = join_position
        preset["data"]["tone"][dsp]["split"]["@position"] = split_position


def add_controller_and_snapshot_keys_if_missing(preset_dict, dsp_name):
    if "controller" not in preset_dict["data"]["tone"]:
        preset_dict["data"]["tone"]["controller"] = {}
    if dsp_name not in preset_dict["data"]["tone"]["controller"]:
        preset_dict["data"]["tone"]["controller"][dsp_name] = {}
        for snapshot_num in range(constants.NUM_SNAPSHOTS):
            snapshot_name = "snapshot" + str(snapshot_num)
            preset_dict["data"]["tone"][snapshot_name]["controllers"][dsp_name] = {}


def set_preset_name(preset_dict, preset_name):
    print("Preset name: " + preset_name)
    preset_dict["data"]["meta"]["name"] = preset_name


def swap_some_snapshot_controls_to_pedal(preset_dict, pedal_control_num):
    print("\nSwapping some snapshot controls to pedal...")
    for _ in range(constants.NUM_PEDAL_PARAMS):
        choose.random_controlled_parameter_and_ranges(preset_dict, pedal_control_num)


def generate_preset_from_template_file(template_name, save_name, preset_name):
    with open(template_name, "r") as f:
        preset_dict = json.load(f)

        print("\nGenerating preset from template " + template_name + "...")
        set_preset_name(preset_dict, preset_name)

        populate_preset_with_random_blocks(preset_dict)
        # print("finished populating")
        addCabs(preset_dict)

        print()
        # print("about to mutate")
        mutate.mutate_parameter_values_for_all_snapshots(preset_dict)
        # print("finished mutating")
        print()

        mutate.rearrange_block_positions(preset_dict, 1.0)

        choose.random_series_or_parallel_dsp_configuration(preset_dict)

        print("\nPruning controls to maximum 64...")
        while utils.count_parameters_in_controller(preset_dict) > 64:
            choose.remove_one_random_controller_parameter(preset_dict)

        swap_some_snapshot_controls_to_pedal(preset_dict, constants.PEDAL_2)
        mutate.toggle_some_block_states(preset_dict, 0.5)

        mutate.set_led_colours(preset_dict)

        with open(save_name, "w") as json_file:
            json.dump(preset_dict, json_file, indent=4)


# def generate_multiple_presets_from_template(args):
#     now = datetime.now()
#     preset_name_base = now.strftime("%y%m%d-%H%M")
#     for i in range(args.num_presets):
#         preset_name = preset_name_base + chr(ord("a") + (i % 26))
#         generate_preset_from_template_file(
#             args.template_file,
#             args.output_file[:-4] + str(i + 1) + ".hlx",
#             preset_name,
#         )


def generate_multiple_presets_from_template(args):
    now = datetime.now()
    preset_name_base = now.strftime("%y%m%d-%H%M")
    for i in range(args.get("num_presets")):
        preset_name = preset_name_base + chr(ord("a") + (i % 26))
        generate_preset_from_template_file(
            args.get("template_file"),
            args.get("output_file")[:-4] + str(i + 1) + ".hlx",
            preset_name,
        )


# def generate_multiple_presets_from_template_gui(template_file, output_file, preset_name, num_presets):
#     now = datetime.now()
#     preset_name_base = now.strftime("%y%m%d-%H%M")
#     for i in range(num_presets):
#         preset_name_i = preset_name_base + chr(ord("a") + (i % 26))
#         generate_preset_from_template_file(
#             template_file,
#             output_file[:-4] + str(i + 1) + ".hlx",
#             preset_name_i,
#         )


def main():
    # Parse the JSON string argument
    args = json.loads(sys.argv[1])

    generate_multiple_presets_from_template(args)


if __name__ == "__main__":
    main()

# generate_multiple_presets_from_template(args)
# mutate.mutations(5)
