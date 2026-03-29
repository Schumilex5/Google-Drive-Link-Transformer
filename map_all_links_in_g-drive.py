import os
from pathlib import Path
from tqdm import tqdm
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth.transport.requests import Request
from dotenv import load_dotenv
import requests
from requests.exceptions import RequestException

# Load environment variables from .env (if present)
load_dotenv()

# Define the scope and configurable settings (can be set in a .env file)
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
CREDENTIALS_FILE = os.environ.get('CREDENTIALS_FILE', 'credentials.json')
TOKEN_FILE = os.environ.get('TOKEN_FILE', 'token.json')
ROOT_FOLDER_ID = os.environ.get('ROOT_FOLDER_ID', '1-D7FP0TFHlDw5WScm6s71ReyqNX3eREH')
LOCAL_ROOT = os.environ.get('LOCAL_ROOT', 'drive_links')
# If the folder resides in a shared drive, set SUPPORTS_ALL_DRIVES=true in your .env
SUPPORTS_ALL_DRIVES = os.environ.get('SUPPORTS_ALL_DRIVES', 'false').lower() in ('1', 'true', 'yes')

def authenticate():
    """Authenticate and return the Google Drive service."""
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    
    # Create a requests.Session subclass that enforces a default timeout
    class TimeoutSession(requests.Session):
        def __init__(self, timeout=10, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._timeout = timeout

        def request(self, method, url, **kwargs):
            if 'timeout' not in kwargs:
                kwargs['timeout'] = self._timeout
            return super().request(method, url, **kwargs)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                # Use a session with a default timeout to avoid hanging indefinitely
                request_obj = Request(session=TimeoutSession())
                creds.refresh(request_obj)
            except RequestException as e:
                print(f"Network error while refreshing credentials: {e}")
                print("Check your internet connection, proxy settings, or firewall.")
                print(f"You can try deleting '{TOKEN_FILE}' to force a new auth flow.")
                raise
            except Exception as e:
                print(f"Failed to refresh credentials: {e}")
                print(f"Falling back to interactive authentication using '{CREDENTIALS_FILE}'.")
                flow = InstalledAppFlow.from_client_secrets_file(
                    CREDENTIALS_FILE, SCOPES)
                creds = flow.run_local_server(port=0)
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
        try:
            results = service.files().list(
                q=query,
                fields="nextPageToken, files(id, name, mimeType)",
                pageToken=page_token,
                includeItemsFromAllDrives=SUPPORTS_ALL_DRIVES,
                supportsAllDrives=SUPPORTS_ALL_DRIVES,
            ).execute()
        except HttpError as e:
            # Provide clearer guidance on common causes
            print(f"Drive API error when listing files for folder '{folder_id}': {e}")
            print("- Check that the folder ID is correct and the authenticated user has access.")
            print("- If the folder is on a shared drive, set SUPPORTS_ALL_DRIVES=true in your .env.")
            return

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
