"""
Data Models for AI Personal Task Automation Agent
Defines the core data structures for tasks, events, reminders, and user preferences
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict
from enum import Enum


class Priority(Enum):
    """Task priority levels"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    URGENT = 4


class TaskStatus(Enum):
    """Task completion status"""
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class IntentType(Enum):
    """Types of user intents"""
    CREATE_TASK = "create_task"
    UPDATE_TASK = "update_task"
    DELETE_TASK = "delete_task"
    CREATE_EVENT = "create_event"
    SEND_EMAIL = "send_email"
    QUERY_TASKS = "query_tasks"
    QUERY_EVENTS = "query_events"
    SET_REMINDER = "set_reminder"
    RESCHEDULE = "reschedule"


@dataclass
class Task:
    """Represents a task/todo item"""
    id: Optional[int] = None
    title: str = ""
    description: str = ""
    priority: Priority = Priority.MEDIUM
    status: TaskStatus = TaskStatus.TODO
    deadline: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    tags: List[str] = field(default_factory=list)
    estimated_duration: Optional[int] = None  # in minutes
    assigned_to: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert task to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'priority': self.priority.name,
            'status': self.status.value,
            'deadline': self.deadline.isoformat() if self.deadline else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'tags': self.tags,
            'estimated_duration': self.estimated_duration,
            'assigned_to': self.assigned_to
        }


@dataclass
class CalendarEvent:
    """Represents a calendar event"""
    id: Optional[str] = None
    title: str = ""
    description: str = ""
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    location: str = ""
    attendees: List[str] = field(default_factory=list)
    reminder_minutes: int = 15
    google_event_id: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert event to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'location': self.location,
            'attendees': self.attendees,
            'reminder_minutes': self.reminder_minutes,
            'google_event_id': self.google_event_id
        }


@dataclass
class EmailNotification:
    """Represents an email notification"""
    id: Optional[int] = None
    recipient: str = ""
    subject: str = ""
    body: str = ""
    scheduled_time: Optional[datetime] = None
    sent: bool = False
    task_id: Optional[int] = None
    
    def to_dict(self) -> Dict:
        """Convert email to dictionary"""
        return {
            'id': self.id,
            'recipient': self.recipient,
            'subject': self.subject,
            'body': self.body,
            'scheduled_time': self.scheduled_time.isoformat() if self.scheduled_time else None,
            'sent': self.sent,
            'task_id': self.task_id
        }


@dataclass
class UserIntent:
    """Represents extracted user intent from natural language"""
    intent_type: IntentType
    entities: Dict = field(default_factory=dict)
    confidence: float = 0.0
    original_text: str = ""
    
    def to_dict(self) -> Dict:
        """Convert intent to dictionary"""
        return {
            'intent_type': self.intent_type.value,
            'entities': self.entities,
            'confidence': self.confidence,
            'original_text': self.original_text
        }


@dataclass
class Reminder:
    """Represents a reminder"""
    id: Optional[int] = None
    task_id: Optional[int] = None
    event_id: Optional[str] = None
    reminder_time: datetime = field(default_factory=datetime.now)
    message: str = ""
    sent: bool = False
    notification_type: str = "email"  # email, push, sms
    
    def to_dict(self) -> Dict:
        """Convert reminder to dictionary"""
        return {
            'id': self.id,
            'task_id': self.task_id,
            'event_id': self.event_id,
            'reminder_time': self.reminder_time.isoformat(),
            'message': self.message,
            'sent': self.sent,
            'notification_type': self.notification_type
        }
