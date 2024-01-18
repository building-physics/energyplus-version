# SPDX-FileCopyrightText: 2023-present Oak Ridge National Laboratory, managed by UT-Battelle
#
# SPDX-License-Identifier: BSD-3-Clause
import sys
import os
import glob
import json

def usage():
    print('usage: find_object.py OBJECT VERSION')

if len(sys.argv) != 3:
    usage()
    exit(1)

object_name = sys.argv[1]
version = sys.argv[2]

script_directory = os.path.dirname(os.path.abspath(sys.argv[0]))

version_path = os.path.join(script_directory, '..', 'test_files', version)

if not os.path.exists(version_path):
    print('Failed to find path to test files "%s"' % version_path)
    usage()
    exit(1)


files = glob.glob(os.path.join(version_path, '*.epJSON'))

#report = open('report.txt', 'w')

for file in files:
    basename = os.path.basename(file)
    with open(file, 'r') as fp:
        data = json.load(fp)
    if object_name in data:
        print(basename)
        out = {object_name: data[object_name]}
        print(json.dumps(out, indent=4))
    #target = basename[:-4] + '.epJSON'
    #if os.path.exists(target):
    #    #print('Skipping', file)
    #    continue
    #os.system("%s -o . %s" %(convert_exe, file))
    #report.write(basename + '\n')

#report.close()
    
