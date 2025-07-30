""" 
util.py
 
 This file is part of phelix.
 
 Copyright 2024 Tim Barrass
 
 phelix is licensed under the GNU General Public Licence (GPL) Version 3 or later. 
"""

from copy import deepcopy
from datetime import datetime
import variables
import file
# from debug import save_debug_hlx


def set_preset_name(preset, preset_name):
    print(f"Preset name: {preset_name}")
    preset["data"]["meta"]["name"] = preset_name


def add_raw_block_to_preset(preset, dsp, slot, raw_block_dict):
    print("  adding raw block to preset", raw_block_dict["Defaults"]["@model"], dsp, slot)
    add_raw_block_default_to_dsp(preset, dsp, slot, raw_block_dict)
    add_raw_block_to_controller(preset, dsp, slot, raw_block_dict)
    add_raw_block_to_snapshots(preset, dsp, slot, raw_block_dict)


def add_raw_block_default_to_dsp(preset, dsp, slot, raw_block_dict):
    preset["data"]["tone"][dsp][slot] = deepcopy(raw_block_dict["Defaults"])


def add_raw_block_to_controller(preset, dsp, slot, raw_block_dict):
    controller_slot = get_controller_dsp(preset, dsp)
    controller_slot[slot] = deepcopy(raw_block_dict["Controller_Dict"])
    # print(" added block to controller: " + dsp, slot, block_dict["Defaults"]["@model"])


def set_raw_max_and_min_for_controlled_param(preset, dsp, slot, param):
    controlled_param = get_controller_dsp(preset, dsp)[slot][param]
    raw_block_dict = file.reload_raw_block_dictionary(preset, dsp, slot)["Controller_Dict"]
    controlled_param["@min"] = raw_block_dict[param]["@min"]
    controlled_param["@max"] = raw_block_dict[param]["@max"]
    
    
def set_controller_type(preset, dsp, slot, parameter, control_type):
    get_controller_dsp_slot_parameter(preset, dsp, slot, parameter)["@controller"] = control_type
    # print("  set_controller_type ", str(control_type), "for", dsp, slot, parameter)
    
    
def add_controller_block_parameter_cc(preset, dsp, slot, parameter, cc):
    print("  add_controller_block_parameter_cc", dsp, slot, parameter, "cc", cc)
    get_controller_dsp_slot_parameter(preset, dsp, slot, parameter).setdefault("@cc", {})
    get_controller_dsp_slot_parameter(preset, dsp, slot, parameter)["@cc"] = cc


def add_controller_block_parameter_and_control_type(preset, dsp, slot, parameter, raw_block_dict, control_type):
    if slot not in get_controller_dsp(preset, dsp):
        get_controller_dsp(preset, dsp)[slot] = {}
    # save_debug_hlx(preset)
    get_controller_dsp_slot(preset, dsp, slot)[parameter] = deepcopy(raw_block_dict["Controller_Dict"][parameter])
    get_controller_dsp_slot_parameter(preset, dsp, slot, parameter)["@controller"] = control_type
    print("  add_parameter_to_controller ", get_model_name(preset, dsp, slot), ",", dsp, slot, parameter, control_type)
    
    
def remove_controller_block_parameter_cc(preset, dsp, slot, parameter):
    del get_controller_dsp_slot_parameter(preset, dsp, slot, parameter)["@cc"]


def get_available_default_dsps(preset):
    return [key for key in preset["data"]["tone"].keys() if key.startswith("dsp")]


def get_default(preset):
    return preset["data"]["tone"]


def get_default_dsp(preset, dsp):
    return preset["data"]["tone"][dsp]


def get_default_dsp_slot(preset, dsp, slot):
    return preset["data"]["tone"][dsp][slot]


def get_default_dsp_slot_parameter_value(preset, dsp, slot, parameter):
    return preset["data"]["tone"][dsp][slot][parameter]


def get_snapshot(preset, snapshot_num):
    return preset["data"]["tone"][f"snapshot{snapshot_num}"]


def get_snapshot_blocks(preset, snapshot_num):
    return preset["data"]["tone"][f"snapshot{snapshot_num}"]["blocks"]


def get_snapshot_blocks_dsp(preset, snapshot_num, dsp):
    return preset["data"]["tone"][f"snapshot{snapshot_num}"]["blocks"][dsp]


def get_snapshot_controllers(preset, snapshot_num):
    return preset["data"]["tone"][f"snapshot{snapshot_num}"]["controllers"]


def get_snapshot_controllers_dsp(preset, snapshot_num, dsp):
    return preset["data"]["tone"][f"snapshot{snapshot_num}"]["controllers"][dsp]


def get_snapshot_controllers_blocks_dsp(preset, snapshot_num, dsp):
    return preset["data"]["tone"][f"snapshot{snapshot_num}"]["blocks"][dsp]


def get_snapshot_controllers_dsp_slot(preset, snapshot_num, dsp, slot):
    # print(
    #     "get_snapshot_controllers_dsp_slot",
    #     snapshot_num,
    #     dsp,
    #     slot,
    #     preset["data"]["tone"][f"snapshot{snapshot_num}"]["controllers"][dsp][slot],
    # )
    return preset["data"]["tone"][f"snapshot{snapshot_num}"]["controllers"][dsp][slot]


def get_snapshot_controllers_dsp_slot_parameter(preset, snapshot_num, dsp, slot, parameter):
    return preset["data"]["tone"][f"snapshot{snapshot_num}"]["controllers"][dsp][slot][parameter]


def get_snapshot_controllers_dsp_slot_parameter_value(preset, snapshot_num, dsp, slot, parameter):
    # print("get_snapshot_controllers_dsp_slot_parameter_value", snapshot_num, dsp, slot, parameter)
    return preset["data"]["tone"][f"snapshot{snapshot_num}"]["controllers"][dsp][slot][parameter]["@value"]


def add_raw_block_to_snapshots(preset, dsp, slot, raw_block_dict):
    # print("Adding raw block to snapshots")
    for snapshot_num in range(variables.NUM_SNAPSHOTS):
        snapshot_slot = get_snapshot_controllers_dsp(preset, snapshot_num, dsp)
        snapshot_slot[slot] = deepcopy(raw_block_dict["SnapshotParams"])


# splits can only move on their own dsp
# cabs can only move to the dsp where their amp is
# blocks can move to any dsp


def move_slot(preset, from_dsp, from_slot, to_dsp, to_slot, slot_type):
    move_default_slot(preset, from_dsp, from_slot, to_dsp, to_slot)
    move_controller_slot(preset, from_dsp, from_slot, to_dsp, to_slot)
    move_snapshot_slot(preset, from_dsp, from_slot, to_dsp, to_slot, slot_type)


def move_default_slot(preset, from_dsp, from_slot, to_dsp, to_slot):
    preset["data"]["tone"][to_dsp][to_slot] = {}
    preset["data"]["tone"][to_dsp][to_slot] = preset["data"]["tone"][from_dsp].pop(from_slot)


def move_controller_slot(preset, from_dsp, from_slot, to_dsp, to_slot):
    if from_slot in get_controller_dsp(preset, from_dsp):
        get_controller_dsp(preset, to_dsp)[to_slot] = {}
        get_controller_dsp(preset, to_dsp)[to_slot] = get_controller_dsp(preset, from_dsp).pop(from_slot)


def move_snapshot_slot(preset, from_dsp, from_slot, to_dsp, to_slot, slot_type):
    if from_slot in get_snapshot_controllers_dsp(preset, 0, from_dsp):
        for snapshot_num in range(variables.NUM_SNAPSHOTS):
            # NOTE: this if may be unnecessary, might not need slot_type at all
            if slot_type in ["block", "cab"]:
                to_snapshot_controllers = get_snapshot_controllers_dsp(preset, snapshot_num, to_dsp)
                from_snapshot_controllers = get_snapshot_controllers_dsp(preset, snapshot_num, from_dsp)
                to_snapshot_controllers[to_slot] = {}
                to_snapshot_controllers[to_slot] = from_snapshot_controllers.pop(from_slot)

                # also move block true/false
                if slot_type == "block":
                    to_snapshot_blocks = get_snapshot_controllers_blocks_dsp(preset, snapshot_num, to_dsp)
                    from_snapshot_blocks = get_snapshot_controllers_blocks_dsp(preset, snapshot_num, from_dsp)
                    # print(to_snapshot_blocks, from_snapshot_blocks)
                    to_snapshot_blocks[to_slot] = {}
                    to_snapshot_blocks[to_slot] = from_snapshot_blocks.pop(from_slot)


def list_controls_of_type(preset, controller_type):
    # get a list of params with control (eg. pedal controller number 2)
    params_with_control_set_to_pedal = []
    for dsp in get_controller(preset):
        for slot in get_controller_dsp(preset, dsp):
            params_with_control_set_to_pedal.extend(
                [dsp, slot, parameter]
                for parameter in get_controller_dsp_slot(preset, dsp, slot)
                if get_controller_dsp_slot_parameter(preset, dsp, slot, parameter)["@controller"] == controller_type
            )
    return params_with_control_set_to_pedal


def count_parameters_in_controller(preset):
    return len(
        [
            parameter
            for dsp in get_controller(preset)
            for slot in get_controller_dsp(preset, dsp)
            if slot.startswith(("block", "split", "cab"))
            for parameter in get_controller_dsp_slot(preset, dsp, slot)
        ]
    )


def add_parameter_to_all_snapshots(preset, dsp, slot, parameter, raw_block_dict):
# print("add_parameter_to_all_snapshots " + parameter + " in " + get_model_name(preset, dsp, slot) + ", " + dsp + " " + slot)
    for snapshot_num in range(variables.NUM_SNAPSHOTS):
        snapshot_name = f"snapshot{snapshot_num}"
        if snapshot_name in preset["data"]["tone"]:
            if slot not in get_snapshot_controllers_dsp(preset, snapshot_num, dsp):
                get_snapshot_controllers_dsp(preset, snapshot_num, dsp)[slot] = {}
            snapshot_dict = get_snapshot_controllers_dsp_slot(preset, snapshot_num, dsp, slot)
            snapshot_dict[parameter] = deepcopy(raw_block_dict["SnapshotParams"][parameter])
            


def remove_parameter_from_all_snapshots(preset, dsp, slot, parameter):
    print(f"remove_parameter_from_all_snapshots: {dsp} {slot}, {get_model_name(preset, dsp, slot)} {parameter}")
    for snapshot_num in range(variables.NUM_SNAPSHOTS):
        snapshot = get_snapshot_controllers_dsp(preset, snapshot_num, dsp)
        del snapshot[slot][parameter]
 

def remove_all_blocks_from_controller(preset):
    print("\nremove_all_blocks_from_controller")
    for dsp in get_controller(preset):
        get_controller_dsp(preset, dsp).clear()


def remove_all_snapshots(preset):
    print("\nremove_all_snapshots")
    for _ in range(variables.NUM_SNAPSHOTS):
        get_snapshot(preset, _).clear()



def get_controller(preset):
    # preset["data"]["tone"].setdefault("controller", {})
    return preset["data"]["tone"]["controller"]


def get_controller_dsp(preset, dsp):
    # preset["data"]["tone"]["controller"].setdefault(dsp, {})
    return preset["data"]["tone"]["controller"][dsp]


def get_controller_dsp_slot(preset, dsp, slot):
    # preset["data"]["tone"]["controller"][dsp].setdefault(slot, {})
    return preset["data"]["tone"]["controller"][dsp][slot]


def get_controller_dsp_slot_parameter(preset, dsp, slot, parameter):
    return preset["data"]["tone"]["controller"][dsp][slot][parameter]


def remove_parameter_from_controller(preset, dsp, slot, parameter):
    print(f"remove_parameter_from_controller: {dsp} {slot}, {get_model_name(preset, dsp, slot)} {parameter}")
    del get_controller_dsp_slot(preset, dsp, slot)[parameter]
    

def get_model_name(preset, dsp, slot):
    # print("get_model_name " + dsp + " " + slot)
    return preset["data"]["tone"][dsp][slot]["@model"]


def set_led_colours(preset):
    for snapshot_num in range(variables.NUM_SNAPSHOTS):
        preset["data"]["tone"][f"snapshot{snapshot_num}"]["@ledcolor"] = str(snapshot_num + 1)


def set_preset_name_for_generate(preset, args, postfix_num):     
    name = args.get("preset_name")
    if name == "":
        now = datetime.now()
        name = now.strftime("%y%m%d-%H%M")
    name = f"{name}-{str(postfix_num).zfill(2)}"
    preset["data"]["meta"]["name"] = name
    print(f"Preset name: {name}")
    
    
def set_preset_name_for_mutate(preset, args, postfix_num):
    name = args.get("preset_name")
    if name == "":
        name = preset["data"]["meta"]["name"]
    name = f"{name}{str(postfix_num).zfill(2)}"
    print(f"\n\nPreset name: {name}")
    preset["data"]["meta"]["name"] = name

    

def populate_controller_dsp_slot_from_raw_file(preset, dsp, slot):
    controller_block_dict = file.reload_raw_block_dictionary(preset, dsp, slot)["Controller_Dict"]
    get_controller_dsp(preset, dsp)[slot] = deepcopy(controller_block_dict)
    # print("populate_controller_from_defaults " + get_model_name(preset, dsp, slot) + ", " + dsp + " " + slot)


def populate_all_controller_slots_from_raw_file(preset):
    print("\npopulate_all_controller_slots_from_raw_file")
    for dsp in get_available_default_dsps(preset):
        for slot in get_default_dsp(preset, dsp):
            if slot.startswith(("block", "split", "cab")):
                get_controller_dsp(preset, dsp)[slot] = {}
                populate_controller_dsp_slot_from_raw_file(preset, dsp, slot)


def populate_snapshot_with_controllers_from_file(preset, snapshot_num):
    for dsp in get_available_default_dsps(preset):
        for slot in get_default_dsp(preset, dsp):
            if slot.startswith(("block", "split", "cab")):
                snapshot_block_dict = file.reload_raw_block_dictionary(preset, dsp, slot)["SnapshotParams"]
                get_snapshot_controllers_dsp(preset, snapshot_num, dsp)[slot] = {}
                get_snapshot_controllers_dsp(preset, snapshot_num, dsp)[slot] = deepcopy(snapshot_block_dict)


def populate_all_snapshots_with_controllers_from_file(preset):
    for snapshot_num in range(variables.NUM_SNAPSHOTS):
        populate_snapshot_with_controllers_from_file(preset, snapshot_num)


def copy_controlled_default_parameter_values_to_snapshot(preset, snapshot_num):
    for dsp in get_available_default_dsps(preset):
        for slot in get_controller_dsp(preset, dsp):
            for parameter in get_controller_dsp_slot(preset, dsp, slot):
                # print("copy_controlled_default_parameter_values_to_snapshot", dsp, slot, parameter)
                # get_snapshot_controllers_dsp_slot(preset, snapshot_num, dsp, slot)[parameter] = {}
                get_snapshot_controllers_dsp_slot_parameter(preset, snapshot_num, dsp, slot, parameter)["@value"] = (
                    deepcopy(get_default_dsp_slot(preset, dsp, slot)[parameter])
                )


def remove_empty_controller_dsp_slots(preset):
    empty_controller_dsp_slots = [
        (dsp, slot)
        for dsp in get_available_default_dsps(preset)
        for slot in get_controller_dsp(preset, dsp)
        if get_controller_dsp_slot(preset, dsp, slot) == {}
    ]

    # print("empty_controller_dsp_slots ", empty_controller_dsp_slots)
    for dsp, slot in empty_controller_dsp_slots:
        del get_controller_dsp(preset, dsp)[slot]
        print("  removed empty controller ", dsp, slot)

    for dsp, slot in empty_controller_dsp_slots:
        for snapshot_num in range(variables.NUM_SNAPSHOTS):
            del get_snapshot_controllers_dsp(preset, snapshot_num, dsp)[slot]
        print("  removed empty snapshot controller ", dsp, slot)


def count_amps(preset, dsp):
    return sum(bool(get_model_name(preset, dsp, slot).startswith("HD2_Amp")) for slot in get_default_dsp(preset, dsp))


def count_controllers(preset):
    count = 0
    for dsp in get_available_default_dsps(preset):
        for slot in get_default_dsp(preset, dsp):
            if slot in get_controller_dsp(preset, dsp):
                count += 1
    return count


def copy_snapshot_values_to_default(preset, snapshot_src_num_str):
    print("\ncopy_snapshot_values_to_default")
    if snapshot_src_num_str.isdigit():
        snapshot_src_num = int(snapshot_src_num_str) - 1  # 0-indexed
        if 0 <= snapshot_src_num <= 7:
            for dsp in get_available_default_dsps(preset):
                for slot in get_snapshot_controllers_dsp(preset, snapshot_src_num, dsp):
                    for parameter in get_snapshot_controllers_dsp_slot(preset, snapshot_src_num, dsp, slot):
                        get_default_dsp_slot(preset, dsp, slot)[parameter] = deepcopy(
                            get_snapshot_controllers_dsp_slot_parameter_value(preset, snapshot_src_num, dsp, slot, parameter)
                        )


def set_topologies_to_SABJ(preset):
    preset["data"]["tone"]["global"]["@topology0"] = "SABJ"  # dsp0
    preset["data"]["tone"]["global"]["@topology1"] = "SABJ"  # dsp1
    # some options: "ABJ" (pathA, pathB, Join), "SABJ", (split, pathA, pathB, join)


# def count_blocks_on_each_dsp_path(preset, dsp):
#     blocks_on_path0 = 0
#     blocks_on_path1 = 0
#     for slot in util.get_default_dsp(preset, dsp):
#         if slot.startswith("block"):
#             blocks_on_path0 += 1 if dsp == "dsp0" else 0
#             blocks_on_path1 += 1 if dsp == "dsp1" else 0
#     return blocks_on_path0, blocks_on_path1

# def check_and_set_topologies(preset):
#     for dsp in get_available_default_dsps(preset):
#         blocks_on_path0, blocks_on_path1 = count_blocks_on_each_dsp_path(preset, dsp)
#         if blocks_on_path0 == 0:
#             preset["data"]["tone"]["global"]["@topology0"] = "A"  # dsp0
#         if blocks_on_path1 == 0:
#             preset["data"]["tone"]["global"]["@topology1"] = "B"  # dsp1
#         # remove split from default, controllers and snapshots


def add_dsp_controller_and_snapshot_keys_if_missing(preset):
    for dsp in ["dsp0", "dsp1"]:
        preset["data"]["tone"].setdefault(dsp, {})
        preset["data"]["tone"].setdefault("controller", {}).setdefault(dsp, {})
        for snapshot_num in range(variables.NUM_SNAPSHOTS):
            snapshot_name = f"snapshot{snapshot_num}"
            preset["data"]["tone"].setdefault(snapshot_name, {}).setdefault("controllers", {}).setdefault(dsp, {})
            get_snapshot(preset, snapshot_num).setdefault("controllers", {}).setdefault(dsp, {})
            get_snapshot(preset, snapshot_num).setdefault("blocks", {}).setdefault(dsp, {})



def add_default_dsp_keys_if_missing(preset):
    for dsp in ["dsp0", "dsp1"]:
        preset["data"]["tone"].setdefault(dsp, {})


def add_default_controller_dsp_keys_if_missing(preset):
    for dsp in ["dsp0", "dsp1"]:
        preset["data"]["tone"].setdefault("controller", {}).setdefault(dsp, {})


def add_splits(preset):
    for dsp in get_available_default_dsps(preset):
        for snapshot_num in range(variables.NUM_SNAPSHOTS):
            get_snapshot_blocks_dsp(preset, snapshot_num, dsp).setdefault("split", "false")  # bypass not controlled?


def duplicate_snapshot(preset, snapshot_src, snapshot_dst):
    preset["data"]["tone"][snapshot_dst] = deepcopy(preset["data"]["tone"][snapshot_src])
    preset["data"]["tone"][snapshot_dst]["@name"] = snapshot_dst


def add_snapshot_controller_dsp_keys_if_missing(preset):
    for dsp in ["dsp0", "dsp1"]:
        for snapshot_num in range(variables.NUM_SNAPSHOTS):
            snapshot_name = f"snapshot{snapshot_num}"
            preset["data"]["tone"].setdefault(snapshot_name, {}).setdefault("controllers", {}).setdefault(dsp, {})
            get_snapshot(preset, snapshot_num).setdefault("controllers", {}).setdefault(dsp, {})
            get_snapshot(preset, snapshot_num).setdefault("blocks", {}).setdefault(dsp, {})


def set_dsp1_input_to_multi(preset):
    preset["data"]["tone"]["dsp1"]["inputA"]["@input"] = 1
    
    
cc_being_used = variables.useable_cc_numbers[: variables.NUM_CC_PARAMS]

def reinit_cc_being_used():
    global cc_being_used
    cc_being_used = variables.useable_cc_numbers[: variables.NUM_CC_PARAMS]


def num_ccs_spare():
    return len(cc_being_used)


def nextCC():
    return cc_being_used.pop(0)


def add_splits(preset):
    for dsp in get_available_default_dsps(preset):
        for snapshot_num in range(variables.NUM_SNAPSHOTS):
            get_snapshot_blocks_dsp(preset, snapshot_num, dsp).setdefault("split", "false")  # bypass not controlled?


def duplicate_snapshot(preset, snapshot_src, snapshot_dst):
    preset["data"]["tone"][snapshot_dst] = deepcopy(preset["data"]["tone"][snapshot_src])
    preset["data"]["tone"][snapshot_dst]["@name"] = snapshot_dst


# def add_footswitch_dsp_blocks_cc_control_if_missing(preset):
#     for dsp in ["dsp0", "dsp1"]:
#         preset["data"]["tone"].setdefault("footswitch", {}).setdefault(dsp, {})
#         for slot in get_default_dsp(preset, dsp):
#             if slot.startswith("block"):
#                 preset["data"]["tone"]["footswitch"][dsp].setdefault(slot, {})
#                 preset["data"]["tone"]["footswitch"][dsp][slot]["@cc"] = nextCC()


# def add_footswitch_dsp_blocks_snapshot_control_if_missing(preset):
#     for dsp in ["dsp0", "dsp1"]:
#         preset["data"]["tone"].setdefault("footswitch", {}).setdefault(dsp, {})
#         for slot in get_default_dsp(preset, dsp):
#             if slot.startswith("block"):
#                 preset["data"]["tone"]["footswitch"][dsp].setdefault(slot, {})
#                 preset["data"]["tone"]["footswitch"][dsp][slot]["@fs_index"] = variables.SNAPSHOT_CONTROL

                
                
def copy_all_default_values_to_snapshot(preset, snapshot_num):
    for dsp in get_available_default_dsps(preset):
        for slot in get_snapshot_controllers_dsp(preset, snapshot_num, dsp):
            for parameter in get_snapshot_controllers_dsp_slot(preset, snapshot_num, dsp, slot):
                get_snapshot_controllers_dsp_slot_parameter(preset, snapshot_num, dsp, slot, parameter)["@value"] = (
                    deepcopy(get_default_dsp_slot_parameter_value(preset, dsp, slot, parameter))
                )


def copy_all_default_values_to_all_snapshots(preset):
    for snapshot_num in range(variables.NUM_SNAPSHOTS):
        copy_all_default_values_to_snapshot(preset, snapshot_num)


def duplicate_src_snapshot_to_all(preset, snapshot_src):
    for snapshot_num in range(variables.NUM_SNAPSHOTS):
        snapshot_dst = f"snapshot{snapshot_num}"
        if snapshot_dst != snapshot_src:
            duplicate_snapshot(preset, snapshot_src, snapshot_dst)


def count_controllable_parameters_in_preset(preset):
    count = 0
    for dsp in get_available_default_dsps(preset):
        for slot in get_default_dsp(preset, dsp):
            if slot.startswith(("block", "split", "cab")):
                count += len(file.reload_raw_block_dictionary(preset, dsp, slot)["Controller_Dict"].keys())
    return count
