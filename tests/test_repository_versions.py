# SPDX-FileCopyrightText: 2023-present Oak Ridge National Laboratory, managed by UT-Battelle
#
# SPDX-License-Identifier: BSD-3-Clause
import importlib
import re
from pathlib import Path

from energyplus_version import EnergyPlusVersion


PROJECT_ROOT = Path(__file__).parents[1]
DOTTED_VERSION_PATTERN = re.compile(r"\d+\.\d+\.\d+")
MODULE_VERSION_PATTERN = re.compile(r"version_(\d+)_(\d+)_(\d+)")
MANIFEST_PATTERN = re.compile(r"\d+\.\d+\.\d+-to-\d+\.\d+\.\d+\.json")
RULE_PATTERNS = (
    re.compile(r"Rules\d+-\d+-\d+-to-\d+-\d+-\d+\.md"),
    re.compile(r"OutputChanges\d+-\d+-\d+-to-\d+-\d+-\d+\.md"),
    re.compile(r"Report Variables \d+-\d+-\d+ to \d+-\d+-\d+\.csv"),
)


def test_version_data_directories_use_three_components():
    for root_name in ("schema", "test_files", "idd"):
        directories = (path for path in (PROJECT_ROOT / root_name).iterdir() if path.is_dir())
        invalid = sorted(path.name for path in directories if DOTTED_VERSION_PATTERN.fullmatch(path.name) is None)
        assert invalid == [], f"Invalid version directories under {root_name}: {invalid}"


def test_upgrade_modules_and_declarations_use_three_components():
    package_root = PROJECT_ROOT / "src" / "energyplus_version"
    for module_path in package_root.glob("version_*.py"):
        match = MODULE_VERSION_PATTERN.fullmatch(module_path.stem)
        assert match is not None, f"Invalid upgrade module name: {module_path.name}"

        source_version = ".".join(match.groups())
        module = importlib.import_module(f"energyplus_version.{module_path.stem}")
        upgrade = module.Upgrade()
        assert upgrade.from_version() == source_version
        assert EnergyPlusVersion.from_string(upgrade.to_version()) is not None


def test_manifest_names_use_three_component_versions():
    invalid = sorted(
        path.name
        for path in (PROJECT_ROOT / "manifests").iterdir()
        if path.is_file() and MANIFEST_PATTERN.fullmatch(path.name) is None
    )
    assert invalid == []


def test_rule_asset_names_use_three_component_versions():
    invalid = sorted(
        path.name
        for path in (PROJECT_ROOT / "rules").iterdir()
        if path.is_file() and not any(pattern.fullmatch(path.name) for pattern in RULE_PATTERNS)
    )
    assert invalid == []
