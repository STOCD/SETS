# SETS - STO Equipment and Trait Selector
A Star Trek Online build tool in Python
**Website: https://stobuilds.com/SETS/**
**Github: https://github.com/STOCD/SETS**
**Dailies (app): https://stobuilds.com/SETS/downloads/**

## Application (no installations required)
- https://stobuilds.com/SETS/downloads/ for the latest app build
  - Windows 8, 10, 11 -- available
  - MacOS -- in development
  - Linux -- if requested
  
## Installing for the script (if not using Application version)
### Windows:
- Install Python (/www.python.org/downloads/windows/)
    - 3.9 is suggested for most systems with the 64-bit installer (as of March 2022)
    - Requires Windows 8 or later
    - Run installer and select the 'Add Python [3.9] to PATH' option
- Install Git (https://gitforwindows.org/)

At a shell prompt [^1], change to the folder you want the SETS folder installed into and run the following:
> git clone https://github.com/STOCD/SETS.git
> 
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
> 
> python3 -m pip install -r requirements.txt
> 
> python3 main.py


### MacOS:
MacOS has the most complicated installation.
- MacOS already has python2
- XCode installs have an older python3
- This installation will update any existing python3 and leave python2 in place
- There are a couple extra steps to enable JPEGs

At a shell prompt, change to the folder you want the SETS folder installed into and run the following:
> /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)" [^2]
> 
> brew install python3
> 
> brew link python3 [^3]
> > brew link --overwrite --dry-run python@3.9 [^3] [^4]
> 
> > brew link --overwrite python@3.9 [^3] [^4]
> 
> brew install python-tk@3.9 [^4]
> 
> > python3 -m pip uninstall Pillow [^5]
> 
> > brew uninstall libjpeg [^5]
> 
> > brew install libjpeg [^5]
> 
> python3 -m pip install -r requirements.txt
> 
> python3 main.py

## Updating the script
This will get the current version of SETS from Github and update the requirements (if any).
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

[^1]: For Windows, PowerShell or Command Prompt

[^2]: Homebrew for macOS is the way chosen for this installation as the python website version did not work out of the box at the time of testing (March 2022)

[^3]: Brew link will attempt to replace the active python with the homebrew version. If you have existing versions, it will partially fail and notify you of the need to use --overwrite.  Use --dry-run first to see which files are being changed.

[^4]: the '@3.9' portion of the text may be different if you're using a different python version

[^5]: MacOS (10.15 tested) has some issues with the build in JPEG library.  These steps were necessary to get it to function.  Feel free to skip them initialy -- if there is a failure, you can run these steps and then run the `python3 -m pip install -y requirements.txt` again.