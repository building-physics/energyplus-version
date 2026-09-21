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
            ev.ChangeFieldName(
                "Coil:Heating:WaterToAirHeatPump:VariableSpeedEquationFit",
                "speed_1_reference_unit_rated_air_flow",
                "speed_1_reference_unit_rated_air_flow_rate",
            ),
            *(
                ev.ChangeFieldName(
                    "Coil:Cooling:DX:VariableSpeed",
                    old_field,
                    f"speed_{speed}_reference_unit_rated_condenser_air_flow_rate",
                )
                for speed, old_field in (
                    (6, "speed_6_reference_unit_condenser_air_flow_rate"),
                    (7, "speed_7_reference_unit_condenser_flow_rate"),
                    (8, "speed_8_reference_unit_condenser_air_flow_rate"),
                    (9, "speed_9_reference_unit_condenser_air_flow_rate"),
                    (10, "speed_10_reference_unit_condenser_air_flow_rate"),
                )
            ),
            *(
                ev.ChangeFieldName(
                    "Coil:Heating:DX:VariableSpeed",
                    f"speed_{speed}_heating_capacity_function_of_air_flow_fraction_curve_name",
                    f"speed_{speed}_total_heating_capacity_function_of_air_flow_fraction_curve_name",
                )
                for speed in range(4, 11)
            ),
            *(
                ev.ChangeFieldName(
                    "Coil:WaterHeating:AirToWaterHeatPump:VariableSpeed",
                    old_field,
                    new_field,
                )
                for speed in range(1, 11)
                for old_field, new_field in (
                    (
                        f"rated_sensible_heat_ratio_at_speed_{speed}",
                        f"speed_{speed}_rated_sensible_heat_ratio",
                    ),
                    (
                        f"rated_water_heating_capacity_at_speed_{speed}",
                        f"speed_{speed}_rated_water_heating_capacity",
                    ),
                    (
                        f"rated_water_heating_cop_at_speed_{speed}",
                        f"speed_{speed}_rated_water_heating_cop",
                    ),
                )
            ),
        ]

    def from_version(self):
        return "25.1.0"

    def to_version(self):
        return "25.2.0"
