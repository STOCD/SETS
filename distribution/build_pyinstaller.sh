#!/bin/sh
set -e
if [ ! -d  distribution ] || [ ! -f local/SETS_icon_small.png ]
then
  echo "[Error] Start this script from the base folder of the application"
  exit
fi

echo "[Info]  Checking for existing venv \".venv\""
if [ ! -d ".venv" ]
then
  echo "[Info]  No venv found. Creating venv \".venv\"..."
  python3 -m venv .venv
fi

echo "[Info]  Activating venv."
. ".venv/bin/activate"

echo "[Info]  Installing (build) dependencies."
python3 -m pip install --upgrade pip setuptools wheel
python3 -m pip install -e ".[pyinst]"

echo "[Info]  Creating binary app."
pyinstaller --noconfirm --clean --onedir --name SETS main.py \
  --add-data local:local --windowed \
  --icon local/SETS_icon_small.png

echo "[Info]  Leaving venv."
deactivate
