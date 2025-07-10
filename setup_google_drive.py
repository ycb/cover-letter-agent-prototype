#!/usr/bin/env python3
"""
Google Drive Setup Script
========================

Interactive script to help set up Google Drive integration for the cover letter agent.
"""

import os
import json
from pathlib import Path


def print_setup_instructions():
    """Print detailed setup instructions."""
    print("\n" + "="*60)
    print("GOOGLE DRIVE SETUP INSTRUCTIONS")
    print("="*60)
    print("Follow these steps to enable Google Drive integration:")
    print()
    print("1. GOOGLE CLOUD CONSOLE SETUP:")
    print("   - Go to https://console.cloud.google.com")
    print("   - Create a new project or select existing")
    print("   - Enable Google Drive API")
    print()
    print("2. CREATE SERVICE ACCOUNT:")
    print("   - Go to 'IAM & Admin' > 'Service Accounts'")
    print("   - Click 'Create Service Account'")
    print("   - Name: 'cover-letter-agent'")
    print("   - Description: 'Service account for cover letter agent'")
    print("   - Grant 'Editor' role")
    print()
    print("3. DOWNLOAD CREDENTIALS:")
    print("   - Click on your service account")
    print("   - Go to 'Keys' tab")
    print("   - Click 'Add Key' > 'Create new key'")
    print("   - Choose JSON format")
    print("   - Download as 'credentials.json' to project root")
    print()
    print("4. SHARE GOOGLE DRIVE FOLDER:")
    print("   - Create a folder in Google Drive for your materials")
    print("   - Right-click folder > 'Share'")
    print("   - Add your service account email (from credentials.json)")
    print("   - Give 'Editor' access")
    print()
    print("5. GET FOLDER ID:")
    print("   - Open your Google Drive folder in browser")
    print("   - Copy folder ID from URL")
    print("   - URL format: https://drive.google.com/drive/folders/FOLDER_ID")
    print()
    print("6. UPDATE CONFIGURATION:")
    print("   - Edit data/agent_config.yaml")
    print("   - Set google_drive.enabled: true")
    print("   - Set google_drive.folder_id: 'your_folder_id'")
    print()
    print("7. INSTALL DEPENDENCIES:")
    print("   pip install -r requirements.txt")
    print("="*60)


def create_sample_credentials():
    """Create a sample credentials.json file."""
    sample_credentials = {
        "type": "service_account",
        "project_id": "your-project-id",
        "private_key_id": "your-private-key-id",
        "private_key": "-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY_HERE\n-----END PRIVATE KEY-----\n",
        "client_email": "your-service-account@your-project.iam.gserviceaccount.com",
        "client_id": "your-client-id",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/your-service-account%40your-project.iam.gserviceaccount.com"
    }
    
    with open("credentials.json", "w") as f:
        json.dump(sample_credentials, f, indent=2)
    
    print("✅ Created sample credentials.json file")
    print("⚠️  Replace with your actual credentials from Google Cloud Console")


def update_agent_config():
    """Update agent_config.yaml with Google Drive settings."""
    config_path = Path("data/agent_config.yaml")
    
    if not config_path.exists():
        print("❌ agent_config.yaml not found. Please create it first.")
        return
    
    print("\n" + "="*60)
    print("UPDATE AGENT CONFIGURATION")
    print("="*60)
    
    folder_id = input("Enter your Google Drive folder ID: ").strip()
    
    if not folder_id:
        print("❌ No folder ID provided. Please get it from your Google Drive URL.")
        return
    
    # Read current config
    import yaml
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Update Google Drive settings
    if 'google_drive' not in config:
        config['google_drive'] = {}
    
    config['google_drive']['enabled'] = True
    config['google_drive']['folder_id'] = folder_id
    config['google_drive']['credentials_file'] = 'credentials.json'
    
    # Write updated config
    with open(config_path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False, indent=2)
    
    print("✅ Updated agent_config.yaml with Google Drive settings")
    print(f"   Folder ID: {folder_id}")
    print("   Enabled: true")


def test_google_drive_integration():
    """Test Google Drive integration."""
    print("\n" + "="*60)
    print("TESTING GOOGLE DRIVE INTEGRATION")
    print("="*60)
    
    try:
        from agents.google_drive_integration import GoogleDriveIntegration
        
        integration = GoogleDriveIntegration()
        
        if integration.available:
            print("✅ Google Drive integration is working!")
            files = integration.list_files()
            print(f"   Found {len(files)} files in your folder")
            
            if files:
                print("   Sample files:")
                for file in files[:3]:
                    print(f"   - {file['name']} ({file['mimeType']})")
        else:
            print("❌ Google Drive integration failed")
            print("   Check your credentials.json and folder permissions")
            
    except ImportError:
        print("❌ Google Drive dependencies not installed")
        print("   Run: pip install -r requirements.txt")
    except Exception as e:
        print(f"❌ Error testing integration: {e}")


def main():
    """Main setup function."""
    print("🚀 Google Drive Setup for Cover Letter Agent")
    print("="*60)
    
    while True:
        print("\nChoose an option:")
        print("1. Show setup instructions")
        print("2. Create sample credentials.json")
        print("3. Update agent configuration")
        print("4. Test Google Drive integration")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == "1":
            print_setup_instructions()
        elif choice == "2":
            create_sample_credentials()
        elif choice == "3":
            update_agent_config()
        elif choice == "4":
            test_google_drive_integration()
        elif choice == "5":
            print("👋 Setup complete!")
            break
        else:
            print("❌ Invalid choice. Please enter 1-5.")


if __name__ == "__main__":
    main() 