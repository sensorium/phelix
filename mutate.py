""" 
mutate.py
 
 This file is part of phelix.
 
 Copyright 2024 Tim Barrass
 
 phelix is licensed under the GNU General Public Licence (GPL) Version 3 or later. 
"""



import itertools
import random
import debug
import process_preset
import var
import file
import util
import choose


def is_specific_model_type(preset, dsp, slot):
    return util.get_default_dsp_slot(preset, dsp, slot)["@model"].startswith(("HD2_Reverb", "VIC", "Victoria"))


def is_reverb(preset, dsp, slot):
    return util.get_default_dsp_slot(preset, dsp, slot)["@model"].startswith(("HD2_Reverb", "VIC", "Victoria"))


def random_triangle(pmin, pmax, mode_fraction, lowest_fraction):
    lowest = ((pmax - pmin) * lowest_fraction) + pmin
    mode = ((pmax - pmin) * mode_fraction) + pmin
    return random.triangular(lowest, pmax, mode)


def get_mutated_level(pmin, pmax, slot):
    if util.is_block_or_cab_slot(slot):
        return random_triangle(pmin, pmax, 0.8, 0.0)
    else:
        return random.uniform(pmin, pmax)


def get_mutated_decay(pmin, pmax, preset, dsp, slot):
    if is_reverb(preset, dsp, slot):
        return random_triangle(pmin, pmax, 0.05, 0.0)
    else:
        return random.uniform(pmin, pmax)


def get_mutated_time(pmax):
    return min(pmax, random.expovariate(0.95 + (0.75 - 0.95) * (pmax - 2) / (8 - 2)))


def get_mutated_mix(pmin, pmax):
    return random_triangle(pmin, pmax, 0.5, 0.0)


def get_mutated_feedback(pmin, pmax):
    return random_triangle(pmin, pmax, 0.5, 0.0)


def get_mutated_param_value(preset, dsp, slot, param, pmin, pmax):
    if isinstance(pmin, bool):
        return random.choice([True, False])
    if param == "Level":
        return get_mutated_level(pmin, pmax, slot)
    elif param == "Decay":
        return get_mutated_decay(pmin, pmax, preset, dsp, slot)
    elif param == "Time":
        return get_mutated_time(pmax)
    elif param == "Mix":
        return get_mutated_mix(pmin, pmax)
    elif param == "Feedback":
        return get_mutated_feedback(pmin, pmax)
    else:
        return random.uniform(pmin, pmax)


def mutate_param_values_for_one_snapshot_slot(preset, snap_num, dsp, slot, fraction_new):
    raw_controllers = file.reload_raw_block_dictionary(preset, dsp, slot)["Controller_Dict"]
    # print("mutate_param_values_for_one_snapshot_slot", dsp, slot, util.get_default_dsp_slot(preset, dsp, slot)["@model"])
    for param in util.get_controller_dsp_slot(preset, dsp, slot):
        if util.get_controller_dsp_slot_param(preset, dsp, slot, param)["@controller"] == var.CONTROLLER_SNAPSHOT:
            pmin = raw_controllers[param]["@min"]
            pmax = raw_controllers[param]["@max"]
            result = get_mutated_param_value(preset, dsp, slot, param, pmin, pmax)
            prev_result = util.get_snapshot_controllers_dsp_slot_param_value(preset, snap_num, dsp, slot, param)
            result_mix = mix_values(fraction_new, pmin, pmax, result, prev_result)
            # print("mutate", dsp, slot, parameter, pmin, pmax, result, prev_result, result_mix)
            util.get_snapshot_controllers_dsp_slot_param(preset, snap_num, dsp, slot, param)["@value"] = result_mix
            

def mutate_param_values_for_all_snapshots(preset, fraction_new):
    print("\nmutate_param_values_for_all_snapshots")
    # debug.save_debug_hlx(preset)
    for snapshot_num in range(var.NUM_SNAPSHOTS):
        for dsp in util.get_snapshot_controllers(preset, snapshot_num):
            for slot in util.get_snapshot_controllers_dsp(preset, snapshot_num, dsp):
                mutate_param_values_for_one_snapshot_slot(preset, snapshot_num, dsp, slot, fraction_new)
                
                
def mutate_values_in_default_block(preset, dsp, slot, fraction_new):
    raw_controllers = file.reload_raw_block_dictionary(preset, dsp, slot)["Controller_Dict"]
    print("mutate_values_in_default_block", dsp, slot, util.get_model_name(preset, dsp, slot))
    for param in raw_controllers:  # not all default params can be changed on the helix
        pmin = raw_controllers[param]["@min"]
        pmax = raw_controllers[param]["@max"]
        result = get_mutated_param_value(preset, dsp, slot, param, pmin, pmax)
        prev_result = util.get_default_dsp_slot_param_value(preset, dsp, slot, param)
        util.get_default_dsp_slot(preset, dsp, slot)[param] = mix_values(
            fraction_new, pmin, pmax, result, prev_result
        )


def mix_values(fraction_new, pmin, pmax, result, prev_result):
    if isinstance(result, bool):
        return result
    fraction_prev = 1.0 - fraction_new
    result_mix = result * fraction_new + prev_result * fraction_prev
    return max(pmin, min(result_mix, pmax))


def mutate_values_in_all_default_blocks(preset, fraction_new):
    print("Mutating values in preset default")
    for dsp in util.get_available_default_dsp_names(preset):
        for slot in util.get_default_dsp(preset, dsp):
            if slot.startswith(("cab", "split", "block")):
                mutate_values_in_default_block(preset, dsp, slot, fraction_new)

def mutate_parameter_value(mean, p_min, p_max):
    p_range = p_max - p_min
    sigma = p_range / 4
    p = random.normalvariate(mean, sigma)
    while not p_min <= p <= p_max:
        p = random.normalvariate(mean, sigma)
    return p


def remove_some_controllers_and_assign_new_ones_to_snapshot(preset, from_control_type, max_changes):
    print("\nremove_some_controllers_and_assign_new_ones_to_snapshot...")
    num_changes = random.randint(0, max_changes)
    choose.remove_random_controls_of_type(preset, from_control_type, num_changes)
    for _ in range(num_changes):
        choose.assign_random_parameter_controller_to_snapshot_and_randomise_range(preset)


def change_some_controller_types(preset, controller_type, number_of_changes):
    print("\nchange_some_controller_types to controller "+str(controller_type))
    for _ in range(number_of_changes):
        choose.assign_random_parameter_to_controller_type_and_randomise_range(preset, controller_type)


def toggle_block_state(preset, dsp, slot):
    current_state = util.get_default_dsp_slot_param_value(preset, dsp, slot, "@enabled")
    util.get_default_dsp_slot(preset, dsp, slot)["@enabled"] = not current_state


def toggle_some_block_states(preset, change_fraction):
    for dsp in util.get_available_default_dsp_names(preset):
        for slot in util.get_default_dsp(preset, dsp):
            if slot.startswith("block") and random.uniform(0, 1) < change_fraction:
                toggle_block_state(preset, dsp, slot)

    for snapshot_num in range(var.NUM_SNAPSHOTS):
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
    for dsp in util.get_available_default_dsp_names(preset):
        dsp_slot.extend([dsp, slot] for slot in util.get_default_dsp(preset, dsp) if slot.startswith("block"))
    return dsp_slot


def find_unused_default_block_slots(preset):
    dsp_slot = []
    for dsp in util.get_available_default_dsp_names(preset):
        for block_num in range(var.NUM_SLOTS_PER_DSP):
            slot = f"block{block_num}"
            if slot not in util.get_default_dsp(preset, dsp):
                dsp_slot.append([dsp, slot])
    return list(reversed(dsp_slot))


def find_used_default_dsp_path_pos(preset):
    dsp_path_pos = {}
    for dsp in util.get_available_default_dsp_names(preset):
        dsp_path_pos[dsp] = []
        for slot in util.get_default_dsp(preset, dsp):
            if slot.startswith("block"):
                slot_dict = util.get_default_dsp_slot(preset, dsp, slot)
                dsp_path_pos[dsp].append((slot_dict["@path"], slot_dict["@position"]))
    return dsp_path_pos


def find_unused_dsp_path_positions(preset):
    used_dsp_path_positions = find_used_default_dsp_path_pos(preset)
    unused_dsp_path_positions = {}
    for dsp in util.get_available_default_dsp_names(preset):
        unused_dsp_path_positions[dsp] = []
        for path, pos in itertools.product(range(var.NUM_PATHS_PER_DSP), range(var.NUM_POSITIONS_PER_PATH)):
            if (path, pos) not in used_dsp_path_positions[dsp]:
                unused_dsp_path_positions[dsp].append((path, pos))
    return unused_dsp_path_positions


def find_used_default_dsp_cab_slots(preset):
    used_dsp_cab_slots = {}
    for dsp in util.get_available_default_dsp_names(preset):
        used_dsp_cab_slots[dsp] = []
        for slot in util.get_default_dsp(preset, dsp):
            if slot.startswith("cab"):
                used_dsp_cab_slots[dsp].append(slot)
    return used_dsp_cab_slots


def find_unused_default_dsp_cab_slots(preset):
    used_dsp_cab_slots = find_used_default_dsp_cab_slots(preset)
    unused_dsp_cab_slots = {}
    for dsp in util.get_available_default_dsp_names(preset):
        unused_dsp_cab_slots[dsp] = []
        for cab_num in range(var.NUM_SLOTS_PER_DSP):
            slot = f"cab{cab_num}"
            if slot not in used_dsp_cab_slots[dsp]:
                unused_dsp_cab_slots[dsp].append(slot)
        unused_dsp_cab_slots[dsp] = list(reversed(unused_dsp_cab_slots[dsp]))
    return unused_dsp_cab_slots


def count_blocks_on_each_dsp(preset):
    blocks_on_dsp0 = 0
    blocks_on_dsp1 = 0
    for dsp in util.get_available_default_dsp_names(preset):
        for slot in util.get_default_dsp(preset, dsp):
            if slot.startswith("block"):
                blocks_on_dsp0 += 1 if dsp == "dsp0" else 0
                blocks_on_dsp1 += 1 if dsp == "dsp1" else 0
    return blocks_on_dsp0, blocks_on_dsp1


def which_dsp_to_move_to(preset):
    blocks_on_dsp0, blocks_on_dsp1 = count_blocks_on_each_dsp(preset)
    print("blocks_on_dsp0, blocks_on_dsp1", blocks_on_dsp0, blocks_on_dsp1)
    choice_list = ["dsp0"] * blocks_on_dsp1 + ["dsp1"] * blocks_on_dsp0  # note reversed probability
    return random.choice(choice_list)


def get_unused_block_slot(unused_block_slots, to_dsp):
    """Finds and returns an unused block slot in the specified DSP."""
    for to_dsp_slot in unused_block_slots:
        if to_dsp_slot[0] == to_dsp:
            to_slot = to_dsp_slot[1]
            unused_block_slots.remove([to_dsp, to_slot])
            return to_dsp, to_slot
    return None, None  # No unused slot found in the specified DSP


def is_amp_slot(preset, to_dsp, model_name):
    return model_name.startswith("HD2_Amp") and util.count_amps(preset, to_dsp) > 0


def rearrange_blocks(preset, fraction_move):
    print("\nrearrange_blocks")
    used_block_slots = find_used_default_block_slots(preset)
    unused_block_slots = find_unused_default_block_slots(preset)
    used_dsp_path_positions = find_used_default_dsp_path_pos(preset)
    unused_dsp_path_positions = find_unused_dsp_path_positions(preset)
    used_dsp_cab_slots = find_used_default_dsp_cab_slots(preset)
    unused_dsp_cab_slots = find_unused_default_dsp_cab_slots(preset)
    unused_block_slots.reverse()  # so we find low slots first
    # print(used_slots, unused_slots)
    for dsp, slot in used_block_slots:
        if random.uniform(0, 1) < fraction_move:
            model_name = util.get_model_name(preset, dsp, slot)
            # update slot arrays
            # to_dsp, to_slot = unused_block_slots.pop()
            to_dsp = which_dsp_to_move_to(preset)
            for to_dsp_slot in unused_block_slots:
                if to_dsp_slot[0] == to_dsp:
                    to_slot = to_dsp_slot[1]
                    unused_block_slots.remove([to_dsp, to_slot])
                    break

            # wastes unused slot this turn if there is already an amp in to_dsp
            if model_name.startswith("HD2_Amp") and dsp != to_dsp and util.count_amps(preset, to_dsp) > 0:
                return

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
    for dsp in util.get_available_default_dsp_names(preset):
        for slot in util.get_default_dsp(preset, dsp):
            if random.uniform(0, 1) < change_fraction:
                util.remove_controller_dsp_slot_if_present(preset, dsp, slot)
                util.remove_snapshots_controllers_dsp_slot_if_present(preset, dsp, slot)
                if slot.startswith("block"):
                    swap_block_from_file_using_probabilities(preset, dsp, slot)
                if slot.startswith("split") and random.uniform(0, 1) < change_fraction:
                    swap_with_random_split_from_file(preset, dsp, slot)
                
                # TODO : fix swap_with_random_cab_from_file
                # if slot.startswith("cab") and random.uniform(0, 1) < change_fraction:
                #     swap_with_random_cab_from_file(preset, dsp, slot)
                

def swap_block_from_file_using_probabilities(preset, dsp, slot):
    print("swap_block_from_file_using_probabilities")
    path = util.get_default_dsp_slot(preset, dsp, slot)["@path"]
    pos = util.get_default_dsp_slot(preset, dsp, slot)["@position"]
    raw_block_dict = file.load_block_dictionary(choose.probabilities_block_file_excluding_cab_or_split())
    util.add_raw_block_to_default_and_controller_and_snapshots(preset, dsp, slot, raw_block_dict)
    util.get_default_dsp_slot(preset, dsp, slot)["@path"] = path
    util.get_default_dsp_slot(preset, dsp, slot)["@position"] = pos
    for snapshot_num in range(var.NUM_SNAPSHOTS):
        mutate_param_values_for_one_snapshot_slot(preset, snapshot_num, dsp, slot, 1.0)


def swap_with_random_split_from_file(preset, dsp, slot):
    print("swap_with_random_split_from_file")
    keep_position = util.get_default_dsp_slot(preset, dsp, slot)["@position"]
    split_dict = file.load_block_dictionary(choose.random_block_file_in_category("Split"))
    util.add_raw_block_to_default_and_controller_and_snapshots(preset, dsp, slot, split_dict)
    util.get_default_dsp_slot(preset, dsp, slot)["@position"] = keep_position
    
    
def mutate_all_control_ranges(preset, controller):
    for dsp in util.get_controller(preset):
        for slot in util.get_controller_dsp(preset, dsp):
            block = util.get_controller_dsp(preset, dsp)[slot]
            if any(block[param]["@controller"] == controller for param in block):
                for parameter in block:
                    if block[parameter]["@controller"] == controller:
                        mutate_one_set_of_control_ranges(preset, dsp, slot, parameter)
                break



def mutate_one_set_of_control_ranges(preset, dsp, slot, parameter):
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



def change_topology(preset):
    rearrange_blocks(preset, var.FRACTION_MOVE)
    choose.move_splits_and_joins(preset)
    toggle_series_or_parallel_dsps(preset, var.TOGGLE_RATE)



def mutate_values_ranges_and_states(preset, mutation_rate, block_toggle_rate):
    mutate_param_values_for_all_snapshots(preset, mutation_rate)
    mutate_all_control_ranges(preset, var.CONTROLLER_PEDAL2)
    mutate_all_control_ranges(preset, var.CONTROLLER_MIDICC)    
    mutate_values_in_all_default_blocks(preset, mutation_rate)
    toggle_some_block_states(preset, block_toggle_rate)
    


def mutate_preset_processor(preset, args, postfix_num):
    snapshot_src_num_str = args.get("snapshot_src_num")
    if snapshot_src_num_str == "":
        snapshot_src_num_str = "default"
 
    util.set_preset_name_for_mutate(preset, args, postfix_num)
    util.copy_snapshot_values_to_default(preset, snapshot_src_num_str)
    util.copy_all_default_values_to_all_snapshots(preset)
    # util.add_dsp_controller_splits_and_snapshot_keys_if_missing(preset)
    util.set_led_colours(preset)
    util.add_splits_if_missing(preset)
    if args.get("change_topology") is True:
        util.set_topologies_to_SABJ(preset)
        util.set_dsp1_input_to_multi(preset)
        change_topology(preset)
    swap_some_blocks_and_splits_from_file(preset, var.MUTATION_RATE)
    if args.get("change_controllers") is True:
        choose.remove_some_random_controllers(preset) 
        util.remove_empty_controller_dsp_slots(preset) 
        choose.grow_SNAPSHOT_controllers(preset)
        choose.grow_PEDAL2_controllers(preset)
        choose.grow_MIDICC_controllers(preset)
    mutate_values_ranges_and_states(preset, var.MUTATION_RATE, var.MUTATION_RATE)
    return preset



def main():
    process_preset.main(mutate_preset_processor)



if __name__ == "__main__":
    main()