# Input Change Catalog #

This document attempts to categorize the changes made to the schema so that the changes can be generalized.

## 9.4 to 9.5 ##

### Object Change: Construction:AirBoundary
Removes two fields ("Solar and Daylighting Method" and "Radiant Exchange Method") and warns for values other than "GroupedZones".

## 22.1 to 22.2 ##


## 22.1 to 22.2 ##


## 22.2 to 23.1 ##


## 23.1 to 23.2 ##

### Object Change: Coil:Cooling:DX:CurveFit:Performance
### Object Change: Coil:Cooling:DX:SingleSpeed
### Object Change: Coil:Cooling:DX:MultiSpeed
### Object Change: Coil:Cooling:DX:TwoStageWithHumidityControlMode
### Object Change: Coil:Heating:DX:SingleSpeed
### Object Change: Coil:Heating:DX:MultiSpeed
### Object Change: Coil:Heating:DX:VariableSpeed
### Object Change: Coil:WaterHeating:AirToWaterHeatPump:Pumped
### Object Change: Coil:WaterHeating:AirToWaterHeatPump:Wrapped
### Object Change: Coil:WaterHeating:AirToWaterHeatPump:VariableSpeed

All of these objects add an optional field, no change in the epJSON

### Object Change: Site:GroundTemperature:Undisturbed:Xing
Change the name of the field "Average Soil Surface Tempeature" to "Average Soil Surface Temperature".