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
FIXTURE_DIRECTORY = PROJECT_ROOT / "tests" / "fixtures" / "26_1_0_to_26_2_0"

REPORT_VARIABLE_RENAMES = {
    "Refrigeration Zone Air Chiller Sensible Heat Ratio":
        "Refrigeration Zone Air Chiller Coil Sensible Heat Ratio",
    "Refrigeration Zone Air Chiller Frost Accumulation Mass":
        "Refrigeration Zone Air Chiller Coil Frost Accumulation Mass",
    "Refrigeration Zone Air Chiller Defrost Electricity Rate":
        "Refrigeration Zone Air Chiller Coil Defrost Electricity Rate",
    "Refrigeration Zone Air Chiller Defrost Electricity Energy":
        "Refrigeration Zone Air Chiller Coil Defrost Electricity Energy",
}


def load_json(path):
    with path.open(encoding="utf-8") as json_file:
        return json.load(json_file)


def apply_upgrade(model):
    from energyplus_version.version_26_1_0 import Upgrade

    return jsonpatch.JsonPatch(Upgrade().generate_patch(model)).apply(model)


def test_upgrade_26_1_0_to_26_2_0_end_to_end():
    source = load_json(FIXTURE_DIRECTORY / "input.epJSON")
    expected = load_json(FIXTURE_DIRECTORY / "expected.epJSON")
    original = deepcopy(source)
    source_schema = load_json(PROJECT_ROOT / "schema" / "26.1.0" / "Energy+.schema.epJSON")
    destination_schema = load_json(PROJECT_ROOT / "schema" / "26.2.0" / "Energy+.schema.epJSON")

    assert jsonschema_rs.Draft7Validator(source_schema).is_valid(source)

    upgraded = apply_upgrade(source)

    assert source == original
    assert upgraded == expected
    assert jsonschema_rs.Draft7Validator(destination_schema).is_valid(upgraded)


def test_central_heat_pump_system_removes_control_method():
    model = {
        "CentralHeatPumpSystem": {
            "Heat Pump System": {
                "control_method": "SmartMixing",
                "cooling_loop_inlet_node_name": "Cooling Inlet",
            }
        }
    }
    original = deepcopy(model)

    upgraded = apply_upgrade(model)

    assert model == original
    assert upgraded == {
        "CentralHeatPumpSystem": {
            "Heat Pump System": {
                "cooling_loop_inlet_node_name": "Cooling Inlet",
            }
        }
    }


def test_chiller_heater_performance_removes_condenser_type():
    model = {
        "ChillerHeaterPerformance:Electric:EIR": {
            "Chiller Heater Performance": {
                "condenser_type": "WaterCooled",
                "reference_cooling_mode_cop": 5.5,
            }
        }
    }
    original = deepcopy(model)

    upgraded = apply_upgrade(model)

    assert model == original
    assert upgraded == {
        "ChillerHeaterPerformance:Electric:EIR": {
            "Chiller Heater Performance": {
                "reference_cooling_mode_cop": 5.5,
            }
        }
    }


def test_humidistat_schedule_fields_are_renamed():
    model = {
        "ZoneControl:Humidistat": {
            "Humidistat": {
                "zone_name": "Zone 1",
                "humidifying_relative_humidity_setpoint_schedule_name": "Humidifying Schedule",
                "dehumidifying_relative_humidity_setpoint_schedule_name": "Dehumidifying Schedule",
            }
        }
    }
    original = deepcopy(model)

    upgraded = apply_upgrade(model)

    assert model == original
    assert upgraded == {
        "ZoneControl:Humidistat": {
            "Humidistat": {
                "zone_name": "Zone 1",
                "humidifying_setpoint_schedule_name": "Humidifying Schedule",
                "dehumidifying_setpoint_schedule_name": "Dehumidifying Schedule",
            }
        }
    }


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


def test_new_optional_and_defaulted_fields_are_not_materialized():
    model = {
        "Building": {"Building": {"terrain": "Suburbs"}},
        "Coil:Cooling:DX:CurveFit:OperatingMode": {
            "Operating Mode": {"speed_1_name": "Speed 1"}
        },
        "Material": {
            "Material": {
                "roughness": "MediumRough",
                "thickness": 0.1,
                "conductivity": 0.5,
                "density": 800.0,
                "specific_heat": 900.0,
            }
        },
        "Material:NoMass": {
            "No Mass Material": {
                "roughness": "MediumRough",
                "thermal_resistance": 0.5,
            }
        },
        "MaterialProperty:VariableAbsorptance": {
            "Variable Absorptance": {"reference_material_name": "Material"}
        },
        "Space": {
            "Space": {
                "zone_name": "Zone 1",
                "tags": [{"tag": "Fixture tag"}],
            }
        },
        "ZoneBaseboard:OutdoorTemperatureControlled": {
            "Baseboard": {
                "zone_or_zonelist_or_space_or_spacelist_name": "Zone 1",
                "schedule_name": "Always On",
                "capacity_at_low_temperature": 1000.0,
                "low_temperature": -10.0,
                "capacity_at_high_temperature": 0.0,
                "high_temperature": 20.0,
            }
        },
    }
    original = deepcopy(model)

    upgraded = apply_upgrade(model)

    assert upgraded == original
