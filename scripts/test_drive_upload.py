#!/usr/bin/env python3
"""
Test Google Drive Upload
=======================

Test script to verify Google Drive upload functionality.
"""

import sys
from pathlib import Path

# Add the agents directory to the path
sys.path.append(str(Path(__file__).parent.parent / "agents"))

from google_drive_integration import GoogleDriveIntegration


def test_drive_upload():
    """Test uploading a cover letter draft to Google Drive."""

    # Initialize Google Drive integration with correct credentials file and folder ID
    drive = GoogleDriveIntegration("cover-letter-agent-02f33aa315d7.json", "1rCpW912CrPC6K0NvYdwnyXFw-f_V66_x")

    if not drive.available:
        print("❌ Google Drive integration not available")
        print("Make sure you have:")
        print("1. Google Drive API credentials file")
        print("2. Required packages installed: google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")
        return False

    print("✅ Google Drive integration available")

    # Test cover letter content
    test_cover_letter = """Dear Hiring Team,

I am excited to apply for the Senior Product Manager position at Test Company. With my experience in building and scaling AI-powered products, I believe I can make significant contributions to your team.

At Meta, I led the development of explainable AI tools for recruiting, which improved trust and adoption by 10X. I also have experience scaling B2B platforms from Series A to C, as demonstrated in my work at Aurora Solar.

I am particularly drawn to Test Company's mission and believe my background in AI/ML products and enterprise customer trust aligns well with your needs.

Best regards,
Peter Spannagle
linkedin.com/in/pspan"""

    # Test upload
    print("\n📤 Uploading test cover letter to Google Drive...")

    file_id = drive.upload_cover_letter_draft(test_cover_letter, "Test Company", "Senior Product Manager", 8.5)

    if file_id:
        print(f"✅ Successfully uploaded to Google Drive drafts folder with ID: {file_id}")
        print("📁 File saved in: [Your Drive Folder]/drafts/")
        return True
    else:
        print("❌ Failed to upload to Google Drive")
        return False


if __name__ == "__main__":
    success = test_drive_upload()
    if success:
        print("\n🎉 Google Drive upload test passed!")
    else:
        print("\n💥 Google Drive upload test failed!")
