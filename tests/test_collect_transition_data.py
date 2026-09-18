# SPDX-FileCopyrightText: 2023-present Oak Ridge National Laboratory, managed by UT-Battelle
#
# SPDX-License-Identifier: BSD-3-Clause
import argparse
import io
from contextlib import redirect_stderr
from pathlib import Path

import pytest

from scripts.collect_transition_data import (
    Version,
    clean_converter_diagnostic,
    print_failure_details,
    schema_declared_version,
    transition_source_paths,
)


def test_version_requires_and_preserves_patch_component():
    version = Version.parse("23.2.1")

    assert version.dotted() == "23.2.1"
    assert version.dashed() == "23-2-1"
    assert version.short() == "23.2"
    assert version.tag() == "v23.2.1"

    with pytest.raises(argparse.ArgumentTypeError):
        Version.parse("23.2")


def test_transition_source_paths():
    paths = transition_source_paths(Version.parse("23.2.0"), Version.parse("24.1.0"))

    assert paths["input_rules"].endswith("Rules23-2-0-to-24-1-0.md")
    assert paths["output_changes"].endswith("OutputChanges23-2-0-to-24-1-0.md")
    assert paths["report_variables"].endswith("Report Variables 23-2-0 to 24-1-0.csv")
    assert paths["fortran_reference"].endswith("CreateNewIDFUsingRulesV24_1_0.f90")


def test_schema_declared_version():
    schema = {
        "properties": {
            "Version": {
                "patternProperties": {
                    ".*": {"properties": {"version_identifier": {"default": 23.2}}}
                }
            }
        }
    }

    assert schema_declared_version(schema) == "23.2"


def test_verbose_failure_details():
    output = io.StringIO()
    conversion_failures = [
        {
            "source": "Example.idf",
            "expected_output": "Example.epJSON",
            "converter_exit_code": 1,
            "converter_message": "Unsupported object",
        }
    ]
    validation_failures = [{"file": "Invalid.epJSON", "error": "Required property is missing"}]

    with redirect_stderr(output):
        print_failure_details(conversion_failures, validation_failures)

    details = output.getvalue()
    assert "Example.idf" in details
    assert "ConvertInputFormat exit code: 1" in details
    assert "Unsupported object" in details
    assert "Invalid.epJSON" in details
    assert "Required property is missing" in details


def test_clean_converter_diagnostic():
    source = __file__
    diagnostic = clean_converter_diagnostic(
        "Missing required property 'Building'\n"
        "Errors occurred when validating input file. Preceding condition(s) cause termination.\n"
        f"Input file conversion failed: | 1/1 | {source}\n",
        "",
        Path(source),
    )

    assert diagnostic == "Missing required property 'Building'"
