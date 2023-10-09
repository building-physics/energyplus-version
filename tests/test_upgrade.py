# SPDX-FileCopyrightText: 2023-present Oak Ridge National Laboratory, managed by UT-Battelle
#
# SPDX-License-Identifier: BSD-3-Clause
import energyplus_version
import jsonpatch

def test_generic_upgrade():
    obj = {'Test': {'field_one': 1.0, 'field_two': 2.0}}
    upgrade = energyplus_version.Upgrade()
    # Single change
    upgrade.changes = [energyplus_version.ChangeFieldName('Test', 'field_one', 'field_uno')]
    patch = upgrade.generate_patch(obj)
    #assert change.valid(obj['Test'])
    #patch = change.apply()
    assert len(patch) == 1
    #jp =jsonpatch.JsonPatch(patch)
    #new_obj = jp.apply(obj)
    #expected = {'Test': {'field_uno': 1.0, 'field_two': 2.0}}
    #assert all((new_obj.get(k) == v for k, v in expected.items()))
    #jp =jsonpatch.JsonPatch(patch)
    #new_obj = jp.apply(obj)
    #
    #
    assert upgrade.describe() == '# Object: Test\nChange the field named "field_one" to "field_uno".\n\n'
    # Two changes
    upgrade.changes.append(energyplus_version.ChangeFieldName('Test', 'field_two', 'field_dos'))
    patch = upgrade.generate_patch(obj)
    #assert change.valid(obj['Test'])
    #patch = change.apply()
    assert len(patch) == 2
    assert upgrade.describe() == '# Object: Test\nChange the field named "field_one" to "field_uno".\n\nChange the field named "field_two" to "field_dos".\n\n'

    unaff = {'Test': {'field_uno': 1.0, 'field_dos': 2.0}}
    patch = upgrade.generate_patch(unaff)
    assert patch == []
    nope = {'Nope': {'field_one': 1.0, 'field_two': 2.0}}
    patch = upgrade.generate_patch(nope)
    assert patch == []
