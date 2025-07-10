#!/usr/bin/env python3
"""
List all files in the Google Drive materials folders using the integration logic.
"""
import yaml
from agents.google_drive_integration import GoogleDriveIntegration

def main():
    with open('data/agent_config.yaml') as f:
        config = yaml.safe_load(f)
    gd = GoogleDriveIntegration(
        config['google_drive']['credentials_file'],
        config['google_drive']['folder_id']
    )
    materials = config['google_drive']['materials']
    folder_id = config['google_drive']['folder_id']
    subfolders = gd.list_files(folder_id)
    for material_type, subfolder_name in materials.items():
        # Find the subfolder ID
        subfolder_id = None
        for f in subfolders:
            if f['mimeType'] == 'application/vnd.google-apps.folder' and subfolder_name.strip('/').lower() in f['name'].lower():
                subfolder_id = f['id']
                break
        if not subfolder_id:
            print(f'No {material_type} folder found in Drive root')
            continue
        files = gd.list_files(subfolder_id)
        print(f'Found {len(files)} files in {material_type}:')
        for file in files:
            print(f"- {file['name']} ({file['mimeType']})")
        print()

if __name__ == "__main__":
    main() 