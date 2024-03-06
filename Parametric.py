import sys, os, json, random

def makehlx():
	with open(os.path.expanduser('Parametric.hlx'), 'r') as f:
		preset_dict = json.load(f)

		target_block = 'block0'
		
		for snapshot_num in range(8):
			target_snapshot = 'snapshot' + str(snapshot_num)
			parametric_block = preset_dict['data']['tone'][target_snapshot]['controllers']['dsp0'][target_block]
			
			parametric_block['LowFreq']['@value'] = random.randint(20,495)
			parametric_block['LowQ']['@value'] = random.randint(1,100)/10
			parametric_block['LowGain']['@value'] = random.randint(-120,120)/10
			
			parametric_block['MidFreq']['@value'] = random.randint(125,8000)
			parametric_block['MidQ']['@value'] = random.randint(1,100)/10
			parametric_block['MidGain']['@value'] = random.randint(-120,120)/10
			
			parametric_block['HighFreq']['@value'] = random.randint(500,18000)
			parametric_block['HighQ']['@value'] = random.randint(1,100)/10
			parametric_block['HighGain']['@value'] = random.randint(-120,120)/10
		
			parametric_block['LowCut']['@value'] = random.randint(20,1000)
			parametric_block['HighCut']['@value'] = random.randint(1000,20000)

			# lowgain = random.randint(-120,120)/10
			# preset_dict['data']['tone'][target_snapshot]['controllers']['dsp0']['block1']['LowGain']['@value'] = lowgain
			# midgain = random.randint(-120,120)/10
			# preset_dict['data']['tone'][target_snapshot]['controllers']['dsp0']['block1']['MidGain']['@value'] = midgain
			# highgain = random.randint(-120,120)/10
			# preset_dict['data']['tone'][target_snapshot]['controllers']['dsp0']['block1']['HighGain']['@value'] = highgain
			# midfreq = random.randint(125,4000)
			# preset_dict['data']['tone'][target_snapshot]['controllers']['dsp0']['block1']['MidFreq']['@value'] = midfreq

		with open(os.path.expanduser('RandPara.hlx'), 'w') as json_file:
			json.dump(preset_dict, json_file, indent = 4)

makehlx()
