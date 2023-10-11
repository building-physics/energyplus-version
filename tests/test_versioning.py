# SPDX-FileCopyrightText: 2023-present Oak Ridge National Laboratory, managed by UT-Battelle
#
# SPDX-License-Identifier: BSD-3-Clause
import energyplus_version
import jsonpatch

def test_version():
    version = energyplus_version.EnergyPlusVersion(22, 2)
    assert str(version) == '22.2'
    assert str(version.previous()) == '22.1'
    assert str(version.next()) == '23.1'
    assert str(version.next().next()) == '23.2'
    assert str(version.next().previous()) == '22.2'

def test_errors():
    version = energyplus_version.EnergyPlusVersion.from_string('22.one')
    assert version is None

def test_version_string():
    version = energyplus_version.EnergyPlusVersion.from_string('22.2')
    assert str(version) == '22.2'
    assert str(version.previous()) == '22.1'
    assert str(version.next()) == '23.1'
    assert str(version.next().next()) == '23.2'
    assert str(version.next().previous()) == '22.2'
    