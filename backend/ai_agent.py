"""
AI Agent for Personal Task Automation
LLM-based intelligent task planning and autonomous decision-making
Supports Google Gemini API
"""

import os
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from models import Task, CalendarEvent, Priority, IntentType, UserIntent
from nlp_engine import NLPEngine

# Try to import Gemini
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("Warning: google-generativeai not installed. Using NLP-only mode.")


class AIAgent:
    """LLM-powered autonomous agent for task automation"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize AI agent with Gemini or fallback to NLP-only"""
        self.api_key = api_key or os.getenv('GEMINI_API_KEY') or os.getenv('OPENAI_API_KEY')
        self.model = None
        self.nlp_engine = NLPEngine()
        
        # Try to initialize Gemini
        if GEMINI_AVAILABLE and self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-1.5-flash')
                print("✓ Gemini AI initialized successfully")
            except Exception as e:
                print(f"Warning: Could not initialize Gemini: {e}")
                self.model = None
        
        # Agent personality and system prompt
        self.system_prompt = """You are ARIA, an intelligent personal task automation assistant. 
Your role is to help users manage their tasks, calendar events, and emails efficiently.

When the user asks you to do something, respond with a JSON object containing:
- action: The action type (create_task, create_event, send_email, query_tasks, query_events)
- parameters: Object with the action parameters
- response: A friendly response message

For create_task:
- parameters should include: title, description (optional), priority (LOW/MEDIUM/HIGH/URGENT), deadline (ISO datetime, optional)

For create_event:
- parameters should include: title, datetime (ISO format), duration (minutes), location (optional)

For send_email:
- parameters should include: emails (array), title (subject), description (body)

Always respond with valid JSON only."""
    
    def process_user_input(self, user_message: str, context: Optional[Dict] = None) -> Dict:
        """
        Process user input and determine appropriate action
        
        Args:
            user_message: Natural language input from user
            context: Optional context (existing tasks, events, etc.)
            
        Returns:
            Dict with action type and parameters
        """
        # First, use NLP engine for quick local intent extraction
        intent = self.nlp_engine.extract_intent(user_message)
        
        # If we have Gemini configured, use it for enhanced understanding
        if self.model and context:
            try:
                enhanced_result = self._gemini_enhanced_processing(user_message, intent, context)
                return enhanced_result
            except Exception as e:
                print(f"Gemini processing error: {e}")
                # Fallback to NLP-only
                return self._create_action_from_intent(intent)
        else:
            # Fallback to NLP-only processing
            return self._create_action_from_intent(intent)
    
    def _gemini_enhanced_processing(self, user_message: str, base_intent: UserIntent, context: Dict) -> Dict:
        """Use Gemini for enhanced understanding and intelligent decision-making"""
        
        # Prepare context for LLM
        context_str = json.dumps({
            'existing_tasks': context.get('tasks', [])[:10],  # Limit context size
            'upcoming_events': context.get('events', [])[:5],
            'current_time': datetime.now().isoformat()
        }, indent=2, default=str)
        
        # Create prompt for Gemini
        prompt = f"""{self.system_prompt}

User request: "{user_message}"

Current context:
{context_str}

Respond with a JSON object only. No markdown, no explanation, just the JSON."""
        
        try:
            response = self.model.generate_content(prompt)
            result_text = response.text.strip()
            
            # Extract JSON from response (handle markdown code blocks)
            if '```json' in result_text:
                result_text = result_text.split('```json')[1].split('```')[0].strip()
            elif '```' in result_text:
                result_text = result_text.split('```')[1].split('```')[0].strip()
            
            result = json.loads(result_text)
            
            # Merge with base intent for fallback
            result['base_intent'] = base_intent.to_dict()
            
            return result
            
        except Exception as e:
            print(f"Gemini processing error: {e}")
            # Fallback to NLP-only
            return self._create_action_from_intent(base_intent)
    
    def _create_action_from_intent(self, intent: UserIntent) -> Dict:
        """Create action dictionary from NLP intent (fallback when no LLM)"""
        return {
            'action': intent.intent_type.value,
            'parameters': intent.entities,
            'priority': intent.entities.get('priority', 'MEDIUM'),
            'reasoning': 'Based on natural language processing',
            'conflicts': [],
            'suggestions': [],
            'confidence': intent.confidence
        }
    
    def prioritize_tasks(self, tasks: List[Dict]) -> List[Dict]:
        """Intelligently prioritize tasks using AI"""
        
        if not self.model or not tasks:
            # Fallback: simple rule-based prioritization
            return self._rule_based_prioritization(tasks)
        
        # Use Gemini for intelligent prioritization
        tasks_summary = [
            {
                'id': t['id'],
                'title': t['title'],
                'deadline': t.get('deadline'),
                'priority': t.get('priority'),
                'estimated_duration': t.get('estimated_duration')
            }
            for t in tasks[:20]  # Limit to avoid token limits
        ]
        
        prompt = f"""Analyze these tasks and suggest optimal prioritization order:

Tasks:
{json.dumps(tasks_summary, indent=2, default=str)}

Current time: {datetime.now().isoformat()}

Provide a JSON object with: {{"prioritized_ids": [id1, id2, id3, ...], "reasoning": "brief explanation"}}
Respond with JSON only."""
        
        try:
            response = self.model.generate_content(prompt)
            result_text = response.text.strip()
            
            if '```json' in result_text:
                result_text = result_text.split('```json')[1].split('```')[0].strip()
            elif '```' in result_text:
                result_text = result_text.split('```')[1].split('```')[0].strip()
            
            result = json.loads(result_text)
            prioritized_ids = result.get('prioritized_ids', [])
            
            # Reorder tasks based on LLM suggestions
            id_to_task = {t['id']: t for t in tasks}
            prioritized = []
            for task_id in prioritized_ids:
                if task_id in id_to_task:
                    prioritized.append(id_to_task[task_id])
            
            # Add any remaining tasks not included in prioritization
            for task in tasks:
                if task not in prioritized:
                    prioritized.append(task)
            
            return prioritized
            
        except Exception as e:
            print(f"Prioritization error: {e}")
            return self._rule_based_prioritization(tasks)
    
    def _rule_based_prioritization(self, tasks: List[Dict]) -> List[Dict]:
        """Simple rule-based prioritization fallback"""
        priority_order = {'URGENT': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
        
        def sort_key(task):
            priority_score = priority_order.get(task.get('priority', 'MEDIUM'), 2)
            deadline = task.get('deadline')
            if deadline:
                try:
                    deadline_dt = datetime.fromisoformat(deadline.replace('Z', '+00:00'))
                    hours_until = (deadline_dt - datetime.now()).total_seconds() / 3600
                    time_score = max(0, min(100, hours_until))
                except:
                    time_score = 100
            else:
                time_score = 100
            return (priority_score, time_score)
        
        return sorted(tasks, key=sort_key)
    
    def suggest_schedule(self, events: List[Dict], new_event_duration: int) -> Dict:
        """Suggest optimal time slot for new event"""
        
        if not self.model:
            # Fallback: suggest next available hour
            now = datetime.now()
            suggested = now.replace(hour=now.hour + 1, minute=0, second=0, microsecond=0)
            return {
                'suggested_time': suggested.isoformat(),
                'reasoning': 'Next available hour slot'
            }
        
        # Use Gemini for intelligent scheduling
        events_summary = [
            {
                'title': e.get('title'),
                'start': e.get('start_time'),
                'end': e.get('end_time')
            }
            for e in events[:10]
        ]
        
        prompt = f"""Analyze these existing events and suggest the best time for a {new_event_duration}-minute meeting:

Existing events:
{json.dumps(events_summary, indent=2, default=str)}

Current time: {datetime.now().isoformat()}

Suggest an optimal time slot. Respond with JSON: {{"suggested_time": "ISO datetime", "reasoning": "brief explanation"}}"""
        
        try:
            response = self.model.generate_content(prompt)
            result_text = response.text.strip()
            
            if '```json' in result_text:
                result_text = result_text.split('```json')[1].split('```')[0].strip()
            elif '```' in result_text:
                result_text = result_text.split('```')[1].split('```')[0].strip()
            
            return json.loads(result_text)
        except Exception as e:
            print(f"Schedule suggestion error: {e}")
            now = datetime.now()
            suggested = now.replace(hour=now.hour + 1, minute=0, second=0, microsecond=0)
            return {
                'suggested_time': suggested.isoformat(),
                'reasoning': 'Next available hour slot'
            }
    
    def draft_email(self, subject: str, context: str, tone: str = 'professional') -> str:
        """Draft an email using AI"""
        
        if not self.model:
            return f"Subject: {subject}\n\n{context}"
        
        prompt = f"""Draft a {tone} email with the following:

Subject: {subject}
Context/Key Points: {context}

Write a complete, well-structured email that is concise and clear. Respond with just the email body."""
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"Email drafting error: {e}")
            return f"Subject: {subject}\n\n{context}"
    
    def chat_response(self, user_message: str, conversation_history: List[Dict] = None, action_result: Dict = None) -> str:
        """Generate conversational response to user"""
        
        # If we have action result, generate a response based on that
        if action_result and action_result.get('success'):
            action_type = action_result.get('type', '')
            if action_type == 'task_created':
                return f"✅ Done! I've created that task for you. You can see it in your task list."
            elif action_type == 'event_created':
                return f"📅 Great! I've scheduled that event on your calendar."
            elif action_type == 'email_sent':
                return f"📧 Email sent successfully!"
            elif action_type == 'tasks_retrieved':
                tasks = action_result.get('tasks', [])
                if tasks:
                    return f"📋 You have {len(tasks)} task(s). Check the tasks panel to see them all."
                return "📋 You don't have any tasks yet. Want me to create one?"
            elif action_type == 'events_retrieved':
                events = action_result.get('events', [])
                if events:
                    return f"📅 You have {len(events)} upcoming event(s). Check your calendar panel."
                return "📅 No upcoming events. Shall I schedule something?"
        
        # Try Gemini for natural conversation
        if self.model:
            prompt = f"""You are ARIA, a helpful AI assistant. Respond conversationally to the user.
Keep responses brief and friendly. If you performed an action, confirm it.

User: {user_message}

Respond naturally in 1-2 sentences."""
            
            try:
                response = self.model.generate_content(prompt)
                return response.text.strip()
            except Exception as e:
                print(f"Chat error: {e}")
                # Fall through to rule-based response
        
        # Rule-based responses when Gemini unavailable
        msg_lower = user_message.lower()
        
        if any(word in msg_lower for word in ['task', 'todo', 'remind']):
            return "I'll create that task for you. Check your task list!"
        elif any(word in msg_lower for word in ['meeting', 'schedule', 'calendar', 'event']):
            return "I'll add that to your calendar. Check the events section!"
        elif any(word in msg_lower for word in ['email', 'send', 'mail']):
            return "Use the email form below to send your message."
        elif any(word in msg_lower for word in ['hi', 'hello', 'hey']):
            return "Hello! 👋 I can help you create tasks, schedule events, and compose emails. Just tell me what you need!"
        elif any(word in msg_lower for word in ['help', 'what can']):
            return "I can help you with:\n• Creating tasks: 'Add task to review documents'\n• Scheduling events: 'Schedule meeting tomorrow at 2pm'\n• Sending emails: 'Email john about the project'"
        else:
            return "I'm processing your request. Check your tasks and calendar for updates!"
