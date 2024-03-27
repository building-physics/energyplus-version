# SPDX-FileCopyrightText: 2023-present Oak Ridge National Laboratory, managed by UT-Battelle
#
# SPDX-License-Identifier: BSD-3-Clause
import jsonpatch

#from energyplus_version import UpgradeWarning
from energyplus_version.version_23_2_0 import Upgrade

def diff_as_string(left, right):
    diffpatch = jsonpatch.JsonPatch.from_diff(left, right)
    return diffpatch.to_string()

def test_versions():
    upgrade = Upgrade()
    assert upgrade.from_version() == '23.2.0'
    assert upgrade.to_version() == '24.1.0'

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
    assert len(patch) == 10
    jp = jsonpatch.JsonPatch(patch)
    new_epjson = jp.apply(hx)
    assert new_epjson
