# SPDX-FileCopyrightText: 2023-present Oak Ridge National Laboratory, managed by UT-Battelle
#
# SPDX-License-Identifier: BSD-3-Clause
import pytest
import jsonpatch
import glob
import os
import itertools
import json
import importlib
import jsonschema_rs

from energyplus_version import EnergyPlusVersion

versions = ['23.2.0']


def version_directory(version):
    return '.'.join(version.split('.')[:2])


files = {
    version: glob.glob(os.path.join('test_files', version_directory(version), '*.epJSON'))
    for version in versions
}
parameters = list(itertools.chain(*[[(version, file) for file in files[version]] for version in versions]))


# This should probably be moved into a fixture at some point
def load_schema(version):
    schema_filepath = os.path.join('schema', version_directory(version), 'Energy+.schema.epJSON')
    with open(schema_filepath) as schema_file:
        schema_data = json.load(schema_file)
    return schema_data


validators = {
    version: jsonschema_rs.Draft7Validator(load_schema(version))
    for version in ['23.2.0', '24.1.0']
}


def validate_json(json_data, version):
    return validators[version].is_valid(json_data)


@pytest.mark.parametrize("version, filename", parameters)
def test_does_it_run(version, filename):
    with open(filename, 'r') as fp:
        epjson = json.load(fp)
    version_string = list(epjson['Version'].values())[0]['version_identifier']
    normalized_version = str(EnergyPlusVersion.from_string(version_string))
    assert normalized_version == version
    # Load the right Upgrade here
    mod = importlib.import_module('energyplus_version.version_%s' % version.replace('.', '_'))
    upgrade = mod.Upgrade()
    # Generate the patch
    patch = upgrade.generate_patch(epjson)
    jp = jsonpatch.JsonPatch(patch)
    # Apply the patch
    new_epjson = jp.apply(epjson)
    # Check if we got anything back
    assert new_epjson
    # Check that it is legal JSON
    json.dumps(new_epjson)
    # Check that the new data is valid according to the schema
    new_version = upgrade.to_version()
    assert validate_json(new_epjson, new_version)
