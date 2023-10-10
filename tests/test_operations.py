# SPDX-FileCopyrightText: 2023-present Oak Ridge National Laboratory, managed by UT-Battelle
#
# SPDX-License-Identifier: BSD-3-Clause
import energyplus_version
import jsonpatch

def test_change_field_name():
    obj = {'Test': {'test_one': {'field_one': 1.0, 'field_two': 2.0}}}
    change = energyplus_version.ChangeFieldName('Test', 'field_one', 'field_uno')
    assert change.valid(obj['Test']['test_one'])
    patch = change.apply('test_one')
    assert len(patch) == 1
    expected = {'op': 'move', 'from': '/Test/test_one/field_one', 'path': '/Test/test_one/field_uno'}
    assert all((patch[0].get(k) == v for k, v in expected.items()))
    jp =jsonpatch.JsonPatch(patch)
    new_obj = jp.apply(obj)
    expected = {'Test': {'test_one': {'field_uno': 1.0, 'field_two': 2.0}}}
    assert all((new_obj['Test']['test_one'].get(k) == v for k, v in expected['Test']['test_one'].items()))
    assert change.describe() == 'Change the field named "field_one" to "field_uno".'

def test_remove_field():
    obj = {'Test': {'test_one': {'field_one': 1.0, 'field_two': 2.0}}}
    change = energyplus_version.RemoveField('Test', 'field_two')
    assert change.valid(obj['Test']['test_one'])
    patch = change.apply('test_one')
    assert len(patch) == 1
    expected = {'op': 'remove', 'path': '/Test/test_one/field_two'}
    assert all((patch[0].get(k) == v for k, v in expected.items()))
    jp =jsonpatch.JsonPatch(patch)
    new_obj = jp.apply(obj)
    expected = {'Test': {'test_one': {'field_one': 1.0}}}
    assert all((new_obj['Test']['test_one'].get(k) == v for k, v in expected['Test']['test_one'].items()))
    assert change.describe() == 'Remove the field named "field_two".'

