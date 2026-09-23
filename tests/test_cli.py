# SPDX-FileCopyrightText: 2023-present Oak Ridge National Laboratory, managed by UT-Battelle
#
# SPDX-License-Identifier: BSD-3-Clause
from pathlib import Path

from click.testing import CliRunner

from energyplus_version.cli import energyplus_version


PROJECT_ROOT = Path(__file__).parents[1]
INPUT_FIXTURE = PROJECT_ROOT / "tests" / "fixtures" / "23_2_0_to_24_1_0" / "input.epJSON"


def test_upgrade_dispatches_two_component_input_as_three_component_version():
    result = CliRunner().invoke(
        energyplus_version,
        ["upgrade", str(INPUT_FIXTURE), "--dry-run", "--verbose"],
    )

    assert result.exit_code == 0, result.output
    assert "Attempting to upgrade from version 23.2.0." in result.output


def test_describe_requires_three_component_version():
    result = CliRunner().invoke(energyplus_version, ["describe", "23.2"])

    assert result.exit_code != 0
    assert "use a three-component version such as 23.2.0" in result.output


def test_describe_dispatches_three_component_version():
    result = CliRunner().invoke(energyplus_version, ["describe", "23.2.0"])

    assert result.exit_code == 0, result.output
    assert result.output.startswith("Input Changes Version 23.2.0 to 24.1.0")
