#!/bin/bash

if [ "$EUID" -eq 0 ]
  then echo "Please don't run as root"
  exit
fi

pip install pygame
pip install pyperclip
pip install pycryptodome

mkdir -p ~/.config/qwerty
cp qwerty.py ~/.config/qwerty
cp crypto_ops.py ~/.config/qwerty
cp qwerty_cli.py ~/.config/qwerty
cp qwerty.png ~/.config/qwerty
cp PixelOperator8.ttf ~/.config/qwerty
chmod +x qwerty
sudo cp qwerty /usr/bin

echo "qwerty installed successfully! run the command 'qwerty' to start it.\n"
echo "If this is your first time installing the app, the password is 'qwerty'. You can change it by pressing CTRL+P.\n"
echo "read the given README for further details on how to use.\n"
