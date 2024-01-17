# SPDX-FileCopyrightText: 2023-present Oak Ridge National Laboratory, managed by UT-Battelle
#
# SPDX-License-Identifier: BSD-3-Clause
import energyplus_version as ev
import warnings

def solar_and_daylighting_method_check(value):
    if value == 'InteriorWindow':
       warnings.warn('The "Solar and Daylighting Method" type "InteriorWindow" is no longer available, "GroupedZones" will be used')

def radiant_exchange_method_check(value):
    if value == 'IRTSurface':
        warnings.warn('The "Radiant Exchange Method" type "IRTSurface" is no longer available, "GroupedZones" will be used')

class Upgrade(ev.EnergyPlusUpgrade):
    def changes(self):
        return [
            ev.RemoveField('Construction:AirBoundary', 'solar_and_daylighting_method', check_value=solar_and_daylighting_method_check),
            ev.RemoveField('Construction:AirBoundary', 'radiant_exchange_method', check_value=radiant_exchange_method_check)

            # ev.ChangeFieldName('ZoneInfiltration:DesignFlowRate',
            #                    'zone_or_zonelist_name',
            #                    'zone_or_zonelist_or_space_or_spacelist_name'),
            # ev.ChangeFieldName('ZoneInfiltration:DesignFlowRate',
            #                    'flow_per_zone_floor_area',
            #                    'flow_rate_per_floor_area'),        
            # ev.ChangeFieldName('ZoneInfiltration:DesignFlowRate',
            #                    'flow_per_exterior_surface_area',
            #                    'flow_rate_per_exterior_surface_area'),

            # ev.ChangeFieldName('ZoneVentilation:DesignFlowRate',
            #                    'zone_or_zonelist_name',
            #                    'zone_or_zonelist_or_space_or_spacelist_name'),
            # ev.ChangeFieldName('ZoneVentilation:DesignFlowRate',
            #                    'flow_rate_per_zone_floor_area',
            #                    'flow_rate_per_floor_area'),

            # ev.ChangeFieldName('ZoneInfiltration:EffectiveLeakageArea', 'zone_name', 'zone_or_space_name'),
                            
            # ev.ChangeFieldName('ZoneInfiltration:FlowCoefficient', 'zone_name', 'zone_or_space_name'),
                            
            # ev.ChangeFieldName('ZoneVentilation:WindandStackOpenArea', 'zone_name', 'zone_or_space_name')

        ]

    def from_version(self):
        return '9.4'
    
    def to_version(self):
        return '9.5'

