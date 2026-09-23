# SPDX-FileCopyrightText: 2023-present Oak Ridge National Laboratory, managed by UT-Battelle
#
# SPDX-License-Identifier: BSD-3-Clause
import energyplus_version
import jsonpatch

class LocalUpgrade(energyplus_version.Upgrade):
    def __init__(self, changes):
        self.change_list = changes
    def changes(self):
        return self.change_list

class LocalVariableRenameUpgrade(LocalUpgrade):
    def variable_renames(self):
        return {'Old Report Variable': 'New Report Variable'}

def test_generic_upgrades():
    obj = {'Test': {'test_one': {'field_one': 1.0, 'field_two': 2.0}}}
    # Single change
    upgrade = LocalUpgrade([energyplus_version.ChangeFieldName('Test', 'field_one', 'field_uno')])
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

def test_variable_renames_are_applied_to_direct_and_extensible_references():
    model = {
        'Output:Variable': {
            'Direct/Reference': {
                'variable_name': 'old report variable [W]',
            },
        },
        'EnergyManagementSystem:Sensor': {
            'Sensor': {
                'output_variable_or_output_meter_name': 'Old Report Variable',
            },
        },
        'Output:Table:Monthly': {
            'Monthly Table': {
                'variable_details': [
                    {
                        'variable_or_meter_name': 'OLD REPORT VARIABLE',
                        'aggregation_type_for_variable_or_meter': 'Maximum',
                    },
                ],
            },
        },
        'Meter:Custom': {
            'Custom Meter': {
                'variable_details': [
                    {
                        'key_name': '*',
                        'output_variable_or_meter_name': 'Old Report Variable',
                    },
                ],
            },
        },
    }

    patch = LocalVariableRenameUpgrade([]).generate_patch(model)
    upgraded = jsonpatch.JsonPatch(patch).apply(model)

    assert upgraded['Output:Variable']['Direct/Reference']['variable_name'] == 'New Report Variable'
    assert (
        upgraded['EnergyManagementSystem:Sensor']['Sensor']['output_variable_or_output_meter_name']
        == 'New Report Variable'
    )
    assert (
        upgraded['Output:Table:Monthly']['Monthly Table']['variable_details'][0]['variable_or_meter_name']
        == 'New Report Variable'
    )
    assert (
        upgraded['Meter:Custom']['Custom Meter']['variable_details'][0]['output_variable_or_meter_name']
        == 'New Report Variable'
    )

class LocalEpUpgrade(energyplus_version.EnergyPlusUpgrade):
    def changes(self):
        return [
            energyplus_version.ChangeFieldName('RunPeriod', 'treat_weather_as_actual', 'leap_year_pedantry')
        ]
    def from_version(self):
        return '22.1.0'
    def to_version(self):
        return '22.2.0'

def test_fake_upgrade():
    epjson = {
        "RunPeriod": {
            "Run Period 2": {
                "apply_weekend_holiday_rule": "No",
                "begin_day_of_month": 6,
                "begin_month": 7,
                "begin_year": 2021,
                "end_day_of_month": 14,
                "end_month": 7,
                "end_year": 2021,
                "use_weather_file_daylight_saving_period": "Yes",
                "use_weather_file_holidays_and_special_days": "Yes",
                "use_weather_file_rain_indicators": "Yes",
                "use_weather_file_snow_indicators": "Yes"
            }
        },
        "Version": {
            "Pointless Name": {
                "version_identifier": "22.1"
            }
        }
    }
    upgrade = LocalEpUpgrade()
    assert upgrade.describe().startswith('Input Changes Version 22.1.0 to 22.2.0\n')
    patch = upgrade.generate_patch(epjson)
    assert len(patch) == 1
    upgraded = jsonpatch.JsonPatch(patch).apply(epjson)
    assert upgraded['Version']['Pointless Name']['version_identifier'] == '22.2'

    epjson['RunPeriod']['Run Period 2']['treat_weather_as_actual'] = True
    patch = upgrade.generate_patch(epjson)
    assert len(patch) == 2

def test_bad_energyplus_upgrade():
    epjson = {
        "RunPeriod": {
            "Run Period 2": {
                "apply_weekend_holiday_rule": "No",
                "begin_day_of_month": 6,
                "begin_month": 7,
                "begin_year": 2021,
                "end_day_of_month": 14,
                "end_month": 7,
                "end_year": 2021,
                "use_weather_file_daylight_saving_period": "Yes",
                "use_weather_file_holidays_and_special_days": "Yes",
                "use_weather_file_rain_indicators": "Yes",
                "use_weather_file_snow_indicators": "Yes"
            }
        }
    }
    upgrade = LocalEpUpgrade()
    patch = upgrade.generate_patch(epjson)
    assert patch == []
