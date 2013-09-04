#!/bin/bash

set -e  # If occur any error, exit
set -x  # Verbose mode

function to_console {
    echo -e "\n*** $1 ***\n"
}

to_console "Checkouting to branch"
git checkout -b "$BRANCH" || git checkout "$BRANCH"
git reset # reverting all possible local changes


to_console "Updating repo"
git pull origin "$BRANCH"

to_console "Last commit"
git log -1

to_console "Merge com master"
git pull origin master

to_console "Removing .pyc files"
find . -name "*.pyc" -delete

cd ..
virtualenv $APP_NAME

cd $APP_NAME
source bin/activate

pip install -r requirements.txt --upgrade --use-mirrors

to_console "Generating i18n po files on src/locale"

cd i18n
chmod 700 make_files.py
make_files.py compile_po
cd ..


to_console "Running tests"
test/testloader.py
