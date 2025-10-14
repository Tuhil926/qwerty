#!/bin/bash

# put the command you use to run python here
PYTHON="python3"

# put the place where you want to install qwerty here
INSTALL_DIR="$HOME/.config/qwerty"

# default place to put desktop files. you probably don't need to change this
DESKTOP_FILE_DIR="$HOME/.local/share/applications"

# make this 1 if you want it to also install the necessary python modules
INSTALL_PYTHON_MODULES=0

# make this 1 if you want it to save to google drive as a backup
USE_GOOGLE_DRIVE=1

echo 'Installing qwerty at '"$INSTALL_DIR"' using '"$PYTHON"' as the python command...'

if [ "$EUID" -eq 0 ]
  then echo "Please don't run as root"
  exit
fi

if [ "$INSTALL_PYTHON_MODULES" -eq 1 ]; then
    echo 'Installing necessary python modules..'
    $PYTHON -m pip install pygame
    $PYTHON -m pip install pyperclip
    $PYTHON -m pip install pycryptodome
    $PYTHON -m pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
fi

mkdir -p $INSTALL_DIR
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
    cp qwerty.txt qwerty_backup.txt
else
    '"$PYTHON"' qwerty.py
fi' > qwerty
chmod +x qwerty
sudo cp qwerty /usr/bin

echo '[Desktop Entry]
Name=qwerty
Exec=qwerty
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
