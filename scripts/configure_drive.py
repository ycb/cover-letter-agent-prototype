#!/usr/bin/env python3
"""
CLI tool for configuring Google Drive folders and file discovery.
Makes the system flexible for any user's folder structure.
"""

import argparse
import yaml
import os
from pathlib import Path

def load_config(config_path):
    """Load existing config or create new one."""
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    else:
        return {}

def save_config(config, config_path):
    """Save config to file."""
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    with open(config_path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)

def discover_folders(drive):
    """List all accessible folders for user selection."""
    try:
        # Get root folder
        root_files = drive.list_files(folder_id='root')
        folders = []
        
        for file in root_files:
            if file.get('mimeType') == 'application/vnd.google-apps.folder':
                folders.append({
                    'id': file['id'],
                    'name': file['name'],
                    'path': f"/{file['name']}"
                })
        
        # Also check shared folders
        shared_files = drive.list_files(folder_id='shared')
        for file in shared_files:
            if file.get('mimeType') == 'application/vnd.google-apps.folder':
                folders.append({
                    'id': file['id'],
                    'name': file['name'],
                    'path': f"/Shared/{file['name']}"
                })
        
        return folders
    except Exception as e:
        print(f"Error discovering folders: {e}")
        return []

def discover_files_in_folder(drive, folder_id, file_type="spreadsheet"):
    """List files in a folder for user selection."""
    try:
        files = drive.list_files(folder_id=folder_id)
        relevant_files = []
        
        for file in files:
            mime_type = file.get('mimeType', '')
            if file_type == "spreadsheet" and "spreadsheet" in mime_type:
                relevant_files.append(file)
            elif file_type == "folder" and "folder" in mime_type:
                relevant_files.append(file)
            elif file_type == "document" and "document" in mime_type:
                relevant_files.append(file)
        
        return relevant_files
    except Exception as e:
        print(f"Error discovering files: {e}")
        return []

def interactive_folder_selection(drive, prompt, file_type="spreadsheet"):
    """Interactive folder and file selection."""
    print(f"\n{prompt}")
    print("Available folders:")
    
    folders = discover_folders(drive)
    if not folders:
        print("No folders found. Please check your Drive permissions.")
        return None
    
    for i, folder in enumerate(folders[:10]):  # Show first 10
        print(f"  {i+1}. {folder['path']} (ID: {folder['id']})")
    
    if len(folders) > 10:
        print(f"  ... and {len(folders) - 10} more folders")
    
    try:
        choice = input("\nEnter folder number (or 'skip' to skip): ").strip()
        if choice.lower() == 'skip':
            return None
        
        folder_idx = int(choice) - 1
        if 0 <= folder_idx < len(folders):
            selected_folder = folders[folder_idx]
            
            # Now show files in this folder
            print(f"\nFiles in {selected_folder['path']}:")
            files = discover_files_in_folder(drive, selected_folder['id'], file_type)
            
            if not files:
                print("No relevant files found in this folder.")
                return selected_folder['id']  # Return folder ID anyway
            
            for i, file in enumerate(files[:10]):
                print(f"  {i+1}. {file['name']} (ID: {file['id']})")
            
            if len(files) > 10:
                print(f"  ... and {len(files) - 10} more files")
            
            file_choice = input("\nEnter file number (or 'folder' to use folder ID): ").strip()
            if file_choice.lower() == 'folder':
                return selected_folder['id']
            else:
                file_idx = int(file_choice) - 1
                if 0 <= file_idx < len(files):
                    return files[file_idx]['id']
        
        print("Invalid selection.")
        return None
    except (ValueError, IndexError):
        print("Invalid input.")
        return None

def configure_drive_setup():
    """Interactive Drive configuration setup."""
    try:
        from agents.enhanced_drive_integration import EnhancedGoogleDriveIntegration
        
        drive = EnhancedGoogleDriveIntegration()
        if not drive.available:
            print("❌ Google Drive not available. Please set up credentials first.")
            return
        
        print("🚀 Google Drive Configuration Setup")
        print("This will help you configure your Drive folders for the cover letter agent.")
        
        # Load existing config
        config_path = "users/peter/config.yaml"  # TODO: Make user configurable
        config = load_config(config_path)
        
        # Initialize google_drive section if not exists
        if 'google_drive' not in config:
            config['google_drive'] = {}
        if 'materials' not in config['google_drive']:
            config['google_drive']['materials'] = {}
        if 'file_discovery' not in config['google_drive']:
            config['google_drive']['file_discovery'] = {}
        
        print("\n📁 Let's configure your Drive folders...")
        
        # STAR Stories configuration
        print("\n1️⃣ STAR Stories Configuration")
        print("Where are your STAR stories stored?")
        star_file_id = interactive_folder_selection(drive, "Select folder containing STAR stories:")
        if star_file_id:
            config['google_drive']['materials']['star_stories'] = star_file_id
            print(f"✓ STAR stories configured: {star_file_id}")
        
        # Job Tracker configuration
        print("\n2️⃣ Job Tracker Configuration")
        print("Where is your job application tracker stored?")
        job_file_id = interactive_folder_selection(drive, "Select job tracker spreadsheet:")
        if job_file_id:
            config['google_drive']['materials']['job_tracker'] = job_file_id
            print(f"✓ Job tracker configured: {job_file_id}")
        
        # Cover Letters configuration
        print("\n3️⃣ Cover Letters Configuration")
        print("Where are your cover letters stored?")
        cover_letters_id = interactive_folder_selection(drive, "Select cover letters folder:")
        if cover_letters_id:
            config['google_drive']['materials']['cover_letters'] = cover_letters_id
            print(f"✓ Cover letters configured: {cover_letters_id}")
        
        # Portfolio Work configuration
        print("\n4️⃣ Portfolio Work Configuration")
        print("Where is your portfolio work stored?")
        portfolio_id = interactive_folder_selection(drive, "Select portfolio work folder:")
        if portfolio_id:
            config['google_drive']['materials']['portfolio_work'] = portfolio_id
            print(f"✓ Portfolio work configured: {portfolio_id}")
        
        # Presentations configuration
        print("\n5️⃣ Presentations Configuration")
        print("Where are your presentations stored?")
        presentations_id = interactive_folder_selection(drive, "Select presentations folder:")
        if presentations_id:
            config['google_drive']['materials']['presentations'] = presentations_id
            print(f"✓ Presentations configured: {presentations_id}")
        
        # Save configuration
        save_config(config, config_path)
        print(f"\n✅ Configuration saved to {config_path}")
        print("\n🎯 Your Drive is now configured! You can run the analysis script.")
        
    except Exception as e:
        print(f"❌ Error during configuration: {e}")

def main():
    parser = argparse.ArgumentParser(description="Configure Google Drive for cover letter agent")
    parser.add_argument("--setup", action="store_true", help="Run interactive setup")
    parser.add_argument("--user", default="peter", help="User name for config")
    
    args = parser.parse_args()
    
    if args.setup:
        configure_drive_setup()
    else:
        print("Use --setup to run the interactive configuration")
        print("Example: python scripts/configure_drive.py --setup")

if __name__ == "__main__":
    main() 