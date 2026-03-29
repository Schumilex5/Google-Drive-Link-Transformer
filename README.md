# Google Drive Link Transformer

I made this for personal use, I needed a free way to store images for my fan wiki project, google drive was an obvious long term solution but I had issues with displaying images using the default link format. 

This small utility scans a Google Drive folder (recursively) and writes viewable links for each file into `links.txt` files placed in a local folder structure that mirrors the Drive folder tree.

# Known Bugs
- If it crashes with keyboard interrup on first launch, just run it again

Prerequisites
- Python 3.8+
- A Google Cloud project with the Drive API enabled and an OAuth 2.0 Client ID (desktop)

Quick start
1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Place the downloaded `credentials.json` (OAuth client) in the project root.
4. Run the script:

```bash
python map_all_links_in_g-drive.py
```

Configuration
- Edit `ROOT_FOLDER_ID` and `LOCAL_ROOT` at the top of `map_all_links_in_g-drive.py` to set the Drive folder to scan and the local output directory.

Outputs
- The script creates `token.json` (authenticated session) and a local folder (value of `LOCAL_ROOT`) containing `links.txt` files with names and view URLs.
