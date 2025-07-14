# 🔧 Google Cloud OAuth 2.0 Setup Guide

## 🚨 Error: invalid_client

The "Error 401: invalid_client" means the OAuth client ID is not properly configured in Google Cloud Console.

## ⚠️ Important: OAuth Scope Information

**Current Scope**: `https://www.googleapis.com/auth/drive`

This scope requests **full access to your Google Drive**. Users will see this in the consent screen:

> "This app wants to access your Google Drive files and folders"

### What This Means for Users:
- ✅ **Full Drive access** is requested during authentication
- ✅ **Only specific folders** are actually accessed by the agent
- ✅ **No browsing** of your entire Drive occurs
- ✅ **All operations** are scoped to the configured folder

### Security Note:
While the app requests full Drive access, it only operates within the folder you specify in the configuration. The broad scope is required by Google's API design, but the agent is programmed to only access the designated folder.

## ✅ Step-by-Step OAuth Setup

### Step 1: Access Google Cloud Console

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Sign in with your Google account
3. Create a new project or select an existing one

### Step 2: Enable Google Drive API

1. In the left sidebar, click **"APIs & Services"** → **"Library"**
2. Search for **"Google Drive API"**
3. Click on **"Google Drive API"**
4. Click **"Enable"**

### Step 3: Create OAuth 2.0 Credentials

1. In the left sidebar, click **"APIs & Services"** → **"Credentials"**
2. Click **"Create Credentials"** at the top
3. Select **"OAuth 2.0 Client IDs"**

### Step 4: Configure OAuth Consent Screen

**If this is your first OAuth app, you'll need to configure the consent screen:**

1. Click **"Configure Consent Screen"**
2. Choose **"External"** (unless you have Google Workspace)
3. Click **"Create"**
4. Fill in the required information:
   - **App name**: "Cover Letter Agent"
   - **User support email**: Your email
   - **Developer contact information**: Your email
   - **App description**: "Generates cover letters and saves drafts to Google Drive"
5. Click **"Save and Continue"**
6. On **"Scopes"** page:
   - Click **"Add or Remove Scopes"**
   - Search for **"Google Drive API"**
   - Select **"../auth/drive"** (Full access to Google Drive)
   - Click **"Update"**
7. On **"Test users"** page, add your email address
8. Click **"Save and Continue"**

### Step 5: Create OAuth Client ID

1. Go back to **"Credentials"**
2. Click **"Create Credentials"** → **"OAuth 2.0 Client IDs"**
3. Choose **"Desktop application"** as the application type
4. Name it **"Cover Letter Agent"**
5. Click **"Create"**

### Step 6: Download Credentials

1. A popup will show your client ID and client secret
2. Click **"Download JSON"**
3. Rename the downloaded file to `credentials.json`
4. Place it in your project root directory

### Step 7: Verify Credentials Format

Your `credentials.json` should look like this:

```json
{
  "installed": {
    "client_id": "123456789-abcdef.apps.googleusercontent.com",
    "project_id": "your-project-id",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_secret": "GOCSPX-your-actual-secret",
    "redirect_uris": ["http://localhost"]
  }
}
```

**Important**: The file must have the `"installed"` section, not `"type": "service_account"`.

### Step 8: Test the Integration

1. Delete any existing `token.json` file (if it exists)
2. Run the test:
   ```bash
   python scripts/test_drive_upload.py
   ```
3. A browser window should open for Google authentication
4. You'll see the consent screen asking for Drive access
5. Grant permissions to access your Google Drive

## 🔧 Troubleshooting

### "invalid_client" Error
- Make sure you're using OAuth 2.0 credentials, not service account
- Verify the credentials.json has the correct format with `"installed"` section
- Check that the client ID and secret are correct

### "Access Denied" Error
- Make sure you added your email as a test user in the consent screen
- Try using a different Google account
- Check that the OAuth consent screen is properly configured

### "Redirect URI" Error
- Make sure you chose "Desktop application" when creating credentials
- The redirect URI should be `http://localhost`

### "API Not Enabled" Error
- Go to APIs & Services → Library
- Search for "Google Drive API"
- Click "Enable"

## 📋 Checklist

- [ ] Created Google Cloud project
- [ ] Enabled Google Drive API
- [ ] Configured OAuth consent screen with Drive scope
- [ ] Created OAuth 2.0 client ID (Desktop application)
- [ ] Downloaded credentials.json
- [ ] Verified credentials format (has "installed" section)
- [ ] Placed credentials.json in project root
- [ ] Deleted old token.json (if exists)
- [ ] Tested authentication flow

## 🚀 Quick Test

After setting up:

```bash
# Test the integration
python scripts/test_drive_upload.py

# Or run the agent
python scripts/run_cover_letter_agent.py --user your_name -i job_description.txt
```

The browser should open for Google authentication, and you should be able to grant permissions successfully.

## 🔒 Privacy & Security

**What users should know:**
- The app requests full Google Drive access during authentication
- The app only accesses files in the configured folder
- No browsing or scanning of the entire Drive occurs
- All operations are scoped to the designated folder
- Users can revoke access anytime in their Google Account settings 