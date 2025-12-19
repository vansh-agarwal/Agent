# Supabase Setup Guide

## Step 1: Create Supabase Project

1. Go to [supabase.com](https://supabase.com) and sign in/sign up
2. Click "New Project"
3. Fill in project details:
   - **Name**: `aria-task-agent` (or your preferred name)
   - **Database Password**: (create a strong password and save it)
   - **Region**: Choose closest to you
4. Click "Create new project"
5. Wait for project to be provisioned (~2 minutes)

## Step 2: Get Your API Keys

1. Once project is ready, go to **Settings** → **API**
2. Copy the following values:
   - **Project URL**: `https://[your-project-id].supabase.co`
   - **anon public** key: `eyJ...` (long string)
   - **service_role** key: `eyJ...` (keep this SECRET!)

## Step 3: Configure Environment Variables

1. Open `.env` file in your project root
2. Add these lines (replace with your actual values):

```env
# Supabase Configuration
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=your_anon_key_here
SUPABASE_SERVICE_KEY=your_service_key_here

# Keep existing variables
OPENAI_API_KEY=...
GOOGLE_CREDENTIALS_PATH=...
```

## Step 4: Run Database Schema

1. In Supabase Dashboard, go to **SQL Editor**
2. Click **New Query**
3. Copy the contents of `supabase_schema.sql` file
4. Paste into the editor
5. Click **Run** (bottom right)
6. Verify: You should see "Success. No rows returned" message
7. Check **Table Editor** to see your new tables:
   - `tasks`
   - `calendar_events`
   - `email_notifications`
   - `reminders`
   - `user_profiles`

## Step 5: Configure Authentication

1. Go to **Authentication** → **Providers**
2. Enable **Google** provider:
   - Click on Google
   - Toggle **Enable Google**
   - Add your Google OAuth credentials:
     - **Client ID**: (from your Google Cloud Console)
     - **Client Secret**: (from your Google Cloud Console)
   - Click **Save**

### Update Google OAuth Redirect URI

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Navigate to **APIs & Services** → **Credentials**
3. Click on your OAuth 2.0 Client ID
4. In **Authorized redirect URIs**, add:
   ```
   https://[your-project-id].supabase.co/auth/v1/callback
   ```
5. Click **Save**

## Step 6: Test Connection

Run the test script:

```bash
python test_supabase.py
```

You should see:
```
✅ Supabase connection successful!
✅ Can query tasks table
```

## Step 7: Verify Row Level Security

1. In Supabase Dashboard, go to **Authentication** → **Policies**
2. You should see policies for each table:
   - `tasks`: 4 policies (SELECT, INSERT, UPDATE, DELETE)
   - `calendar_events`: 1 policy (ALL)
   - etc.

3. Test RLS:
   - Try to query tasks without being authenticated → Should return empty
   - Sign in with Google → Should see your own tasks only

## Troubleshooting

### Error: "relation 'tasks' does not exist"
- **Solution**: Run the SQL schema again in SQL Editor

### Error: "Invalid API key"
- **Solution**: Check that SUPABASE_URL and SUPABASE_ANON_KEY are correct in `.env`

### Error: "new row violates row-level security policy"
- **Solution**: Make sure you're authenticated (user_id matches auth.uid())

### Google OAuth not working
- **Solution**: Verify redirect URI is added to Google Cloud Console

## Next Steps

Once setup is complete:
1. ✅ Supabase project created
2. ✅ API keys configured in .env
3. ✅ Database schema created
4. ✅ Authentication configured
5. ✅ Connection tested

You're ready to use Supabase! The backend will automatically use Supabase for all database operations.

## Useful Links

- **Supabase Dashboard**: https://app.supabase.com/project/[your-project-id]
- **API Docs**: https://supabase.com/docs/reference/javascript/introduction
- **Python Client**: https://github.com/supabase-community/supabase-py
- **Table Editor**: Check your data visually
- **SQL Editor**: Run custom queries
- **Logs**: Monitor database activity
