"""
Supabase Database Operations
Provides database functionality using Supabase instead of SQLite
"""

from typing import List, Optional, Dict
from datetime import datetime
from supabase_client import get_supabase_client
import json


class SupabaseDB:
    """Supabase database operations wrapper"""
    
    def __init__(self):
        """Initialize Supabase database client"""
        self.client = get_supabase_client()
        self.db_path = "supabase"  # For compatibility
    
    # ==================== TASK OPERATIONS ====================
    
    def create_task(self, task_data: Dict, user_id: str) -> str:
        """
        Create a new task
        
        Args:
            task_data: Task information
            user_id: User UUID from Supabase Auth
            
        Returns:
            Task UUID
        """
        # Prepare task data
        task = {
            'user_id': user_id,
            'title': task_data.get('title'),
            'description': task_data.get('description', ''),
            'priority': task_data.get('priority', 'MEDIUM'),
            'status': task_data.get('status', 'todo'),
            'deadline': task_data.get('deadline'),
            'tags': task_data.get('tags', []),
            'estimated_duration': task_data.get('estimated_duration'),
            'assigned_to': task_data.get('assigned_to')
        }
        
        result = self.client.table('tasks').insert(task).execute()
        return result.data[0]['id'] if result.data else None
    
    def get_task(self, task_id: str, user_id: str) -> Optional[Dict]:
        """Get a task by ID (with RLS, automatically filtered by user)"""
        result = self.client.table('tasks').select('*').eq('id', task_id).execute()
        return result.data[0] if result.data else None
    
    def get_all_tasks(self, status: Optional[str] = None, user_id: str = None) -> List[Dict]:
        """
        Get all tasks for a user (RLS handles user filtering automatically)
        
        Args:
            status: Optional status filter
            user_id: Not needed - RLS handles this automatically
            
        Returns:
            List of tasks
        """
        query = self.client.table('tasks').select('*')
        
        if status:
            query = query.eq('status', status)
        
        # Order by priority and deadline
        query = query.order('created_at', desc=True)
        
        result = query.execute()
        return result.data if result.data else []
    
    def update_task(self, task_id: str, task_data: Dict, user_id: str) -> bool:
        """Update a task (RLS ensures user owns it)"""
        try:
            result = self.client.table('tasks').update(task_data).eq('id', task_id).execute()
            return len(result.data) > 0
        except Exception as e:
            print(f"Error updating task: {e}")
            return False
    
    def delete_task(self, task_id: str, user_id: str) -> bool:
        """Delete a task (RLS ensures user owns it)"""
        try:
            result = self.client.table('tasks').delete().eq('id', task_id).execute()
            return True
        except Exception as e:
            print(f"Error deleting task: {e}")
            return False
    
    # ==================== EVENT OPERATIONS ====================
    
    def create_event(self, event_data: Dict, user_id: str) -> str:
        """Create a new calendar event"""
        event = {
            'user_id': user_id,
            'title': event_data.get('title'),
            'description': event_data.get('description', ''),
            'start_time': event_data.get('start_time'),
            'end_time': event_data.get('end_time'),
            'location': event_data.get('location', ''),
            'attendees': event_data.get('attendees', []),
            'reminder_minutes': event_data.get('reminder_minutes', 15),
            'google_event_id': event_data.get('google_event_id')
        }
        
        result = self.client.table('calendar_events').insert(event).execute()
        return result.data[0]['id'] if result.data else None
    
    def get_all_events(self, user_id: str = None) -> List[Dict]:
        """Get all calendar events for a user (RLS handles filtering)"""
        result = self.client.table('calendar_events')\
            .select('*')\
            .order('start_time', desc=False)\
            .execute()
        
        return result.data if result.data else []
    
    def delete_event(self, event_id: str, user_id: str) -> bool:
        """Delete a calendar event (RLS ensures ownership)"""
        try:
            result = self.client.table('calendar_events').delete().eq('id', event_id).execute()
            return True
        except Exception as e:
            print(f"Error deleting event: {e}")
            return False
    
    # ==================== EMAIL OPERATIONS ====================
    
    def create_email(self, email_data: Dict, user_id: str) -> str:
        """Create an email notification"""
        email = {
            'user_id': user_id,
            'recipient': email_data.get('recipient'),
            'subject': email_data.get('subject'),
            'body': email_data.get('body'),
            'scheduled_time': email_data.get('scheduled_time'),
            'task_id': email_data.get('task_id')
        }
        
        result = self.client.table('email_notifications').insert(email).execute()
        return result.data[0]['id'] if result.data else None
    
    def get_pending_emails(self, user_id: str = None) -> List[Dict]:
        """Get all unsent emails for a user"""
        result = self.client.table('email_notifications')\
            .select('*')\
            .eq('sent', False)\
            .execute()
        
        return result.data if result.data else []
    
    def mark_email_sent(self, email_id):
        """Mark an email as sent"""
        return self.client.table('email_notifications').update({'sent': True}).eq('id', email_id).execute()
    
    # ==================== REMINDER OPERATIONS ====================
    
    def create_reminder(self, reminder_data: Dict, user_id: str) -> str:
        """Create a reminder"""
        reminder = {
            'user_id': user_id,
            'task_id': reminder_data.get('task_id'),
            'event_id': reminder_data.get('event_id'),
            'reminder_time': reminder_data.get('reminder_time'),
            'message': reminder_data.get('message'),
            'notification_type': reminder_data.get('notification_type', 'email')
        }
        
        result = self.client.table('reminders').insert(reminder).execute()
        return result.data[0]['id'] if result.data else None
    
    def get_pending_reminders(self, user_id: str = None) -> List[Dict]:
        """Get all pending reminders for a user"""
        now = datetime.now().isoformat()
        result = self.client.table('reminders')\
            .select('*')\
            .eq('sent', False)\
            .lte('reminder_time', now)\
            .execute()
        
        return result.data if result.data else []
    
    def mark_reminder_sent(self, reminder_id):
        """Mark a reminder as sent"""
        return self.client.table('reminders').update({'sent': True}).eq('id', reminder_id).execute()
    
    # ==================== USER PROFILE OPERATIONS ====================
    
    def get_or_create_user_profile(self, user_id: str, email: str, name: str = None) -> Dict:
        """Get or create user profile"""
        # Try to get existing profile
        result = self.client.table('user_profiles').select('*').eq('id', user_id).execute()
        
        if result.data:
            return result.data[0]
        
        # Create new profile
        profile = {
            'id': user_id,
            'email': email,
            'name': name
        }
        
        result = self.client.table('user_profiles').insert(profile).execute()
        return result.data[0] if result.data else None
    
    # ==================== COMPATIBILITY METHODS ====================
    
    def get_user_preferences(self):
        """Get user preferences - SQLite compatibility"""
        return {}  # TODO: Implement if needed
    
    def save_oauth_tokens(self, user_email, access_token, refresh_token, expiry):
        """Save OAuth tokens - for compatibility"""
        # TODO: Store in supabase or keep in SQLite
        pass
    
    def get_oauth_tokens(self, user_email):
        """Get OAuth tokens - for compatibility"""
        # TODO: Retrieve from supabase or SQLite
        return None
    
    def delete_oauth_tokens(self, user_email):
        """Delete OAuth tokens - for compatibility"""
        # TODO: Delete from supabase or SQLite
        pass
