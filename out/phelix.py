import sys, os, json, random

# preset_string = '{"data":,
# "meta":,
# "name": "TestPreset",
# "application" : "HX Edit",
# "build_sha" : "ec7605f",
# "modifieddate" : 1679354818,
# "appversion" : 55640064
# }'

def makehlx():
	with open(os.path.expanduser('SimpleExample.hlx'), 'r') as f:
		preset_dict = json.load(f)
		# print(json.dumps(preset_string, indent = 4))
		# print(preset_dict.get('data'))	
		# print(preset_dict['data']['meta'])
		# print(preset_dict.get('data').get('meta'))
		# print('Items:', list(preset_dict.items()))
		# print('Keys:',list(preset_dict.keys()))
		# print('Values:',list(preset_dict.values()))

		# print(preset_dict['data']['tone']["snapshot7"])
		# snapshot7 = preset_dict['data']['tone']["snapshot7"]
		target_block = 'block1'
		for snapshot_num in range(8):
			target_snapshot = 'snapshot' + str(snapshot_num)

		# target = preset_dict['data']['tone']["dsp0"]["block0"]["Gain"]
		# target = preset_dict['data']['tone']["dsp0"][target_block]["Gain"]
		# target = preset_dict['data']['tone']["dsp0"][target_block]
		
		# target = preset_dict['data']['tone'][target_snapshot]['controllers']['dsp0']['block1']['LowGain']['@value']
			lowgain = random.randint(-120,120)/10
			preset_dict['data']['tone'][target_snapshot]['controllers']['dsp0']['block1']['LowGain']['@value'] = lowgain
			midgain = random.randint(-120,120)/10
			preset_dict['data']['tone'][target_snapshot]['controllers']['dsp0']['block1']['MidGain']['@value'] = midgain
			highgain = random.randint(-120,120)/10
			preset_dict['data']['tone'][target_snapshot]['controllers']['dsp0']['block1']['HighGain']['@value'] = highgain
			midfreq = random.randint(125,4000)
			preset_dict['data']['tone'][target_snapshot]['controllers']['dsp0']['block1']['MidFreq']['@value'] = midfreq
	
		# print(target)
		# target += 1
		# preset_dict['data']['tone']["dsp0"]["block0"]["Gain"] = target

	with open(os.path.expanduser('preset.hlx'), 'w') as json_file:
		json.dump(preset_dict, json_file, indent = 4)

makehlx()
