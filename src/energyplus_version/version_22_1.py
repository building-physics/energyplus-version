# SPDX-FileCopyrightText: 2023-present Oak Ridge National Laboratory, managed by UT-Battelle
#
# SPDX-License-Identifier: BSD-3-Clause
import energyplus_version as ev

class Upgrade(ev.EnergyPlusUpgrade):
    def __init__(self):
        self.changes = [
            ev.ChangeFieldName('Coil:Cooling:DX:SingleSpeed',
                               'rated_evaporator_fan_power_per_volume_flow_rate',
                               '2017_rated_evaporator_fan_power_per_volume_flow_rate'),
            
            ev.ChangeFieldName('Coil:Heating:DX:SingleSpeed',
                               'rated_evaporator_fan_power_per_volume_flow_rate',
                               '2017_rated_evaporator_fan_power_per_volume_flow_rate'),

            ev.RemoveField('FuelFactors', 'units_of_measure'),
            ev.RemoveField('FuelFactors', 'energy_per_unit_factor'),

            ev.ChangeFieldName('ZoneInfiltration:DesignFlowRate',
                               'zone_or_zonelist_name',
                               'zone_or_zonelist_or_space_or_spacelist_name'),
            ev.ChangeFieldName('ZoneInfiltration:DesignFlowRate',
                               'flow_per_zone_floor_area',
                               'flow_rate_per_floor_area'),        
            ev.ChangeFieldName('ZoneInfiltration:DesignFlowRate',
                               'flow_per_exterior_surface_area',
                               'flow_rate_per_exterior_surface_area'),

            ev.ChangeFieldName('ZoneVentilation:DesignFlowRate',
                               'zone_or_zonelist_name',
                               'zone_or_zonelist_or_space_or_spacelist_name'),
            ev.ChangeFieldName('ZoneVentilation:DesignFlowRate',
                               'flow_rate_per_zone_floor_area',
                               'flow_rate_per_floor_area'),

            ev.ChangeFieldName('ZoneInfiltration:EffectiveLeakageArea', 'zone_name', 'zone_or_space_name'),
                            
            ev.ChangeFieldName('ZoneInfiltration:FlowCoefficient', 'zone_name', 'zone_or_space_name'),
                            
            ev.ChangeFieldName('ZoneVentilation:WindandStackOpenArea', 'zone_name', 'zone_or_space_name')

        ]

    def from_version(self):
        return '22.1'
    
    def to_version(self):
        return '22.2'

