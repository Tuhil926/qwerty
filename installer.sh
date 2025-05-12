#!/bin/bash

# put the command you use to run python here
PYTHON="python3"

# put the place where you want to install qwerty here
INSTALL_DIR="$HOME/.config/qwerty"

# make this 1 if you want it to also install the necessary python modules
INSTALL_PYTHON_MODULES=0

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
fi

mkdir -p $INSTALL_DIR
cp qwerty.py $INSTALL_DIR
cp crypto_ops.py $INSTALL_DIR
cp qwerty_cli.py $INSTALL_DIR
cp qwerty.png $INSTALL_DIR
cp PixelOperator8.ttf $INSTALL_DIR
echo '#!/bin/bash
cd '"$INSTALL_DIR"'
if [ "$1" = "cli" ]; then
    '"$PYTHON"' qwerty_cli.py
else
    '"$PYTHON"' qwerty.py
fi' > qwerty
chmod +x qwerty
sudo cp qwerty /usr/bin

printf "\n\n"
echo "qwerty installed successfully! run the command 'qwerty' to start it, or 'qwerty cli' to start the cli.\n"
echo "If this is your first time installing the app, the password is 'qwerty'. You can change it by pressing CTRL+P.\n"
echo "read the given README for further details on how to use.\n"
