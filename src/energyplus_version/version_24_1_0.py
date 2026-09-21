# SPDX-FileCopyrightText: 2023-present Oak Ridge National Laboratory, managed by UT-Battelle
#
# SPDX-License-Identifier: BSD-3-Clause
import energyplus_version as ev


REPORT_VARIABLE_RENAMES = {
    "Zone Windows Total Transmitted Solar Radiation Rate":
        "Enclosure Windows Total Transmitted Solar Radiation Rate",
    "Zone Exterior Windows Total Transmitted Beam Solar Radiation Rate":
        "Enclosure Exterior Windows Total Transmitted Beam Solar Radiation Rate",
    "Zone Interior Windows Total Transmitted Beam Solar Radiation Rate":
        "Enclosure Interior Windows Total Transmitted Beam Solar Radiation Rate",
    "Zone Exterior Windows Total Transmitted Diffuse Solar Radiation Rate":
        "Enclosure Exterior Windows Total Transmitted Diffuse Solar Radiation Rate",
    "Zone Interior Windows Total Transmitted Diffuse Solar Radiation Rate":
        "Enclosure Interior Windows Total Transmitted Diffuse Solar Radiation Rate",
    "Zone Windows Total Transmitted Solar Radiation Energy":
        "Enclosure Windows Total Transmitted Solar Radiation Energy",
    "Zone Exterior Windows Total Transmitted Beam Solar Radiation Energy":
        "Enclosure Exterior Windows Total Transmitted Beam Solar Radiation Energy",
    "Zone Interior Windows Total Transmitted Beam Solar Radiation Energy":
        "Enclosure Interior Windows Total Transmitted Beam Solar Radiation Energy",
    "Zone Exterior Windows Total Transmitted Diffuse Solar Radiation Energy":
        "Enclosure Exterior Windows Total Transmitted Diffuse Solar Radiation Energy",
    "Zone Interior Windows Total Transmitted Diffuse Solar Radiation Energy":
        "Enclosure Interior Windows Total Transmitted Diffuse Solar Radiation Energy",
    "Indoor Living Wall Energy Required For Evapotranspiration Per Unit Area":
        "Indoor Living Wall Energy Rate Required For Evapotranspiration Per Unit Area",
}


def output_space_sizing(fields, model):
    return fields.get("output_zone_sizing")


class NumberedFieldsToExtensible(ev.Change):
    def __init__(self, object_type, value_fields, maximum_number):
        self.object = object_type
        self.value_fields = value_fields
        self.maximum_number = maximum_number

    @staticmethod
    def _pointer_token(value):
        return str(value).replace("~", "~0").replace("/", "~1")

    def generate_patch(self, model):
        patch = []
        for object_name, fields in model.get(self.object, {}).items():
            values = []
            fields_to_remove = []
            for number in range(1, self.maximum_number + 1):
                numbered_fields = {
                    value_field: f"{value_field}_{number}"
                    for value_field in self.value_fields
                }
                if not any(field in fields for field in numbered_fields.values()):
                    continue
                values.append({
                    value_field: fields[numbered_field]
                    for value_field, numbered_field in numbered_fields.items()
                    if numbered_field in fields
                })
                fields_to_remove.extend(
                    field for field in numbered_fields.values() if field in fields
                )

            if not fields_to_remove:
                continue

            object_path = "/{}/{}".format(
                self._pointer_token(self.object),
                self._pointer_token(object_name),
            )
            patch.extend(
                {"op": "remove", "path": f"{object_path}/{field}"}
                for field in fields_to_remove
            )
            patch.append({
                "op": "add",
                "path": f"{object_path}/values",
                "value": values,
            })
        return patch

    def describe(self):
        fields = " and ".join(f'"{field}_N"' for field in self.value_fields)
        return f"Move the numbered {fields} fields into the extensible values array."


class ConvertVRFVariableVolumeFans(ev.Change):
    def __init__(self):
        self.object = "ZoneHVAC:TerminalUnit:VariableRefrigerantFlow"

    @staticmethod
    def _pointer_token(value):
        return str(value).replace("~", "~0").replace("/", "~1")

    @staticmethod
    def _minimum_flow_fraction(fan):
        method = fan.get("fan_power_minimum_flow_rate_input_method", "Fraction")
        if method.casefold() != "fixedflowrate":
            return fan.get("fan_power_minimum_flow_fraction", 0.25)

        maximum_flow_rate = fan.get("maximum_flow_rate")
        minimum_flow_rate = fan.get("fan_power_minimum_air_flow_rate", 0.0)
        if (
            isinstance(maximum_flow_rate, str)
            and maximum_flow_rate.casefold() == "autosize"
        ):
            return 0.0
        if not maximum_flow_rate:
            return 0.0
        return minimum_flow_rate / maximum_flow_rate

    @staticmethod
    def _system_model_fan(fan, curve_name):
        system_fan = {
            "air_inlet_node_name": fan["air_inlet_node_name"],
            "air_outlet_node_name": fan["air_outlet_node_name"],
            "speed_control_method": "Continuous",
            "electric_power_minimum_flow_rate_fraction":
                ConvertVRFVariableVolumeFans._minimum_flow_fraction(fan),
            "design_pressure_rise": fan["pressure_rise"],
            "motor_efficiency": fan.get("motor_efficiency", 0.9),
            "motor_in_air_stream_fraction": fan.get("motor_in_airstream_fraction", 1.0),
            "design_electric_power_consumption": "Autosize",
            "design_power_sizing_method": "TotalEfficiencyAndPressure",
            "fan_total_efficiency": fan.get("fan_total_efficiency", 0.7),
            "electric_power_function_of_flow_fraction_curve_name": curve_name,
            "end_use_subcategory": fan.get("end_use_subcategory", "General"),
        }
        if "availability_schedule_name" in fan:
            system_fan["availability_schedule_name"] = fan["availability_schedule_name"]
        if "maximum_flow_rate" in fan:
            system_fan["design_maximum_air_flow_rate"] = fan["maximum_flow_rate"]
        return system_fan

    @staticmethod
    def _quartic_curve(fan):
        curve = {
            "minimum_value_of_x": 0.0,
            "maximum_value_of_x": 1.0,
            "minimum_curve_output": 0.0,
            "maximum_curve_output": 5.0,
            "input_unit_type_for_x": "Dimensionless",
            "output_unit_type": "Dimensionless",
        }
        for number, curve_field in enumerate(
            (
                "coefficient1_constant",
                "coefficient2_x",
                "coefficient3_x_2",
                "coefficient4_x_3",
                "coefficient5_x_4",
            ),
            start=1,
        ):
            old_field = f"fan_power_coefficient_{number}"
            if old_field in fan:
                curve[curve_field] = fan[old_field]
        return curve

    def generate_patch(self, model):
        variable_volume_fans = model.get("Fan:VariableVolume", {})
        fan_names = {name.casefold(): name for name in variable_volume_fans}
        converted_fans = {}
        curves = {}
        patch = []

        for terminal_name, terminal in model.get(self.object, {}).items():
            fan_type = terminal.get("supply_air_fan_object_type", "")
            if fan_type.casefold() != "fan:variablevolume":
                continue

            fan_name = terminal.get("supply_air_fan_object_name", "")
            terminal_path = "/{}/{}/supply_air_fan_object_type".format(
                self._pointer_token(self.object),
                self._pointer_token(terminal_name),
            )
            patch.append({"op": "replace", "path": terminal_path, "value": "Fan:SystemModel"})

            source_fan_name = fan_names.get(fan_name.casefold())
            if source_fan_name is None:
                continue
            if source_fan_name in converted_fans:
                continue
            fan = variable_volume_fans[source_fan_name]
            curve_name = f"{source_fan_name}_curve"
            converted_fans[source_fan_name] = self._system_model_fan(fan, curve_name)
            curves[curve_name] = self._quartic_curve(fan)

        if not converted_fans:
            return patch

        if len(converted_fans) == len(variable_volume_fans):
            patch.append({"op": "remove", "path": "/Fan:VariableVolume"})
        else:
            patch.extend(
                {
                    "op": "remove",
                    "path": f"/Fan:VariableVolume/{self._pointer_token(fan_name)}",
                }
                for fan_name in converted_fans
            )

        for object_type, generated_objects in (
            ("Fan:SystemModel", converted_fans),
            ("Curve:Quartic", curves),
        ):
            if object_type not in model:
                patch.append({
                    "op": "add",
                    "path": f"/{self._pointer_token(object_type)}",
                    "value": generated_objects,
                })
            else:
                patch.extend(
                    {
                        "op": "add",
                        "path": "/{}/{}".format(
                            self._pointer_token(object_type),
                            self._pointer_token(name),
                        ),
                        "value": fields,
                    }
                    for name, fields in generated_objects.items()
                )
        return patch

    def describe(self):
        return (
            "Replace each referenced Fan:VariableVolume with a Fan:SystemModel and "
            "its fan-power Curve:Quartic."
        )


class Upgrade(ev.EnergyPlusUpgrade):
    def variable_renames(self):
        return REPORT_VARIABLE_RENAMES

    def changes(self):
        return [
            ev.AddComputedField(
                "OutputControl:Files",
                "output_space_sizing",
                output_space_sizing,
            ),
            ev.ChangeFieldName(
                "Output:IlluminanceMap",
                "zone_name",
                "zone_or_space_name",
            ),
            ev.ChangeFieldName(
                "ZoneCoolTower:Shower",
                "zone_name",
                "zone_or_space_name",
            ),
            ev.ChangeFieldName(
                "ZoneRefrigerationDoorMixing",
                "zone_1_name",
                "zone_or_space_name_1",
            ),
            ev.ChangeFieldName(
                "ZoneRefrigerationDoorMixing",
                "zone_2_name",
                "zone_or_space_name_2",
            ),
            *(
                ev.ChangeFieldName(
                    "ZoneThermalChimney",
                    f"zone_{number}_name",
                    f"zone_or_space_name_{number}",
                )
                for number in range(1, 21)
            ),
            *(
                ev.ChangeFieldName(
                    "ZoneThermalChimney",
                    f"relative_ratios_of_air_flow_rates_passing_through_zone_{number}",
                    f"relative_ratios_of_air_flow_rates_passing_through_inlet_{number}",
                )
                for number in range(1, 21)
            ),
            ev.ChangeFieldName(
                "IndoorLivingWall",
                "led_intensity_schedule_name_",
                "led_intensity_schedule_name",
            ),
            ev.ChangeFieldName(
                "IndoorLivingWall",
                "led_nominal_intensity_",
                "led_nominal_intensity",
            ),
            NumberedFieldsToExtensible(
                "MaterialProperty:PhaseChange",
                ("temperature", "enthalpy"),
                16,
            ),
            NumberedFieldsToExtensible(
                "MaterialProperty:VariableThermalConductivity",
                ("temperature", "thermal_conductivity"),
                10,
            ),
            ConvertVRFVariableVolumeFans(),
        ]

    def from_version(self):
        return "24.1.0"

    def to_version(self):
        return "24.2.0"
