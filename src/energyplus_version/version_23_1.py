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
            ev.ChangeFieldName('Construction:ComplexFenestrationState',
                               'Outside Layer Directional Front Absoptance Matrix Name',
                               'Outside Layer Directional Front Absorptance Matrix Name'),
            ev.ChangeFieldName('Construction:ComplexFenestrationState',
                               'Outside Layer Directional Back Absoptance Matrix Name',
                               'Outside Layer Directional Back Absorptance Matrix Name'),
            ev.ChangeFieldName('Construction:ComplexFenestrationState',
                               'layer_2_directional_front_absoptance_matrix_name',
                               'layer_2_directional_front_absorptance_matrix_name'),
            ev.ChangeFieldName('Construction:ComplexFenestrationState',
                               'layer_2_directional_back_absoptance_matrix_name',
                               'layer_2_directional_back_absorptance_matrix_name'),
            ev.ChangeFieldName('Construction:ComplexFenestrationState',
                               'layer_3_directional_front_absoptance_matrix_name',
                               'layer_3_directional_front_absorptance_matrix_name'),
            ev.ChangeFieldName('Construction:ComplexFenestrationState',
                               'layer_3_directional_back_absoptance_matrix_name',
                               'layer_3_directional_back_absorptance_matrix_name'),
            ev.ChangeFieldName('Construction:ComplexFenestrationState',
                               'layer_4_directional_front_absoptance_matrix_name',
                               'layer_4_directional_front_absorptance_matrix_name'),
            ev.ChangeFieldName('Construction:ComplexFenestrationState',
                               'layer_4_directional_back_absoptance_matrix_name',
                               'layer_4_directional_back_absorptance_matrix_name'),
            ev.ChangeFieldName('Construction:ComplexFenestrationState',
                               'cfs_gap_1_directional_front_absoptance_matrix_name',
                               'cfs_gap_1_directional_front_absorptance_matrix_name'),
            ev.ChangeFieldName('Construction:ComplexFenestrationState',
                               'cfs_gap_1_directional_back_absoptance_matrix_name',
                               'cfs_gap_1_directional_back_absorptance_matrix_name'),
            ev.ChangeFieldName('Construction:ComplexFenestrationState',
                               'gap_2_directional_front_absoptance_matrix_name',
                               'gap_2_directional_front_absorptance_matrix_name'),
            ev.ChangeFieldName('Construction:ComplexFenestrationState',
                               'gap_2_directional_back_absoptance_matrix_name',
                               'gap_2_directional_back_absorptance_matrix_name'),
            ev.ChangeFieldName('Construction:ComplexFenestrationState',
                               'gap_3_directional_back_absoptance_matrix_name',
                               'gap_3_directional_back_absorptance_matrix_name'),
            ev.ChangeFieldName('Construction:ComplexFenestrationState',
                               'gap_4_directional_back_absoptance_matrix_name',
                               'gap_4_directional_back_absorptance_matrix_name'),

            
            ev.ChangeFieldName('Construction:ComplexFenestrationState',
                               'Gap X Directional Back Absoptance Matrix Name',
                               'Gap X Directional Back Absorptance Matrix Name'),

            ev.ChangeFieldName('Construction:ComplexFenestrationState',
                               'Gap X Directional Front Absoptance Matrix Name',
                               'Gap X Directional Front Absorptance Matrix Name'),

            
            ev.ChangeFieldName('Construction:ComplexFenestrationState',
                               'Gap X Directional Back Absoptance Matrix Name',
                               'Gap X Directional Back Absorptance Matrix Name'),


            ev.ChangeFieldName('Coil:Heating:Fuel',
                               'parasitic_electric_load',
                               'on_cycle_parasitic_electric_load'),
            ev.ChangeFieldName('Coil:Heating:Fuel',
                               'parasitic_fuel_load',
                               'off_cycle_parasitic_fuel_load'),
            ev.ChangeFieldName('Coil:Heating:Gas:MultiStage',
                               'parasitic_gas_load',
                               'off_cycle_parasitic_gas_load'),
            ev.ChangeFieldName('Coil:Heating:Gas:MultiStage',
                               'stage_1_parasitic_electric_load',
                               'stage_1_on_cycle_parasitic_electric_load'),
            ev.ChangeFieldName('Coil:Heating:Gas:MultiStage',
                               'stage_2_parasitic_electric_load',
                               'stage_2_on_cycle_parasitic_electric_load'),
            ev.ChangeFieldName('Coil:Heating:Gas:MultiStage',
                               'stage_3_parasitic_electric_load',
                               'stage_3_on_cycle_parasitic_electric_load'),
            ev.ChangeFieldName('Coil:Heating:Gas:MultiStage',
                               'stage_4_parasitic_electric_load',
                               'stage_4_on_cycle_parasitic_electric_load'),
            ev.ChangeFieldName('Coil:Heating:Desuperheater',
                               'parasitic_electric_load',
                               'on_cycle_parasitic_electric_load'),
            ev.ChangeFieldName('Boiler:HotWater',
                               'parasitic_electric_load',
                               'on_cycle_parasitic_electric_load'),
            ev.ChangeFieldName('SurfaceProperty:LocalEnvironment',
                               'External Shading Fraction Schedule Name',
                               'Sunlit Fraction Schedule Name'),
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

