"""
Test script for user data isolation
Verifies that each user can only access their own data
"""

import sys
import os

# Add backend directory to path  
backend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
sys.path.insert(0, backend_path)

from database import Database
from datetime import datetime

def test_user_isolation():
    """Test that user data is properly isolated"""
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tasks.db')
    db = Database(db_path)
    
    print("=" * 60)
    print("Testing User Data Isolation")
    print("=" * 60)
    
    # Create tasks for two different users
    user1_email = "user1@test.com"
    user2_email = "user2@test.com"
    
    print(f"\n1. Creating tasks for {user1_email}...")
    task1_id = db.create_task({
        'title': 'User 1 Task 1',
        'description': 'This belongs to user 1',
        'priority': 'HIGH',
        'status': 'todo',
        'user_email': user1_email,
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat(),
        'tags': ['test']
    })
    print(f"   ✓ Created task {task1_id} for {user1_email}")
    
    print(f"\n2. Creating tasks for {user2_email}...")
    task2_id = db.create_task({
        'title': 'User 2 Task 1',
        'description': 'This belongs to user 2',
        'priority': 'MEDIUM',
        'status': 'todo',
        'user_email': user2_email,
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat(),
        'tags': ['test']
    })
    print(f"   ✓ Created task {task2_id} for {user2_email}")
    
    # Test retrieval isolation
    print(f"\n3. Testing task retrieval isolation...")
    user1_tasks = db.get_all_tasks(user_email=user1_email)
    user2_tasks = db.get_all_tasks(user_email=user2_email)
    
    print(f"   User 1 sees {len(user1_tasks)} tasks")
    print(f"   User 2 sees {len(user2_tasks)} tasks")
    
    # Verify User 1 only sees their task
    user1_task_titles = [t['title'] for t in user1_tasks if 'User 1' in t['title']]
    user1_sees_user2 = any('User 2' in t['title'] for t in user1_tasks)
    
    if user1_sees_user2:
        print("   ❌ FAIL: User 1 can see User 2's tasks!")
        return False
    else:
        print("   ✓ PASS: User 1 cannot see User 2's tasks")
    
    # Verify User 2 only sees their task  
    user2_sees_user1 = any('User 1' in t['title'] for t in user2_tasks)
    
    if user2_sees_user1:
        print("   ❌ FAIL: User 2 can see User 1's tasks!")
        return False
    else:
        print("   ✓ PASS: User 2 cannot see User 1's tasks")
    
    # Test events isolation
    print(f"\n4. Creating events for both users...")
    event1_id = db.create_event({
        'title': 'User 1 Meeting',
        'description': 'User 1 event',
        'start_time': datetime.now().isoformat(),
        'end_time': datetime.now().isoformat(),
        'user_email': user1_email
    })
    print(f"   ✓ Created event {event1_id} for {user1_email}")
    
    event2_id = db.create_event({
        'title': 'User 2 Meeting',
        'description': 'User 2 event',
        'start_time': datetime.now().isoformat(),
        'end_time': datetime.now().isoformat(),
        'user_email': user2_email
    })
    print(f"   ✓ Created event {event2_id} for {user2_email}")
    
    # Test event retrieval isolation
    print(f"\n5. Testing event retrieval isolation...")
    user1_events = db.get_all_events(user_email=user1_email)
    user2_events = db.get_all_events(user_email=user2_email)
    
    print(f"   User 1 sees {len(user1_events)} events")
    print(f"   User 2 sees {len(user2_events)} events")
    
    user1_sees_user2_events = any('User 2' in e['title'] for e in user1_events)
    user2_sees_user1_events = any('User 1' in e['title'] for e in user2_events)
    
    if user1_sees_user2_events:
        print("   ❌ FAIL: User 1 can see User 2's events!")
        return False
    else:
        print("   ✓ PASS: User 1 cannot see User 2's events")
    
    if user2_sees_user1_events:
        print("   ❌ FAIL: User 2 can see User 1's events!")
        return False
    else:
        print("   ✓ PASS: User 2 cannot see User 1's events")
    
    # Cleanup
    print(f"\n6. Cleaning up test data...")
    db.delete_task(task1_id)
    db.delete_task(task2_id)
    db.delete_event(event1_id)
    db.delete_event(event2_id)
    print("   ✓ Cleanup complete")
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED - User data isolation is working!")
    print("=" * 60)
    return True

if __name__ == '__main__':
    try:
        success = test_user_isolation()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
