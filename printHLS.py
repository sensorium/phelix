#!/usr/bin/env python

import base64
import zlib
import json

f = open("Helix 3.0 FACTORY 1.hls", "r") 
helix_json  = json.load(f)		
helix_ascii = helix_json["encoded_data"].encode("ascii") 
helix_decoded = base64.b64decode(helix_ascii) 
helix_decompressed =  zlib.decompress(helix_decoded)
helix_readable = helix_decompressed.decode("ascii)")
print(helix_readable)