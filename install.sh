#!/bin/bash
pyinstaller --onefile --distpath $HOME/bin/ -n kin procmanager/__main__.py
#cp ./dist/pm-cli $HOME/bin/
