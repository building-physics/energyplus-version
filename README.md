# energyplus_version

[![PyPI - Version](https://img.shields.io/pypi/v/energyplus-version.svg)](https://pypi.org/project/energyplus-version)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/energyplus-version.svg)](https://pypi.org/project/energyplus-version)

-----

**Table of Contents**

- [Installation](#installation)
- [Usage](#usage)
- [Supported transitions](#supported-transitions)
- [Version conventions](#version-conventions)
- [Validation and reference data](#validation-and-reference-data)
- [License](#license)
- [Setting up a Visual Studio Code Development Environment](#setting-up-a-visual-studio-code-development-environment)

## Installation

```console
pip install energyplus-version
```

## Usage

Inspect the changes implemented for a source version with its complete version
number:

```console
energyplus-version describe 23.2.0
```

Upgrade one epJSON file by one EnergyPlus release:

```console
energyplus-version upgrade input.epJSON --output upgraded.epJSON
```

The command determines the source release from the input file's `Version`
object. It applies one transition per invocation and does not currently accept
a final destination version. To cross multiple releases, use the output of one
invocation as the input to the next and validate each intermediate result with
the corresponding EnergyPlus release.

## Supported transitions

The implemented transitions form a continuous path:

| Source | Destination |
| --- | --- |
| 23.2.0 | 24.1.0 |
| 24.1.0 | 24.2.0 |
| 24.2.0 | 25.1.0 |
| 25.1.0 | 25.2.0 |
| 25.2.0 | 26.1.0 |
| 26.1.0 | 26.2.0 |

## Version conventions

Package-owned version values and names always use all three components, such
as `23.2.0`. This includes command-line version arguments, upgrade module
names, collected-data directories, manifests, and transition metadata.

EnergyPlus input files remain an explicit exception. The `Version` object in
an IDF or epJSON file uses the EnergyPlus `major.minor` identifier, such as
`23.2`. The package converts that identifier to a three-component internal
version before selecting an upgrade, and writes `major.minor` back to upgraded
input files. Consequently, `energyplus-version describe` requires a version
such as `23.2.0`, while `energyplus-version upgrade` reads the two-component
identifier from the input file.

## Validation and reference data

The command-line upgrade currently transforms epJSON but does not validate the
source or result against an EnergyPlus schema. The integration suite performs
both checks for 4,741 collected EnergyPlus examples across the supported
transitions. Schema validity confirms structural compatibility, but it does
not by itself prove exact behavioral equivalence with the official EnergyPlus
Fortran transition program.

The `schema`, `idd`, `rules`, `manifests`, and `test_files` directories contain
the collected reference material. New transition data is produced by the
repeatable collection workflow documented in
[`scripts/collect_transition_data.md`](scripts/collect_transition_data.md).
The manifests record provenance and any example files that could not be
converted. The official Fortran source remains in the EnergyPlus repository
and is consulted as the behavioral reference rather than copied here.

## License

`energyplus-version` is distributed under the terms of the [BSD-3-Clause](https://spdx.org/licenses/BSD-3-Clause.html) license.

## Setting up a Visual Studio Code Development Environment

To set up a Visual Studio Code development environment, first install Python. Next, install Visual Studio code and the Python extension(s) from Microsoft. Next, install hatch with

```console
pip install hatch
```

Clone the repository to the location of your choice and get a command window running in that location. In the root folder of the repo, execute the following to generate an environment that has everything that is needed:

```console
hatch env create
```

When that is done, there should now be an environment ready that will have the package installed. To point Visual Studio Code at the created environment, execute

```console
hatch run python -c "import sys;print(sys.executable)"
```

and copy the result. In Visual Studio Code, hit `ctrl-shift-P` to bring up the command palette, select "Python: Select Interpreter", and paste in the result from above. Any warnings (yellow squiqqly underlines) in the source files should go away. To make sure that everything has worked, run

```console
hatch shell
```

to enter the environment that was created, and then execute

```console
energyplus-version --help
```

You should see the help output from the tool. Typing `exit` will exit the shell. 
