
import sys, os, json, random, math
from collections import defaultdict
from copy import deepcopy

# load a template preset from a json file, return a dictionary
def loadPreset(presetFile):
    with open(os.path.expanduser(presetFile), "r") as f:
        preset_dict = json.load(f)
    return preset_dict

# load extracted block parameters from a json file, return a dictionary
def loadBlockParams(blocksFile):
    with open(os.path.expanduser(blocksFile), "r") as f:
        block_dict = json.load(f)
    return block_dict

# replace block default params with extracted block params, given blockNumber and dspName
def replaceBlockDefaultParams(block_dict,preset_dict,block_num,dspName):
    preset_dict["data"]["tone"][dspName]["block"+str(block_num)] = block_dict["Defaults"]


def chooseBlock(blocks_path):
    block_files = [f for f in os.listdir(blocks_path) if os.path.isfile(os.path.join(blocks_path, f))]
    return random.choice(block_files)

# insert param keys into each snapshot in preset
def replaceParamKeys(preset_dict,dspName,blocks_path):
    for block_name in preset_dict["data"]["tone"][dspName]:
        if block_name.startswith("block") or block_name.startswith("cab"):
            # delete exisiting block 
            # del preset_dict["data"]["tone"][dspName][block_name]

            # delete contents of block_name
            # preset_dict["data"]["tone"][dspName][block_name] = {}

            # load default params from file chosen randomly from blocks folder
            block_dict = loadBlockParams(blocks_path+"/"+chooseBlock(blocks_path))
            preset_dict["data"]["tone"][dspName][block_name] = block_dict["Defaults"]
            # insert snapshot params into preset
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
                # delete exisitng snapshot params
                #if block_name in preset_dict["data"]["tone"][snapshot_name]["controllers"][dspName]:
                #    del preset_dict["data"]["tone"][snapshot_name]["controllers"][dspName][block_name]

                # add snapshot params from block_dict
                preset_dict["data"]["tone"][snapshot_name]["controllers"][dspName][block_name] = deepcopy(block_dict["SnapshotParams"])
                print("   loaded " + block_name + " " + preset_dict["data"]["tone"][dspName][block_name]["@model"])


def chooseParamValues(preset_dict,dspName):
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

def setLedColours(preset_dict):
    for snapshot_num in range(8):
        snapshot_name = "snapshot" + str(snapshot_num)
        # snapshot ledcolor
        preset_dict["data"]["tone"][snapshot_name]["@ledcolor"] = str(snapshot_num + 1)


def generateFromSavedBlocks(preset_dict, dspName,blocks_path):
    print(dspName)
    replaceParamKeys(preset_dict,dspName,blocks_path)
    #chooseParamValues(preset_dict,dspName)
    #turnBlocksOnOrOff(preset_dict,dspName)

def processPreset(presets_path,blocks_path, presetName):
    with open(os.path.join(presets_path, presetName+".hlx"), "r") as f:
        preset_dict = json.load(f)

        generateFromSavedBlocks(preset_dict, "dsp0",blocks_path)
        generateFromSavedBlocks(preset_dict, "dsp1",blocks_path)
        setLedColours(preset_dict)

        with open(os.path.join(presets_path, "Test.hlx"), "w") as json_file:
            json.dump(preset_dict, json_file, indent=4)

processPreset("presets/others", "blocks/new","Distortions1")