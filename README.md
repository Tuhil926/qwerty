# Qwerty
Definitely not a password manager that encrypts yours passwords with AES.

# How to install:
You can just run the installation script:
`./installer.sh`
This will ask you for you sudo password for the final step (to copy the launcher script to /usr/bin)
Then, you can run the gui program with the `qwerty` command, and the cli program with `qwerty cli`

# How to use:
- If you installed it for the first time, the master password is `qwerty`
- The input boxes in the entries can be focued on by clicking on them. If you click on them again or press enter, you can go into edit mode.
- You can edit text in edit mode. Press CTRL+BACKSPACE or CTRL+W to delete whole words.
- To exit edit mode, you can either click away, press esc or CTRL+C.
- You can use the arrow keys, or hjkl like in vim to move around among the entries.
- When focused on a field(and not in edit mode), you can press CTRL+C to copy a value to clipboard, or CTRL+V to paste it from clipboard. Note that if the pasted text contains newlines, they will be replaced with spaces.
- To change the password, press CTRL+P. This will take you to the ui for changing the password.
- You can delete an entry by clicking the `X` to it's right. If you deleted it on accident, you can get it back by pressing CTRL+Z.
- You can press the `+` button at the bottom or use the shortcut CTRL+A to add new entries.
- If you have more entries than can fit on the screen, you can scroll up or down.

