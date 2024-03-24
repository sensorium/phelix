#!/usr/bin/env python

import json
from pprint import pprint
import base64
import zlib

data = None
compress_data = None
data_bundle = None

with open('bundleparser/Mar-08.hxb') as file_bundle:
        data = json.load(file_bundle)

if 'encoded_data' in data:
        compress_data = base64.b64decode(data['encoded_data'])
        bundle = zlib.decompress(compress_data)

        data_bundle = json.loads(bundle)
        pprint(data_bundle)