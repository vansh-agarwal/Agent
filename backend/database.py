"""
Database Management for AI Personal Task Automation Agent
SQLite database for storing tasks, events, reminders, and user preferences
"""

import sqlite3
from datetime import datetime
from typing import List, Optional, Dict
import json
import os


class Database:
    """Manages all database operations"""
    
    def __init__(self, db_path: str = "tasks.db"):
        """Initialize database connection"""
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        return conn
    
    def init_database(self):
        """Initialize database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Tasks table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_email TEXT NOT NULL DEFAULT 'anonymous@demo.com',
                title TEXT NOT NULL,
                description TEXT,
                priority TEXT DEFAULT 'MEDIUM',
                status TEXT DEFAULT 'todo',
                deadline TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                tags TEXT,
                estimated_duration INTEGER,
                assigned_to TEXT
            )
        ''')
        
        # Calendar events table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS calendar_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_email TEXT NOT NULL DEFAULT 'anonymous@demo.com',
                title TEXT NOT NULL,
                description TEXT,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                location TEXT,
                attendees TEXT,
                reminder_minutes INTEGER DEFAULT 15,
                google_event_id TEXT
            )
        ''')
        
        # Email notifications table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS email_notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_email TEXT NOT NULL DEFAULT 'anonymous@demo.com',
                recipient TEXT NOT NULL,
                subject TEXT NOT NULL,
                body TEXT NOT NULL,
                scheduled_time TEXT,
                sent INTEGER DEFAULT 0,
                task_id INTEGER,
                FOREIGN KEY (task_id) REFERENCES tasks (id)
            )
        ''')
        
        # Reminders table with user isolation
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_email TEXT NOT NULL DEFAULT 'anonymous@demo.com',
                task_id INTEGER,
                event_id INTEGER,
                reminder_time TEXT NOT NULL,
                message TEXT NOT NULL,
                sent INTEGER DEFAULT 0,
                notification_type TEXT DEFAULT 'email',
                FOREIGN KEY (task_id) REFERENCES tasks (id),
                FOREIGN KEY (event_id) REFERENCES calendar_events (id)
            )
        ''')
        
        # User preferences table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE NOT NULL,
                value TEXT NOT NULL
            )
        ''')
        
        # OAuth tokens table for Google integration
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS oauth_tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_email TEXT UNIQUE NOT NULL,
                google_access_token TEXT,
                google_refresh_token TEXT,
                token_expiry TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    # ==================== TASK OPERATIONS ====================
    
    def create_task(self, task_data: Dict) -> int:
        """Create a new task"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO tasks 
            (user_email, title, description, priority, status, deadline, created_at, updated_at, tags, estimated_duration, assigned_to)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            task_data.get('user_email', 'anonymous@demo.com'),
            task_data.get('title'),
            task_data.get('description', ''),
            task_data.get('priority', 'MEDIUM'),
            task_data.get('status', 'todo'),
            task_data.get('deadline'),
            task_data.get('created_at', datetime.now().isoformat()),
            task_data.get('updated_at', datetime.now().isoformat()),
            json.dumps(task_data.get('tags', [])),
            task_data.get('estimated_duration'),
            task_data.get('assigned_to')
        ))
        
        task_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return task_id
    
    def get_task(self, task_id: int) -> Optional[Dict]:
        """Get a task by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM tasks WHERE id = ?', (task_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            task = dict(row)
            task['tags'] = json.loads(task['tags']) if task['tags'] else []
            return task
        return None
    
    def get_all_tasks(self, status: Optional[str] = None, user_email: str = 'anonymous@demo.com') -> List[Dict]:
        """Get all tasks for a specific user, optionally filtered by status"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if status:
            cursor.execute('SELECT * FROM tasks WHERE status = ? AND user_email = ? ORDER BY priority DESC, deadline ASC', (status, user_email))
        else:
            cursor.execute('SELECT * FROM tasks WHERE user_email = ? ORDER BY priority DESC, deadline ASC', (user_email,))
        
        rows = cursor.fetchall()
        conn.close()
        
        tasks = []
        for row in rows:
            task = dict(row)
            task['tags'] = json.loads(task['tags']) if task['tags'] else []
            tasks.append(task)
        
        return tasks
    
    def update_task(self, task_id: int, task_data: Dict) -> bool:
        """Update a task"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Build dynamic update query
        update_fields = []
        values = []
        
        for key, value in task_data.items():
            if key != 'id':
                update_fields.append(f"{key} = ?")
                if key == 'tags':
                    values.append(json.dumps(value))
                else:
                    values.append(value)
        
        update_fields.append("updated_at = ?")
        values.append(datetime.now().isoformat())
        values.append(task_id)
        
        query = f"UPDATE tasks SET {', '.join(update_fields)} WHERE id = ?"
        cursor.execute(query, values)
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return success
    
    def delete_task(self, task_id: int) -> bool:
        """Delete a task"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
        success = cursor.rowcount > 0
        
        conn.commit()
        conn.close()
        return success
    
    # ==================== EVENT OPERATIONS ====================
    
    def create_event(self, event_data: Dict) -> int:
        """Create a new calendar event"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO calendar_events 
            (user_email, title, description, start_time, end_time, location, attendees, reminder_minutes, google_event_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            event_data.get('user_email', 'anonymous@demo.com'),
            event_data.get('title'),
            event_data.get('description', ''),
            event_data.get('start_time'),
            event_data.get('end_time'),
            event_data.get('location', ''),
            json.dumps(event_data.get('attendees', [])),
            event_data.get('reminder_minutes', 15),
            event_data.get('google_event_id')
        ))
        
        event_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return event_id
    
    def get_all_events(self, user_email: str = 'anonymous@demo.com') -> List[Dict]:
        """Get all calendar events for a specific user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM calendar_events WHERE user_email = ? ORDER BY start_time ASC', (user_email,))
        rows = cursor.fetchall()
        conn.close()
        
        events = []
        for row in rows:
            event = dict(row)
            event['attendees'] = json.loads(event['attendees']) if event['attendees'] else []
            events.append(event)
        
        return events
    
    def delete_event(self, event_id: int) -> bool:
        """Delete a calendar event"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM calendar_events WHERE id = ?', (event_id,))
        success = cursor.rowcount > 0
        
        conn.commit()
        conn.close()
        return success
    
    # ==================== EMAIL OPERATIONS ====================
    
    def create_email(self, email_data: Dict) -> int:
        """Create an email notification"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO email_notifications 
            (user_email, recipient, subject, body, scheduled_time, sent, task_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            email_data.get('user_email', 'anonymous@demo.com'),
            email_data.get('recipient'),
            email_data.get('subject'),
            email_data.get('body'),
            email_data.get('scheduled_time'),
            0,
            email_data.get('task_id')
        ))
        
        email_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return email_id
    
    def get_pending_emails(self, user_email: str = 'anonymous@demo.com') -> List[Dict]:
        """Get all unsent emails for a specific user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM email_notifications WHERE sent = 0 AND user_email = ?', (user_email,))
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    # ==================== REMINDER OPERATIONS ====================
    
    def create_reminder(self, reminder_data: Dict) -> int:
        """Create a reminder"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO reminders 
            (user_email, task_id, event_id, reminder_time, message, sent, notification_type)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            reminder_data.get('user_email', 'anonymous@demo.com'),
            reminder_data.get('task_id'),
            reminder_data.get('event_id'),
            reminder_data.get('reminder_time'),
            reminder_data.get('message'),
            0,
            reminder_data.get('notification_type', 'email')
        ))
        
        reminder_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return reminder_id
    
    def get_pending_reminders(self, user_email: str = 'anonymous@demo.com') -> List[Dict]:
        """Get all pending reminders for a specific user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        now = datetime.now().isoformat()
        cursor.execute('SELECT * FROM reminders WHERE sent = 0 AND reminder_time <= ? AND user_email = ?', (now, user_email))
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    # ==================== OAUTH TOKEN OPERATIONS ====================
    
    def save_oauth_tokens(self, user_email: str, access_token: str, refresh_token: str = None, expiry: str = None) -> bool:
        """Save or update OAuth tokens for a user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        now = datetime.now().isoformat()
        
        cursor.execute('''
            INSERT OR REPLACE INTO oauth_tokens 
            (user_email, google_access_token, google_refresh_token, token_expiry, created_at, updated_at)
            VALUES (?, ?, ?, ?, COALESCE((SELECT created_at FROM oauth_tokens WHERE user_email = ?), ?), ?)
        ''', (user_email, access_token, refresh_token, expiry, user_email, now, now))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return success
    
    def get_oauth_tokens(self, user_email: str) -> Optional[Dict]:
        """Get OAuth tokens for a user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM oauth_tokens WHERE user_email = ?', (user_email,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    def delete_oauth_tokens(self, user_email: str) -> bool:
        """Delete OAuth tokens for a user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM oauth_tokens WHERE user_email = ?', (user_email,))
        success = cursor.rowcount > 0
        
        conn.commit()
        conn.close()
        return success
