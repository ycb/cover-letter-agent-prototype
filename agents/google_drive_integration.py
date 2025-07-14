#!/usr/bin/env python3
"""
Google Drive Integration
=======================

Module for accessing supporting materials (presentations, spreadsheets,
past cover letters) from Google Drive and uploading cover letter drafts.
Uses OAuth delegation for regular Google accounts.
"""

import logging
import os
import json
from datetime import datetime
from typing import Any, Dict, List, Optional

try:
    import io
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload

    GOOGLE_DRIVE_AVAILABLE = True
except ImportError:
    GOOGLE_DRIVE_AVAILABLE = False
    logging.warning(
        "Google Drive API not available. Install with: pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client"
    )

logger = logging.getLogger(__name__)

# OAuth 2.0 scopes
SCOPES = ['https://www.googleapis.com/auth/drive']


class GoogleDriveIntegration:
    """Handles Google Drive integration using OAuth delegation for regular Google accounts."""

    def __init__(self, credentials_file: str = "credentials.json", folder_id: str = ""):
        """Initialize Google Drive integration with OAuth."""
        self.credentials_file = credentials_file
        self.folder_id = folder_id
        self.service = None
        self.available = False
        self.token_file = "token.json"

        if GOOGLE_DRIVE_AVAILABLE:
            self._initialize_service()

    def _initialize_service(self):
        """Initialize Google Drive service with OAuth authentication."""
        try:
            creds = None
            
            # Load existing token
            if os.path.exists(self.token_file):
                creds = Credentials.from_authorized_user_file(self.token_file, SCOPES)
            
            # If no valid credentials available, let the user log in
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    if not os.path.exists(self.credentials_file):
                        logger.error(f"OAuth credentials file not found: {self.credentials_file}")
                        logger.info("Please download OAuth credentials from Google Cloud Console")
                        return
                    
                    flow = InstalledAppFlow.from_client_secrets_file(self.credentials_file, SCOPES)
                    creds = flow.run_local_server(port=0)
                
                # Save the credentials for the next run
                with open(self.token_file, 'w') as token:
                    token.write(creds.to_json())

            self.service = build("drive", "v3", credentials=creds)
            self.available = True
            logger.info("Google Drive service initialized successfully with OAuth")

        except Exception as e:
            logger.error(f"Failed to initialize Google Drive service: {e}")
            self.available = False

    def list_files(self, folder_id: Optional[str] = None, file_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """List files in a Google Drive folder."""
        if not self.available or not self.service:
            return []

        folder_id = folder_id or self.folder_id
        if not folder_id:
            logger.warning("No folder ID specified")
            return []

        try:
            query = f"'{folder_id}' in parents and trashed=false"
            if file_type:
                query += f" and mimeType contains '{file_type}'"

            results = (
                self.service.files()
                .list(q=query, pageSize=100, fields="nextPageToken, files(id, name, mimeType, size, modifiedTime)")
                .execute()
            )

            files = results.get("files", [])
            logger.info(f"Found {len(files)} files in folder")
            return files

        except Exception as e:
            logger.error(f"Error listing files: {e}")
            return []

    def download_file(self, file_id: str, local_path: str) -> bool:
        """Download a file from Google Drive."""
        if not self.available or not self.service:
            return False

        try:
            request = self.service.files().get_media(fileId=file_id)
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)

            done = False
            while done is False:
                status, done = downloader.next_chunk()
                logger.info(f"Download {int(status.progress() * 100)}%")

            fh.seek(0)

            # Ensure directory exists
            os.makedirs(os.path.dirname(local_path), exist_ok=True)

            with open(local_path, "wb") as f:
                f.write(fh.read())

            logger.info(f"Downloaded file to: {local_path}")
            return True

        except Exception as e:
            logger.error(f"Error downloading file: {e}")
            return False

    def upload_file(
        self, content: str, filename: str, folder_id: Optional[str] = None, mime_type: str = "text/plain"
    ) -> Optional[str]:
        """Upload a file to Google Drive."""
        if not self.available or not self.service:
            logger.error("Google Drive service not available")
            return None

        folder_id = folder_id or self.folder_id
        if not folder_id:
            logger.error("No folder ID specified for upload")
            return None

        try:
            # Create file metadata
            file_metadata = {"name": filename, "parents": [folder_id]}

            # Create media upload
            fh = io.BytesIO(content.encode("utf-8"))
            media = MediaIoBaseUpload(fh, mimetype=mime_type, resumable=True)

            # Upload file
            file = self.service.files().create(body=file_metadata, media_body=media, fields="id").execute()

            logger.info(f"Uploaded file to Google Drive: {filename} (ID: {file.get('id')})")
            return file.get("id")

        except Exception as e:
            logger.error(f"Error uploading file: {e}")
            return None

    def upload_cover_letter_draft(
        self, cover_letter: str, company_name: str, position_title: str, job_score: float = 0.0
    ) -> Optional[str]:
        """Upload a cover letter draft to Google Drive with metadata."""
        if not self.available:
            logger.warning("Google Drive not available for upload")
            return None

        # Create filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_company = company_name.replace(" ", "_").replace("/", "_")[:30]
        safe_position = position_title.replace(" ", "_").replace("/", "_")[:30]

        filename = f"{safe_company}_{safe_position}_{timestamp}.txt"

        # Add metadata to the content
        metadata_header = f"""# Cover Letter Draft
Company: {company_name}
Position: {position_title}
Score: {job_score:.2f}
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

"""

        full_content = metadata_header + cover_letter

        # Get or create drafts subfolder
        drafts_folder_id = self._get_or_create_drafts_folder()
        if not drafts_folder_id:
            logger.error("Could not create or find drafts folder")
            return None

        return self.upload_file(full_content, filename, drafts_folder_id)

    def _get_or_create_drafts_folder(self) -> Optional[str]:
        """Get or create a drafts subfolder in the main Google Drive folder."""
        if not self.available or not self.service:
            return None

        try:
            # First, try to find existing drafts folder
            query = f"'{self.folder_id}' in parents and name='drafts' and mimeType='application/vnd.google-apps.folder' and trashed=false"
            results = self.service.files().list(q=query, fields="files(id, name)").execute()

            files = results.get("files", [])
            if files:
                # Drafts folder already exists
                drafts_folder_id = files[0]["id"]
                logger.info(f"Found existing drafts folder: {drafts_folder_id}")
                return drafts_folder_id

            # Create new drafts folder
            folder_metadata = {"name": "drafts", "mimeType": "application/vnd.google-apps.folder", "parents": [self.folder_id]}

            folder = self.service.files().create(body=folder_metadata, fields="id").execute()

            drafts_folder_id = folder.get("id")
            logger.info(f"Created new drafts folder: {drafts_folder_id}")
            return drafts_folder_id

        except Exception as e:
            logger.error(f"Error creating/finding drafts folder: {e}")
            return None

    def get_supporting_materials(self, materials_config: Dict[str, str]) -> Dict[str, List[Dict]]:
        """Get supporting materials organized by type."""
        if not self.available:
            return {}

        materials = {}

        for material_type, subfolder in materials_config.items():
            # Find the subfolder in Google Drive
            subfolder_files = self.list_files(self.folder_id)
            materials[material_type] = []

            for file in subfolder_files:
                if subfolder.lower() in file["name"].lower():
                    materials[material_type].append(
                        {
                            "id": file["id"],
                            "name": file["name"],
                            "type": file["mimeType"],
                            "size": file.get("size", "Unknown"),
                            "modified": file.get("modifiedTime", "Unknown"),
                        }
                    )

        return materials

    def download_materials(self, materials: Dict[str, List[Dict]], local_dir: str = "materials") -> Dict[str, List[str]]:
        """Download supporting materials to local directory."""
        if not self.available:
            return {}

        downloaded_files = {}

        for material_type, files in materials.items():
            downloaded_files[material_type] = []

            for file in files:
                local_path = os.path.join(local_dir, material_type, file["name"])

                if self.download_file(file["id"], local_path):
                    downloaded_files[material_type].append(local_path)

        return downloaded_files

    def search_case_studies(self, keywords: List[str]) -> List[Dict]:
        """Search for case studies matching keywords."""
        if not self.available:
            return []

        all_files = self.list_files(self.folder_id)
        matching_files = []

        for file in all_files:
            file_name_lower = file["name"].lower()

            # Check if any keywords match the file name
            for keyword in keywords:
                if keyword.lower() in file_name_lower:
                    matching_files.append(
                        {
                            "id": file["id"],
                            "name": file["name"],
                            "type": file["mimeType"],
                            "matched_keywords": [k for k in keywords if k.lower() in file_name_lower],
                        }
                    )
                    break

        return matching_files


def setup_google_drive_instructions():
    """Print instructions for setting up Google Drive integration with OAuth."""
    print("\n" + "=" * 60)
    print("GOOGLE DRIVE SETUP INSTRUCTIONS (OAuth)")
    print("=" * 60)
    print("1. Go to Google Cloud Console (https://console.cloud.google.com)")
    print("2. Create a new project or select an existing one")
    print("3. Enable the Google Drive API")
    print("4. Create OAuth 2.0 credentials:")
    print("   - Go to 'APIs & Services' > 'Credentials'")
    print("   - Click 'Create Credentials' > 'OAuth 2.0 Client IDs'")
    print("   - Choose 'Desktop application'")
    print("   - Download the JSON file as 'credentials.json'")
    print("5. Place credentials.json in the project root")
    print("6. Run the agent - it will open a browser for authentication")
    print("7. Grant permissions to access your Google Drive")
    print("8. Update agent_config.yaml with your folder ID")
    print("\nRequired packages:")
    print("pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")
    print("=" * 60)


if __name__ == "__main__":
    # Test the integration
    integration = GoogleDriveIntegration()

    if integration.available:
        print("✅ Google Drive integration is available")
        files = integration.list_files()
        print(f"Found {len(files)} files in root folder")
    else:
        print("❌ Google Drive integration not available")
        setup_google_drive_instructions()
