"""
variables.py

 This file is part of phelix.

 Copyright 2024 Tim Barrass

 phelix is licensed under the GNU General Public Licence (GPL) Version 3 or later.
"""

# These can change
NUM_PEDAL2_PARAMS = 16
NUM_MIDICC_PARAMS = 2
NUM_SNAPSHOT_PARAMS = 46
BLOCKS_PATH = "blocks/"
MUTATION_RATE = 0.2
FRACTION_MOVE = 0.2
TOGGLE_RATE = 0.2



useable_cc_numbers = [
    4,
    5,
    6,
    7,
    8,
    9,
    10,
    11,
    12,
    13,
    14,
    15,
    16,
    17,
    18,
    19,
    20,
    21,
    22,
    23,
    24,
    25,
    26,
    27,
    28,
    29,
    30,
    31,
    # skip 32
    33,
    34,
    35,
    36,
    37,
    38,
    39,
    40,
    41,
    42,
    43,
    44,
    45,
    46,
    47,
    # 48, I've used it for fs12 for communicating with Pd
    # skip some
    82,
    83,
    84,
    85,
    86,
    87,
    88,
    89,
    90,
    91,
    92,
    93,
    94,
    95,
    96,
    97,
    98,
    99,
    100,
    101,
    102,
    103,
    104,
    105,
    106,
    107,
    108,
    109,
    110,
    111,
    112,
    113,
    114,
    115,
    116,
    117,
    118,
    119,
    120,
    121,
    122,
    123,
    124,
    125,
    126,
    127,
]


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
CONTROLLER_PEDAL2 = 2
CONTROLLER_SNAPSHOT = 19
CONTROLLER_MIDICC = 18
NUM_SNAPSHOTS = 8
NUM_SLOTS_PER_DSP = 16
NUM_PATHS_PER_DSP = 2
NUM_POSITIONS_PER_PATH = 8
MAXIMUM_CONTROLLERS = 64
