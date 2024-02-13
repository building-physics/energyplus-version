# SPDX-FileCopyrightText: 2023-present Oak Ridge National Laboratory, managed by UT-Battelle
#
# SPDX-License-Identifier: BSD-3-Clause
import energyplus_version
import jsonpatch

def test_change_field_name():
    obj = {'Test': {'test_one': {'field_one': 1.0, 'field_two': 2.0}}}
    change = energyplus_version.ChangeFieldName('Test', 'field_one', 'field_uno')
    assert change.valid(obj)
    patch = change.generate_patch(obj)
    assert len(patch) == 1
    expected = {'op': 'move', 'from': '/Test/test_one/field_one', 'path': '/Test/test_one/field_uno'}
    assert all((patch[0].get(k) == v for k, v in expected.items()))
    jp =jsonpatch.JsonPatch(patch)
    new_obj = jp.apply(obj)
    expected = {'Test': {'test_one': {'field_uno': 1.0, 'field_two': 2.0}}}
    assert all((new_obj['Test']['test_one'].get(k) == v for k, v in expected['Test']['test_one'].items()))
    assert change.describe() == 'Change the field named "field_one" to "field_uno".'

def test_change_field_name_all():
    obj = {'Test': {'test_one': {'field_one': 1.0, 'field_two': 2.0}}}
    change = energyplus_version.ChangeFieldName('Test', 'field_one', 'field_uno')
    assert change.valid(obj)
    patch = change.generate_patch(obj)
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
    assert change.valid(obj)
    patch = change.generate_patch(obj)
    assert len(patch) == 1
    expected = {'op': 'remove', 'path': '/Test/test_one/field_two'}
    assert all((patch[0].get(k) == v for k, v in expected.items()))
    jp =jsonpatch.JsonPatch(patch)
    new_obj = jp.apply(obj)
    expected = {'Test': {'test_one': {'field_one': 1.0}}}
    assert all((new_obj['Test']['test_one'].get(k) == v for k, v in expected['Test']['test_one'].items()))
    assert change.describe() == 'Remove the field named "field_two".'

def test_remove_field_all():
    obj = {'Test': {'test_one': {'field_one': 1.0, 'field_two': 2.0}}}
    change = energyplus_version.RemoveField('Test', 'field_two')
    assert change.valid(obj)
    patch = change.generate_patch(obj)
    assert len(patch) == 1
    expected = {'op': 'remove', 'path': '/Test/test_one/field_two'}
    assert all((patch[0].get(k) == v for k, v in expected.items()))
    jp =jsonpatch.JsonPatch(patch)
    new_obj = jp.apply(obj)
    expected = {'Test': {'test_one': {'field_one': 1.0}}}
    assert all((new_obj['Test']['test_one'].get(k) == v for k, v in expected['Test']['test_one'].items()))
    assert change.describe() == 'Remove the field named "field_two".'

def test_map_field_value():
    obj = {'Test': {'test_one': {'field_one': 'A', 'field_two': 'B'}}}
    change = energyplus_version.MapValues('Test', 'field_one', {'A': 'Z', 'B': 'Y'})
    assert change.valid(obj['Test']['test_one'])
    patch = change.apply('test_one', obj['Test']['test_one'])
    assert len(patch) == 1
    expected = {'op': 'replace', 'path': '/Test/test_one/field_one', 'value': 'Z'}
    assert all((patch[0].get(k) == v for k, v in expected.items()))
    jp =jsonpatch.JsonPatch(patch)
    new_obj = jp.apply(obj)
    expected = {'Test': {'test_one': {'field_one': 'Z', 'field_two': 'B'}}}
    assert all((new_obj['Test']['test_one'].get(k) == v for k, v in expected['Test']['test_one'].items()))
    assert change.describe() == 'Change the values of field named "field_one" as follows: "A" to "Z", "B" to "Y".'

def test_map_field_value():
    obj = {'Test': {'test_one': {'field_one': 'A', 'field_two': 'B'}}}
    change = energyplus_version.MapValues('Test', 'field_one', {'A': 'Z', 'B': 'Y'})
    assert change.valid(obj)
    patch = change.generate_patch(obj)
    assert len(patch) == 1
    expected = {'op': 'replace', 'path': '/Test/test_one/field_one', 'value': 'Z'}
    assert all((patch[0].get(k) == v for k, v in expected.items()))
    jp =jsonpatch.JsonPatch(patch)
    new_obj = jp.apply(obj)
    expected = {'Test': {'test_one': {'field_one': 'Z', 'field_two': 'B'}}}
    assert all((new_obj['Test']['test_one'].get(k) == v for k, v in expected['Test']['test_one'].items()))
    assert change.describe() == 'Change the values of field named "field_one" as follows: "A" to "Z", "B" to "Y".'

def test_change_object_name():
    obj = {'Test': {'test_one': {'field_one': 'A', 'field_two': 'B'}}}
    change = energyplus_version.ChangeObjectName('Test', 'NotATest')
    patch = change.generate_patch(obj)
    assert len(patch) == 1
    expected = {'op': 'move', 'from': '/Test', 'path': '/NotATest'}
    assert all((patch[0].get(k) == v for k, v in expected.items()))
    jp =jsonpatch.JsonPatch(patch)
    new_obj = jp.apply(obj)
    expected = {'NotATest': {'test_one': {'field_one': 'A', 'field_two': 'B'}}}
    assert all((new_obj['NotATest']['test_one'].get(k) == v for k, v in expected['NotATest']['test_one'].items()))
    assert change.describe() == 'Change the name of the object named "Test" to "NotATest".'

def double_the_new_field(object, objects):
    if 'field_one' in object:
        return str(object['field_one'])
    return None

def test_new_double_field():
    objs = {'Test': {'test_one': {'field_one': 1.0, 'field_two': 2.0},
                     'test_two': {'field_two': 2.0}}}
    change = energyplus_version.ChangeFieldName('Test', 'field_one', 'field_uno')
    patch = change.apply_to_all(objs['Test'])
    assert len(patch) == 1
    #expected = {'op': 'move', 'from': '/Test/test_one/field_one', 'path': '/Test/test_one/field_uno'}
    #assert all((patch[0].get(k) == v for k, v in expected.items()))
    #jp =jsonpatch.JsonPatch(patch)
    #new_obj = jp.apply(obj)
    #expected = {'Test': {'test_one': {'field_uno': 1.0, 'field_two': 2.0}}}
    #assert all((new_obj['Test']['test_one'].get(k) == v for k, v in expected['Test']['test_one'].items()))
    #assert change.describe() == 'Change the field named "field_one" to "field_uno".'