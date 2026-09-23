# SPDX-FileCopyrightText: 2023-present Oak Ridge National Laboratory, managed by UT-Battelle
#
# SPDX-License-Identifier: BSD-3-Clause
import importlib
import json
import re
from functools import lru_cache
from pathlib import Path

import jsonpatch
import jsonschema_rs
import pytest

import energyplus_version
from energyplus_version import EnergyPlusVersion


PROJECT_ROOT = Path(__file__).parents[1]
SCHEMA_ROOT = PROJECT_ROOT / "schema"
TEST_FILES_ROOT = PROJECT_ROOT / "test_files"
VERSION_MODULE_PATTERN = re.compile(r"version_(\d+)_(\d+)_(\d+)$")


def version_directory(root, version):
    directory = root / version
    if not directory.is_dir():
        raise FileNotFoundError(f'No data directory found for EnergyPlus {version} under "{root}".')
    return directory


def discover_upgrades():
    package_directory = Path(energyplus_version.__file__).parent
    upgrades = []

    for module_path in package_directory.glob("version_*.py"):
        match = VERSION_MODULE_PATTERN.fullmatch(module_path.stem)
        if match is None:
            continue

        module_version = ".".join(match.groups())
        module = importlib.import_module(f"energyplus_version.{module_path.stem}")
        upgrade = module.Upgrade()
        if upgrade.from_version() != module_version:
            raise ValueError(
                f'Upgrade module "{module_path.stem}" declares source version '
                f'"{upgrade.from_version()}" instead of "{module_version}".'
            )
        upgrades.append((module_version, upgrade.to_version()))

    return sorted(upgrades, key=lambda item: tuple(int(part) for part in item[0].split(".")))


def integration_parameters():
    parameters = []
    for source_version, destination_version in discover_upgrades():
        source_directory = version_directory(TEST_FILES_ROOT, source_version)
        source_files = sorted(source_directory.rglob("*.epJSON"))
        if not source_files:
            parameters.append((source_version, destination_version, None))
            continue
        parameters.extend(
            (source_version, destination_version, source_file)
            for source_file in source_files
        )
    return parameters


@lru_cache
def validator(version):
    schema_path = version_directory(SCHEMA_ROOT, version) / "Energy+.schema.epJSON"
    with schema_path.open(encoding="utf-8") as schema_file:
        return jsonschema_rs.Draft7Validator(json.load(schema_file))


def parameter_id(parameter):
    source_version, _, source_file = parameter
    if source_file is None:
        return f"{source_version}:no-test-files"
    relative_path = source_file.relative_to(version_directory(TEST_FILES_ROOT, source_version))
    return f"{source_version}:{relative_path.as_posix()}"


PARAMETERS = integration_parameters()


@pytest.mark.parametrize(
    "source_version,destination_version,filename",
    PARAMETERS,
    ids=[parameter_id(parameter) for parameter in PARAMETERS],
)
def test_does_it_run(source_version, destination_version, filename):
    assert filename is not None, f"No epJSON test files found for EnergyPlus {source_version}."

    with filename.open(encoding="utf-8") as epjson_file:
        epjson = json.load(epjson_file)

    validator(source_version).validate(epjson)
    version_string = next(iter(epjson["Version"].values()))["version_identifier"]
    normalized_version = str(EnergyPlusVersion.from_energyplus_identifier(version_string))
    assert normalized_version == source_version

    module_name = f"energyplus_version.version_{source_version.replace('.', '_')}"
    upgrade = importlib.import_module(module_name).Upgrade()
    assert upgrade.to_version() == destination_version

    patch = upgrade.generate_patch(epjson)
    upgraded_epjson = jsonpatch.JsonPatch(patch).apply(epjson)

    assert upgraded_epjson
    json.dumps(upgraded_epjson)
    validator(destination_version).validate(upgraded_epjson)
