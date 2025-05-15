import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.http import MediaIoBaseDownload
from google.auth.transport.requests import Request
import io

QWERTY_FILENAME = "qwerty.txt"

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
            try:
                creds = flow.run_local_server(port=0)
            except:
                creds = flow.run_local_server(open_browser=False)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return build('drive', 'v3', credentials=creds)


def update_file(service, file_id, new_filepath):
    media = MediaFileUpload(new_filepath, resumable=True)
    service.files().update(fileId=file_id, media_body=media).execute()


def download_file(service, file_id, destination_path):
    request = service.files().get_media(fileId=file_id)
    fh = io.FileIO(destination_path, 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()
        print(f"Download {int(status.progress() * 100)}%.")


def find_file_id_by_name(service, filename):
    results = service.files().list(q=f"name='{filename}' and trashed=false", spaces='drive', fields="files(id, name)").execute()
    files = results.get('files', [])
    if files:
        return files[0]['id']
    return None


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
        print(f'Successfully uploaded qwerty.txt with ID: {file.get("id")}')
        with open("qwerty_oauth_file_id.txt", "w") as file_id_file:
            file_id_file.write(file.get("id"))


# Example usage
if __name__ == '__main__':
    try:
        drive_service = authenticate()
        upload_file(drive_service, QWERTY_FILENAME, QWERTY_FILENAME)
    except:
        print("Could not backup to drive!")
