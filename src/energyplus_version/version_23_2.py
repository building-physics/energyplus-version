# SPDX-FileCopyrightText: 2023-present Oak Ridge National Laboratory, managed by UT-Battelle
#
# SPDX-License-Identifier: BSD-3-Clause
import energyplus_version as ev

def compute_no_load_supply_air_flow_rate_control_set_to_low_speed(objects,model,name):
     
    selected_obj= model[objects][name]
    if objects == "ZoneHVAC:PackagedTerminalAirConditioner":
        if selected_obj["cooling_coil_object_type"]=="Coil:Cooling:DX:VariableSpeed":
            return "Yes"
        else:
            return "No"
        
    elif objects in ["AirloopHVAC:UnitarySystem","ZoneHVAC:PackagedTerminalHeatPump"]:
        if selected_obj["cooling_coil_object_type"]=="Coil:Cooling:DX:VariableSpeed":
            return "Yes"
        elif selected_obj["heating_coil_object_type"]=="Coil:Heating:DX:VariableSpeed":
            return "Yes"
        else:
            return "No"
    elif objects == "ZoneHVAC:WaterToAirHeatPump":
        return "No"
        
        
        

class Upgrade(ev.EnergyPlusUpgrade):
    def changes(self):
        return [
            # Changes go here
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
            
            ev.AddComputedField("ZoneHVAC:PackagedTerminalAirConditioner", "no_load_supply_air_flow_rate_control_set_to_low_speed",compute_no_load_supply_air_flow_rate_control_set_to_low_speed),
            ev.AddComputedField("ZoneHVAC:PackagedTerminalHeatPump","no_load_supply_air_flow_rate_control_set_to_low_speed",compute_no_load_supply_air_flow_rate_control_set_to_low_speed),
            ev.AddComputedField("ZoneHVAC:WaterToAirHeatPump","no_load_supply_air_flow_rate_control_set_to_low_speed",compute_no_load_supply_air_flow_rate_control_set_to_low_speed)
            
        ]

    def from_version(self):
        return '23.2'
    
    def to_version(self):
        return '24.1'
