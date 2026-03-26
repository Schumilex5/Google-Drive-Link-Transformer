import os
from pathlib import Path
from tqdm import tqdm
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from dotenv import load_dotenv

# Load environment variables from .env (if present)
load_dotenv()

# Define the scope and configurable settings (can be set in a .env file)
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
ROOT_FOLDER_ID = os.environ.get('ROOT_FOLDER_ID', '1-D7FP0TFHlDw5WScm6s71ReyqNX3eREH')
CREDENTIALS_FILE = os.environ.get('CREDENTIALS_FILE', 'credentials.json')
TOKEN_FILE = os.environ.get('TOKEN_FILE', 'token.json')
LOCAL_ROOT = os.environ.get('LOCAL_ROOT', 'catimagesv2')

def authenticate():
    """Authenticate and return the Google Drive service."""
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, 'w', encoding='utf-8') as token:
            token.write(creds.to_json())
    return build('drive', 'v3', credentials=creds)

def list_files(service, folder_id, parent_path):
    """Recursively list all files and replicate folder structure."""
    query = f"'{folder_id}' in parents and trashed=false"
    page_token = None
    while True:
        results = service.files().list(
            q=query,
            fields="nextPageToken, files(id, name, mimeType)",
            pageToken=page_token
        ).execute()
        items = results.get('files', [])
        for item in items:
            if item['mimeType'] == 'application/vnd.google-apps.folder':
                new_folder = parent_path / item['name']
                new_folder.mkdir(parents=True, exist_ok=True)
                yield from list_files(service, item['id'], new_folder)
            else:
                yield item['name'], item['id'], parent_path
        page_token = results.get('nextPageToken', None)
        if page_token is None:
            break

def main():
    service = authenticate()
    Path(LOCAL_ROOT).mkdir(parents=True, exist_ok=True)
    with tqdm(desc="Processing files", unit="file") as pbar:
        for name, file_id, path in list_files(service, ROOT_FOLDER_ID, Path(LOCAL_ROOT)):
            view_url = f"https://drive.google.com/uc?export=view&id={file_id}"
            with open(path / 'links.txt', 'a', encoding='utf-8') as f:
                f.write(f"{name}\n{view_url}\n\n")
            pbar.update(1)

if __name__ == '__main__':
    main()
