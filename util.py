from copy import deepcopy
import constants

# from debug import save_debug_hlx
import choose


def add_raw_block_to_preset(preset, dsp, slot, raw_block_dict):
    add_raw_block_default_to_dsp(preset, dsp, slot, raw_block_dict)
    add_raw_block_to_controller(preset, dsp, slot, raw_block_dict)
    add_raw_block_to_snapshots(preset, dsp, slot, raw_block_dict)


def add_raw_block_default_to_dsp(preset, dsp, slot, raw_block_dict):
    preset["data"]["tone"][dsp][slot] = deepcopy(raw_block_dict["Defaults"])


def add_raw_block_to_controller(preset, dsp, slot, raw_block_dict):
    controller_slot = get_controller(preset, dsp)
    controller_slot[slot] = deepcopy(raw_block_dict["Ranges"])
    # print(" added block to controller: " + dsp, slot, block_dict["Defaults"]["@model"])


def get_default_slot(preset, dsp, slot):
    return preset["data"]["tone"][dsp][slot]


def get_controller(preset, dsp):
    return preset["data"]["tone"]["controller"][dsp]


def get_snapshot_slot(preset, snapshot_num, dsp, slot):
    snapshot_name = f"snapshot{snapshot_num}"
    return preset["data"]["tone"][snapshot_name]["controllers"][dsp][slot]


def get_snapshot(preset, snapshot_num, dsp):
    snapshot_name = f"snapshot{snapshot_num}"
    return preset["data"]["tone"][snapshot_name]["controllers"][dsp]


def add_raw_block_to_snapshots(preset, dsp, slot, raw_block_dict):
    # print("Adding raw block to snapshots")
    for snapshot_num in range(constants.NUM_SNAPSHOTS):
        snapshot_slot = get_snapshot(preset, snapshot_num, dsp)
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
    get_controller(preset, to_dsp)[to_slot] = {}
    get_controller(preset, to_dsp)[to_slot] = get_controller(preset, from_dsp).pop(from_slot)


def move_snapshot_slot(preset, from_dsp, from_slot, to_dsp, to_slot, slot_type):
    for snapshot_num in range(constants.NUM_SNAPSHOTS):
        # NOTE: this if may be unnecessary, might not need slot_type at all
        if slot_type in ["block", "cab"]:
            to_snapshot = get_snapshot(preset, snapshot_num, to_dsp)
            from_snapshot = get_snapshot(preset, snapshot_num, from_dsp)
            to_snapshot[to_slot] = {}
            to_snapshot[to_slot] = from_snapshot.pop(from_slot)


def list_pedal_controls(preset, controller_num):
    # get a list of params with control (eg. pedal controller number 2)
    params_with_control_set_to_pedal = []
    for dsp in ["dsp0", "dsp1"]:
        for slot in get_controller(preset, dsp):
            params_with_control_set_to_pedal.extend(
                [dsp, slot, parameter]
                for parameter in get_controller_slot(preset, dsp, slot)
                if get_controller_slot_parameter(preset, dsp, slot, parameter)["@controller"] == controller_num
            )
    return params_with_control_set_to_pedal


def count_parameters_in_controller(preset):
    num_params = 0
    for dsp in ["dsp0", "dsp1"]:
        for slot in get_controller(preset, dsp):
            if slot.startswith(("block", "split", "cab")):
                for parameter in get_controller_slot(preset, dsp, slot):
                    # print("counting " + parameter)
                    num_params += 1
    return num_params


def add_parameter_to_all_snapshots(preset, dsp, slot, parameter, raw_block_dict):
    for snapshot_num in range(constants.NUM_SNAPSHOTS):
        snapshot_name = f"snapshot{snapshot_num}"
        if snapshot_name in preset["data"]["tone"]:
            snapshot_dict = get_snapshot_slot(preset, snapshot_num, dsp, slot)
            snapshot_dict[parameter] = deepcopy(raw_block_dict["SnapshotParams"][parameter])
            # print("add_parameter_to_all_snapshots " + parameter + " in " + get_model_name(preset, dsp, slot) + ", " + dsp + " " + slot)


def remove_parameter_from_all_snapshots(preset, dsp, slot, parameter):
    for snapshot_num in range(constants.NUM_SNAPSHOTS):
        snapshot = get_snapshot(preset, snapshot_num, dsp)
        del snapshot[slot][parameter]
        # print("remove_parameter_from_all_snapshots " + parameter + " in " + get_model_name(preset, dsp, slot) + ", " + dsp + " " + slot)


def add_parameter_to_controller(preset, dsp, slot, parameter, raw_block_dict):
    if slot not in get_controller(preset, dsp):
        get_controller(preset, dsp)[slot] = {}
    # save_debug_hlx(preset)
    get_controller_slot(preset, dsp, slot)[parameter] = deepcopy(raw_block_dict["Ranges"][parameter])
    get_controller_slot_parameter(preset, dsp, slot, parameter)["@controller"] = 19
    print("add_parameter_to_controller ", parameter, "in", get_model_name(preset, dsp, slot), ",", dsp, slot)


def get_controller_slot_parameter(preset, dsp, slot, parameter):
    return preset["data"]["tone"]["controller"][dsp][slot][parameter]


def get_controller_slot(preset, dsp, slot):
    return preset["data"]["tone"]["controller"][dsp][slot]


def remove_parameter_from_controller(preset, dsp, slot, param):
    del get_controller_slot(preset, dsp, slot)[param]
    model_name = get_model_name(preset, dsp, slot)
    print(f"remove_parameter_from_controller {param} in {model_name}, {dsp} {slot}")


def get_model_name(preset, dsp, slot):
    # print("get_model_name " + dsp + " " + slot)
    return preset["data"]["tone"][dsp][slot]["@model"]


def set_led_colours(preset):
    for snapshot_num in range(constants.NUM_SNAPSHOTS):
        preset["data"]["tone"][f"snapshot{snapshot_num}"]["@ledcolor"] = str(snapshot_num + 1)


def prune_controllers(preset):
    print("\nPruning controls to maximum 64...")
    while count_parameters_in_controller(preset) > constants.MAXIMUM_CONTROLLERS:
        choose.remove_one_random_controller_parameter(preset)


def grow_controllers(preset):
    print("\nGrowing controls to maximum 64...")
    while count_parameters_in_controller(preset) < constants.MAXIMUM_CONTROLLERS:  # to avoid setting any twice
        choose.add_random_parameter_to_controller(preset)


def add_dsp_controller_and_snapshot_keys_if_missing(preset):
    for dsp in ["dsp0", "dsp1"]:
        preset["data"]["tone"].setdefault(dsp, {})
        preset["data"]["tone"].setdefault("controller", {}).setdefault(dsp, {})
        for snapshot_num in range(constants.NUM_SNAPSHOTS):
            snapshot_name = f"snapshot{snapshot_num}"
            preset["data"]["tone"].setdefault(snapshot_name, {}).setdefault("controllers", {}).setdefault(dsp, {})
