# SPDX-FileCopyrightText: 2023-present Oak Ridge National Laboratory, managed by UT-Battelle
#
# SPDX-License-Identifier: BSD-3-Clause
import json
from copy import deepcopy
from pathlib import Path

import jsonpatch
import jsonschema

#from energyplus_version import UpgradeWarning
from energyplus_version.version_23_2_0 import Upgrade


PROJECT_ROOT = Path(__file__).parents[1]
FIXTURE_DIRECTORY = PROJECT_ROOT / "tests" / "fixtures" / "23_2_0_to_24_1_0"


def load_json(path):
    with path.open(encoding="utf-8") as json_file:
        return json.load(json_file)

def diff_as_string(left, right):
    diffpatch = jsonpatch.JsonPatch.from_diff(left, right)
    return diffpatch.to_string()

def test_versions():
    upgrade = Upgrade()
    assert upgrade.from_version() == '23.2.0'
    assert upgrade.to_version() == '24.1.0'


def test_upgrade_23_2_0_to_24_1_0_end_to_end():
    input_path = FIXTURE_DIRECTORY / "input.epJSON"
    expected_path = FIXTURE_DIRECTORY / "expected.epJSON"
    source = load_json(input_path)
    original = deepcopy(source)
    expected = load_json(expected_path)

    source_schema = load_json(PROJECT_ROOT / "schema" / "23.2.0" / "Energy+.schema.epJSON")
    destination_schema = load_json(PROJECT_ROOT / "schema" / "24.1.0" / "Energy+.schema.epJSON")
    jsonschema.Draft7Validator(source_schema).validate(source)

    patch = Upgrade().generate_patch(source)
    upgraded = jsonpatch.JsonPatch(patch).apply(source)

    assert source == original
    assert upgraded == expected
    jsonschema.Draft7Validator(destination_schema).validate(upgraded)

hx = {
    "HeatExchanger:AirToAir:SensibleAndLatent": {
        "F2 N1 Apartment OA Heat Exchanger": {
            "availability_schedule_name": "AllOn_Except_DD",
            "exhaust_air_inlet_node_name": "F2 N1 Apartment Zone Exhaust Node",
            "exhaust_air_outlet_node_name": "F2 N1 Apartment ERV Secondary Outlet Node",
            "frost_control_type": "ExhaustOnly",
            "heat_exchanger_type": "Rotary",
            "initial_defrost_time_fraction": 0.167,
            "latent_effectiveness_at_75_cooling_air_flow": 0,
            "latent_effectiveness_at_75_heating_air_flow": 0,
            "latent_effectiveness_at_100_cooling_air_flow": 0,
            "latent_effectiveness_at_100_heating_air_flow": 0,
            "nominal_electric_power": 0,
            "nominal_supply_air_flow_rate": "Autosize",
            "rate_of_defrost_time_fraction_increase": 1.44,
            "sensible_effectiveness_at_75_cooling_air_flow": 0.618,
            "sensible_effectiveness_at_75_heating_air_flow": 0.623,
            "sensible_effectiveness_at_100_cooling_air_flow": 0.596,
            "sensible_effectiveness_at_100_heating_air_flow": 0.6,
            "supply_air_inlet_node_name": "F2 N1 Apartment Outside Air Node",
            "supply_air_outlet_node_name": "F2 N1 Apartment ERV Outlet Node",
            "supply_air_outlet_temperature_control": "No",
            "threshold_temperature": -23.3
        }
    }
}

def test_hx():
    upgrade = Upgrade()
    patch = upgrade.generate_patch(hx)
    jp = jsonpatch.JsonPatch(patch)
    new_epjson = jp.apply(hx)
    assert new_epjson
    hx_objects = new_epjson["HeatExchanger:AirToAir:SensibleAndLatent"]
    hx_object = hx_objects["F2 N1 Apartment OA Heat Exchanger"]
    curve_fields = (
        "sensible_effectiveness_of_heating_air_flow_curve_name",
        "latent_effectiveness_of_heating_air_flow_curve_name",
        "sensible_effectiveness_of_cooling_air_flow_curve_name",
        "latent_effectiveness_of_cooling_air_flow_curve_name",
    )
    curve_names = {hx_object[field] for field in curve_fields if field in hx_object}
    assert curve_names == {
        "F2 N1 Apartment OA Heat Exchanger_1",
        "F2 N1 Apartment OA Heat Exchanger_3",
    }
    assert curve_names <= set(new_epjson["Table:Lookup"])
    independent_variables = new_epjson["Table:IndependentVariableList"]
    assert independent_variables["effectiveness_IndependentVariableList"] == {
        "independent_variables": [{"independent_variable_name": "HxAirFlowRatio"}]
    }


def test_hx_preserves_existing_lookup_tables():
    model = dict(hx)
    model["Table:Lookup"] = {"Existing Lookup Table": {"values": []}}

    upgraded = jsonpatch.JsonPatch(Upgrade().generate_patch(model)).apply(model)

    lookup_tables = upgraded["Table:Lookup"]
    assert "Existing Lookup Table" in lookup_tables
    assert "F2 N1 Apartment OA Heat Exchanger_1" in lookup_tables
    assert "F2 N1 Apartment OA Heat Exchanger_3" in lookup_tables


def test_hx_uses_defaults_for_omitted_effectiveness_fields():
    model = {
        "HeatExchanger:AirToAir:SensibleAndLatent": {
            "Defaulted Heat Exchanger": {
                "sensible_effectiveness_at_100_heating_air_flow": 0.7,
            }
        }
    }

    upgraded = jsonpatch.JsonPatch(Upgrade().generate_patch(model)).apply(model)

    hx_object = upgraded["HeatExchanger:AirToAir:SensibleAndLatent"]["Defaulted Heat Exchanger"]
    curve_name = hx_object["sensible_effectiveness_of_heating_air_flow_curve_name"]
    assert curve_name == "Defaulted Heat Exchanger_1"
    assert upgraded["Table:Lookup"][curve_name]["values"] == [
        {"output_value": 0.0},
        {"output_value": 0.7},
    ]


def test_airloop_unitary_system_no_load_airflow_control():
    model = {
        "AirLoopHVAC:UnitarySystem": {
            "Variable Speed Heating": {
                "heating_coil_object_type": "Coil:Heating:DX:VariableSpeed",
                "cooling_coil_object_type": "Coil:Cooling:DX:SingleSpeed",
            },
            "Single Speed Heating and Cooling": {
                "heating_coil_object_type": "Coil:Heating:DX:SingleSpeed",
                "cooling_coil_object_type": "Coil:Cooling:DX:SingleSpeed",
            },
        }
    }

    upgraded = jsonpatch.JsonPatch(Upgrade().generate_patch(model)).apply(model)
    systems = upgraded["AirLoopHVAC:UnitarySystem"]

    airflow_control_field = "no_load_supply_air_flow_rate_control_set_to_low_speed"
    assert systems["Variable Speed Heating"][airflow_control_field] == "Yes"
    assert systems["Single Speed Heating and Cooling"][airflow_control_field] == "No"


def test_pthp_heating_only_variable_speed_uses_low_speed_airflow():
    model = {
        "ZoneHVAC:PackagedTerminalHeatPump": {
            "Heating Variable Speed PTHP": {
                "heating_coil_object_type": "Coil:Heating:DX:VariableSpeed",
                "cooling_coil_object_type": "Coil:Cooling:DX:SingleSpeed",
            }
        }
    }

    upgraded = jsonpatch.JsonPatch(Upgrade().generate_patch(model)).apply(model)
    pthp = upgraded["ZoneHVAC:PackagedTerminalHeatPump"]["Heating Variable Speed PTHP"]

    airflow_control_field = "no_load_supply_air_flow_rate_control_set_to_low_speed"
    assert pthp[airflow_control_field] == "Yes"
