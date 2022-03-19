#!/bin/bash -e
python3 -m venv pyenv
source ./pyenv/bin/activate
python -m pip install -r requirements.txt
python -m level
