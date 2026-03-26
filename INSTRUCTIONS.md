# Instructions


Setup virtual environment (Windows PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Setup Google Drive API credentials:
1. Go to the Google Cloud Console and create/select a project.
2. Enable the Google Drive API for the project.
3. Create OAuth 2.0 credentials (Application type: Desktop) and download `credentials.json`.
4. Place `credentials.json` into the project root (next to `map_all_links_in_g-drive.py`), or set a custom path in the `.env` file (see below).

Create a `.env` file in the project root with these values (example):

```
ROOT_FOLDER_ID=1-D7FP0TFHlDw5WScm6s71ReyqNX3eREH
LOCAL_ROOT=drive_links
CREDENTIALS_FILE=credentials.json
TOKEN_FILE=token.json
```

Running the script:

```bash
python map_all_links_in_g-drive.py
```

First run will open a browser to complete OAuth. On success, the file named by `TOKEN_FILE` (default `token.json`) will be created.

Configuration notes:
- Use the `.env` file to set `ROOT_FOLDER_ID`, `LOCAL_ROOT`, `CREDENTIALS_FILE`, and `TOKEN_FILE`.

Troubleshooting:
- If authentication fails, delete the token file and retry.
- Ensure `credentials.json` matches the OAuth client you created (desktop application).
