import argparse
from copy import deepcopy
import json
import random

import constants
import file
import utils
import choose


def get_mutated_parameter_value(preset, dsp, slot, parameter, pmin, pmax):
    defaults_block = utils.get_default_slot(preset, dsp, slot)
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


def random_triangle(pmax, pmin, mode_fraction, lowest_fraction):
    lowest = ((pmax - pmin) * lowest_fraction) + pmin
    mode = (pmax - pmin) * mode_fraction + pmin
    return random.triangular(lowest, pmax, mode)


# chooses and stores parameter values for one block into a single snapshot
#
def mutate_parameter_values_for_one_snapshot_slot(preset, snapshot_num, dsp, slot, fraction_new):
    unpruned_block_ranges = file.reload_raw_block_dictionary(preset, dsp, slot)["Ranges"]
    # model_name = utils.get_default_slot(preset, dsp, slot)["@model"]
    # print("mutating", dsp, slot, model_name)
    for parameter in utils.get_controller_slot(preset, dsp, slot):
        # print("  about to mutate " + parameter)
        # print(get_snapshot_slot(preset, snapshot_num, dsp, slot))
        pmin = unpruned_block_ranges[parameter]["@min"]
        pmax = unpruned_block_ranges[parameter]["@max"]
        result = get_mutated_parameter_value(preset, dsp, slot, parameter, pmin, pmax)

        # file.save_debug_hlx(preset)
        prev_result = utils.get_snapshot_slot(preset, snapshot_num, dsp, slot)[parameter]["@value"]
        result_mix = mix_values(fraction_new, pmin, pmax, result, prev_result)
        utils.get_snapshot_slot(preset, snapshot_num, dsp, slot)[parameter]["@value"] = result_mix


def mutate_default_block(preset, dsp, slot, fraction_new):
    defaults_block = utils.get_default_slot(preset, dsp, slot)
    unpruned_block_ranges = file.reload_raw_block_dictionary(preset, dsp, slot)["Ranges"]
    print("mutate_default_block", dsp, slot, utils.get_model_name(preset, dsp, slot))
    # print(defaults_block)
    for parameter in unpruned_block_ranges:  # not all default params can be changed on the helix
        pmin = unpruned_block_ranges[parameter]["@min"]
        pmax = unpruned_block_ranges[parameter]["@max"]
        result = get_mutated_parameter_value(preset, dsp, slot, parameter, pmin, pmax)
        if isinstance(result, bool):
            defaults_block[parameter] = result
        else:
            # random nudge default param
            prev_result = defaults_block[parameter]
            fraction_prev = 1.0 - fraction_new
            result_mix = result * fraction_new + prev_result * fraction_prev
            result_mix_constrained = max(pmin, min(result_mix, pmax))
            defaults_block[parameter] = result_mix_constrained


def mutate_all_default_blocks(preset, fraction_new):
    for dsp in ["dsp0", "dsp1"]:
        for slot in preset["data"]["tone"][dsp]:
            if slot.startswith(("cab", "split", "block")):
                mutate_default_block(preset, dsp, slot, fraction_new)


def mix_values(fraction_new, pmin, pmax, result, prev_result):
    if isinstance(result, bool):
        return result
    fraction_prev = 1.0 - fraction_new
    result_mix = result * fraction_new + prev_result * fraction_prev
    result_mix_constrained = max(pmin, min(result_mix, pmax))
    return result_mix_constrained
    # print(pmin, pmax, prev_result, result_mix_constrained)


def mutate_parameter_values_for_all_snapshots(preset, fraction_new):
    print("mutate_parameter_values_for_all_snapshots")
    for snapshot_num in range(constants.NUM_SNAPSHOTS):
        for dsp in ["dsp0", "dsp1"]:
            for slot in utils.get_snapshot(preset, snapshot_num, dsp):
                mutate_parameter_values_for_one_snapshot_slot(preset, snapshot_num, dsp, slot, fraction_new)


def mutate_parameter_value(mean, p_min, p_max):
    p_range = p_max - p_min
    sigma = p_range / 4
    p = random.normalvariate(mean, sigma)
    while not p_min <= p <= p_max:
        p = random.normalvariate(mean, sigma)
    return p


def swap_some_control_destinations(preset, control_num, max_changes):
    num_changes = random.randint(0, max_changes)
    choose.random_remove_controls(preset, control_num, num_changes)
    for _ in range(num_changes):
        choose.random_controlled_parameter_and_ranges(preset, control_num)


def toggle_some_block_states(preset, change_fraction):
    for snapshot_num in range(constants.NUM_SNAPSHOTS):
        snapshot_name = f"snapshot{snapshot_num}"
        snapshot_blocks = preset["data"]["tone"][snapshot_name]["blocks"]
        for dsp in ["dsp0", "dsp1"]:
            if dsp in snapshot_blocks:
                for slot in snapshot_blocks[dsp]:
                    if slot.startswith("block") and random.uniform(0, 1) < change_fraction:
                        current_state = snapshot_blocks[dsp][slot]
                        new_state = not current_state
                        snapshot_blocks[dsp][slot] = new_state


def toggle_series_or_parallel_dsps(preset, change_fraction):
    if random.uniform(0, 1) < change_fraction:  # change state
        print("toggling series or parallel dsps")
        current = preset["data"]["tone"]["dsp0"]["outputA"]["@output"]
        preset["data"]["tone"]["dsp0"]["outputA"]["@output"] = 2 if current == 1 else 1


def duplicate_snapshot(preset, snapshot_src, snapshot_dst):
    preset["data"]["tone"][snapshot_dst] = deepcopy(preset["data"]["tone"][snapshot_src])
    preset["data"]["tone"][snapshot_dst]["@name"] = snapshot_dst


def duplicate_snapshot_to_all(preset, snapshot_src):
    for snapshot_num in range(constants.NUM_SNAPSHOTS):
        snapshot_dst = f"snapshot{snapshot_num}"
        if snapshot_dst != snapshot_src:
            duplicate_snapshot(preset, snapshot_src, snapshot_dst)


def find_used_block_slots(preset):
    dsp_slot = []
    for dsp in ["dsp0", "dsp1"]:
        dsp_slot.extend([dsp, slot] for slot in preset["data"]["tone"][dsp] if slot.startswith("block"))
    return dsp_slot


def find_unused_block_slots(preset):
    dsp_slot = []
    for dsp in ["dsp0", "dsp1"]:
        for block_num in range(constants.NUM_SLOTS_PER_DSP):
            slot = f"block{block_num}"
            if slot not in preset["data"]["tone"][dsp]:
                dsp_slot.append([dsp, slot])
    return list(reversed(dsp_slot))


def find_used_dsp_path_pos(preset):
    dsp_path_pos = {}
    for dsp in ["dsp0", "dsp1"]:
        dsp_path_pos[dsp] = []
        for slot in preset["data"]["tone"][dsp]:
            if slot.startswith("block"):
                slot_dict = utils.get_default_slot(preset, dsp, slot)
                dsp_path_pos[dsp].append((slot_dict["@path"], slot_dict["@position"]))
    return dsp_path_pos


def find_unused_dsp_path_positions(preset):
    used_dsp_path_positions = find_used_dsp_path_pos(preset)
    unused_dsp_path_positions = {}
    for dsp in ["dsp0", "dsp1"]:
        unused_dsp_path_positions[dsp] = []
        for path in range(constants.NUM_PATHS_PER_DSP):
            for pos in range(constants.NUM_POSITIONS_PER_PATH):
                if (path, pos) not in used_dsp_path_positions[dsp]:
                    unused_dsp_path_positions[dsp].append((path, pos))
    return unused_dsp_path_positions


def find_used_dsp_cab_slots(preset):
    used_dsp_cab_slots = {}
    for dsp in ["dsp0", "dsp1"]:
        used_dsp_cab_slots[dsp] = []
        for slot in preset["data"]["tone"][dsp]:
            if slot.startswith("cab"):
                used_dsp_cab_slots[dsp].append(slot)
    return used_dsp_cab_slots


def find_unused_dsp_cab_slots(preset):
    used_dsp_cab_slots = find_used_dsp_cab_slots(preset)
    unused_dsp_cab_slots = {}
    for dsp in ["dsp0", "dsp1"]:
        unused_dsp_cab_slots[dsp] = []
        for cab_num in range(constants.NUM_SLOTS_PER_DSP):
            slot = f"cab{cab_num}"
            if slot not in used_dsp_cab_slots[dsp]:
                unused_dsp_cab_slots[dsp].append(slot)
        unused_dsp_cab_slots[dsp] = list(reversed(unused_dsp_cab_slots[dsp]))
    return unused_dsp_cab_slots


def rearrange_blocks(preset, fraction_move):
    print("Rearranging blocks")
    used_block_slots = find_used_block_slots(preset)
    unused_block_slots = find_unused_block_slots(preset)
    used_dsp_path_positions = find_used_dsp_path_pos(preset)
    unused_dsp_path_positions = find_unused_dsp_path_positions(preset)
    used_dsp_cab_slots = find_used_dsp_cab_slots(preset)
    unused_dsp_cab_slots = find_unused_dsp_cab_slots(preset)
    # print(used_slots, unused_slots)
    for dsp, slot in used_block_slots:
        if random.uniform(0, 1) < fraction_move:
            model_name = utils.get_model_name(preset, dsp, slot)
            # update slot arrays
            to_dsp, to_slot = unused_block_slots.pop()
            unused_block_slots.append([dsp, slot])
            # get new unused path and position on to_dsp
            from_path = utils.get_default_slot(preset, dsp, slot)["@path"]
            from_pos = utils.get_default_slot(preset, dsp, slot)["@position"]
            used_dsp_path_positions[dsp].remove((from_path, from_pos))

            random.shuffle(unused_dsp_path_positions[to_dsp])
            to_path, to_pos = unused_dsp_path_positions[to_dsp].pop()
            used_dsp_path_positions[to_dsp].append((to_path, to_pos))

            # actually move the block
            utils.move_slot(preset, dsp, slot, to_dsp, to_slot, "block")

            # set new path, position
            utils.get_default_slot(preset, to_dsp, to_slot)["@path"] = to_path
            utils.get_default_slot(preset, to_dsp, to_slot)["@position"] = to_pos

            print("moved", model_name, "from", dsp, slot, "to", to_dsp, to_slot)
            # if it's an amp, find an unused cab slot on to_dsp, and move it there
            if model_name.startswith("HD2_Amp"):
                rearrange_cab(preset, used_dsp_cab_slots, unused_dsp_cab_slots, dsp, to_dsp, to_slot)


def rearrange_cab(preset, used_dsp_cab_slots, unused_dsp_cab_slots, dsp, amp_dsp, amp_slot):
    if dsp != amp_dsp:
        old_cab_slot = utils.get_default_slot(preset, amp_dsp, amp_slot)["@cab"]
        print("rearrange_cab old_cab_slot", dsp, old_cab_slot)
        # Move cab_from_slot from used to unused list
        used_dsp_cab_slots[dsp].remove(old_cab_slot)
        unused_dsp_cab_slots[dsp].append(old_cab_slot)

        new_cab_slot = unused_dsp_cab_slots[amp_dsp].pop()
        used_dsp_cab_slots[amp_dsp].append(new_cab_slot)

        utils.move_slot(preset, dsp, old_cab_slot, amp_dsp, new_cab_slot, "cab")
        # register the cab with its amp
        utils.get_default_slot(preset, amp_dsp, amp_slot)["@cab"] = new_cab_slot
        print("  moved cab from", dsp, old_cab_slot, "to", amp_dsp, new_cab_slot)


def swap_some_blocks_and_splits_from_file(preset, change_fraction):
    for dsp in ["dsp0", "dsp1"]:
        for slot in preset["data"]["tone"][dsp]:
            if slot.startswith("block") and random.uniform(0, 1) < change_fraction:
                swap_block_from_file(preset, dsp, slot)
            if slot.startswith("split") and random.uniform(0, 1) < change_fraction:
                swap_split_from_file(preset, dsp, slot)


def swap_block_from_file(preset, dsp, slot):
    print("Swapping block from file")
    path = utils.get_default_slot(preset, dsp, slot)["@path"]
    pos = utils.get_default_slot(preset, dsp, slot)["@position"]
    raw_block_dict = file.load_block_dictionary(choose.random_block_file_excluding_cab_or_split())
    utils.add_raw_block_to_preset(preset, dsp, slot, raw_block_dict)
    utils.get_default_slot(preset, dsp, slot)["@path"] = path
    utils.get_default_slot(preset, dsp, slot)["@position"] = pos
    for snapshot_num in range(constants.NUM_SNAPSHOTS):
        mutate_parameter_values_for_one_snapshot_slot(preset, snapshot_num, dsp, slot, 1.0)


def swap_split_from_file(preset, dsp, slot):
    print("swapping split from file")
    keep_position = utils.get_default_slot(preset, dsp, slot)["@position"]
    split_dict = file.load_block_dictionary(choose.random_block_file_in_category("Split"))
    utils.add_raw_block_to_preset(preset, dsp, slot, split_dict)
    utils.get_default_slot(preset, dsp, slot)["@position"] = keep_position
    mutate_parameter_values_for_all_snapshots(preset, 1.0)


def increment_preset_name(preset, postfix_num):
    name = preset["data"]["meta"]["name"]
    name = name + str(postfix_num)
    preset["data"]["meta"]["name"] = name
    print("Preset name: " + name)


def mutate_all_pedal_ranges(preset):
    for dsp in ["dsp0", "dsp1"]:
        for slot in utils.get_controller(preset, dsp):
            block = utils.get_controller(preset, dsp)[slot]
            if any(block[param]["@controller"] == 2 for param in block):
                for parameter in block:
                    if block[parameter]["@controller"] == 2:
                        mutate_one_set_of_pedal_ranges(preset, dsp, slot, parameter)
                break


def mutate_one_set_of_pedal_ranges(preset, dsp, slot, parameter):
    param = utils.get_controller(preset, dsp)[slot][parameter]
    if not isinstance(param["@min"], bool):  # don't want to pedal bools
        # get original ranges from file
        raw_block_dict = file.reload_raw_block_dictionary(preset, dsp, slot)
        pmin = raw_block_dict["Ranges"][parameter]["@min"]
        pmax = raw_block_dict["Ranges"][parameter]["@max"]
        # print(pedalParam["@min"], pmin, pmax)
        new_min = mutate_parameter_value(param["@min"], pmin, pmax)  # (mean, pmin, pmax)
        new_max = mutate_parameter_value(param["@max"], pmin, pmax)
        param["@min"] = new_min
        param["@max"] = new_max


def snapshot(snapshot_num):
    return f"snapshot{snapshot_num}"


def mutate_dictionary(preset, snapshot_src_num, postfix_num):
    increment_preset_name(preset, postfix_num)
    duplicate_snapshot_to_all(preset, snapshot(snapshot_src_num))
    choose.random_new_params_for_snapshot_control(preset)
    mutate_parameter_values_for_all_snapshots(preset, constants.MUTATION_RATE)
    mutate_all_default_blocks(preset, constants.MUTATION_RATE)
    swap_some_control_destinations(preset, constants.PEDAL_2, 10)
    mutate_all_pedal_ranges(preset)
    rearrange_blocks(preset, constants.FRACTION_MOVE)
    swap_some_blocks_and_splits_from_file(preset, 0.1)
    toggle_some_block_states(preset, constants.MUTATION_RATE)
    toggle_series_or_parallel_dsps(preset, constants.TOGGLE_RATE)
    utils.set_led_colours(preset)


def mutate_preset_from_source_snapshot(template_file, snapshot_src_num, output_file, postfix_num):
    with open(template_file, "r") as f:
        preset = json.load(f)
        mutate_dictionary(preset, snapshot_src_num, postfix_num)
        print("mutate")
        with open(output_file, "w") as f:
            json.dump(preset, f, indent=4)


def generate_multiple_mutations_from_template(args):
    # preset_name_base = args.get("preset_name_base")
    print("hey!")
    for i in range(args.get("num_presets")):
        # preset_name = preset_name_base + chr(ord("a") + (i % 26))
        mutate_preset_from_source_snapshot(
            args.get("template_file"),
            args.get("snapshot_src_num"),
            args.get("output_file")[:-4] + str(i + 1) + ".hlx",
            i,
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("args_json", type=str, help="JSON string containing arguments")
    args = parser.parse_args()

    args_dict = json.loads(args.args_json)
    generate_multiple_mutations_from_template(args_dict)
