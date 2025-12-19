"""
Supabase Client Configuration
Provides a singleton Supabase client for the application
"""

import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

# Supabase configuration
SUPABASE_URL = os.getenv('SUPABASE_URL', '')
# Use service_role key for backend (bypasses RLS)
# Check multiple common names for robustness
SUPABASE_KEY = (
    os.getenv('SUPABASE_SERVICE_ROLE_KEY') or 
    os.getenv('SUPABASE_SERVICE_KEY') or 
    os.getenv('SUPABASE_ANON_KEY', '')
)

# Global Supabase client instance
_supabase_client: Client = None


def get_supabase_client() -> Client:
    """
    Get or create the Supabase client instance
    
    Returns:
        Supabase client instance
    """
    global _supabase_client
    
    if _supabase_client is None:
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise ValueError(
                "Supabase credentials not found. Please set SUPABASE_URL and SUPABASE_ANON_KEY in .env file"
            )
        
        _supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ Supabase client initialized")
    
    return _supabase_client


def check_connection() -> bool:
    """
    Check if Supabase connection is working
    
    Returns:
        True if connection is successful, False otherwise
    """
    try:
        client = get_supabase_client()
        # Try a simple query to test connection
        result = client.table('tasks').select('id').limit(1).execute()
        return True
    except Exception as e:
        print(f"Supabase connection error: {e}")
        return False
