# 🔧 Google Drive Integration Fix (OAuth)

## 🚨 Problem: Service Account Storage Quota

The error you're seeing:
```
Service Accounts do not have storage quota. Leverage shared drives (https://developers.google.com/workspace/drive/api/guides/about-shareddrives), or use OAuth delegation (http://support.google.com/a/answer/7281227) instead.
```

This happens because **Service Accounts don't have storage quota** in regular Google Drive folders.

## ✅ Solution: Use OAuth 2.0 (Recommended)

OAuth 2.0 uses your personal Google account and has no storage quota limitations.

### Step 1: Create OAuth 2.0 Credentials

**📖 For detailed step-by-step instructions, see [Google Cloud OAuth Setup Guide](GOOGLE_CLOUD_OAUTH_SETUP.md)**

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project or select existing
3. Enable Google Drive API
4. Configure OAuth consent screen (required for first-time setup)
5. Go to **"APIs & Services"** → **"Credentials"**
6. Click **"Create Credentials"** → **"OAuth 2.0 Client IDs"**
7. Choose **"Desktop application"**
8. Name it **"Cover Letter Agent"**
9. Download the JSON file as `credentials.json`

### Step 2: Setup Credentials

1. Place `credentials.json` in the project root directory
2. The file should look like this:
   ```json
   {
     "installed": {
       "client_id": "your-client-id.apps.googleusercontent.com",
       "project_id": "your-project-id",
       "auth_uri": "https://accounts.google.com/o/oauth2/auth",
       "token_uri": "https://oauth2.googleapis.com/token",
       "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
       "client_secret": "your-client-secret",
       "redirect_uris": ["http://localhost"]
     }
   }
   ```

### Step 3: Create Google Drive Folder

1. Create a folder in your Google Drive for materials
2. Right-click folder → **"Share"** → **"Copy link"**
3. Get the folder ID from the URL:
   ```
   https://drive.google.com/drive/folders/FOLDER_ID
   ```

### Step 4: First Run Authentication

1. Run the agent for the first time:
   ```bash
   python scripts/run_cover_letter_agent.py --user your_name -i job_description.txt
   ```
2. A browser window will open for Google authentication
3. Grant permissions to access your Google Drive
4. A `token.json` file will be created automatically

### Step 5: Update Configuration

Edit `data/agent_config.yaml`:

```yaml
google_drive:
  enabled: true
  credentials_file: "credentials.json"
  folder_id: "YOUR_FOLDER_ID_HERE"
  use_oauth: true
  token_file: "token.json"
```

### Step 6: Test the Integration

```bash
python scripts/test_drive_upload.py
```

## 🔄 Alternative Solutions

### Option 2: Use Shared Drives (Advanced)

If you have Google Workspace and want to use shared drives:

1. **Create a Shared Drive** in Google Drive
2. **Get the Shared Drive ID** from the URL
3. **Share it** with your service account
4. **Update configuration** to use shared drive ID

### Option 3: Use Google Workspace Service Account

If you have Google Workspace:
- Service accounts work normally with Google Workspace accounts
- No storage quota limitations

## 🛠️ Updated Code

The integration has been updated to use OAuth 2.0:

```python
# Initialize with OAuth
drive = GoogleDriveIntegration(
    credentials_file="credentials.json",
    folder_id="your_folder_id"
)

# Upload to Google Drive
file_id = drive.upload_cover_letter_draft(
    cover_letter, 
    company_name, 
    position_title, 
    job_score
)
```

## 📋 Checklist

- [ ] Create OAuth 2.0 credentials in Google Cloud Console
- [ ] Download credentials.json to project root
- [ ] Create Google Drive folder and get folder ID
- [ ] Run agent first time for authentication
- [ ] Update agent_config.yaml with folder ID
- [ ] Test upload functionality
- [ ] Verify drafts are saved to Google Drive

## 🎯 Benefits of OAuth 2.0

- **No storage quota limits** (uses your personal account)
- **Works with regular Google accounts**
- **No need for shared drives or Google Workspace**
- **Secure authentication flow**
- **Automatic token refresh**

## 🚀 Quick Fix

If you want to test immediately:

1. Create OAuth 2.0 credentials in Google Cloud Console
2. Download as `credentials.json` to project root
3. Create a Google Drive folder and get its ID
4. Run the agent once for authentication
5. Test the upload

This should resolve the storage quota issue and enable full read/write access! 🎉

## 🔧 Troubleshooting

### "Service account" errors
- Make sure you're using OAuth 2.0 credentials, not service account credentials
- OAuth credentials have `"installed"` section, service accounts have `"type": "service_account"`

### Authentication issues
- Delete `token.json` and run the agent again
- Check that `credentials.json` is in the project root
- Verify the credentials file has the correct OAuth 2.0 format

### Permission errors
- Make sure you granted Google Drive access during authentication
- Check that the folder ID is correct
- Verify the folder exists in your Google Drive 