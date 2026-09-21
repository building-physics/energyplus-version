# SPDX-FileCopyrightText: 2023-present Oak Ridge National Laboratory, managed by UT-Battelle
#
# SPDX-License-Identifier: BSD-3-Clause
from copy import deepcopy
import json
from pathlib import Path

import jsonpatch
import jsonschema_rs
import pytest


PROJECT_ROOT = Path(__file__).parents[1]
FIXTURE_DIRECTORY = PROJECT_ROOT / "tests" / "fixtures" / "24_2_0_to_25_1_0"

REPORT_VARIABLE_RENAMES = {
    "Zone Hybrid Unitary HVAC DehumidificationLoad to Humidistat Setpoint Heat Tansfer Energy":
        "Zone Hybrid Unitary HVAC Dehumidification Load to Humidistat Setpoint Heat Transfer Energy",
    "Zone Hybrid Unitary HVAC Humidification Load to Humidistat Setpoint Heat Tansfer Energy":
        "Zone Hybrid Unitary HVAC Humidification Load to Humidistat Setpoint Heat Transfer Energy",
    "Infiltration Air Change Rate":
        "Infiltration Current Density Air Change Rate",
    "Zone Infiltration Air Change Rate":
        "Zone Infiltration Current Density Air Change Rate",
    "Zone Ventilation Air Change Rate":
        "Zone Ventilation Current Density Air Change Rate",
}


def load_json(path):
    with path.open(encoding="utf-8") as json_file:
        return json.load(json_file)


def apply_upgrade(model):
    from energyplus_version.version_24_2_0 import Upgrade

    return jsonpatch.JsonPatch(Upgrade().generate_patch(model)).apply(model)


def test_versions():
    from energyplus_version.version_24_2_0 import Upgrade

    upgrade = Upgrade()

    assert upgrade.from_version() == "24.2.0"
    assert upgrade.to_version() == "25.1.0"


def test_upgrade_24_2_0_to_25_1_0_end_to_end():
    source = load_json(FIXTURE_DIRECTORY / "input.epJSON")
    expected = load_json(FIXTURE_DIRECTORY / "expected.epJSON")
    original = deepcopy(source)
    source_schema = load_json(PROJECT_ROOT / "schema" / "24.2.0" / "Energy+.schema.epJSON")
    destination_schema = load_json(PROJECT_ROOT / "schema" / "25.1.0" / "Energy+.schema.epJSON")

    assert jsonschema_rs.Draft7Validator(source_schema).is_valid(source)

    upgraded = apply_upgrade(source)

    assert source == original
    assert upgraded == expected
    assert jsonschema_rs.Draft7Validator(destination_schema).is_valid(upgraded)


@pytest.mark.parametrize(("old_name", "new_name"), REPORT_VARIABLE_RENAMES.items())
def test_output_variable_names_are_updated(old_name, new_name):
    model = {
        "Output:Variable": {
            "Output Request": {
                "key_value": "*",
                "variable_name": old_name,
            }
        }
    }
    original = deepcopy(model)

    upgraded = apply_upgrade(model)

    assert model == original
    assert upgraded["Output:Variable"]["Output Request"]["variable_name"] == new_name


def test_new_density_basis_fields_are_not_materialized():
    model = {
        "ZoneInfiltration:DesignFlowRate": {
            "Infiltration": {
                "zone_or_zonelist_or_space_or_spacelist_name": "Fixture Zone",
                "air_changes_per_hour": 0.5,
            }
        },
        "ZoneVentilation:DesignFlowRate": {
            "Ventilation": {
                "zone_or_zonelist_or_space_or_spacelist_name": "Fixture Zone",
                "design_flow_rate": 0.1,
            }
        },
    }

    assert apply_upgrade(model) == model
