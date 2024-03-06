
import sys, os, json

def replace(data, match, repl):
    if isinstance(data, dict):
        return {k: replace(v, match, repl) for k, v in data.items()}
    elif isinstance(data, list):
        return [replace(i, match, repl) for i in data]
    else:
        return repl if data == match else data


def extractControls():
	source_preset = "LuckyCountry"
	with open(os.path.expanduser("presets/WRS/"+source_preset+".hlx"), "r") as f:
		source_dict = json.load(f)
		
	dest_preset = "Vol"
	with open(os.path.expanduser("presets/WRS/"+source_preset+".hlx"), "r") as dest_f:
		dest_dict = json.load(dest_f)





		for item_name in preset_dict["data"]["tone"]["controller"]["dsp0"]:
			if item_name.startswith("block"):
				block_dict = {}
				block_dict["SnapshotParams"] = preset_dict["data"]["tone"]["snapshot0"]["controllers"]["dsp0"][item_name]
				block_dict["Ranges"] = preset_dict["data"]["tone"]["controller"]["dsp0"][item_name]
				block_filename = preset_dict["data"]["tone"]["dsp0"][item_name]["@model"]
				with open(os.path.expanduser("blocks/"+block_filename), "w") as json_file:
					json.dump(block_dict, json_file, indent=4)
				print(block_filename)

extractControls()
