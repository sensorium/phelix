
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
	
def extractControls(folder, presetName):
	blocks_path = os.path.join(folder,presetName,"blocks")
	print(blocks_path)
	os.makedirs(blocks_path, exist_ok=True)
	with open(os.path.join(folder, presetName+".hlx"), "r") as f:
		preset_dict = json.load(f)
		extractBlocksFromPath(preset_dict, "dsp0", blocks_path)
		extractBlocksFromPath(preset_dict, "dsp1", blocks_path)


extractControls("presets", "coctow")
