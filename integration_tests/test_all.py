# SPDX-FileCopyrightText: 2023-present Oak Ridge National Laboratory, managed by UT-Battelle
#
# SPDX-License-Identifier: BSD-3-Clause
import pytest
import jsonpatch
import glob
import os
import itertools
import json
import jsonschema
import importlib

versions = ['9.4', '23.1', '23.2']
files = {version: glob.glob(os.path.join('test_files', version, '*.epJSON')) for version in versions}
parameters = list(itertools.chain(*[[(version, file) for file in files[version]] for version in versions]))

# This should probably be moved into a fixture at some point
def load_schema(version):
    schema_filepath = os.path.join('schema', version, 'Energy+.schema.epJSON')
    with open(schema_filepath) as schema_file:
        schema_data=json.load(schema_file)
    return schema_data 
    
schemas = {version: load_schema(version) for version in ['9.4', '23.1', '23.2', '24.1']}

def validate_json(json_data, version):
    try:
        jsonschema.validate(instance=json_data, schema=schemas[version])
        return True
    except jsonschema.exceptions.ValidationError:
        return False

@pytest.mark.parametrize("version, filename", parameters)
def test_does_it_run(version, filename):
    with open(filename, 'r') as fp:
        epjson = json.load(fp)
    version_string = list(epjson['Version'].values())[0]['version_identifier']
    assert version_string == version
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
    if float(version)>22: #There are issues with V9.4 which needs to be addressed later
        # Check that the new data is valid accordoing to the schema
        new_version=upgrade.to_version()
        assert validate_json(new_epjson,new_version)