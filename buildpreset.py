
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

# replace block default params with extracted block params, given blockNumber and dsp_name
def replaceBlockDefaultParams(block_dict,preset_dict,block_num,dsp_name):
    preset_dict["data"]["tone"][dsp_name]["block"+str(block_num)] = block_dict["Defaults"]


def chooseBlockFile(blocks_path):
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
        cab_dict = loadBlockParams(blocks_path+"/Cab/"+random.choice(cabs_file_list))
        # delete cab path and position, if they exist
        if "@path" in cab_dict["Defaults"]:
            del cab_dict["Defaults"]["@path"]
        if "@position" in cab_dict["Defaults"]:
            del cab_dict["Defaults"]["@position"]
        preset_dict["data"]["tone"][dsp_name][cab_name] = cab_dict["Defaults"]
        



def getRandControllerBlock(preset_dict,dsp_name):
    # returns a random block, or "none" if there are no blocks
    blocks = []
    for block_name in preset_dict["data"]["tone"]["controller"][dsp_name]:
        blocks.append(block_name)
    randblock = "none"
    if len(blocks)>0:
        randblock = random.choice(blocks)
    return randblock

def getRandControllerParam(preset_dict,dsp_name,block):
    # returns a random param, or "none" if there are no params
    #print("getRandControllerParam for "+dsp_name+" "+block)
    params = []
    for param in preset_dict["data"]["tone"]["controller"][dsp_name][block]:
        params.append(param)
        #print("append to getRandControllerParam choices " +param)
    randparam = "none"
    if len(params) > 0:
        randparam = random.choice(params)
    return randparam


def delRandomParamControl(preset_dict,dsp_name):
# delete a param if the random choice exists
    randblock = getRandControllerBlock(preset_dict,dsp_name)
    if randblock != "none":
        randparam = getRandControllerParam(preset_dict,dsp_name,randblock)
        if randparam != "none":
            # remove the param from all snapshots
            for snapshot_num in range(num_snapshots):
                snapshot_name = "snapshot" + str(snapshot_num)
                if randparam in preset_dict["data"]["tone"][snapshot_name]["controllers"][dsp_name][randblock]:
                    del preset_dict["data"]["tone"][snapshot_name]["controllers"][dsp_name][randblock][randparam]
        
            # remove param from controller
            if randparam in preset_dict["data"]["tone"]["controller"][dsp_name][randblock]:
                del preset_dict["data"]["tone"]["controller"][dsp_name][randblock][randparam]
    
    #print("deleted "+randblock+" "+randparam)




def countParamControls(preset_dict,dsp_name):
    num_params = 0
    for block_name in preset_dict["data"]["tone"]["controller"][dsp_name]:
        if block_name.startswith("block"):
            #print("counting params in "+block_name)
            for parameter in preset_dict["data"]["tone"]["controller"][dsp_name][block_name]: #.items():
                num_params += 1
                #print("counted "+parameter,num_params)
    return num_params


def replaceWithPedalControllers(preset_dict,dsp_name, pedalnum):
    print("insert pedal")
    # choose some blocks in dsp_name, and change controller 19 to controller 1 if the blocks and params exist
    max_controllers = min(countParamControls(preset_dict,dsp_name),8)
    #for i in range(random.randint(0,max_controllers)) :
    for i in range(8) :
        randblock = getRandControllerBlock(preset_dict,dsp_name)
        if randblock != "none":
            randparam = getRandControllerParam(preset_dict,dsp_name,randblock)
            if randparam != "none":
                print("replacing "+dsp_name, randblock, randparam, pedalnum)
            # print(preset_dict["data"]["tone"]["controller"][dsp_name][randblock])
                pedalParam = preset_dict["data"]["tone"]["controller"][dsp_name][randblock][randparam]

                pedalParam["@controller"] = pedalnum
                if isinstance(pedalParam["@min"], bool):
                    p = [True, False]
                    random.shuffle(p)
                    new_max = p.pop()
                    new_min = p.pop()
                else:
                    new_max = random.uniform(pedalParam["@min"],pedalParam["@max"])
                    new_min = random.uniform(pedalParam["@min"],pedalParam["@max"])
                                
                # also choose random max and min values within the original limits
                pedalParam["@max"] = new_max
                pedalParam["@min"] = new_min


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
                block_dict = loadBlockParams(blocks_path+"/"+chooseBlockFile(blocks_path))
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

            # insert snapshot params into preset
            for snapshot_num in range(num_snapshots):
                snapshot_name = "snapshot" + str(snapshot_num)
                #print(snapshot_name)
                # following "if" line probably unnecessary
                if "controllers" not in preset_dict["data"]["tone"][snapshot_name]:
                    preset_dict["data"]["tone"][snapshot_name]["controllers"] = {}
                    print("added controllers")
                # following "if" line probably unnecessary
                if dsp_name not in preset_dict["data"]["tone"][snapshot_name]["controllers"]:
                    preset_dict["data"]["tone"][snapshot_name]["controllers"][dsp_name] = {}
                    print("added " + dsp_name)

                # add snapshot params from block_dict
                preset_dict["data"]["tone"][snapshot_name]["controllers"][dsp_name][block_name] = deepcopy(block_dict["SnapshotParams"])
        
        elif block_name.startswith("split"):
            split_dict = chooseSplit(preset_dict,dsp_name,blocks_path)
            preset_dict["data"]["tone"][dsp_name]["split"] = deepcopy(split_dict["Defaults"])
            preset_dict["data"]["tone"]["controller"][dsp_name][block_name] = split_dict["Ranges"]
            for snapshot_num in range(num_snapshots):
                snapshot_name = "snapshot" + str(snapshot_num)
                preset_dict["data"]["tone"][snapshot_name]["controllers"][dsp_name][block_name] = deepcopy(split_dict["SnapshotParams"])

            
               
    join_position = random.randint(3,8)
    split_position = random.randint(0,join_position-1)

    preset_dict["data"]["tone"][dsp_name]["join"]["@position"] = join_position
    preset_dict["data"]["tone"][dsp_name]["split"]["@position"] = split_position


def chooseSplit(preset_dict,dsp_name,blocks_path):
    # list all splits in split folder
    splits_file_list = []
    for filename in os.listdir(blocks_path+"/Split/"):
        if filename.startswith("HD2_AppDSPFlowSplit"):
            splits_file_list.append(filename)
    return loadBlockParams(blocks_path+"/Split/"+random.choice(splits_file_list))

        

def chooseParamValues(preset_dict,dsp_name):
   # make random parameter values
    for snapshot_num in range(num_snapshots):
        snapshot_name = "snapshot" + str(snapshot_num)
        #print(snapshot_name)
        for block_name in preset_dict["data"]["tone"][snapshot_name]["controllers"][dsp_name]:
            # for control parameter max and mins
            prototype_block = preset_dict["data"]["tone"]["controller"][dsp_name][block_name]
            defaults_block = preset_dict["data"]["tone"][dsp_name][block_name]

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
                    #mode = ((pmax-pmin) * 0.1) + pmin
                    #result = random.triangular(pmin, pmax, mode)
                    closerToOneForLowerNum = 0.95 + (0.75 - 0.95) * (pmax - 2) / (8 - 2)
                    result = min(pmax, random.expovariate(closerToOneForLowerNum))
                    print("setting Time, max "+str(pmax),str(result))
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
                preset_dict["data"]["tone"][snapshot_name]["controllers"][dsp_name][block_name][parameter]["@value"] = result
                # make defaults same as snapshot 0
                if (snapshot_num == 0) and (block_name.startswith("block") or block_name.startswith("cab") or block_name.startswith("split")) and (not parameter.startswith("@")):
                        defaults_block[parameter] = result



def turnBlocksOnOrOff(preset_dict,dsp_name):
    for snapshot_num in range(num_snapshots):
        snapshot_name = "snapshot" + str(snapshot_num)
        if dsp_name in preset_dict["data"]["tone"][snapshot_name]["blocks"]:
            for block in preset_dict["data"]["tone"][snapshot_name]["blocks"][dsp_name]:
                if block.startswith("block") or block.startswith("cab"):
                    state = False
                    if (random.uniform(0,1) < .7): 
                        state = True
                    preset_dict["data"]["tone"][snapshot_name]["blocks"][dsp_name][block] = state


def setLedColours(preset_dict):
    for snapshot_num in range(num_snapshots):
        snapshot_name = "snapshot" + str(snapshot_num)
        # snapshot ledcolor
        preset_dict["data"]["tone"][snapshot_name]["@ledcolor"] = str(snapshot_num + 1)


def generateFromSavedBlocks(preset_dict, dsp_name,blocks_path):
    print(dsp_name)
    replaceParamKeys(preset_dict,dsp_name,blocks_path)
    chooseParamValues(preset_dict,dsp_name)
    addCabs(preset_dict,dsp_name,blocks_path)
    turnBlocksOnOrOff(preset_dict,dsp_name)



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

        while (countParamControls(preset_dict,"dsp0")+countParamControls(preset_dict,"dsp1"))>64:
            if random.randint(0,1) == 1:
                delRandomParamControl(preset_dict, "dsp0")
            else:
                delRandomParamControl(preset_dict, "dsp1")
            
        replaceWithPedalControllers(preset_dict,"dsp0", 2)
        replaceWithPedalControllers(preset_dict,"dsp1", 2)
        
        setLedColours(preset_dict)

        with open(os.path.join(presets_path, "aTest.hlx"), "w") as json_file:
            json.dump(preset_dict, json_file, indent=4)

num_snapshots = 8
processPreset("presets/test", "blocks/test","LessOccSplit.hlx")