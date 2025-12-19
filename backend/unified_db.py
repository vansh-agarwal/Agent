"""
Unified Database Wrapper  
Provides a consistent interface for both SQLite and Supabase
"""

from typing import List, Optional, Dict
import os
import sys
from dotenv import load_dotenv

# Add backend directory to path if needed
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

load_dotenv()

# TEMPORARY: Force SQLite for reliability (Supabase key has header issues)
# Set to True when Supabase is properly configured
USE_SUPABASE = False  # os.getenv('SUPABASE_URL') and os.getenv('SUPABASE_ANON_KEY')

if USE_SUPABASE:
    try:
        from supabase_db import SupabaseDB
        print("✅ Using Supabase cloud database")
    except ImportError as e:
        print(f"⚠️  Supabase import failed: {e}, falling back to SQLite")
        from database import Database
        USE_SUPABASE = False
else:
    from database import Database
    print("📁 Using SQLite local database (reliable mode)")


class UnifiedDB:
    """Wrapper that provides consistent interface for both database backends"""
    
    def __init__(self):
        if USE_SUPABASE:
            self.backend = SupabaseDB()
            self.is_supabase = True
            # Add db_path for compatibility
            self.db_path = "supabase"
        else:
            self.backend = Database(os.getenv('DATABASE_PATH', 'tasks.db'))
            self.is_supabase = False
            self.db_path = self.backend.db_path
    
    def create_task(self, task_data: Dict, user_email: str = 'anonymous@demo.com') -> str:
        """Create a task - works with both backends"""
        if self.is_supabase:
            user_id = '00000000-0000-0000-0000-000000000000'
            return self.backend.create_task(task_data, user_id)
        else:
            task_data['user_email'] = user_email
            return self.backend.create_task(task_data)
    
    def get_all_tasks(self, status: Optional[str] = None, user_email: str = 'anonymous@demo.com') -> List[Dict]:
        """Get all tasks - works with both backends"""
        if self.is_supabase:
            return self.backend.get_all_tasks(status=status)
        else:
            return self.backend.get_all_tasks(status=status, user_email=user_email)
    
    def get_task(self, task_id: str, user_email: str = 'anonymous@demo.com') -> Optional[Dict]:
        """Get a single task"""
        if self.is_supabase:
            user_id = '00000000-0000-0000-0000-000000000000'
            return self.backend.get_task(task_id, user_id)
        else:
            return self.backend.get_task(task_id)
    
    def update_task(self, task_id: str, task_data: Dict, user_email: str = 'anonymous@demo.com') -> bool:
        """Update a task"""
        if self.is_supabase:
            user_id = '00000000-0000-0000-0000-000000000000'
            return self.backend.update_task(task_id, task_data, user_id)
        else:
            return self.backend.update_task(task_id, task_data)
    
    def delete_task(self, task_id: str, user_email: str = 'anonymous@demo.com') -> bool:
        """Delete a task"""
        if self.is_supabase:
            user_id = '00000000-0000-0000-0000-000000000000'
            return self.backend.delete_task(task_id, user_id)
        else:
            return self.backend.delete_task(task_id)
    
    def create_event(self, event_data: Dict, user_email: str = 'anonymous@demo.com') -> str:
        """Create an event"""
        if self.is_supabase:
            user_id = '00000000-0000-0000-0000-000000000000'
            return self.backend.create_event(event_data, user_id)
        else:
            event_data['user_email'] = user_email
            return self.backend.create_event(event_data)
    
    def get_all_events(self, user_email: str = 'anonymous@demo.com') -> List[Dict]:
        """Get all events"""
        if self.is_supabase:
            return self.backend.get_all_events()
        else:
            return self.backend.get_all_events(user_email=user_email)
    
    def delete_event(self, event_id: str, user_email: str = 'anonymous@demo.com') -> bool:
        """Delete an event"""
        if self.is_supabase:
            user_id = '00000000-0000-0000-0000-000000000000'
            return self.backend.delete_event(event_id, user_id)
        else:
            return self.backend.delete_event(event_id)
    
    def create_email(self, email_data: Dict, user_email: str = 'anonymous@demo.com') -> str:
        """Create an email notification"""
        if self.is_supabase:
            user_id = '00000000-0000-0000-0000-000000000000'
            return self.backend.create_email(email_data, user_id)
        else:
            email_data['user_email'] = user_email
            return self.backend.create_email(email_data)
    
    def get_pending_emails(self, user_email: str = 'anonymous@demo.com') -> List[Dict]:
        """Get pending emails"""
        if self.is_supabase:
            return self.backend.get_pending_emails()
        else:
            return self.backend.get_pending_emails(user_email=user_email)
    
    def mark_email_sent(self, email_id):
        """Mark an email as sent"""
        return self.backend.mark_email_sent(email_id)
    
    def create_reminder(self, reminder_data: Dict, user_email: str = 'anonymous@demo.com') -> str:
        """Create a reminder"""
        if self.is_supabase:
            user_id = '00000000-0000-0000-0000-000000000000'
            return self.backend.create_reminder(reminder_data, user_id)
        else:
            reminder_data['user_email'] = user_email
            return self.backend.create_reminder(reminder_data)
    
    def get_pending_reminders(self, user_email: str = 'anonymous@demo.com') -> List[Dict]:
        """Get pending reminders"""
        if self.is_supabase:
            return self.backend.get_pending_reminders()
        else:
            return self.backend.get_pending_reminders(user_email=user_email)
    
    def mark_reminder_sent(self, reminder_id):
        """Mark a reminder as sent"""
        return self.backend.mark_reminder_sent(reminder_id)
    
    # Pass through other methods that don't need modification
    def get_user_preferences(self):
        return self.backend.get_user_preferences()
    
    def save_oauth_tokens(self, user_email, access_token, refresh_token, expiry):
        return self.backend.save_oauth_tokens(user_email, access_token, refresh_token, expiry)
    
    def get_oauth_tokens(self, user_email):
        return self.backend.get_oauth_tokens(user_email)
    
    def delete_oauth_tokens(self, user_email):
        return self.backend.delete_oauth_tokens(user_email)
    
    def get_connection(self):
        """Get database connection - for SQLite compatibility"""
        if hasattr(self.backend, 'get_connection'):
            return self.backend.get_connection()
        return None  # Supabase doesn't have a direct connection
