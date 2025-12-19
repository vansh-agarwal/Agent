"""
Demo Data Generator
Creates sample tasks and events for demonstration purposes
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from database import Database
from datetime import datetime, timedelta
import random


def generate_demo_data():
    """Generate demo tasks and events"""
    db = Database('tasks.db')
    
    print("🎨 Generating demo data...")
    
    # Sample tasks
    demo_tasks = [
        {
            'title': 'Review Q4 marketing strategy',
            'description': 'Analyze campaign performance and prepare recommendations for next quarter',
            'priority': 'HIGH',
            'status': 'todo',
            'deadline': (datetime.now() + timedelta(days=2)).isoformat(),
            'tags': ['marketing', 'strategy'],
            'estimated_duration': 120
        },
        {
            'title': 'Update project documentation',
            'description': 'Add API documentation and usage examples',
            'priority': 'MEDIUM',
            'status': 'todo',
            'deadline': (datetime.now() + timedelta(days=5)).isoformat(),
            'tags': ['documentation', 'development'],
            'estimated_duration': 90
        },
        {
            'title': 'Prepare presentation for client meeting',
            'description': 'Create slides showcasing project progress and next milestones',
            'priority': 'URGENT',
            'status': 'in_progress',
            'deadline': (datetime.now() + timedelta(days=1)).isoformat(),
            'tags': ['presentation', 'client'],
            'estimated_duration': 180
        },
        {
            'title': 'Code review for new features',
            'description': 'Review pull requests from team members',
            'priority': 'HIGH',
            'status': 'todo',
            'deadline': (datetime.now() + timedelta(days=3)).isoformat(),
            'tags': ['development', 'code-review'],
            'estimated_duration': 60
        },
        {
            'title': 'Team building activity planning',
            'description': 'Organize next month\'s team event',
            'priority': 'LOW',
            'status': 'todo',
            'deadline': (datetime.now() + timedelta(days=14)).isoformat(),
            'tags': ['team', 'event'],
            'estimated_duration': 45
        },
        {
            'title': 'Research new AI tools',
            'description': 'Explore latest AI automation tools for productivity',
            'priority': 'MEDIUM',
            'status': 'todo',
            'deadline': (datetime.now() + timedelta(days=7)).isoformat(),
            'tags': ['research', 'ai'],
            'estimated_duration': 120
        },
        {
            'title': 'Budget review meeting prep',
            'description': 'Gather financial data and create summary report',
            'priority': 'HIGH',
            'status': 'todo',
            'deadline': (datetime.now() + timedelta(days=4)).isoformat(),
            'tags': ['finance', 'meeting'],
            'estimated_duration': 90
        }
    ]
    
    # Create tasks
    task_ids = []
    for task_data in demo_tasks:
        task_data['created_at'] = datetime.now().isoformat()
        task_data['updated_at'] = datetime.now().isoformat()
        task_id = db.create_task(task_data)
        task_ids.append(task_id)
        print(f"  ✅ Created task: {task_data['title']}")
    
    # Sample events
    demo_events = [
        {
            'title': 'Team Standup',
            'description': 'Daily sync with development team',
            'start_time': (datetime.now() + timedelta(days=1, hours=9)).replace(minute=0, second=0).isoformat(),
            'end_time': (datetime.now() + timedelta(days=1, hours=9, minutes=30)).replace(minute=30, second=0).isoformat(),
            'location': 'Conference Room A',
            'attendees': ['team@company.com']
        },
        {
            'title': 'Client Presentation',
            'description': 'Project update presentation for ABC Corp',
            'start_time': (datetime.now() + timedelta(days=1, hours=14)).replace(minute=0, second=0).isoformat(),
            'end_time': (datetime.now() + timedelta(days=1, hours=15)).replace(minute=0, second=0).isoformat(),
            'location': 'Zoom Meeting',
            'attendees': ['client@abccorp.com']
        },
        {
            'title': 'Project Planning Session',
            'description': 'Q1 roadmap planning with product team',
            'start_time': (datetime.now() + timedelta(days=2, hours=10)).replace(minute=0, second=0).isoformat(),
            'end_time': (datetime.now() + timedelta(days=2, hours=12)).replace(minute=0, second=0).isoformat(),
            'location': 'Meeting Room B',
            'attendees': ['product@company.com', 'engineering@company.com']
        },
        {
            'title': 'One-on-One with Manager',
            'description': 'Weekly check-in meeting',
            'start_time': (datetime.now() + timedelta(days=3, hours=15)).replace(minute=0, second=0).isoformat(),
            'end_time': (datetime.now() + timedelta(days=3, hours=15, minutes=30)).replace(minute=30, second=0).isoformat(),
            'location': 'Manager\'s Office',
            'attendees': []
        },
        {
            'title': 'Lunch with Marketing Team',
            'description': 'Casual lunch meeting to discuss collaboration',
            'start_time': (datetime.now() + timedelta(days=4, hours=12)).replace(minute=0, second=0).isoformat(),
            'end_time': (datetime.now() + timedelta(days=4, hours=13)).replace(minute=0, second=0).isoformat(),
            'location': 'Local Cafe',
            'attendees': ['marketing@company.com']
        }
    ]
    
    # Create events
    for event_data in demo_events:
        event_id = db.create_event(event_data)
        print(f"  📅 Created event: {event_data['title']}")
    
    print(f"\n✨ Demo data generated successfully!")
    print(f"   Tasks created: {len(demo_tasks)}")
    print(f"   Events created: {len(demo_events)}")
    print(f"\n🚀 You can now start the application!")


if __name__ == '__main__':
    generate_demo_data()
