# SETS - STO Equipment and Trait Selector
A Star Trek Online build tool in Python. Please refer to the [website](https://stobuilds.com/apps/sets) for information on how this app is used and included features.

## Description
Build management and sharing tool for STO.
Builds can be exported to a PNG or JSON file that can be opened by another person using SETS.

## Installation
### Executable for Windows
Download the latest app installer from the [release](https://github.com/STOCD/SETS/releases) page. Execute the installer and follow its instructions to install the app.

### Executable for Arch
Download the latest package from the [release](https://github.com/STOCD/SETS/releases) page. Run `sudo pacman -U /path/to/package-file` to install the app.

### Executable for Debian
Download the latest package from the [release](https://github.com/STOCD/SETS/releases) page. Run `sudo apt install -f /path/to/package-file` to install the app.

### Script version using PIP
Install the app globally or in a python virtual environment by running `python -m pip install sto-sets`. Start the app using the `sets` command. If the app is installed in a python virtual environment, make sure to activate it before trying to start the app.

### Script (all systems; development version)
*Before installation, make sure python 3 is installed on your system alongside the python package manager pip.*

First, create a folder to house your app. Open a command prompt or shell and navigate *inside* the created folder.

Download the source code. This can be done using `git` or manual download:
- Manual Download: On the GitHub page of [this repository](https://github.com/STOCD/SETS), click on the green `CODE` button and select "Download ZIP". Save the archive and unpack it so that the files and folders seen on the repository page are *directly* inside your app folder.
- Git: run `git clone https://github.com/STOCD/SETS.git .`

*Ubuntu* users might need to install the `libxcb-cursor0` package for this app to work: `sudo apt install libxcb-cursor0`

On UNIX systems (or using a compatible shell), run the `install.sh` script by double-clicking it in your file manager or running `./install.sh` in your shell. If you cannot run the file, make sure it is executable using your file manager or the command `chmod +x install.sh`. After that, the app can be started by running `run.sh` either from your file explorer or shell. If you cannot run the file, make sure it is executable using your file manager or the command `chmod +x run.sh`.

If you cannot use the installer script, continue by installing dependencies using `python -m pip install .`.

To run the app, open a shell inside the app folder and run `python main.py --config-dir ./sets-config`.


## Updating the app
All versions of this app can be updated by following the installation steps detailed above. The existing installation will be replaced automatically, preserving settings and other configuration.

## Contributing
If you find any information or images missing, please check or update the [official wiki](https://stowiki.net) -- where SETS gets this information. You can report wiki issues on the [Star Trek Online Community Discord Server](https://discord.gg/eApUvTRr5q) in the "#wiki-discussion" channel or on the [STOBuilds Discord Server](https://discord.gg/kxwHxbsqzF) in the "#wiki-update-talk" channel.

For application-related issues or suggestions, please visit the [STOBuilds Discord](https://discord.gg/kxwHxbsqzF) ("#sets-support" channel).
