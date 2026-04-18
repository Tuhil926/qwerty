#!/bin/bash

# put the command you use to run python here
USER_PYTHON="python3"

# put the place where you want to install qwerty here
INSTALL_DIR="$HOME/.config/qwerty"

# This is where the qwerty launcher lives
# make sure this in in your PATH if you want to be able to run it as a command
EXEC_DIR="$HOME/.local/bin"

# default place to put desktop files. you probably don't need to change this
DESKTOP_FILE_DIR="$HOME/.local/share/applications"

# make this 1 if you want it to save to google drive as a backup, 0 if not
USE_GOOGLE_DRIVE=1

echo 'Installing qwerty at '"$INSTALL_DIR"' and '"$EXEC_DIR"' using '"$USER_PYTHON"' as the python command...'

mkdir -p $INSTALL_DIR
mkdir -p $EXEC_DIR

PYTHON="$INSTALL_DIR/venv/bin/python"

if [ ! -d $INSTALL_DIR/venv ]; then
    echo 'Creating a python virtual environment...'
    $USER_PYTHON -m venv $INSTALL_DIR/venv
    echo 'Installing necessary requirements...'
    $PYTHON -m pip install -r requirements.txt
    echo 'done'
fi

echo 'copying files to '"$INSTALL_DIR"'...'

cp qwerty.py $INSTALL_DIR
cp crypto_ops.py $INSTALL_DIR
cp qwerty_cli.py $INSTALL_DIR
cp qwerty.png $INSTALL_DIR
cp PixelOperator8.ttf $INSTALL_DIR
if [ "$USE_GOOGLE_DRIVE" -eq 1 ]; then
    cp client_secret.json $INSTALL_DIR
    cp qwerty_pull.py $INSTALL_DIR
fi
cp qwerty_oauth.py $INSTALL_DIR
echo '#!/bin/bash
cd '"$INSTALL_DIR"'
if [ "$1" = "cli" ]; then
    '"$PYTHON"' qwerty_cli.py
elif [ "$1" = "pull" ]; then
    '"$PYTHON"' qwerty_pull.py
elif [ "$1" = "backup" ]; then
    backup_filename=qwerty_backup_$(date +%Y-%m-%d-%H:%M:%S)
    cp qwerty.txt $backup_filename
    echo "Created a local backup: '$INSTALL_DIR'/$backup_filename"
else
    '"$PYTHON"' qwerty.py
fi' > qwerty
chmod +x qwerty
cp qwerty $EXEC_DIR

echo '[Desktop Entry]
Name=qwerty
Exec='"$EXEC_DIR"'/qwerty
Icon='"$INSTALL_DIR"'/qwerty.png
Type=Application
Categories=Utility;
Terminal=false
Comment=Definitely not a password manager
Keywords=qwerty;password;' > qwerty.desktop

cp qwerty.desktop $DESKTOP_FILE_DIR

printf "\n\n"
echo "qwerty installed successfully! run the command 'qwerty' to start it, or 'qwerty cli' to start the cli."
echo "If this is your first time installing the app, the password is 'qwerty'. You can change it by pressing CTRL+P."
echo "read the given README for further details on how to use."
