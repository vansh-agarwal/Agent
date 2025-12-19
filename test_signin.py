"""
Quick diagnostic to verify sign-in functionality
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend'))

from database import Database
from datetime import datetime

def test_sign_in_flow():
    """Test the sign-in/OAuth flow"""
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tasks.db')
    db = Database(db_path)
    
    print("=" * 60)
    print("Sign-In Flow Diagnostic")
    print("=" * 60)
    
    # Test 1: Can we save OAuth tokens?
    print("\n1. Testing OAuth token storage...")
    test_email = "test@example.com"
    try:
        success = db.save_oauth_tokens(
            user_email=test_email,
            access_token="test_access_token",
            refresh_token="test_refresh_token",
            expiry=datetime.now().isoformat()
        )
        if success:
            print(f"   ✓ Successfully saved OAuth tokens for {test_email}")
        else:
            print(f"   ❌ Failed to save OAuth tokens")
            return False
    except Exception as e:
        print(f"   ❌ Error saving OAuth tokens: {e}")
        return False
    
    # Test 2: Can we retrieve OAuth tokens?
    print("\n2. Testing OAuth token retrieval...")
    try:
        tokens = db.get_oauth_tokens(test_email)
        if tokens:
            print(f"   ✓ Successfully retrieved OAuth tokens for {test_email}")
            print(f"      Access token: {tokens['google_access_token'][:20]}...")
        else:
            print(f"   ❌ No tokens found")
            return False
    except Exception as e:
        print(f"   ❌ Error retrieving OAuth tokens: {e}")
        return False
    
    # Test 3: Can an anonymous user create tasks?
    print("\n3. Testing anonymous user task creation...")
    try:
        task_id = db.create_task({
            'title': 'Anonymous Task',
            'description': 'Test task',
            'priority': 'MEDIUM',
            'status': 'todo',
            'user_email': 'anonymous@demo.com',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'tags': []
        })
        print(f"   ✓ Anonymous user can create tasks (ID: {task_id})")
        
        # Cleanup
        db.delete_task(task_id)
    except Exception as e:
        print(f"   ❌ Error creating anonymous task: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 4: Can an authenticated user create tasks?
    print("\n4. Testing authenticated user task creation...")
    try:
        task_id = db.create_task({
            'title': 'Authenticated Task',
            'description': 'Test task',
            'priority': 'HIGH',
            'status': 'todo',
            'user_email': test_email,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'tags': []
        })
        print(f"   ✓ Authenticated user can create tasks (ID: {task_id})")
        
        # Cleanup
        db.delete_task(task_id)
    except Exception as e:
        print(f"   ❌ Error creating authenticated task: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 5: Can we delete OAuth tokens (sign out)?
    print("\n5. Testing OAuth token deletion (sign out)...")
    try:
        success = db.delete_oauth_tokens(test_email)
        if success:
            print(f"   ✓ Successfully deleted OAuth tokens for {test_email}")
        else:
            print(f"   ⚠️  No tokens to delete (might be already deleted)")
    except Exception as e:
        print(f"   ❌ Error deleting OAuth tokens: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✅ ALL SIGN-IN TESTS PASSED")
    print("=" * 60)
    print("\nIf you still can't sign in, please check:")
    print("1. Is the backend server running? (python backend/app.py)")
    print("2. Are you accessing http://localhost:5000?")
    print("3. Check browser console for any error messages")
    print("4. Try clearing browser cache/localStorage")
    return True

if __name__ == '__main__':
    try:
        success = test_sign_in_flow()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Diagnostic failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
