from copy import deepcopy
import json
import random
import os
import file

PEDAL_2 = 2
NUM_SNAPSHOTS = 8
NUM_SLOTS_PER_DSP = 16
NUM_PEDAL_PARAMS = 16

LAST_SLOT_POSITION = 8


# functions that start with "get"
def choose_random_dsp_and_block(preset_dict):
    # returns a random block, or "none" if there are no blocks
    dsp_names = ["dsp0", "dsp1"]
    found_blocks = []
    for dsp_name in dsp_names:
        for block_name in preset_dict["data"]["tone"]["controller"][dsp_name]:
            found_blocks.append((dsp_name, block_name))
    rand_dsp_and_block = ["none", "none"]
    if len(found_blocks) > 0:
        rand_dsp_and_block = random.choice(found_blocks)
    return rand_dsp_and_block


def choose_random_controller_param(preset_dict, dsp_name, block):
    # returns a random param, or "none" if there are no params
    # print("getRandControllerParam for "+dsp_name+" "+block)
    params = []
    for param in preset_dict["data"]["tone"]["controller"][dsp_name][block]:
        params.append(param)
        # print("append to getRandControllerParam choices " +param)
    randparam = "none"
    if len(params) > 0:
        randparam = random.choice(params)
    return randparam


def choose_random_controller_param_excluding_bools_and_mic(preset_dict, dsp_name, block):
    # returns a random param (but not one with a boolean value), or "none" if there are no params
    params = []
    for param in preset_dict["data"]["tone"]["controller"][dsp_name][block]:
        if (
            not isinstance(
                preset_dict["data"]["tone"]["controller"][dsp_name][block][param]["@min"],
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


def choose_random_controlled_parameter_and_ranges(preset_dict, control_num):
    randdsp, randblock = choose_random_dsp_and_block(preset_dict)
    if randblock != "none":
        if control_num == PEDAL_2:
            randparam = choose_random_controller_param_excluding_bools_and_mic(preset_dict, randdsp, randblock)
        else:
            randparam = choose_random_controller_param(preset_dict, randdsp, randblock)
        if randparam != "none":
            controlled_param = preset_dict["data"]["tone"]["controller"][randdsp][randblock][randparam]
            controlled_param["@controller"] = control_num
            new_max = random.uniform(controlled_param["@min"], controlled_param["@max"])
            new_min = random.uniform(controlled_param["@min"], controlled_param["@max"])
            # set new random max and min values within the original limits
            controlled_param["@max"] = new_max
            controlled_param["@min"] = new_min
            model_name = preset_dict["data"]["tone"][randdsp][randblock]["@model"]
            print("set controller " + str(control_num) + " to " + randdsp, randblock, model_name, randparam)


def set_led_colours(preset_dict):
    for snapshot_num in range(NUM_SNAPSHOTS):
        snapshot_name = "snapshot" + str(snapshot_num)
        # snapshot ledcolor
        preset_dict["data"]["tone"][snapshot_name]["@ledcolor"] = str(snapshot_num + 1)


def add_random_parameter_to_controller(preset_dict):
    dsp_name, slot_name = choose_random_block_split_or_cab_in_dsps(preset_dict)
    print("putRandomParamInController from " + dsp_name, slot_name)

    if slot_name not in preset_dict["data"]["tone"]["controller"][dsp_name]:
        preset_dict["data"]["tone"]["controller"][dsp_name][slot_name] = {}
    params_not_in_controller = [
        parameter
        for parameter in preset_dict["data"]["tone"][dsp_name][slot_name]
        if parameter not in preset_dict["data"]["tone"]["controller"][dsp_name][slot_name]
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
        block_dict = file.load_block_dictionary_from_file(preset_dict, dsp_name, slot_name)
        # print(block_dict["Ranges"][random_param])
        preset_dict["data"]["tone"]["controller"][dsp_name][slot_name][random_param] = {}
        preset_dict["data"]["tone"]["controller"][dsp_name][slot_name][random_param] = deepcopy(
            block_dict["Ranges"][random_param]
        )
        preset_dict["data"]["tone"]["controller"][dsp_name][slot_name][random_param]["@controller"] = 19
        # add the param to snapshots
        add_parameter_to_all_snapshots(preset_dict, dsp_name, slot_name, random_param)


def get_mutated_parameter_value(preset_dict, dsp_name, block_name, parameter, pmin, pmax):
    defaults_block = preset_dict["data"]["tone"][dsp_name][block_name]

    # do the right thing for the kind of parameter
    if isinstance(pmin, bool):
        result = random.choice([True, False])
    elif (block_name.startswith("block") or block_name.startswith("cab")) and parameter == "Level":
        lowest = ((pmax - pmin) * 0.2) + pmin
        mode = ((pmax - pmin) * 0.8) + pmin  # choose level from 0.2 to max, peak around 0.8 of max range
        result = random.triangular(lowest, pmax, mode)
    elif parameter == "Time":  # choose times at the short end
        # mode = ((pmax-pmin) * 0.1) + pmin
        # result = random.triangular(pmin, pmax, mode)
        closer_to_one_for_lower_num = 0.95 + (0.75 - 0.95) * (pmax - 2) / (8 - 2)
        result = min(pmax, random.expovariate(closer_to_one_for_lower_num))
        # print("setting Time, max "+str(pmax),str(result))
    elif parameter == "Mix":  # choose mix around middle
        lowest = ((pmax - pmin) * 0.2) + pmin  # choose mix from 0.2 to max, peak around 0.5 of max range
        mode = ((pmax - pmin) * 0.5) + pmin
        result = random.triangular(lowest, pmax, mode)
    elif parameter == "Feedback":  # choose feedback around middle
        mode = ((pmax - pmin) * 0.5) + pmin
        result = random.triangular(pmin, pmax, mode)
    elif (
        defaults_block["@model"].startswith("HD2_Reverb")
        or defaults_block["@model"].startswith("VIC")
        or defaults_block["@model"].startswith("Victoria")
    ) and parameter == "Decay":
        mode = ((pmax - pmin) * 0.05) + pmin
        result = random.triangular(pmin, pmax, mode)
        # result = min(pmax, random.expovariate(0.5))
    else:
        result = random.uniform(pmin, pmax)  # switch choices are rounded to nearest integer in helix
    return result


# chooses and stores parameter values for one block into a single snapshot
#
def mutate_parameter_values_for_one_block(preset_dict, snapshot_num, dsp_name, slot_name, fraction_new):
    snapshot_name = "snapshot" + str(snapshot_num)
    snapshot_slot = preset_dict["data"]["tone"][snapshot_name]["controllers"][dsp_name][slot_name]
    controllers_block_dict = preset_dict["data"]["tone"]["controller"][dsp_name][slot_name]
    model_name = preset_dict["data"]["tone"][dsp_name][slot_name]["@model"]
    # print(preset_dict["data"]["tone"][dsp_name][slot_name])
    print("looking for " + model_name)
    unpruned_block_ranges = file.load_block_dictionary_from_file(preset_dict, dsp_name, slot_name)["Ranges"]

    print("mutating", dsp_name, slot_name, model_name)
    for parameter in unpruned_block_ranges:
        if not parameter.startswith("@"):
            pmin = unpruned_block_ranges[parameter]["@min"]
            pmax = unpruned_block_ranges[parameter]["@max"]
            result = get_mutated_parameter_value(preset_dict, dsp_name, slot_name, parameter, pmin, pmax)

        if parameter in controllers_block_dict:
            print("  about to mutate " + parameter)
            # prev_result = snapshot_slot[parameter]["@value"]
            prev_result = preset_dict["data"]["tone"][snapshot_name]["controllers"][dsp_name][slot_name][parameter][
                "@value"
            ]
            result_mix = mix_values(fraction_new, pmin, pmax, result, prev_result)
            preset_dict["data"]["tone"][snapshot_name]["controllers"][dsp_name][slot_name][parameter][
                "@value"
            ] = result_mix
            # snapshot_slot[parameter]["@value"] = result_mix


def mutate_default_block(preset_dict, dsp_name, slot_name, fraction_new):
    defaults_block = preset_dict["data"]["tone"][dsp_name][slot_name]
    unpruned_block_ranges = file.load_block_dictionary_from_file(preset_dict, dsp_name, slot_name)["Ranges"]
    for parameter in defaults_block:
        if not parameter.startswith("@"):
            pmin = unpruned_block_ranges[parameter]["@min"]
            pmax = unpruned_block_ranges[parameter]["@max"]
            result = get_mutated_parameter_value(preset_dict, dsp_name, slot_name, parameter, pmin, pmax)
            if isinstance(result, bool):
                defaults_block[parameter] = result
            else:
                # random nudge default param
                prev_result = defaults_block[parameter]
                fraction_prev = 1.0 - fraction_new
                result_mix = result * fraction_new + prev_result * fraction_prev
                result_mix_constrained = max(pmin, min(result_mix, pmax))
                defaults_block[parameter] = result_mix_constrained


def mutate_all_default_blocks(preset_dict, fraction_new):
    for dsp_name in ["dsp0", "dsp1"]:
        for slot_name in preset_dict["data"]["tone"][dsp_name]:
            if slot_name.startswith(("cab", "split", "block")):
                mutate_default_block(preset_dict, dsp_name, slot_name, fraction_new)


def mix_values(fraction_new, pmin, pmax, result, prev_result):
    if isinstance(result, bool):
        return result
    fraction_prev = 1.0 - fraction_new
    result_mix = result * fraction_new + prev_result * fraction_prev
    result_mix_constrained = max(pmin, min(result_mix, pmax))
    return result_mix_constrained
    # print(pmin, pmax, prev_result, result_mix_constrained)


def mutate_parameter_values_for_all_snapshots(preset_dict):
    for snapshot_num in range(NUM_SNAPSHOTS):
        snapshot_name = "snapshot" + str(snapshot_num)
        for dsp_name in ["dsp0", "dsp1"]:
            for block_name in preset_dict["data"]["tone"][snapshot_name]["controllers"][dsp_name]:
                mutate_parameter_values_for_one_block(preset_dict, snapshot_num, dsp_name, block_name, 1.0)


def mutate_parameter_value(mean, p_min, p_max):
    p_range = p_max - p_min
    sigma = p_range / 4
    p = random.normalvariate(mean, sigma)
    while not p_min <= p <= p_max:
        p = random.normalvariate(mean, sigma)
    return p


def choose_block_category() -> str:
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


def choose_random_block_file_of_type(category):
    random_category = choose_block_category()
    while random_category in ["Split", "Cab"]:
        random_category = choose_block_category()
    return choose_block_file_in_category(category)


def choose_random_block_file_excluding_cab_or_split():
    random_category = choose_block_category()
    while random_category in ["Split", "Cab"]:
        random_category = choose_block_category()
    return choose_block_file_in_category(random_category)


def choose_block_file_in_category(category_folder):
    full_path = os.path.join(file.BLOCKS_PATH, category_folder)
    block_files = [f for f in os.listdir(full_path) if os.path.isfile(os.path.join(full_path, f))]
    filename = os.path.join(full_path, random.choice(block_files))
    print("choosing" + filename)
    return filename


def choose_random_block_split_or_cab_in_dsps(preset_dict):
    dsp_name = random.choice(["dsp0", "dsp1"])
    block_name = random.choice(list(preset_dict["data"]["tone"][dsp_name].keys()))
    if block_name.startswith(("block", "split", "cab")):
        return dsp_name, block_name
    else:
        return choose_random_block_split_or_cab_in_dsps(preset_dict)


def list_pedal_controls(preset_dict, controller_num):
    # get a list of params with control (eg. pedal controller number 2)
    params_with_control_set_to_pedal = []
    for dsp_name in ["dsp0", "dsp1"]:
        for block in preset_dict["data"]["tone"]["controller"][dsp_name]:
            for param in preset_dict["data"]["tone"]["controller"][dsp_name][block]:
                if preset_dict["data"]["tone"]["controller"][dsp_name][block][param]["@controller"] == controller_num:
                    params_with_control_set_to_pedal.append([dsp_name, block, param])
    return params_with_control_set_to_pedal


SNAPSHOT_CONTROL = 19


def set_controller_to_snapshot(preset_dict, param_list, control_num):
    # choose a block,param pair
    random_index = random.randint(0, len(param_list) - 1)
    dsp_name, block, param = param_list[random_index]
    # set control to snapshot
    preset_dict["data"]["tone"]["controller"][dsp_name][block][param]["@controller"] = SNAPSHOT_CONTROL
    model_name = preset_dict["data"]["tone"][dsp_name][block]["@model"]
    print("set control " + control_num + " for " + dsp_name, block, model_name, param)


def choose_and_remove_controls(preset_dict, control_num, num_changes):
    controlled_param_list = list_pedal_controls(preset_dict, control_num)
    for _ in range(num_changes):
        set_controller_to_snapshot(preset_dict, controlled_param_list, control_num)


def swap_some_control_destinations(preset_dict, control_num, max_changes):
    num_changes = random.randint(0, max_changes)
    choose_and_remove_controls(preset_dict, control_num, num_changes)
    for _ in range(num_changes):
        # set another param to pedalnum
        choose_random_controlled_parameter_and_ranges(preset_dict, control_num)


def choose_some_new_params_for_snapshot_control(preset_dict):
    num_controllers_to_change = random.randint(0, 20)
    for i in range(num_controllers_to_change):
        remove_one_random_controller_parameter(preset_dict)

    while count_parameters_in_controller(preset_dict) < 64:  # to avoid setting any twice
        add_random_parameter_to_controller(preset_dict)


def toggle_some_block_states(preset_dict, change_fraction):
    # global num_snapshots
    for snapshot_num in range(NUM_SNAPSHOTS):
        snapshot_name = f"snapshot{snapshot_num}"
        snapshot_blocks = preset_dict["data"]["tone"][snapshot_name]["blocks"]
        for dsp_name in ["dsp0", "dsp1"]:
            if dsp_name in snapshot_blocks:
                for block_name in snapshot_blocks[dsp_name]:
                    if block_name.startswith(("block", "cab")):
                        if random.uniform(0, 1) < change_fraction:  # change state
                            current_state = snapshot_blocks[dsp_name][block_name]
                            new_state = not current_state
                            snapshot_blocks[dsp_name][block_name] = new_state
                            print(
                                f"{snapshot_name} changed state of {dsp_name} {block_name} from {current_state} to {new_state}"
                            )


def toggle_series_or_parallel_dsps(preset_dict, change_fraction):
    if random.uniform(0, 1) < change_fraction:  # change state
        print("toggling series or parallel dsps")
        current = preset_dict["data"]["tone"]["dsp0"]["outputA"]["@output"]
        if current == 1:
            preset_dict["data"]["tone"]["dsp0"]["outputA"]["@output"] = 2
        else:
            preset_dict["data"]["tone"]["dsp0"]["outputA"]["@output"] = 1


def count_parameters_in_controller(preset_dict):
    num_params = 0
    for dsp_name in ["dsp0", "dsp1"]:
        for block_name in preset_dict["data"]["tone"]["controller"][dsp_name]:
            if block_name.startswith(("block", "split", "cab")):
                for parameter in preset_dict["data"]["tone"]["controller"][dsp_name][block_name]:
                    # print("counting " + parameter)
                    num_params += 1
    return num_params


def remove_one_random_controller_parameter(preset_dict):
    # delete a param if the random choice exists
    randdsp, randblock = choose_random_dsp_and_block(preset_dict)
    if randblock != "none":
        randparam = choose_random_controller_param(preset_dict, randdsp, randblock)
        if randparam != "none":
            # remove the param from all snapshots
            for snapshot_num in range(NUM_SNAPSHOTS):
                snapshot_name = "snapshot" + str(snapshot_num)
                if randparam in preset_dict["data"]["tone"][snapshot_name]["controllers"][randdsp][randblock]:
                    del preset_dict["data"]["tone"][snapshot_name]["controllers"][randdsp][randblock][randparam]

            # remove param from controller
            if randparam in preset_dict["data"]["tone"]["controller"][randdsp][randblock]:
                del preset_dict["data"]["tone"]["controller"][randdsp][randblock][randparam]
            model_name = preset_dict["data"]["tone"][randdsp][randblock]["@model"]
            print("removed controller for " + randparam + " in " + model_name + ", " + randdsp + " " + randblock)


def duplicate_snapshot(preset_dict, snapshot_src, snapshot_dst):
    preset_dict["data"]["tone"][snapshot_dst] = deepcopy(preset_dict["data"]["tone"][snapshot_src])
    preset_dict["data"]["tone"][snapshot_dst]["@name"] = snapshot_dst


def duplicate_snapshot_to_all(preset_dict, snapshot_src):
    for snapshot_num in range(NUM_SNAPSHOTS):
        snapshot_dst = "snapshot" + str(snapshot_num)
        if snapshot_dst != snapshot_src:
            duplicate_snapshot(preset_dict, snapshot_src, snapshot_dst)


def find_unused_slot_name_in_dsp(preset_dict, dsp_name):
    for i in range(16):
        new_block_name = "block" + str(i)
        if new_block_name not in preset_dict["data"]["tone"][dsp_name]:
            break
    return new_block_name


def rearrange_block_positions(preset_dict, fraction_move):
    dsp_names = ["dsp0", "dsp1"]
    # find block positions
    found_dsp_path_pos = []
    for dsp_name in dsp_names:
        for block_name in preset_dict["data"]["tone"][dsp_name]:
            block_dict = preset_dict["data"]["tone"][dsp_name][block_name]
            if block_name.startswith("block"):
                found_dsp_path_pos.append([dsp_name, block_dict["@path"], block_dict["@position"]])

    # find vacant positions
    vacant_dsp_path_pos = []
    for dsp_name in dsp_names:
        for path in (0, 1):
            for pos in range(LAST_SLOT_POSITION):  # slots per path
                if [dsp_name, path, pos] not in found_dsp_path_pos:
                    vacant_dsp_path_pos.append([dsp_name, path, pos])

    # print(vacant_dsp_path_pos)

    dsp_blockname_to_dsp_path_pos = []
    for dsp_name in dsp_names:
        for block_name in preset_dict["data"]["tone"][dsp_name]:
            if block_name.startswith("block"):
                chance = random.uniform(0, 1)
                if chance < fraction_move:
                    from_path = preset_dict["data"]["tone"][dsp_name][block_name]["@path"]
                    from_position = preset_dict["data"]["tone"][dsp_name][block_name]["@position"]
                    # choose a vacant position from vacant_dsp_path_pos[]
                    random_index = random.randint(0, len(vacant_dsp_path_pos) - 1)
                    new_dsp_path_position = vacant_dsp_path_pos[random_index]
                    vacant_dsp_path_pos.remove(new_dsp_path_position)  # remove it from list of vacant positions
                    vacant_dsp_path_pos.append([dsp_name, from_path, from_position])
                    dsp_blockname_to_dsp_path_pos.append([dsp_name, block_name, new_dsp_path_position])
    # print(dsp_blockname_to_dsp_path_pos)
    move_blocks(preset_dict, dsp_blockname_to_dsp_path_pos)


def move_blocks(preset_dict, dsp_slot_name_to_dsp_path_pos):
    for item in dsp_slot_name_to_dsp_path_pos:
        from_dsp = item[0]
        slot_name = item[1]
        from_path = preset_dict["data"]["tone"][from_dsp][slot_name]["@path"]
        from_position = preset_dict["data"]["tone"][from_dsp][slot_name]["@position"]
        to_dsp = item[2][0]
        to_path = item[2][1]
        to_position = item[2][2]
        new_slot_name = find_unused_slot_name_in_dsp(preset_dict, to_dsp)
        preset_dict["data"]["tone"][to_dsp][new_slot_name] = preset_dict["data"]["tone"][from_dsp].pop(slot_name)
        preset_dict["data"]["tone"][to_dsp][new_slot_name]["@path"] = to_path
        preset_dict["data"]["tone"][to_dsp][new_slot_name]["@position"] = to_position
        preset_dict["data"]["tone"]["controller"][to_dsp][new_slot_name] = preset_dict["data"]["tone"]["controller"][
            from_dsp
        ].pop(slot_name)

        for snapshot_num in range(NUM_SNAPSHOTS):
            snapshot_name = "snapshot" + str(snapshot_num)
            # preset_dict["data"]["tone"][snapshot_name]["blocks"][to_dsp][new_slot_name] = deepcopy(
            #     preset_dict["data"]["tone"][snapshot_name]["blocks"][from_dsp][slot_name]
            # )
            preset_dict["data"]["tone"][snapshot_name]["blocks"][to_dsp][new_slot_name] = preset_dict["data"]["tone"][
                snapshot_name
            ]["blocks"][from_dsp].pop(slot_name)

        print(
            "Moved",
            from_dsp,
            slot_name,
            from_path,
            from_position,
            "to",
            to_dsp,
            new_slot_name,
            to_path,
            to_position,
        )


def add_block_to_snapshots(preset_dict, dsp_name, destination_slot_name, new_block_dict):
    for snapshot_num in range(NUM_SNAPSHOTS):
        snapshot_name = "snapshot" + str(snapshot_num)
        preset_dict["data"]["tone"][snapshot_name]["controllers"][dsp_name][destination_slot_name] = deepcopy(
            new_block_dict["SnapshotParams"]
        )


def swap_some_blocks_and_splits_from_file(preset_dict, change_fraction):
    for dsp_name in ["dsp0", "dsp1"]:
        for block_name in preset_dict["data"]["tone"][dsp_name]:
            if block_name.startswith("block"):
                if random.uniform(0, 1) < change_fraction:  # change state
                    swap_block_from_file(preset_dict, dsp_name, block_name)
            if block_name.startswith("split"):
                if random.uniform(0, 1) < change_fraction:  # change state
                    swap_split_from_file(preset_dict, dsp_name, block_name)


def swap_block_from_file(preset_dict, dsp_name, block_name):
    print("swapping block from file")
    path = preset_dict["data"]["tone"][dsp_name][block_name]["@path"]
    pos = preset_dict["data"]["tone"][dsp_name][block_name]["@position"]
    new_block_dict = file.load_block_dictionary(choose_random_block_file_excluding_cab_or_split())
    preset_dict["data"]["tone"][dsp_name][block_name] = new_block_dict["Defaults"]
    preset_dict["data"]["tone"][dsp_name][block_name]["@path"] = path
    preset_dict["data"]["tone"][dsp_name][block_name]["@position"] = pos
    add_block_to_snapshots(preset_dict, dsp_name, block_name, new_block_dict)
    preset_dict["data"]["tone"]["controller"][dsp_name][block_name] = new_block_dict["Ranges"]
    for snapshot_num in range(NUM_SNAPSHOTS):
        mutate_parameter_values_for_one_block(preset_dict, snapshot_num, dsp_name, block_name, 1.0)


def swap_split_from_file(preset_dict, dsp_name, block_name):
    print("swapping split from file")
    pos = preset_dict["data"]["tone"][dsp_name][block_name]["@position"]
    new_block_dict = file.load_block_dictionary(choose_block_file_in_category("Split"))
    preset_dict["data"]["tone"][dsp_name][block_name] = new_block_dict["Defaults"]
    preset_dict["data"]["tone"][dsp_name][block_name]["@position"] = pos
    add_block_to_snapshots(preset_dict, dsp_name, block_name, new_block_dict)
    preset_dict["data"]["tone"]["controller"][dsp_name][block_name] = new_block_dict["Ranges"]
    for snapshot_num in range(NUM_SNAPSHOTS):
        mutate_parameter_values_for_one_block(preset_dict, snapshot_num, dsp_name, block_name, 1.0)


def increment_preset_name(preset_dict, postfix_num):
    name = preset_dict["data"]["meta"]["name"]
    name = name + str(postfix_num)
    preset_dict["data"]["meta"]["name"] = name
    print("Preset name: " + name)


def mutate_all_pedal_ranges(preset_dict):
    for dsp_name in ["dsp0", "dsp1"]:
        for block_split_cab_name in preset_dict["data"]["tone"]["controller"][dsp_name]:
            params = preset_dict["data"]["tone"]["controller"][dsp_name][block_split_cab_name]
            if any(params[param]["@controller"] == 2 for param in params):
                for param in params:
                    if params[param]["@controller"] == 2:
                        mutate_one_set_of_pedal_ranges(preset_dict, dsp_name, block_split_cab_name, param)
                break


def mutate_one_set_of_pedal_ranges(preset_dict, dsp_name, block_or_split_name, param_name):
    param = preset_dict["data"]["tone"]["controller"][dsp_name][block_or_split_name][param_name]
    if not isinstance(param["@min"], bool):  # don't want to pedal bools
        # get original ranges from file
        block_dict = file.load_block_dictionary_from_file(preset_dict, dsp_name, block_or_split_name)
        pmin = block_dict["Ranges"][param_name]["@min"]
        pmax = block_dict["Ranges"][param_name]["@max"]
        # print(pedalParam["@min"], pmin, pmax)
        new_min = mutate_parameter_value(param["@min"], pmin, pmax)  # (mean, pmin, pmax)
        new_max = mutate_parameter_value(param["@max"], pmin, pmax)
        param["@min"] = new_min
        param["@max"] = new_max


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
    for snapshot_num in range(NUM_SNAPSHOTS):
        snapshot_name = "snapshot" + str(snapshot_num)
        if snapshot_name in preset_dict["data"]["tone"][dsp_name][block_name]:
            snapshot_dict = preset_dict["data"]["tone"][dsp_name][block_name][snapshot_name]
            snapshot_dict[random_param] = deepcopy(
                preset_dict["data"]["tone"]["controller"][dsp_name][block_name][random_param]
            )


def mutate_dictionary(preset_dict, snapshot_src_num, postfix_num):
    increment_preset_name(preset_dict, postfix_num)
    snapshot_src_name = "snapshot" + str(snapshot_src_num)
    duplicate_snapshot_to_all(preset_dict, snapshot_src_name)
    choose_some_new_params_for_snapshot_control(preset_dict)
    mutate_parameter_values_for_all_snapshots(preset_dict)
    mutate_all_default_blocks(preset_dict, MUTATION_RATE)
    swap_some_control_destinations(preset_dict, PEDAL_2, 10)
    mutate_all_pedal_ranges(preset_dict)
    rearrange_block_positions(preset_dict, fraction_move)
    swap_some_blocks_and_splits_from_file(preset_dict, 0.1)
    toggle_some_block_states(preset_dict, MUTATION_RATE)
    toggle_series_or_parallel_dsps(preset_dict, 0.2)
    set_led_colours(preset_dict)


def mutate_preset_from_source_snapshot(template_file, snapshot_src_num, output_file, postfix_num):
    with open(template_file, "r") as f:
        preset_dict = json.load(f)
        mutate_dictionary(preset_dict, snapshot_src_num, postfix_num)
        with open(output_file, "w") as f:
            json.dump(preset_dict, f, indent=4)


MUTATION_RATE = 0.1
fraction_move = 0.1


# def mutations(num):
#     for i in range(num):
#         mutate_preset_from_source_snapshot(
#             "presets/test/aGenerated1.hlx",
#             6,
#             "presets/test/aGenerated1+" + str(i + 1) + ".hlx",
#             (i + 1),
#         )


def generate_multiple_mutations_from_template(args):
    preset_name_base = args.get("preset_name_base")
    for i in range(args.get("num_presets")):
        preset_name = preset_name_base + chr(ord("a") + (i % 26))
        mutate_preset_from_source_snapshot(
            args.get("template_file"),
            args.get("snapshot_src_num"),
            args.get("output_file")[:-4] + str(i + 1) + ".hlx",
            args.get("postfix_num"),
        )
