# SPDX-FileCopyrightText: 2023-present Oak Ridge National Laboratory, managed by UT-Battelle
#
# SPDX-License-Identifier: BSD-3-Clause
import energyplus_version as ev


class Upgrade(ev.EnergyPlusUpgrade):
    def changes(self):
        return [
            ev.RemoveField(
                "AirTerminal:SingleDuct:ParallelPIU:Reheat",
                "reheat_coil_air_inlet_node_name",
            ),
            ev.RemoveField(
                "AirTerminal:SingleDuct:SeriesPIU:Reheat",
                "reheat_coil_air_inlet_node_name",
            ),
        ]

    def from_version(self):
        return "25.2.0"

    def to_version(self):
        return "26.1.0"
