
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

# return a random number biased between max and min
# from https://stackoverflow.com/questions/29325069/how-to-generate-random-numbers-biased-towards-one-value-in-a-range
def getRndBias(min, max, bias, influence):
    rnd = random.uniform(min, max) # random number in the min-max range
    mix = random.uniform(0,1) * influence # random normalized mix value
    return rnd * (1 - mix) + bias * mix  # Mix random with bias based on random mix


# if an amp is chosen
# choose a cab


def addCabs(preset_dict,dspName,blocks_path):
    # list all cabs in blocks folder
    cabs_file_list = []
    for filename in os.listdir(blocks_path+"/Cab/"):
        if filename.startswith("HD2_Cab"):
            cabs_file_list.append(filename)

    # keep track of how many cabs used
    cabs_used = 0

    amp_blocks_list = []
    for block_name in preset_dict["data"]["tone"][dspName]:
        if preset_dict["data"]["tone"][dspName][block_name]["@model"].startswith("HD2_Amp"):
            amp_blocks_list.append(block_name)

    for amp in amp_blocks_list:  
        # add a cab
        cab_name = "cab" + str(cabs_used)
        cabs_used += 1
        preset_dict["data"]["tone"][dspName][amp]["@cab"] = cab_name
        # load a random cab
        cab_dict = loadBlockParams(blocks_path+"/Cab/"+random.choice(cabs_file_list))
        # delete cab path and position, if they exist
        if "@path" in cab_dict["Defaults"]:
            del cab_dict["Defaults"]["@path"]
        if "@position" in cab_dict["Defaults"]:
            del cab_dict["Defaults"]["@position"]
        preset_dict["data"]["tone"][dspName][cab_name] = cab_dict["Defaults"]
        

def delRandomParam(preset_dict,dspName):
    blocks = []
    params = []

    for block_name in preset_dict["data"]["tone"][dspName]:
        if block_name.startswith("block"):
            blocks.append(block_name)
    randblock = random.choice(blocks)
    # print(randblock)

    for param in preset_dict["data"]["tone"][dspName][randblock]:
        #if not preset_dict["data"]["tone"][dspName][randblock][param].startswith("@"):
        if not param.startswith("@"):
            params.append(param)
    randparam = random.choice(params)
    # print(randparam)
    
    # remove the param from all snapshots
    for snapshot_num in range(num_snapshots):
        snapshot_name = "snapshot" + str(snapshot_num)
        if randparam in preset_dict["data"]["tone"][snapshot_name]["controllers"][dspName][randblock]:
            del preset_dict["data"]["tone"][snapshot_name]["controllers"][dspName][randblock][randparam]
 
    # remove param from controller
    if randparam in preset_dict["data"]["tone"]["controller"][dspName][randblock]:
        del preset_dict["data"]["tone"]["controller"][dspName][randblock][randparam]
    
    #print("deleted "+randblock+" "+randparam)

def countParams(preset_dict):
    num_params = 0
    for block_name in preset_dict["data"]["tone"]["snapshot0"]["controllers"]["dsp0"]:
        prototype_block = preset_dict["data"]["tone"]["controller"]["dsp0"][block_name]
        for parameter in prototype_block.items():
            num_params += 1
    for block_name in preset_dict["data"]["tone"]["snapshot0"]["controllers"]["dsp1"]:
        prototype_block = preset_dict["data"]["tone"]["controller"]["dsp1"][block_name]
        for parameter  in prototype_block.items():
            num_params += 1
    #print(num_params)
    return num_params



# insert param keys into each snapshot in preset
def replaceParamKeys(preset_dict,dspName,blocks_path):
    num_amps = 0

    # add controller and dsp keys, if not present
    if "controller" not in preset_dict["data"]["tone"]:
        preset_dict["data"]["tone"]["controller"] = {}
        preset_dict["data"]["tone"]["controller"][dspName] = {}

    # set up shuffled block positions
    block_positions_path0 = [i for i in range(8)] # 8 per path
    random.shuffle(block_positions_path0)
    block_positions_path1 = [i for i in range(8)] # 8 per path
    random.shuffle(block_positions_path1)

    for block_name in preset_dict["data"]["tone"][dspName]:

        if block_name.startswith("block"): # or block_name.startswith("cab"): # cabs will be sorted with amps later, but cabs in amps will take an extra position at this step
            # load default params from file chosen randomly from blocks folder
            while True:
                block_dict = loadBlockParams(blocks_path+"/"+chooseBlock(blocks_path))
                # allow only one amp in dsp section of preset_dict
                if block_dict["Defaults"]["@model"].startswith("HD2_Amp"):
                     num_amps += 1                                          
                if not block_dict["Defaults"]["@model"].startswith("HD2_Amp") or num_amps < 2:
                    break
                    
            preset_dict["data"]["tone"][dspName][block_name] = block_dict["Defaults"]
            print("   loaded " + block_name + " " + block_dict["Defaults"]["@model"])
            
            path_num = random.randint(0,1)
            preset_dict["data"]["tone"][dspName][block_name]["@path"] = path_num
            if (path_num==0):
                preset_dict["data"]["tone"][dspName][block_name]["@position"] = block_positions_path0.pop()
            else:
                preset_dict["data"]["tone"][dspName][block_name]["@position"] = block_positions_path1.pop()

            preset_dict["data"]["tone"]["controller"][dspName][block_name] = block_dict["Ranges"]

            # insert snapshot params into preset
            for snapshot_num in range(num_snapshots):
                snapshot_name = "snapshot" + str(snapshot_num)
                #print(snapshot_name)
                # following "if" line probably unnecessary
                if "controllers" not in preset_dict["data"]["tone"][snapshot_name]:
                    preset_dict["data"]["tone"][snapshot_name]["controllers"] = {}
                    print("added controllers")
                # following "if" line probably unnecessary
                if dspName not in preset_dict["data"]["tone"][snapshot_name]["controllers"]:
                    preset_dict["data"]["tone"][snapshot_name]["controllers"][dspName] = {}
                    print("added " + dspName)

                # add snapshot params from block_dict
                preset_dict["data"]["tone"][snapshot_name]["controllers"][dspName][block_name] = deepcopy(block_dict["SnapshotParams"])
                     
    join_position = random.randint(2,8)
    split_position = random.randint(1,join_position-1)

    preset_dict["data"]["tone"][dspName]["join"]["@position"] = join_position
    preset_dict["data"]["tone"][dspName]["split"]["@position"] = split_position


def chooseParamValues(preset_dict,dspName):
   # make random parameter values
    for snapshot_num in range(num_snapshots):
        snapshot_name = "snapshot" + str(snapshot_num)
        #print(snapshot_name)
        for block_name in preset_dict["data"]["tone"][snapshot_name]["controllers"][dspName]:
            # for control parameter max and mins
            prototype_block = preset_dict["data"]["tone"]["controller"][dspName][block_name]
            defaults_block = preset_dict["data"]["tone"][dspName][block_name]

            for parameter, v in prototype_block.items():
                #print(parameter)
                pmin = prototype_block[parameter]["@min"]
                pmax = prototype_block[parameter]["@max"]
                # do the right thing for the kind of parameter
                if isinstance(pmin, bool):
                    result = random.choice([True, False])
                elif (block_name.startswith("block") or block_name.startswith("cab")) and parameter == "Level":
                    lowest = ((pmax-pmin) * 0.2) + pmin
                    mode = ((pmax-pmin) * 0.8) + pmin # choose level from 0.2 to max, peak around 0.8 of max range
                    result = random.triangular(lowest, pmax, mode)
                elif parameter == "Time": # choose times at the short end  
                    mode = ((pmax-pmin) * 0.1) + pmin
                    result = random.triangular(pmin, pmax, mode)
                    #print("setting Time "+str(result))
                    #result = math.min(max, random.expovariate(0.5))
                elif parameter == "Mix": # choose mix around middle
                    lowest = ((pmax-pmin) * 0.2) + pmin # choose mix from 0.2 to max, peak around 0.5 of max range
                    mode = ((pmax-pmin) * 0.5) + pmin
                    result = random.triangular(lowest, pmax, mode)
                elif parameter == "Feedback": # choose feedback around middle
                    mode = ((pmax-pmin) * 0.5) + pmin
                    result = random.triangular(pmin, pmax, mode)
                elif (defaults_block["@model"].startswith("HD2_Reverb") or defaults_block["@model"].startswith("VIC") or defaults_block["@model"].startswith("Victoria")) and parameter == "Decay":
                    mode = ((pmax-pmin) * 0.05) + pmin
                    result = random.triangular(pmin, pmax, mode)
                    #result = min(pmax, random.expovariate(0.5))
                else:
                    result = random.uniform(pmin, pmax) # switch choices are rounded to nearest integer in helix
                preset_dict["data"]["tone"][snapshot_name]["controllers"][dspName][block_name][parameter]["@value"] = result


def combThruAmpsAndCabs(preset_dict,dspName):
    #make lists of Amps and Cabs
    cabs = []
    amps = []

    for block_name in preset_dict["data"]["tone"][dspName]:
        if block_name.startswith("cab"):
            cabs.append(block_name)
        if preset_dict["data"]["tone"][dspName][block_name]["@model"].startswith("HD2_Amp"):
            amps.append(block_name)

    random.shuffle(cabs)
    random.shuffle(amps)

    if amps:
        for amp in amps:
            if "@cab" in preset_dict["data"]["tone"][dspName][amp]:
                del preset_dict["data"]["tone"][dspName][amp]["@cab"] # remove exisiting cab
            if cabs:
                if random.randint(0,1) == 1:
                    preset_dict["data"]["tone"][dspName][amp]["@cab"] = cabs.pop()
                    del preset_dict["data"]["tone"][dspName][amp]["@cab"]["@path"]
                    del preset_dict["data"]["tone"][dspName][amp]["@cab"]["@position"]
    

def turnBlocksOnOrOff(preset_dict,dspName):
    for snapshot_num in range(num_snapshots):
        snapshot_name = "snapshot" + str(snapshot_num)
        if dspName in preset_dict["data"]["tone"][snapshot_name]["blocks"]:
            for block in preset_dict["data"]["tone"][snapshot_name]["blocks"][dspName]:
                if block.startswith("block") or block.startswith("cab"):
                    preset_dict["data"]["tone"][snapshot_name]["blocks"][dspName][block] = random.choice([True, False])


def setLedColours(preset_dict):
    for snapshot_num in range(num_snapshots):
        snapshot_name = "snapshot" + str(snapshot_num)
        # snapshot ledcolor
        preset_dict["data"]["tone"][snapshot_name]["@ledcolor"] = str(snapshot_num + 1)


def generateFromSavedBlocks(preset_dict, dspName,blocks_path):
    print(dspName)
    replaceParamKeys(preset_dict,dspName,blocks_path)
    chooseParamValues(preset_dict,dspName)
    addCabs(preset_dict,dspName,blocks_path)
    #combThruAmpsAndCabs(preset_dict,dspName)
    turnBlocksOnOrOff(preset_dict,dspName)

def processPreset(presets_path,blocks_path, presetName):
    with open(os.path.join(presets_path, presetName), "r") as f:
        preset_dict = json.load(f)

        with open(os.path.join(presets_path, "TestBefore.hlx"), "w") as json_file:
            json.dump(preset_dict, json_file, indent=4)

        print("generating")
        generateFromSavedBlocks(preset_dict, "dsp0",blocks_path)
        generateFromSavedBlocks(preset_dict, "dsp1",blocks_path)

        while countParams(preset_dict)>64:
            if random.randint(0,1) == 1:
                delRandomParam(preset_dict, "dsp0")
            else:
                delRandomParam(preset_dict, "dsp1")
            
        setLedColours(preset_dict)

        with open(os.path.join(presets_path, "aTest.hlx"), "w") as json_file:
            json.dump(preset_dict, json_file, indent=4)

num_snapshots = 8
processPreset("presets/test", "blocks/test","LessOccupied.hlx")