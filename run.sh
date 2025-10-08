#!/bin/sh
source ".venv/bin/activate"
if [ $? != 0 ]
then
    echo "[Error] Virtual environment could not be activated. Make sure a"\
        "virtual environment exists and is accessible."
    echo "[Info]  (Run \"install.sh\ to install SETS if you haven't done that already.)"
    exit
fi
python3 main.py
deactivate
