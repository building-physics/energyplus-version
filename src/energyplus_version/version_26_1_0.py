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


class ChangeReportVariableNames(ev.Change):
    """Update report-variable references handled by the official transition."""

    object = "Report variable references"

    direct_fields = {
        "Output:Variable": "variable_name",
        "Output:Table:TimeBins": "variable_name",
        "ExternalInterface:FunctionalMockupUnitImport:From:Variable": "output_variable_name",
        "ExternalInterface:FunctionalMockupUnitExport:From:Variable": "output_variable_name",
        "EnergyManagementSystem:Sensor": "output_variable_or_output_meter_name",
    }
    extensible_fields = {
        "Output:Table:Monthly": ("variable_details", "variable_or_meter_name"),
        "Meter:Custom": ("variable_details", "output_variable_or_meter_name"),
        "Meter:CustomDecrement": ("variable_details", "output_variable_or_meter_name"),
    }

    def __init__(self):
        self._renames = {
            old_name.casefold(): new_name
            for old_name, new_name in REPORT_VARIABLE_RENAMES.items()
        }

    @staticmethod
    def _pointer_token(value):
        return str(value).replace("~", "~0").replace("/", "~1")

    def _replacement(self, value):
        if not isinstance(value, str):
            return None
        # The Fortran transition ignores legacy unit suffixes while matching
        # report-variable names and writes the canonical new name.
        name_without_units = value.split("[", 1)[0].rstrip()
        return self._renames.get(name_without_units.casefold())

    def generate_patch(self, model):
        patch = []

        for object_type, field in self.direct_fields.items():
            for object_name, fields in model.get(object_type, {}).items():
                replacement = self._replacement(fields.get(field))
                if replacement is not None:
                    path = "/{}/{}/{}".format(
                        self._pointer_token(object_type),
                        self._pointer_token(object_name),
                        self._pointer_token(field),
                    )
                    patch.append({"op": "replace", "path": path, "value": replacement})

        for object_type, (array_field, value_field) in self.extensible_fields.items():
            for object_name, fields in model.get(object_type, {}).items():
                for index, item in enumerate(fields.get(array_field, [])):
                    replacement = self._replacement(item.get(value_field))
                    if replacement is not None:
                        path = "/{}/{}/{}/{}/{}".format(
                            self._pointer_token(object_type),
                            self._pointer_token(object_name),
                            self._pointer_token(array_field),
                            index,
                            self._pointer_token(value_field),
                        )
                        patch.append({"op": "replace", "path": path, "value": replacement})

        return patch

    def describe(self):
        return "Update renamed report-variable references."


class Upgrade(ev.EnergyPlusUpgrade):
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
            ChangeReportVariableNames(),
        ]

    def from_version(self):
        return "26.1.0"

    def to_version(self):
        return "26.2.0"
