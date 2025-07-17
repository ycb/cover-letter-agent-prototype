#!/usr/bin/env python3
"""
Select and Map Google Drive Resources for Cover Letter Agent

- Finds file IDs for '2025' (Google Sheets) and 'Resume Grid' (Google Sheets)
- Confirms folder IDs for cover letters, portfolio work, and presentations
- Updates user's config.yaml with these IDs under google_drive.materials
- Prints a summary of the mapping
"""
import sys
import os
import yaml
from collections import defaultdict

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.google_drive_integration import GoogleDriveIntegration

USER_ID = 'peter'  # Change as needed
CONFIG_PATH = f'users/{USER_ID}/config.yaml'
FOLDER_IDS = {
    'cover_letters': '0B9PEBLmrpxxiX29qaHlUb3RLME0',
    'portfolio_work': '0B9PEBLmrpxxibkNlaTZmSVB6MUE',
    'presentations': '1cNjWcSc7c2a9OVpGTFblQ7XXZdwnQxUG',
}
KEY_FILES = {
    'job_tracker': '2025',
    'star_stories': 'Resume Grid',
}

CREDENTIALS_FILE = 'credentials.json'

# --- RECURSIVE FILE LISTING ---
def list_all_files_recursive(drive, parent_id=None):
    all_files = []
    parent_id = parent_id or 'root'
    page_token = None
    while True:
        response = drive.service.files().list(
            q=f"'{parent_id}' in parents and trashed=false",
            fields="nextPageToken, files(id, name, mimeType, parents)",
            pageToken=page_token
        ).execute()
        all_files.extend(response.get('files', []))
        page_token = response.get('nextPageToken', None)
        if not page_token:
            break
    # Recurse into subfolders
    folders = [f for f in all_files if f['mimeType'] == 'application/vnd.google-apps.folder']
    for folder in folders:
        all_files.extend(list_all_files_recursive(drive, folder['id']))
    return all_files

# --- MAIN ---
def main():
    drive = GoogleDriveIntegration(credentials_file=CREDENTIALS_FILE)
    if not drive.available:
        print("Google Drive integration not available. Check credentials.")
        return

    print("Recursively listing all files in Drive...")
    files = list_all_files_recursive(drive)
    print(f"Found {len(files)} files (all folders).\n")

    # Find key files
    file_ids = {}
    for key, name in KEY_FILES.items():
        matches = [f for f in files if f['name'] == name and f['mimeType'] == 'application/vnd.google-apps.spreadsheet']
        if matches:
            file_ids[key] = matches[0]['id']
            print(f"Found {key}: {name} (ID: {matches[0]['id']})")
        else:
            print(f"WARNING: Could not find {key} file named '{name}' (Google Sheets)")
            file_ids[key] = None

    # Confirm folder IDs
    for key, folder_id in FOLDER_IDS.items():
        print(f"{key.replace('_', ' ').title()}: {folder_id}")

    # Update config.yaml
    with open(CONFIG_PATH, 'r') as f:
        config = yaml.safe_load(f)
    if 'google_drive' not in config:
        config['google_drive'] = {}
    config['google_drive']['materials'] = {
        'cover_letters': FOLDER_IDS['cover_letters'],
        'portfolio_work': FOLDER_IDS['portfolio_work'],
        'presentations': FOLDER_IDS['presentations'],
        'job_tracker': file_ids['job_tracker'],
        'star_stories': file_ids['star_stories'],
    }
    with open(CONFIG_PATH, 'w') as f:
        yaml.safe_dump(config, f, sort_keys=False)
    print("\nUpdated config.yaml with selected Drive resources.")
    print("\nConfig snippet:")
    print(yaml.dump({'google_drive': {'materials': config['google_drive']['materials']}}, sort_keys=False))

if __name__ == "__main__":
    main() 