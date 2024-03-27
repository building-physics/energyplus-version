# SPDX-FileCopyrightText: 2023-present Oak Ridge National Laboratory, managed by UT-Battelle
#
# SPDX-License-Identifier: BSD-3-Clause
import energyplus_version as ev

def compute_field_PTAC(object, model):
    if object["cooling_coil_object_type"] == "Coil:Cooling:DX:VariableSpeed":
        return "Yes"
    return "No"

def compute_field_PTHP(object, model):
    if object["cooling_coil_object_type"]=="Coil:Cooling:DX:VariableSpeed":
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
        self.curve_id = 0

    def generate_patch(self, model: dict) -> list:
        patch = []
        table_added = False
        if self.object in model:
            for name, object in model[self.object].items():
                for field_75_name, field_100_name in HXA2ASL_fields.items():
                    if field_75_name in object:
                        # Remove fields
                        path = '/%s/%s/%s' % (self.object, name, field_75_name)
                        patch.append({'op': 'remove', 'path': path})
                        # Generate curves
                        if field_100_name in object:
                            if object[field_75_name] != object[field_100_name]:
                                self.curve_id += 1
                                table_added = True
                                curve_name = '%s_%d' % (name, self.curve_id)
                                curve_dict = self.curve_object(object[field_100_name], object[field_75_name])
                                # Add at one level higher if there are not Table:Lookup objects
                                if 'Table:Lookup' not in model:
                                    curve_dict = {curve_name: curve_dict}
                                    path = '/Table:Lookup'
                                else:
                                    path = '/Table:Lookup/%s' % curve_name
                                patch.append({'op': 'add', 'path': path, 'value': curve_dict})
                                # Connect the curve
                                curve_field_name = HXA2SL_curves[field_75_name]
                                path = '/%s/%s/%s' % (self.object, name, curve_field_name)
                                patch.append({'op': 'add', 'path': path, 'value': curve_name})
        if table_added:
            value = {
                'independent_variables': [{'independent_variable_name':'airFlowRatio'}]
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
            path = '/Table:IndependentVariable/airflowRatio'
            if 'Table:IndependentVariable' not in model:
                value = {'airflowRatio': value}
                path = '/Table:IndependentVariable'
            patch.append({'op': 'add', 'path': path, 'value': value})
        return patch

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
