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


def add_block_to_snapshots(preset_dict, dsp_name, destination_slot, block_dict):
    # print("Adding block to snapshots")
    for snapshot_num in range(constants.NUM_SNAPSHOTS):
        snapshot_name = "snapshot" + str(snapshot_num)
        preset_dict["data"]["tone"][snapshot_name]["controllers"][dsp_name][destination_slot] = deepcopy(
            block_dict["SnapshotParams"]
        )


def list_pedal_controls(preset_dict, controller_num):
    # get a list of params with control (eg. pedal controller number 2)
    params_with_control_set_to_pedal = []
    for dsp_name in ["dsp0", "dsp1"]:
        for block in preset_dict["data"]["tone"]["controller"][dsp_name]:
            for param in preset_dict["data"]["tone"]["controller"][dsp_name][block]:
                if preset_dict["data"]["tone"]["controller"][dsp_name][block][param]["@controller"] == controller_num:
                    params_with_control_set_to_pedal.append([dsp_name, block, param])
    return params_with_control_set_to_pedal


def count_parameters_in_controller(preset_dict):
    num_params = 0
    for dsp_name in ["dsp0", "dsp1"]:
        for block_name in preset_dict["data"]["tone"]["controller"][dsp_name]:
            if block_name.startswith(("block", "split", "cab")):
                for parameter in preset_dict["data"]["tone"]["controller"][dsp_name][block_name]:
                    # print("counting " + parameter)
                    num_params += 1
    return num_params


def add_parameter_to_all_snapshots(preset_dict, dsp_name, block_name, random_param):
    """
    Adds a parameter to the snapshot dictionaries for a block.

    Parameters
    ----------
    preset_dict : dict
        The dictionary containing the entire preset.
    dsp_name : str
        The name of the DSP (either "dsp0" or "dsp1").
    block_name : str
        The name of the block.
    random_param : str
        The name of the parameter to be added to the snapshot.

    Returns
    -------
    None

    """
    for snapshot_num in range(constants.NUM_SNAPSHOTS):
        snapshot_name = "snapshot" + str(snapshot_num)
        if snapshot_name in preset_dict["data"]["tone"][dsp_name][block_name]:
            snapshot_dict = preset_dict["data"]["tone"][dsp_name][block_name][snapshot_name]
            snapshot_dict[random_param] = deepcopy(
                preset_dict["data"]["tone"]["controller"][dsp_name][block_name][random_param]
            )
