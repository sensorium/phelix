#!/usr/bin/env python
 
import os
import json
import base64
import zlib
 
SETLIST = "Helix 3.0 FACTORY 1.hls"
 
setlist_file = open(SETLIST)
setlist_data = json.load(setlist_file)
setlist_file.close()
keys = setlist_data.keys()
if 'encoded_data' in keys:
    unz = zlib.decompress(base64.b64decode(setlist_data['encoded_data']))
    setlist = json.loads(unz)
    presets = setlist['presets']
    #print json.dumps(presets, indent=4)
    for preset in presets:
        if 'meta' in preset.keys():
            meta = preset['meta']
            preset_name = meta['name']
            print (preset_name)