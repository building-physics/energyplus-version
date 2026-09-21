# SPDX-FileCopyrightText: 2023-present Oak Ridge National Laboratory, managed by UT-Battelle
#
# SPDX-License-Identifier: BSD-3-Clause
import energyplus_version as ev


REPORT_VARIABLE_RENAMES = {
    "Refrigeration Zone Air Chiller Sensible Heat Ratio":
        "Refrigeration Zone Air Chiller Coil Sensible Heat Ratio",
    "Refrigeration Zone Air Chiller Frost Accumulation Mass":
        "Refrigeration Zone Air Chiller Coil Frost Accumulation Mass",
    "Refrigeration Zone Air Chiller Defrost Electricity Rate":
        "Refrigeration Zone Air Chiller Coil Defrost Electricity Rate",
    "Refrigeration Zone Air Chiller Defrost Electricity Energy":
        "Refrigeration Zone Air Chiller Coil Defrost Electricity Energy",
}


class Upgrade(ev.EnergyPlusUpgrade):
    def variable_renames(self):
        return REPORT_VARIABLE_RENAMES

    def changes(self):
        return [
            ev.RemoveField("CentralHeatPumpSystem", "control_method"),
            ev.RemoveField(
                "ChillerHeaterPerformance:Electric:EIR",
                "condenser_type",
            ),
            ev.ChangeFieldName(
                "ZoneControl:Humidistat",
                "humidifying_relative_humidity_setpoint_schedule_name",
                "humidifying_setpoint_schedule_name",
            ),
            ev.ChangeFieldName(
                "ZoneControl:Humidistat",
                "dehumidifying_relative_humidity_setpoint_schedule_name",
                "dehumidifying_setpoint_schedule_name",
            ),
        ]

    def from_version(self):
        return "26.1.0"

    def to_version(self):
        return "26.2.0"
