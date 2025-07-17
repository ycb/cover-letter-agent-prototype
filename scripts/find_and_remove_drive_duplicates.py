#!/usr/bin/env python3
"""
Find, Summarize, and Delete Google Drive Duplicates (Recursive)

- Recursively lists all files in Drive (from FOLDER_ID or root)
- Deletes all 'Copy of ...' files and 'Untitled document' files (with confirmation)
- Leaves 'phrase.wav' and 'patch.xml' untouched
- Prints summary of deleted files
"""
import sys
import os
from collections import defaultdict

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.google_drive_integration import GoogleDriveIntegration

# --- CONFIG ---
FOLDER_ID = ""  # Set to your Drive folder ID, or leave blank for root
CREDENTIALS_FILE = "credentials.json"

# --- RECURSIVE FILE LISTING ---
def list_all_files_recursive(drive, parent_id=None):
    """Recursively list all files in Drive starting from parent_id (or root)."""
    all_files = []
    parent_id = parent_id or 'root'
    # List folders first
    folders = drive.service.files().list(q=f"'{parent_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false", fields="files(id, name)").execute().get('files', [])
    # List files in this folder
    files = drive.service.files().list(q=f"'{parent_id}' in parents and mimeType!='application/vnd.google-apps.folder' and trashed=false", fields="files(id, name, mimeType, size, modifiedTime, parents)").execute().get('files', [])
    all_files.extend(files)
    # Recurse into subfolders
    for folder in folders:
        all_files.extend(list_all_files_recursive(drive, folder['id']))
    return all_files

def list_all_files_in_folder(drive, folder_id):
    """List all files in a folder, handling pagination."""
    all_files = []
    page_token = None
    while True:
        response = drive.service.files().list(
            q=f"'{folder_id}' in parents and trashed=false",
            fields="nextPageToken, files(id, name, parents)",
            pageToken=page_token
        ).execute()
        all_files.extend(response.get('files', []))
        page_token = response.get('nextPageToken', None)
        if not page_token:
            break
    return all_files

def move_all_files_between_folders(drive, source_folder_id, dest_folder_id):
    print(f"Moving all files from {source_folder_id} to {dest_folder_id}...")
    # List all files in the source and destination folders
    source_files_before = list_all_files_in_folder(drive, source_folder_id)
    dest_files_before = list_all_files_in_folder(drive, dest_folder_id)
    print(f"Source folder before: {len(source_files_before)} files")
    print(f"Destination folder before: {len(dest_files_before)} files")
    moved = []
    for f in source_files_before:
        try:
            drive.service.files().update(
                fileId=f['id'],
                addParents=dest_folder_id,
                removeParents=source_folder_id,
                fields='id, parents'
            ).execute()
            moved.append(f['name'])
        except Exception as e:
            print(f"Failed to move {f['name']}: {e}")
    # List files again after move
    source_files_after = list_all_files_in_folder(drive, source_folder_id)
    dest_files_after = list_all_files_in_folder(drive, dest_folder_id)
    print(f"Source folder after: {len(source_files_after)} files")
    print(f"Destination folder after: {len(dest_files_after)} files")
    print(f"Moved {len(moved)} files from {source_folder_id} to {dest_folder_id}.")
    if moved:
        print("Files moved:")
        for name in moved:
            print(f"  - {name}")

# --- MAIN ---
def main():
    drive = GoogleDriveIntegration(credentials_file=CREDENTIALS_FILE, folder_id=FOLDER_ID)
    if not drive.available:
        print("Google Drive integration not available. Check credentials.")
        return

    print("Recursively listing all files in Drive...")
    files = list_all_files_recursive(drive, FOLDER_ID or None)
    print(f"Found {len(files)} files (all folders).")

    # Find 'Copy of' files and 'Untitled document' files
    copy_of_files = [f for f in files if f['name'].startswith('Copy of')]
    untitled_docs = [f for f in files if f['name'] == 'Untitled document']

    # Confirm deletion
    print(f"\nReady to delete {len(copy_of_files)} 'Copy of' files and {len(untitled_docs)} 'Untitled document' files.")
    confirm = input("Proceed with deletion? (y/N): ").strip().lower()
    if confirm == 'y':
        # Delete 'Copy of' files
        deleted_copy_of = []
        for f in copy_of_files:
            try:
                drive.service.files().delete(fileId=f['id']).execute()
                deleted_copy_of.append(f['name'])
            except Exception as e:
                print(f"Failed to delete {f['name']}: {e}")

        # Delete 'Untitled document' files
        deleted_untitled = []
        for f in untitled_docs:
            try:
                drive.service.files().delete(fileId=f['id']).execute()
                deleted_untitled.append(f['name'])
            except Exception as e:
                print(f"Failed to delete {f['name']}: {e}")

        print(f"\nDeleted {len(deleted_copy_of)} 'Copy of' files and {len(deleted_untitled)} 'Untitled document' files.")
        print("Done with deletion.")
    else:
        print("Skipping deletion phase.")

    # Always run the move task
    move_all_files_between_folders(
        drive,
        source_folder_id="1rD4UFOABddZatGlqFaBRjcv1fLYi8v9y",
        dest_folder_id="0B9PEBLmrpxxiX29qaHlUb3RLME0"
    )

if __name__ == "__main__":
    main() 