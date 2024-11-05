#!/bin/bash
pyinstaller --onefile --distpath $HOME/bin/ -n pm-cli procmanager/__main__.py
#cp ./dist/pm-cli $HOME/bin/
