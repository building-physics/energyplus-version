# SPDX-FileCopyrightText: 2023-present Oak Ridge National Laboratory, managed by UT-Battelle
#
# SPDX-License-Identifier: BSD-3-Clause
import pytest
import jsonpatch

#from energyplus_version import UpgradeWarning
from energyplus_version.version_23_1 import Upgrade

def test_versions():
    upgrade = Upgrade()
    assert upgrade.from_version() == '23.1'
    assert upgrade.to_version() == '23.2'

xing = {
    "Site:GroundTemperature:Undisturbed:Xing": {
        "Golden-NREL-Temps": {
            "average_soil_surface_tempeature": 11.3,
            "phase_shift_of_temperature_amplitude_1": 26,
            "phase_shift_of_temperature_amplitude_2": 5,
            "soil_density": 962,
            "soil_specific_heat": 2576,
            "soil_surface_temperature_amplitude_1": 10.9,
            "soil_surface_temperature_amplitude_2": -0.5,
            "soil_thermal_conductivity": 1.08
        }
    }
}

xing_expected = {
    "Site:GroundTemperature:Undisturbed:Xing": {
        "Golden-NREL-Temps": {
            "average_soil_surface_temperature": 11.3,
            "phase_shift_of_temperature_amplitude_1": 26,
            "phase_shift_of_temperature_amplitude_2": 5,
            "soil_density": 962,
            "soil_specific_heat": 2576,
            "soil_surface_temperature_amplitude_1": 10.9,
            "soil_surface_temperature_amplitude_2": -0.5,
            "soil_thermal_conductivity": 1.08
        }
    }
}

def compare(left, right):
    return all((left.get(k) == v for k, v in right.items()))

def test_xing():
    upgrade = Upgrade()
    patch = upgrade.generate_patch(xing)
    assert len(patch) == 1
    jp = jsonpatch.JsonPatch(patch)
    new_epjson = jp.apply(xing)
    assert compare(xing_expected["Site:GroundTemperature:Undisturbed:Xing"]["Golden-NREL-Temps"],new_epjson["Site:GroundTemperature:Undisturbed:Xing"]["Golden-NREL-Temps"])
