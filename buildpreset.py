# this module takes a preset file and modifies it to be a valid preset for the pedalboard
# it loads and modifies the json, and then saves it back as a new file
from datetime import datetime
import os
import json
import random
from copy import deepcopy
import mutate

BLOCKS_PATH = "blocks/test"

# todo:
# load effects from category folders so there can be even (or other) chances of them being used
# swap blocks with ones from file
# make wahs frequently have pedal control - if exp1, then the default val can be randomly chosen


# load a template preset from a json file, return a dictionary
def loadPreset(preset_file):
    with open(os.path.expanduser(preset_file), "r") as f:
        preset_dict = json.load(f)
    return preset_dict


# return a random number biased between max and min
# from https://stackoverflow.com/questions/29325069/how-to-generate-random-numbers-biased-towards-one-value-in-a-range
def getRndBias(minval, maxval, bias, influence):
    rnd = random.uniform(minval, maxval)  # random number in the min-max range
    mix = random.uniform(0, 1) * influence  # random normalized mix value
    return rnd * (1 - mix) + bias * mix  # Mix random with bias based on random mix


# if an amp is chosen
# choose a cab


def addCabs(preset_dict, dsp_name):
    # list all cabs in blocks folder
    cabs_file_list = []
    for filename in os.listdir(BLOCKS_PATH + "/Cab/"):
        if filename.startswith("HD2_Cab"):
            cabs_file_list.append(filename)

    # keep track of how many cabs used
    cabs_used = 0

    amp_blocks_list = []
    for block_name in preset_dict["data"]["tone"][dsp_name]:
        if preset_dict["data"]["tone"][dsp_name][block_name]["@model"].startswith(
            "HD2_Amp"
        ):
            amp_blocks_list.append(block_name)

    for amp in amp_blocks_list:
        # add a cab
        cab_name = "cab" + str(cabs_used)
        cabs_used += 1
        preset_dict["data"]["tone"][dsp_name][amp]["@cab"] = cab_name
        # load a random cab
        cab_dict = mutate.loadBlockParams(
            BLOCKS_PATH + "/Cab/" + random.choice(cabs_file_list)
        )
        # delete cab path and position, if they exist
        if "@path" in cab_dict["Defaults"]:
            del cab_dict["Defaults"]["@path"]
        if "@position" in cab_dict["Defaults"]:
            del cab_dict["Defaults"]["@position"]
        preset_dict["data"]["tone"][dsp_name][cab_name] = cab_dict["Defaults"]


# insert param keys into each snapshot in preset
def replaceParamKeys(preset_dict, dsp_name):
    num_amps = 0

    addControllerAndDspKeysIfNeeded(preset_dict, dsp_name)

    block_positions_path0 = [i for i in range(8)]  # 8 per path
    random.shuffle(block_positions_path0)
    block_positions_path1 = [i for i in range(8)]  # 8 per path
    random.shuffle(block_positions_path1)

    for destination_block_name in preset_dict["data"]["tone"][dsp_name]:
        if destination_block_name.startswith(
            "block"
        ):  # or block_name.startswith("cab"): # cabs will be sorted with amps later, but cabs in amps will take an extra position at this step
            new_block_dict = loadBlockParamsForOneBlock(num_amps)
            num_amps = updateNumAmps(num_amps, new_block_dict)
            preset_dict["data"]["tone"][dsp_name][destination_block_name] = (
                new_block_dict["Defaults"]
            )
            print(
                "   loaded "
                + destination_block_name
                + " "
                + new_block_dict["Defaults"]["@model"]
            )

            path_num = random.randint(0, 1)
            setPathAndPositionForOneBlock(
                preset_dict,
                dsp_name,
                destination_block_name,
                path_num,
                block_positions_path0,
                block_positions_path1,
            )

            addBlockToController(
                preset_dict, dsp_name, destination_block_name, new_block_dict
            )
            mutate.insertBlockParamsIntoAllSnapshots(
                preset_dict, dsp_name, destination_block_name, new_block_dict
            )

        elif destination_block_name.startswith("split"):
            split_dict = chooseSplit()
            preset_dict["data"]["tone"][dsp_name]["split"] = deepcopy(
                split_dict["Defaults"]
            )
            preset_dict["data"]["tone"]["controller"][dsp_name][
                destination_block_name
            ] = split_dict["Ranges"]
            for snapshot_num in range(num_snapshots):
                snapshot_name = "snapshot" + str(snapshot_num)
                preset_dict["data"]["tone"][snapshot_name]["controllers"][dsp_name][
                    destination_block_name
                ] = deepcopy(split_dict["SnapshotParams"])

    join_position = random.randint(6, 8)
    split_position = random.randint(0, join_position - 3)

    preset_dict["data"]["tone"][dsp_name]["join"]["@position"] = join_position
    preset_dict["data"]["tone"][dsp_name]["split"]["@position"] = split_position


def addControllerAndDspKeysIfNeeded(preset_dict, dsp_name):
    if "controller" not in preset_dict["data"]["tone"]:
        preset_dict["data"]["tone"]["controller"] = {}
    if dsp_name not in preset_dict["data"]["tone"]["controller"]:
        preset_dict["data"]["tone"]["controller"][dsp_name] = {}


def loadBlockParamsForOneBlock(num_amps):
    while True:
        block_dict = mutate.loadBlockParams(mutate.chooseAnyBlockFileExceptCabOrSplit())
        if not block_dict["Defaults"]["@model"].startswith("HD2_Amp") or num_amps < 1:
            break
    return block_dict


def updateNumAmps(num_amps, block_dict):
    if block_dict["Defaults"]["@model"].startswith("HD2_Amp"):
        num_amps += 1
    return num_amps


def setPathAndPositionForOneBlock(
    preset_dict,
    dsp_name,
    block_name,
    path_num,
    block_positions_path0,
    block_positions_path1,
):
    preset_dict["data"]["tone"][dsp_name][block_name]["@path"] = path_num
    if path_num == 0:
        preset_dict["data"]["tone"][dsp_name][block_name][
            "@position"
        ] = block_positions_path0.pop()
    else:
        preset_dict["data"]["tone"][dsp_name][block_name][
            "@position"
        ] = block_positions_path1.pop()


def addBlockToController(preset_dict, dsp_name, block_name, block_dict):
    preset_dict["data"]["tone"]["controller"][dsp_name][block_name] = block_dict[
        "Ranges"
    ]


def chooseSplit():
    # list all splits in split folder
    splits_file_list = [
        "HD2_AppDSPFlowSplitAB",
        "HD2_AppDSPFlowSplitDyn",
        "HD2_AppDSPFlowSplitXOver",
    ]
    weights = [0.5, 0.25, 0.25]
    split_file = "".join(random.choices(splits_file_list, weights, k=1))
    print(split_file)
    return mutate.loadBlockParams(BLOCKS_PATH + "/Split/" + split_file + ".json")


def chooseBlocksOnOrOff(preset_dict, dsp_name):
    for snapshot_num in range(num_snapshots):
        snapshot_name = "snapshot" + str(snapshot_num)
        if dsp_name in preset_dict["data"]["tone"][snapshot_name]["blocks"]:
            for block in preset_dict["data"]["tone"][snapshot_name]["blocks"][dsp_name]:
                if block.startswith("block") or block.startswith("cab"):
                    state = False
                    if random.uniform(0, 1) < 0.7:
                        state = True
                    preset_dict["data"]["tone"][snapshot_name]["blocks"][dsp_name][
                        block
                    ] = state


def generateFromSavedBlocks(preset_dict, dsp_name):
    print(dsp_name)
    replaceParamKeys(preset_dict, dsp_name)
    mutate.chooseParamValuesForAllSnapshots(preset_dict)
    addCabs(preset_dict, dsp_name)
    chooseBlocksOnOrOff(preset_dict, dsp_name)


last_name = None
count = 0


def namePresetByDate(preset_dict):
    global last_name, count
    now = datetime.now()
    name = now.strftime("%y%m%d-%H%M%S")
    if last_name == name:
        count += 1
        name = name + "-" + str(count)
    else:
        count = 0
    last_name = name
    print(name)
    preset_dict["data"]["meta"]["name"] = name


def namePreset(preset_dict):
    vowels = "aeiou"
    consonants = "bcdfghjklmnpqrstvwxyz"
    name = ""
    for _ in range(random.randint(2, 4)):
        if random.choice([True, False]):
            name += random.choice(vowels) + random.choice(consonants)
        else:
            name += random.choice(consonants) + random.choice(vowels)
    print(name)
    preset_dict["data"]["meta"]["name"] = name


def replaceWithPedalControllers(preset_dict, pedalnum):
    print("insert pedal")
    for i in range(mutate.NUM_PEDAL_PARAMS):
        mutate.setRandPedalParamAndRanges(preset_dict, pedalnum)


def generatePresetFromTemplate(presets_path, template_name, save_name):
    with open(os.path.join(presets_path, template_name), "r") as f:
        preset_dict = json.load(f)

        print("generating")
        generateFromSavedBlocks(preset_dict, "dsp0")
        generateFromSavedBlocks(preset_dict, "dsp1")

        mutate.seriesOrParallelPaths(preset_dict)
        namePresetByDate(preset_dict)

        while mutate.countParamControls(preset_dict) > 64:
            mutate.delRandomParamControl(preset_dict)

        replaceWithPedalControllers(preset_dict, 2)
        # replaceWithPedalControllers(preset_dict,"dsp1", 2)

        mutate.setLedColours(preset_dict)

        with open(os.path.join(presets_path, save_name), "w") as json_file:
            json.dump(preset_dict, json_file, indent=4)


num_snapshots = 8
fraction_change_block_states = 0.1
fraction_move = 0.1
fraction_swap = 0.15

# generatePresetFromTemplate(
#    "presets/test", "blocks/test", "LessOccSplit.hlx", "aGenerated.hlx"
# )


def generateSomePresets(num):
    for i in range(num):
        generatePresetFromTemplate(
            "presets/test",
            "LessOccSplit.hlx",
            "aGenerated" + str(i + 1) + ".hlx",
        )


def mutations(num):
    for i in range(num):
        mutate.mutatePresetSnapshotParams(
            "presets/test/240521-2016ded.hlx",
            6,
            "presets/test/240521-2016ded+" + str(i + 1) + ".hlx",
            0.1,
            fraction_change_block_states,
            fraction_move,
            fraction_swap,
        )


#generateSomePresets(5)
mutations(5)
# mutate.mutatePresetSnapshotParams("presets/test/memiyun_7.hlx", 7, "presets/test/memiyun_7+.hlx",0.1,fraction_change_block_states,fraction_move, fraction_swap)

# if __name__ == '__main__':
#     main()
#mutate probs: 2 amps on 1 dsp
# split disappears on dsp1
# cabs are in block positions - are they getting chosen, or not attached to amps properly? (might be when generating, not sure if geerating or mutating)