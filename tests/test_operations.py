# SPDX-FileCopyrightText: 2023-present Oak Ridge National Laboratory, managed by UT-Battelle
#
# SPDX-License-Identifier: BSD-3-Clause
import energyplus_version
import jsonpatch

def test_change_field_name():
    obj = {'Test': {'field_one': 1.0, 'field_two': 2.0}}
    change = energyplus_version.ChangeFieldName('Test', 'field_one', 'field_uno')
    assert change.valid(obj['Test'])
    patch = change.apply()
    assert len(patch) == 1
    expected = {'op': 'move', 'from': '/Test/field_one', 'path': '/Test/field_uno'}
    assert all((patch[0].get(k) == v for k, v in expected.items()))
    jp =jsonpatch.JsonPatch(patch)
    new_obj = jp.apply(obj)
    expected = {'Test': {'field_uno': 1.0, 'field_two': 2.0}}
    assert all((new_obj['Test'].get(k) == v for k, v in expected['Test'].items()))

def test_remove_field():
    obj = {'Test': {'field_one': 1.0, 'field_two': 2.0}}
    change = energyplus_version.RemoveField('Test', 'field_two')
    assert change.valid(obj['Test'])
    patch = change.apply()
    assert len(patch) == 1
    expected = {'op': 'remove', 'path': '/Test/field_two'}
    assert all((patch[0].get(k) == v for k, v in expected.items()))
    jp =jsonpatch.JsonPatch(patch)
    new_obj = jp.apply(obj)
    expected = {'Test': {'field_one': 1.0}}
    assert all((new_obj['Test'].get(k) == v for k, v in expected['Test'].items()))

