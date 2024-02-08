# Test Files for E+ Version 22.1 #

The files in this directory are a subset of the EnergyPlus example files. Excluded files are those that require the use of ExpandObjects and/or the ParametricPreprocessor. Including those files as part of automated testing requires a bit more work (need to run the appropriate program(s) before running the version upgrades) so that is left as future work. 

| Example File                                   | Reason for Exclusion   |
| ---------------------------------------------- | ---------------------- |
| 1ZoneParameterAspect.idf                       | ParametricPreprocessor |
| 5ZoneAirCooledWithSlab.idf                     | ExpandObjects          |
| LBuildingAppGRotPar.idf                        | ParametricPreprocessor |
| LgOffVAVusingBasement.idf                      | ExpandObjects          |
| ParametricInsulation-5ZoneAirCooled.idf        | ParametricPreprocessor |
| SingleFamilyHouse_HP_Slab.idf                  | ExpandObjects          |
| SingleFamilyHouse_HP_Slab_Dehumidification.idf | ExpandObjects          |
