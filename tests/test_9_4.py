# SPDX-FileCopyrightText: 2023-present Oak Ridge National Laboratory, managed by UT-Battelle
#
# SPDX-License-Identifier: BSD-3-Clause
import pytest
import jsonpatch

from energyplus_version import UpgradeWarning
from energyplus_version.version_9_4 import Upgrade

def test_versions():
    upgrade = Upgrade()
    assert upgrade.from_version() == '9.4'
    assert upgrade.to_version() == '9.5'

air_boundary = {
    "Construction:AirBoundary": {
        "Air Wall": {
            "air_exchange_method": "SimpleMixing",
            "radiant_exchange_method": "GroupedZones",
            "simple_mixing_air_changes_per_hour": 0.5,
            "solar_and_daylighting_method": "GroupedZones"
        }
    }
}

air_boundary_warnings = {
    "Construction:AirBoundary": {
        "Air Wall": {
            "air_exchange_method": "SimpleMixing",
            "radiant_exchange_method": "IRTSurface",
            "simple_mixing_air_changes_per_hour": 0.5,
            "solar_and_daylighting_method": "InteriorWindow"
        }
    }
}

air_boundary_expected = {
    "Construction:AirBoundary": {
        "Air Wall": {
            "air_exchange_method": "SimpleMixing",
            "simple_mixing_air_changes_per_hour": 0.5
        }
    }
}

def compare(left, right):
    return all((left.get(k) == v for k, v in right.items()))

def test_air_boundary():
    upgrade = Upgrade()
    patch = upgrade.generate_patch(air_boundary)
    assert len(patch) == 2
    jp = jsonpatch.JsonPatch(patch)
    new_epjson = jp.apply(air_boundary)
    assert compare(air_boundary_expected["Construction:AirBoundary"]["Air Wall"],new_epjson["Construction:AirBoundary"]["Air Wall"])
    with pytest.warns(UpgradeWarning) as record:
        patch = upgrade.generate_patch(air_boundary_warnings)
    assert len(patch) == 2
    jp = jsonpatch.JsonPatch(patch)
    new_epjson = jp.apply(air_boundary)
    assert compare(air_boundary_expected["Construction:AirBoundary"]["Air Wall"],new_epjson["Construction:AirBoundary"]["Air Wall"])
    assert len(record) == 2
