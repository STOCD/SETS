# Build and Packaging instructions for Windows
## Building
To build the app, first activate your virtual environment and install all dependencies. ```python -m pip install -e .[pyinst]```

While in the base directory of the project, run ```pyinstaller --noconfirm --clean --onedir --name SETS main.py --add-data local:local --windowed --icon local/sets_icon_small.ico``` to build the app.

While in the base directory of the project, run ```iscc distribution\SETS.iss``` to package the app with [Inno Setup Installer](https://jrsoftware.org/isinfo.php). If the command `iscc` is not available, add the install location of the `iscc` executable to PATH or provide the full path to the executable.

The resulting installer will be placed into the `dist\SETS\` folder.
