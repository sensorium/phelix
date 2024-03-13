# todo: test 2 paths, dsp0 and dsp1 is easiest, then within a path
#  try with a loop send/return
# see how switches end up - make sure "1" gets selected if there's a 0/1 choice
# does the helix round numbers or truncate them when suing switches rather than continuous numbers?
# how to tell automatically which controls do what ?
#  build a library of blocks for algorithmic combining
# generate small variations on a preset's existng settings
# a tool to copy command centre sections between presets


import sys, os, json, random, math
from collections import defaultdict
from copy import deepcopy

def makehlx():
	preset = "EQ"
	with open(os.path.expanduser("presets/"+preset+".hlx"), "r") as f:
		preset_dict = json.load(f)
		
		# build_preset_dict = defaultdict()
		# for key, value in preset_dict.items():
		# 		build_preset_dict[key] = value

		# set up to shuffle block positions
		block_positions = [i for i in range(8)] # only use 7 positions, leave 8 for vol pedal
		random.shuffle(block_positions)
		print(block_positions)
		
		# add controller and dsp0 keys
		preset_dict["data"]["tone"]["controller"] = {}
		preset_dict["data"]["tone"]["controller"]["dsp0"] = {}

		for block_name in preset_dict["data"]["tone"]["dsp0"]:
			if block_name.startswith("block"):
				print(block_name)
				# shuffle blocks
				if preset_dict["data"]["tone"]["dsp0"][block_name]["@model"] != "HD2_VolPanVol":
					preset_dict["data"]["tone"]["dsp0"][block_name]["@position"] = block_positions.pop()
				# load snapshot params from file
				model_name = preset_dict["data"]["tone"]["dsp0"][block_name]["@model"]
				print(model_name)
				with open(os.path.expanduser("blocks/"+model_name), "r") as json_file:
					block_dict = json.load(json_file)
					
					# put ranges section into preset
					preset_dict["data"]["tone"]["controller"]["dsp0"][block_name] = block_dict["Ranges"]

				# put params into each snapshot in preset
				for snapshot_num in range(8):
					snapshot_name = "snapshot" + str(snapshot_num)
					preset_dict["data"]["tone"][snapshot_name]["controllers"] = {}
					preset_dict["data"]["tone"][snapshot_name]["controllers"]["dsp0"] = {}
					preset_dict["data"]["tone"][snapshot_name]["controllers"]["dsp0"][block_name] = {}
					preset_dict["data"]["tone"][snapshot_name]["controllers"]["dsp0"][block_name] = deepcopy(block_dict["SnapshotParams"])

		for snapshot_num in range(7):
			snapshot_name = "snapshot" + str(snapshot_num)
			# snapshot ledcolor
			preset_dict["data"]["tone"][snapshot_name]["@ledcolor"] = str(snapshot_num + 1)
			print(snapshot_num)
			for block_name in preset_dict["data"]["tone"]["controller"]["dsp0"]:	
					
				# for control parameter max and mins
				prototype_block = preset_dict["data"]["tone"]["controller"]["dsp0"][block_name]
				print(block_name)
				# block to edit
				snapshot_block = preset_dict["data"]["tone"][snapshot_name]["controllers"]["dsp0"][block_name]

				for parameter, v in prototype_block.items():
					min = prototype_block[parameter]["@min"]
					max = prototype_block[parameter]["@max"]
					# do the right thing for the kind of parameter
					if isinstance(min, bool):
						result = random.choice([True,False])
					elif min == 0 and max > 1:
						result = random.randint(min, max)
					else:
						result = random.uniform(min, max)
					preset_dict["data"]["tone"][snapshot_name]["controllers"]["dsp0"][block_name][parameter]["@value"] = result
					# snapshot_block[parameter]["@value"] = result
					print(preset_dict["data"]["tone"][snapshot_name]["controllers"]["dsp0"][block_name][parameter]["@value"])

		with open(os.path.expanduser("presets/Test.hlx"), "w") as json_file:
			json.dump(preset_dict, json_file, indent=4)
			print(json.dumps(preset_dict, indent=2))
		# with open(os.path.expanduser("presets/TestBuilt.hlx"), "w") as json_file:
		# 	json.dump(build_preset_dict, json_file, indent=4)

makehlx()
