"""
Test Supabase Connection and Setup
Verifies that Supabase is properly configured
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend'))

def test_supabase_connection():
    """Test Supabase connection and configuration"""
    print("=" * 60)
    print("Supabase Connection Test")
    print("=" * 60)
    
    # Test 1: Check environment variables
    print("\n1. Checking environment variables...")
    from dotenv import load_dotenv
    load_dotenv()
    
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_ANON_KEY')
    
    if not supabase_url:
        print("   ❌ SUPABASE_URL not found in .env")
        print("   → Please add SUPABASE_URL to your .env file")
        return False
    
    if not supabase_key:
        print("   ❌ SUPABASE_ANON_KEY not found in .env")
        print("   → Please add SUPABASE_ANON_KEY to your .env file")
        return False
    
    print(f"   ✓ SUPABASE_URL: {supabase_url[:30]}...")
    print(f"   ✓ SUPABASE_ANON_KEY: {supabase_key[:20]}...")
    
    # Test 2: Initialize Supabase client
    print("\n2. Initializing Supabase client...")
    try:
        from supabase_client import get_supabase_client
        client = get_supabase_client()
        print("   ✓ Supabase client created successfully")
    except Exception as e:
        print(f"   ❌ Failed to create Supabase client: {e}")
        return False
    
    # Test 3: Test connection with a simple query
    print("\n3. Testing database connection...")
    try:
        result = client.table('tasks').select('id').limit(1).execute()
        print(f"   ✓ Successfully connected to Supabase database")
        print(f"   ✓ Tasks table is accessible")
    except Exception as e:
        print(f"   ❌ Database connection failed: {e}")
        print("\n   Possible issues:")
        print("   1. Have you run the SQL schema in Supabase SQL Editor?")
        print("   2. Are your API keys correct?")
        print("   3. Is your Supabase project active?")
        return False
    
    # Test 4: Check all tables exist
    print("\n4. Verifying database schema...")
    tables = ['tasks', 'calendar_events', 'email_notifications', 'reminders', 'user_profiles']
    all_exist = True
    
    for table in tables:
        try:
            client.table(table).select('id').limit(1).execute()
            print(f"   ✓ Table '{table}' exists")
        except Exception as e:
            print(f"   ❌ Table '{table}' not found")
            all_exist = False
    
    if not all_exist:
        print("\n   → Please run supabase_schema.sql in your Supabase SQL Editor")
        return False
    
    # Test 5: Test Supabase DB wrapper
    print("\n5. Testing Supabase DB wrapper...")
    try:
        from supabase_db import SupabaseDB
        db = SupabaseDB()
        print("   ✓ SupabaseDB initialized successfully")
    except Exception as e:
        print(f"   ❌ Failed to initialize SupabaseDB: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED!")
    print("=" * 60)
    print("\nYour Supabase integration is ready to use!")
    print("\nNext steps:")
    print("1. Update your backend to use SupabaseDB")
    print("2. Test authentication with Supabase Auth")
    print("3. Deploy and enjoy cloud-powered database!")
    print()
    
    return True

if __name__ == '__main__':
    try:
        success = test_supabase_connection()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
