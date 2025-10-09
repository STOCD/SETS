# SETS - STO Equipment and Trait Selector
A Star Trek Online build tool in Python. Please refer to the [website](https://stobuilds.com/apps/sets) for information on how this app is used and included features.

## Description
Build management and sharing tool for STO.
Builds can be exported to a PNG or JSON file that can be opened by another person using SETS.

## Installation
### Executable for Windows
Download the zipped app from the [release](https://github.com/STOCD/SETS/releases) page. Unzip it into a folder where you want your app to live. To speed up the image downloading process, obtain the images library as detailed below (Images library section). Double-clicking `SETS.exe` will start the app.

You can create a desktop shortcut by rightclicking on `SETS.exe` and clicking on "Create shortcut" in the context menu. Then move the created shortcut to your desktop. To create a start menu entry, open the start menu folder by rightclicking on an arbitrary app in your start menu and clicking on "Open file location". Then move the created shortcut to the folder that opened.

### Script (UNIX-like systems)
*Before installation, make sure python 3 is installed on your system alongside the python package manager pip.*

First, create a folder to house your app and open it in your file manager or shell.

Download the source code. This can be done using `git` or manual download:
- Manual Download: On the GitHub page of [this repository](https://github.com/STOCD/SETS), click on the green `CODE` button and select "Download ZIP". Save the archive and unpack it so that the files and folders seen on the repository page are *directly* inside your app folder.
- Git: run `git clone https://github.com/STOCD/SETS.git .`

Run the `install.sh` script by double-clicking it in your file manager or running `./install.sh` in your shell. If you cannot run the file, make sure it is executable using your file manager or the command `chmod +x install.sh`.

To speed up the image download process on first start of the app, download the latest image archive from [releases](https://github.com/STOCD/SETS/releases). Create a `.config` folder and unpack the images archive into it. The images should be in `<app_root>/.config/images/`.

Start the app by running the `run.sh` file by double-clicking it in your file manager or running `.run.sh` in your shell. If you cannot run the file, make sure it is executable using your file manager or the command `chmod +x run.sh`.


### Script (Cross-Platform)
*The commands below are for Windows and require a version of python 3 to be installed. If you want to install the app on Linux, use `python3` instead of `python`. A more comprehensive guide for installing the script version can be found on the [website](https://stobuilds.com/apps/sets/installation).*

First, create a folder to house your app. Open a command prompt and navigate *inside* the created folder.

Download the source code. This can be done using `git` or manual download:
- Manual Download: On the GitHub page of [this repository](https://github.com/STOCD/SETS), click on the green `CODE` button and select "Download ZIP". Save the archive and unpack it so that the files and folders seen on the repository page are *directly* inside your app folder.
- Git: run `git clone https://github.com/STOCD/SETS.git .`

Install dependencies by running `python -m pip install .`.

To speed up the image download process on first start of the app, download the latest image archive from [releases](https://github.com/STOCD/SETS/releases). Create a `.config` folder and unpack the images archive into it. The images should be in `<app_root>\.config\images\`.

*Ubuntu* users might need to install the `libxcb-cursor0` package for this app to work: `sudo apt install libxcb-cursor0`

To run the app, navigate to your apps folder. Then:
- Windows: Use `python main.py` to start the app.
- Linux: Use `python3 main.py` to start the app.

### Images library
All installation methods require an images library containing the game icons. The app will download these automatically, but as this takes a very long time, it is recommended to download the newest compressed image library from the [release](https://github.com/STOCD/SETS/releases) page. Once downloaded this has to be decompressed and placed in into the `.config/images` folder. You might need to create a folder with the name `.config` manually. The folder structure should look like below:
```
SETS
 +- .config
 |  `- images
 |    `- <lots of images>
 +- SETS.exe / main.py
 +- ...
```

## Updating the app
### Executable for Windows
Navigate to your SETS folder and delete all files and folders **except** the `.config` folder and the `.SETS_settings.ini` file. Download the newest version from the [release](https://github.com/STOCD/SETS/releases) page and unpack it into the SETS folder to replace the files and folders deleted before.

### Script (Cross-Platform)
When using Git, open a command line at the location of your SETS folder and type `git pull` to get the newest version of the app.

Otherwise, navigate to your SETS folder and delete all files and folders **except** the `.config` folder and the `.SETS_settings.ini` file. Also keep your *virtual environment* folder in place if you used a virtual environment to install dependencies. Download the app into the same folder as detailed in the installation section above. Open a command line at the location of your SETS folder and update dependencies by running `python -m pip install .`.

## Contributing
If you find any information or images missing, please check or update the [official wiki](https://stowiki.net) -- where SETS gets this information. You can report wiki issues on the [Star Trek Online Community Discord Server](https://discord.gg/eApUvTRr5q) in the "#wiki-discussion" channel or on the [STOBuilds Discord Server](https://discord.gg/kxwHxbsqzF) in the "#wiki-update-talk" channel.

For application-related issues or suggestions, please visit the [STOBuilds Discord](https://discord.gg/kxwHxbsqzF) ("#sets-support" channel).
