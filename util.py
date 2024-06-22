from copy import deepcopy
import constants
import file

# from debug import save_debug_hlx


def add_raw_block_to_preset(preset, dsp, slot, raw_block_dict):
    add_raw_block_default_to_dsp(preset, dsp, slot, raw_block_dict)
    add_raw_block_to_controller(preset, dsp, slot, raw_block_dict)
    add_raw_block_to_snapshots(preset, dsp, slot, raw_block_dict)


def add_raw_block_default_to_dsp(preset, dsp, slot, raw_block_dict):
    preset["data"]["tone"][dsp][slot] = deepcopy(raw_block_dict["Defaults"])


def add_raw_block_to_controller(preset, dsp, slot, raw_block_dict):
    controller_slot = get_controller_dsp(preset, dsp)
    controller_slot[slot] = deepcopy(raw_block_dict["Ranges"])
    # print(" added block to controller: " + dsp, slot, block_dict["Defaults"]["@model"])


def get_available_default_dsps(preset):
    return [key for key in preset["data"]["tone"].keys() if key.startswith("dsp")]


def get_default(preset):
    return preset["data"]["tone"]


def get_default_dsp(preset, dsp):
    return preset["data"]["tone"][dsp]


def get_default_dsp_slot(preset, dsp, slot):
    return preset["data"]["tone"][dsp][slot]


def get_snapshot_blocks(preset, snapshot_num):
    return preset["data"]["tone"][f"snapshot{snapshot_num}"]["blocks"]


def get_snapshot_controllers(preset, snapshot_num):
    return preset["data"]["tone"][f"snapshot{snapshot_num}"]["controllers"]


def get_snapshot_controllers_dsp(preset, snapshot_num, dsp):
    return preset["data"]["tone"][f"snapshot{snapshot_num}"]["controllers"][dsp]


def get_snapshot_controllers_dsp_slot(preset, snapshot_num, dsp, slot):
    preset["data"]["tone"][f"snapshot{snapshot_num}"]["controllers"][dsp].setdefault(slot, {})
    return preset["data"]["tone"][f"snapshot{snapshot_num}"]["controllers"][dsp][slot]


def add_raw_block_to_snapshots(preset, dsp, slot, raw_block_dict):
    # print("Adding raw block to snapshots")
    for snapshot_num in range(constants.NUM_SNAPSHOTS):
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
    get_controller_dsp(preset, to_dsp)[to_slot] = {}
    get_controller_dsp(preset, to_dsp)[to_slot] = get_controller_dsp(preset, from_dsp).pop(from_slot)


def move_snapshot_slot(preset, from_dsp, from_slot, to_dsp, to_slot, slot_type):
    for snapshot_num in range(constants.NUM_SNAPSHOTS):
        # NOTE: this if may be unnecessary, might not need slot_type at all
        if slot_type in ["block", "cab"]:
            to_snapshot = get_snapshot_controllers_dsp(preset, snapshot_num, to_dsp)
            from_snapshot = get_snapshot_controllers_dsp(preset, snapshot_num, from_dsp)
            to_snapshot[to_slot] = {}
            to_snapshot[to_slot] = from_snapshot.pop(from_slot)


def list_pedal_controls(preset, controller_num):
    # get a list of params with control (eg. pedal controller number 2)
    params_with_control_set_to_pedal = []
    for dsp in get_controller(preset):
        for slot in get_controller_dsp(preset, dsp):
            params_with_control_set_to_pedal.extend(
                [dsp, slot, parameter]
                for parameter in get_controller_dsp_slot(preset, dsp, slot)
                if get_controller_dsp_slot_parameter(preset, dsp, slot, parameter)["@controller"] == controller_num
            )
    return params_with_control_set_to_pedal


def count_parameters_in_controller(preset):
    num_params = 0
    for dsp in get_controller(preset):
        for slot in get_controller_dsp(preset, dsp):
            if slot.startswith(("block", "split", "cab")):
                for parameter in get_controller_dsp_slot(preset, dsp, slot):
                    # print("counting " + parameter)
                    num_params += 1
    return num_params


def add_parameter_to_all_snapshots(preset, dsp, slot, parameter, raw_block_dict):
    for snapshot_num in range(constants.NUM_SNAPSHOTS):
        snapshot_name = f"snapshot{snapshot_num}"
        if snapshot_name in preset["data"]["tone"]:
            snapshot_dict = get_snapshot_controllers_dsp_slot(preset, snapshot_num, dsp, slot)
            snapshot_dict[parameter] = deepcopy(raw_block_dict["SnapshotParams"][parameter])
            # print("add_parameter_to_all_snapshots " + parameter + " in " + get_model_name(preset, dsp, slot) + ", " + dsp + " " + slot)


def remove_parameter_from_all_snapshots(preset, dsp, slot, parameter):
    for snapshot_num in range(constants.NUM_SNAPSHOTS):
        snapshot = get_snapshot_controllers_dsp(preset, snapshot_num, dsp)
        del snapshot[slot][parameter]
        # print("remove_parameter_from_all_snapshots " + parameter + " in " + get_model_name(preset, dsp, slot) + ", " + dsp + " " + slot)


def add_parameter_to_controller(preset, dsp, slot, parameter, raw_block_dict):
    if slot not in get_controller_dsp(preset, dsp):
        get_controller_dsp(preset, dsp)[slot] = {}
    # save_debug_hlx(preset)
    get_controller_dsp_slot(preset, dsp, slot)[parameter] = deepcopy(raw_block_dict["Ranges"][parameter])
    get_controller_dsp_slot_parameter(preset, dsp, slot, parameter)["@controller"] = 19
    print("add_parameter_to_controller ", parameter, "in", get_model_name(preset, dsp, slot), ",", dsp, slot)


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


def remove_parameter_from_controller(preset, dsp, slot, param):
    del get_controller_dsp_slot(preset, dsp, slot)[param]
    model_name = get_model_name(preset, dsp, slot)
    print(f"remove_parameter_from_controller {param} in {model_name}, {dsp} {slot}")


def get_model_name(preset, dsp, slot):
    # print("get_model_name " + dsp + " " + slot)
    return preset["data"]["tone"][dsp][slot]["@model"]


def set_led_colours(preset):
    for snapshot_num in range(constants.NUM_SNAPSHOTS):
        preset["data"]["tone"][f"snapshot{snapshot_num}"]["@ledcolor"] = str(snapshot_num + 1)


def add_dsp_controller_and_snapshot_keys_if_missing(preset):
    for dsp in ["dsp0", "dsp1"]:
        preset["data"]["tone"].setdefault(dsp, {})
        preset["data"]["tone"].setdefault("controller", {}).setdefault(dsp, {})
        for snapshot_num in range(constants.NUM_SNAPSHOTS):
            snapshot_name = f"snapshot{snapshot_num}"
            preset["data"]["tone"].setdefault(snapshot_name, {}).setdefault("controllers", {}).setdefault(dsp, {})


def populate_controller_dsp_slot_from_raw_default(preset, dsp, slot):
    controller_block_dict = file.reload_raw_block_dictionary(preset, dsp, slot)["Ranges"]
    get_controller_dsp_slot(preset, dsp, slot).update(controller_block_dict)
    # print("populate_controller_from_defaults " + get_model_name(preset, dsp, slot) + ", " + dsp + " " + slot)


def populate_missing_controller_slots_from_raw_defaults(preset):
    for dsp in get_available_default_dsps(preset):
        for slot in get_default_dsp(preset, dsp):
            if slot not in get_controller_dsp(preset, dsp) and slot.startswith(("block", "split", "cab")):
                get_controller_dsp(preset, dsp)[slot] = {}
                populate_controller_dsp_slot_from_raw_default(preset, dsp, slot)


def populate_missing_snapshot_controllers_from_raw_defaults(preset, snapshot_num):
    for dsp in get_available_default_dsps(preset):
        for slot in get_default_dsp(preset, dsp):
            if slot not in get_snapshot_controllers_dsp(preset, snapshot_num, dsp) and slot.startswith(
                ("block", "split", "cab")
            ):
                get_snapshot_controllers_dsp(preset, snapshot_num, dsp)[slot] = {}
                snapshot_block_dict = file.reload_raw_block_dictionary(preset, dsp, slot)["SnapshotParams"]
                get_snapshot_controllers_dsp_slot(preset, snapshot_num, dsp, slot).update(snapshot_block_dict)


def copy_controlled_default_parameter_values_to_snapshot(preset, snapshot_num):
    for dsp in get_available_default_dsps(preset):
        for slot in get_controller_dsp(preset, dsp):
            for parameter in get_controller_dsp_slot(preset, dsp, slot):
                get_snapshot_controllers_dsp_slot(preset, snapshot_num, dsp, slot)[parameter].update(
                    get_default_dsp_slot(preset, dsp, slot)[parameter]
                )


# def populate_all_missing_snapshot_controllers_from_defaults(preset):
#     print("populate_all_snapshot_controllers_from_defaults")
#     for snapshot_num in range(constants.NUM_SNAPSHOTS):
#         populate_missing_snapshot_controllers_from_defaults(preset, snapshot_num)


def count_controllers(preset):
    count = 0
    for dsp in get_available_default_dsps(preset):
        for slot in get_default_dsp(preset, dsp):
            if slot in get_controller_dsp(preset, dsp):
                count += 1
    return count


# def copy_defaults_to_all_snapshots(preset):
#     for dsp in get_available_default_dsps(preset):
#         for slot in get_default_dsp(preset, dsp):
#             if slot in get_controller_dsp(preset, dsp):
#                 for snapshot_num in range(constants.NUM_SNAPSHOTS):
#                     get_snapshot_controllers_dsp_slot(preset, snapshot_num, dsp, slot).update(
#                         get_controller_dsp_slot(preset, dsp, slot)
#                     )
