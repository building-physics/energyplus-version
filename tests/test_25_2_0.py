# SPDX-FileCopyrightText: 2023-present Oak Ridge National Laboratory, managed by UT-Battelle
#
# SPDX-License-Identifier: BSD-3-Clause
from copy import deepcopy
import json
from pathlib import Path

import jsonpatch
import jsonschema_rs


PROJECT_ROOT = Path(__file__).parents[1]
FIXTURE_DIRECTORY = PROJECT_ROOT / "tests" / "fixtures" / "25_2_0_to_26_1_0"


def load_json(path):
    with path.open(encoding="utf-8") as json_file:
        return json.load(json_file)


def apply_upgrade(model):
    from energyplus_version.version_25_2_0 import Upgrade

    return jsonpatch.JsonPatch(Upgrade().generate_patch(model)).apply(model)


def test_upgrade_25_2_0_to_26_1_0_end_to_end():
    source = load_json(FIXTURE_DIRECTORY / "input.epJSON")
    expected = load_json(FIXTURE_DIRECTORY / "expected.epJSON")
    original = deepcopy(source)
    source_schema = load_json(PROJECT_ROOT / "schema" / "25.2.0" / "Energy+.schema.epJSON")
    destination_schema = load_json(PROJECT_ROOT / "schema" / "26.1.0" / "Energy+.schema.epJSON")

    assert jsonschema_rs.Draft7Validator(source_schema).is_valid(source)

    upgraded = apply_upgrade(source)

    assert source == original
    assert upgraded == expected
    assert jsonschema_rs.Draft7Validator(destination_schema).is_valid(upgraded)


def test_parallel_piu_removes_reheat_coil_air_inlet_node_name():
    model = {
        "AirTerminal:SingleDuct:ParallelPIU:Reheat": {
            "Parallel PIU": {
                "outlet_node_name": "Parallel PIU Outlet",
                "reheat_coil_air_inlet_node_name": "Parallel PIU Reheat Inlet",
                "zone_mixer_name": "Parallel PIU Mixer",
            }
        }
    }
    original = deepcopy(model)

    upgraded = apply_upgrade(model)

    assert model == original
    assert upgraded == {
        "AirTerminal:SingleDuct:ParallelPIU:Reheat": {
            "Parallel PIU": {
                "outlet_node_name": "Parallel PIU Outlet",
                "zone_mixer_name": "Parallel PIU Mixer",
            }
        }
    }


def test_series_piu_removes_reheat_coil_air_inlet_node_name():
    model = {
        "AirTerminal:SingleDuct:SeriesPIU:Reheat": {
            "Series PIU": {
                "outlet_node_name": "Series PIU Outlet",
                "reheat_coil_air_inlet_node_name": "Series PIU Reheat Inlet",
                "zone_mixer_name": "Series PIU Mixer",
            }
        }
    }
    original = deepcopy(model)

    upgraded = apply_upgrade(model)

    assert model == original
    assert upgraded == {
        "AirTerminal:SingleDuct:SeriesPIU:Reheat": {
            "Series PIU": {
                "outlet_node_name": "Series PIU Outlet",
                "zone_mixer_name": "Series PIU Mixer",
            }
        }
    }
