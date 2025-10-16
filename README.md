# Qwerty
Definitely not a password manager that encrypts yours passwords with AES and stores the encrypted file on your google drive.

## How to install:
- Clone the repository and make sure you have python installed.
- If you want to change the defaults for qwerty gets installed and what python version it uses, or whether or not you want to also install the necessary modules, you can change the required variables at the top of `install.sh`.
- If you want to enable the backup to google drive, you can either add your own `client_secret.json` file to the repo, or if you know me, you can ask me to add you as a test user. The, you have to enable the `USE_GOOGLE_DRIVE` option in the installer script.
- Then, run the installation script:
`./installer.sh`
- This will ask you for you sudo password for the final step (to copy the launcher script to /usr/bin)
- Then, you can run the gui program with the `qwerty` command, and the cli program with `qwerty cli`
- If you had previously installed it, you can still update it by running this script, and your passwords file won't be touched.

## How to install on windows:
- Clone this repo or download it in a place you want to keep it.
- Install python
- Then, open terminal and run:


* `python -m pip install pygame`
* `python -m pip install pyperclip`
* `python -m pip install pycryptodome`
* `python -m pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib`

- Then, right click on qwerty.py and create a desktop shortcut. You can also set the icon as qwerty.ico if you want.


## How to use:
- If you installed it for the first time, the master password is `qwerty`
- Make sure you change your password (ctrl+p)!
- Then, if you've enabled the drive backups, it will prompt you to grant access to this app to upload to your google drive. This is needed to back up your qwerty.txt file.
- The input boxes in the entries can be focued on by clicking on them. If you click on them again or press enter, you can go into edit mode.
- You can edit text in edit mode. Press ctrl+backspace or ctrl+w to delete whole words.
- To exit edit mode, you can either click away, press esc or ctrl+c.
- You can use the arrow keys, or hjkl like in vim to move around among the entries.
- You can use the search bar to search for entries. You can enter the search bar by pressing ctrl+/.
- If you're not focued on any of the entries, pressing tab will focus on the first entry
- When focused on a field(and not in edit mode), you can press ctrl+c to copy a value to clipboard, or ctrl+v to paste it from clipboard.
- To change the password, press ctrl+p. This will take you to the ui for changing the password.
- You can delete an entry by clicking the `X` to it's right. If you deleted it on accident, you can get it back by pressing ctrl+z.
- You can press the `+` button at the bottom or use the shortcut ctrl+a to add new entries.
- You can drag on the `=` button on the left of the entries to change the ordering.
- If you have more entries than can fit on the screen, you can scroll up or down.

## Backups
- By default, qwerty will back up your encrypted passwords file to drive whenever the contents change.
- However, It doesn't download the encrypted file from your drive every time, since that will drastically increase the loading time.
- If you want to download the encrypted file from your drive, you can do so by running `qwerty pull`. THIS WILL OVERWRITE THE LOCAL ENCRYPTED FILE, so be careful with this.
- You can also run `qwerty backup` to create a local backup (qwerty_backup.txt) in your install directory. I would recommend doing this once in a while just to be safe, so that you don't lose your passwords.
