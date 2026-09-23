# SPDX-FileCopyrightText: 2023-present Oak Ridge National Laboratory, managed by UT-Battelle
#
# SPDX-License-Identifier: BSD-3-Clause
import energyplus_version
import pytest


def test_version():
    version = energyplus_version.EnergyPlusVersion(22, 2, 0)
    assert str(version) == '22.2.0'
    assert str(version.previous()) == '22.1.0'
    assert str(version.next()) == '23.1.0'
    assert str(version.next().next()) == '23.2.0'
    assert str(version.next().previous()) == '22.2.0'


def test_version_requires_patch_component():
    with pytest.raises(TypeError):
        energyplus_version.EnergyPlusVersion(22, 2)


def test_errors():
    version = energyplus_version.EnergyPlusVersion.from_string('22.one')
    assert version is None

def test_version_string():
    assert energyplus_version.EnergyPlusVersion.from_string('22.2') is None

    version = energyplus_version.EnergyPlusVersion.from_string('22.2.0')
    assert str(version) == '22.2.0'
    assert str(version.previous()) == '22.1.0'
    assert str(version.next()) == '23.1.0'
    assert str(version.next().next()) == '23.2.0'
    assert str(version.next().previous()) == '22.2.0'


def test_patch_version_string():
    version = energyplus_version.EnergyPlusVersion.from_string('23.2.1')
    assert str(version) == '23.2.1'


@pytest.mark.parametrize(
    ('identifier', 'expected'),
    (
        ('22.2', '22.2.0'),
        ('23.2.1', '23.2.1'),
    ),
)
def test_parse_energyplus_input_identifier(identifier, expected):
    version = energyplus_version.EnergyPlusVersion.from_energyplus_identifier(identifier)
    assert str(version) == expected


@pytest.mark.parametrize(
    ('version', 'expected'),
    (
        ((22, 2, 0), '22.2'),
        ((23, 2, 1), '23.2'),
    ),
)
def test_energyplus_input_identifier_is_two_components(version, expected):
    assert energyplus_version.EnergyPlusVersion(*version).energyplus_identifier() == expected
