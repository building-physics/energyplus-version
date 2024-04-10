# energyplus_version

[![PyPI - Version](https://img.shields.io/pypi/v/energyplus-version.svg)](https://pypi.org/project/energyplus-version)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/energyplus-version.svg)](https://pypi.org/project/energyplus-version)

-----

**Table of Contents**

- [Installation](#installation)
- [License](#license)
- [Setting up a Visual Studio Code Development Environment](#setting-up-a-visual-studio-code-development-environment)

## Installation

```console
pip install energyplus-version
```

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
