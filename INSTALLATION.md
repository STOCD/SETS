# SETS - STO Equipment and Trait Selector
A Star Trek Online build tool in Python
**Website: https://stobuilds.com/SETS/**
**GitHub: https://github.com/STOCD/SETS**
**Dailies (app): https://stobuilds.com/SETS/downloads.html**

## Application (no installations required)
- https://stobuilds.com/SETS/downloads.html for the latest app build
  - Windows 8, 10, 11 -- available
  - MacOS -- in development
  - Linux -- if requested
  
## Installing for the script (if not using Application version)
All versions:
- Start with a folder you want to install SETS into (this will create a `SETS` folder at your current location)
- Download the base image cache: <https://stobuilds.com/SETS/files/images.zip>


### Windows:
> For an easy usable version with setup script and debug functions get the newest `SETS_Package` from: https://stobuilds.com/SETS/downloads.html or https://www.dropbox.com/sh/3rqhak69tr6ki2c/AADkuygAThVa9z9e_ckc4vB9a?dl=0
> Manual Install below
- Install Python (/www.python.org/downloads/windows/)
    - 3.9 is suggested for most systems with the 64-bit installer (as of March 2022)
    - Requires Windows 8 or later
    - Run installer and select the 'Add Python [3.9] to PATH' option
- Install Git (https://gitforwindows.org/)

At a shell prompt [^1], change to the folder you want the SETS folder installed into and run the following:
> git clone https://github.com/STOCD/SETS.git
> 
> cd SETS

Unzip the downloaded images.zip inside SETS (`SETS/images/...`)

> python -m pip install -r requirements.txt
> 
> python main.py


### Linux:
At a shell prompt, change to the folder you want the SETS folder installed into and run the following:
> apt install -y python3 python3-tk git
> 
> apt install -y python3-pip
> 
> git clone https://github.com/STOCD/SETS.git

Unzip the downloaded images.zip inside SETS (`SETS/images/...`)

> python3 -m pip install -r requirements.txt
> 
> python3 main.py


### MacOS (11.5, 11.6):
MacOS has the most complicated installation.
- MacOS already has python2
- XCode installs have an older python3
- This installation will update any existing python3 and leave python2 in place
- There are a couple extra steps to enable JPEGs

At a shell prompt, change to the folder you want the SETS folder installed into and run the following:
> > xcode-select --install [^6]
>
> /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)" [^2]
> 
> brew install python3
>
> brew link python3 [^3]
> 
> > brew link --overwrite python@3.9 [^3] [^4]
> 
> brew install python-tk@3.9 [^4]

If these are not installed, the uninstalls will complain.  Ignore and continue with the steps.
> > python3 -m pip uninstall Pillow [^5]
> 
> > brew uninstall libjpeg [^5]
> 
> brew install libjpeg [^5]
> 
> git clone https://github.com/STOCD/SETS.git

Unzip the downloaded images.zip inside SETS (`SETS/images/...`)

> /usr/local/bin/python3 -m pip install -r requirements.txt [^7]
> 
> /usr/local/bin/python3 main.py [^7]

## Updating the script
This will get the current version of SETS from GitHub and update the requirements (if any).
### Windows:
At a shell prompt [^1], change to the folder SETS is in
> git pull
> 
> python -m pip install -r requirements.txt

### Linux/MacOS:
At a shell prompt [^1], change to the folder SETS is in
> git pull
> 
> python3 -m pip install -r requirements.txt

[^1] For Windows, PowerShell or Command Prompt

[^2] Homebrew for macOS is the way chosen for this installation as the python website version did not work out of the box at the time of testing (March 2022)

[^3] Brew link will attempt to replace the active python with the homebrew version. If you have existing versions, it will partially fail and notify you of the need to use --overwrite.  Use --dry-run first to see which files are being changed.

[^4] The '@3.9' portion of the text may be different if you're using a different python version

[^5] macOS (10.15 tested) has some issues with the build in JPEG library.  These steps were necessary to get it to function.  Feel free to skip them initially -- if there is a failure, you can run these steps and then run the `python3 -m pip install -y requirements.txt` again.

[^6] If xcode hangs on finding/install, check <https://developer.apple.com/download/all/> for `Command Line Tools for Xcode 13.3` (13.3 for macOS 12+ and 13.2 for down to macOS 11.3).  Homebrew should install this automatically, but can hang on download (requiring this to be installed manually).

[^7] `/usr/bin/python3` is usually the xcode one (a few components are too old for SETS currently) -- check where brew links them.
