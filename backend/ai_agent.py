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
        
        # Agent personality and system prompt - ENHANCED FOR GENERAL INTELLIGENCE
        self.system_prompt = """You are ARIA, an intelligent AI assistant with broad knowledge and task automation capabilities.
You can help users with:
1. Task management (creating tasks, todos)
2. Calendar/scheduling (events, meetings, appointments with times)
3. Email composition and sending
4. GENERAL KNOWLEDGE questions on ANY topic (science, history, math, coding, health, etc.)
5. ML-powered predictions (career advice, productivity analysis, customer insights)
6. Complex problem solving and explanations

## CATEGORIZATION RULES:

### RULE 1: ANYTHING WITH A SPECIFIC TIME → create_event (CALENDAR)
If the user mentions a time ("at 6:30 pm", "tomorrow at 3pm"), use create_event

### RULE 2: TASK WITHOUT TIME → create_task
Use create_task when user says "task", "todo", "remind me" without specific time

### RULE 3: GENERAL QUESTIONS → general_response
For questions like:
- "What is quantum computing?"
- "How does photosynthesis work?"
- "Explain machine learning"
- "What's the capital of France?"
- "Help me with this code"
- "Give me career advice"
Use action: "general_response" and provide a helpful answer

### RULE 4: ML PREDICTION REQUESTS → ml_prediction
For requests like:
- "Predict my career income"
- "Analyze employee productivity"
- "What customer segment am I?"
Use action: "ml_prediction" with appropriate type

## RESPONSE FORMAT:
{
  "action": "create_task" | "create_event" | "send_email" | "query_tasks" | "query_events" | "general_response" | "ml_prediction",
  "parameters": {...},
  "response": "Your helpful response"
}

For general_response:
- Provide accurate, helpful information
- Be conversational and engaging
- Use examples and analogies when helpful

RESPOND WITH VALID JSON ONLY. NO MARKDOWN. NO EXPLANATION OUTSIDE JSON."""

    
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
    
    def chat_response(self, user_message: str, conversation_history: List[Dict] = None, action_result: Dict = None, language: str = 'english') -> str:
        """Generate conversational response to user in selected language"""
        
        # Language-specific responses for actions
        action_responses = {
            'english': {
                'task_created': "✅ Done! I've added that to your task list. Is there anything else you'd like me to help with?",
                'event_created': "📅 Perfect! I've scheduled that event on your calendar. You're all set! 🎉",
                'email_sent': "📧 Your email has been sent! Let me know if you need to send another.",
                'tasks_retrieved': "📋 Here are your tasks! You've got {} task(s). Anything you'd like me to add or change?",
                'events_retrieved': "📅 You have {} upcoming event(s). Want me to schedule something new?",
                'no_tasks': "📋 Your task list is empty! That's great if you're all done, or I can help add something new.",
                'no_events': "📅 No upcoming events on your calendar. Want me to schedule one?"
            },
            'hindi': {
                'task_created': "✅ हो गया! मैंने इसे आपकी टास्क लिस्ट में जोड़ दिया है। क्या कुछ और मदद चाहिए?",
                'event_created': "📅 बढ़िया! मैंने यह इवेंट आपके कैलेंडर में शेड्यूल कर दिया है! 🎉",
                'email_sent': "📧 आपका ईमेल भेज दिया गया है! बताइए क्या कुछ और भेजना है?",
                'tasks_retrieved': "📋 आपके {} टास्क हैं। कुछ जोड़ना या बदलना है?",
                'events_retrieved': "📅 आपके {} आगामी इवेंट हैं। कुछ नया शेड्यूल करना है?",
                'no_tasks': "📋 आपकी टास्क लिस्ट खाली है! कुछ नया जोड़ूं?",
                'no_events': "📅 कोई आगामी इवेंट नहीं है। कुछ शेड्यूल करूं?"
            },
            'tamil': {
                'task_created': "✅ முடிந்தது! உங்கள் பணிப்பட்டியலில் சேர்த்துவிட்டேன். வேறு ஏதாவது உதவி வேண்டுமா?",
                'event_created': "📅 அருமை! உங்கள் நாட்காட்டியில் நிகழ்வை திட்டமிட்டுவிட்டேன்! 🎉",
                'email_sent': "📧 உங்கள் மின்னஞ்சல் அனுப்பப்பட்டது! வேறு ஏதாவது அனுப்ப வேண்டுமா?",
                'tasks_retrieved': "📋 உங்களுக்கு {} பணிகள் உள்ளன। ஏதாவது சேர்க்க வேண்டுமா?",
                'events_retrieved': "📅 உங்களுக்கு {} வரவிருக்கும் நிகழ்வுகள் உள்ளன। புதியதை திட்டமிடலாமா?",
                'no_tasks': "📋 உங்கள் பணிப்பட்டியல் காலியாக உள்ளது! புதிதாக சேர்க்கலாமா?",
                'no_events': "📅 வரவிருக்கும் நிகழ்வுகள் இல்லை. ஏதாவது திட்டமிடலாமா?"
            }
        }
        
        responses = action_responses.get(language, action_responses['english'])
        
        # If we have action result, generate a response based on that
        if action_result and action_result.get('success'):
            action_type = action_result.get('type', '')
            if action_type == 'task_created':
                return responses['task_created']
            elif action_type == 'event_created':
                return responses['event_created']
            elif action_type == 'email_sent':
                return responses['email_sent']
            elif action_type == 'tasks_retrieved':
                tasks = action_result.get('tasks', [])
                if tasks:
                    return responses['tasks_retrieved'].format(len(tasks))
                return responses['no_tasks']
            elif action_type == 'events_retrieved':
                events = action_result.get('events', [])
                if events:
                    return responses['events_retrieved'].format(len(events))
                return responses['no_events']
        
        # Try Gemini for natural conversation in selected language
        if self.model:
            lang_instruction = {
                'english': 'Respond in English.',
                'hindi': 'Respond in Hindi (हिंदी में जवाब दें). Use Devanagari script.',
                'tamil': 'Respond in Tamil (தமிழில் பதிலளிக்கவும்). Use Tamil script.'
            }
            
            prompt = f"""You are ARIA, a highly intelligent AI assistant with BROAD KNOWLEDGE on any topic.

## YOUR CAPABILITIES:
1. **General Knowledge**: Answer questions about science, history, geography, math, technology, culture, etc.
2. **Technical Help**: Explain coding, algorithms, software, engineering concepts
3. **Life Advice**: Career guidance, personal development, health tips, productivity advice
4. **Problem Solving**: Help analyze problems, provide solutions, compare options
5. **Creative Tasks**: Write stories, poems, summaries, explanations
6. **Task Management**: Schedule events, create tasks, send emails

## PERSONALITY:
- Warm, friendly, and genuinely helpful 😊
- Uses occasional emojis to express emotions
- Explains complex topics in simple, understandable ways
- Provides accurate, well-reasoned answers
- Admits when uncertain and suggests alternatives

## IMPORTANT RULES:
- For factual questions, provide accurate, detailed answers
- For complex topics, break down explanations step-by-step
- For career/life questions, give thoughtful, practical advice
- Always be helpful - never say "I can only help with tasks/calendar"

{lang_instruction.get(language, lang_instruction['english'])}

User said: {user_message}

Provide a helpful, informative response. Be conversational but thorough. If it's a complex question, explain well. If it's a simple chat, be friendly and brief."""
            
            try:
                response = self.model.generate_content(prompt)
                return response.text.strip()
            except Exception as e:
                print(f"Chat error: {e}")
        
        # Rule-based fallback responses by language
        fallback = {
            'english': {
                'greet': "Hello! 👋 Great to see you! How can I make your day easier?",
                'task': "I'll create that task for you right away! ✅",
                'event': "Let me add that to your calendar! 📅",
                'email': "I'll help you send that email! 📧",
                'help': "I'm here to help! I can:\n• Create tasks: 'Remind me to...'\n• Schedule events: 'Schedule meeting at...'\n• Send emails: 'Email someone about...'\n• Chat: 'How's my day looking?'",
                'default': "Got it! Let me help you with that. 🤝"
            },
            'hindi': {
                'greet': "नमस्ते! 👋 आपसे मिलकर खुशी हुई! आज मैं कैसे मदद कर सकता हूं?",
                'task': "मैं अभी वह टास्क बना देता हूं! ✅",
                'event': "मैं इसे आपके कैलेंडर में जोड़ देता हूं! 📅",
                'email': "मैं वह ईमेल भेजने में मदद करता हूं! 📧",
                'help': "मैं यहां मदद के लिए हूं!\n• टास्क: 'मुझे याद दिलाओ...'\n• इवेंट: 'मीटिंग शेड्यूल करो...'\n• ईमेल: 'किसी को ईमेल करो...'",
                'default': "समझ गया! मैं इसमें आपकी मदद करता हूं। 🤝"
            },
            'tamil': {
                'greet': "வணக்கம்! 👋 உங்களைப் பார்த்ததில் மகிழ்ச்சி! நான் எப்படி உதவ முடியும்?",
                'task': "உடனே அந்த பணியை உருவாக்குகிறேன்! ✅",
                'event': "உங்கள் நாட்காட்டியில் சேர்க்கிறேன்! 📅",
                'email': "அந்த மின்னஞ்சலை அனுப்ப உதவுகிறேன்! 📧",
                'help': "நான் உதவ இங்கே இருக்கிறேன்!\n• பணிகள்: 'எனக்கு நினைவூட்டு...'\n• நிகழ்வுகள்: 'சந்திப்பை திட்டமிடு...'\n• மின்னஞ்சல்: 'யாருக்காவது மின்னஞ்சல் அனுப்பு...'",
                'default': "புரிந்தது! இதில் உங்களுக்கு உதவுகிறேன்। 🤝"
            }
        }
        
        lang_fallback = fallback.get(language, fallback['english'])
        msg_lower = user_message.lower()
        
        if any(word in msg_lower for word in ['task', 'todo', 'remind', 'टास्क', 'याद', 'பணி']):
            return lang_fallback['task']
        elif any(word in msg_lower for word in ['meeting', 'schedule', 'calendar', 'event', 'मीटिंग', 'कैलेंडर', 'சந்திப்பு', 'நாட்காட்டி']):
            return lang_fallback['event']
        elif any(word in msg_lower for word in ['email', 'send', 'mail', 'ईमेल', 'भेज', 'மின்னஞ்சல்']):
            return lang_fallback['email']
        elif any(word in msg_lower for word in ['hi', 'hello', 'hey', 'नमस्ते', 'हाय', 'வணக்கம்']):
            return lang_fallback['greet']
        elif any(word in msg_lower for word in ['help', 'what can', 'मदद', 'உதவி']):
            return lang_fallback['help']
        else:
            return lang_fallback['default']

