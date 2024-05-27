from copy import deepcopy
import json
import random
import os


NUM_SNAPSHOTS = 8
NUM_SLOTS_PER_DSP = 16
NUM_PEDAL_PARAMS = 16
BLOCKS_PATH = "blocks/test"


def countNumControllersSetTo2(preset_dict):
    count = 0
    for dsp_name in ["dsp0", "dsp1"]:
        for block_name in preset_dict["data"]["tone"]["controller"][dsp_name]:
            if preset_dict["data"]["tone"]["controller"][dsp_name][block_name] == 2:
                count += 1
    return count


def chooseParamValuesForOneBlock(preset_dict, snapshot_num, dsp_name, block_name, fraction_new):
    # snapshot_name = "snapshot" + str(snapshot_num)
    block_dict_controls = preset_dict["data"]["tone"]["controller"][dsp_name][block_name]
    defaults_block = preset_dict["data"]["tone"][dsp_name][block_name]
    for parameter in block_dict_controls:
        pmin = block_dict_controls[parameter]["@min"]
        pmax = block_dict_controls[parameter]["@max"]
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
            result = random.uniform(
                pmin, pmax
            )  # switch choices are rounded to nearest integer in helix preset_dict["data"]["tone"][snapshot_name]["controllers"][dsp_name][block_name][parameter]["@value"] = result
        # make defaults same as snapshot 0
        if snapshot_num == 0 and block_name[:3] in ("block", "cab", "split") and not parameter.startswith("@"):
            if isinstance(result, bool):
                defaults_block[parameter] = result
            else:
                prev_result = defaults_block[parameter]
                fraction_prev = 1.0 - fraction_new
                result_mix = result * fraction_new + prev_result * fraction_prev
                result_mix_constrained = max(pmin, min(result_mix, pmax))
                defaults_block[parameter] = result_mix_constrained
                # print(pmin, pmax, prev_result, result_mix_constrained)


def chooseParamValuesForAllSnapshots(preset_dict):
    for snapshot_num in range(NUM_SNAPSHOTS):
        snapshot_name = "snapshot" + str(snapshot_num)
        for dsp_name in ["dsp0", "dsp1"]:
            for block_name in preset_dict["data"]["tone"][snapshot_name]["controllers"][dsp_name]:
                chooseParamValuesForOneBlock(preset_dict, snapshot_num, dsp_name, block_name, 1.0)


def countParamControls(preset_dict):
    num_params = 0
    for dsp_name in ["dsp0", "dsp1"]:
        for block_name in preset_dict["data"]["tone"]["controller"][dsp_name]:
            if block_name.startswith(("block", "split")):
                for parameter in preset_dict["data"]["tone"]["controller"][dsp_name][block_name]:
                    num_params += 1
    return num_params


def setLedColours(preset_dict):
    for snapshot_num in range(NUM_SNAPSHOTS):
        snapshot_name = "snapshot" + str(snapshot_num)
        # snapshot ledcolor
        preset_dict["data"]["tone"][snapshot_name]["@ledcolor"] = str(snapshot_num + 1)


def getRandDspAndBlock(preset_dict):
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


def getRandControllerParam(preset_dict, dsp_name, block):
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


def getRandControllerParamNoBoolNoMic(preset_dict, dsp_name, block):
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


def delRandomParamControl(preset_dict):
    # delete a param if the random choice exists
    randdsp, randblock = getRandDspAndBlock(preset_dict)
    if randblock != "none":
        randparam = getRandControllerParam(preset_dict, randdsp, randblock)
        if randparam != "none":
            # remove the param from all snapshots
            for snapshot_num in range(NUM_SNAPSHOTS):
                snapshot_name = "snapshot" + str(snapshot_num)
                if randparam in preset_dict["data"]["tone"][snapshot_name]["controllers"][randdsp][randblock]:
                    del preset_dict["data"]["tone"][snapshot_name]["controllers"][randdsp][randblock][randparam]

            # remove param from controller
            if randparam in preset_dict["data"]["tone"]["controller"][randdsp][randblock]:
                del preset_dict["data"]["tone"]["controller"][randdsp][randblock][randparam]

            print("deleted " + randblock + " " + randparam)


def changeSomePedalControls(preset_dict, pedalnum, max_changes):
    # get a list of params with pedal control (controller number 2)
    pedal_block_params = []
    for dsp_name in ["dsp0", "dsp1"]:
        for block in preset_dict["data"]["tone"]["controller"][dsp_name]:
            # if block.startswith(("block", "split", "cab")):
            for param in preset_dict["data"]["tone"]["controller"][dsp_name][block]:
                if preset_dict["data"]["tone"]["controller"][dsp_name][block][param]["@controller"] == 2:
                    pedal_block_params.append([dsp_name, block, param])
    # choose a block,param pair
    num_changes = random.randint(0, max_changes)
    for _ in range(num_changes):
        random_index = random.randint(0, len(pedal_block_params) - 1)
        dsp_name, block, param = pedal_block_params[random_index]
        # set control to snapshot
        print("unsetting pedal for " + dsp_name, block, param, pedalnum)
        preset_dict["data"]["tone"]["controller"][dsp_name][block][param][
            "@controller"
        ] = 19  # set back to snapshot control
        # set another param to pedalnum
        setRandPedalParamAndRanges(preset_dict, pedalnum)


def setRandPedalParamAndRanges(preset_dict, pedalnum):
    randdsp, randblock = getRandDspAndBlock(preset_dict)
    if randblock != "none":
        randparam = getRandControllerParamNoBoolNoMic(preset_dict, randdsp, randblock)
        if randparam != "none":
            model_name = preset_dict["data"]["tone"][randdsp][randblock]["@model"]
            print(
                "setting pedal for " + randdsp,
                randblock,
                model_name,
                randparam,
                pedalnum,
            )
            pedal_param = preset_dict["data"]["tone"]["controller"][randdsp][randblock][randparam]
            pedal_param["@controller"] = pedalnum
            new_max = random.uniform(pedal_param["@min"], pedal_param["@max"])
            new_min = random.uniform(pedal_param["@min"], pedal_param["@max"])
            # set new random max and min values within the original limits
            pedal_param["@max"] = new_max
            pedal_param["@min"] = new_min


def chooseParamValueAround(mean, p_min, p_max):
    p_range = p_max - p_min
    sigma = p_range / 4
    p = random.normalvariate(mean, sigma)
    while not p_min <= p <= p_max:
        p = random.normalvariate(mean, sigma)
    return p


def copySnapshot(preset_dict, snapshot_src, snapshot_dst):
    preset_dict["data"]["tone"][snapshot_dst] = deepcopy(preset_dict["data"]["tone"][snapshot_src])
    preset_dict["data"]["tone"][snapshot_dst]["@name"] = snapshot_dst


def copySnapshotToAll(preset_dict, snapshot_src):
    for snapshot_num in range(NUM_SNAPSHOTS):
        snapshot_dst = "snapshot" + str(snapshot_num)
        if snapshot_dst != snapshot_src:
            copySnapshot(preset_dict, snapshot_src, snapshot_dst)


def changeBlockStates(preset_dict, change_fraction):
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


def findUnusedBlockNameInDsp(preset_dict, dsp_name):
    for i in range(16):
        new_block_name = "block" + str(i)
        if new_block_name not in preset_dict["data"]["tone"][dsp_name]:
            break
    return new_block_name


def moveBlockPositions(preset_dict, fraction_move):
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
            for pos in range(8):  # slots per path
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
    moveBlocks(preset_dict, dsp_blockname_to_dsp_path_pos)


def moveBlocks(preset_dict, dsp_blockname_to_dsp_path_pos):
    for item in dsp_blockname_to_dsp_path_pos:
        from_dsp = item[0]
        block_name = item[1]
        from_path = preset_dict["data"]["tone"][from_dsp][block_name]["@path"]
        from_position = preset_dict["data"]["tone"][from_dsp][block_name]["@position"]
        to_dsp = item[2][0]
        to_path = item[2][1]
        to_position = item[2][2]
        new_block_name = findUnusedBlockNameInDsp(preset_dict, to_dsp)
        preset_dict["data"]["tone"][to_dsp][new_block_name] = preset_dict["data"]["tone"][from_dsp].pop(block_name)
        preset_dict["data"]["tone"][to_dsp][new_block_name]["@path"] = to_path
        preset_dict["data"]["tone"][to_dsp][new_block_name]["@position"] = to_position
        preset_dict["data"]["tone"]["controller"][to_dsp][new_block_name] = preset_dict["data"]["tone"]["controller"][
            from_dsp
        ].pop(block_name)

        for snapshot_num in range(NUM_SNAPSHOTS):
            snapshot_name = "snapshot" + str(snapshot_num)
            preset_dict["data"]["tone"][snapshot_name]["blocks"][to_dsp][new_block_name] = preset_dict["data"]["tone"][
                snapshot_name
            ]["blocks"][from_dsp].pop(block_name)

        print(
            "Moved",
            from_dsp,
            block_name,
            from_path,
            from_position,
            "to",
            to_dsp,
            new_block_name,
            to_path,
            to_position,
        )


# replace block default params with extracted block params, given blockNumber and dsp_name
def replaceBlockDefaultParams(block_dict, preset_dict, block_num, dsp_name):
    preset_dict["data"]["tone"][dsp_name]["block" + str(block_num)] = block_dict["Defaults"]


# load extracted block parameters from a json file, return a dictionary
def loadBlockDict(block_filename):
    with open(os.path.expanduser(block_filename), "r") as f:
        block_dict = json.load(f)
    return block_dict


def chooseCategory() -> str:
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


def chooseAnyBlockFileExceptCabOrSplit():
    randcat = chooseCategory()
    while randcat in ["Split", "Cab"]:
        randcat = chooseCategory()
    return chooseBlockFileInCategory(randcat)


def chooseBlockFileInCategory(category_folder):
    full_path = os.path.join(BLOCKS_PATH, category_folder)
    block_files = [f for f in os.listdir(full_path) if os.path.isfile(os.path.join(full_path, f))]
    filename = os.path.join(full_path, random.choice(block_files))
    # print("choosing" + filename)
    return filename


def insertBlockParamsIntoAllSnapshots(preset_dict, dsp_name, destination_block_name, new_block_dict):
    for snapshot_num in range(NUM_SNAPSHOTS):
        snapshot_name = "snapshot" + str(snapshot_num)
        # following "if" line probably unnecessary
        if "controllers" not in preset_dict["data"]["tone"][snapshot_name]:
            preset_dict["data"]["tone"][snapshot_name]["controllers"] = {}
            print("added controllers")
        # following "if" line probably unnecessary
        if dsp_name not in preset_dict["data"]["tone"][snapshot_name]["controllers"]:
            preset_dict["data"]["tone"][snapshot_name]["controllers"][dsp_name] = {}
            print("added " + dsp_name)

        # add snapshot params from block_dict
        preset_dict["data"]["tone"][snapshot_name]["controllers"][dsp_name][destination_block_name] = deepcopy(
            new_block_dict["SnapshotParams"]
        )


def swapSomeBlocksAndSplitsFromFile(preset_dict, change_fraction):
    for dsp_name in ["dsp0", "dsp1"]:
        for block_name in preset_dict["data"]["tone"][dsp_name]:
            if block_name.startswith("block"):
                if random.uniform(0, 1) < change_fraction:  # change state
                    swapBlockFromFile(preset_dict, dsp_name, block_name)
            if block_name.startswith("split"):
                if random.uniform(0, 1) < change_fraction:  # change state
                    swapSplitFromFile(preset_dict, dsp_name, block_name)


def swapBlockFromFile(preset_dict, dsp_name, block_name):
    print("swapping block from file")
    path = preset_dict["data"]["tone"][dsp_name][block_name]["@path"]
    pos = preset_dict["data"]["tone"][dsp_name][block_name]["@position"]
    new_block_dict = loadBlockDict(chooseAnyBlockFileExceptCabOrSplit())
    preset_dict["data"]["tone"][dsp_name][block_name] = new_block_dict["Defaults"]
    preset_dict["data"]["tone"][dsp_name][block_name]["@path"] = path
    preset_dict["data"]["tone"][dsp_name][block_name]["@position"] = pos
    insertBlockParamsIntoAllSnapshots(preset_dict, dsp_name, block_name, new_block_dict)
    preset_dict["data"]["tone"]["controller"][dsp_name][block_name] = new_block_dict["Ranges"]
    for snapshot_num in range(NUM_SNAPSHOTS):
        chooseParamValuesForOneBlock(preset_dict, snapshot_num, dsp_name, block_name, 1.0)


def swapSplitFromFile(preset_dict, dsp_name, block_name):
    print("swapping split from file")
    pos = preset_dict["data"]["tone"][dsp_name][block_name]["@position"]
    new_block_dict = loadBlockDict(chooseBlockFileInCategory("Split"))
    preset_dict["data"]["tone"][dsp_name][block_name] = new_block_dict["Defaults"]
    preset_dict["data"]["tone"][dsp_name][block_name]["@position"] = pos
    insertBlockParamsIntoAllSnapshots(preset_dict, dsp_name, block_name, new_block_dict)
    preset_dict["data"]["tone"]["controller"][dsp_name][block_name] = new_block_dict["Ranges"]
    for snapshot_num in range(NUM_SNAPSHOTS):
        chooseParamValuesForOneBlock(preset_dict, snapshot_num, dsp_name, block_name, 1.0)


def mutateName(preset_dict):
    vowels = "aeiou"
    consonants = "bcdfghjklmnpqrstvwxyz"
    name = preset_dict["data"]["meta"]["name"]
    last_char = name[-1]
    if last_char in vowels:
        if random.uniform(0, 1) < 0.2:
            name += random.choice(vowels)
        else:
            name += random.choice(consonants)
    else:
        if random.uniform(0, 1) < 0.2:
            name += random.choice(consonants)
        else:
            name += random.choice(vowels)
    # Replace the last 2 characters of the string
    # if random.choice([True, False]):
    #     name = name[:-2]+random.choice(vowels)+random.choice(consonants)
    # else:
    #     name = name[:-2]+random.choice(consonants)+random.choice(vowels)
    preset_dict["data"]["meta"]["name"] = name
    print(name)


def mutateAllPedalRanges(preset_dict):
    for dsp_name in ["dsp0", "dsp1"]:
        for block_or_split_name in preset_dict["data"]["tone"]["controller"][dsp_name]:
            params = preset_dict["data"]["tone"]["controller"][dsp_name][block_or_split_name]
            if any(params[param]["@controller"] == 2 for param in params):
                for param in params:
                    if params[param]["@controller"] == 2:
                        mutateOneSetOfPedalRanges(preset_dict, dsp_name, block_or_split_name, param)
                break


def mutateOneSetOfPedalRanges(preset_dict, dsp_name, block_or_split_name, param_name):
    param = preset_dict["data"]["tone"]["controller"][dsp_name][block_or_split_name][param_name]
    if not isinstance(param["@min"], bool):  # don't want to pedal bools
        # get original ranges from file
        block_dict = loadBlockDictFromFile(preset_dict, dsp_name, block_or_split_name)
        pmin = block_dict["Ranges"][param_name]["@min"]
        pmax = block_dict["Ranges"][param_name]["@max"]
        # print(pedalParam["@min"], pmin, pmax)
        new_min = chooseParamValueAround(param["@min"], pmin, pmax)  # (mean, pmin, pmax)
        new_max = chooseParamValueAround(param["@max"], pmin, pmax)
        param["@min"] = new_min
        param["@max"] = new_max


def loadBlockDictFromFile(preset_dict, dsp_name, block_or_split_name):
    block_filename = preset_dict["data"]["tone"][dsp_name][block_or_split_name]["@model"] + ".json"
    block_folder = None
    for root, _, files in os.walk(BLOCKS_PATH):
        if block_filename in files:
            block_folder = root
            break
    print(block_folder, block_filename)
    block_dict = loadBlockDict(block_folder + "/" + block_filename)
    return block_dict


def seriesOrParallelPaths(preset_dict):
    preset_dict["data"]["tone"]["dsp0"]["outputA"]["@output"] = random.randint(1, 2)


def changeSeriesOrParallelPaths(preset_dict, change_fraction):
    if random.uniform(0, 1) < change_fraction:  # change state
        print("changing series or parallel paths")
        current = preset_dict["data"]["tone"]["dsp0"]["outputA"]["@output"]
        if current == 1:
            preset_dict["data"]["tone"]["dsp0"]["outputA"]["@output"] = 2
        else:
            preset_dict["data"]["tone"]["dsp0"]["outputA"]["@output"] = 1


def load_block_params(block_filename):
    block_folder = None
    for root, _, files in os.walk(BLOCKS_PATH):
        if block_filename in files:
            block_folder = root
            break
    block_dict = loadBlockDict(block_folder + "/" + block_filename)
    return block_dict


# def loadBlockParamsForOneBlock(preset_dict, dsp_name, block_or_split_name):
#     block_filename = preset_dict["data"]["tone"][dsp_name][block_or_split_name]["@model"] + ".json"
#     block_dict = load_block_params(block_filename)
#     return block_dict


def chooseAnyBlockInDictionary(preset_dict):
    dsp_name = random.choice(["dsp0", "dsp1"])
    block_name = random.choice(list(preset_dict["data"]["tone"][dsp_name].keys()))
    if block_name.startswith(("block", "split", "cab")):
        return dsp_name, block_name
    else:
        return chooseAnyBlockInDictionary(preset_dict)


def addParamToAllSnapshots(preset_dict, dsp_name, block_name, random_param):
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


def setRandomParamControl(preset_dict):
    dsp_name, block_name = chooseAnyBlockInDictionary(preset_dict)
    params_not_in_controller = [
        parameter
        for parameter in preset_dict["data"]["tone"][dsp_name][block_name]
        if parameter not in preset_dict["data"]["tone"]["controller"][dsp_name][block_name]
        and not parameter.startswith("@")
        and not parameter.startswith("bypass")
    ]
    if params_not_in_controller:
        random_param = random.choice(params_not_in_controller)
        print(params_not_in_controller)
        print(random_param)
        block_dict = loadBlockDictFromFile(preset_dict, dsp_name, block_name)
        print(block_dict["Ranges"][random_param])
        preset_dict["data"]["tone"]["controller"][dsp_name][block_name][random_param] = {}
        preset_dict["data"]["tone"]["controller"][dsp_name][block_name][random_param] = deepcopy(
            block_dict["Ranges"][random_param]
        )
        preset_dict["data"]["tone"]["controller"][dsp_name][block_name][random_param]["@controller"] = 19
        # add the param to snapshots
        addParamToAllSnapshots(preset_dict, dsp_name, block_name, random_param)


def changeSomeSnapshotControllers(preset_dict):
    num_controllers_to_change = random.randint(0, 20)
    for i in range(num_controllers_to_change):
        delRandomParamControl(preset_dict)

    while countParamControls(preset_dict) < 64:  # to avoid setting any twice
        setRandomParamControl(preset_dict)


def mutateSnapshot(preset_dict, snapshot_src_num, fraction_change_block_states, fraction_move):
    mutateName(preset_dict)
    snapshot_src_name = "snapshot" + str(snapshot_src_num)
    copySnapshotToAll(preset_dict, snapshot_src_name)
    changeSomeSnapshotControllers(preset_dict)
    chooseParamValuesForAllSnapshots(preset_dict)
    changeBlockStates(preset_dict, fraction_change_block_states)
    changeSomePedalControls(preset_dict, 2, 5)
    mutateAllPedalRanges(preset_dict)
    moveBlockPositions(preset_dict, fraction_move)
    swapSomeBlocksAndSplitsFromFile(preset_dict, 0.1)
    changeSeriesOrParallelPaths(preset_dict, 0.2)
    setLedColours(preset_dict)


def mutatePresetSnapshotParams(
    preset_filename, snapshot_num, new_preset_filename, fraction_change_block_states, fraction_move
):
    with open(preset_filename, "r") as f:
        preset_dict = json.load(f)
        mutateSnapshot(preset_dict, snapshot_num, fraction_change_block_states, fraction_move)
        with open(new_preset_filename, "w") as f:
            json.dump(preset_dict, f, indent=4)
