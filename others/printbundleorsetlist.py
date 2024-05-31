#!/usr/bin/env python
 
import sys
import os
import json
import base64
import zlib
 
#SETLIST_OR_BUNDLE = "/Users/bsd/helix/setlists/USER 1-2016-11-22.hls"
#SETLIST_OR_BUNDLE = "/Users/bsd/helix/bundles/2017-01-14.hlb"
SETLIST_OR_BUNDLE = "Helix 3.0 FACTORY 1.hls"

infile = open(SETLIST_OR_BUNDLE)
data = json.load(infile)
infile.close()
 
keys = data.keys()
if 'encoded_data' in keys:
    unz = zlib.decompress(base64.b64decode(data['encoded_data']))
    setlist_or_bundle = json.loads(unz)
    keys = setlist_or_bundle.keys()
    if 'setlists' in keys:
        setlists = setlist_or_bundle['setlists']
    elif 'presets' in keys:
        setlists = [setlist_or_bundle]
    for setlist in setlists:
        keys = setlist.keys()
        if 'meta' in keys:
            print
            print ("SETLIST: %s" % (setlist['meta']['name']))
        presets = setlist['presets']
        #print json.dumps(presets, indent=4)
        for preset in presets:
            if 'meta' in preset.keys():
                meta = preset['meta']
                preset_name = meta['name']
                print("  ", preset_name)