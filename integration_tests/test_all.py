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

versions = ['9.4', '23.1', '23.2']
files = {version: glob.glob(os.path.join('test_files', version, '*.epJSON')) for version in versions}
parameters = list(itertools.chain(*[[(version, file) for file in files[version]] for version in versions]))

@pytest.mark.parametrize("version, filename", parameters)
def test_does_it_run(version, filename):
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
    assert len(new_epjson) > 0
