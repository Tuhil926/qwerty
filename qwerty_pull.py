#!/bin/python3

from qwerty_oauth import *

try:
    drive_service = authenticate()
    file_id = find_file_id_by_name(drive_service, QWERTY_FILENAME)
    if not file_id:
        raise Exception("File not found on drive")
    download_file(drive_service, file_id, QWERTY_FILENAME)
    print("Successfully pulled qwertyfile!")
except:
    print("Could not download qwertyfile from drive!")
