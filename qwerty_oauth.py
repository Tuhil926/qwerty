import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request

from crypto_ops import QWERTY_FILENAME

SCOPES = ['https://www.googleapis.com/auth/drive.file']

def authenticate():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('client_secret.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return build('drive', 'v3', credentials=creds)

def update_file(service, file_id, new_filepath):
    media = MediaFileUpload(new_filepath, resumable=True)
    service.files().update(
        fileId=file_id,
        media_body=media
    ).execute()

def upload_file(service, filename, filepath):
    try:
        with open("qwerty_oauth_file_id.txt", "r") as file_id_file:
            file_id = file_id_file.read().strip()
            update_file(service, file_id, QWERTY_FILENAME)
            print("Successfully backed up qwerty.txt")
    except:
        file_metadata = {'name': filename}
        media = MediaFileUpload(filepath, resumable=True)
        file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        print(f'Uploaded qwerty.txt with ID: {file.get("id")}')
        with open("qwerty_oauth_file_id.txt", "w") as file_id_file:
            file_id_file.write(file.get("id"))

# Example usage
if __name__ == '__main__':
    try:
        drive_service = authenticate()
        upload_file(drive_service, QWERTY_FILENAME, QWERTY_FILENAME)
    except:
        print("Could not backup to drive!")
