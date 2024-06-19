import pytest
from copy import deepcopy
from util import add_raw_block_default_to_dsp

@pytest.mark.parametrize(
    "preset, dsp, slot, raw_block_dict, expected_preset",
    [
        # Happy path tests
        (
            {"data": {"tone": {"dsp1": {}}}},
            "dsp1",
            "slot1",
            {"Defaults": {"param1": "value1"}},
            {"data": {"tone": {"dsp1": {"slot1": {"param1": "value1"}}}}},
            id="happy_path_single_param"
        ),
        (
            {"data": {"tone": {"dsp2": {}}}},
            "dsp2",
            "slot2",
            {"Defaults": {"param1": "value1", "param2": "value2"}},
            {"data": {"tone": {"dsp2": {"slot2": {"param1": "value1", "param2": "value2"}}}}},
            id="happy_path_multiple_params"
        ),
        # Edge cases
        (
            {"data": {"tone": {"dsp3": {}}}},
            "dsp3",
            "slot3",
            {"Defaults": {}},
            {"data": {"tone": {"dsp3": {"slot3": {}}}}},
            id="edge_case_empty_defaults"
        ),
        (
            {"data": {"tone": 
