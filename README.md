# SETS - STO Equipment and Trait Selector
A Star Trek Online build tool in Python

## Description

Pre-alpha version of build tool for STO

## Getting Started
Follow the instructions below to setup your Python environment.

**NOTE**: At this early stage of development, performance will be slow as the cache is built. It will take several seconds after the click of a button for the pop-up window to appear!

### Easy Access
Easy way for Windows 10 users: Download the latest version, double-click to unpack it and follow instructions in readme.txt. Most of the images are included in this package, so the app runs smoother. I you start the app this way, you'll get the latest version each time you execute it.
https://www.dropbox.com/sh/3rqhak69tr6ki2c/AADkuygAThVa9z9e_ckc4vB9a?dl=0

### Dependencies

* Python 3.7 or higher
* Pillow
* requests-html
* numpy

### Installing

> pip install -r requirements.txt

Make also sure to have the 'local' folder downloaded and in the same folder as main.py to see the title banner.

### Executing program

Windows:
> python main.py

Linux:
> python3 main.py

## Configuration locations
The configuration directory will house all of the configuration files. [^1]

Portable mode can be enabled (keeping all of the files inside the application's directory) or the application can be allowed to create an OS-based default settings directory.
### Configuration directory
Portable mode:
: Create a folder named `.config/` inside the application directory (uses APPDIR/.config/ for all files)
: Create a file named `.config.json` inside the application directory (uses APPDIR/ for all files, can be an empty file)

Windows: [^2]
: Will attempt to make `~/OneDrive/Documents/SETS/` and use it for all files
: Will try `~/Documents/SETS/` if OneDrive not available

OSX:
: Will attempt to make `~/Library/Application Support/SETS/` and use it for all files

Unix:
: Will attempt to make `~/.config/SETS/` and use it for all files

All:
: Will use the APPDIR/ for all files if the above are note accessible

### Configuration Files
- `cache/` (automatic) is used to store downloaded wiki source data
- `images/` (automatic) is used to store downloaded images.  [^1]
- `library/` (automatic) is the default open/save location for exports and imports.
- `override/` (optional) will be checked for images/files before the standard locations, allowing a user to manually override any item.
- `.state_SETS.json` (automatic) is used to store settings
- `.config.json` (optional) is used for manual settings
- `.template.json` (optional) will be imported when running the app [^3]

## Authors

* Producer - Mara "Sizer" Morrigan - mara.mos714@gmail.com, Discord: Sizer#3498
* Programmer - Liraal2
* Programmer | Linux Testing - Serious Table - Discord: Serious Table#8141
* Programmer - Stephen Hill - Discord: sukobi#1841

## Licence

SETS and its source code is licensed under GPLv3

Star Trek Online and its content is copyright of Cryptic Studios.

[^1]: The `images/` directory will stay in the APPDIR/ if that directory already exists, regardless of configuration directory.
[^2]: File paths are listed with forward slashes -- `/` -- but windows uses `\` in actual paths
[^3]: This is a standard .json file exported from SETS
