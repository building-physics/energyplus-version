# SPDX-FileCopyrightText: 2023-present Oak Ridge National Laboratory, managed by UT-Battelle
#
# SPDX-License-Identifier: BSD-3-Clause
import energyplus_version as ev


class Upgrade(ev.EnergyPlusUpgrade):
    def variable_renames(self):
        return {
            **{
                f"{water_type} Water Thermal Storage {suffix}":
                    f"{water_type} Water Thermal Storage Tank {suffix}"
                for water_type in ("Chilled", "Hot")
                for suffix in (
                    "Final Tank Temperature",
                    "Use Side Mass Flow Rate",
                    "Use Side Inlet Temperature",
                    "Use Side Outlet Temperature",
                    "Use Side Heat Transfer Rate",
                    "Use Side Heat Transfer Energy",
                    "Source Side Mass Flow Rate",
                    "Source Side Inlet Temperature",
                    "Source Side Outlet Temperature",
                    "Source Side Heat Transfer Rate",
                    "Source Side Heat Transfer Energy",
                ) + tuple(
                    node_suffix
                    for node_number in range(1, 11)
                    for node_suffix in (
                        f"Temperature Node {node_number}",
                        f"Final Temperature Node {node_number}",
                    )
                )
            },
            "Zone Opaque Surface Inside Faces Total Conduction Heat Gain Rate":
                "Zone Opaque Surface Inside Faces Conduction Heat Gain Rate",
            "Zone Opaque Surface Inside Faces Total Conduction Heat Loss Rate":
                "Zone Opaque Surface Inside Faces Conduction Heat Loss Rate",
            "Zone Opaque Surface Inside Faces Total Conduction Heat Gain Energy":
                "Zone Opaque Surface Inside Faces Conduction Heat Gain Energy",
            "Zone Opaque Surface Inside Faces Total Conduction Heat Loss Energy":
                "Zone Opaque Surface Inside Faces Conduction Heat Loss Energy",
        }

    def changes(self):
        return [
            ev.RemoveField(
                "AirLoopHVAC:UnitaryHeatPump:AirToAir:MultiSpeed",
                "minimum_outdoor_dry_bulb_temperature_for_compressor_operation",
            ),
        ]

    def from_version(self):
        return "25.1.0"

    def to_version(self):
        return "25.2.0"
