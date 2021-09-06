# Spine Toolbox
Link to the documentation: [https://spine-toolbox.readthedocs.io/en/latest/?badge=latest](https://spine-toolbox.readthedocs.io/en/latest/?badge=latest)

[![Python](https://img.shields.io/badge/python-3.7%20|%203.8-blue.svg)](https://www.python.org/downloads/release/python-379/)
[![Documentation Status](https://readthedocs.org/projects/spine-toolbox/badge/?version=latest)](https://spine-toolbox.readthedocs.io/en/latest/?badge=latest)
[![Unit tests](https://github.com/Spine-project/Spine-Toolbox/workflows/Unit%20tests/badge.svg)](https://github.com/Spine-project/Spine-Toolbox/actions?query=workflow%3A"Unit+tests")
[![codecov](https://codecov.io/gh/Spine-project/Spine-Toolbox/branch/master/graph/badge.svg)](https://codecov.io/gh/Spine-project/Spine-Toolbox)
[![PyPI version](https://badge.fury.io/py/spinetoolbox.svg)](https://badge.fury.io/py/spinetoolbox)

Spine Toolbox is an open source Python package to manage data, scenarios and workflows for modelling and simulation. You can have your local workflow, but work as a team through version control and SQL databases.

## Programming language

- Python 3.7
- Python 3.8

Please note that Python 3.9 is not supported yet. 

## License

Spine Toolbox is released under the GNU Lesser General Public License (LGPL) license. All accompanying
documentation, original graphics and other material are released under the 
[Creative Commons BY-SA 4.0 license](https://creativecommons.org/licenses/by-sa/4.0/).
Licenses of all packages used by Spine Toolbox are listed in the Spine Toolbox User 
Guide.

## Installation

We provide three options for installing Spine Toolbox: [Python/pipx](#installation-with-python-and-pipx), [Windows installation file](#windows-64-bit-installer-package), and [git](#installation-from-sources-using-git).

### Installation with Python and pipx

This works best for users that want to just use Spine Toolbox but also keep it updated with new releases.

1. If you don't yet have Python 3.7 or 3.8, then install Python 3.8.
   - On Windows, open **Microsoft Store** from the start menu,
     enter ‘python’ in the search box, select Python 3.8, and press **Get**.
   - On OS X and Linux, get [the latest release from Python.org](https://www.python.org/downloads/).

2. Open a terminal (e.g., Command Prompt on Windows).

3. Get the latest version of `pip` (pip is a package manager for Python)

        python -m pip install --upgrade pip

4. Install [pipx](https://pypa.github.io/pipx/) (pipx allows to create an isolated environment for Spine Toolbox to avoid package conflicts with other Python tools)

        python -m pip install pipx
        python -m pipx ensurepath
        
5. Install the latest Spine Toolbox release by running

        pipx install spinetoolbox

That’s it!

To launch Spine Toolbox, open a terminal and run

    spinetoolbox

To update Spine Toolbox to the latest available release, open a terminal and run

    pipx upgrade spinetoolbox


### Windows 64-bit Installer Package

Windows installer packages are published periodically
but not as frequently as the standard Python installation above.
This option is suitable for users who cannot install Python or don’t need to get the most recent updates. This should be the most stable option.
Download the latest installer package from [here](https://github.com/Spine-project/Spine-Toolbox/releases),
run it, and follow the instructions to install Spine Toolbox.


### Installation from sources using GIT

This option is for the developers and other contributors who want to debug or 
edit the Spine Toolbox source code.
First, follow the instructions above to install Python and get the latest 
version of pip.

1. Clone or download the source code from this repository.
   
2. Browse to the folder and create a virtual environment using

        python -m venv .venv

   (Advanced users can also manage the environment using 
   [conda](https://docs.conda.io/projects/conda/), but this is not covered here.)
    
3. Activate the environment using `.venv\Scripts\activate.bat` (Windows cmd.exe) 
   or `source .venv/bin/activate` (bash, zsh). 

4. Make sure that the terminal prompt indicates the active environment, 
   and install Spine Toolbox by running

        pip install -r requirements.txt
    
5. (Optional) Install additional development packages with

        pip install -r dev-requirements.txt

You can now launch Spine Toolbox by running `spinetoolbox` when the environment 
is active. 

**To upgrade**, pull or copy the latest changes from the repository and run

    pip install --upgrade -r requirements.txt

**NOTE:** Even though `spinedb_api`, `spine_engine`, and `spine_items` are listed in spinetoolbox's `requirements.txt`, 
the command above may not always upgrade these packages. This is because we do not bump the version number on every 
commit. Before writing a bug report, **please make sure you are using the latest commit of these three packages 
by doing the following:**

To upgrade `spinedb_api`, run

    pip uninstall -y spinedb-api && pip install --upgrade git+https://github.com/Spine-project/Spine-Database-API.git

To upgrade `spine_engine`, run

    pip uninstall -y spine-engine && pip install --upgrade git+https://github.com/Spine-project/spine-engine.git#egg=spine_engine

To upgrade `spine_items`, run

    pip uninstall -y spine-items && pip install --upgrade git+https://github.com/Spine-project/spine-items.git#egg=spine_items

Or you can use the provided script `/bin/upgrade_spine_reqs.bat` (Windows) or `/bin/upgrade_spine_reqs.py` 
(Other OS's) files to upgrade all three at once.

### About requirements

Python 3.7 or Python 3.8 is required.

See file `setup.py` and `requirements.txt` for packages required to run Spine Toolbox.
(Additional packages needed for development are listed in `dev-requirements.txt`.)

The requirements include three packages ([`spinedb_api`](https://github.com/Spine-project/Spine-Database-API),
[`spine_engine`](https://github.com/Spine-project/spine-engine), and [`spine_items`](https://github.com/Spine-project/spine-items)),
developed by the Spine project consortium.

### Building the User Guide

You can find the latest documentation on [readthedocs](https://spine-toolbox.readthedocs.io/en/latest/index.html).
If you want to build the documentation yourself,
source files for the User Guide can be found in `docs/source` directory. In order to 
build the HTML docs, you need to install the *optional requirements* (see section 
'Installing requirements' above). This installs Sphinx (among other things), which 
is required in building the documentation. When Sphinx is installed, you can build the 
HTML pages from the user guide source files by using the `bin/build_doc.bat` script on 
Windows or the `bin/build_doc.sh` script on Linux and Mac. After running the script, the 
index page can be found in `docs/build/html/index.html`. The User Guide can also 
be opened from Spine Toolbox menu Help->User Guide (F2).

### Troubleshooting

#### Installation fails

Please make sure you are using Python 3.7 or Python 3.8 to install the requirements.

#### Installation fails on Linux
If Python runs into errors while installing on Linux systems, running the 
following commands in a terminal may help:

```shell
$ sudo apt install libpq-dev
$ sudo apt-get install unixodbc-dev
```

#### Problems in starting the application

If there are problems in starting Spine Toolbox, the chances are that the required 
packages were not installed successfully. In case this happens, the first thing you 
should check is that you don't have `Qt`, `PyQt4`, `PyQt5`, `PySide`, and `PySide2` 
packages installed in the same environment. These do not play nice together and may 
introduce conflicts. In addition, make sure that you do not have multiple versions 
of these `Qt` related packages installed in the same environment. The easiest way 
to solve this problem is to create a blank (e.g. virtual environment) Python 
environment just for `PySide2` applications and installing the requirements again.

**Warning: Using the *conda-forge* channel for installing the requirements is not 
recommended.**

The required `qtconsole` package from the ***conda-forge*** channel also
installs `qt` and `PyQt` packages. Since this is a `PySide2` application, those are 
not needed and there is a chance of conflicts between the packages.

**Note**: Supported PySide2 version is **5.14**. Spine Toolbox does not support PySide2 
version 5.15 (yet).

## Contribution Guide

All are welcome to contribute!

See detailed instructions for contribution in [Spine Toolbox User Guide](https://spine-toolbox.readthedocs.io/en/latest/contribution_guide.html).

Below are the bare minimum things you need to know.

### Setting up development environment

1. Install the developer requirements:

        pip install -r dev-requirements.txt

2. Optionally, run `pre-commit install` in project's root directory. This sets up some git hooks.

### Coding style

- [Black](https://github.com/python/black) is used for Python code formatting.
  The project's GitHub page includes instructions on how to integrate Black in IDEs.
- Google style docstrings

### Linting

It is advisable to run [`pylint`](https://pylint.readthedocs.io/en/latest/) regularly on files that have been changed.
The project root includes a configuration file for `pylint`.
`pylint`'s user guide includes instructions on how to [integrate the tool in IDEs](https://pylint.readthedocs.io/en/latest/user_guide/ide-integration.html#pylint-in-pycharm).

### Unit tests

Unit tests are located in the `tests` directory.
You can run the entire test suite from project root by

    python -m unittest

### Reporting bugs
If you think you have found a bug, please check the following before creating a new 
issue:
1. **Make sure you’re on the latest version.** 
2. **Try older versions.**
3. **Try upgrading/downgrading the dependencies**
4. **Search the project’s bug/issue tracker to make sure it’s not a known issue.**

What to put in your bug report:
1. **Python version**. What version of the Python interpreter are you using? 32-bit 
    or 64-bit?
2. **OS**. What operating system are you on?
3. **Application Version**. Which version or versions of the software are you using? 
    If you have forked the project from Git, which branch and which commit? Otherwise, 
    supply the application version number (Help->About menu).
4. **How to recreate**. How can the developers recreate the bug? A screenshot 
    demonstrating the bug is usually the most helpful thing you can report. Relevant 
    output from the Event Log and debug messages from the console of your run, should 
    also be included.

### Feature requests
The developers of Spine Toolbox are happy to hear new ideas for features or improvements 
to existing functionality. The format for requesting new features is free. Just fill 
out the required fields on the issue tracker and give a description of the new feature. 
A picture accompanying the description is a good way to get your idea into development
faster. But before you make a new issue, please check that there isn't a related idea 
already open in the issue tracker.

&nbsp;
<hr>
<center>
<table width=500px frame="none">
<tr>
<td valign="middle" width=100px>
<img src=https://europa.eu/european-union/sites/europaeu/files/docs/body/flag_yellow_low.jpg alt="EU emblem" width=100%></td>
<td valign="middle">This project has received funding from the European Union’s Horizon 2020 research and innovation programme under grant agreement No 774629.</td>
</table>
</center>
