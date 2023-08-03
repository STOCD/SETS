# SETS - STO Equipment and Trait Selector
A Star Trek Online build tool in Python
**Website: https://stobuilds.com/SETS/**

## Description

Alpha version of build management and sharing tool for STO.
Builds can be exported to a PNG file that can be opened by another person using SETS.

## Contributing
If you find any information or images missing, please check or update the official wiki (https://sto.fandom.com/) -- where SETS gets this information. You can report wiki issues on the Star Trek Online Community Discord Server (https://discord.gg/eApUvTRr5q) in the #wiki-requests channel or on the STOBuilds Discord Server (https://discord.gg/stobuilds) in the #wiki-update-talk channel.

For application-related issues or suggestions, please visit the github: https://github.com/STOCD/SETS/issues

## Getting Started
### Application (no installations required)
- https://stobuilds.com/SETS/downloads.html for the latest app build
  - Windows 8, 10, 11 -- currently not available
  - MacOS -- in development
  - Linux -- if requested

### Script (Windows 8, 10, 11 ONLY)
For Windows 8, 10, 11 there is the possibility to get `SETS Package` that contains everything needed for installing the script verion of the app. Get the newest version here: https://stobuilds.com/SETS/downloads.html

### Script (using the git source)
- View the INSTALLATION.md file for detailed installation information
- This is not necessary with the application version.

### Running the program (script, not application)

Windows:
> python main.py

Linux/macOS:
> python3 main.py
> 
### Dependencies
* Python 3.7 or higher
* Pillow
* requests-html
* numpy
* tkmacos (MacOS only)


> 
## Image cache
The image cache can be over 4,000 files.

The majority of this are gear icons and ship images.  Gear icons tend to be very small (under 40MB for them all, included in the packaged images) while ship images can be quite large and are left for automatic download.
- `CONFIG_DIRECTORY/images/` (automatic) is used to store downloaded images.
- `APP_DIRECTORY/images/` (optional) is checked after downloaded images.
  - This is where packaged images are initially set up.
  - https://stobuilds.com/SETS/files/images.zip can be added here for a quick start

## Configuration directory
The configuration directory contains multiple files and folders.
The configuration directory will automatically be created unless using portable mode.

Portable mode (optional):
: Keeps all files inside the application's directory
: Create a folder named `.config/` inside the application directory (uses APPDIR/.config/ for all files)

Windows: [^1]
: Will attempt to make `~/OneDrive/Documents/SETS/` and use it for all files
: Will try `~/Documents/SETS/` if OneDrive not available

OSX:
: Will attempt to make `~/Library/Application Support/SETS/` and use it for all files

Unix:
: Will attempt to make `~/.config/SETS/` and use it for all files

All:
: Will use the APPDIR/ for all files if the above are not accessible

### Configuration Files
- `cache/` (automatic) is used to store downloaded wiki source data
- `library/` (automatic) is the default open/save location for exports and imports.
- `library/.template.json` (optional) will be imported when running the app [^2]
- `library/autosave.json` (automatic) will be used to save changes as you make them
- `override/` (optional) will be checked for images/files before the standard locations, allowing a user to manually override any item.
- `.state_SETS.json` (automatic) is used to store settings
- `.config.json` (optional) is used for manual settings

## Authors

* Producer - Mara "Sizer" Morrigan - mara.mos714@gmail.com, Discord: Sizer#3498
* Programmer - Liraal2
* Programmer | Linux Testing - Serious Table - Discord: Serious Table#8141
* Programmer - Stephen Hill - Discord: sukobi#1841
* Programmer | QA | "girl Friday" - Shinga - Discord: Shinga#9959

## Licence

SETS and its source code is licensed under GPLv3

Star Trek Online and its content is copyright of Cryptic Studios.

[^1]: File paths are listed with forward slashes -- `/` -- but windows uses `\` in actual paths

[^2]: This is a standard .json file exported from SETS
