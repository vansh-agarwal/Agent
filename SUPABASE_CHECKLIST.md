# Supabase Setup Checklist

Follow these steps in order. Check off each one as you complete it.

## Step 1: Create Supabase Account ⏳

1. [ ] Go to https://supabase.com
2. [ ] Click "Start your project" or "Sign In"
3. [ ] Sign up with GitHub, Google, or email
4. [ ] Verify your email (check inbox)

## Step 2: Create New Project ⏳

1. [ ] Click "New Project" button
2. [ ] Fill in project details:
   - **Name**: `aria-task-agent` (or your choice)
   - **Database Password**: Create a strong password and SAVE IT
   - **Region**: Choose closest to your location
   - **Pricing Plan**: Free (should be selected by default)
3. [ ] Click "Create new project"
4. [ ] **WAIT 2-3 minutes** for project to provision (grab a coffee ☕)

## Step 3: Get API Keys ⏳

Once project is ready:

1. [ ] Click on **Settings** (gear icon) in left sidebar
2. [ ] Click on **API** section
3. [ ] Find and copy these values:

   **Project URL**: `https://_____________.supabase.co`
   
   Copy here: _______________________________________________

   **anon public key**: `eyJ_____...`
   
   Copy here: _______________________________________________
   
   **service_role key**: `eyJ_____...` (KEEP SECRET!)
   
   Copy here: _______________________________________________

## Step 4: Update .env File ⏳

1. [ ] Open your `.env` file in the project root
2. [ ] Add these lines (paste your actual values):

```env
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=eyJ...your_anon_key...
SUPABASE_SERVICE_KEY=eyJ...your_service_key...
```

3. [ ] Save the file

## Step 5: Run Database Schema ⏳

1. [ ] In Supabase Dashboard, click **SQL Editor** in left sidebar
2. [ ] Click **New query** button
3. [ ] Open `supabase_schema.sql` file from your project
4. [ ] Copy ALL the SQL code
5. [ ] Paste into the Supabase SQL editor
6. [ ] Click **Run** button (bottom right)
7. [ ] Wait for "Success. No rows returned" message
8. [ ] Verify tables were created:
   - [ ] Click **Table Editor** in left sidebar
   - [ ] You should see: tasks, calendar_events, email_notifications, reminders, user_profiles

## Step 6: Configure Google OAuth (Optional) ⏳

1. [ ] Go to **Authentication** → **Providers** in Supabase
2. [ ] Find **Google** provider
3. [ ] Toggle **Enable Google**
4. [ ] Add your Google OAuth credentials:
   - **Client ID**: (from Google Cloud Console)
   - **Client Secret**: (from Google Cloud Console)
5. [ ] Click **Save**

## Step 7: Update Google Cloud Console ⏳

1. [ ] Go to https://console.cloud.google.com
2. [ ] Navigate to **APIs & Services** → **Credentials**
3. [ ] Click on your OAuth 2.0 Client ID
4. [ ] Under **Authorized redirect URIs**, add:
   ```
   https://[your-project-id].supabase.co/auth/v1/callback
   ```
5. [ ] Click **Save**

## Step 8: Test Connection ✅

Once all above steps are complete:

1. [ ] Run: `python test_supabase.py`
2. [ ] You should see all green checkmarks ✅
3. [ ] If any errors, see troubleshooting below

---

## Troubleshooting

**❌ "Invalid API key"**
- Check that you copied the full key (they're very long!)
- Make sure no extra spaces in .env file
- Keys should start with `eyJ`

**❌ "Table 'tasks' does not exist"**
- Go back to Step 5 and run the SQL schema again
- Make sure you ran the ENTIRE schema file

**❌ "Connection timeout"**
- Check your internet connection
- Verify project is "Active" in Supabase dashboard

---

## When All Steps Complete

✅ **You're ready!** Let me know and I'll help you:
1. Migrate the backend to use Supabase
2. Update authentication to use Supabase Auth
3. Test everything works

---

**Current Status**: ⏳ Waiting for setup completion

Let me know when you've completed the steps above or if you need help with any of them!
