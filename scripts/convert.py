# SPDX-FileCopyrightText: 2023-present Oak Ridge National Laboratory, managed by UT-Battelle
#
# SPDX-License-Identifier: BSD-3-Clause
import sys
import os
import glob
import shutil

def usage():
    print('usage: convert.py PATH/TO/EXAMPLE/FILES PATH/TO/CONVERTER')

if len(sys.argv) != 3:
    usage()
    exit(1)

filepath = sys.argv[1]
convert_exe = sys.argv[2]

if not os.path.exists(filepath):
    print('Failed to find path "%s"' % filepath)
    usage()
    exit(1)

if not os.path.exists(convert_exe):
    print('Failed to find converter "%s"' % convert_exe)
    usage()
    exit(1)

files = glob.glob(os.path.join(filepath, '*.idf'))

# Convert IDFs
report = open('report.txt', 'w')
for file in files:
    basename = os.path.basename(file)
    target = basename[:-4] + '.epJSON'
    if os.path.exists(target):
        #print('Skipping', file)
        continue
    os.system("%s -o . %s" %(convert_exe, file))
    report.write(basename + '\n')
report.close()

# Copy over epJSONs
files = glob.glob(os.path.join(filepath, '*.epJSON'))
for file in files:
    basename = os.path.basename(file)
    if not os.path.exists(basename):
        shutil.copy(file, basename)
    
    
