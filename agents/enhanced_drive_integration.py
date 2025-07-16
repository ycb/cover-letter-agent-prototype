#!/usr/bin/env python3
"""
Enhanced Google Drive Integration with Sheets and Slides API Support
==================================================================

Module for accessing supporting materials (presentations, spreadsheets,
past cover letters) from Google Drive and uploading cover letter drafts.
Includes Google Sheets and Google Slides API support.
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
    import yaml

    GOOGLE_DRIVE_AVAILABLE = True
except ImportError:
    GOOGLE_DRIVE_AVAILABLE = False
    logging.warning(
        "Google Drive API not available. Install with: pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client"
    )

logger = logging.getLogger(__name__)

# OAuth 2.0 scopes
SCOPES = [
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/presentations'
]


class EnhancedGoogleDriveIntegration:
    """Handles Google Drive integration with Sheets and Slides API support."""

    def __init__(self, credentials_file: str = "credentials.json"):
        """Initialize Google Drive integration with OAuth."""
        self.credentials_file = credentials_file
        self.drive_service = None
        self.sheets_service = None
        self.slides_service = None
        self.available = False
        self.token_file = "token.json"

        if GOOGLE_DRIVE_AVAILABLE:
            self._initialize_services()

    def _initialize_services(self):
        """Initialize Google Drive, Sheets, and Slides services with OAuth authentication."""
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

            # Initialize all services
            self.drive_service = build("drive", "v3", credentials=creds)
            self.sheets_service = build("sheets", "v4", credentials=creds)
            self.slides_service = build("slides", "v1", credentials=creds)
            self.available = True
            logger.info("Google Drive, Sheets, and Slides services initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize Google services: {e}")
            self.available = False

    def list_files(self, folder_id: Optional[str] = None, file_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """List files in a Google Drive folder."""
        if not self.available or not self.drive_service:
            return []

        if not folder_id:
            logger.warning("No folder ID specified")
            return []

        try:
            query = f"'{folder_id}' in parents and trashed=false"
            if file_type:
                query += f" and mimeType contains '{file_type}'"

            results = (
                self.drive_service.files()
                .list(q=query, pageSize=100, fields="nextPageToken, files(id, name, mimeType, size, modifiedTime)")
                .execute()
            )

            files = results.get("files", [])
            logger.info(f"Found {len(files)} files in folder")
            return files

        except Exception as e:
            logger.error(f"Error listing files: {e}")
            return []

    def list_all_files_recursive(self, parent_id: str = None, parent_path: str = "", depth: int = 0) -> list:
        """Recursively list all files and folders starting from parent_id. Returns a list of dicts with metadata."""
        if not self.available or not self.drive_service:
            return []
        parent_id = parent_id or 'root'
        all_files = []
        page_token = None
        while True:
            response = self.drive_service.files().list(
                q=f"'{parent_id}' in parents and trashed=false",
                fields="nextPageToken, files(id, name, mimeType, size, modifiedTime, parents)",
                pageToken=page_token
            ).execute()
            files = response.get('files', [])
            for f in files:
                f['parent_path'] = parent_path
                all_files.append(f)
            page_token = response.get('nextPageToken', None)
            if not page_token:
                break
        # Recurse into subfolders
        for f in all_files.copy():
            if f['mimeType'] == 'application/vnd.google-apps.folder':
                sub_path = f"{parent_path}/{f['name']}" if parent_path else f['name']
                sub_files = self.list_all_files_recursive(f['id'], sub_path, depth+1)
                all_files.extend(sub_files)
        return all_files

    def read_sheets_data(self, spreadsheet_id: str, range_name: str = "A:Z") -> List[List[str]]:
        """Read data from Google Sheets."""
        if not self.available or not self.sheets_service:
            logger.error("Google Sheets service not available")
            return []

        try:
            result = self.sheets_service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            logger.info(f"Read {len(values)} rows from Google Sheets")
            return values

        except Exception as e:
            logger.error(f"Error reading Google Sheets: {e}")
            return []

    def read_slides_content(self, presentation_id: str) -> Dict[str, Any]:
        """Read content from Google Slides."""
        if not self.available or not self.slides_service:
            logger.error("Google Slides service not available")
            return {}

        try:
            presentation = self.slides_service.presentations().get(
                presentationId=presentation_id
            ).execute()
            
            slides_content = []
            for slide in presentation.get('slides', []):
                slide_text = []
                for element in slide.get('pageElements', []):
                    if 'shape' in element and 'text' in element['shape']:
                        for text_element in element['shape']['text'].get('textElements', []):
                            if 'textRun' in text_element:
                                slide_text.append(text_element['textRun']['content'])
                
                slides_content.append({
                    'slide_id': slide.get('objectId'),
                    'text': ' '.join(slide_text)
                })
            
            logger.info(f"Read {len(slides_content)} slides from Google Slides")
            return {
                'presentation_id': presentation_id,
                'title': presentation.get('properties', {}).get('title', ''),
                'slides': slides_content
            }

        except Exception as e:
            logger.error(f"Error reading Google Slides: {e}")
            return {}

    def get_job_tracker_data(self, spreadsheet_id: str) -> List[Dict[str, Any]]:
        """Extract job tracker data from Google Sheets."""
        if not spreadsheet_id:
            return []
        
        raw_data = self.read_sheets_data(spreadsheet_id)
        if not raw_data:
            return []
        
        # Assume first row is headers
        headers = raw_data[0] if raw_data else []
        jobs = []
        
        for row in raw_data[1:]:
            job = {}
            for i, value in enumerate(row):
                if i < len(headers):
                    job[headers[i]] = value
            if job:  # Only add non-empty rows
                jobs.append(job)
        
        logger.info(f"Extracted {len(jobs)} job entries from tracker")
        return jobs

    def get_cover_letters_with_metadata(self, folder_id: str) -> List[Dict[str, Any]]:
        """Get cover letters with metadata from Drive folder."""
        files = self.list_files(folder_id=folder_id)
        cover_letters = []
        
        for file in files:
            if file.get('mimeType') == 'application/vnd.google-apps.document':
                # Google Doc - we can extract text
                cover_letters.append({
                    'id': file['id'],
                    'name': file['name'],
                    'type': 'google_doc',
                    'modified': file.get('modifiedTime'),
                    'size': file.get('size')
                })
            elif file.get('mimeType') in ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']:
                # PDF or Word doc
                cover_letters.append({
                    'id': file['id'],
                    'name': file['name'],
                    'type': 'file',
                    'modified': file.get('modifiedTime'),
                    'size': file.get('size')
                })
        
        logger.info(f"Found {len(cover_letters)} cover letter files")
        return cover_letters

    def download_file(self, file_id: str, local_path: str) -> bool:
        """Download a file from Google Drive."""
        if not self.available or not self.drive_service:
            return False

        try:
            request = self.drive_service.files().get_media(fileId=file_id)
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
        self, content: str, filename: str, folder_id: str, mime_type: str = "text/plain"
    ) -> Optional[str]:
        """Upload a file to Google Drive."""
        if not self.available or not self.drive_service:
            logger.error("Google Drive service not available")
            return None

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
            file = self.drive_service.files().create(body=file_metadata, media_body=media, fields="id").execute()

            logger.info(f"Uploaded file to Google Drive: {filename} (ID: {file.get('id')})")
            return file.get("id")

        except Exception as e:
            logger.error(f"Error uploading file: {e}")
            return None


def setup_google_drive_instructions():
    """Print setup instructions for Google Drive integration."""
    print("""
Google Drive Integration Setup
============================

1. Go to Google Cloud Console (https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable the following APIs:
   - Google Drive API
   - Google Sheets API
   - Google Slides API
4. Create OAuth 2.0 credentials:
   - Go to "Credentials" in the left sidebar
   - Click "Create Credentials" > "OAuth 2.0 Client IDs"
   - Choose "Desktop application"
   - Download the credentials file as 'credentials.json'
5. Place 'credentials.json' in the project root
6. Share your Google Drive folders with the service account email

The first time you run the script, it will open a browser window for OAuth authentication.
    """)


def extract_and_stage_drive_content(user_id: str, config: dict):
    """
    Extracts Drive/Sheets/Slides content and stages as per-job, per-example YAML with visibility flags.
    For each example, sets 'company' to the parent folder name, and adds 'file_name', 'file_type', and 'source_folder'.
    Saves work history examples to users/{user}/staging/net_new_stories.yaml and cover letters to users/{user}/cover_letters.yaml.
    """
    import os
    import yaml
    from pathlib import Path
    drive = EnhancedGoogleDriveIntegration(config)
    materials = config.get('google_drive', {}).get('materials', {})
    staging_dir = f"users/{user_id}/staging"
    os.makedirs(staging_dir, exist_ok=True)
    net_new_path = os.path.join(staging_dir, "net_new_stories.yaml")
    cover_letters_path = f"users/{user_id}/cover_letters.yaml"
    staged_examples = []
    staged_cover_letters = []

    # Helper to get folder name from ID
    def get_folder_name(folder_id):
        # Try to map known IDs to names
        for k, v in materials.items():
            if v == folder_id:
                return k.replace('_', ' ').title()
        return folder_id

    # --- Portfolio Work (private by default) ---
    portfolio_id = materials.get('portfolio_work')
    if portfolio_id and isinstance(portfolio_id, str):
        files = drive.list_files(folder_id=portfolio_id)
        folder_name = get_folder_name(portfolio_id)
        for f in files:
            staged_examples.append({
                'company': folder_name,
                'file_name': f.get('name', ''),
                'file_type': f.get('mimeType', ''),
                'source_folder': folder_name,
                'source_url': f"https://drive.google.com/file/d/{f['id']}",
                'type': 'portfolio_artifact',
                'text': f"Portfolio artifact: {f.get('name', '')}",
                'expanded_case_study': None,
                'supporting_artifacts': [{
                    'title': f.get('name', ''),
                    'url': f"https://drive.google.com/file/d/{f['id']}",
                    'visibility': 'private',
                }],
                'tags': ['portfolio', 'artifact'],
            })

    # --- Presentations (private by default) ---
    presentations_id = materials.get('presentations')
    if presentations_id and isinstance(presentations_id, str):
        files = drive.list_files(folder_id=presentations_id)
        folder_name = get_folder_name(presentations_id)
        for f in files:
            staged_examples.append({
                'company': folder_name,
                'file_name': f.get('name', ''),
                'file_type': f.get('mimeType', ''),
                'source_folder': folder_name,
                'source_url': f"https://docs.google.com/presentation/d/{f['id']}",
                'type': 'presentation',
                'text': f"Presentation: {f.get('name', '')}",
                'expanded_case_study': None,
                'supporting_artifacts': [{
                    'title': f.get('name', ''),
                    'url': f"https://docs.google.com/presentation/d/{f['id']}",
                    'visibility': 'private',
                }],
                'tags': ['presentation'],
            })

    # --- Cover Letters (public, staged separately) ---
    cover_letters_id = materials.get('cover_letters')
    if cover_letters_id and isinstance(cover_letters_id, str):
        files = drive.list_files(folder_id=cover_letters_id)
        folder_name = get_folder_name(cover_letters_id)
        for f in files:
            staged_cover_letters.append({
                'company': folder_name,
                'file_name': f.get('name', ''),
                'file_type': f.get('mimeType', ''),
                'source_folder': folder_name,
                'source_url': f"https://docs.google.com/document/d/{f['id']}",
                'position': None,  # Could extract from file name or metadata if available
                'date_applied': f.get('modified', None),
                'cover_letter_text': None,  # Could extract text if needed
                'url': f"https://docs.google.com/document/d/{f['id']}",
                'tags': ['cover_letter'],
                'metadata': {k: v for k, v in f.items() if k not in ['id', 'name', 'mimeType', 'size', 'modifiedTime']},
            })

    # --- Interviewed Folder (role-specific prep) ---
    interviewed_id = '1m6cD7Kun6l4HZcPDlS0OXOdm4KTJCCmQ'
    def scan_interviewed_folder(parent_id, parent_name):
        subfolders = drive.list_files(folder_id=parent_id)
        for sub in subfolders:
            if sub.get('mimeType') == 'application/vnd.google-apps.folder':
                company_name = sub.get('name', 'Unknown')
                # List all files in this subfolder
                files = drive.list_files(folder_id=sub['id'])
                for f in files:
                    if f.get('mimeType') == 'application/vnd.google-apps.folder':
                        continue  # skip nested folders for now
                    staged_examples.append({
                        'company': company_name,
                        'file_name': f.get('name', ''),
                        'file_type': f.get('mimeType', ''),
                        'source_folder': parent_name,
                        'source_url': f"https://drive.google.com/file/d/{f['id']}",
                        'type': 'interview_prep',
                        'text': f"Interview prep artifact: {f.get('name', '')}",
                        'tags': ['interview_prep'],
                    })
    scan_interviewed_folder(interviewed_id, 'Interviewed')

    # --- Star Stories (fix extraction) ---
    star_stories_id = materials.get('star_stories')
    if star_stories_id and isinstance(star_stories_id, str):
        rows = drive.read_sheets_data(star_stories_id)
        headers = rows[0] if rows else []
        folder_name = get_folder_name(star_stories_id)
        for row in rows[1:]:
            if not any(row):
                continue  # skip empty rows
            story = {headers[i]: row[i] for i in range(min(len(headers), len(row)))}
            # Debug: print the story row
            print(f"Star story row: {story}")
            text = story.get('situation', '')
            if not text:
                continue  # skip if no situation text
            staged_examples.append({
                'company': story.get('company', folder_name),
                'file_name': story.get('file_name', ''),
                'file_type': story.get('file_type', ''),
                'source_folder': folder_name,
                'source_url': story.get('source_url', ''),
                'type': 'star_story',
                'text': text,
                'tags': ['star_story'],
            })

    # --- Job Tracker (exclude from new stories) ---
    job_tracker_id = materials.get('job_tracker')
    if job_tracker_id:
        jobs = drive.get_job_tracker_data(job_tracker_id)
        folder_name = get_folder_name(job_tracker_id)
        for job in jobs:
            # Do not add job tracker entries to staged_examples
            pass

    # Save staged examples and cover letters
    with open(net_new_path, 'w') as f:
        yaml.safe_dump(staged_examples, f, sort_keys=False)
    print(f"Staged {len(staged_examples)} work history examples to {net_new_path}")
    with open(cover_letters_path, 'w') as f:
        yaml.safe_dump(staged_cover_letters, f, sort_keys=False)
    print(f"Staged {len(staged_cover_letters)} cover letters to {cover_letters_path}")


if __name__ == "__main__":
    # Test the integration
    drive = EnhancedGoogleDriveIntegration()
    if drive.available:
        print("✅ Google Drive integration is working!")
    else:
        print("❌ Google Drive integration failed")
        setup_google_drive_instructions() 