# -*- coding: utf-8 -*-
"""
Created on Thu Feb  8 12:37:34 2024

@author: vyk
"""


import json
import jsonschema

def validate_json(json_data, schema_filepath):
    with open(schema_filepath) as schema_file:
        schema_data=json.load(schema_file)
    
    try:
        jsonschema.validate(instance=json_data, schema=schema_data)
        #print("JSON is valid against the schema.")
        return True
    except:
        pass
        return False
#    except jsonschema.exceptions.ValidationError as error:
#                print("JSON is not valid against the schema:")
#                print(error)
#                return False

# Example usage:
# =============================================================================
# if __name__ == "__main__":
#     # Load JSON data and schema
#     with open('C:\\Users\\vyk\\Desktop\\EpJSON_transition\\Eplus\\DaylightingDeviceShelf.epJSON') as json_file:
#         json_data = json.load(json_file)
# 
#     with open('C:\\Users\\vyk\\Desktop\\EpJSON_transition\\Energy+.schema_9.6.epJSON') as schema_file:
#         schema_data = json.load(schema_file)
# 
#     # Validate JSON against schema
#     Validated=validate_json(json_data, schema_data)
# =============================================================================
