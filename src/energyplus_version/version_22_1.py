# SPDX-FileCopyrightText: 2023-present Oak Ridge National Laboratory, managed by UT-Battelle
#
# SPDX-License-Identifier: BSD-3-Clause
from .upgrade import ChangeFieldName, RemoveField, Upgrade

class Version_22_1(Upgrade):
    def __init__(self):
        self.changes = [
            ChangeFieldName('Coil:Cooling:DX:SingleSpeed',
                            'rated_evaporator_fan_power_per_volume_flow_rate',
                            '2017_rated_evaporator_fan_power_per_volume_flow_rate'),
            
            ChangeFieldName('Coil:Heating:DX:SingleSpeed',
                            'rated_evaporator_fan_power_per_volume_flow_rate',
                            '2017_rated_evaporator_fan_power_per_volume_flow_rate'),

            RemoveField('FuelFactors', 'units_of_measure'),
            RemoveField('FuelFactors', 'energy_per_unit_factor'),

            ChangeFieldName('ZoneInfiltration:DesignFlowRate',
                            'zone_or_zonelist_name',
                            'zone_or_zonelist_or_space_or_spacelist_name'),
            ChangeFieldName('ZoneInfiltration:DesignFlowRate',
                            'flow_per_zone_floor_area',
                             'flow_rate_per_floor_area'),        
            ChangeFieldName('ZoneInfiltration:DesignFlowRate',
                            'flow_per_exterior_surface_area',
                            'flow_rate_per_exterior_surface_area'),

            ChangeFieldName('ZoneVentilation:DesignFlowRate',
                            'zone_or_zonelist_name',
                            'zone_or_zonelist_or_space_or_spacelist_name'),
            ChangeFieldName('ZoneVentilation:DesignFlowRate',
                            'flow_rate_per_zone_floor_area',
                             'flow_rate_per_floor_area'),

            ChangeFieldName('ZoneInfiltration:EffectiveLeakageArea', 'zone_name', 'zone_or_space_name'),
                            
            ChangeFieldName('ZoneInfiltration:FlowCoefficient', 'zone_name', 'zone_or_space_name'),
                            
            ChangeFieldName('ZoneVentilation:WindandStackOpenArea', 'zone_name', 'zone_or_space_name')

        ]

