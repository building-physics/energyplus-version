# Test Files for E+ Version 9.4 #

The files in this directory are a subset of the EnergyPlus example files. Excluded files are those that require the use of ExpandObjects and/or the ParametricPreprocessor. Including those files as part of automated testing requires a bit more work (need to run the appropriate program(s) before running the version upgrades) so that is left as future work. 

| Example File                                         | Reason for Exclusion                   |
| ---------------------------------------------------- | -------------------------------------- |
| 1ZoneParameterAspect.idf                             | ParametricPreprocessor                 |
| HAMT_DailyProfileReport.idf                          | ExpandObjects                          |
| HAMT_HourlyProfileReport.idf                         | ExpandObjects                          |
| HVACTemplate-5ZoneBaseboardHeat.idf                  | ExpandObjects                          |
| HVACTemplate-5ZoneConstantVolumeChillerBoiler.idf    | ExpandObjects                          |
| HVACTemplate-5ZoneDualDuct.idf                       | ExpandObjects                          |
| HVACTemplate-5ZoneFanCoil-DOAS.idf                   | ExpandObjects                          |
| HVACTemplate-5ZoneFanCoil.idf                        | ExpandObjects                          |
| HVACTemplate-5ZoneFurnaceDX.idf                      | ExpandObjects                          |
| HVACTemplate-5ZonePackagedVAV.idf                    | ExpandObjects                          |
| HVACTemplate-5ZonePTAC-DOAS.idf                      | ExpandObjects                          |
| HVACTemplate-5ZonePTAC.idf                           | ExpandObjects                          |
| HVACTemplate-5ZonePTHP.idf                           | ExpandObjects                          |
| HVACTemplate-5ZonePurchAir.idf                       | ExpandObjects                          |
| HVACTemplate-5ZoneUnitaryHeatPump.idf                | ExpandObjects                          |
| HVACTemplate-5ZoneUnitarySystem.idf                  | ExpandObjects                          |
| HVACTemplate-5ZoneVAVFanPowered.idf                  | ExpandObjects                          |
| HVACTemplate-5ZoneVAVWaterCooled-ObjectReference.idf | ExpandObjects                          |
| HVACTemplate-5ZoneVAVWaterCooled.idf                 | ExpandObjects                          |
| HVACTemplate-5ZoneVRF.idf                            | ExpandObjects                          |
| HVACTemplate-5ZoneWaterToAirHeatPumpTowerBoiler.idf  | ExpandObjects                          |
| LBuilding-G000.idf                                   | ExpandObjects                          |
| LBuilding-G090.idf                                   | ExpandObjects                          |
| LBuilding-G180.idf                                   | ExpandObjects                          |
| LBuilding-G270.idf                                   | ExpandObjects                          |
| LBuildingAppGRotPar.idf                              | ParametricPreprocessor & ExpandObjects |
| ParametricInsulation-5ZoneAirCooled.idf              | ParametricPreprocessor                 |
