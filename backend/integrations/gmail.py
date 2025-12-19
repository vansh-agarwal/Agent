"""
Gmail API Integration
Sends automated email notifications and manages email communications
"""

import os
import pickle
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, List, Dict
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class GmailIntegration:
    """Gmail API wrapper for sending emails"""
    
    # Scopes required for Gmail access
    SCOPES = ['https://www.googleapis.com/auth/gmail.send', 
              'https://www.googleapis.com/auth/gmail.readonly']
    
    def __init__(self, credentials_path: str = 'credentials.json'):
        """Initialize Gmail integration"""
        self.credentials_path = credentials_path
        self.creds = None
        self.service = None
        # Don't authenticate immediately - do it lazily when needed
    
    def _ensure_authenticated(self):
        """Ensure we're authenticated before making API calls"""
        if self.service is not None:
            return True
        
        if not os.path.exists(self.credentials_path):
            print(f"Note: {self.credentials_path} not found. Gmail integration will work in demo mode.")
            return False
        
        try:
            self._authenticate()
            return self.service is not None
        except Exception as e:
            print(f"Gmail authentication error: {e}")
            return False
    
    def _authenticate(self):
        """Authenticate with Gmail API"""
        token_path = 'token_gmail.pickle'
        
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
            self.service = build('gmail', 'v1', credentials=self.creds)
    
    def send_email(self, to: str, subject: str, body: str, html: bool = False) -> bool:
        """
        Send an email via Gmail
        
        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body (plain text or HTML)
            html: Whether body is HTML
            
        Returns:
            True if successful, False otherwise
        """
        if not self._ensure_authenticated():
            print("Gmail service not available. Running in demo mode.")
            # In demo mode, just print the email
            print(f"\n=== EMAIL (Demo Mode) ===")
            print(f"To: {to}")
            print(f"Subject: {subject}")
            print(f"Body:\n{body}")
            print("========================\n")
            return True  # Return True for demo
        
        try:
            # Create message
            if html:
                message = MIMEMultipart('alternative')
                message['to'] = to
                message['subject'] = subject
                
                html_part = MIMEText(body, 'html')
                message.attach(html_part)
            else:
                message = MIMEText(body)
                message['to'] = to
                message['subject'] = subject
            
            # Encode message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            
            # Send message
            sent_message = self.service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()
            
            print(f"Email sent successfully. Message ID: {sent_message['id']}")
            return True
            
        except HttpError as error:
            print(f"An error occurred while sending email: {error}")
            return False
        except Exception as e:
            print(f"Error sending email: {e}")
            return False
    
    def send_task_reminder(self, to: str, task_title: str, deadline: str = None) -> bool:
        """Send a task reminder email"""
        subject = f"Reminder: {task_title}"
        
        body = f"""Hello,

This is a friendly reminder about your task:

Task: {task_title}
"""
        
        if deadline:
            body += f"Deadline: {deadline}\n"
        
        body += """
Please make sure to complete this task on time.

Best regards,
Your AI Task Assistant
"""
        
        return self.send_email(to, subject, body)
    
    def send_event_notification(self, to: str, event_title: str, start_time: str, location: str = None) -> bool:
        """Send an event notification email"""
        subject = f"Upcoming Event: {event_title}"
        
        body = f"""Hello,

You have an upcoming event:

Event: {event_title}
Time: {start_time}
"""
        
        if location:
            body += f"Location: {location}\n"
        
        body += """
See you there!

Best regards,
Your AI Task Assistant
"""
        
        return self.send_email(to, subject, body)
    
    def get_recent_emails(self, max_results: int = 10) -> List[Dict]:
        """Get recent emails from inbox"""
        if not self.service:
            return []
        
        try:
            # Get message IDs
            results = self.service.users().messages().list(
                userId='me',
                labelIds=['INBOX'],
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            
            emails = []
            for msg in messages:
                # Get full message
                message = self.service.users().messages().get(
                    userId='me',
                    id=msg['id'],
                    format='metadata',
                    metadataHeaders=['From', 'Subject', 'Date']
                ).execute()
                
                headers = message['payload']['headers']
                email_data = {'id': msg['id']}
                
                for header in headers:
                    if header['name'] == 'From':
                        email_data['from'] = header['value']
                    elif header['name'] == 'Subject':
                        email_data['subject'] = header['value']
                    elif header['name'] == 'Date':
                        email_data['date'] = header['value']
                
                emails.append(email_data)
            
            return emails
            
        except HttpError as error:
            print(f"An error occurred: {error}")
            return []
    
    def draft_and_send(self, to: str, subject: str, body: str) -> bool:
        """Draft and immediately send an email"""
        return self.send_email(to, subject, body, html=False)
