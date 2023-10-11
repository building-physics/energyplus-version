# SPDX-FileCopyrightText: 2023-present Oak Ridge National Laboratory, managed by UT-Battelle
#
# SPDX-License-Identifier: BSD-3-Clause
import energyplus_version
import jsonpatch

class TestUpgrade(energyplus_version.Upgrade):
    def __init__(self, changes):
        self.change_list = changes
    def changes(self):
        return self.change_list

def test_generic_upgrades():
    obj = {'Test': {'test_one': {'field_one': 1.0, 'field_two': 2.0}}}
    # Single change
    upgrade = TestUpgrade([energyplus_version.ChangeFieldName('Test', 'field_one', 'field_uno')])
    patch = upgrade.generate_patch(obj)
    assert len(patch) == 1
    assert 'op' in patch[0]
    jp = jsonpatch.JsonPatch(patch)
    new_obj = jp.apply(obj)
    expected = {'Test': {'test_one': {'field_uno': 1.0, 'field_two': 2.0}}}
    assert all((new_obj['Test']['test_one'].get(k) == v for k, v in expected['Test']['test_one'].items()))
    assert upgrade.describe() == '# Object Change: Test\nChange the field named "field_one" to "field_uno".\n\n'
    # Two changes
    upgrade.change_list.append(energyplus_version.ChangeFieldName('Test', 'field_two', 'field_dos'))
    patch = upgrade.generate_patch(obj)
    assert len(patch) == 2
    assert 'op' in patch[0]
    assert 'op' in patch[1]
    jp = jsonpatch.JsonPatch(patch)
    new_obj = jp.apply(obj)
    expected = {'Test': {'test_one': {'field_uno': 1.0, 'field_dos': 2.0}}}
    assert all((new_obj['Test']['test_one'].get(k) == v for k, v in expected['Test']['test_one'].items()))
    assert upgrade.describe() == '# Object Change: Test\nChange the field named "field_one" to "field_uno".\n\nChange the field named "field_two" to "field_dos".\n\n'
    # No changes
    unaff = {'Test': {'test_one': {'field_uno': 1.0, 'field_dos': 2.0}}}
    patch = upgrade.generate_patch(unaff)
    assert patch == []
    nope = {'Nope': {'test_one': {'field_one': 1.0, 'field_two': 2.0}}}
    patch = upgrade.generate_patch(nope)
    assert patch == []
