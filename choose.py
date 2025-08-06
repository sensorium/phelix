""" 
choose.py
 
 This file is part of phelix.
 
 Copyright 2024 Tim Barrass
 
 phelix is licensed under the GNU General Public Licence (GPL) Version 3 or later. 
"""

import os
import random

from numpy import delete
import var
import util
import file


def probabilities_block_file_excluding_cab_or_split():
    random_category = random_block_category_using_probabilities()
    while random_category in ["Split", "Cab"]:
        random_category = random_block_category_using_probabilities()
    return random_block_file_in_category(random_category)


def random_block_file_in_category(category_folder):
    folder_path = os.path.join(var.BLOCKS_PATH, category_folder)
    block_files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
    return os.path.join(folder_path, random.choice(block_files))


def random_block_split_or_cab_in_default_dsps(preset):
    found_blocks_splits_cabs = []
    for dsp in util.get_available_default_dsp_names(preset):
        found_blocks_splits_cabs.extend(
            (dsp, slot)
            for slot in util.get_default_dsp(preset, dsp)
            if slot.startswith(("block", "split", "cab"))
        )
    return random.choice(found_blocks_splits_cabs) if found_blocks_splits_cabs else ["none", "none"]


def random_controller_dsp_and_slot(preset):
    # returns a random block, or "none" if there are no blocks
    found_blocks = []
    for dsp in util.get_controller(preset):
        found_blocks.extend((dsp, slot) for slot in util.get_controller_dsp(preset, dsp))
    return random.choice(found_blocks) if found_blocks else ["none", "none"]


def random_controller_slot_param(preset, dsp, slot):
    # returns a random param, or "none" if there are no params
    # print("getRandControllerParam for "+dsp+" "+block)
    params = []
    params.extend(iter(util.get_controller_dsp(preset, dsp)[slot]))
    return random.choice(params) if params else "none"


def list_params_assigned_to_controller_type(preset, dsp, slot,controller_type):
    return [
        param
        for param in util.get_controller_dsp_slot(preset, dsp, slot)
        if util.get_controller_dsp_slot_param(preset, dsp, slot, param)["@controller"] == controller_type
    ]


def dsp_slot_list_params_usable_for_MIDICC(preset, dsp, slot):
    # dsp, slot = random_block_split_or_cab_in_default_dsps(preset)
    # if slot != "none":
    raw_block_dict = file.reload_raw_block_dictionary(preset, dsp, slot)
    return [
        param
        for param in raw_block_dict["Controller_Dict"]
        if param not in ("Mic", "Position", "Distance", "Angle")
        ]
    # else:
    #     return []


def dsp_slot_list_params_usable_for_PEDAL2(preset, dsp, slot):
    # dsp, slot = random_block_split_or_cab_in_default_dsps(preset)
    # if slot != "none":
    raw_block_dict = file.reload_raw_block_dictionary(preset, dsp, slot)
    return [
            param
            for param in raw_block_dict["Controller_Dict"]
            if param not in ("Mic", "Position", "Distance", "Angle")
    ]
    # else:
    #     return []   
    
    
def dsp_slot_list_params_usable_for_SNAPSHOT(preset,dsp,slot):
    # dsp, slot = random_block_split_or_cab_in_default_dsps(preset)
    # if slot != "none":
    raw_block_dict = file.reload_raw_block_dictionary(preset, dsp, slot)
    return list(raw_block_dict["Controller_Dict"].keys())
    # else:
    #     return []
   


def assign_random_parameter_to_controller_SNAPSHOT_and_randomise_range(preset):
    print()
    dsp, slot = random_block_split_or_cab_in_default_dsps(preset)
    if slot != "none":
        if params := dsp_slot_list_params_usable_for_SNAPSHOT(preset, dsp, slot):
            param = random.choice(params)
            params.remove(param)
            util.remove_controller_if_present(preset, dsp, slot, param)
            raw_block_dict = file.reload_raw_block_dictionary(preset, dsp, slot)
            util.add_controller_block_param_and_control_type(preset, dsp, slot, param, raw_block_dict, var.CONTROLLER_SNAPSHOT)
            random_max_and_min_for_controlled_param(preset, dsp, slot, param)
            raw_block_dict = file.reload_raw_block_dictionary(preset, dsp, slot)
            util.add_parameter_to_all_snapshots(preset, dsp, slot, param, raw_block_dict)



def assign_random_parameter_to_controller_MIDICC_and_randomise_range(preset):
    print()
    dsp, slot = random_block_split_or_cab_in_default_dsps(preset)
    if slot != "none":
        if params := dsp_slot_list_params_usable_for_MIDICC(preset, dsp, slot):
            param = random.choice(params)
            params.remove(param)
            util.remove_controller_if_present(preset, dsp, slot, param)
            raw_block_dict = file.reload_raw_block_dictionary(preset, dsp, slot)
            util.add_controller_block_param_and_control_type(preset, dsp, slot, param, raw_block_dict, var.CONTROLLER_MIDICC)
            util.add_controller_block_parameter_cc(preset, dsp, slot, param, util.nextCC())
            random_max_and_min_for_controlled_param(preset, dsp, slot, param)


def assign_random_parameter_to_controller_PEDAL2_and_randomise_range(preset):
    print()
    dsp, slot = random_block_split_or_cab_in_default_dsps(preset)
    if slot != "none":
        if params := dsp_slot_list_params_usable_for_PEDAL2(preset, dsp, slot):
            param = random.choice(params)
            params.remove(param)
            util.remove_controller_if_present(preset, dsp, slot, param)
            raw_block_dict = file.reload_raw_block_dictionary(preset, dsp, slot)
            util.add_controller_block_param_and_control_type(preset, dsp, slot, param, raw_block_dict, var.CONTROLLER_PEDAL2)
            random_max_and_min_for_controlled_param(preset, dsp, slot, param)
        
        
# def log_controller_assignment(dsp, slot, model_name, param, control_type):
#     print("set", dsp, slot, model_name, param, util.num_to_control_type(control_type))   


def random_max_and_min_for_controlled_param(preset, dsp, slot, parameter):
    print("random_max_and_min_for_controlled_param", dsp, slot, parameter)
    controlled_param = util.get_controller_dsp_slot_param(preset, dsp, slot, parameter)
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
        list(var.block_probabilities.keys()),
        weights=[float(w) for w in list(var.block_probabilities.values())],
        k=1,
    )[0]



def random_controller_to_snapshot(preset, param_list, control_type):
    # choose a block,param pair
    random_index = random.randint(0, len(param_list) - 1)
    dsp, slot, parameter = param_list[random_index]
    # set control to snapshot
    util.get_controller_dsp_slot_param(preset, dsp, slot, parameter)["@controller"] = var.CONTROLLER_SNAPSHOT
    print(
        f"  set control {str(control_type)} to snapshot {str(control_type)} for {dsp}",
        slot,
        util.get_model_name(preset, dsp, slot),
        parameter,
    )


def assign_random_series_or_parallel_dsp_configuration(preset):
    preset["data"]["tone"]["dsp0"]["outputA"]["@output"] = random.choice([1, 2])

def remove_some_random_controllers(preset):
    print("remove_some_random_controllers")
    remove_some_random_SNAPSHOT_controllers(preset, var.MUTATION_RATE * var.NUM_SNAPSHOT_PARAMS)
    remove_some_random_PEDAL2_controllers(preset, var.MUTATION_RATE * var.NUM_PEDAL2_PARAMS)
    remove_some_random_MIDICC_controllers(preset, var.MUTATION_RATE * var.NUM_MIDICC_PARAMS)


def remove_some_random_PEDAL2_controllers(preset):
    num_removable = len(util.list_controls_of_type(preset, var.CONTROLLER_PEDAL2))
    max_to_remove = num_removable * var.MUTATION_RATE
    num_to_remove = random.randint(0, int(max_to_remove))
    print("remove_some_random_PEDAL2_controllers ", num_to_remove)
    list_of_PEDAL2_controllers = util.list_controls_of_type(preset, var.CONTROLLER_PEDAL2)
    for _ in range(num_to_remove):
        dsp, slot, param = random.choice(list_of_PEDAL2_controllers)
        # list_of_PEDAL2_controllers.remove((dsp, slot, param))
        util.remove_PEDAL2_controller(preset, dsp, slot, param)

      
def remove_some_random_MIDICC_controllers(preset):
    num_removable = len(util.list_controls_of_type(preset, var.CONTROLLER_MIDICC))
    max_to_remove = num_removable * var.MUTATION_RATE
    num_to_remove = random.randint(0, int(max_to_remove))
    print("remove_some_random_MIDICC_controllers ", num_to_remove)
    list_of_MIDICC_controllers = util.list_controls_of_type(preset, var.CONTROLLER_MIDICC)
    for _ in range(num_to_remove):
        dsp, slot, param  = random.choice(list_of_MIDICC_controllers)
        # TODO fix problem removing from list
        # list_of_MIDICC_controllers.remove((dsp, slot, param))
        util.remove_MIDICC_controller(preset, dsp, slot, param)
        
         
def remove_some_random_SNAPSHOT_controllers(preset, max_to_remove):
    num_removable = len(util.list_controls_of_type(preset, var.CONTROLLER_SNAPSHOT))
    max_to_remove = num_removable * var.MUTATION_RATE
    num_to_remove = random.randint(0, int(max_to_remove))
    print("remove_some_random_SNAPSHOT_controllers ", num_to_remove)
    list_of_SNAPSHOT_controllers = util.list_controls_of_type(preset, var.CONTROLLER_SNAPSHOT)
    for _ in range(num_to_remove):
        dsp, slot, param = random.choice(list_of_SNAPSHOT_controllers)
        # list_of_SNAPSHOT_controllers.remove((dsp, slot, param))
        util.remove_SNAPSHOT_controller(preset, dsp, slot, param)
        

        
 
def grow_SNAPSHOT_controllers(preset):
    num_to_grow = min(len(util.list_total_params_usable_for_controller_type(preset, var.CONTROLLER_SNAPSHOT)), var.NUM_SNAPSHOT_PARAMS)
    print("\ngrow_SNAPSHOT_controllers by ", num_to_grow)
    for _ in range(num_to_grow):
        assign_random_parameter_to_controller_SNAPSHOT_and_randomise_range(preset)

def grow_PEDAL2_controllers(preset):
    num_to_grow = min(len(util.list_total_params_usable_for_controller_type(preset, var.CONTROLLER_PEDAL2)), var.NUM_PEDAL2_PARAMS)
    print("\ngrow_PEDAL2_controllers by ", num_to_grow)
    for _ in range(num_to_grow):
        assign_random_parameter_to_controller_PEDAL2_and_randomise_range(preset)
        
        
def grow_MIDICC_controllers(preset):
    num_to_grow = min(len(util.list_total_params_usable_for_controller_type(preset, var.CONTROLLER_MIDICC)), var.NUM_MIDICC_PARAMS)
    print("\ngrow_MIDICC_controllers by ", num_to_grow)
    for _ in range(num_to_grow):
        assign_random_parameter_to_controller_MIDICC_and_randomise_range(preset)     


def move_split_and_join(preset, dsp):
    join_position = random.randint(var.NUM_POSITIONS_PER_PATH - 4, var.NUM_POSITIONS_PER_PATH)
    split_position = random.randint(0, join_position - 3)
    preset["data"]["tone"][dsp]["join"]["@position"] = join_position
    preset["data"]["tone"][dsp]["split"]["@position"] = split_position



def move_splits_and_joins(preset):
    for dsp in util.get_available_default_dsp_names(preset):
        move_split_and_join(preset, dsp)
