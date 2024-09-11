""" 
debug.py
 
 This file is part of phelix.
 
 Copyright 2024 Tim Barrass
 
 phelix is licensed under the GNU General Public Licence (GPL) Version 3 or later. 
"""

import json


def save_debug_hlx(preset):
    with open("debug.hlx", "w") as json_file:
        json.dump(preset, json_file, indent=4)
