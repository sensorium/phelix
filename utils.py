from copy import deepcopy
import constants


def add_block_to_preset(preset, dsp, slot, block_dict):
    add_block_to_dsp(preset, dsp, slot, block_dict)
    add_block_to_controller(preset, dsp, slot, block_dict)
    add_block_to_snapshots(preset, dsp, slot, block_dict)


def add_block_to_dsp(preset, dsp, slot, block_dict):
    preset["data"]["tone"][dsp][slot] = deepcopy(block_dict["Defaults"])


def add_block_to_controller(preset, dsp, slot, block_dict):
    preset["data"]["tone"]["controller"][dsp][slot] = deepcopy(block_dict["Ranges"])
    # print(" added block to controller: " + dsp, slot, block_dict["Defaults"]["@model"])


def add_block_to_snapshots(preset, dsp, destination_slot, block_dict):
    # print("Adding block to snapshots")
    for snapshot_num in range(constants.NUM_SNAPSHOTS):
        snapshot_name = f"snapshot{snapshot_num}"
        preset["data"]["tone"][snapshot_name]["controllers"][dsp][destination_slot] = deepcopy(
            block_dict["SnapshotParams"]
        )


def list_pedal_controls(preset, controller_num):
    # get a list of params with control (eg. pedal controller number 2)
    params_with_control_set_to_pedal = []
    for dsp in ["dsp0", "dsp1"]:
        for block in preset["data"]["tone"]["controller"][dsp]:
            for param in preset["data"]["tone"]["controller"][dsp][block]:
                if preset["data"]["tone"]["controller"][dsp][block][param]["@controller"] == controller_num:
                    params_with_control_set_to_pedal.append([dsp, block, param])
    return params_with_control_set_to_pedal


def count_parameters_in_controller(preset):
    num_params = 0
    for dsp in ["dsp0", "dsp1"]:
        for slot in preset["data"]["tone"]["controller"][dsp]:
            if slot.startswith(("block", "split", "cab")):
                for parameter in preset["data"]["tone"]["controller"][dsp][slot]:
                    # print("counting " + parameter)
                    num_params += 1
    return num_params


def add_parameter_to_all_snapshots(preset, dsp, slot, random_param):
    """
    Adds a parameter to the snapshot dictionaries for a block.

    Parameters
    ----------
    preset : dict
        The dictionary containing the entire preset.
    dsp : str
        The name of the DSP (either "dsp0" or "dsp1").
    slot : str
        The name of the block.
    random_param : str
        The name of the parameter to be added to the snapshot.

    Returns
    -------
    None

    """
    for snapshot_num in range(constants.NUM_SNAPSHOTS):
        snapshot_name = f"snapshot{snapshot_num}"
        if snapshot_name in preset["data"]["tone"][dsp][slot]:
            snapshot_dict = preset["data"]["tone"][dsp][slot][snapshot_name]
            snapshot_dict[random_param] = deepcopy(preset["data"]["tone"]["controller"][dsp][slot][random_param])


def remove_parameter_from_controller(preset, dsp, slot, param):
    if param in preset["data"]["tone"]["controller"][dsp][slot]:
        del preset["data"]["tone"]["controller"][dsp][slot][param]
    model_name = preset["data"]["tone"][dsp][slot]["@model"]
    print("removed controller for " + param + " in " + model_name + ", " + dsp + " " + slot)


def set_led_colours(preset):
    for snapshot_num in range(constants.NUM_SNAPSHOTS):
        snapshot_name = f"snapshot{snapshot_num}"
        # snapshot ledcolor
        preset["data"]["tone"][snapshot_name]["@ledcolor"] = str(snapshot_num + 1)
