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
import sys

pwd=os.getcwd()
parent_dir=os.path.dirname(pwd)
folder=os.path.join(parent_dir,"src")
sys.path.append(folder)

versions = ['23.1']#,'9.4'] #'9.4',
files = {version: glob.glob(os.path.join('..\\test_files', version, '*.epJSON')) for version in versions}
parameters = list(itertools.chain(*[[(version, file) for file in files[version]] for version in versions]))



def validate_json(json_data, schema_filepath):
    
    with open(schema_filepath) as schema_file:
        schema_data=json.load(schema_file) 
    try:
        jsonschema.validate(instance=json_data, schema=schema_data)
        #print("JSON is valid against the schema.")
        return True
    except:
        #print("JSON is not valid against the schema:")
        jsonschema.validate(instance=json_data, schema=schema_data)
        return False
    


@pytest.mark.parametrize("version, filename", parameters)
def test_does_it_run(version, filename):
    if float(version)>22: #There are issues with V9.4 which needs to be addressed later
        with open(filename, 'r') as fp:
            epjson = json.load(fp)
        version_string = list(epjson['Version'].values())[0]['version_identifier']
        assert version_string == version
        # Load the right Upgrade here
        mod = importlib.import_module('energyplus_version.version_%s' % version.replace('.', '_'))
        upgrade = mod.Upgrade()
        patch = upgrade.generate_patch(epjson)
        jp = jsonpatch.JsonPatch(patch)
        new_epjson = jp.apply(epjson)
       
        schema="..//schema//"+version_string+"//Energy+.schema.epJSON"
        assert validate_json(epjson,schema)
        
    
        new_version=upgrade.to_version()
        new_schema="..//schema//"+new_version+"//Energy+.schema.epJSON"
        assert validate_json(new_epjson,new_schema)
  

# =============================================================================
# 
# if __name__ == "__main__":    
#     for element in parameters[0:5]:
#         test_does_it_run(element[0],element[1])
# =============================================================================



