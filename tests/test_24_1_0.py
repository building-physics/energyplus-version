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
FIXTURE_DIRECTORY = PROJECT_ROOT / "tests" / "fixtures" / "24_1_0_to_24_2_0"

REPORT_VARIABLE_RENAMES = {
    "Zone Windows Total Transmitted Solar Radiation Rate":
        "Enclosure Windows Total Transmitted Solar Radiation Rate",
    "Zone Exterior Windows Total Transmitted Beam Solar Radiation Rate":
        "Enclosure Exterior Windows Total Transmitted Beam Solar Radiation Rate",
    "Zone Interior Windows Total Transmitted Beam Solar Radiation Rate":
        "Enclosure Interior Windows Total Transmitted Beam Solar Radiation Rate",
    "Zone Exterior Windows Total Transmitted Diffuse Solar Radiation Rate":
        "Enclosure Exterior Windows Total Transmitted Diffuse Solar Radiation Rate",
    "Zone Interior Windows Total Transmitted Diffuse Solar Radiation Rate":
        "Enclosure Interior Windows Total Transmitted Diffuse Solar Radiation Rate",
    "Zone Windows Total Transmitted Solar Radiation Energy":
        "Enclosure Windows Total Transmitted Solar Radiation Energy",
    "Zone Exterior Windows Total Transmitted Beam Solar Radiation Energy":
        "Enclosure Exterior Windows Total Transmitted Beam Solar Radiation Energy",
    "Zone Interior Windows Total Transmitted Beam Solar Radiation Energy":
        "Enclosure Interior Windows Total Transmitted Beam Solar Radiation Energy",
    "Zone Exterior Windows Total Transmitted Diffuse Solar Radiation Energy":
        "Enclosure Exterior Windows Total Transmitted Diffuse Solar Radiation Energy",
    "Zone Interior Windows Total Transmitted Diffuse Solar Radiation Energy":
        "Enclosure Interior Windows Total Transmitted Diffuse Solar Radiation Energy",
    "Indoor Living Wall Energy Required For Evapotranspiration Per Unit Area":
        "Indoor Living Wall Energy Rate Required For Evapotranspiration Per Unit Area",
}


def load_json(path):
    with path.open(encoding="utf-8") as json_file:
        return json.load(json_file)


def apply_upgrade(model):
    from energyplus_version.version_24_1_0 import Upgrade

    return jsonpatch.JsonPatch(Upgrade().generate_patch(model)).apply(model)


def test_versions():
    from energyplus_version.version_24_1_0 import Upgrade

    upgrade = Upgrade()

    assert upgrade.from_version() == "24.1.0"
    assert upgrade.to_version() == "24.2.0"


def test_upgrade_24_1_0_to_24_2_0_end_to_end():
    source = load_json(FIXTURE_DIRECTORY / "input.epJSON")
    expected = load_json(FIXTURE_DIRECTORY / "expected.epJSON")
    original = deepcopy(source)
    source_schema = load_json(PROJECT_ROOT / "schema" / "24.1.0" / "Energy+.schema.epJSON")
    destination_schema = load_json(PROJECT_ROOT / "schema" / "24.2.0" / "Energy+.schema.epJSON")

    assert jsonschema_rs.Draft7Validator(source_schema).is_valid(source)

    upgraded = apply_upgrade(source)

    assert source == original
    assert upgraded == expected
    assert jsonschema_rs.Draft7Validator(destination_schema).is_valid(upgraded)


def test_output_space_sizing_copies_output_zone_sizing():
    model = {
        "OutputControl:Files": {
            "Output Files": {
                "output_zone_sizing": "No",
                "output_system_sizing": "Yes",
            }
        }
    }
    original = deepcopy(model)

    upgraded = apply_upgrade(model)

    assert model == original
    assert upgraded == {
        "OutputControl:Files": {
            "Output Files": {
                "output_space_sizing": "No",
                "output_zone_sizing": "No",
                "output_system_sizing": "Yes",
            }
        }
    }


def test_output_space_sizing_is_not_materialized_when_zone_sizing_is_omitted():
    model = {"OutputControl:Files": {"Output Files": {"output_system_sizing": "No"}}}

    assert apply_upgrade(model) == model


def test_zone_and_space_fields_are_renamed():
    chimney = {
        **{f"zone_{number}_name": f"Zone {number}" for number in range(1, 21)},
        **{
            f"relative_ratios_of_air_flow_rates_passing_through_zone_{number}": number / 20
            for number in range(1, 21)
        },
    }
    model = {
        "Output:IlluminanceMap": {"Map": {"zone_name": "Zone 1"}},
        "ZoneCoolTower:Shower": {"Cool Tower": {"zone_name": "Zone 2"}},
        "ZoneRefrigerationDoorMixing": {
            "Door": {"zone_1_name": "Zone 1", "zone_2_name": "Zone 2"}
        },
        "ZoneThermalChimney": {"Chimney": chimney},
    }

    upgraded = apply_upgrade(model)

    assert upgraded["Output:IlluminanceMap"]["Map"] == {
        "zone_or_space_name": "Zone 1"
    }
    assert upgraded["ZoneCoolTower:Shower"]["Cool Tower"] == {
        "zone_or_space_name": "Zone 2"
    }
    assert upgraded["ZoneRefrigerationDoorMixing"]["Door"] == {
        "zone_or_space_name_1": "Zone 1",
        "zone_or_space_name_2": "Zone 2",
    }
    assert upgraded["ZoneThermalChimney"]["Chimney"] == {
        **{
            f"zone_or_space_name_{number}": f"Zone {number}"
            for number in range(1, 21)
        },
        **{
            f"relative_ratios_of_air_flow_rates_passing_through_inlet_{number}": number / 20
            for number in range(1, 21)
        },
    }


def test_indoor_living_wall_trailing_underscores_are_removed():
    model = {
        "IndoorLivingWall": {
            "Living Wall": {
                "led_intensity_schedule_name_": "Lighting Schedule",
                "led_nominal_intensity_": 32.5,
            }
        }
    }

    upgraded = apply_upgrade(model)

    assert upgraded == {
        "IndoorLivingWall": {
            "Living Wall": {
                "led_intensity_schedule_name": "Lighting Schedule",
                "led_nominal_intensity": 32.5,
            }
        }
    }


def test_phase_change_fields_become_extensible_values():
    model = {
        "MaterialProperty:PhaseChange": {
            "PCM": {
                "temperature_coefficient_for_thermal_conductivity": 0.1,
                **{
                    field: value
                    for number, temperature, enthalpy in (
                        (1, -20.0, 0.1),
                        (2, 22.0, 18260.0),
                        (3, 22.1, 32000.0),
                        (4, 60.0, 71000.0),
                    )
                    for field, value in (
                        (f"temperature_{number}", temperature),
                        (f"enthalpy_{number}", enthalpy),
                    )
                },
            }
        }
    }

    upgraded = apply_upgrade(model)

    assert upgraded == {
        "MaterialProperty:PhaseChange": {
            "PCM": {
                "temperature_coefficient_for_thermal_conductivity": 0.1,
                "values": [
                    {"temperature": -20.0, "enthalpy": 0.1},
                    {"temperature": 22.0, "enthalpy": 18260.0},
                    {"temperature": 22.1, "enthalpy": 32000.0},
                    {"temperature": 60.0, "enthalpy": 71000.0},
                ],
            }
        }
    }


def test_variable_thermal_conductivity_fields_become_extensible_values():
    model = {
        "MaterialProperty:VariableThermalConductivity": {
            "Variable Conductivity": {
                **{
                    field: value
                    for number, temperature, conductivity in (
                        (1, -40.0, 1.7),
                        (2, 24.0, 1.7),
                        (3, 25.0, 2.2),
                        (4, 100.0, 2.2),
                    )
                    for field, value in (
                        (f"temperature_{number}", temperature),
                        (f"thermal_conductivity_{number}", conductivity),
                    )
                }
            }
        }
    }

    upgraded = apply_upgrade(model)

    assert upgraded == {
        "MaterialProperty:VariableThermalConductivity": {
            "Variable Conductivity": {
                "values": [
                    {"temperature": -40.0, "thermal_conductivity": 1.7},
                    {"temperature": 24.0, "thermal_conductivity": 1.7},
                    {"temperature": 25.0, "thermal_conductivity": 2.2},
                    {"temperature": 100.0, "thermal_conductivity": 2.2},
                ]
            }
        }
    }


def test_vrf_terminal_variable_volume_fan_becomes_system_model_fan():
    model = {
        "ZoneHVAC:TerminalUnit:VariableRefrigerantFlow": {
            "VRF Terminal": {
                "supply_air_fan_object_type": "Fan:VariableVolume",
                "supply_air_fan_object_name": "VRF Fan",
            }
        },
        "Fan:VariableVolume": {
            "VRF Fan": {
                "availability_schedule_name": "Always On",
                "fan_total_efficiency": 0.7,
                "pressure_rise": 500.0,
                "maximum_flow_rate": 1.25,
                "fan_power_minimum_flow_rate_input_method": "FixedFlowRate",
                "fan_power_minimum_air_flow_rate": 0.25,
                "motor_efficiency": 0.9,
                "motor_in_airstream_fraction": 1.0,
                "fan_power_coefficient_1": 0.001,
                "fan_power_coefficient_2": 0.01,
                "fan_power_coefficient_3": 0.1,
                "fan_power_coefficient_4": 0.2,
                "fan_power_coefficient_5": 0.689,
                "air_inlet_node_name": "Fan Inlet",
                "air_outlet_node_name": "Fan Outlet",
                "end_use_subcategory": "VRF Fans",
            },
            "Unreferenced Fan": {
                "pressure_rise": 400.0,
                "air_inlet_node_name": "Other Inlet",
                "air_outlet_node_name": "Other Outlet",
            },
        },
    }

    upgraded = apply_upgrade(model)

    terminal = upgraded["ZoneHVAC:TerminalUnit:VariableRefrigerantFlow"]["VRF Terminal"]
    assert terminal["supply_air_fan_object_type"] == "Fan:SystemModel"
    assert terminal["supply_air_fan_object_name"] == "VRF Fan"
    assert upgraded["Fan:VariableVolume"] == {
        "Unreferenced Fan": model["Fan:VariableVolume"]["Unreferenced Fan"]
    }
    assert upgraded["Fan:SystemModel"]["VRF Fan"] == {
        "availability_schedule_name": "Always On",
        "air_inlet_node_name": "Fan Inlet",
        "air_outlet_node_name": "Fan Outlet",
        "design_maximum_air_flow_rate": 1.25,
        "speed_control_method": "Continuous",
        "electric_power_minimum_flow_rate_fraction": 0.2,
        "design_pressure_rise": 500.0,
        "motor_efficiency": 0.9,
        "motor_in_air_stream_fraction": 1.0,
        "design_electric_power_consumption": "Autosize",
        "design_power_sizing_method": "TotalEfficiencyAndPressure",
        "fan_total_efficiency": 0.7,
        "electric_power_function_of_flow_fraction_curve_name": "VRF Fan_curve",
        "end_use_subcategory": "VRF Fans",
    }
    assert upgraded["Curve:Quartic"]["VRF Fan_curve"] == {
        "coefficient1_constant": 0.001,
        "coefficient2_x": 0.01,
        "coefficient3_x_2": 0.1,
        "coefficient4_x_3": 0.2,
        "coefficient5_x_4": 0.689,
        "minimum_value_of_x": 0.0,
        "maximum_value_of_x": 1.0,
        "minimum_curve_output": 0.0,
        "maximum_curve_output": 5.0,
        "input_unit_type_for_x": "Dimensionless",
        "output_unit_type": "Dimensionless",
    }


@pytest.mark.parametrize(
    ("method", "maximum_flow_rate", "minimum_fraction", "minimum_flow_rate", "expected"),
    (
        ("Fraction", 1.25, 0.3, 0.0, 0.3),
        ("FixedFlowRate", "Autosize", 0.25, 0.0, 0.0),
    ),
)
def test_vrf_system_model_fan_minimum_flow_fraction(
    method,
    maximum_flow_rate,
    minimum_fraction,
    minimum_flow_rate,
    expected,
):
    model = {
        "ZoneHVAC:TerminalUnit:VariableRefrigerantFlow": {
            "VRF Terminal": {
                "supply_air_fan_object_type": "Fan:VariableVolume",
                "supply_air_fan_object_name": "VRF Fan",
            }
        },
        "Fan:VariableVolume": {
            "VRF Fan": {
                "pressure_rise": 500.0,
                "maximum_flow_rate": maximum_flow_rate,
                "fan_power_minimum_flow_rate_input_method": method,
                "fan_power_minimum_flow_fraction": minimum_fraction,
                "fan_power_minimum_air_flow_rate": minimum_flow_rate,
                "fan_power_coefficient_1": 0.001,
                "fan_power_coefficient_2": 0.01,
                "fan_power_coefficient_3": 0.1,
                "fan_power_coefficient_4": 0.2,
                "fan_power_coefficient_5": 0.689,
                "air_inlet_node_name": "Fan Inlet",
                "air_outlet_node_name": "Fan Outlet",
            }
        },
    }

    upgraded = apply_upgrade(model)

    fan = upgraded["Fan:SystemModel"]["VRF Fan"]
    assert fan["electric_power_minimum_flow_rate_fraction"] == expected


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

    upgraded = apply_upgrade(model)

    assert upgraded["Output:Variable"]["Output Request"]["variable_name"] == new_name


def test_new_optional_heat_recovery_fields_are_not_materialized():
    model = {
        "HeatPump:PlantLoop:EIR:Cooling": {"Cooling Heat Pump": {}},
        "HeatPump:PlantLoop:EIR:Heating": {"Heating Heat Pump": {}},
    }

    assert apply_upgrade(model) == model
