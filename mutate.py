from copy import deepcopy
import json
import random

import constants
import file
import utils
import choose


def set_led_colours(preset_dict):
    for snapshot_num in range(constants.NUM_SNAPSHOTS):
        snapshot_name = "snapshot" + str(snapshot_num)
        # snapshot ledcolor
        preset_dict["data"]["tone"][snapshot_name]["@ledcolor"] = str(snapshot_num + 1)


def get_mutated_parameter_value(preset, dsp, slot, parameter, pmin, pmax):
    defaults_block = preset["data"]["tone"][dsp][slot]
    parameter_settings = {
        "Level": lambda: (
            random_triangle(pmax, pmin, 0.8, 0.0)
            if (slot.startswith("block") or slot.startswith("cab"))
            else random.uniform(pmin, pmax)
        ),
        "Time": lambda: min(pmax, random.expovariate(0.95 + (0.75 - 0.95) * (pmax - 2) / (8 - 2))),
        "Mix": lambda: random_triangle(pmax, pmin, 0.5, 0.0),
        "Feedback": lambda: random_triangle(pmax, pmin, 0.5, 0.0),
        "Decay": lambda: (
            random_triangle(pmax, pmin, 0.05, 0.0)
            if defaults_block["@model"].startswith(("HD2_Reverb", "VIC", "Victoria"))
            else random.uniform(pmin, pmax)
        ),
    }

    if isinstance(pmin, bool):
        return random.choice([True, False])
    else:
        return parameter_settings.get(parameter, lambda: random.uniform(pmin, pmax))()


# def get_mutated_parameter_value(preset_dict, dsp_name, block_name, parameter, pmin, pmax):
#     defaults_block = preset_dict["data"]["tone"][dsp_name][block_name]

#     # do the right thing for the kind of parameter
#     if isinstance(pmin, bool):
#         return random.choice([True, False])
#     elif (block_name.startswith("block") or block_name.startswith("cab")) and parameter == "Level":
#         return get_triangular_random(pmax, pmin, 0.8, 0.0)
#     elif parameter == "Time":  # choose times at the short end
#         # mode = ((pmax-pmin) * 0.1) + pmin
#         # result = random.triangular(pmin, pmax, mode)
#         closer_to_one_for_lower_num = 0.95 + (0.75 - 0.95) * (pmax - 2) / (8 - 2)
#         return min(pmax, random.expovariate(closer_to_one_for_lower_num))
#         # print("setting Time, max "+str(pmax),str(result))
#     elif parameter == "Mix":  # choose mix around middle
#         return get_triangular_random(pmax, pmin, 0.5, 0.0)
#     elif parameter == "Feedback":  # choose feedback around middle
#         return get_triangular_random(pmax, pmin, 0.5, 0.0)
#         # mode = ((pmax - pmin) * 0.5) + pmin
#         # return random.triangular(pmin, pmax, mode)
#     elif (
#         defaults_block["@model"].startswith("HD2_Reverb")
#         or defaults_block["@model"].startswith("VIC")
#         or defaults_block["@model"].startswith("Victoria")
#     ) and parameter == "Decay":
#         return get_triangular_random(pmax, pmin, 0.05, 0.0)
#         # mode = ((pmax - pmin) * 0.05) + pmin
#         # return random.triangular(pmin, pmax, mode)
#         # result = min(pmax, random.expovariate(0.5))
#     else:
#         return random.uniform(pmin, pmax)


def random_triangle(pmax, pmin, mode_fraction, lowest_fraction):
    lowest = ((pmax - pmin) * lowest_fraction) + pmin
    mode = (pmax - pmin) * mode_fraction + pmin
    return random.triangular(lowest, pmax, mode)


# chooses and stores parameter values for one block into a single snapshot
#
def mutate_parameter_values_for_one_block(preset_dict, snapshot_name, dsp, slot, fraction_new):
    # snapshot_name = "snapshot" + str(snapshot_num)
    controllers_block_dict = preset_dict["data"]["tone"]["controller"][dsp][slot]
    #    model_name = preset_dict["data"]["tone"][dsp][slot]["@model"]

    # print("looking for " + model_name)
    # ###################

    # with open("debug.hlx", "w") as json_file:
    #     json.dump(preset_dict, json_file, indent=4)

    #     ################

    unpruned_block_ranges = file.reload_unpruned_block_dictionary(preset_dict, dsp, slot)["Ranges"]

    # print("mutating", dsp, slot, model_name)
    for parameter in unpruned_block_ranges:
        if not parameter.startswith("@"):
            pmin = unpruned_block_ranges[parameter]["@min"]
            pmax = unpruned_block_ranges[parameter]["@max"]
            result = get_mutated_parameter_value(preset_dict, dsp, slot, parameter, pmin, pmax)

        if parameter in controllers_block_dict:
            # print("  about to mutate " + parameter)
            prev_result = preset_dict["data"]["tone"][snapshot_name]["controllers"][dsp][slot][parameter]["@value"]
            result_mix = mix_values(fraction_new, pmin, pmax, result, prev_result)
            preset_dict["data"]["tone"][snapshot_name]["controllers"][dsp][slot][parameter]["@value"] = result_mix


def mutate_default_block(preset_dict, dsp_name, slot_name, fraction_new):
    defaults_block = preset_dict["data"]["tone"][dsp_name][slot_name]
    unpruned_block_ranges = file.reload_unpruned_block_dictionary(preset_dict, dsp_name, slot_name)["Ranges"]
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


def mutate_parameter_values_for_all_snapshots(preset):
    for n in range(constants.NUM_SNAPSHOTS):
        # snapshot_name = "snapshot" + str(n)
        for dsp in ["dsp0", "dsp1"]:
            for slot in preset["data"]["tone"][snapshot_name(n)]["controllers"][dsp]:
                mutate_parameter_values_for_one_block(preset, snapshot_name(n), dsp, slot, 1.0)


def mutate_parameter_value(mean, p_min, p_max):
    p_range = p_max - p_min
    sigma = p_range / 4
    p = random.normalvariate(mean, sigma)
    while not p_min <= p <= p_max:
        p = random.normalvariate(mean, sigma)
    return p


def swap_some_control_destinations(preset_dict, control_num, max_changes):
    num_changes = random.randint(0, max_changes)
    choose.random_remove_controls(preset_dict, control_num, num_changes)
    for _ in range(num_changes):
        # set another param to pedalnum
        choose.random_controlled_parameter_and_ranges(preset_dict, control_num)


def toggle_some_block_states(preset_dict, change_fraction):
    for snapshot_num in range(constants.NUM_SNAPSHOTS):
        snapshot_name = f"snapshot{snapshot_num}"
        snapshot_blocks = preset_dict["data"]["tone"][snapshot_name]["blocks"]
        for dsp_name in ["dsp0", "dsp1"]:
            if dsp_name in snapshot_blocks:
                for block_name in snapshot_blocks[dsp_name]:
                    if block_name.startswith("block") and random.uniform(0, 1) < change_fraction:
                        current_state = snapshot_blocks[dsp_name][block_name]
                        new_state = not current_state
                        snapshot_blocks[dsp_name][block_name] = new_state


def toggle_series_or_parallel_dsps(preset_dict, change_fraction):
    if random.uniform(0, 1) < change_fraction:  # change state
        print("toggling series or parallel dsps")
        current = preset_dict["data"]["tone"]["dsp0"]["outputA"]["@output"]
        if current == 1:
            preset_dict["data"]["tone"]["dsp0"]["outputA"]["@output"] = 2
        else:
            preset_dict["data"]["tone"]["dsp0"]["outputA"]["@output"] = 1


def duplicate_snapshot(preset_dict, snapshot_src, snapshot_dst):
    preset_dict["data"]["tone"][snapshot_dst] = deepcopy(preset_dict["data"]["tone"][snapshot_src])
    preset_dict["data"]["tone"][snapshot_dst]["@name"] = snapshot_dst


def duplicate_snapshot_to_all(preset_dict, snapshot_src):
    for snapshot_num in range(constants.NUM_SNAPSHOTS):
        snapshot_dst = "snapshot" + str(snapshot_num)
        if snapshot_dst != snapshot_src:
            duplicate_snapshot(preset_dict, snapshot_src, snapshot_dst)


def find_unused_slot_in_dsp(preset, dsp, slot_type):
    for i in range(constants.NUM_SLOTS_PER_DSP):
        slot = slot_type + str(i)
        if slot not in preset["data"]["tone"][dsp]:
            break
    return slot


def rearrange_block_positions(preset, fraction_move):
    cabs_from_dsp_amp_slot_to_dsp = []

    # find block positions
    found_dsp_path_pos = []
    for dsp in ["dsp0", "dsp1"]:
        for pos in preset["data"]["tone"][dsp]:
            if pos.startswith("block"):
                block_dict = preset["data"]["tone"][dsp][pos]
                found_dsp_path_pos.append([dsp, block_dict["@path"], block_dict["@position"]])

    # print(found_dsp_path_pos)

    # find vacant positions

    vacant_dsp_path_pos = []
    for dsp in ["dsp0", "dsp1"]:
        for path in (0, 1):
            for pos in range(constants.LAST_SLOT_POSITION):  # positions per path
                if [dsp, path, pos] not in found_dsp_path_pos:
                    vacant_dsp_path_pos.append([dsp, path, pos])

    # print(vacant_dsp_path_pos)

    from_dsp_slot_to_dsp_path_pos = []
    for dsp in ["dsp0", "dsp1"]:
        for slot in preset["data"]["tone"][dsp]:
            if slot.startswith("block"):
                chance = random.uniform(0, 1)
                if chance < fraction_move:
                    from_path = preset["data"]["tone"][dsp][slot]["@path"]
                    from_pos = preset["data"]["tone"][dsp][slot]["@position"]

                    random.shuffle(vacant_dsp_path_pos)
                    new_dsp_path_pos = vacant_dsp_path_pos.pop()
                    vacant_dsp_path_pos.append([dsp, from_path, from_pos])

                    from_dsp_slot_to_dsp_path_pos.append([dsp, slot, new_dsp_path_pos])
                    # check if it's an Amp, if so, move its Cab with it... must call before the amp block is moved
                    if preset["data"]["tone"][dsp][slot]["@model"].startswith("HD2_Amp"):

                        to_dsp = new_dsp_path_pos[0]
                        if dsp != to_dsp:
                            cabs_from_dsp_amp_slot_to_dsp.append([dsp, slot, to_dsp])

    move_cabs(preset, cabs_from_dsp_amp_slot_to_dsp)
    # print(from_dsp_slot_to_dsp_path_pos)
    move_blocks(preset, from_dsp_slot_to_dsp_path_pos)


# must call before the amp block is moved
def move_cabs(preset, cabs_from_dsp_amp_slot_to_dsp):
    for item in cabs_from_dsp_amp_slot_to_dsp:
        from_dsp = item[0]
        amp_slot = item[1]
        to_dsp = item[2]
        from_slot = preset["data"]["tone"][from_dsp][amp_slot]["@cab"]
        to_slot = find_unused_slot_in_dsp(preset, to_dsp, "cab")
        move_slot(preset, from_dsp, from_slot, to_dsp, to_slot, "cab")
        # register cab with amp
        preset["data"]["tone"][from_dsp][amp_slot]["@cab"] = to_slot


def move_blocks(preset, from_dsp_slot_to_dsp_path_pos):
    for item in from_dsp_slot_to_dsp_path_pos:
        from_dsp = item[0]
        from_slot = item[1]
        from_path = preset["data"]["tone"][from_dsp][from_slot]["@path"]
        from_position = preset["data"]["tone"][from_dsp][from_slot]["@position"]
        to_dsp = item[2][0]
        to_path = item[2][1]
        to_pos = item[2][2]
        to_slot = find_unused_slot_in_dsp(preset, to_dsp, "block")

        move_slot(preset, from_dsp, from_slot, to_dsp, to_slot, "block")
        preset["data"]["tone"][to_dsp][to_slot]["@path"] = to_path
        preset["data"]["tone"][to_dsp][to_slot]["@position"] = to_pos

        print(
            "Moved",
            from_dsp,
            from_slot,
            from_path,
            from_position,
            "to",
            to_dsp,
            to_slot,
            to_path,
            to_pos,
        )


def move_slot(preset, from_dsp, from_slot, to_dsp, to_slot, slot_type):
    move_default_slot(preset, from_dsp, from_slot, to_dsp, to_slot)
    move_controller_slot(preset, from_dsp, from_slot, to_dsp, to_slot)
    move_snapshot_slot(preset, from_dsp, from_slot, to_dsp, to_slot, slot_type)


def move_default_slot(preset, from_dsp, from_slot, to_dsp, to_slot):
    preset["data"]["tone"][to_dsp][to_slot] = {}
    preset["data"]["tone"][to_dsp][to_slot] = preset["data"]["tone"][from_dsp].pop(from_slot)


def move_controller_slot(preset, from_dsp, from_slot, to_dsp, to_slot):
    preset["data"]["tone"]["controller"][to_dsp][to_slot] = {}
    preset["data"]["tone"]["controller"][to_dsp][to_slot] = preset["data"]["tone"]["controller"][from_dsp].pop(
        from_slot
    )


def move_snapshot_slot(preset, from_dsp, from_slot, to_dsp, to_slot, slot_type):
    for snapshot_num in range(constants.NUM_SNAPSHOTS):
        snapshot_name = "snapshot" + str(snapshot_num)
        # move bypass state name (not for cabs)
        if slot_type == "block":
            preset["data"]["tone"][snapshot_name]["blocks"][to_dsp][to_slot] = {}
            preset["data"]["tone"][snapshot_name]["blocks"][to_dsp][to_slot] = preset["data"]["tone"][snapshot_name][
                "blocks"
            ][from_dsp].pop(from_slot)
        # move snapshot controller block
        preset["data"]["tone"][snapshot_name]["controllers"][to_dsp][to_slot] = {}
        preset["data"]["tone"][snapshot_name]["controllers"][to_dsp][to_slot] = preset["data"]["tone"][snapshot_name][
            "controllers"
        ][from_dsp].pop(from_slot)


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
    print("Swapping block from file")
    path = preset_dict["data"]["tone"][dsp_name][block_name]["@path"]
    pos = preset_dict["data"]["tone"][dsp_name][block_name]["@position"]
    new_block_dict = file.load_block_dictionary(choose.random_block_file_excluding_cab_or_split())
    preset_dict["data"]["tone"][dsp_name][block_name] = new_block_dict["Defaults"]
    preset_dict["data"]["tone"][dsp_name][block_name]["@path"] = path
    preset_dict["data"]["tone"][dsp_name][block_name]["@position"] = pos
    utils.add_block_to_snapshots(preset_dict, dsp_name, block_name, new_block_dict)
    preset_dict["data"]["tone"]["controller"][dsp_name][block_name] = new_block_dict["Ranges"]
    for snapshot_num in range(constants.NUM_SNAPSHOTS):
        mutate_parameter_values_for_one_block(preset_dict, snapshot_num, dsp_name, block_name, 1.0)


def swap_split_from_file(preset, dsp, slot):
    print("swapping split from file")
    keep_position = preset["data"]["tone"][dsp][slot]["@position"]
    split_dict = file.load_block_dictionary(choose.random_block_file_in_category("Split"))
    utils.add_block_to_preset(preset, dsp, slot, split_dict)
    preset["data"]["tone"][dsp][slot]["@position"] = keep_position
    for snapshot_num in range(constants.NUM_SNAPSHOTS):
        mutate_parameter_values_for_one_block(preset, snapshot_num, dsp, slot, 1.0)


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
        block_dict = file.reload_unpruned_block_dictionary(preset_dict, dsp_name, block_or_split_name)
        pmin = block_dict["Ranges"][param_name]["@min"]
        pmax = block_dict["Ranges"][param_name]["@max"]
        # print(pedalParam["@min"], pmin, pmax)
        new_min = mutate_parameter_value(param["@min"], pmin, pmax)  # (mean, pmin, pmax)
        new_max = mutate_parameter_value(param["@max"], pmin, pmax)
        param["@min"] = new_min
        param["@max"] = new_max


def snapshot_name(snapshot_num):
    return "snapshot" + str(snapshot_num)


def mutate_dictionary(preset, snapshot_src_num, postfix_num):
    increment_preset_name(preset, postfix_num)
    duplicate_snapshot_to_all(preset, snapshot_name(snapshot_src_num))
    choose.random_new_params_for_snapshot_control(preset)
    mutate_parameter_values_for_all_snapshots(preset)
    mutate_all_default_blocks(preset, constants.MUTATION_RATE)
    swap_some_control_destinations(preset, constants.PEDAL_2, 10)
    mutate_all_pedal_ranges(preset)
    rearrange_block_positions(preset, constants.FRACTION_MOVE)
    swap_some_blocks_and_splits_from_file(preset, 0.1)
    toggle_some_block_states(preset, constants.MUTATION_RATE)
    toggle_series_or_parallel_dsps(preset, constants.TOGGLE_RATE)
    set_led_colours(preset)


def mutate_preset_from_source_snapshot(template_file, snapshot_src_num, output_file, postfix_num):
    with open(template_file, "r") as f:
        preset_dict = json.load(f)
        mutate_dictionary(preset_dict, snapshot_src_num, postfix_num)
        with open(output_file, "w") as f:
            json.dump(preset_dict, f, indent=4)


# def mutations(num):
#     for i in range(num):
#         mutate_preset_from_source_snapshot(
#             "presets/test/aGenerated1.hlx",
#             6,
#             "presets/test/aGenerated1+" + str(i + 1) + ".hlx",
#             (i + 1),
#         )


def generate_multiple_mutations_from_template(args):
    # preset_name_base = args.get("preset_name_base")
    for i in range(args.get("num_presets")):
        # preset_name = preset_name_base + chr(ord("a") + (i % 26))
        mutate_preset_from_source_snapshot(
            args.get("template_file"),
            args.get("snapshot_src_num"),
            args.get("output_file")[:-4] + str(i + 1) + ".hlx",
            args.get("postfix_num"),
        )
