# SPDX-FileCopyrightText: 2023-present Oak Ridge National Laboratory, managed by UT-Battelle
#
# SPDX-License-Identifier: BSD-3-Clause
import energyplus_version as ev

class Upgrade(ev.EnergyPlusUpgrade):
    def changes(self):
        return [
            ev.ChangeFieldName('Site:GroundTemperature:Undisturbed:Xing',
                               'average_soil_surface_tempeature',
                               'average_soil_surface_temperature')
        ]

    def from_version(self):
        return '23.1'
    
    def to_version(self):
        return '23.2'

