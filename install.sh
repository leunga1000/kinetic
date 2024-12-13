#!/bin/bash
python -m venv build_venv && 
	source build_venv/bin/activate &&
	pip install -r requirements.txt && 
## In cmd.exe
#venv\Scripts\activate.bat
## In PowerShell
#venv\Scripts\Activate.ps1

pyinstaller --onefile --distpath $HOME/bin/ -n kin procmanager/__main__.py 
deactivate  # not really necessary as shell script is in its own env
#cp ./dist/pm-cli $HOME/bin/
