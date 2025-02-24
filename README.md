# SETS - STO Equipment and Trait Selector
A Star Trek Online build tool in Python. Please refer to the [website](https://stobuilds.com/apps/sets) for information on how this app is used and included features.

## Installation
*Note: The commands below are for Windows. If you want to install the app on Linux, use `python3` instead of `python`.*

First, create a folder to house your app. Open a command prompt and navigate *inside* the created folder.

Download the source code. This can be done using `git` or manual download:
- Manual Download: On the GitHub page of [this repository](https://github.com/Shinga13/SETS), click on the green `CODE` button and select "Download ZIP". Save the archive and unpack it so that the files and folders seen on the repository page are *directly* inside your app folder.
- Git: run `git clone https://github.com/Shinga13/SETS.git .`

Install dependencies by running `python -m pip install .`.

To speed up the image download process on first start of the app, download the latest image archive from [releases](https://github.com/Shinga13/SETS/releases). Create a `.config` folder and unpack the images archive into it. The images should be in `<app_root>\.config\images\`.

*Ubuntu* users might need to install the `libxcb-cursor0` package for this app to work: `sudo apt install libxcb-cursor0`

## Running the app
Navigate to your apps folder.
- Windows: Use `python main.py` to start the app.
- Linux: Use `python3 main.py` to start the app.
