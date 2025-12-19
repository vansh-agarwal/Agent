"""
Google Calendar API Integration
Manages calendar events, scheduling, and conflict detection
"""

import os
import pickle
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class GoogleCalendarIntegration:
    """Google Calendar API wrapper"""
    
    # Scopes required for calendar access
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    
    def __init__(self, credentials_path: str = 'credentials.json'):
        """Initialize Google Calendar integration"""
        self.credentials_path = credentials_path
        self.creds = None
        self.service = None
        # Don't authenticate immediately - do it lazily when needed
        # This prevents blocking on startup
    
    def _ensure_authenticated(self):
        """Ensure we're authenticated before making API calls"""
        if self.service is not None:
            return True
        
        if not os.path.exists(self.credentials_path):
            print(f"Note: {self.credentials_path} not found. Calendar integration will work in demo mode.")
            return False
        
        try:
            self._authenticate()
            return self.service is not None
        except Exception as e:
            print(f"Calendar authentication error: {e}")
            return False
    
    def _authenticate(self):
        """Authenticate with Google Calendar API"""
        token_path = 'token_calendar.pickle'
        
        # Check if we have saved credentials
        if os.path.exists(token_path):
            with open(token_path, 'rb') as token:
                self.creds = pickle.load(token)
        
        # If no valid credentials, authenticate
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_path):
                    return
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, self.SCOPES)
                self.creds = flow.run_local_server(port=0)
            
            # Save credentials for next run
            with open(token_path, 'wb') as token:
                pickle.dump(self.creds, token)
        
        # Build service
        if self.creds:
            self.service = build('calendar', 'v3', credentials=self.creds)
    
    def create_event(self, event_data: Dict) -> Optional[str]:
        """
        Create a calendar event
        
        Args:
            event_data: Dict with title, description, start_time, end_time, etc.
            
        Returns:
            Event ID if successful, None otherwise
        """
        if not self._ensure_authenticated():
            print("Calendar service not available - operating in demo mode")
            return None
        
        # Parse datetime strings
        start_time = event_data.get('start_time')
        end_time = event_data.get('end_time')
        
        if isinstance(start_time, str):
            start_time = datetime.fromisoformat(start_time)
        if isinstance(end_time, str):
            end_time = datetime.fromisoformat(end_time)
        
        # Build event object
        event = {
            'summary': event_data.get('title', 'Untitled Event'),
            'description': event_data.get('description', ''),
            'start': {
                'dateTime': start_time.isoformat(),
                'timeZone': 'UTC',
            },
            'end': {
                'dateTime': end_time.isoformat(),
                'timeZone': 'UTC',
            },
        }
        
        # Add location if provided
        if event_data.get('location'):
            event['location'] = event_data['location']
        
        # Add attendees if provided
        if event_data.get('attendees'):
            event['attendees'] = [{'email': email} for email in event_data['attendees']]
        
        # Add reminders
        reminder_minutes = event_data.get('reminder_minutes', 15)
        event['reminders'] = {
            'useDefault': False,
            'overrides': [
                {'method': 'email', 'minutes': reminder_minutes},
                {'method': 'popup', 'minutes': 10},
            ],
        }
        
        try:
            created_event = self.service.events().insert(
                calendarId='primary',
                body=event
            ).execute()
            
            print(f"Event created: {created_event.get('htmlLink')}")
            return created_event.get('id')
            
        except HttpError as error:
            print(f"An error occurred: {error}")
            return None
    
    def get_upcoming_events(self, max_results: int = 10) -> List[Dict]:
        """
        Get upcoming calendar events
        
        Args:
            max_results: Maximum number of events to return
            
        Returns:
            List of event dictionaries
        """
        if not self._ensure_authenticated():
            return []
        
        try:
            now = datetime.utcnow().isoformat() + 'Z'
            
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=now,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            # Convert to our format
            formatted_events = []
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                end = event['end'].get('dateTime', event['end'].get('date'))
                
                formatted_events.append({
                    'id': event['id'],
                    'title': event.get('summary', 'No Title'),
                    'description': event.get('description', ''),
                    'start_time': start,
                    'end_time': end,
                    'location': event.get('location', ''),
                    'attendees': [att.get('email') for att in event.get('attendees', [])],
                    'google_event_id': event['id']
                })
            
            return formatted_events
            
        except HttpError as error:
            print(f"An error occurred: {error}")
            return []
    
    def update_event(self, event_id: str, updates: Dict) -> bool:
        """Update an existing calendar event"""
        if not self.service:
            return False
        
        try:
            # Get existing event
            event = self.service.events().get(
                calendarId='primary',
                eventId=event_id
            ).execute()
            
            # Update fields
            if 'title' in updates:
                event['summary'] = updates['title']
            if 'description' in updates:
                event['description'] = updates['description']
            if 'start_time' in updates:
                event['start'] = {
                    'dateTime': updates['start_time'],
                    'timeZone': 'UTC'
                }
            if 'end_time' in updates:
                event['end'] = {
                    'dateTime': updates['end_time'],
                    'timeZone': 'UTC'
                }
            
            # Execute update
            updated_event = self.service.events().update(
                calendarId='primary',
                eventId=event_id,
                body=event
            ).execute()
            
            print(f"Event updated: {updated_event.get('htmlLink')}")
            return True
            
        except HttpError as error:
            print(f"An error occurred: {error}")
            return False
    
    def delete_event(self, event_id: str) -> bool:
        """Delete a calendar event"""
        if not self.service:
            return False
        
        try:
            self.service.events().delete(
                calendarId='primary',
                eventId=event_id
            ).execute()
            
            print(f"Event deleted: {event_id}")
            return True
            
        except HttpError as error:
            print(f"An error occurred: {error}")
            return False
    
    def find_free_slots(self, duration_minutes: int = 60, days_ahead: int = 7) -> List[Dict]:
        """Find available time slots in calendar"""
        if not self.service:
            return []
        
        # Get busy times
        now = datetime.utcnow()
        time_min = now.isoformat() + 'Z'
        time_max = (now + timedelta(days=days_ahead)).isoformat() + 'Z'
        
        try:
            free_busy = self.service.freebusy().query(body={
                'timeMin': time_min,
                'timeMax': time_max,
                'items': [{'id': 'primary'}]
            }).execute()
            
            busy_times = free_busy['calendars']['primary'].get('busy', [])
            
            # Simple algorithm: suggest morning slots (9 AM - 12 PM)
            free_slots = []
            current_date = now.date()
            
            for day in range(days_ahead):
                check_date = current_date + timedelta(days=day)
                
                # Skip weekends
                if check_date.weekday() >= 5:
                    continue
                
                # Check 9 AM, 10 AM, 11 AM slots
                for hour in [9, 10, 11, 14, 15, 16]:
                    slot_start = datetime.combine(check_date, datetime.min.time()).replace(hour=hour)
                    slot_end = slot_start + timedelta(minutes=duration_minutes)
                    
                    # Check if slot overlaps with busy times
                    is_free = True
                    for busy in busy_times:
                        busy_start = datetime.fromisoformat(busy['start'].replace('Z', '+00:00'))
                        busy_end = datetime.fromisoformat(busy['end'].replace('Z', '+00:00'))
                        
                        if slot_start < busy_end and slot_end > busy_start:
                            is_free = False
                            break
                    
                    if is_free:
                        free_slots.append({
                            'start': slot_start.isoformat(),
                            'end': slot_end.isoformat()
                        })
                        
                        if len(free_slots) >= 5:
                            return free_slots
            
            return free_slots
            
        except HttpError as error:
            print(f"An error occurred: {error}")
            return []
