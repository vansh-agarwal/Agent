# Fixing Google OAuth Error 400: redirect_uri_mismatch

You're seeing this error because the redirect URI in your code (`http://localhost:5000/auth/google/callback`) hasn't been added to your Google Cloud Console OAuth client configuration.

![OAuth Error](C:/Users/vansh/.gemini/antigravity/brain/407eb6ae-bb74-44de-8024-d70155ef1378/uploaded_image_1766075874432.png)

## Quick Fix Steps

### Option 1: Add Redirect URI to Google Cloud Console (Recommended)

1. **Go to Google Cloud Console**
   - Visit: https://console.cloud.google.com/apis/credentials
   - Make sure you're in the correct project

2. **Edit Your OAuth 2.0 Client ID**
   - Find your OAuth 2.0 Client IDs in the list
   - Click the edit icon (pencil) on your client

3. **Add Authorized Redirect URIs**
   - Scroll down to "Authorized redirect URIs"
   - Click "+ ADD URI"
   - Add these URIs:
     ```
     http://localhost:5000/auth/google/callback
     http://127.0.0.1:5000/auth/google/callback
     ```
   
4. **Save Changes**
   - Click "SAVE" at the bottom
   - Wait 5-10 seconds for changes to propagate

5. **Try Signing In Again**
   - Refresh your application
   - Click "Sign In with Google" again

---

### Option 2: Download New Credentials (If Option 1 Doesn't Work)

If you don't have access to edit the OAuth client or want to start fresh:

1. **Create New OAuth Credentials**
   - Go to https://console.cloud.google.com/apis/credentials
   - Click "+ CREATE CREDENTIALS" → "OAuth client ID"
   - Application type: "Web application"
   - Name: "ARIA Local Development"

2. **Configure**
   - **Authorized JavaScript origins:**
     - `http://localhost:5000`
     - `http://127.0.0.1:5000`
   
   - **Authorized redirect URIs:**
     - `http://localhost:5000/auth/google/callback`
     - `http://127.0.0.1:5000/auth/google/callback`

3. **Download Credentials**
   - Click "CREATE"
   - Download the JSON file
   - Save it as `credentials.json` in your `c:\Users\vansh\Desktop\Hackathon\` directory
   - Replace the existing file

---

## Troubleshooting

### Still Getting the Error?

**Check your credentials.json file:**

```powershell
# View your current credentials
Get-Content credentials.json | ConvertFrom-Json | Select-Object -ExpandProperty web | Select-Object redirect_uris
```

The redirect_uris should include `http://localhost:5000/auth/google/callback`

### Google Showing Different Error?

If you see "This app isn't verified":
- Click "Advanced" → "Go to ARIA (unsafe)"
- This is normal for development apps

### Want to Use a Different Port?

If you need to use a different port (e.g., 3000):

1. Update `backend/app.py` line 74:
   ```python
   REDIRECT_URI = 'http://localhost:3000/auth/google/callback'
   ```

2. Update the port in line 601:
   ```python
   app.run(debug=True, host='0.0.0.0', port=3000)
   ```

3. Add the new URI to Google Cloud Console

---

## What This Error Means

The error occurs because Google OAuth 2.0 requires **exact matching** between:
- The redirect URI sent in the authorization request
- The redirect URIs configured in your OAuth client

**Security Feature**: This prevents malicious apps from stealing your OAuth codes.

---

## Next Steps After Fixing

Once OAuth is working:
1. ✅ Sign in with Google
2. ✅ Grant calendar and Gmail permissions
3. ✅ Get redirected to dashboard
4. ✅ All Google integrations will work

The backend is already configured correctly - you just need to update the Google Cloud Console settings!
