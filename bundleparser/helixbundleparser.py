#!/usr/bin/env python
# started from Line6-Helix-Bundle-Parser from github

import json
from pprint import pprint
import base64
import zlib
import string

data = None
compress_data = None
data_bundle = None
c=0
dataout = {}
valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)

#Replace Feb.hlb with the name of your Helix bundle file.  Must be in root directory of where the python script is located
#with open('bundleparser/Mar-08.hlb') as file_bundle:
#    data = json.load(file_bundle)

with open('bundleparser/Mar-08.hxb', 'rb') as file_bundle:  # Add 'rb' for opening the file in binary mode
	data = json.load(file_bundle, encoding='utf-8')  # Specify the encoding parameter

	if 'encoded_data' in data:
		compress_data = base64.b64decode(data['encoded_data'])
		bundle = zlib.decompress(compress_data)

		data_bundle = json.loads(bundle)
		for s in data_bundle['setlists']:
			for tone in s['presets']:
				if 'meta' in tone:
					presetname = tone['meta']['name']
					filename = presetname + "_" + str(c) + ".hlx"
					safe_filename = ''.join(c for c in filename if c in valid_chars)
					print ("Writing %s" % safe_filename)
					with open(safe_filename, 'w') as outfile:
						dataout['version'] = 6
						dataout['data'] = tone
						dataout['schema'] = "L6Preset"
						json.dump(dataout,outfile)
					c += 1 
					
				
