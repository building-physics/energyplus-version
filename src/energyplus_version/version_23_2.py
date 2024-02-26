# SPDX-FileCopyrightText: 2023-present Oak Ridge National Laboratory, managed by UT-Battelle
#
# SPDX-License-Identifier: BSD-3-Clause
import energyplus_version as ev

class Upgrade(ev.EnergyPlusUpgrade):
    def changes(self):
        return [
            # Changes go here
        ]

    def from_version(self):
        return '23.2'
    
    def to_version(self):
        return '24.1'

