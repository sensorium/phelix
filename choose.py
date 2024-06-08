from copy import deepcopy
import os
import random
import constants
import utils
import file


def random_block_file_excluding_cab_or_split():
    random_category = random_block_category()
    while random_category in ["Split", "Cab"]:
        random_category = random_block_category()
    return random_block_file_in_category(random_category)


def random_block_file_in_category(category_folder):
    folder_path = os.path.join(constants.BLOCKS_PATH, category_folder)
    block_files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
    filepath = os.path.join(folder_path, random.choice(block_files))
    print("  choosing " + filepath)
    return filepath


def random_block_split_or_cab_in_dsps(preset):
    dsp = random.choice(["dsp0", "dsp1"])
    slot = random.choice(list(preset["data"]["tone"][dsp].keys()))
    if slot.startswith(("block", "split", "cab")):
        return dsp, slot
    else:
        return random_block_split_or_cab_in_dsps(preset)


def random_dsp_and_block(preset):
    # returns a random block, or "none" if there are no blocks
    found_blocks = []
    for dsp in ["dsp0", "dsp1"]:
        for slot in preset["data"]["tone"]["controller"][dsp]:
            found_blocks.append((dsp, slot))
    rand_dsp_and_block = ["none", "none"]
    if len(found_blocks) > 0:
        rand_dsp_and_block = random.choice(found_blocks)
    return rand_dsp_and_block


def random_controller_param(preset, dsp, block):
    # returns a random param, or "none" if there are no params
    # print("getRandControllerParam for "+dsp+" "+block)
    params = []
    for param in preset["data"]["tone"]["controller"][dsp][block]:
        params.append(param)
        # print("append to getRandControllerParam choices " +param)
    randparam = "none"
    if len(params) > 0:
        randparam = random.choice(params)
    return randparam


def random_controller_param_excluding_bools_and_mic(preset, dsp, slot):
    # returns a random param (but not one with a boolean value), or "none" if there are no params
    params = []
    for param in preset["data"]["tone"]["controller"][dsp][slot]:
        if (
            not isinstance(
                preset["data"]["tone"]["controller"][dsp][slot][param]["@min"],
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


def random_controlled_parameter_and_ranges(preset, control_num):
    randdsp, randblock = random_dsp_and_block(preset)
    if randblock != "none":
        if control_num == constants.PEDAL_2:
            randparam = random_controller_param_excluding_bools_and_mic(preset, randdsp, randblock)
        else:
            randparam = random_controller_param(preset, randdsp, randblock)
        if randparam != "none":
            controlled_param = preset["data"]["tone"]["controller"][randdsp][randblock][randparam]
            controlled_param["@controller"] = control_num
            new_max = random.uniform(controlled_param["@min"], controlled_param["@max"])
            new_min = random.uniform(controlled_param["@min"], controlled_param["@max"])
            # set new random max and min values within the original limits
            controlled_param["@max"] = new_max
            controlled_param["@min"] = new_min
            model_name = preset["data"]["tone"][randdsp][randblock]["@model"]
            print("set controller " + str(control_num) + " to " + randdsp, randblock, model_name, randparam)


def random_block_category() -> str:
    block_categories = [
        ("Amp", 20),
        ("Cab", 10),
        ("Delay", 20),
        ("Distort", 15),
        ("Dynamics", 10),
        ("EQ", 20),
        ("Filter", 5),
        ("Mod", 30),
        ("PitchSynth", 10),
        ("Reverb", 25),
        ("Split", 10),
        ("Wah", 10),
    ]
    # make 1 choice with weighted probabilities
    return random.choices(
        [choice[0] for choice in block_categories], weights=[choice[1] for choice in block_categories], k=1
    )[0]


def random_remove_controls(preset, control_num, num_changes):
    controlled_param_list = utils.list_pedal_controls(preset, control_num)
    for _ in range(num_changes):
        random_controller_to_snapshot(preset, controlled_param_list, control_num)


def random_new_params_for_snapshot_control(preset):
    num_controllers_to_change = random.randint(0, 20)
    for i in range(num_controllers_to_change):
        remove_one_random_controller_parameter(preset)

    while utils.count_parameters_in_controller(preset) < 64:  # to avoid setting any twice
        add_random_parameter_to_controller(preset)


def random_controller_to_snapshot(preset, param_list, control_num):
    # choose a block,param pair
    random_index = random.randint(0, len(param_list) - 1)
    dsp, block, param = param_list[random_index]
    # set control to snapshot
    preset["data"]["tone"]["controller"][dsp][block][param]["@controller"] = constants.SNAPSHOT_CONTROL
    model_name = preset["data"]["tone"][dsp][block]["@model"]
    print("set control " + control_num + " for " + dsp, block, model_name, param)


def remove_one_random_controller_parameter(preset):
    # delete a param if the random choice exists
    randdsp, randblock = random_dsp_and_block(preset)
    if randblock != "none":
        randparam = random_controller_param(preset, randdsp, randblock)
        if randparam != "none":
            # remove the param from all snapshots
            for snapshot_num in range(constants.NUM_SNAPSHOTS):
                snapshot_name = f"snapshot{snapshot_num}"
                if randparam in preset["data"]["tone"][snapshot_name]["controllers"][randdsp][randblock]:
                    del preset["data"]["tone"][snapshot_name]["controllers"][randdsp][randblock][randparam]

            # remove param from controller
            utils.remove_parameter_from_controller(preset, randdsp, randblock, randparam)


def add_random_parameter_to_controller(preset):
    dsp, slot_name = random_block_split_or_cab_in_dsps(preset)
    print("putRandomParamInController from " + dsp, slot_name)

    if slot_name not in preset["data"]["tone"]["controller"][dsp]:
        preset["data"]["tone"]["controller"][dsp][slot_name] = {}
    params_not_in_controller = [
        parameter
        for parameter in preset["data"]["tone"][dsp][slot_name]
        if parameter not in preset["data"]["tone"]["controller"][dsp][slot_name]
        and not parameter.startswith("@")
        and not parameter.startswith("bypass")
        and not parameter.startswith("Pan")  # extra unshown uncontrolable parameters in SimplePitchSynth
        and not parameter.startswith("TempoSync1")  # not visible for GlitchDelay, maybe others
        and not parameter.startswith("Lock")  # not visible for GlitchDelay, maybe others
        and not parameter.startswith("Scale")  # Heliosphere Delay
    ]
    if params_not_in_controller:
        random_param = random.choice(params_not_in_controller)
        print(params_not_in_controller)
        print(random_param)
        block_dict = file.reload_unpruned_block_dictionary(preset, dsp, slot_name)
        # print(block_dict["Ranges"][random_param])
        preset["data"]["tone"]["controller"][dsp][slot_name][random_param] = {}
        preset["data"]["tone"]["controller"][dsp][slot_name][random_param] = deepcopy(
            block_dict["Ranges"][random_param]
        )
        preset["data"]["tone"]["controller"][dsp][slot_name][random_param]["@controller"] = 19
        # add the param to snapshots
        utils.add_parameter_to_all_snapshots(preset, dsp, slot_name, random_param)


def random_series_or_parallel_dsp_configuration(preset):
    preset["data"]["tone"]["dsp0"]["outputA"]["@output"] = random.choice([1, 2])
