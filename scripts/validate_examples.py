# SPDX-FileCopyrightText: 2023-present Oak Ridge National Laboratory, managed by UT-Battelle
#
# SPDX-License-Identifier: BSD-3-Clause
import sys
import os
import glob
import json
import jsonschema

def usage():
    print('usage: validate_examples.py VERSION')

if len(sys.argv) != 2:
    usage()
    exit(1)

version = sys.argv[1]

script_directory = os.path.dirname(os.path.abspath(sys.argv[0]))

version_path = os.path.join(script_directory, '..', 'test_files', version)
schema_path = os.path.join(script_directory, '..', 'schema', version,'Energy+.schema.epJSON')

if not os.path.exists(version_path):
    print('Failed to find path to test files "%s"' % version_path)
    usage()
    exit(1)

if not os.path.exists(schema_path):
    print('Failed to find the specified schema "%s"' % schema_path)
    usage()
    exit(1)


files = glob.glob(os.path.join(version_path, '*.epJSON'))


with open(schema_path) as schema_file:
    schema_data=json.load(schema_file)

failures = []
for file in files:
    basename = os.path.basename(file)
    #print(basename)
    with open(file, 'r') as fp:
        data = json.load(fp)
    try:
        jsonschema.validate(instance=data, schema=schema_data)
        sys.stdout.write('.')
    except jsonschema.exceptions.ValidationError:
        sys.stdout.write('F')
        failures.append(file)
    sys.stdout.flush()

sys.stdout.write('\n')
for file in failures:
    print(file,'failed')
    
