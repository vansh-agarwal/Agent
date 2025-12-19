"""
Quick Supabase Diagnostic
"""
import os
from dotenv import load_dotenv

load_dotenv()

print("Checking .env file...")
print(f"SUPABASE_URL: {os.getenv('SUPABASE_URL')}")
print(f"SUPABASE_ANON_KEY: {os.getenv('SUPABASE_ANON_KEY')[:30]}..." if os.getenv('SUPABASE_ANON_KEY') else "NOT SET")

print("\nTrying to connect to Supabase...")
try:
    from supabase import create_client
    
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_ANON_KEY')
    
    if not url or not key:
        print("ERROR: Credentials not found in .env")
    else:
        client = create_client(url, key)
        print("✓ Client created")
        
        # Try to query tasks table
        result = client.table('tasks').select('id').limit(1).execute()
        print("✓ Successfully connected to database!")
        print("✓ Tasks table accessible")
        
except Exception as e:
    print(f"ERROR: {e}")
    print("\nPossible issues:")
    print("1. Did you run the SQL schema in Supabase SQL Editor?")
    print("2. Check if your .env file has the correct credentials")
