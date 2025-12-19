"""
Workflow Engine for Task Automation
Handles trigger-based automation, task dependencies, and proactive reminders
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional
from database import Database
from integrations.gmail import GmailIntegration


class WorkflowEngine:
    """Orchestrates automated workflows and task execution"""
    
    def __init__(self, db: Database, gmail: Optional[GmailIntegration] = None):
        """Initialize workflow engine"""
        self.db = db
        self.gmail = gmail
        self.workflows = []
    
    def check_and_execute_triggers(self):
        """Check for trigger conditions and execute workflows"""
        # Check for upcoming deadlines
        self._check_deadline_reminders()
        
        # Check for pending reminders
        self._process_pending_reminders()
        
        # Check for email notifications
        self._process_pending_emails()
    
    def _check_deadline_reminders(self):
        """Check tasks approaching deadline and send reminders"""
        tasks = self.db.get_all_tasks(status='todo')
        now = datetime.now()
        
        for task in tasks:
            if not task.get('deadline'):
                continue
            
            try:
                deadline = datetime.fromisoformat(task['deadline'])
                time_until = deadline - now
                
                # Send reminder if deadline is within 24 hours
                if timedelta(hours=0) < time_until < timedelta(hours=24):
                    # Check if we already sent a reminder
                    existing_reminders = self.db.get_pending_reminders()
                    reminder_exists = any(
                        r['task_id'] == task['id'] and not r['sent']
                        for r in existing_reminders
                    )
                    
                    if not reminder_exists:
                        # Create reminder
                        reminder_data = {
                            'task_id': task['id'],
                            'reminder_time': (now + timedelta(hours=1)).isoformat(),
                            'message': f"Task '{task['title']}' is due in {time_until.seconds // 3600} hours!",
                            'notification_type': 'email'
                        }
                        self.db.create_reminder(reminder_data)
                        print(f"Created reminder for task: {task['title']}")
            
            except Exception as e:
                print(f"Error checking deadline for task {task.get('id')}: {e}")
    
    def _process_pending_reminders(self):
        """Process and send pending reminders"""
        reminders = self.db.get_pending_reminders()
        
        for reminder in reminders:
            try:
                # Get associated task or event
                message = reminder['message']
                
                if reminder.get('task_id'):
                    task = self.db.get_task(reminder['task_id'])
                    if task:
                        message = f"Reminder: {task['title']}\n\n{task.get('description', '')}"
                
                # Send reminder (for now, just print)
                print(f"\n[REMINDER] {message}")
                
                # Mark as sent
                # self.db.update_reminder(reminder['id'], {'sent': 1})
                
            except Exception as e:
                print(f"Error processing reminder {reminder.get('id')}: {e}")
    
    def _process_pending_emails(self):
        """Send pending email notifications"""
        emails = self.db.get_pending_emails()
        
        for email in emails:
            try:
                if self.gmail:
                    success = self.gmail.send_email(
                        to=email['recipient'],
                        subject=email['subject'],
                        body=email['body']
                    )
                    
                    if success:
                        print(f"Sent email to {email['recipient']}")
                        # Mark as sent in database
                        # self.db.update_email(email['id'], {'sent': 1})
                else:
                    # Demo mode - just print
                    print(f"\n[EMAIL] To: {email['recipient']}")
                    print(f"Subject: {email['subject']}")
                    print(f"Body: {email['body']}\n")
            
            except Exception as e:
                print(f"Error sending email {email.get('id')}: {e}")
    
    def create_follow_up_task(self, original_task: Dict, days_ahead: int = 1) -> int:
        """Automatically create a follow-up task"""
        follow_up = {
            'title': f"Follow-up: {original_task['title']}",
            'description': f"Follow-up from task: {original_task['title']}",
            'priority': original_task.get('priority', 'MEDIUM'),
            'status': 'todo',
            'deadline': (datetime.now() + timedelta(days=days_ahead)).isoformat(),
            'tags': original_task.get('tags', []) + ['follow-up']
        }
        
        return self.db.create_task(follow_up)
    
    def reschedule_task(self, task_id: int, new_deadline: str) -> bool:
        """Reschedule a task to a new deadline"""
        return self.db.update_task(task_id, {
            'deadline': new_deadline,
            'updated_at': datetime.now().isoformat()
        })
    
    def batch_update_priority(self, task_ids: List[int], new_priority: str) -> int:
        """Update priority for multiple tasks"""
        count = 0
        for task_id in task_ids:
            if self.db.update_task(task_id, {'priority': new_priority}):
                count += 1
        return count
    
    def auto_schedule_tasks(self, tasks: List[Dict], available_hours_per_day: int = 6) -> List[Dict]:
        """Automatically schedule tasks based on estimated duration"""
        scheduled = []
        current_time = datetime.now().replace(hour=9, minute=0, second=0)  # Start at 9 AM
        
        for task in tasks:
            duration = task.get('estimated_duration', 60)  # Default 60 minutes
            
            # Schedule task
            task_schedule = {
                'task_id': task['id'],
                'title': task['title'],
                'scheduled_start': current_time.isoformat(),
                'scheduled_end': (current_time + timedelta(minutes=duration)).isoformat()
            }
            
            scheduled.append(task_schedule)
            
            # Move to next time slot
            current_time += timedelta(minutes=duration + 15)  # 15 min buffer
            
            # If past work hours, move to next day
            if current_time.hour >= 17:  # 5 PM
                current_time = (current_time + timedelta(days=1)).replace(hour=9, minute=0)
        
        return scheduled
    
    def detect_conflicts(self, events: List[Dict]) -> List[Dict]:
        """Detect scheduling conflicts between events"""
        conflicts = []
        
        for i, event1 in enumerate(events):
            for event2 in events[i+1:]:
                try:
                    start1 = datetime.fromisoformat(event1['start_time'])
                    end1 = datetime.fromisoformat(event1['end_time'])
                    start2 = datetime.fromisoformat(event2['start_time'])
                    end2 = datetime.fromisoformat(event2['end_time'])
                    
                    # Check for overlap
                    if start1 < end2 and start2 < end1:
                        conflicts.append({
                            'event1': event1['title'],
                            'event2': event2['title'],
                            'time': f"{start1.isoformat()} - {end1.isoformat()}"
                        })
                except:
                    continue
        
        return conflicts
