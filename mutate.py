from copy import deepcopy
import json
import random
import os

num_snapshots = 8
num_slots_per_dsp = 16
NUM_PEDAL_PARAMS = 16

def countNumControllersSetTo2(preset_dict):
    count = 0
    for dsp_name in ["dsp0", "dsp1"]:
        for block_name in preset_dict["data"]["tone"]["controller"][dsp_name]:
            if preset_dict["data"]["tone"]["controller"][dsp_name][block_name] == 2:
                count += 1
    return count


def chooseParamValuesForOneBlock(preset_dict, snapshot_num, dsp_name, block_name, fraction_new):
    snapshot_name = "snapshot" + str(snapshot_num)
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
            #print("setting Time, max "+str(pmax),str(result))
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
                if isinstance(result, bool):
                    defaults_block[parameter] = result
                else:
                    prev_result = defaults_block[parameter]
                    fraction_prev = 1.0-fraction_new
                    result_mix = result*fraction_new + prev_result*fraction_prev
                    result_mix_constrained = max(pmin, min(result_mix, pmax))
                    defaults_block[parameter] = result_mix_constrained
                    #print(pmin, pmax, prev_result, result_mix_constrained)


def chooseParamValues(preset_dict, fraction_new): #fraction_new is 0.0 to 1.0
   # make random parameter values
    for snapshot_num in range(num_snapshots):
        snapshot_name = "snapshot" + str(snapshot_num)
        #print(snapshot_name)
        for dsp_name in ["dsp0", "dsp1"]:
            for block_name in preset_dict["data"]["tone"][snapshot_name]["controllers"][dsp_name]:
                # for control parameter max and mins
               chooseParamValuesForOneBlock(preset_dict, snapshot_num, dsp_name, block_name, 1.0)

def countParamControls(preset_dict):
    num_params = 0
    for dsp_name in ["dsp0", "dsp1"]:
        for block_name in preset_dict["data"]["tone"]["controller"][dsp_name]:
            if block_name.startswith("block"):
                #print("counting params in "+block_name)
                for parameter in preset_dict["data"]["tone"]["controller"][dsp_name][block_name]: #.items():
                    num_params += 1
                    #print("counted "+parameter,num_params)
    return num_params


def setLedColours(preset_dict):
    for snapshot_num in range(num_snapshots):
        snapshot_name = "snapshot" + str(snapshot_num)
        # snapshot ledcolor
        preset_dict["data"]["tone"][snapshot_name]["@ledcolor"] = str(snapshot_num + 1)


def getRandDspAndBlock(preset_dict):
    # returns a random block, or "none" if there are no blocks
    dsp_names = ["dsp0","dsp1"]
    found_blocks = []
    for dsp_name in dsp_names:
        for block_name in preset_dict["data"]["tone"]["controller"][dsp_name]:
            found_blocks.append((dsp_name,block_name))
    rand_dsp_and_block = ["none", "none"]
    if len(found_blocks)>0:
        rand_dsp_and_block = random.choice(found_blocks)
    return rand_dsp_and_block


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


def getRandControllerParamNoBool(preset_dict,dsp_name,block):
    # returns a random param (but not one with a boolean value), or "none" if there are no params
    #print("getRandControllerParamNoBool for "+dsp_name+" "+block)
    params = []
    for param in preset_dict["data"]["tone"]["controller"][dsp_name][block]:
        if not isinstance(preset_dict["data"]["tone"]["controller"][dsp_name][block][param]["@min"], bool):
            params.append(param)
            #print("append to getRandControllerParamNoBool choices " +param)
    randparam = "none"
    if len(params) > 0:
        randparam = random.choice(params)
    return randparam


def delRandomParamControl(preset_dict):
    #global num_snapshots
    # delete a param if the random choice exists
    randdsp, randblock = getRandDspAndBlock(preset_dict)
    if randblock != "none":
        randparam = getRandControllerParam(preset_dict,randdsp,randblock)
        if randparam != "none":
            # remove the param from all snapshots
            for snapshot_num in range(num_snapshots):
                snapshot_name = "snapshot" + str(snapshot_num)
                if randparam in preset_dict["data"]["tone"][snapshot_name]["controllers"][randdsp][randblock]:
                    del preset_dict["data"]["tone"][snapshot_name]["controllers"][randdsp][randblock][randparam]
        
            # remove param from controller
            if randparam in preset_dict["data"]["tone"]["controller"][randdsp][randblock]:
                del preset_dict["data"]["tone"]["controller"][randdsp][randblock][randparam]
    
    #print("deleted "+randblock+" "+randparam)


def changeSomePedalControllers(preset_dict, pedalnum, change_fraction):
    #global num_snapshots
    #get a list of params with pedal control (controller number 2)
    pedal_block_params = []
    for dsp_name in ["dsp0", "dsp1"]:
        for block in preset_dict["data"]["tone"]["controller"][dsp_name]:
            if block.startswith("block"):
                for param in preset_dict["data"]["tone"]["controller"][dsp_name][block]:
                    if preset_dict["data"]["tone"]["controller"][dsp_name][block][param]["@controller"] == 2:
                        pedal_block_params.append([dsp_name,block,param]) 
    #choose a block,param pair
    random_index = random.randint(0, len(pedal_block_params) - 1)
    dsp_name, block, param = pedal_block_params[random_index]
    if (random.uniform(0,1) < change_fraction):
        # set control to snapshot
        print("unsetting pedal for "+dsp_name, block, param, pedalnum)
        preset_dict["data"]["tone"]["controller"][dsp_name][block][param]["@controller"] = 19 # snapshot control
        # set another param to pedalnum
        randdsp,randblock = getRandDspAndBlock(preset_dict)
        if randblock != "none":
            randparam = getRandControllerParamNoBool(preset_dict,randdsp,randblock)
            if randparam != "none":
                print("setting pedal for "+randdsp, randblock, randparam, pedalnum)
                pedalParam = preset_dict["data"]["tone"]["controller"][randdsp][randblock][randparam]
                pedalParam["@controller"] = pedalnum
                new_max = random.uniform(pedalParam["@min"],pedalParam["@max"])
                new_min = random.uniform(pedalParam["@min"],pedalParam["@max"])            
                # set new random max and min values within the original limits
                pedalParam["@max"] = new_max
                pedalParam["@min"] = new_min


def chooseParamValueAround(mean, pmin, pmax):
    range = pmax-pmin
    sigma=range/4
    p = random.normalvariate(mean,sigma)
    while not (pmin <= p <= pmax):
        p = random.normalvariate(mean,sigma)
    return p
  

def copySnapshot(preset_dict, snapshot_src, snapshot_dst):
    preset_dict["data"]["tone"][snapshot_dst] = deepcopy(preset_dict["data"]["tone"][snapshot_src])

def copySnapshotToAll(preset_dict, snapshot_src):
    #global num_snapshots
    for snapshot_num in range(num_snapshots):
        snapshot_dst = "snapshot" + str(snapshot_num)
        if snapshot_dst != snapshot_src:
            copySnapshot(preset_dict, snapshot_src, snapshot_dst)


def changeBlockStates(preset_dict, change_fraction):
    #global num_snapshots
    for snapshot_num in range(num_snapshots):
        snapshot_name = f"snapshot{snapshot_num}"

        for dsp_name in ["dsp0", "dsp1"]:
            if dsp_name in preset_dict["data"]["tone"][snapshot_name]["blocks"]:
                for block_name in preset_dict["data"]["tone"][snapshot_name]["blocks"][dsp_name]:
                    if block_name.startswith(("block", "cab")):
                        if random.uniform(0, 1) < change_fraction:  # change state
                            current_state = preset_dict["data"]["tone"][snapshot_name]["blocks"][dsp_name][block_name]
                            new_state = not current_state
                            preset_dict["data"]["tone"][snapshot_name]["blocks"][dsp_name][block_name] = new_state
                            print(f"{snapshot_name} changed state of {dsp_name} {block_name} from {current_state} to {new_state}")


def findUnusedBlockNameInDsp(preset_dict, dsp_name):
    for i in range(16):
        new_block_name = "block"+str(i)
        if new_block_name not in preset_dict["data"]["tone"][dsp_name]:
            break
    return new_block_name


def mutateBlockPositions(preset_dict, fraction_move, fraction_swap):
    dsp_names = ["dsp0","dsp1"]

    # find block positions
    found_dsp_path_pos = []
    for dsp_name in dsp_names:
        for block_name in preset_dict["data"]["tone"][dsp_name]:
            block_dict = preset_dict["data"]["tone"][dsp_name][block_name]
            if block_name.startswith("block"):
                found_dsp_path_pos.append([dsp_name, block_dict["@path"],block_dict["@position"]])
    
    #print(found_dsp_path_pos)

    # find vacant positions
    vacant_dsp_path_pos = []
    for dsp_name in dsp_names:
        for path in (0,1):
            for pos in range(8): # slots per path
                if [dsp_name,path,pos] not in found_dsp_path_pos:
                    vacant_dsp_path_pos.append([dsp_name,path,pos])

    #print(vacant_dsp_path_pos)

    dsp_blockname_to_dsp_path_pos = []
    for dsp_name in dsp_names:
        for block_name in preset_dict["data"]["tone"][dsp_name]:
            if block_name.startswith("block"):
                chance = random.uniform(0,1) 
                if chance < fraction_move:
                    from_path = preset_dict["data"]["tone"][dsp_name][block_name]["@path"]
                    from_position = preset_dict["data"]["tone"][dsp_name][block_name]["@position"]
                    # choose a vacant position from vacant_dsp_path_pos[]
                    random_index = random.randint(0, len(vacant_dsp_path_pos) - 1)
                    new_dsp_path_position = vacant_dsp_path_pos[random_index]
                    vacant_dsp_path_pos.remove(new_dsp_path_position)  # remove it from list of vacant positions
                    vacant_dsp_path_pos.append([dsp_name, from_path, from_position])
                    dsp_blockname_to_dsp_path_pos.append([dsp_name,block_name, new_dsp_path_position])
                    
    #print(dsp_blockname_to_dsp_path_pos)
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
           
        preset_dict["data"]["tone"]["controller"][to_dsp][new_block_name] = preset_dict["data"]["tone"]["controller"][from_dsp].pop(block_name)
        
        for snapshot_num in range(num_snapshots):
            snapshot_name = "snapshot" + str(snapshot_num)
            preset_dict["data"]["tone"][snapshot_name]["blocks"][to_dsp][new_block_name] = preset_dict["data"]["tone"][snapshot_name]["blocks"][from_dsp].pop(block_name)

        print("Moved", from_dsp, block_name, from_path, from_position,
              "to", to_dsp, new_block_name, to_path, to_position)


# replace block default params with extracted block params, given blockNumber and dsp_name
def replaceBlockDefaultParams(block_dict,preset_dict,block_num,dsp_name):
    preset_dict["data"]["tone"][dsp_name]["block"+str(block_num)] = block_dict["Defaults"]


# load extracted block parameters from a json file, return a dictionary
def loadBlockParams(block_filename):
    with open(os.path.expanduser(block_filename), "r") as f:
        block_dict = json.load(f)
    return block_dict


def chooseBlockFile(blocks_path="blocks/test"):
    block_folders = [f for f in os.listdir(blocks_path) if os.path.isdir(os.path.join(blocks_path, f)) and f not in ["Cab", "Split"]]
    folder = random.choice(block_folders)
    blocks_path = os.path.join(blocks_path, folder)
    block_files = [f for f in os.listdir(blocks_path) if os.path.isfile(os.path.join(blocks_path, f))]
    filename = os.path.join(blocks_path, random.choice(block_files))
    print(filename)
    return filename


def insertSnapshotParamsIntoPreset(preset_dict,dsp_name, block_name, new_block_dict):
    for snapshot_num in range(num_snapshots):
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
        preset_dict["data"]["tone"][snapshot_name]["controllers"][dsp_name][block_name] = deepcopy(new_block_dict["SnapshotParams"])


def swapBlocksFromFile(preset_dict, change_fraction):
    for dsp_name in ["dsp0", "dsp1"]:
        for block_name in preset_dict["data"]["tone"][dsp_name]:
            if block_name.startswith("block"):
                if random.uniform(0, 1) < change_fraction:  # change state
                    # replace this block with a random one from file
                    print("swapping block from file")
                    path = preset_dict["data"]["tone"][dsp_name][block_name]["@path"]
                    pos = preset_dict["data"]["tone"][dsp_name][block_name]["@position"]
                    new_block_dict = loadBlockParams(chooseBlockFile())
                    preset_dict["data"]["tone"][dsp_name][block_name] = new_block_dict["Defaults"]
                    preset_dict["data"]["tone"][dsp_name][block_name]["@path"] = path
                    preset_dict["data"]["tone"][dsp_name][block_name]["@position"] = pos
                    insertSnapshotParamsIntoPreset(preset_dict,dsp_name, block_name, new_block_dict)
                    preset_dict["data"]["tone"]["controller"][dsp_name][block_name] = new_block_dict["Ranges"]
                    for snapshot_num in range(num_snapshots):
                        chooseParamValuesForOneBlock(preset_dict, snapshot_num, dsp_name, block_name, 1.0)
                    # add pedal controls to replace any lost from the block replaced
                    for param in range(NUM_PEDAL_PARAMS  - countNumControllersSetTo2(preset_dict)):
                        # set control to pedal (controller number 2)
                        # choose a random parameter
                        randparam = random.choice(list(preset_dict["data"]["tone"]["controller"][dsp_name][block_name].keys()))
                        preset_dict["data"]["tone"]["controller"][dsp_name][block_name][randparam]["@controller"] = 2
                        
   
def mutateName(preset_dict):
    vowels = 'aeiou'
    consonants = 'bcdfghjklmnpqrstvwxyz'
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



def movePedalRanges(preset_dict):
    for dsp_name in ["dsp0", "dsp1"]:
        for block_or_split_name in preset_dict["data"]["tone"]["controller"][dsp_name]:
            for param in preset_dict["data"]["tone"]["controller"][dsp_name][block_or_split_name]:
                pedalParam = preset_dict["data"]["tone"]["controller"][dsp_name][block_or_split_name][param]
                if pedalParam["@controller"] == 2:
                    if not isinstance(pedalParam["@min"], bool): # don't want to pedal bools
                        # get original ranges from file
                        block_filename = preset_dict["data"]["tone"][dsp_name][block_or_split_name]["@model"]+".json"
                        block_folder = "blocks/test/"
                        for dirpath, dirnames, filenames in os.walk(block_folder):
                            #print(dirpath,dirnames, filenames)
                            if block_filename in filenames:
                                block_folder = dirpath+"/"
                                break
                        #print(block_folder+block_filename)
                        block_dict = loadBlockParams(block_folder+block_filename)
                        pmin = block_dict["Ranges"][param]["@min"]
                        pmax = block_dict["Ranges"][param]["@max"]
                        #print(pedalParam["@min"], pmin, pmax)
                        new_min = chooseParamValueAround(pedalParam["@min"], pmin, pmax) #(mean, pmin, pmax)
                        new_max = chooseParamValueAround(pedalParam["@max"], pmin, pmax)
                        pedalParam["@min"] = new_min
                        pedalParam["@max"] = new_max

                        
                        
#  maybe don't pedal booleans
# def changeSomePedalRanges(preset_dict,change_fraction):
#     for i in range(countParamControls(preset_dict)) :
#         if (random.uniform(0,1) < change_fraction): # or change them all by gauss? see below
#             randdsp,randblock = getRandDspAndBlock(preset_dict)
#             if randblock != "none":
#                 randparam = getRandControllerParam(preset_dict,randdsp,randblock)
#                 if randparam != "none":
#                     pedalParam = preset_dict["data"]["tone"]["controller"][randdsp][randblock][randparam]
#                     if pedalParam["@controller"] == 2:
#                         if isinstance(pedalParam["@min"], bool):
#                             p = [True, False]
#                             random.shuffle(p)
#                             new_max = p.pop()
#                             new_min = p.pop()
#                         else:
                            
#                             #sort this out - maybe use gaussian distribution or new uniform rand within default max and min
#                             new_max = random.uniform(pedalParam["@min"],pedalParam["@max"])*change_fraction
#                             new_min = random.uniform(pedalParam["@min"],pedalParam["@max"])*change_fraction
#                         pedalParam["@max"] = new_max
#                         pedalParam["@min"] = new_min
                        

def mutateSnapshot(preset_dict, snapshot_src_num,fraction_new,fraction_change_block_states,fraction_move, fraction_swap):
    mutateName(preset_dict)
    snapshot_src_name = "snapshot" + str(snapshot_src_num)
    copySnapshotToAll(preset_dict, snapshot_src_name)
    # change param values in all snapshots
    chooseParamValues(preset_dict,fraction_new)
    changeBlockStates(preset_dict, fraction_change_block_states)

    changeSomePedalControllers(preset_dict, 2, 0.5)
    movePedalRanges(preset_dict)
    mutateBlockPositions(preset_dict, fraction_move, fraction_swap)
    swapBlocksFromFile(preset_dict, 0.1)
    # sometimes change some split types
    # sometimes change series or parallel
    setLedColours(preset_dict)
    
def mutatePresetSnapshotParams(preset_filename, snapshot_num, new_preset_filename, fraction_new,fraction_change_block_states, fraction_move, fraction_swap):
    with open(preset_filename, "r") as f:
        preset_dict = json.load(f)
        mutateSnapshot(preset_dict, snapshot_num,fraction_new,fraction_change_block_states,fraction_move, fraction_swap)
        with open(new_preset_filename, "w") as f:
            json.dump(preset_dict, f, indent=4) 

