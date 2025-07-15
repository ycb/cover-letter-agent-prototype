#!/usr/bin/env python3
"""
Test Google Drive Upload (OAuth)
===============================

Test script to verify Google Drive upload functionality using OAuth 2.0.
"""

import sys
from pathlib import Path

# Add the agents directory to the path
sys.path.append(str(Path(__file__).parent.parent / "agents"))

from google_drive_integration import GoogleDriveIntegration


def test_drive_upload():
    """Test uploading a cover letter draft to Google Drive using OAuth."""

    # Initialize Google Drive integration with OAuth
    drive = GoogleDriveIntegration(
        credentials_file="credentials.json", 
        folder_id="1rCpW912CrPC6K0NvYdwnyXFw-f_V66_x"
    )

    if not drive.available:
        print("❌ Google Drive integration not available")
        print("Make sure you have:")
        print("1. OAuth credentials.json file (not service account)")
        print("2. Required packages installed: google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")
        print("3. Run the agent first to authenticate with Google")
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

    try:
        file_id = drive.upload_cover_letter_draft(test_cover_letter, "Test Company", "Senior Product Manager", 8.5)

        if file_id:
            print(f"✅ Successfully uploaded to Google Drive drafts folder with ID: {file_id}")
            print("📁 File saved in: [Your Drive Folder]/drafts/")
            return True
        else:
            print("❌ Failed to upload to Google Drive")
            print("\n🔧 Troubleshooting:")
            print("1. Check if you have OAuth credentials (not service account)")
            print("2. Verify you've authenticated with Google (run agent first)")
            print("3. Check the error message above for specific issues")
            print("\n📖 See setup_google_drive.py for OAuth setup instructions")
            return False
            
    except Exception as e:
        print(f"❌ Error during upload: {e}")
        if "storageQuotaExceeded" in str(e):
            print("\n🚨 STORAGE QUOTA ISSUE DETECTED!")
            print("This shouldn't happen with OAuth - check your credentials type.")
            print("Make sure you're using OAuth 2.0 credentials, not service account.")
        return False


if __name__ == "__main__":
    success = test_drive_upload()
    if success:
        print("\n🎉 Google Drive upload test passed!")
    else:
        print("\n💥 Google Drive upload test failed!")
        print("\n💡 Need help? Run: python setup_google_drive.py")
