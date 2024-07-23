import argparse
import json
import random
import constants
from debug import save_debug_hlx
import file
import util
import choose


def is_block_or_cab_slot(slot):
    return slot.startswith("block") or slot.startswith("cab")


def is_specific_model_type(preset, dsp, slot):
    return util.get_default_dsp_slot(preset, dsp, slot)["@model"].startswith(("HD2_Reverb", "VIC", "Victoria"))


def is_reverb(preset, dsp, slot):
    return util.get_default_dsp_slot(preset, dsp, slot)["@model"].startswith(("HD2_Reverb", "VIC", "Victoria"))


def random_triangle(pmax, pmin, mode_fraction, lowest_fraction):
    lowest = ((pmax - pmin) * lowest_fraction) + pmin
    mode = (pmax - pmin) * mode_fraction + pmin
    return random.triangular(lowest, pmax, mode)


special_parameter_mutations_cache = {}  # Global cache


def get_mutated_parameter_value(preset, dsp, slot, parameter, pmin, pmax):
    global special_parameter_mutations_cache

    # Check if special_parameter_mutations is cached
    if "special_parameter_mutations" not in special_parameter_mutations_cache:
        special_parameter_mutations_cache["special_parameter_mutations"] = {
            "Level": lambda: (
                random_triangle(pmax, pmin, 0.8, 0.0) if is_block_or_cab_slot(slot) else random.uniform(pmin, pmax)
            ),
            "Decay": lambda: (
                random_triangle(pmax, pmin, 0.05, 0.0) if is_reverb(preset, dsp, slot) else random.uniform(pmin, pmax)
            ),
            "Time": lambda: min(pmax, random.expovariate(0.95 + (0.75 - 0.95) * (pmax - 2) / (8 - 2))),
            "Mix": lambda: random_triangle(pmax, pmin, 0.5, 0.0),
            "Feedback": lambda: random_triangle(pmax, pmin, 0.5, 0.0),
        }

    special_parameter_mutations = special_parameter_mutations_cache["special_parameter_mutations"]

    if isinstance(pmin, bool):
        return random.choice([True, False])
    else:
        return special_parameter_mutations.get(parameter, lambda: random.uniform(pmin, pmax))()


# chooses and stores parameter values for one block into a single snapshot
#
def mutate_parameter_values_for_one_snapshot_slot(preset, snapshot_num, dsp, slot, fraction_new):
    raw_controllers = file.reload_raw_block_dictionary(preset, dsp, slot)["Controller_Dict"]
    # print("mutating", dsp, slot, utils.get_default_slot(preset, dsp, slot)["@model"])
    for parameter in util.get_controller_dsp_slot(preset, dsp, slot):
        pmin = raw_controllers[parameter]["@min"]
        pmax = raw_controllers[parameter]["@max"]
        result = get_mutated_parameter_value(preset, dsp, slot, parameter, pmin, pmax)
        prev_result = util.get_snapshot_controllers_dsp_slot_parameter_value(
            preset, snapshot_num, dsp, slot, parameter
        )
        result_mix = mix_values(fraction_new, pmin, pmax, result, prev_result)
        util.get_snapshot_controllers_dsp_slot_parameter(preset, snapshot_num, dsp, slot, parameter)[
            "@value"
        ] = result_mix


def mutate_default_block(preset, dsp, slot, fraction_new):
    raw_controllers = file.reload_raw_block_dictionary(preset, dsp, slot)["Controller_Dict"]
    print("  mutate_default_block", dsp, slot, util.get_model_name(preset, dsp, slot))
    for parameter in raw_controllers:  # not all default params can be changed on the helix
        pmin = raw_controllers[parameter]["@min"]
        pmax = raw_controllers[parameter]["@max"]
        result = get_mutated_parameter_value(preset, dsp, slot, parameter, pmin, pmax)
        prev_result = util.get_default_dsp_slot_parameter_value(preset, dsp, slot, parameter)
        util.get_default_dsp_slot(preset, dsp, slot)[parameter] = mix_values(
            fraction_new, pmin, pmax, result, prev_result
        )


# def mix_result(fraction_new, defaults_block, parameter, pmin, pmax, result):
#     prev_result = defaults_block[parameter]
#     fraction_prev = 1.0 - fraction_new
#     result_mix = result * fraction_new + prev_result * fraction_prev
#     return max(pmin, min(result_mix, pmax))


def mix_values(fraction_new, pmin, pmax, result, prev_result):
    if isinstance(result, bool):
        return result
    fraction_prev = 1.0 - fraction_new
    result_mix = result * fraction_new + prev_result * fraction_prev
    return max(pmin, min(result_mix, pmax))


def mutate_all_default_blocks(preset, fraction_new):
    for dsp in util.get_available_default_dsps(preset):
        for slot in util.get_default_dsp(preset, dsp):
            if slot.startswith(("cab", "split", "block")):
                mutate_default_block(preset, dsp, slot, fraction_new)


def mutate_parameter_values_for_all_snapshots(preset, fraction_new):
    print("Mutating parameter values for all snapshots")
    for snapshot_num in range(constants.NUM_SNAPSHOTS):
        for dsp in util.get_snapshot_controllers(preset, snapshot_num):
            for slot in util.get_snapshot_controllers_dsp(preset, snapshot_num, dsp):
                mutate_parameter_values_for_one_snapshot_slot(preset, snapshot_num, dsp, slot, fraction_new)


def mutate_parameter_value(mean, p_min, p_max):
    p_range = p_max - p_min
    sigma = p_range / 4
    p = random.normalvariate(mean, sigma)
    while not p_min <= p <= p_max:
        p = random.normalvariate(mean, sigma)
    return p


def swap_some_control_destinations(preset, control_num, max_changes):
    print("Swapping some control destinations")
    num_changes = random.randint(0, max_changes)
    choose.random_remove_controls(preset, control_num, num_changes)
    for _ in range(num_changes):
        choose.random_controlled_parameter_and_ranges(preset, control_num)


def toggle_block_state(preset, dsp, slot):
    current_state = util.get_default_dsp_slot_parameter_value(preset, dsp, slot, "@enabled")
    util.get_default_dsp_slot(preset, dsp, slot)["@enabled"] = not current_state


def toggle_some_block_states(preset, change_fraction):
    for dsp in util.get_available_default_dsps(preset):
        for slot in util.get_default_dsp(preset, dsp):
            if slot.startswith("block") and random.uniform(0, 1) < change_fraction:
                toggle_block_state(preset, dsp, slot)

    for snapshot_num in range(constants.NUM_SNAPSHOTS):
        snapshot_blocks = util.get_snapshot_blocks(preset, snapshot_num)
        for dsp in snapshot_blocks:
            for slot in snapshot_blocks[dsp]:
                if slot.startswith("block") and random.uniform(0, 1) < change_fraction:
                    current_state = snapshot_blocks[dsp][slot]
                    snapshot_blocks[dsp][slot] = not current_state


def toggle_series_or_parallel_dsps(preset, change_fraction):
    if random.uniform(0, 1) < change_fraction:  # change state
        print("toggling series or parallel dsps")
        current = preset["data"]["tone"]["dsp0"]["outputA"]["@output"]
        preset["data"]["tone"]["dsp0"]["outputA"]["@output"] = 2 if current == 1 else 1


def find_used_default_block_slots(preset):
    dsp_slot = []
    for dsp in util.get_available_default_dsps(preset):
        dsp_slot.extend([dsp, slot] for slot in util.get_default_dsp(preset, dsp) if slot.startswith("block"))
    return dsp_slot


def find_unused_default_block_slots(preset):
    dsp_slot = []
    for dsp in util.get_available_default_dsps(preset):
        for block_num in range(constants.NUM_SLOTS_PER_DSP):
            slot = f"block{block_num}"
            if slot not in util.get_default_dsp(preset, dsp):
                dsp_slot.append([dsp, slot])
    return list(reversed(dsp_slot))


def find_used_default_dsp_path_pos(preset):
    dsp_path_pos = {}
    for dsp in util.get_available_default_dsps(preset):
        dsp_path_pos[dsp] = []
        for slot in util.get_default_dsp(preset, dsp):
            if slot.startswith("block"):
                slot_dict = util.get_default_dsp_slot(preset, dsp, slot)
                dsp_path_pos[dsp].append((slot_dict["@path"], slot_dict["@position"]))
    return dsp_path_pos


def find_unused_dsp_path_positions(preset):
    used_dsp_path_positions = find_used_default_dsp_path_pos(preset)
    unused_dsp_path_positions = {}
    for dsp in util.get_available_default_dsps(preset):
        unused_dsp_path_positions[dsp] = []
        for path in range(constants.NUM_PATHS_PER_DSP):
            for pos in range(constants.NUM_POSITIONS_PER_PATH):
                if (path, pos) not in used_dsp_path_positions[dsp]:
                    unused_dsp_path_positions[dsp].append((path, pos))
    return unused_dsp_path_positions


def find_used_default_dsp_cab_slots(preset):
    used_dsp_cab_slots = {}
    for dsp in util.get_available_default_dsps(preset):
        used_dsp_cab_slots[dsp] = []
        for slot in util.get_default_dsp(preset, dsp):
            if slot.startswith("cab"):
                used_dsp_cab_slots[dsp].append(slot)
    return used_dsp_cab_slots


def find_unused_default_dsp_cab_slots(preset):
    used_dsp_cab_slots = find_used_default_dsp_cab_slots(preset)
    unused_dsp_cab_slots = {}
    for dsp in util.get_available_default_dsps(preset):
        unused_dsp_cab_slots[dsp] = []
        for cab_num in range(constants.NUM_SLOTS_PER_DSP):
            slot = f"cab{cab_num}"
            if slot not in used_dsp_cab_slots[dsp]:
                unused_dsp_cab_slots[dsp].append(slot)
        unused_dsp_cab_slots[dsp] = list(reversed(unused_dsp_cab_slots[dsp]))
    return unused_dsp_cab_slots


def rearrange_blocks(preset, fraction_move):
    print("Rearranging blocks")
    used_block_slots = find_used_default_block_slots(preset)
    unused_block_slots = find_unused_default_block_slots(preset)
    used_dsp_path_positions = find_used_default_dsp_path_pos(preset)
    unused_dsp_path_positions = find_unused_dsp_path_positions(preset)
    used_dsp_cab_slots = find_used_default_dsp_cab_slots(preset)
    unused_dsp_cab_slots = find_unused_default_dsp_cab_slots(preset)
    # print(used_slots, unused_slots)
    for dsp, slot in used_block_slots:
        if random.uniform(0, 1) < fraction_move:
            model_name = util.get_model_name(preset, dsp, slot)
            # update slot arrays
            to_dsp, to_slot = unused_block_slots.pop()
            unused_block_slots.append([dsp, slot])
            # get new unused path and position on to_dsp
            from_path = util.get_default_dsp_slot(preset, dsp, slot)["@path"]
            from_pos = util.get_default_dsp_slot(preset, dsp, slot)["@position"]
            used_dsp_path_positions[dsp].remove((from_path, from_pos))

            random.shuffle(unused_dsp_path_positions[to_dsp])
            to_path, to_pos = unused_dsp_path_positions[to_dsp].pop()
            used_dsp_path_positions[to_dsp].append((to_path, to_pos))

            # actually move the block
            util.move_slot(preset, dsp, slot, to_dsp, to_slot, "block")

            # set new path, position
            util.get_default_dsp_slot(preset, to_dsp, to_slot)["@path"] = to_path
            util.get_default_dsp_slot(preset, to_dsp, to_slot)["@position"] = to_pos

            print("  moved", model_name, "from", dsp, slot, "to", to_dsp, to_slot)
            # if it's an amp, find an unused cab slot on to_dsp, and move it there
            if model_name.startswith("HD2_Amp"):
                rearrange_cab(preset, used_dsp_cab_slots, unused_dsp_cab_slots, dsp, to_dsp, to_slot)


def rearrange_cab(preset, used_dsp_cab_slots, unused_dsp_cab_slots, dsp, amp_dsp, amp_slot):
    if dsp != amp_dsp:
        old_cab_slot = util.get_default_dsp_slot(preset, amp_dsp, amp_slot)["@cab"]
        # print("rearrange_cab old_cab_slot", dsp, old_cab_slot)
        # Move cab_from_slot from used to unused list
        used_dsp_cab_slots[dsp].remove(old_cab_slot)
        unused_dsp_cab_slots[dsp].append(old_cab_slot)

        new_cab_slot = unused_dsp_cab_slots[amp_dsp].pop()
        used_dsp_cab_slots[amp_dsp].append(new_cab_slot)

        util.move_slot(preset, dsp, old_cab_slot, amp_dsp, new_cab_slot, "cab")
        # register the cab with its amp
        util.get_default_dsp_slot(preset, amp_dsp, amp_slot)["@cab"] = new_cab_slot
        print("  moved cab from", dsp, old_cab_slot, "to", amp_dsp, new_cab_slot)


def swap_some_blocks_and_splits_from_file(preset, change_fraction):
    print("Swapping some blocks and splits from file")
    for dsp in util.get_available_default_dsps(preset):
        for slot in util.get_default_dsp(preset, dsp):
            if slot.startswith("block") and random.uniform(0, 1) < change_fraction:
                swap_with_random_block_from_file(preset, dsp, slot)
            if slot.startswith("split") and random.uniform(0, 1) < change_fraction:
                swap_with_random_split_from_file(preset, dsp, slot)


def swap_with_random_block_from_file(preset, dsp, slot):
    print("Swapping block from file")
    path = util.get_default_dsp_slot(preset, dsp, slot)["@path"]
    pos = util.get_default_dsp_slot(preset, dsp, slot)["@position"]
    raw_block_dict = file.load_block_dictionary(choose.random_block_file_excluding_cab_or_split())
    util.add_raw_block_to_preset(preset, dsp, slot, raw_block_dict)
    util.get_default_dsp_slot(preset, dsp, slot)["@path"] = path
    util.get_default_dsp_slot(preset, dsp, slot)["@position"] = pos
    for snapshot_num in range(constants.NUM_SNAPSHOTS):
        mutate_parameter_values_for_one_snapshot_slot(preset, snapshot_num, dsp, slot, 1.0)


def swap_with_random_split_from_file(preset, dsp, slot):
    print("swapping split from file")
    keep_position = util.get_default_dsp_slot(preset, dsp, slot)["@position"]
    split_dict = file.load_block_dictionary(choose.random_block_file_in_category("Split"))
    util.add_raw_block_to_preset(preset, dsp, slot, split_dict)
    util.get_default_dsp_slot(preset, dsp, slot)["@position"] = keep_position
    mutate_parameter_values_for_all_snapshots(preset, 1.0)


def increment_preset_name(preset, preset_name, postfix_num):
    name = preset["data"]["meta"]["name"] if preset_name == "" else preset_name
    postfix_num_str = str(postfix_num).zfill(3)
    name = f"{name}-{postfix_num_str}"
    preset["data"]["meta"]["name"] = name
    print(f"Preset name: {name}")


def mutate_all_pedal_ranges(preset):
    for dsp in util.get_controller(preset):
        for slot in util.get_controller_dsp(preset, dsp):
            block = util.get_controller_dsp(preset, dsp)[slot]
            if any(block[param]["@controller"] == 2 for param in block):
                for parameter in block:
                    if block[parameter]["@controller"] == 2:
                        mutate_one_set_of_pedal_ranges(preset, dsp, slot, parameter)
                break


def set_dsp1_input_to_multi(preset):
    preset["data"]["tone"]["dsp1"]["inputA"]["@input"] = 1


def mutate_one_set_of_pedal_ranges(preset, dsp, slot, parameter):
    param = util.get_controller_dsp(preset, dsp)[slot][parameter]
    if not isinstance(param["@min"], bool):  # don't want to pedal bools
        # get original ranges from file
        raw_block_dict = file.reload_raw_block_dictionary(preset, dsp, slot)
        pmin = raw_block_dict["Controller_Dict"][parameter]["@min"]
        pmax = raw_block_dict["Controller_Dict"][parameter]["@max"]
        # print(pedalParam["@min"], pmin, pmax)
        if param["@min"] == pmin and param["@max"] == pmax:
            new_max = random.uniform(param["@min"], param["@max"])
            new_min = random.uniform(param["@min"], param["@max"])
        else:
            new_min = mutate_parameter_value(param["@min"], pmin, pmax)  # (mean, pmin, pmax)
            new_max = mutate_parameter_value(param["@max"], pmin, pmax)
        param["@min"] = new_min
        param["@max"] = new_max


def snapshot(snapshot_num):
    return f"snapshot{snapshot_num}"


def mutate_dictionary(preset, snapshot_src_num_str, preset_name, postfix_num, args_from_gui):
    increment_preset_name(preset, preset_name, postfix_num)
    set_dsp1_input_to_multi(preset)
    util.set_topologies_to_SABJ(preset)
    util.add_dsp_controller_and_snapshot_keys_if_missing(preset)
    util.add_splits(preset)
    util.populate_all_controller_slots_from_raw_file(preset)
    if snapshot_src_num_str.isdigit():
        snapshot_src_num = int(snapshot_src_num_str) - 1  # 0-indexed
        if 0 <= snapshot_src_num <= 7:
            print(f"Mutating from Source Snapshot {snapshot_src_num_str}")  # str is not 0-indexed
            util.copy_snapshot_values_to_default(preset, snapshot_src_num)  # 0-indexed
    else:
        print("Mutating Default to produce 8 Snapshots")
    util.populate_all_snapshots_with_controllers_from_file(preset)
    util.copy_all_default_values_to_all_snapshots(preset)

    if args_from_gui.get("change_topology") == "true":
        swap_some_blocks_and_splits_from_file(preset, constants.MUTATION_RATE)
        choose.prune_controllers(preset)
        rearrange_blocks(preset, constants.FRACTION_MOVE)
        choose.move_splits_and_joins(preset)
        toggle_series_or_parallel_dsps(preset, constants.TOGGLE_RATE)

    if args_from_gui.get("change_controllers") == "true":
        choose.random_new_params_for_snapshot_control(preset)

    mutate_parameter_values_for_all_snapshots(preset, constants.MUTATION_RATE)
    mutate_all_default_blocks(preset, constants.MUTATION_RATE)
    swap_some_control_destinations(preset, constants.PEDAL_2, 10)
    mutate_all_pedal_ranges(preset)

    toggle_some_block_states(preset, constants.MUTATION_RATE)

    util.set_led_colours(preset)
    print()


def mutate_preset_from_source_snapshot(
    template_file, snapshot_src_num_str, output_file, preset_name, postfix_num, args_from_gui
):
    with open(template_file, "r") as f:
        preset = json.load(f)
        mutate_dictionary(preset, snapshot_src_num_str, preset_name, postfix_num, args_from_gui)
        with open(output_file, "w") as f:
            json.dump(preset, f, indent=4)


def generate_multiple_mutations_from_template(args_from_gui):
    if args_from_gui.get("snapshot_src_num") == "":
        snapshot_src_num_str = "default"
    else:
        snapshot_src_num_str = args_from_gui.get("snapshot_src_num")  # not 0 indexed
    for i in range(args_from_gui.get("num_presets")):
        mutate_preset_from_source_snapshot(
            args_from_gui.get("template_file"),
            snapshot_src_num_str,  # not 0 indexed
            args_from_gui.get("output_file")[:-4] + str(i + 1) + ".hlx",
            args_from_gui.get("preset_name"),
            i,
            args_from_gui,
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("args_json", type=str, help="JSON string containing arguments")
    args = parser.parse_args()

    args_dict = json.loads(args.args_json)
    generate_multiple_mutations_from_template(args_dict)
