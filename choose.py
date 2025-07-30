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


def probabilities_block_file_excluding_cab_or_split():
    random_category = random_block_category_using_probabilities()
    while random_category in ["Split", "Cab"]:
        random_category = random_block_category_using_probabilities()
    return random_block_file_in_category(random_category)


def random_block_file_in_category(category_folder):
    folder_path = os.path.join(variables.BLOCKS_PATH, category_folder)
    block_files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
    return os.path.join(folder_path, random.choice(block_files))


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
    params.extend(iter(util.get_controller_dsp(preset, dsp)[slot]))
    return random.choice(params) if params else "none"


def random_pedal_parameter(preset):
    dsp, slot = random_controller_dsp_and_block(preset)
    if slot != "none":
        if params := [
            param
            for param in util.get_controller_dsp_slot(preset, dsp, slot)
            if param not in ["Mic", "Position", "Distance", "Angle"]
            # and param["@controller"] != variables.MIDI_CC_CONTROL
        ]:
            param = random.choice(params)
            util.set_controller_type(preset, dsp, slot, param, variables.PEDAL_CONTROL_2)
            random_max_and_min_for_controlled_param(preset, dsp, slot, param)
            log_controller_assignment(dsp, slot, util.get_model_name(preset, dsp, slot), param, variables.PEDAL_CONTROL_2)


def random_cc_parameter(preset):
    dsp, slot = random_controller_dsp_and_block(preset)
    if slot != "none":
        if params := [
            param
            for param in util.get_controller_dsp_slot(preset, dsp, slot)
            if param not in ["Mic", "Position", "Distance", "Angle"]
            # and param["@controller"] != variables.PEDAL_CONTROL_2
        ]:
            param = random.choice(params)
            util.set_controller_type(preset, dsp, slot, param, variables.MIDI_CC_CONTROL)
            util.add_controller_block_parameter_cc(preset, dsp, slot, param, util.nextCC())
            random_max_and_min_for_controlled_param(preset, dsp, slot, param)
            log_controller_assignment(dsp, slot, util.get_model_name(preset, dsp, slot), param, variables.MIDI_CC_CONTROL)


def random_snapshot_parameter(preset):
    dsp, slot = random_controller_dsp_and_block(preset)
    if slot != "none":
        if params := list(util.get_controller_dsp_slot(preset, dsp, slot)):
            param = random.choice(params)
            util.set_controller_type(preset, dsp, slot, param, variables.SNAPSHOT_CONTROL)
            random_max_and_min_for_controlled_param(preset, dsp, slot, param)
            log_controller_assignment(dsp, slot, util.get_model_name(preset, dsp, slot), param, variables.SNAPSHOT_CONTROL)


def log_controller_assignment(dsp, slot, model_name, param, control_type):
    print(f"  set {dsp}", slot, model_name, param, f"to controller {str(control_type)}")   


def random_max_and_min_for_controlled_param(preset, dsp, slot, parameter):
    print(
        f"set_random_max_and_min_for_controlled_param {str(dsp)}{str(slot)}{str(parameter)}"
    )
    controlled_param = util.get_controller_dsp_slot_parameter(preset, dsp, slot, parameter)
    block_dict = file.reload_raw_block_dictionary(preset, dsp, slot)["Controller_Dict"]
    pmin = block_dict[parameter]["@min"]
    pmax = block_dict[parameter]["@max"]
    new_max = random.uniform(pmin, pmax)
    new_min = random.uniform(pmin, pmax)
    controlled_param["@max"] = new_max
    controlled_param["@min"] = new_min


def random_block_category_using_probabilities() -> str:
    # make 1 choice with weighted probabilities
    return random.choices(
        list(variables.block_probabilities.keys()),
        weights=[float(w) for w in list(variables.block_probabilities.values())],
        k=1,
    )[0]


def random_remove_controls(preset, control_type, num_changes):
    controlled_param_list = util.list_controls_of_type(preset, control_type)
    if len(controlled_param_list) != 0:
        for _ in range(num_changes):
            random_controller_to_snapshot(preset, controlled_param_list, control_type)


def random_new_params_for_snapshot_control(preset):
    num_controllers_to_change = random.randint(0, 20)
    for _ in range(num_controllers_to_change):
        remove_one_random_controller_parameter(preset)
    grow_snapshot_controllers(preset)


def random_controller_to_snapshot(preset, param_list, control_type):
    # choose a block,param pair
    random_index = random.randint(0, len(param_list) - 1)
    dsp, slot, parameter = param_list[random_index]
    # set control to snapshot
    util.get_controller_dsp_slot_parameter(preset, dsp, slot, parameter)["@controller"] = variables.SNAPSHOT_CONTROL
    print(
        f"  set control {str(control_type)} to snapshot {str(control_type)} for {dsp}",
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


def add_random_parameter_to_controller(preset, control_type):
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
        #util.add_parameter_to_controller(preset, dsp, slot, random_param, raw_block_dict)
        util.add_controller_block_parameter_and_control_type(
            preset, dsp, slot, random_param, raw_block_dict, control_type
        )
        # if control_type == variables.MIDI_CC_CONTROL:
        #     util.add_controller_block_parameter_cc(preset, dsp, slot, random_param, util.nextCC())
        util.add_parameter_to_all_snapshots(preset, dsp, slot, random_param, raw_block_dict)



def random_series_or_parallel_dsp_configuration(preset):
    preset["data"]["tone"]["dsp0"]["outputA"]["@output"] = random.choice([1, 2])


def prune_controllers(preset):
    print("\nPruning controls to "+ str(variables.MAXIMUM_CONTROLLERS))
    while util.count_parameters_in_controller(preset) > variables.MAXIMUM_CONTROLLERS:
        remove_one_random_controller_parameter(preset)


def grow_snapshot_controllers(preset):
    max_controllers = min(util.count_controllable_parameters_in_preset(preset), variables.MAXIMUM_CONTROLLERS)
    print("\nGrowing controls to maximum ", max_controllers)
    while util.count_parameters_in_controller(preset) < max_controllers - 1:
        add_random_parameter_to_controller(preset, variables.SNAPSHOT_CONTROL)


""" def cc_controllers_for_default_blocks(preset):
    print("\nchoose.controllers_for_default_blocks")
    for _ in range(util.num_ccs_spare()):
        add_random_parameter_to_controller(preset, variables.MIDI_CC_CONTROL) """


def move_split_and_join(preset, dsp):
    join_position = random.randint(variables.NUM_POSITIONS_PER_PATH - 4, variables.NUM_POSITIONS_PER_PATH)
    split_position = random.randint(0, join_position - 3)
    preset["data"]["tone"][dsp]["join"]["@position"] = join_position
    preset["data"]["tone"][dsp]["split"]["@position"] = split_position


def move_splits_and_joins(preset):
    for dsp in util.get_available_default_dsps(preset):
        move_split_and_join(preset, dsp)
