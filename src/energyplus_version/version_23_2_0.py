# SPDX-FileCopyrightText: 2023-present Oak Ridge National Laboratory, managed by UT-Battelle
#
# SPDX-License-Identifier: BSD-3-Clause
import energyplus_version as ev

def compute_field_unitary_system(object, model):
    if (object.get("heating_coil_object_type") == "Coil:Heating:DX:VariableSpeed"
            or object.get("cooling_coil_object_type") == "Coil:Cooling:DX:VariableSpeed"):
        return "Yes"
    return "No"

def compute_field_PTAC(object, model):
    if object["cooling_coil_object_type"] == "Coil:Cooling:DX:VariableSpeed":
        return "Yes"
    return "No"

def compute_field_PTHP(object, model):
    if (object.get("heating_coil_object_type") == "Coil:Heating:DX:VariableSpeed"
            or object.get("cooling_coil_object_type") == "Coil:Cooling:DX:VariableSpeed"):
        return "Yes"
    return "No"
    
def compute_field_WAHP(object, model):
    return "No"

    
HXA2ASL_fields = {"sensible_effectiveness_at_75_heating_air_flow": "sensible_effectiveness_at_100_heating_air_flow",
                  "latent_effectiveness_at_75_heating_air_flow": "latent_effectiveness_at_100_heating_air_flow",
                  "sensible_effectiveness_at_75_cooling_air_flow": "sensible_effectiveness_at_100_cooling_air_flow",
                  "latent_effectiveness_at_75_cooling_air_flow": "latent_effectiveness_at_100_cooling_air_flow"}

HXA2SL_curves = {'sensible_effectiveness_at_75_heating_air_flow': 'sensible_effectiveness_of_heating_air_flow_curve_name',
                 'latent_effectiveness_at_75_heating_air_flow': 'latent_effectiveness_of_heating_air_flow_curve_name',
                 'sensible_effectiveness_at_75_cooling_air_flow': 'sensible_effectiveness_of_cooling_air_flow_curve_name',
                 'latent_effectiveness_at_75_cooling_air_flow': 'latent_effectiveness_of_cooling_air_flow_curve_name'}

class ChangeHXA2ASL(ev.Change):
    def __init__(self):
        self.object = "HeatExchanger:AirToAir:SensibleAndLatent"

    def generate_patch(self, model: dict) -> list:
        patch = []
        generated_curves = {}
        if self.object in model:
            for name, object in model[self.object].items():
                for curve_id, (field_75_name, field_100_name) in enumerate(HXA2ASL_fields.items(), start=1):
                    effect_75 = object.get(field_75_name, 0.0)
                    effect_100 = object.get(field_100_name, 0.0)
                    if field_75_name in object:
                        path = '/%s/%s/%s' % (self.object, self._pointer_token(name), field_75_name)
                        patch.append({'op': 'remove', 'path': path})

                    if effect_75 != effect_100:
                        curve_name = '%s_%d' % (name, curve_id)
                        generated_curves[curve_name] = self.curve_object(effect_100, effect_75)
                        curve_field_name = HXA2SL_curves[field_75_name]
                        path = '/%s/%s/%s' % (self.object, self._pointer_token(name), curve_field_name)
                        patch.append({'op': 'add', 'path': path, 'value': curve_name})

        if generated_curves:
            if 'Table:Lookup' in model:
                for curve_name, curve in generated_curves.items():
                    path = '/Table:Lookup/%s' % self._pointer_token(curve_name)
                    patch.append({'op': 'add', 'path': path, 'value': curve})
            else:
                patch.append({'op': 'add', 'path': '/Table:Lookup', 'value': generated_curves})

            value = {
                'independent_variables': [{'independent_variable_name':'HxAirFlowRatio'}]
            }
            path = '/Table:IndependentVariableList/effectiveness_IndependentVariableList'
            # Add at one level higher if there are no previous objects
            if 'Table:IndependentVariableList' not in model:
                value = {'effectiveness_IndependentVariableList': value}
                path = '/Table:IndependentVariableList'
            patch.append({'op': 'add', 'path': path, 'value': value})

            value = {
                'interpolation_method': 'Linear',
                'extrapolation_method': 'Linear',
                'minimum_value': 0.0,
                'maximum_value': 10.0,
                'unit_type': 'Dimensionless',
                'values': [{'value':0.75}, {'value':1.0}]
            }
            path = '/Table:IndependentVariable/HxAirFlowRatio'
            if 'Table:IndependentVariable' not in model:
                value = {'HxAirFlowRatio': value}
                path = '/Table:IndependentVariable'
            patch.append({'op': 'add', 'path': path, 'value': value})
        return patch

    @staticmethod
    def _pointer_token(value: str) -> str:
        return value.replace('~', '~0').replace('/', '~1')

    def curve_object(self, e100_i:float, e75_i:float)->dict:
        return {
            'independent_variable_list_name': 'effectiveness_IndependentVariableList',
            'normalization_method': 'DivisorOnly',
            'normalization_divisor': e100_i,
            'minimum_output': 0.0,
            'maximum_output': 10.0,
            'output_unit_type': 'Dimensionless',
            'values': [{'output_value':e75_i}, {'output_value':e100_i}]
        }

    def describe(self) -> str:
        return 'Modify the "HeatExchanger:AirToAir:SensibleAndLatent" object to add curves.'

class Upgrade(ev.EnergyPlusUpgrade):
    def changes(self):
        return [
            ev.AddComputedField("AirLoopHVAC:UnitarySystem",
                                "no_load_supply_air_flow_rate_control_set_to_low_speed",
                                compute_field_unitary_system),
            ev.ChangeFieldName("ElectricEquipment",
                               "watts_per_zone_floor_area", 
                               "watts_per_floor_area"),
            ev.ChangeFieldName("Lights",
                               "watts_per_zone_floor_area", 
                               "watts_per_floor_area"),
            ev.ChangeFieldName("ElectricEquipment:ITE:AirCooled",
                               "watts_per_zone_floor_area", 
                               "watts_per_floor_area"),
            ev.ChangeFieldName("GasEquipment",
                               "power_per_zone_floor_area", 
                               "power_per_floor_area"),
            ev.ChangeFieldName("HotWaterEquipment",
                               "power_per_zone_floor_area", 
                               "power_per_floor_area"),          
            ev.ChangeFieldName("SteamEquipment",
                               "power_per_zone_floor_area", 
                               "power_per_floor_area"),
            ev.ChangeFieldName("OtherEquipment",
                               "power_per_zone_floor_area", 
                               "power_per_floor_area"),
            ev.MapValues("People", "mean_radiant_temperature_calculation_type", {"ZoneAveraged":"EnclosureAveraged"}),
            ev.RemoveField("ComfortViewFactorAngles","zone_name"),
            
            ev.AddComputedField("ZoneHVAC:PackagedTerminalAirConditioner",
                                "no_load_supply_air_flow_rate_control_set_to_low_speed",
                                compute_field_PTAC),
            ev.AddComputedField("ZoneHVAC:PackagedTerminalHeatPump",
                                "no_load_supply_air_flow_rate_control_set_to_low_speed",
                                compute_field_PTHP),
            ev.AddComputedField("ZoneHVAC:WaterToAirHeatPump", "no_load_supply_air_flow_rate_control_set_to_low_speed",
                                compute_field_WAHP),
            ChangeHXA2ASL()
        ]

    def from_version(self):
        return '23.2.0'
    
    def to_version(self):
        return '24.1.0'
