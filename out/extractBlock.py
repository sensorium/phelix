import sys, os, json, random, math

def makehlx():
	with open(os.path.expanduser('2blocks.hlx'), 'r') as f:
		preset_dict = json.load(f)

		# prototype_block = preset_dict['data']['tone']['controller']['dsp0']['block0']

		for snapshot_num in range(8):
			target_snapshot = 'snapshot' + str(snapshot_num)
			# snapshot ledcolor
			preset_dict['data']['tone'][target_snapshot]['@ledcolor'] = str(snapshot_num+1)
			
			for key in preset_dict['data']['tone']['controller']['dsp0']:
				if key.startswith("block"):
					blockname = key
					print(blockname)

					prototype_block = preset_dict['data']['tone']['controller']['dsp0'][blockname]
					# block to edit
					snapshot_block = preset_dict['data']['tone'][target_snapshot]['controllers']['dsp0'][blockname]

					for parameter, v in prototype_block.items():
						min = prototype_block[parameter]['@min']
						max = prototype_block[parameter]['@max']
						snapshot_block[parameter]['@value'] = random.uniform(min,max)
			
		with open(os.path.expanduser('Test.hlx'), 'w') as json_file:
			json.dump(preset_dict, json_file, indent = 4)

makehlx()