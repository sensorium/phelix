""" 
variables.py
 
 This file is part of phelix.
 
 Copyright 2024 Tim Barrass
 
 phelix is licensed under the GNU General Public Licence (GPL) Version 3 or later. 
"""

# These can change
NUM_PEDAL_PARAMS = 16
BLOCKS_PATH = "blocks/"
MUTATION_RATE = 0.1
FRACTION_MOVE = 0.1
TOGGLE_RATE = 0.2


# Change these in the GUI, not here
block_probabilities = {
    "Amp": 20,
    "Cab": 10,
    "Delay": 20,
    "Distort": 15,
    "Dynamics": 10,
    "EQ": 20,
    "Filter": 5,
    "Mod": 30,
    "PitchSynth": 10,
    "Reverb": 25,
    "Split": 10,
    "VolPan": 3,
    "Wah": 10,
}

# Don't change these, they're builtin to helix
PEDAL_2 = 2
SNAPSHOT_CONTROL = 19
MIDI_CC_CONTROL = 18
NUM_SNAPSHOTS = 8
NUM_SLOTS_PER_DSP = 16
NUM_PATHS_PER_DSP = 2
NUM_POSITIONS_PER_PATH = 8
MAXIMUM_CONTROLLERS = 64
