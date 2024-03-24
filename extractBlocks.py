
# snapshots provide the max and min values for each parameter
# the snapshotted params need to be set by hand in hxedit (unless there's an automatic way to snapshot all params)
# this script extracts the params from the snapshots to a json file in the blocks folder

import sys, os, json

def extractBlocksFromPath(preset_dict, dspName, blocks_path):
	if dspName in preset_dict["data"]["tone"]["controller"]:
		print(dspName)
		for block_name in preset_dict["data"]["tone"]["controller"][dspName]:
			if block_name.startswith("block") or block_name.startswith("cab"):
				block_dict = {}
				block_dict["SnapshotParams"] = preset_dict["data"]["tone"]["snapshot0"]["controllers"][dspName][block_name]
				block_dict["Ranges"] = preset_dict["data"]["tone"]["controller"][dspName][block_name]
				block_dict["Defaults"] = preset_dict["data"]["tone"][dspName][block_name]
				block_filename = preset_dict["data"]["tone"][dspName][block_name]["@model"]
				with open(os.path.join(blocks_path,block_filename), "w") as json_file:
					json.dump(block_dict, json_file, indent=4)
				print(os.path.join(blocks_path,block_filename))


# This code defines a function that creates a directory 
# named "blocks" in the current working directory based on the provided folder and presetName, 
# loads a JSON file, and then calls a function to extract blocks from the JSON data 
# for "dsp0" and "dsp1" into the created directory.

def extractControls(preset_path, blocks_path,presetName):
	#b locks_path = os.path.join(preset_path,presetName,"blocks")
	# print(blocks_path)
	os.makedirs(blocks_path, exist_ok=True)
	with open(os.path.join(preset_path, presetName), "r") as f:
		preset_dict = json.load(f)
		extractBlocksFromPath(preset_dict, "dsp0", blocks_path)
		extractBlocksFromPath(preset_dict, "dsp1", blocks_path)


extractControls("presets/Setlist3-USER 1", "blocks/new", "Preset015-Deadshit Nation.hlx")
