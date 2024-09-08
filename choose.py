""" 
choose.py
 
 This file is part of phelix.
 
 Copyright 2024 Tim Barrass
 
 phelix is licensed under the GNU General Public Licence (GPL) Version 3 or later. 
"""

import os
import random
import variables
import util
import file


def random_block_file_excluding_cab_or_split():
    random_category = random_block_category()
    while random_category in ["Split", "Cab"]:
        random_category = random_block_category()
    return random_block_file_in_category(random_category)


def random_block_file_in_category(category_folder):
    folder_path = os.path.join(variables.BLOCKS_PATH, category_folder)
    block_files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
    filepath = os.path.join(folder_path, random.choice(block_files))
    # print(f"  choosing {filepath}")
    return filepath


def random_block_split_or_cab_in_default_dsps(preset):
    dsp = random.choice(util.get_available_default_dsps(preset))
    slot = random.choice(list(util.get_default_dsp(preset, dsp).keys()))
    if slot.startswith(("block", "split", "cab")):
        return dsp, slot
    else:
        return random_block_split_or_cab_in_default_dsps(preset)


def random_controller_dsp_and_block(preset):
    # returns a random block, or "none" if there are no blocks
    found_blocks = []
    for dsp in util.get_controller(preset):
        found_blocks.extend((dsp, slot) for slot in util.get_controller_dsp(preset, dsp))
    return random.choice(found_blocks) if found_blocks else ["none", "none"]


def random_controller_param(preset, dsp, slot):
    # returns a random param, or "none" if there are no params
    # print("getRandControllerParam for "+dsp+" "+block)
    params = []
    for param in util.get_controller_dsp(preset, dsp)[slot]:
        params.append(param)
        # print("append to getRandControllerParam choices " +param)
    randparam = "none"
    if len(params) > 0:
        randparam = random.choice(params)
    return randparam


def random_controller_param_excluding_bools_and_mic(preset, dsp, slot):
    # returns a random param (but not one with a boolean value), or "none" if there are no params
    params = []
    for param in util.get_controller_dsp_slot(preset, dsp, slot):
        if (
            not isinstance(
                util.get_controller_dsp_slot(preset, dsp, slot)[param]["@min"],
                bool,
            )
            and param != "Mic"
        ):
            params.append(param)
            # print("append to getRandControllerParamNoBool choices " +param)
    randparam = "none"
    if len(params) > 0:
        randparam = random.choice(params)
    return randparam


def random_controller_param_excluding_bools_and_cabparams(preset, dsp, slot):
    # returns a random param (but not one with a boolean value), or "none" if there are no params
    params = []
    for param in util.get_controller_dsp_slot(preset, dsp, slot):
        if not isinstance(
            util.get_controller_dsp_slot(preset, dsp, slot)[param]["@min"],
            bool,
        ) and param not in ["Mic", "Position", "Distance", "Angle"]:
            params.append(param)
            # print("append to getRandControllerParamNoBool choices " +param)
    randparam = "none"
    if len(params) > 0:
        randparam = random.choice(params)
    return randparam


def random_controlled_parameter_and_ranges(preset, control_num):
    dsp, slot = random_controller_dsp_and_block(preset)
    if slot != "none":
        if control_num in [variables.PEDAL_2, variables.MIDI_CC_CONTROL]:
            param = random_controller_param_excluding_bools_and_cabparams(preset, dsp, slot)
        else:
            param = random_controller_param(preset, dsp, slot)
        if param != "none":
            set_controller_num(preset, control_num, dsp, slot, param)
            set_random_max_and_min_for_controlled_param(preset, dsp, slot, param)
            print(
                f"  set {dsp}",
                slot,
                util.get_model_name(preset, dsp, slot),
                param,
                f"to controller {str(control_num)}",
            )


def set_controller_num(preset, control_num, dsp, slot, parameter):
    controlled_param = util.get_controller_dsp(preset, dsp)[slot][parameter]
    controlled_param["@controller"] = control_num


def set_random_max_and_min_for_controlled_param(preset, dsp, slot, parameter):
    controlled_param = util.get_controller_dsp(preset, dsp)[slot][parameter]
    # controlled_param["@controller"] = control_num
    new_max = random.uniform(controlled_param["@min"], controlled_param["@max"])
    new_min = random.uniform(controlled_param["@min"], controlled_param["@max"])
    # set new random max and min values within the original limits
    controlled_param["@max"] = new_max
    controlled_param["@min"] = new_min


def random_block_category() -> str:
    # make 1 choice with weighted probabilities
    return random.choices(
        list(variables.block_probabilities.keys()),
        weights=list(variables.block_probabilities.values()),
        k=1,
    )[0]


def random_remove_controls(preset, control_num, num_changes):
    controlled_param_list = util.list_pedal_controls(preset, control_num)
    if len(controlled_param_list) != 0:
        for _ in range(num_changes):
            random_controller_to_snapshot(preset, controlled_param_list, control_num)


def random_new_params_for_snapshot_control(preset):
    num_controllers_to_change = random.randint(0, 20)
    for _ in range(num_controllers_to_change):
        remove_one_random_controller_parameter(preset)
    grow_controllers(preset)


def random_controller_to_snapshot(preset, param_list, control_num):
    # choose a block,param pair
    random_index = random.randint(0, len(param_list) - 1)
    dsp, slot, parameter = param_list[random_index]
    # set control to snapshot
    util.get_controller_dsp_slot_parameter(preset, dsp, slot, parameter)["@controller"] = variables.SNAPSHOT_CONTROL
    print(
        f"  set control {str(control_num)} to snapshot {str(control_num)} for {dsp}",
        slot,
        util.get_model_name(preset, dsp, slot),
        parameter,
    )


def remove_one_random_controller_parameter(preset):
    # delete a param if the random choice exists
    randdsp, randblock = random_controller_dsp_and_block(preset)
    if randblock != "none":
        randparam = random_controller_param(preset, randdsp, randblock)
        if randparam != "none":
            # remove the param from all snapshots
            util.remove_parameter_from_all_snapshots(preset, randdsp, randblock, randparam)

            # remove param from controller
            util.remove_parameter_from_controller(preset, randdsp, randblock, randparam)


def add_random_parameter_to_controller(preset):
    dsp, slot = random_block_split_or_cab_in_default_dsps(preset)
    # model_name = utils.get_model_name(preset, dsp, slot)
    # print(
    #     f"  add_random_parameter_to_controller from {dsp}",
    #     slot,
    #     util.get_model_name(preset, dsp, slot),
    # )
    if slot not in util.get_controller_dsp(preset, dsp):
        util.get_controller_dsp(preset, dsp)[slot] = {}
    raw_block_dict = file.reload_raw_block_dictionary(preset, dsp, slot)
    if params_not_in_controller := [
        param
        for param in raw_block_dict["Controller_Dict"]
        if param not in util.get_controller_dsp_slot(preset, dsp, slot)
    ]:
        random_param = random.choice(params_not_in_controller)
        # print(f"params_not_in_controller {params_not_in_controller}")
        util.add_parameter_to_controller(preset, dsp, slot, random_param, raw_block_dict)
        util.add_parameter_to_all_snapshots(preset, dsp, slot, random_param, raw_block_dict)


def random_series_or_parallel_dsp_configuration(preset):
    preset["data"]["tone"]["dsp0"]["outputA"]["@output"] = random.choice([1, 2])


def prune_controllers(preset):
    print("\nPruning controls to maximum 64...")
    while util.count_parameters_in_controller(preset) > variables.MAXIMUM_CONTROLLERS:
        remove_one_random_controller_parameter(preset)


def grow_controllers(preset):
    max_controllers = min(util.count_controllable_parameters_in_preset(preset), variables.MAXIMUM_CONTROLLERS)
    print("\nGrowing controls to maximum ", max_controllers)
    while util.count_parameters_in_controller(preset) < max_controllers - 1:
        add_random_parameter_to_controller(preset)


def move_split_and_join(preset, dsp):
    join_position = random.randint(variables.NUM_POSITIONS_PER_PATH - 4, variables.NUM_POSITIONS_PER_PATH)
    split_position = random.randint(0, join_position - 3)
    preset["data"]["tone"][dsp]["join"]["@position"] = join_position
    preset["data"]["tone"][dsp]["split"]["@position"] = split_position


def move_splits_and_joins(preset):
    for dsp in util.get_available_default_dsps(preset):
        move_split_and_join(preset, dsp)
