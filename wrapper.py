#!/usr/bin/env python

""" How to use:

Open a terminal and navigate to this directory.
Run this script with the desired arguments:

python wrapper.py template.hlx output.hlx 5

(this works for me:)
./wrapper.py presets/templates/LessOccSplitCC.hlx presets/generated/aGenerated.hlx 5

This will generate 5 presets from the template file template.hlx and save them to the file output.hlx.
 """

import argparse
import os
import sys

# Add the project directory to the system path to allow importing modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from buildpreset import generate_multiple_presets_from_template

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate presets from a template file.")
    parser.add_argument("template_file", help="The template file to use.")
    parser.add_argument("output_file", help="The output file to save the generated presets to.")
    parser.add_argument("num_presets", type=int, help="The number of presets to generate.")
    args = parser.parse_args()

    generate_multiple_presets_from_template(args)
