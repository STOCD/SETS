#!/bin/sh
if [ ! -r . ] || [ ! -w . ]
then
    echo "[Error] The current folder must be readable and writable."
    exit
fi
python3 --version > /dev/null 2>&1
if [ $? != 0 ]
then
    echo "[Error] No python installation found! Install python 3 to continue."
    exit
fi
python3 -m pip --version > /dev/null 2>&1
if [ $? != 0 ]
then
    echo "[Error] No PIP installation could be found! Install PIP to continue."
    exit
fi
if [ ! -e ".venv/bin/activate" ]
then
    echo "[Info]  No virtual environment found. Creating virtual environment ..."
    python3 -m venv ".venv" > /dev/null 2>&1
    if [ $? != 0 ]
    then
        echo "[Error] Virtual environment creation failed. If this error persists,"\
            "please manually create a python virtual environment in a folder named"\
            "\".venv\"."
    fi
fi
source ".venv/bin/activate"
python3 -m pip install .
if [ $? != 0 ]
then
    echo "[Error] Package installation failed. Please refer to the error message above"
    exit
fi
deactivate
if [ -d ".config" ]
then
    if [ ! -d ".config/images" ]
    then
        echo "[Info]  Creating folder \".config/images\"."
        mkdir .config/images
    fi
else
    echo "[Info]  Creating folders \".config\" and \".config/images\"."
    mkdir .config
    mkdir .config/images
fi
if [ $? = 0 ]
then
    echo "[Info]  Installation successful!"
fi
