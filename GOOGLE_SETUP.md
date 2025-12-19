# 🔐 Google OAuth Setup Guide

This guide will walk you through setting up Google Calendar and Gmail integration for your AI Task Automation Agent.

---

## 📋 Prerequisites

- Google Account
- Google Cloud Console access
- Project folder: `c:\Users\vansh\Desktop\Hackathon`

---

## 🚀 Step-by-Step Setup

### Step 1: Create Google Cloud Project (5 minutes)

1. **Go to Google Cloud Console**
   - Open: https://console.cloud.google.com
   - Sign in with your Google account

2. **Create New Project**
   - Click the project dropdown at the top
   - Click "New Project"
   - Project name: `AI-Task-Automation-Agent` (or any name you like)
   - Click "Create"
   - Wait for project creation (10-20 seconds)

3. **Select Your Project**
   - Click the project dropdown again
   - Select your newly created project

---

### Step 2: Enable Required APIs (3 minutes)

1. **Enable Google Calendar API**
   - In the search bar, type "Google Calendar API"
   - Click on "Google Calendar API"
   - Click the blue "ENABLE" button
   - Wait for it to enable (~5 seconds)

2. **Enable Gmail API**
   - Click the back button or search again
   - Search for "Gmail API"
   - Click on "Gmail API"
   - Click the blue "ENABLE" button
   - Wait for it to enable (~5 seconds)

---

### Step 3: Configure OAuth Consent Screen (5 minutes)

1. **Navigate to OAuth Consent Screen**
   - In the left sidebar, click "APIs & Services"
   - Click "OAuth consent screen"

2. **Choose User Type**
   - Select "External" (for personal use)
   - Click "CREATE"

3. **Fill App Information**
   - **App name:** AI Task Automation Agent
   - **User support email:** Your email address
   - **Developer contact:** Your email address
   - Leave other fields as default
   - Click "SAVE AND CONTINUE"

4. **Scopes (Step 2)**
   - Click "ADD OR REMOVE SCOPES"
   - Search for: `calendar`
   - Check: `.../auth/calendar` (Full access to Google Calendar)
   - Search for: `gmail`
   - Check: `.../auth/gmail.send` (Send email on your behalf)
   - Check: `.../auth/gmail.readonly` (Read email)
   - Click "UPDATE"
   - Click "SAVE AND CONTINUE"

5. **Test Users (Step 3)**
   - Click "+ ADD USERS"
   - Enter your Google email address
   - Click "ADD"
   - Click "SAVE AND CONTINUE"

6. **Review Summary**
   - Scroll down and click "BACK TO DASHBOARD"

---

### Step 4: Create OAuth Credentials (3 minutes)

1. **Navigate to Credentials**
   - In the left sidebar, click "Credentials"

2. **Create OAuth Client ID**
   - Click "+ CREATE CREDENTIALS" at the top
   - Select "OAuth client ID"

3. **Configure Application Type**
   - Application type: **Desktop app**
   - Name: `AI Task Agent Desktop`
   - Click "CREATE"

4. **Download Credentials**
   - A popup will appear with your Client ID and Secret
   - Click "DOWNLOAD JSON"
   - Save the file

---

### Step 5: Install Credentials in Project (2 minutes)

1. **Rename the Downloaded File**
   - The downloaded file is named something like `client_secret_xxxxx.json`
   - Rename it to: `credentials.json`

2. **Move to Project Folder**
   - Move `credentials.json` to: `c:\Users\vansh\Desktop\Hackathon\`
   - It should be in the same folder as `start.bat`

3. **Verify Placement**
   ```
   Hackathon/
   ├── credentials.json    ← Should be here
   ├── start.bat
   ├── README.md
   ├── backend/
   └── frontend/
   ```

---

### Step 6: First Run & Authentication (2 minutes)

1. **Start the Application**
   ```powershell
   cd c:\Users\vansh\Desktop\Hackathon
   python backend/app.py
   ```

2. **Automatic Browser Authentication**
   - When you first run the app, it will automatically open your browser
   - You'll see "Google hasn't verified this app" - Click "Advanced"
   - Click "Go to AI Task Automation Agent (unsafe)"
   - Click "Allow" for Calendar access
   - Click "Allow" for Gmail access
   - You'll see "The authentication flow has completed"
   - Close the browser tab

3. **Tokens Saved**
   - Two files are created automatically:
     - `token_calendar.pickle` (Calendar access)
     - `token_gmail.pickle` (Gmail access)
   - You won't need to authenticate again!

---

## ✅ Verification

After setup, your status badge should show:
- **"Connected"** (green indicator)

To verify integrations:

1. **Check Server Console**
   ```
   🚀 AI Personal Task Automation Agent Starting...
   ============================================================
   📊 Database: tasks.db
   🤖 AI Agent: Enabled
   📅 Google Calendar: Connected    ← Should say Connected
   📧 Gmail: Connected              ← Should say Connected
   ============================================================
   ```

2. **Test Calendar Sync**
   - Create an event in the web interface
   - Check your Google Calendar - it should appear!

3. **Test Email**
   - Send a test email from the interface
   - Check your Gmail sent folder

---

## 🔧 Troubleshooting

### "credentials.json not found"
**Solution:** 
- Make sure `credentials.json` is in the root folder
- Full path: `c:\Users\vansh\Desktop\Hackathon\credentials.json`

### "Access blocked: This app's request is invalid"
**Solution:**
- Make sure you added scopes in OAuth consent screen
- Required scopes:
  - `https://www.googleapis.com/auth/calendar`
  - `https://www.googleapis.com/auth/gmail.send`
  - `https://www.googleapis.com/auth/gmail.readonly`

### "This app isn't verified"
**Solution:** This is normal for development!
- Click "Advanced"
- Click "Go to [app name] (unsafe)"
- This is safe because it's YOUR app

### Authentication browser doesn't open
**Solution:**
- Look in console for a URL
- Copy and paste it into your browser manually

### "Invalid grant" or "Token expired"
**Solution:**
- Delete token files: `token_calendar.pickle` and `token_gmail.pickle`
- Run the app again to re-authenticate

---

## 🎯 Quick Reference

### Files Created During Setup
```
Hackathon/
├── credentials.json          # You download from Google
├── token_calendar.pickle     # Auto-generated on first run
├── token_gmail.pickle        # Auto-generated on first run
└── .env                      # Already exists
```

### Required Scopes
- ✅ `https://www.googleapis.com/auth/calendar` - Full calendar access
- ✅ `https://www.googleapis.com/auth/gmail.send` - Send emails
- ✅ `https://www.googleapis.com/auth/gmail.readonly` - Read emails

### OAuth Flow
1. App requests access → Browser opens
2. You sign in to Google
3. You approve permissions
4. Token saved locally
5. Future requests use saved token (no browser needed)

---

## 🚀 After Setup

Once configured, you can:

✅ **Calendar Features**
- Sync events to Google Calendar
- View upcoming events from Calendar
- Delete events (synced)
- Conflict detection with real Calendar data

✅ **Gmail Features**
- Send actual emails via Gmail
- Read recent emails
- AI-drafted emails sent through your account
- Task reminders sent as real emails

✅ **Full AI Integration**
- "Schedule a meeting tomorrow at 3 PM" → Real calendar event
- "Send an email to john@example.com" → Real email sent
- "What's on my calendar today?" → Shows real events

---

## 🔒 Security Notes

✅ **Your Data is Safe**
- Tokens stored locally on your computer
- No data sent to third parties
- OAuth 2.0 is industry standard (same as Google Drive, Gmail web)

✅ **Revoke Access Anytime**
- Go to: https://myaccount.google.com/permissions
- Find "AI Task Automation Agent"
- Click "Remove Access"

✅ **Keep Credentials Private**
- Never commit `credentials.json` to GitHub
- Already in `.gitignore` for protection
- Token files also ignored

---

## 📞 Support

If you're still having issues:

1. **Check Console Output** - Error messages are helpful
2. **Verify Project Selection** - Make sure you're in the right Google Cloud project
3. **Re-download Credentials** - Sometimes the file gets corrupted
4. **Delete Tokens** - Force re-authentication by deleting `.pickle` files

---

## 🎉 Success!

Once you see:
```
📅 Google Calendar: Connected
📧 Gmail: Connected
```

You're ready to use the full power of AI automation with real Google integration! 🚀

Try: *"Schedule a team meeting tomorrow at 2 PM and send an email to everyone@team.com about it"*
