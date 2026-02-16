"""
Flask Backend API for AI Personal Task Automation Agent
RESTful API with WebSocket support for real-time updates
"""

import os
import urllib.parse
import sys
from flask import Flask, request, jsonify, send_from_directory, redirect, session, url_for
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix
from datetime import datetime, timedelta
from dotenv import load_dotenv
import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

# Add backend directory to path
sys.path.append(os.path.dirname(__file__))

# Import our modules
from unified_db import UnifiedDB
from models import Priority, TaskStatus
from nlp_engine import NLPEngine
from ai_agent import AIAgent
from workflow_engine import WorkflowEngine
from integrations.google_calendar import GoogleCalendarIntegration
from integrations.gmail import GmailIntegration

# Load environment variables
load_dotenv()

# Fix for Railway proxy - tells Flask to trust X-Forwarded-Proto header
# This fixes the "OAuth 2 MUST utilize https" error
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '0'  # Keep strict for production

# Initialize Flask app
app = Flask(__name__, static_folder='../frontend', static_url_path='')
app.secret_key = os.getenv('SECRET_KEY', '60a2adbb6fd6df4b58196ed15c040bcdf0a4bdfbdcaef03ad05ddc71f06a5ffe')

# Apply ProxyFix to handle Railway's reverse proxy (X-Forwarded-Proto, X-Forwarded-Host)
# This makes Flask correctly identify HTTPS requests coming through Railway's proxy
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

CORS(app, supports_credentials=True, origins=[
    'https://aria-app-sigma.vercel.app',  # Production frontend (Vercel)
    'http://localhost:5000'  # Local development
])

# Initialize components
db = UnifiedDB()
nlp_engine = NLPEngine()
ai_agent = AIAgent(api_key=os.getenv('OPENAI_API_KEY'))

# Initialize integrations (with error handling)
try:
    calendar_integration = GoogleCalendarIntegration(
        os.getenv('GOOGLE_CREDENTIALS_PATH', 'credentials.json')
    )
except Exception as e:
    print(f"Calendar integration disabled: {e}")
    calendar_integration = None

try:
    gmail_integration = GmailIntegration(
        os.getenv('GOOGLE_CREDENTIALS_PATH', 'credentials.json')
    )
except Exception as e:
    print(f"Gmail integration disabled: {e}")
    gmail_integration = None

workflow_engine = WorkflowEngine(db, gmail_integration)

# Conversation history for chat
conversation_history = []

# OAuth configuration
CLIENT_SECRETS_FILE = 'credentials.json'

# For production: create credentials.json from env var if it doesn't exist
# Check both GOOGLE_CREDENTIALS_JSON and GOOGLE_CREDENTIALS_PATH for JSON content
if not os.path.exists(CLIENT_SECRETS_FILE):
    import json
    credentials_json = os.getenv('GOOGLE_CREDENTIALS_JSON') or os.getenv('GOOGLE_CREDENTIALS_PATH')
    if credentials_json and credentials_json.strip().startswith('{'):
        try:
            credentials_data = json.loads(credentials_json)
            with open(CLIENT_SECRETS_FILE, 'w') as f:
                json.dump(credentials_data, f)
            print(f"Created {CLIENT_SECRETS_FILE} from environment variable")
        except Exception as e:
            print(f"Failed to create credentials file: {e}")

SCOPES = [
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.readonly',
    'openid',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile'
]
REDIRECT_URI = os.getenv('GOOGLE_REDIRECT_URI', 
    'https://disciplined-embrace-production-9079.up.railway.app/auth/google/callback')

# ==================== HELPER FUNCTIONS ====================

def get_user_email():
    """Extract user email from request header for data isolation"""
    return request.headers.get('X-User-Email', 'anonymous@demo.com')

def get_google_service_for_user(user_email: str, service_type: str = 'calendar'):
    """
    Create a Google service (Calendar or Gmail) using the user's stored OAuth tokens.
    This enables real Google API calls in production.
    
    Args:
        user_email: The user's email address
        service_type: 'calendar' or 'gmail'
        
    Returns:
        Google API service object or None if tokens not available
    """
    try:
        # Get stored tokens from database
        tokens = db.get_oauth_tokens(user_email)
        
        if not tokens or not tokens.get('google_access_token'):
            print(f"No OAuth tokens found for user: {user_email}")
            return None
        
        # Create credentials from stored tokens
        creds = Credentials(
            token=tokens.get('google_access_token'),
            refresh_token=tokens.get('google_refresh_token'),
            token_uri='https://oauth2.googleapis.com/token',
            client_id=os.getenv('GOOGLE_CLIENT_ID'),
            client_secret=os.getenv('GOOGLE_CLIENT_SECRET')
        )
        
        # Build the appropriate service
        if service_type == 'calendar':
            service = build('calendar', 'v3', credentials=creds)
        elif service_type == 'gmail':
            service = build('gmail', 'v1', credentials=creds)
        else:
            return None
            
        return service
        
    except Exception as e:
        print(f"Error creating Google service for {user_email}: {e}")
        return None


# ==================== AUTH ROUTES ====================

@app.route('/auth/google')
def auth_google():
    """Initiate Google OAuth flow"""
    try:
        flow = Flow.from_client_secrets_file(
            CLIENT_SECRETS_FILE,
            scopes=SCOPES,
            redirect_uri=REDIRECT_URI
        )
        
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'
        )
        
        session['state'] = state
        session['user_email'] = request.args.get('email', '')
        
        return jsonify({
            'authorization_url': authorization_url,
            'state': state
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/auth/google/callback')
def auth_google_callback():
    """Handle Google OAuth callback - STATELESS VERSION (no session dependency)"""
    try:
        # Get the state from the URL (Google includes it in the callback)
        state = request.args.get('state')
        
        # Create flow WITHOUT requiring session state
        # We pass the state from the URL directly
        flow = Flow.from_client_secrets_file(
            CLIENT_SECRETS_FILE,
            scopes=SCOPES,
            redirect_uri=REDIRECT_URI
        )
        
        # Fetch the token using the authorization response URL
        # This works even without the original state because we're on the same redirect_uri
        flow.fetch_token(authorization_response=request.url)
        
        credentials = flow.credentials
        
        # Get user info from Google
        service = build('oauth2', 'v2', credentials=credentials)
        user_info = service.userinfo().get().execute()
        google_email = user_info.get('email', '')
        google_name = user_info.get('name', google_email.split('@')[0] if google_email else 'User')
        
        print(f"OAuth SUCCESS: {google_email} logged in")
        
        # Store tokens in database (optional, but good for later API calls)
        try:
            expiry = credentials.expiry.isoformat() if credentials.expiry else None
            db.save_oauth_tokens(
                user_email=google_email,
                access_token=credentials.token,
                refresh_token=credentials.refresh_token,
                expiry=expiry
            )
        except Exception as db_error:
            print(f"Warning: Could not save tokens to DB: {db_error}")
            # Continue anyway - login can still work
        
        # Redirect to frontend with query parameters
        params = {
            'oauth_success': 'true',
            'email': google_email,
            'name': google_name
        }
        query_string = urllib.parse.urlencode(params)
        redirect_url = f'https://aria-app-sigma.vercel.app/?{query_string}'
        print(f"Redirecting to: {redirect_url}")
        return redirect(redirect_url)
    
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"OAuth callback error: {e}")
        print(f"Full traceback: {error_details}")
        # URL-encode the error message for safe transport
        error_msg = urllib.parse.quote(str(e))
        return redirect(f'https://aria-app-sigma.vercel.app/?oauth_error={error_msg}')

@app.route('/auth/logout', methods=['POST'])
def auth_logout():
    """Logout and clear OAuth tokens"""
    data = request.json
    user_email = data.get('email')
    
    if user_email:
        db.delete_oauth_tokens(user_email)
    
    session.clear()
    return jsonify({'success': True})

@app.route('/auth/status', methods=['GET'])
def auth_status():
    """Check if user has valid OAuth tokens"""
    user_email = request.args.get('email')
    
    if not user_email:
        return jsonify({'authenticated': False})
    
    tokens = db.get_oauth_tokens(user_email)
    
    if tokens and tokens.get('google_access_token'):
        return jsonify({
            'authenticated': True,
            'email': user_email,
            'has_calendar': True,
            'has_gmail': True
        })
    
    return jsonify({'authenticated': False})

# ==================== FRONTEND ROUTES ====================

@app.route('/')
def index():
    """Serve the main page"""
    return send_from_directory(app.static_folder, 'index.html')


# ==================== TASK ROUTES ====================

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    """Get all tasks for the current user"""
    user_email = get_user_email()
    print(f"[{datetime.now().isoformat()}] Fetching tasks for: {user_email}")
    
    status = request.args.get('status')
    tasks = db.get_all_tasks(status=status, user_email=user_email)
    print(f"Found {len(tasks)} tasks in DB for {user_email}")
    
    # Intelligently prioritize if requested
    if request.args.get('prioritize') == 'true':
        tasks = ai_agent.prioritize_tasks(tasks)
    
    return jsonify({'tasks': tasks, 'count': len(tasks)})


@app.route('/api/tasks', methods=['POST'])
def create_task():
    """Create a new task for the current user"""
    try:
        data = request.json
        user_email = get_user_email()
        
        # Add user email to task data
        data['user_email'] = user_email
        
        # Create task in database
        task_id = db.create_task(data, user_email)
        
        # Get the created task
        task = db.get_task(task_id, user_email)
        
        return jsonify({'success': True, 'task': task, 'task_id': task_id}), 201
    except Exception as e:
        print(f"Error creating task: {e}")
        return jsonify({'error': str(e), 'success': False}), 500


@app.route('/api/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    """Get a specific task"""
    task = db.get_task(task_id)
    
    if task:
        return jsonify({'task': task})
    else:
        return jsonify({'error': 'Task not found'}), 404


@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    """Update a task"""
    data = request.json
    success = db.update_task(task_id, data)
    
    if success:
        task = db.get_task(task_id)
        return jsonify({'success': True, 'task': task})
    else:
        return jsonify({'error': 'Task not found'}), 404


@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    """Delete a task"""
    success = db.delete_task(task_id)
    
    if success:
        return jsonify({'success': True})
    else:
        return jsonify({'error': 'Task not found'}), 404


# ==================== CALENDAR ROUTES ====================

@app.route('/api/events', methods=['GET'])
def get_events():
    """Get calendar events for the current user"""
    user_email = get_user_email()
    
    google_events = []
    
    # Try to get from Google Calendar using user's OAuth tokens
    try:
        calendar_service = get_google_service_for_user(user_email, 'calendar')
        if calendar_service:
            from datetime import datetime
            now = datetime.utcnow().isoformat() + 'Z'
            
            events_result = calendar_service.events().list(
                calendarId='primary',
                timeMin=now,
                maxResults=20,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            raw_events = events_result.get('items', [])
            
            for event in raw_events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                end = event['end'].get('dateTime', event['end'].get('date'))
                
                google_events.append({
                    'id': event['id'],
                    'title': event.get('summary', 'No Title'),
                    'description': event.get('description', ''),
                    'start_time': start,
                    'end_time': end,
                    'location': event.get('location', ''),
                    'google_event_id': event['id']
                })
            print(f"Fetched {len(google_events)} events from Google Calendar for {user_email}")
    except Exception as e:
        print(f"Error fetching Google Calendar events: {e}")
    
    # Also get from local database with user filtering
    try:
        local_events = db.get_all_events(user_email=user_email)
    except:
        local_events = []
    
    # Merge (prefer Google Calendar data)
    all_events = google_events + [e for e in local_events if not e.get('google_event_id')]
    
    return jsonify({'events': all_events, 'count': len(all_events)})


@app.route('/api/events', methods=['POST'])
def create_event():
    """Create a calendar event for the current user"""
    data = request.json
    user_email = get_user_email()
    
    # Add user email to event data
    data['user_email'] = user_email
    
    google_event_id = None
    
    # Create in Google Calendar using user's OAuth tokens
    try:
        calendar_service = get_google_service_for_user(user_email, 'calendar')
        if calendar_service:
            # Parse start/end times
            start_time = data.get('start_time')
            end_time = data.get('end_time')
            
            event = {
                'summary': data.get('title', 'Untitled Event'),
                'description': data.get('description', ''),
                'start': {
                    'dateTime': start_time,
                    'timeZone': 'UTC',
                },
                'end': {
                    'dateTime': end_time,
                    'timeZone': 'UTC',
                },
            }
            
            created_event = calendar_service.events().insert(
                calendarId='primary',
                body=event
            ).execute()
            
            google_event_id = created_event.get('id')
            data['google_event_id'] = google_event_id
            print(f"Created Google Calendar event: {google_event_id}")
    except Exception as e:
        print(f"Error creating Google Calendar event: {e}")
    
    # Store in local database
    try:
        event_id = db.create_event(data)
    except Exception as e:
        print(f"Error storing event in database: {e}")
        event_id = None
    
    return jsonify({
        'success': True,
        'event_id': event_id,
        'google_event_id': google_event_id
    }), 201


@app.route('/api/events/<int:event_id>', methods=['DELETE'])
def delete_event(event_id):
    """Delete a calendar event with user verification"""
    user_email = get_user_email()
    
    # Get event to verify ownership and find Google ID
    events = db.get_all_events(user_email=user_email)
    event = next((e for e in events if e['id'] == event_id), None)
    
    if not event:
        return jsonify({'error': 'Event not found or access denied'}), 404
    
    # Delete from Google Calendar if it exists there
    if event.get('google_event_id') and calendar_integration:
        calendar_integration.delete_event(event['google_event_id'])
    
    # Delete from local database
    success = db.delete_event(event_id)
    
    return jsonify({'success': success})


# ==================== EMAIL ROUTES ====================

@app.route('/api/emails/send', methods=['POST'])
def send_email():
    """Send an email"""
    data = request.json
    
    recipient = data.get('recipient')
    subject = data.get('subject')
    body = data.get('body')
    
    if not all([recipient, subject, body]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Send via Gmail or demo mode
    if gmail_integration:
        success = gmail_integration.send_email(recipient, subject, body)
    else:
        # Demo mode - print email
        print(f"\n=== EMAIL (Demo) ===")
        print(f"To: {recipient}")
        print(f"Subject: {subject}")
        print(f"Body:\n{body}")
        print("====================\n")
        success = True
    
    return jsonify({'success': success})


@app.route('/api/emails/recent', methods=['GET'])
def get_recent_emails():
    """Get recent emails"""
    if gmail_integration:
        emails = gmail_integration.get_recent_emails(max_results=10)
    else:
        emails = []
    
    return jsonify({'emails': emails})


# ==================== AI CHAT ROUTES ====================

@app.route('/api/chat', methods=['POST'])
def chat():
    """Process natural language command via AI"""
    data = request.json
    message = data.get('message', '')
    language = data.get('language', 'english')  # Get language preference
    user_email = get_user_email()
    
    if not message:
        return jsonify({'error': 'No message provided'}), 400
    
    # Build context with user-specific data and language
    context = {
        'tasks': db.get_all_tasks(user_email=user_email)[:20],
        'events': db.get_all_events(user_email=user_email)[:10],
        'user_email': user_email,
        'language': language  # Pass language to AI
    }
    
    print(f"[{datetime.now().isoformat()}] Chat Request: {message} (User: {user_email}, Language: {language})")
    
    # Process with AI agent
    result = ai_agent.process_user_input(message, context)
    print(f"AI Result: {json.dumps(result, default=str)}")
    
    # Execute the action
    action_result = execute_action(result, user_email)
    print(f"Action Result for {user_email}: {json.dumps(action_result, default=str)}")
    
    # Generate conversational response with action context and language
    response_text = ai_agent.chat_response(message, conversation_history[-6:], action_result, language)
    
    # Update conversation history
    conversation_history.append({'role': 'user', 'content': message})
    conversation_history.append({'role': 'assistant', 'content': response_text})
    
    return jsonify({
        'response': response_text,
        'action': result.get('action'),
        'action_result': action_result,
        'suggestions': result.get('suggestions', [])
    })


def execute_action(action_data: dict, user_email: str) -> dict:
    """Execute an action based on AI agent decision"""
    action_type = action_data.get('action')
    params = action_data.get('parameters', {})
    
    try:
        if action_type == 'create_task':
            # Create task from parameters
            task_data = {
                'title': params.get('title', 'Untitled Task'),
                'description': params.get('description', ''),
                'priority': params.get('priority', 'MEDIUM'),
                'status': 'todo',
                'deadline': params.get('datetime'),
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
                'tags': params.get('tags', []),
                'estimated_duration': params.get('duration'),
                'user_email': user_email  # Add user isolation
            }
            task_id = db.create_task(task_data, user_email)
            return {'success': True, 'task_id': task_id, 'type': 'task_created'}
        
        elif action_type == 'create_event':
            # Create calendar event
            start_time = params.get('datetime', datetime.now().isoformat())
            duration = params.get('duration', 60)
            start_dt = datetime.fromisoformat(start_time)
            end_dt = start_dt + timedelta(minutes=duration)
            
            event_data = {
                'title': params.get('title', 'Untitled Event'),
                'description': params.get('description', ''),
                'start_time': start_dt.isoformat(),
                'end_time': end_dt.isoformat(),
                'location': params.get('location', ''),
                'attendees': params.get('attendees', []),
                'user_email': user_email
            }
            
            google_event_id = None
            
            # Use user's OAuth tokens for Google Calendar (same as manual creation)
            try:
                calendar_service = get_google_service_for_user(user_email, 'calendar')
                if calendar_service:
                    event = {
                        'summary': event_data.get('title', 'Untitled Event'),
                        'description': event_data.get('description', ''),
                        'start': {
                            'dateTime': event_data['start_time'],
                            'timeZone': 'UTC',
                        },
                        'end': {
                            'dateTime': event_data['end_time'],
                            'timeZone': 'UTC',
                        },
                    }
                    
                    created_event = calendar_service.events().insert(
                        calendarId='primary',
                        body=event
                    ).execute()
                    
                    google_event_id = created_event.get('id')
                    event_data['google_event_id'] = google_event_id
                    print(f"[Chat] Created Google Calendar event: {google_event_id}")
            except Exception as e:
                print(f"[Chat] Error creating Google Calendar event: {e}")
            
            event_id = db.create_event(event_data, user_email)
            return {'success': True, 'event_id': event_id, 'google_event_id': google_event_id, 'type': 'event_created'}
        
        elif action_type == 'send_email':
            # Send email using user's OAuth tokens
            success = False
            try:
                gmail_service = get_google_service_for_user(user_email, 'gmail')
                if gmail_service:
                    import base64
                    from email.message import EmailMessage
                    
                    to_email = params.get('emails', [''])[0]
                    subject = params.get('title', 'Message')
                    body = params.get('description', '')
                    
                    message = EmailMessage()
                    message.set_content(body)
                    message['To'] = to_email
                    message['Subject'] = subject
                    
                    encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
                    
                    gmail_service.users().messages().send(
                        userId='me',
                        body={'raw': encoded_message}
                    ).execute()
                    
                    success = True
                    print(f"[Chat] Email sent to {to_email}")
                else:
                    print(f"[Chat] Gmail service not available for user {user_email}")
            except Exception as e:
                print(f"[Chat] Error sending email: {e}")
            
            return {'success': success, 'type': 'email_sent'}
        
        elif action_type == 'query_tasks':
            tasks = db.get_all_tasks(user_email=user_email)
            return {'success': True, 'tasks': tasks, 'type': 'tasks_retrieved'}
        
        elif action_type == 'query_events':
            events = db.get_all_events(user_email=user_email)
            return {'success': True, 'events': events, 'type': 'events_retrieved'}
        
        else:
            return {'success': False, 'error': f'Unknown action: {action_type}'}
    
    except Exception as e:
        return {'success': False, 'error': str(e)}


# ==================== WORKFLOW ROUTES ====================

@app.route('/api/workflows/check', methods=['POST'])
def check_workflows():
    """Manually trigger workflow checks"""
    workflow_engine.check_and_execute_triggers()
    return jsonify({'success': True, 'message': 'Workflow check completed'})


# ==================== ML PREDICTION ROUTES ====================

# Import ML service
try:
    from ml_service import get_ml_service
    ml_service = get_ml_service()
    print("✅ ML Service initialized")
except Exception as e:
    print(f"⚠️ ML Service not available: {e}")
    ml_service = None


@app.route('/api/ml/status', methods=['GET'])
def ml_status():
    """Get ML models status"""
    if ml_service is None:
        return jsonify({'available': False, 'models': {}})
    
    return jsonify({
        'available': True,
        'models': ml_service.get_model_status()
    })


@app.route('/api/ml/career-predict', methods=['POST'])
def predict_career():
    """
    Predict career income bracket based on demographic data.
    
    Expected JSON body:
    {
        "age": 35,
        "workclass": "Private",
        "education": "Bachelors",
        "education_num": 13,
        "marital_status": "Married-civ-spouse",
        "occupation": "Prof-specialty",
        "relationship": "Husband",
        "race": "White",
        "sex": "Male",
        "capital_gain": 0,
        "capital_loss": 0,
        "hours_per_week": 40,
        "native_country": "United-States"
    }
    """
    if ml_service is None:
        return jsonify({'error': 'ML service not available', 'success': False}), 503
    
    try:
        data = request.json
        result = ml_service.predict_career_income(data)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500


@app.route('/api/ml/hr-analyze', methods=['POST'])
def analyze_hr():
    """
    Analyze employee productivity based on HR metrics.
    
    Expected JSON body:
    {
        "satisfaction_rate": 0.8,
        "salary": 60000,
        "age": 32,
        "position": "Senior",
        "years_at_company": 4,
        "projects_completed": 12
    }
    """
    if ml_service is None:
        return jsonify({'error': 'ML service not available', 'success': False}), 503
    
    try:
        data = request.json
        result = ml_service.predict_hr_productivity(data)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500


@app.route('/api/ml/customer-segment', methods=['POST'])
def segment_customer():
    """
    Segment customer based on RFM analysis.
    
    Expected JSON body:
    {
        "recency": 15,
        "frequency": 8,
        "monetary": 500
    }
    """
    if ml_service is None:
        return jsonify({'error': 'ML service not available', 'success': False}), 503
    
    try:
        data = request.json
        result = ml_service.predict_customer_segment(data)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500


# ==================== UTILITY ROUTES ====================


@app.route('/api/status', methods=['GET'])
def get_status():
    """Get system status and integration availability"""
    try:
        user_email = get_user_email()
        
        # Get counts with error handling
        try:
            tasks_count = len(db.get_all_tasks(user_email=user_email))
        except Exception as e:
            print(f"Error getting tasks count: {e}")
            tasks_count = 0
            
        try:
            events_count = len(db.get_all_events(user_email=user_email))
        except Exception as e:
            print(f"Error getting events count: {e}")
            events_count = 0
        
        return jsonify({
            'status': 'running',
            'integrations': {
                'google_calendar': calendar_integration is not None and hasattr(calendar_integration, 'service') and calendar_integration.service is not None,
                'gmail': gmail_integration is not None and hasattr(gmail_integration, 'service') and gmail_integration.service is not None,
                'openai': ai_agent is not None and hasattr(ai_agent, 'model') and ai_agent.model is not None
            },
            'database': 'connected',
            'tasks_count': tasks_count,
            'events_count': events_count
        })
    except Exception as e:
        print(f"Status endpoint error: {e}")
        # Return a basic status even on error
        return jsonify({
            'status': 'running',
            'integrations': {
                'google_calendar': False,
                'gmail': False,
                'openai': False
            },
            'database': 'error',
            'tasks_count': 0,
            'events_count': 0,
            'error': str(e)
        })


# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500


# ==================== MAIN ====================

if __name__ == '__main__':
    print("\n🚀 AI Personal Task Automation Agent Starting...")
    print("=" * 60)
    print(f"📊 Database: {db.db_path}")
    print(f"🤖 AI Agent: {'Enabled' if ai_agent.model else 'Disabled (NLP only)'}")
    print(f"📅 Google Calendar: {'Connected' if calendar_integration and calendar_integration.service else 'Demo Mode'}")
    print(f"📧 Gmail: {'Connected' if gmail_integration and gmail_integration.service else 'Demo Mode'}")
    print("=" * 60)
    print("\n🌐 Server running on: http://localhost:5000")
    print("📝 Press Ctrl+C to stop\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
