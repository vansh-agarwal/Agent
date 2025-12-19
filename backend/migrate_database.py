"""
Database Migration Script - Add User Email Columns
Adds user_email columns to all tables for multi-user isolation
"""

import sqlite3
from datetime import datetime

def migrate_database(db_path='tasks.db'):
    """Add user_email columns to existing tables"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("=" * 60)
    print("Database Migration: Adding User Email Columns")
    print("=" * 60)
    
    # Add user_email to tasks table
    try:
        cursor.execute("ALTER TABLE tasks ADD COLUMN user_email TEXT NOT NULL DEFAULT 'anonymous@demo.com'")
        print("✅ Added user_email to tasks table")
    except sqlite3.OperationalError as e:
        if "duplicate column" in str(e).lower():
            print("ℹ️  user_email already exists in tasks table")
        else:
            print(f"❌ Error adding user_email to tasks: {e}")
    
    # Add user_email to calendar_events table
    try:
        cursor.execute("ALTER TABLE calendar_events ADD COLUMN user_email TEXT NOT NULL DEFAULT 'anonymous@demo.com'")
        print("✅ Added user_email to calendar_events table")
    except sqlite3.OperationalError as e:
        if "duplicate column" in str(e).lower():
            print("ℹ️  user_email already exists in calendar_events table")
        else:
            print(f"❌ Error adding user_email to calendar_events: {e}")
    
    # Add user_email to email_notifications table
    try:
        cursor.execute("ALTER TABLE email_notifications ADD COLUMN user_email TEXT NOT NULL DEFAULT 'anonymous@demo.com'")
        print("✅ Added user_email to email_notifications table")
    except sqlite3.OperationalError as e:
        if "duplicate column" in str(e).lower():
            print("ℹ️  user_email already exists in email_notifications table")
        else:
            print(f"❌ Error adding user_email to email_notifications: {e}")
    
    # Add user_email to reminders table (if not already added)
    try:
        cursor.execute("ALTER TABLE reminders ADD COLUMN user_email TEXT NOT NULL DEFAULT 'anonymous@demo.com'")
        print("✅ Added user_email to reminders table")
    except sqlite3.OperationalError as e:
        if "duplicate column" in str(e).lower():
            print("ℹ️  user_email already exists in reminders table")
        else:
            print(f"❌ Error adding user_email to reminders: {e}")
    
    conn.commit()
    
    # Verify migration
    print("\\n" + "=" * 60)
    print("Verifying Migration...")
    print("=" * 60)
    
    tables = ['tasks', 'calendar_events', 'email_notifications', 'reminders']
    for table in tables:
        cursor.execute(f"PRAGMA table_info({table})")
        columns = [row[1] for row in cursor.fetchall()]
        if 'user_email' in columns:
            print(f"✅ {table}: user_email column present")
        else:
            print(f"❌ {table}: user_email column MISSING")
    
    conn.close()
    print("\\n✅ Migration complete!")
    print("=" * 60)

if __name__ == '__main__':
    migrate_database()
