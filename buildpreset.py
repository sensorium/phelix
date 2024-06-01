# this module takes a preset file and modifies it to be a valid preset for the pedalboard
# it loads and modifies the json, and then saves it back as a new file
from datetime import datetime
import os
import json
import random
from copy import deepcopy
import sys
import mutate


# todo:

# make wahs frequently have pedal control - if exp1, then the default val can be randomly chosen


# refactored print statements to use sys.stdout.write
def print_with_stdout_write(message):
    sys.stdout.write(message)
    sys.stdout.flush()


# load a template preset from a json file, return a dictionary
def load_preset_from_file(preset_file):
    with open(os.path.expanduser(preset_file), "r") as f:
        preset_dict = json.load(f)
    return preset_dict


# return a random number biased between max and min
# from https://stackoverflow.com/questions/29325069/how-to-generate-random-numbers-biased-towards-one-value-in-a-range
def getRndBias(minval, maxval, bias, influence):
    rnd = random.uniform(minval, maxval)  # random number in the min-max range
    mix = random.uniform(0, 1) * influence  # random normalized mix value
    return rnd * (1 - mix) + bias * mix  # Mix random with bias based on random mix


# if an amp is chosen
# choose a cab


def addCabs(preset_dict, dsp_name):
    # list all cabs in blocks folder
    cabs_file_list = []
    for filename in os.listdir(mutate.BLOCKS_PATH + "/Cab/"):
        if filename.startswith("HD2_Cab"):
            cabs_file_list.append(filename)

    # keep track of how many cabs used
    cabs_used = 0

    amp_blocks_list = []
    for block_name in preset_dict["data"]["tone"][dsp_name]:
        if preset_dict["data"]["tone"][dsp_name][block_name]["@model"].startswith("HD2_Amp"):
            amp_blocks_list.append(block_name)

    for amp in amp_blocks_list:
        # add a cab
        cab_name = "cab" + str(cabs_used)
        cabs_used += 1
        preset_dict["data"]["tone"][dsp_name][amp]["@cab"] = cab_name
        # load a random cab
        cab_dict = mutate.load_block_dictionary(mutate.BLOCKS_PATH + "/Cab/" + random.choice(cabs_file_list))
        # delete cab path and position, if they exist
        if "@path" in cab_dict["Defaults"]:
            del cab_dict["Defaults"]["@path"]
        if "@position" in cab_dict["Defaults"]:
            del cab_dict["Defaults"]["@position"]
        preset_dict["data"]["tone"][dsp_name][cab_name] = cab_dict["Defaults"]


def loadRandomBlockParamsForOneBlockNoCabNoSplitCheckAmps(num_amps):
    while True:
        block_dict = mutate.load_block_dictionary(mutate.choose_random_block_file_excluding_cab_or_split())
        if not block_dict["Defaults"]["@model"].startswith("HD2_Amp") or num_amps < 1:
            break
    return block_dict


# insert param keys into each snapshot in preset
def initialize_preset_with_random_blocks(preset_dict, dsp_name):
    num_amps = 0

    add_controller_and_dsp_keys_if_missing(preset_dict, dsp_name)

    block_positions_path0 = [i for i in range(mutate.last_block_position)]
    random.shuffle(block_positions_path0)
    block_positions_path1 = [i for i in range(mutate.last_block_position)]
    random.shuffle(block_positions_path1)

    for destination_block_name in preset_dict["data"]["tone"][dsp_name]:
        if destination_block_name.startswith(
            "block"
        ):  # or block_name.startswith("cab"): # cabs will be sorted with amps later, but cabs in amps will take an extra position at this step
            new_block_dict = loadRandomBlockParamsForOneBlockNoCabNoSplitCheckAmps(num_amps)
            num_amps = increment_amp_count_if_amp_block(num_amps, new_block_dict)
            preset_dict["data"]["tone"][dsp_name][destination_block_name] = new_block_dict["Defaults"]
            # print("       loaded " + destination_block_name + " " + new_block_dict["Defaults"]["@model"])

            path_num = random.randint(0, 1)
            set_path_and_position_for_block(
                preset_dict,
                dsp_name,
                destination_block_name,
                path_num,
                block_positions_path0,
                block_positions_path1,
            )

            add_block_parameters_to_controller(preset_dict, dsp_name, destination_block_name, new_block_dict)
            mutate.insert_block_parameters_into_all_snapshots(
                preset_dict, dsp_name, destination_block_name, new_block_dict
            )

        elif destination_block_name.startswith("split"):
            split_dict = chooseSplit()
            preset_dict["data"]["tone"][dsp_name]["split"] = deepcopy(split_dict["Defaults"])
            preset_dict["data"]["tone"]["controller"][dsp_name][destination_block_name] = split_dict["Ranges"]
            for snapshot_num in range(mutate.NUM_SNAPSHOTS):
                snapshot_name = "snapshot" + str(snapshot_num)
                preset_dict["data"]["tone"][snapshot_name]["controllers"][dsp_name][destination_block_name] = deepcopy(
                    split_dict["SnapshotParams"]
                )

    join_position = random.randint(mutate.last_block_position - 3, mutate.last_block_position)
    split_position = random.randint(0, join_position - 3)

    preset_dict["data"]["tone"][dsp_name]["join"]["@position"] = join_position
    preset_dict["data"]["tone"][dsp_name]["split"]["@position"] = split_position


def add_controller_and_dsp_keys_if_missing(preset_dict, dsp_name):
    if "controller" not in preset_dict["data"]["tone"]:
        preset_dict["data"]["tone"]["controller"] = {}
    if dsp_name not in preset_dict["data"]["tone"]["controller"]:
        preset_dict["data"]["tone"]["controller"][dsp_name] = {}
        for snapshot_num in range(mutate.NUM_SNAPSHOTS):
            snapshot_name = "snapshot" + str(snapshot_num)
            preset_dict["data"]["tone"][snapshot_name]["controllers"][dsp_name] = {}


def increment_amp_count_if_amp_block(num_amps, block_dict):
    if block_dict["Defaults"]["@model"].startswith("HD2_Amp"):
        num_amps += 1
    return num_amps


def set_path_and_position_for_block(
    preset_dict,
    dsp_name,
    block_name,
    path_num,
    block_positions_path0,
    block_positions_path1,
):
    preset_dict["data"]["tone"][dsp_name][block_name]["@path"] = path_num
    if path_num == 0:
        preset_dict["data"]["tone"][dsp_name][block_name]["@position"] = block_positions_path0.pop()
    else:
        preset_dict["data"]["tone"][dsp_name][block_name]["@position"] = block_positions_path1.pop()


def add_block_parameters_to_controller(preset_dict, dsp_name, block_name, block_dict):
    preset_dict["data"]["tone"]["controller"][dsp_name][block_name] = block_dict["Ranges"]


def chooseSplit():
    # list all splits in split folder
    splits_file_list = [
        "HD2_AppDSPFlowSplitAB",
        "HD2_AppDSPFlowSplitDyn",
        "HD2_AppDSPFlowSplitXOver",
    ]
    weights = [0.5, 0.25, 0.25]
    split_file = "".join(random.choices(splits_file_list, weights, k=1))
    # print("       loading " + split_file)
    return mutate.load_block_dictionary(mutate.BLOCKS_PATH + "/Split/" + split_file + ".json")


def randomly_activate_or_deactivate_blocks(preset_dict, dsp_name):
    for snapshot_num in range(mutate.NUM_SNAPSHOTS):
        snapshot_name = "snapshot" + str(snapshot_num)
        if dsp_name in preset_dict["data"]["tone"][snapshot_name]["blocks"]:
            for block in preset_dict["data"]["tone"][snapshot_name]["blocks"][dsp_name]:
                if block.startswith("block") or block.startswith("cab"):
                    state = False
                    if random.uniform(0, 1) < 0.7:
                        state = True
                    preset_dict["data"]["tone"][snapshot_name]["blocks"][dsp_name][block] = state


def generate_preset_from_saved_blocks(preset_dict, dsp_name):
    print("\nGenerating " + dsp_name + "...")
    initialize_preset_with_random_blocks(preset_dict, dsp_name)
    mutate.mutate_parameter_values_for_all_snapshots(preset_dict)
    addCabs(preset_dict, dsp_name)
    randomly_activate_or_deactivate_blocks(preset_dict, dsp_name)


def set_preset_name(preset_dict, preset_name):
    print("Preset name: " + preset_name)
    preset_dict["data"]["meta"]["name"] = preset_name


def replace_parameters_with_pedal_controllers(preset_dict, pedalnum):
    print("Adding pedal controls...")
    for i in range(mutate.NUM_PEDAL_PARAMS):
        mutate.choose_random_pedal_parameter_and_ranges(preset_dict, pedalnum)


def generate_preset_from_template_file(template_name, save_name, preset_name):
    with open(template_name, "r") as f:
        preset_dict = json.load(f)

        print("\nGenerating preset from template " + template_name + "...")
        set_preset_name(preset_dict, preset_name)

        generate_preset_from_saved_blocks(preset_dict, "dsp0")
        generate_preset_from_saved_blocks(preset_dict, "dsp1")

        choose_series_or_parallel_dsp_configuration(preset_dict)

        print("\nReducing number of snapshot and pedal controlled parameters to maximum 64...")
        while mutate.count_parameters_in_controller(preset_dict) > 64:
            mutate.remove_one_random_controller_parameter(preset_dict)

        print()

        replace_parameters_with_pedal_controllers(preset_dict, 2)

        mutate.set_led_colours(preset_dict)

        with open(save_name, "w") as json_file:
            json.dump(preset_dict, json_file, indent=4)


def choose_series_or_parallel_dsp_configuration(preset_dict):
    preset_dict["data"]["tone"]["dsp0"]["outputA"]["@output"] = random.choice([1, 2])


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
