""" 
choose.py
 
 This file is part of phelix.
 
 Copyright 2024 Tim Barrass
 
 phelix is licensed under the GNU General Public Licence (GPL) Version 3 or later. 
"""

import os
import random

from numpy import delete
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
    found_blocks_splits_cabs = []
    for dsp in util.get_available_default_dsps(preset):
        for slot in util.get_default_dsp(preset, dsp):
            if slot.startswith(("block", "split", "cab")):
                found_blocks_splits_cabs.append((dsp, slot))
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
        if util.get_controller_dsp_slot_parameter(preset, dsp, slot, param)["@controller"] == controller_type
    ]


def choose_slot_and_list_params_usable_for_MIDICC(preset):
    dsp, slot = random_block_split_or_cab_in_default_dsps(preset)
    if slot != "none":
        return params := [
                param
                for param in util.get_controller_dsp_slot(preset, dsp, slot)
                if param not in ("Mic", "Position", "Distance", "Angle") # and param["@controller"] != variables.CONTROLLER_MIDICC
        ]
    else:
        return []  


def choose_slot_and_list_params_usable_for_PEDAL2(preset):
    dsp, slot = random_block_split_or_cab_in_default_dsps(preset)
    if slot != "none":
        return params := [
                param
                for param in util.get_controller_dsp_slot(preset, dsp, slot)
                if param not in ("Mic", "Position", "Distance", "Angle") # and param["@controller"] != variables.CONTROLLER_PEDAL2
        ]
    else:
        return []    
    
def choose_slot_and_list_params_usable_for_SNAPSHOT(preset):
    dsp, slot = random_block_split_or_cab_in_default_dsps(preset)
    if slot != "none":
        return params := [
            param
            for param in util.get_controller_dsp_slot(preset, dsp, slot)
            # if param["@controller"] != variables.CONTROLLER_SNAPSHOT
        ]
    else:
        return []
   


def assign_random_parameter_controller_to_SNAPSHOT_and_randomise_range(preset):
    dsp, slot = random_block_split_or_cab_in_default_dsps(preset)
    if slot != "none":
        params = util.list_params_usable_for_SNAPSHOT(preset)
        if params:
            param = random.choice(params)
            util.remove_existing_controller(preset, dsp, slot, param)
            util.set_controller_type(preset, dsp, slot, param, variables.CONTROLLER_SNAPSHOT)
            random_max_and_min_for_controlled_param(preset, dsp, slot, param)
            raw_block_dict = file.reload_raw_block_dictionary(preset, dsp, slot)
            util.add_parameter_to_all_snapshots(preset, dsp, slot, param, raw_block_dict)
            log_controller_assignment(dsp, slot, util.get_model_name(preset, dsp, slot), param, variables.CONTROLLER_SNAPSHOT)


def assign_random_parameter_controller_to_MIDICC_and_randomise_range(preset):
    dsp, slot = random_controller_dsp_and_slot(preset)
    if slot != "none":
        params = util.list_params_usable_for_MIDICC(preset)
        if params:
            param = random.choice(params)
            util.set_controller_type(preset, dsp, slot, param, variables.CONTROLLER_MIDICC)
            util.add_controller_block_parameter_cc(preset, dsp, slot, param, util.nextCC())
            random_max_and_min_for_controlled_param(preset, dsp, slot, param)
            log_controller_assignment(dsp, slot, util.get_model_name(preset, dsp, slot), param, variables.CONTROLLER_MIDICC)


def assign_random_parameter_controller_to_PEDAL2_and_randomise_range(preset):
    dsp, slot = random_controller_dsp_and_slot(preset)
    if slot != "none":
        params = util.list_params_usable_for_PEDAL2(preset)
        if params:
            param = random.choice(params)
            util.set_controller_type(preset, dsp, slot, param, variables.CONTROLLER_PEDAL2)
            random_max_and_min_for_controlled_param(preset, dsp, slot, param)
            log_controller_assignment(dsp, slot, util.get_model_name(preset, dsp, slot), param, variables.CONTROLLER_PEDAL2)
        
        
def log_controller_assignment(dsp, slot, model_name, param, control_type):
    print(f"  set {dsp}", slot, model_name, param, f"to controller {str(control_type)}")   


def random_max_and_min_for_controlled_param(preset, dsp, slot, parameter):
    print(
        f"random_max_and_min_for_controlled_param {str(dsp)}{str(slot)}{str(parameter)}"
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



def random_controller_to_snapshot(preset, param_list, control_type):
    # choose a block,param pair
    random_index = random.randint(0, len(param_list) - 1)
    dsp, slot, parameter = param_list[random_index]
    # set control to snapshot
    util.get_controller_dsp_slot_parameter(preset, dsp, slot, parameter)["@controller"] = variables.CONTROLLER_SNAPSHOT
    print(
        f"  set control {str(control_type)} to snapshot {str(control_type)} for {dsp}",
        slot,
        util.get_model_name(preset, dsp, slot),
        parameter,
    )


def assign_random_series_or_parallel_dsp_configuration(preset):
    preset["data"]["tone"]["dsp0"]["outputA"]["@output"] = random.choice([1, 2])


def prune_PEDAL2_controllers(preset):
    print("\nprune_PEDAL2_controllers "+ str(variables.NUM_PEDAL2_PARAMS))
    list_of_PEDAL2_controllers = util.list_controls_of_type(preset, variables.CONTROLLER_PEDAL2)
    while util.count_parameters_in_controller(preset) > variables.NUM_PEDAL2_PARAMS:
        util.remove_PEDAL2_controller(preset, random(list_of_PEDAL2_controllers))
       
      
def prune_MIDICC_controllers(preset):
    print("\nprune_MIDICC_controllers "+ str(variables.NUM_MIDICC_PARAMS))
    list_of_MIDICC_controllers = util.list_controls_of_type(preset, variables.CONTROLLER_MIDICC)
    while util.count_parameters_in_controller(preset) > variables.NUM_MIDICC_PARAMS:
        util.remove_MIDICC_controller(preset, random(list_of_MIDICC_controllers))
       
         
def prune_SNAPSHOT_controllers(preset):
    print("\nprune_SNAPSHOT_controllers "+ str(variables.NUM_SNAPSHOT_PARAMS))
    list_of_SNAPSHOT_controllers = util.list_controls_of_type(preset, variables.CONTROLLER_SNAPSHOT)
    while util.count_parameters_in_controller(preset) > variables.NUM_SNAPSHOT_PARAMS:
        util.remove_SNAPSHOT_controller(preset, random(list_of_SNAPSHOT_controllers))
 
 
def grow_SNAPSHOT_controllers(preset):
    max_controllers = min(len(util.list_params_usable_for_SNAPSHOT(preset)), variables.NUM_SNAPSHOT_PARAMS)
    print("\grow_SNAPSHOT_controllers to ", max_controllers)
    while util.count_parameters_in_controller(preset) < max_controllers - 1:
        assign_random_parameter_controller_to_SNAPSHOT_and_randomise_range(preset)

def grow_PEDAL2_controllers(preset):
    max_controllers = min(len(util.list_params_usable_for_PEDAL2(preset)), variables.NUM_PEDAL2_PARAMS)
    print("\grow_PEDAL2_controllers to ", max_controllers)
    while util.count_parameters_in_controller(preset) < max_controllers - 1:
        assign_random_parameter_controller_to_PEDAL2_and_randomise_range(preset)
        
        
def grow_MIDICC_controllers(preset):
    max_controllers = min(len(util.list_params_usable_for_MIDICC(preset)), variables.NUM_MIDICC_PARAMS)
    print("\grow_MIDICC_controllers to ", max_controllers)
    while util.count_parameters_in_controller(preset) < max_controllers - 1:
        assign_random_parameter_controller_to_MIDICC_and_randomise_range(preset)     


def move_split_and_join(preset, dsp):
    join_position = random.randint(variables.NUM_POSITIONS_PER_PATH - 4, variables.NUM_POSITIONS_PER_PATH)
    split_position = random.randint(0, join_position - 3)
    preset["data"]["tone"][dsp]["join"]["@position"] = join_position
    preset["data"]["tone"][dsp]["split"]["@position"] = split_position


def move_splits_and_joins(preset):
    for dsp in util.get_available_default_dsps(preset):
        move_split_and_join(preset, dsp)
