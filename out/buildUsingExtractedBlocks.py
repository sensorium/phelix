# todo: test 2 paths, dsp0 and dsp1 is easiest, then within a path
#  try with a loop send/return
# see how switches end up - make sure "1" gets selected if there's a 0/1 choice
# does the helix round numbers or truncate them when suing switches rather than continuous numbers?
# how to tell automatically which controls do what ?
#  build a library of blocks for algorithmic combining
# generate small variations on a preset's existing settings
# a tool to copy command centre sections between presets

# this script is used to generate a preset from a template
# that has been extracted from an existing preset.
# it will shuffle block positions and load block params
# from file.

# further work will be to
# - generate a preset from a larger pool of extracted blocks which are held in a folder
# - insert signal path branches into the preset
# - ensure that the preset is likely to produce a sound
# - make sure the preset is valid
# - use both main signal paths and secondary signal paths in the same preset


import sys, os, json, random, math
from collections import defaultdict
from copy import deepcopy


def shufflePositions(preset_dict,dspName):
    # set up to shuffle block positions
    block_positions = [i for i in range(8)] # 8 per path, but up to 16 if secondary path...
    random.shuffle(block_positions)
    print(block_positions)
    # add controller and dsp0 keys, just once
    if "controller" not in preset_dict["data"]["tone"]:
        preset_dict["data"]["tone"]["controller"] = {}
        preset_dict["data"]["tone"]["controller"][dspName] = {}

    for block_name in preset_dict["data"]["tone"][dspName]:
        if block_name.startswith("block"): # don't shuffle cabs
            print(block_name)
            # shuffle blocks
            if (preset_dict["data"]["tone"][dspName][block_name]["@model"]!= "HD2_VolPanVol" ):
                preset_dict["data"]["tone"][dspName][block_name]["@position"] = block_positions.pop()

def loadBlockParams(blocks_path,preset_dict,dspName):
    for block_name in preset_dict["data"]["tone"][dspName]:
        if block_name.startswith("block") or block_name.startswith("cab"):    
            # load snapshot params from file
            model_name = preset_dict["data"]["tone"][dspName][block_name]["@model"]
            print(model_name)
            with open(os.path.join(blocks_path, model_name), "r") as json_file:
                block_dict = json.load(json_file)
                # put ranges section into preset
                preset_dict["data"]["tone"]["controller"][dspName][block_name] = block_dict["Ranges"]

def setLedColours(preset_dict):
    for snapshot_num in range(8):
        snapshot_name = "snapshot" + str(snapshot_num)
        # snapshot ledcolor
        preset_dict["data"]["tone"][snapshot_name]["@ledcolor"] = str(snapshot_num + 1)


def insertParamKeys(blocks_path,preset_dict,dspName):
    # put param keys into each snapshot in preset
    for snapshot_num in range(8):
        snapshot_name = "snapshot" + str(snapshot_num)
        print(snapshot_name)
        # following "if" line probably unnecessary
        if "controllers" not in preset_dict["data"]["tone"][snapshot_name]:
            preset_dict["data"]["tone"][snapshot_name]["controllers"] = {}
            print("added controllers")
        # following "if" line probably unnecessary
        if dspName not in preset_dict["data"]["tone"][snapshot_name]["controllers"]:
            preset_dict["data"]["tone"][snapshot_name]["controllers"][dspName] = {}
            print("added " + dspName)
        for block_name in preset_dict["data"]["tone"][dspName]:
            if block_name.startswith("block") or block_name.startswith("cab"):
                # load snapshot params from file
                model_name = preset_dict["data"]["tone"][dspName][block_name]["@model"]
                with open(os.path.join(blocks_path, model_name), "r") as json_file:
                    block_dict = json.load(json_file)
                    preset_dict["data"]["tone"][snapshot_name]["controllers"][dspName][block_name] = deepcopy(block_dict["SnapshotParams"])
                    print("   loaded " + model_name)

def chooseParams(preset_dict,dspName):
   # make random parameter values
    for snapshot_num in range(8):
        snapshot_name = "snapshot" + str(snapshot_num)
        print(snapshot_name)
        for block_name in preset_dict["data"]["tone"][snapshot_name]["controllers"][dspName]:
            print(block_name+" params set")
            # for control parameter max and mins
            prototype_block = preset_dict["data"]["tone"]["controller"][dspName][block_name]
            # block to edit
            snapshot_block = preset_dict["data"]["tone"][snapshot_name]["controllers"][dspName][block_name]

            for parameter, v in prototype_block.items():
                min = prototype_block[parameter]["@min"]
                max = prototype_block[parameter]["@max"]
                # do the right thing for the kind of parameter
                if isinstance(min, bool):
                    result = random.choice([True, False])
                # elif min == 0 and max > 1:
                #     result = random.randint(min, max)
                else:
                    result = random.uniform(min, max) # switch choices are rounded to int, so won't reach end values as often
                preset_dict["data"]["tone"][snapshot_name]["controllers"][dspName][block_name][parameter]["@value"] = result

def turnBlocksOnOrOff(preset_dict,dspName):
    for snapshot_num in range(8):
        snapshot_name = "snapshot" + str(snapshot_num)
        if dspName in preset_dict["data"]["tone"][snapshot_name]["blocks"]:
            for block in preset_dict["data"]["tone"][snapshot_name]["blocks"][dspName]:
                preset_dict["data"]["tone"][snapshot_name]["blocks"][dspName][block] = random.choice([True, False])


def randomiseBlocks(blocks_path, preset_dict, dspName):
    print(dspName)
    shufflePositions(preset_dict,dspName)  
    loadBlockParams(blocks_path,preset_dict,dspName)
    insertParamKeys(blocks_path,preset_dict,dspName)
    chooseParams(preset_dict,dspName)
    turnBlocksOnOrOff(preset_dict,dspName)

def chooseBlock(blocks_path):
    block_files = [f for f in os.listdir(blocks_path) if os.path.isfile(os.path.join(blocks_path, f))]
    return random.choice(block_files)

# WIP
def insertBlocks(blocks_path, preset_dict, dspName, numBlocks):
    for i in range(numBlocks):
        chosen_block = chooseBlock(blocks_path)

# WIP
def generateFromSavedBlocks(blocks_path, preset_dict, dspName):
    insertBlocks(blocks_path, preset_dict, dspName, 5)


def processPreset(folder, presetName):
    blocks_path = "blocks"
    with open(os.path.join(folder, presetName+".hlx"), "r") as f:
        preset_dict = json.load(f)

        setLedColours(preset_dict)
        generateFromSavedBlocks(blocks_path, preset_dict, "dsp0")
#        generateFromSavedBlocks(blocks_path, preset_dict, "dsp1")

        with open(os.path.join(folder, "Test.hlx"), "w") as json_file:
            json.dump(preset_dict, json_file, indent=4)


processPreset("presets", "Distortions1")
