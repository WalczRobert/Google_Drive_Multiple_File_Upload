pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
pip install --upgrade google-api-python-client

import os
import googleapiclient
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials

# Define the scopes and credentials
SCOPES = ['https://www.googleapis.com/auth/drive']
CREDENTIALS_FILE = 'path/to/your/credentials.json'

def authenticate_google_drive():
    """Authenticate and return a Google Drive service object."""
    flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
    creds = flow.run_local_server(port=0)
    service = build('drive', 'v3', credentials=creds)
    return service

def file_exists(service, file_name, parent_id):
    """Check if a file already exists in Google Drive."""
    query = f"parents = '{parent_id}' and name = '{file_name}' and trashed = false"
    response = service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
    files = response.get('files', [])
    return len(files) > 0

def upload_file(service, file_path, parent_id):
    """Upload a file to Google Drive."""
    file_metadata = {
        'name': os.path.basename(file_path),
        'parents': [parent_id]
    }
    media = MediaFileUpload(file_path, resumable=True)
    try:
        file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        print(f"Uploaded {file_path} to Google Drive with ID {file['id']}")
    except Exception as error:
        print(f"An error occurred: {error}")
        file = None
    return file

def find_drive_folder(service, folder_name):
    results = service.files().list(
        q=f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false",
        spaces='drive',
        fields='nextPageToken, files(id, name)').execute()
    folders = results.get('files', [])
    if folders:
        return folders[0]['id']  # Return the ID of the first matching folder
    else:
        print(f"The folder '{folder_name}' was not found.")
        return None

def main():
    service = authenticate_google_drive()
    drive_folder_name = 'path/to/the/upload/folder/on/your/Google/drive' # Name of the Google Drive folder where you want to upload files
    drive_folder_id = find_drive_folder(service, drive_folder_name)

    if drive_folder_id:
        local_folder_path = 'path/to/your/local/folder/to/upload' #path to local folder with items to upload
        for folder_name in os.listdir(local_folder_path):
            folder_path = os.path.join(local_folder_path, folder_name)
            if os.path.isdir(folder_path):
                for file_name in os.listdir(folder_path):
                    file_path = os.path.join(folder_path, file_name)
                    # Upload file if it does not already exist in Google Drive
                    if not file_exists(service, file_name, drive_folder_id):
                        upload_file(service, file_path, drive_folder_id)
                    else:
                        print(f"File {file_name} already exists in Google Drive. Skipping upload.")
    else:
        print("Failed to find the Google Drive folder.")


if __name__ == '__main__':
    main()
