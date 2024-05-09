
import os
import json
import random
from copy import deepcopy

import mutate


#todo:
#load effects from category folders so there can be even (or other) chances of them being used
# swap blocks with ones from file
# make wahs frequently have pedal control - if exp1, then the default val can be randomly chosen


    
# load a template preset from a json file, return a dictionary
def loadPreset(presetFile):
    with open(os.path.expanduser(presetFile), "r") as f:
        preset_dict = json.load(f)
    return preset_dict


# return a random number biased between max and min
# from https://stackoverflow.com/questions/29325069/how-to-generate-random-numbers-biased-towards-one-value-in-a-range
def getRndBias(min, max, bias, influence):
    rnd = random.uniform(min, max) # random number in the min-max range
    mix = random.uniform(0,1) * influence # random normalized mix value
    return rnd * (1 - mix) + bias * mix  # Mix random with bias based on random mix


# if an amp is chosen
# choose a cab


def addCabs(preset_dict,dsp_name,blocks_path):
    # list all cabs in blocks folder
    cabs_file_list = []
    for filename in os.listdir(blocks_path+"/Cab/"):
        if filename.startswith("HD2_Cab"):
            cabs_file_list.append(filename)

    # keep track of how many cabs used
    cabs_used = 0

    amp_blocks_list = []
    for block_name in preset_dict["data"]["tone"][dsp_name]:
        if preset_dict["data"]["tone"][dsp_name][block_name]["@model"].startswith("HD2_Amp"):
            amp_blocks_list.append(block_name)

    for amp in amp_blocks_list:  
        # add a cab
        cab_name = "cab" + str(cabs_used)
        cabs_used += 1
        preset_dict["data"]["tone"][dsp_name][amp]["@cab"] = cab_name
        # load a random cab
        cab_dict = mutate.loadBlockParams(blocks_path+"/Cab/"+random.choice(cabs_file_list))
        # delete cab path and position, if they exist
        if "@path" in cab_dict["Defaults"]:
            del cab_dict["Defaults"]["@path"]
        if "@position" in cab_dict["Defaults"]:
            del cab_dict["Defaults"]["@position"]
        preset_dict["data"]["tone"][dsp_name][cab_name] = cab_dict["Defaults"]
        

def seriesOrParallelPaths(preset_dict):
    preset_dict["data"]["tone"]["dsp0"]["outputA"]["@output"] = random.randint(1,2)


# insert param keys into each snapshot in preset
def replaceParamKeys(preset_dict,dsp_name,blocks_path):
    num_amps = 0

    # add controller and dsp keys, if not present
    if "controller" not in preset_dict["data"]["tone"]:
        preset_dict["data"]["tone"]["controller"] = {}
        preset_dict["data"]["tone"]["controller"][dsp_name] = {}

    # set up shuffled block positions
    block_positions_path0 = [i for i in range(8)] # 8 per path
    random.shuffle(block_positions_path0)
    block_positions_path1 = [i for i in range(8)] # 8 per path
    random.shuffle(block_positions_path1)

    for block_name in preset_dict["data"]["tone"][dsp_name]:

        if block_name.startswith("block"): # or block_name.startswith("cab"): # cabs will be sorted with amps later, but cabs in amps will take an extra position at this step
            # load default params from file chosen randomly from blocks folder
            while True:
                block_dict = mutate.loadBlockParams(mutate.chooseBlockFile(blocks_path))
                # allow only one amp in dsp section of preset_dict
                if block_dict["Defaults"]["@model"].startswith("HD2_Amp"):
                     num_amps += 1                                          
                if not block_dict["Defaults"]["@model"].startswith("HD2_Amp") or num_amps < 2:
                    break
                    
            preset_dict["data"]["tone"][dsp_name][block_name] = block_dict["Defaults"]
            print("   loaded " + block_name + " " + block_dict["Defaults"]["@model"])
            
            path_num = random.randint(0,1)
            preset_dict["data"]["tone"][dsp_name][block_name]["@path"] = path_num
            if (path_num==0):
                preset_dict["data"]["tone"][dsp_name][block_name]["@position"] = block_positions_path0.pop()
            else:
                preset_dict["data"]["tone"][dsp_name][block_name]["@position"] = block_positions_path1.pop()

            preset_dict["data"]["tone"]["controller"][dsp_name][block_name] = block_dict["Ranges"]
            mutate.insertSnapshotParamsIntoPreset(preset_dict,dsp_name, block_name, block_dict)
        
        elif block_name.startswith("split"):
            split_dict = chooseSplit(preset_dict,dsp_name,blocks_path)
            preset_dict["data"]["tone"][dsp_name]["split"] = deepcopy(split_dict["Defaults"])
            preset_dict["data"]["tone"]["controller"][dsp_name][block_name] = split_dict["Ranges"]
            for snapshot_num in range(num_snapshots):
                snapshot_name = "snapshot" + str(snapshot_num)
                preset_dict["data"]["tone"][snapshot_name]["controllers"][dsp_name][block_name] = deepcopy(split_dict["SnapshotParams"])

            
               
    join_position = random.randint(6,8)
    split_position = random.randint(0,3)

    preset_dict["data"]["tone"][dsp_name]["join"]["@position"] = join_position
    preset_dict["data"]["tone"][dsp_name]["split"]["@position"] = split_position


def chooseSplit(preset_dict,dsp_name,blocks_path):
    # list all splits in split folder
    splits_file_list = ["HD2_AppDSPFlowSplitAB", "HD2_AppDSPFlowSplitDyn", "HD2_AppDSPFlowSplitXOver"]
    weights = [0.5, 0.25, 0.25]
    split_file = ''.join(random.choices(splits_file_list,weights,k=1))
    print(split_file)
    return mutate.loadBlockParams(blocks_path+"/Split/"+split_file+".json")







def chooseBlocksOnOrOff(preset_dict,dsp_name):
    for snapshot_num in range(num_snapshots):
        snapshot_name = "snapshot" + str(snapshot_num)
        if dsp_name in preset_dict["data"]["tone"][snapshot_name]["blocks"]:
            for block in preset_dict["data"]["tone"][snapshot_name]["blocks"][dsp_name]:
                if block.startswith("block") or block.startswith("cab"):
                    state = False
                    if (random.uniform(0,1) < .7): 
                        state = True
                    preset_dict["data"]["tone"][snapshot_name]["blocks"][dsp_name][block] = state






def generateFromSavedBlocks(preset_dict, dsp_name,blocks_path):
    print(dsp_name)
    replaceParamKeys(preset_dict,dsp_name,blocks_path)
    mutate.chooseParamValues(preset_dict,1.0)
    addCabs(preset_dict,dsp_name,blocks_path)
    chooseBlocksOnOrOff(preset_dict,dsp_name)



def namePreset(preset_dict):
    vowels = 'aeiou'
    consonants = 'bcdfghjklmnpqrstvwxyz'
    name = ''
    for _ in range(random.randint(2,4)):
        if random.choice([True, False]):
            name += random.choice(vowels)+random.choice(consonants)
        else:
            name += random.choice(consonants)+random.choice(vowels)
    print(name)
    preset_dict["data"]["meta"]["name"] = name
    
def replaceWithPedalControllers(preset_dict,dsp_name, pedalnum):
    print("insert pedal")
    # choose some blocks in dsp_name, and change controller 19 to controller 1 if the blocks and params exist
    #max_controllers = min(mutate.countParamControls(preset_dict,dsp_name),8)
    #for i in range(random.randint(0,max_controllers)) :
    for i in range(mutate.NUM_PEDAL_PARAMS) :
        randdsp, randblock = mutate.getRandDspAndBlock(preset_dict)
        if randblock != "none":
            randparam = mutate.getRandControllerParamNoBool(preset_dict,randdsp,randblock)
            if randparam != "none":
                print("replacing "+randdsp, randblock, randparam, pedalnum)
                # print(preset_dict["data"]["tone"]["controller"][dsp_name][randblock])
                # also choose random max and min values within the original limits
                pedalParam = preset_dict["data"]["tone"]["controller"][randdsp][randblock][randparam]
                pedalParam["@controller"] = pedalnum
                new_max = random.uniform(pedalParam["@min"],pedalParam["@max"])
                new_min = random.uniform(pedalParam["@min"],pedalParam["@max"])
                pedalParam["@max"] = new_max
                pedalParam["@min"] = new_min


def processPreset(presets_path,blocks_path, presetName):
    with open(os.path.join(presets_path, presetName), "r") as f:
        preset_dict = json.load(f)

        with open(os.path.join(presets_path, "TestBefore.hlx"), "w") as json_file:
            json.dump(preset_dict, json_file, indent=4)

        print("generating")
        generateFromSavedBlocks(preset_dict, "dsp0",blocks_path)
        generateFromSavedBlocks(preset_dict, "dsp1",blocks_path)
        seriesOrParallelPaths(preset_dict)
        namePreset(preset_dict)

        while mutate.countParamControls(preset_dict)>64:
                mutate.delRandomParamControl(preset_dict)
            
        replaceWithPedalControllers(preset_dict,"dsp0", 2)
        replaceWithPedalControllers(preset_dict,"dsp1", 2)
        
        mutate.setLedColours(preset_dict)

        with open(os.path.join(presets_path, "aTest.hlx"), "w") as json_file:
            json.dump(preset_dict, json_file, indent=4)



num_snapshots = 8
fraction_change_block_states = 0.1
fraction_move = 0.1
fraction_swap = 0.15
#processPreset("presets/test", "blocks/test","LessOccSplit.hlx")
def mutations(num):
    for i in range(num):
        mutate.mutatePresetSnapshotParams("presets/test/epbu_6.hlx", 6, "presets/test/epbu_6.hlx",0.1,fraction_change_block_states,fraction_move, fraction_swap)


#mutations(5)      
mutate.mutatePresetSnapshotParams("presets/test/epbu_6.hlx", 6, "presets/test/epbu_6+.hlx",0.1,fraction_change_block_states,fraction_move, fraction_swap)

# if __name__ == '__main__': 
#     main() 