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
FIXTURE_DIRECTORY = PROJECT_ROOT / "tests" / "fixtures" / "25_1_0_to_25_2_0"

THERMAL_STORAGE_VARIABLE_SUFFIXES = (
    "Final Tank Temperature",
    "Use Side Mass Flow Rate",
    "Use Side Inlet Temperature",
    "Use Side Outlet Temperature",
    "Use Side Heat Transfer Rate",
    "Use Side Heat Transfer Energy",
    "Source Side Mass Flow Rate",
    "Source Side Inlet Temperature",
    "Source Side Outlet Temperature",
    "Source Side Heat Transfer Rate",
    "Source Side Heat Transfer Energy",
) + tuple(
    suffix
    for node_number in range(1, 11)
    for suffix in (
        f"Temperature Node {node_number}",
        f"Final Temperature Node {node_number}",
    )
)

REPORT_VARIABLE_RENAMES = {
    **{
        f"{water_type} Water Thermal Storage {suffix}":
            f"{water_type} Water Thermal Storage Tank {suffix}"
        for water_type in ("Chilled", "Hot")
        for suffix in THERMAL_STORAGE_VARIABLE_SUFFIXES
    },
    "Zone Opaque Surface Inside Faces Total Conduction Heat Gain Rate":
        "Zone Opaque Surface Inside Faces Conduction Heat Gain Rate",
    "Zone Opaque Surface Inside Faces Total Conduction Heat Loss Rate":
        "Zone Opaque Surface Inside Faces Conduction Heat Loss Rate",
    "Zone Opaque Surface Inside Faces Total Conduction Heat Gain Energy":
        "Zone Opaque Surface Inside Faces Conduction Heat Gain Energy",
    "Zone Opaque Surface Inside Faces Total Conduction Heat Loss Energy":
        "Zone Opaque Surface Inside Faces Conduction Heat Loss Energy",
}


def load_json(path):
    with path.open(encoding="utf-8") as json_file:
        return json.load(json_file)


def apply_upgrade(model):
    from energyplus_version.version_25_1_0 import Upgrade

    return jsonpatch.JsonPatch(Upgrade().generate_patch(model)).apply(model)


def test_upgrade_25_1_0_to_25_2_0_end_to_end():
    source = load_json(FIXTURE_DIRECTORY / "input.epJSON")
    expected = load_json(FIXTURE_DIRECTORY / "expected.epJSON")
    original = deepcopy(source)
    source_schema = load_json(PROJECT_ROOT / "schema" / "25.1.0" / "Energy+.schema.epJSON")
    destination_schema = load_json(PROJECT_ROOT / "schema" / "25.2.0" / "Energy+.schema.epJSON")

    assert jsonschema_rs.Draft7Validator(source_schema).is_valid(source)

    upgraded = apply_upgrade(source)

    assert source == original
    assert upgraded == expected
    assert jsonschema_rs.Draft7Validator(destination_schema).is_valid(upgraded)


def test_multispeed_unitary_heat_pump_removes_replaced_minimum_temperature():
    model = {
        "AirLoopHVAC:UnitaryHeatPump:AirToAir:MultiSpeed": {
            "Heat Pump": {
                "air_inlet_node_name": "Heat Pump Inlet",
                "minimum_outdoor_dry_bulb_temperature_for_compressor_operation": -8.0,
            }
        }
    }
    original = deepcopy(model)

    upgraded = apply_upgrade(model)

    assert model == original
    assert upgraded == {
        "AirLoopHVAC:UnitaryHeatPump:AirToAir:MultiSpeed": {
            "Heat Pump": {
                "air_inlet_node_name": "Heat Pump Inlet",
            }
        }
    }


def test_variable_speed_coil_fields_are_renamed():
    cooling_condenser_fields = {
        **{
            f"speed_{speed}_reference_unit_condenser_air_flow_rate": speed
            for speed in (6, 8, 9, 10)
        },
        "speed_7_reference_unit_condenser_flow_rate": 7,
    }
    heating_capacity_curve_fields = {
        f"speed_{speed}_heating_capacity_function_of_air_flow_fraction_curve_name":
            f"Heating Capacity Curve {speed}"
        for speed in range(4, 11)
    }
    water_heating_fields = {
        old_field: speed
        for speed in range(1, 11)
        for old_field in (
            f"rated_sensible_heat_ratio_at_speed_{speed}",
            f"rated_water_heating_capacity_at_speed_{speed}",
            f"rated_water_heating_cop_at_speed_{speed}",
        )
    }
    model = {
        "Coil:Heating:WaterToAirHeatPump:VariableSpeedEquationFit": {
            "Heating Coil": {
                "speed_1_reference_unit_rated_air_flow": 0.5,
            }
        },
        "Coil:Cooling:DX:VariableSpeed": {
            "Cooling Coil": cooling_condenser_fields,
        },
        "Coil:Heating:DX:VariableSpeed": {
            "Heating Coil": heating_capacity_curve_fields,
        },
        "Coil:WaterHeating:AirToWaterHeatPump:VariableSpeed": {
            "Water Heating Coil": water_heating_fields,
        },
    }
    original = deepcopy(model)

    upgraded = apply_upgrade(model)

    assert model == original
    assert upgraded == {
        "Coil:Heating:WaterToAirHeatPump:VariableSpeedEquationFit": {
            "Heating Coil": {
                "speed_1_reference_unit_rated_air_flow_rate": 0.5,
            }
        },
        "Coil:Cooling:DX:VariableSpeed": {
            "Cooling Coil": {
                f"speed_{speed}_reference_unit_rated_condenser_air_flow_rate": speed
                for speed in range(6, 11)
            },
        },
        "Coil:Heating:DX:VariableSpeed": {
            "Heating Coil": {
                f"speed_{speed}_total_heating_capacity_function_of_air_flow_fraction_curve_name":
                    f"Heating Capacity Curve {speed}"
                for speed in range(4, 11)
            },
        },
        "Coil:WaterHeating:AirToWaterHeatPump:VariableSpeed": {
            "Water Heating Coil": {
                new_field: speed
                for speed in range(1, 11)
                for new_field in (
                    f"speed_{speed}_rated_sensible_heat_ratio",
                    f"speed_{speed}_rated_water_heating_capacity",
                    f"speed_{speed}_rated_water_heating_cop",
                )
            },
        },
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


def test_new_optional_fields_are_not_materialized():
    coil_types = (
        "Coil:Cooling:WaterToAirHeatPump:VariableSpeedEquationFit",
        "Coil:Heating:WaterToAirHeatPump:VariableSpeedEquationFit",
        "Coil:Cooling:VariableSpeed",
        "Coil:Heating:VariableSpeed",
        "Coil:WaterHeating:AirToWaterHeatPump:VariableSpeedEquationFit",
        "Coil:Cooling:WaterToAirHeatPump:EquationFit",
        "Coil:Heating:WaterToAirHeatPump:EquationFit",
        "Coil:Cooling:WaterToAirHeatPump:ParameterEstimation",
        "Coil:Heating:WaterToAirHeatPump:ParameterEstimation",
        "Coil:WaterHeating:AirToWaterHeatPump:Pumped",
        "Coil:WaterHeating:AirToWaterHeatPump:Wrapped",
    )
    model = {
        **{coil_type: {"Coil": {}} for coil_type in coil_types},
        "GroundHeatExchanger:System": {"Ground Heat Exchanger": {}},
        "ZoneHVAC:IdealLoadsAirSystem": {"Ideal Loads System": {}},
    }
    original = deepcopy(model)

    upgraded = apply_upgrade(model)

    assert upgraded == original
