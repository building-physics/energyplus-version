# SPDX-FileCopyrightText: 2023-present Oak Ridge National Laboratory, managed by UT-Battelle
#
# SPDX-License-Identifier: BSD-3-Clause
import energyplus_version as ev


REPORT_VARIABLE_RENAMES = {
    "Zone Hybrid Unitary HVAC DehumidificationLoad to Humidistat Setpoint Heat Tansfer Energy":
        "Zone Hybrid Unitary HVAC Dehumidification Load to Humidistat Setpoint Heat Transfer Energy",
    "Zone Hybrid Unitary HVAC Humidification Load to Humidistat Setpoint Heat Tansfer Energy":
        "Zone Hybrid Unitary HVAC Humidification Load to Humidistat Setpoint Heat Transfer Energy",
    "Infiltration Air Change Rate":
        "Infiltration Current Density Air Change Rate",
    "Zone Infiltration Air Change Rate":
        "Zone Infiltration Current Density Air Change Rate",
    "Zone Ventilation Air Change Rate":
        "Zone Ventilation Current Density Air Change Rate",
}


class Upgrade(ev.EnergyPlusUpgrade):
    def variable_renames(self):
        return REPORT_VARIABLE_RENAMES

    def changes(self):
        return []

    def from_version(self):
        return "24.2.0"

    def to_version(self):
        return "25.1.0"
