# SPDX-FileCopyrightText: 2023-present Oak Ridge National Laboratory, managed by UT-Battelle
#
# SPDX-License-Identifier: BSD-3-Clause
import energyplus_version as ev

steam_map = {'Steam': 'DistrictHeatingSteam',
             'DistrictHeating': 'DistrictHeatingWater'}

class Upgrade(ev.EnergyPlusUpgrade):
    def changes(self):
        return [
            ev.ChangeFieldName('Site:GroundTemperature:Undisturbed:Xing',
                               'average_soil_surface_tempeature',
                               'average_soil_surface_temperature'),

            ev.ChangeObjectName('DistrictHeating', 'DistrictHeating:Water'),
            ev.MapValues('OtherEquipment', 'fuel_use', steam_map),
            ev.MapValues('Exterior:FuelEquipment', 'fuel_use_type', steam_map),
            ev.MapValues('ZoneHVAC:HybridUnitaryHVAC', 'first_fuel_type', steam_map),
            ev.MapValues('ZoneHVAC:HybridUnitaryHVAC', 'second_fuel_type', steam_map),
            ev.MapValues('ZoneHVAC:HybridUnitaryHVAC', 'third_fuel_type', steam_map),
            ev.MapValues('WaterHeater:Mixed', 'heater_fuel_type', steam_map),
            ev.MapValues('WaterHeater:Mixed', 'off_cycle_parasitic_fuel_type', steam_map),
            ev.MapValues('WaterHeater:Mixed', 'on_cycle_parasitic_fuel_type', steam_map),
            ev.MapValues('WaterHeater:Stratified', 'heater_fuel_type', steam_map),
            ev.MapValues('WaterHeater:Stratified', 'off_cycle_parasitic_fuel_type', steam_map),
            ev.MapValues('WaterHeater:Stratified', 'on_cycle_parasitic_fuel_type', steam_map),
            ev.MapValues('EnergyManagementSystem:MeteredOutputVariable', 'resource_type', steam_map),
            ev.MapValues('Meter:Custom', 'resource_type', steam_map),
            ev.MapValues('Meter:CustomDecrement', 'resource_type', steam_map),
            ev.MapValues('PythonPlugin:OutputVariable', 'resource_type', steam_map),
            ev.ChangeFieldName('EnvironmentalImpactFactors',
                               'district_heating_efficiency',
                               'district_heating_water_efficiency'),
            ev.ChangeFieldName('EnvironmentalImpactFactors',
                               'steam_conversion_efficiency',
                               'district_heating_steam_conversion_efficiency'),
            ev.MapValues('LifeCycleCost:UsePriceEscalation', 'resource', {'Steam': 'DistrictHeatingSteam'}),
            ev.MapValues('LifeCycleCost:UseAdjustment', 'resource', {'Steam': 'DistrictHeatingSteam'})
        ]

    def from_version(self):
        return '23.1'
    
    def to_version(self):
        return '23.2'

