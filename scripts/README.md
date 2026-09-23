# Developer Scripts

-----

**Table of Contents**

- [convert.py](#convert_py)
- [collect_transition_data.py](#collect_transition_datapy)
- [find_object.py](#find_object_py)
- [validate_examples.py](#validate_examples_py)
- [validate_file.py](#validate_file_py)

## convert.py

Batch convert IDF files in a directory, requires the conversion utility distributed with EnergyPlus.

## collect_transition_data.py

Collect and validate all release data needed to implement one EnergyPlus
epJSON transition. This includes schemas, IDDs, transition documentation,
report-variable mappings, converted examples, and a provenance manifest. The
EnergyPlus checkout is treated as read-only, and the Fortran implementation is
fingerprinted but not copied.

See [collect_transition_data.md](collect_transition_data.md) for prerequisites,
usage, output layout, overwrite behavior, and manifest details.

## find_object.py

Looks for a given object in the `test_files` directory in the repo. Specify the
repository version with three components, for example `23.2.0`.

## validate_examples.py

Validates all of the files in a specified subdirectory of `test_files`. The
version argument must have three components.

## validate_file.py

Validates a specific file. The version argument must have three components.
