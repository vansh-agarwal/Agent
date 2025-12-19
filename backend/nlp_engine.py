"""
NLP Engine for AI Personal Task Automation Agent
Extracts intent and entities from natural language user input
"""

import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from models import UserIntent, IntentType, Priority
import json


class NLPEngine:
    """Natural Language Processing for intent extraction"""
    
    def __init__(self):
        """Initialize NLP engine"""
        # Intent patterns
        self.intent_patterns = {
            IntentType.CREATE_TASK: [
                r'create\s+(?:a\s+)?task',
                r'add\s+(?:a\s+)?task',
                r'new\s+task',
                r'remind\s+me\s+to',
                r'i\s+need\s+to',
                r'todo',
                r'task:'
            ],
            IntentType.CREATE_EVENT: [
                r'schedule\s+(?:a\s+)?meeting',
                r'schedule\s+(?:a\s+)?flight',
                r'schedule\s+(?:a\s+)?call',
                r'schedule\s+(?:a\s+)?appointment',
                r'schedule\s+(?:a\s+)?\w+',  # schedule + any noun
                r'create\s+(?:an?\s+)?event',
                r'add\s+(?:to\s+)?(?:my\s+)?calendar',
                r'put\s+(?:in\s+)?(?:my\s+)?calendar',
                r'book\s+(?:a\s+)?meeting',
                r'book\s+(?:a\s+)?flight',
                r'book\s+(?:a\s+)?\w+',  # book + any noun
                r'set\s+up\s+(?:a\s+)?meeting',
                r'meeting\s+(?:at|on|with)',
                r'(?:at|for)\s+\d{1,2}(?::\d{2})?\s*(?:am|pm)',  # at 6:30 pm
                r'tomorrow\s+at\s+\d',  # tomorrow at X
                r'today\s+at\s+\d',  # today at X
                r'calendar',  # explicit calendar mention
                r'flight\s+(?:at|on|for|tomorrow)',
                r'appointment\s+(?:at|on|for)'
            ],
            IntentType.SEND_EMAIL: [
                r'send\s+(?:an?\s+)?email',
                r'email\s+(?:to|about)',
                r'compose\s+email',
                r'draft\s+email'
            ],
            IntentType.QUERY_TASKS: [
                r'show\s+(?:me\s+)?(?:my\s+)?tasks',
                r'list\s+(?:all\s+)?tasks',
                r'what\s+(?:are\s+)?my\s+tasks',
                r'tasks\s+for',
                r'what\s+do\s+i\s+have\s+to\s+do'
            ],
            IntentType.QUERY_EVENTS: [
                r'show\s+(?:me\s+)?(?:my\s+)?(?:calendar|events|schedule)',
                r'what\'?s\s+on\s+my\s+calendar',
                r'my\s+schedule',
                r'upcoming\s+events'
            ],
            IntentType.SET_REMINDER: [
                r'remind\s+me',
                r'set\s+(?:a\s+)?reminder',
                r'create\s+(?:a\s+)?reminder'
            ]
        }
        
        # Priority keywords
        self.priority_keywords = {
            Priority.URGENT: ['urgent', 'asap', 'critical', 'emergency', 'important'],
            Priority.HIGH: ['high priority', 'important', 'high'],
            Priority.MEDIUM: ['medium', 'normal'],
            Priority.LOW: ['low priority', 'low', 'whenever']
        }
        
        # Time expressions
        self.time_patterns = {
            'absolute_time': r'(?:at\s+)?(\d{1,2})(?::(\d{2}))?\s*(am|pm)?',
            'relative_day': r'(today|tomorrow|yesterday)',
            'day_of_week': r'(monday|tuesday|wednesday|thursday|friday|saturday|sunday)',
            'relative_time': r'in\s+(\d+)\s+(minute|hour|day|week|month)s?',
            'date': r'(\d{1,2})[/\-](\d{1,2})(?:[/\-](\d{2,4}))?'
        }
    
    def extract_intent(self, text: str) -> UserIntent:
        """Extract user intent from natural language text"""
        text_lower = text.lower().strip()
        
        # Detect intent type
        intent_type = self._detect_intent_type(text_lower)
        
        # Extract entities based on intent
        entities = self._extract_entities(text, text_lower, intent_type)
        
        # Calculate confidence (simple heuristic)
        confidence = self._calculate_confidence(text_lower, intent_type, entities)
        
        return UserIntent(
            intent_type=intent_type,
            entities=entities,
            confidence=confidence,
            original_text=text
        )
    
    def _detect_intent_type(self, text: str) -> IntentType:
        """Detect the type of intent from text"""
        scores = {}
        
        for intent_type, patterns in self.intent_patterns.items():
            score = 0
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    score += 1
            scores[intent_type] = score
        
        # Get intent with highest score
        if max(scores.values()) > 0:
            return max(scores, key=scores.get)
        
        # Default to create task if uncertain
        return IntentType.CREATE_TASK
    
    def _extract_entities(self, text: str, text_lower: str, intent_type: IntentType) -> Dict:
        """Extract entities from text based on intent"""
        entities = {}
        
        # Extract time/date information
        time_info = self._extract_time(text_lower)
        if time_info:
            entities.update(time_info)
        
        # Extract priority
        priority = self._extract_priority(text_lower)
        if priority:
            entities['priority'] = priority.name
        
        # Extract email addresses
        emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
        if emails:
            entities['emails'] = emails
        
        # Extract people/attendees (names after 'with' or '@')
        people = re.findall(r'(?:with|@)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)', text)
        if people:
            entities['attendees'] = people
        
        # Extract duration
        duration_match = re.search(r'(?:for\s+)?(\d+)\s+(minute|hour)s?', text_lower)
        if duration_match:
            amount = int(duration_match.group(1))
            unit = duration_match.group(2)
            entities['duration'] = amount * 60 if unit == 'hour' else amount
        
        # Extract title/subject (heuristic: main content after intent keywords)
        title = self._extract_title(text, text_lower, intent_type)
        if title:
            entities['title'] = title
        
        # Extract location (after 'at' or 'in' for events)
        if intent_type == IntentType.CREATE_EVENT:
            location_match = re.search(r'(?:at|in)\s+([A-Z][A-Za-z\s]+?)(?:\s+(?:on|at|with|for|$))', text)
            if location_match:
                entities['location'] = location_match.group(1).strip()
        
        return entities
    
    def _extract_time(self, text: str) -> Optional[Dict]:
        """Extract time and date information"""
        result = {}
        
        # Try relative day (today, tomorrow)
        relative_match = re.search(self.time_patterns['relative_day'], text)
        if relative_match:
            day = relative_match.group(1)
            if day == 'today':
                result['date'] = datetime.now()
            elif day == 'tomorrow':
                result['date'] = datetime.now() + timedelta(days=1)
            elif day == 'yesterday':
                result['date'] = datetime.now() - timedelta(days=1)
        
        # Try day of week
        dow_match = re.search(self.time_patterns['day_of_week'], text)
        if dow_match:
            days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
            target_day = days.index(dow_match.group(1))
            current_day = datetime.now().weekday()
            days_ahead = (target_day - current_day) % 7
            if days_ahead == 0:
                days_ahead = 7
            result['date'] = datetime.now() + timedelta(days=days_ahead)
        
        # Try relative time
        rel_time_match = re.search(self.time_patterns['relative_time'], text)
        if rel_time_match:
            amount = int(rel_time_match.group(1))
            unit = rel_time_match.group(2)
            
            if unit == 'minute':
                result['date'] = datetime.now() + timedelta(minutes=amount)
            elif unit == 'hour':
                result['date'] = datetime.now() + timedelta(hours=amount)
            elif unit == 'day':
                result['date'] = datetime.now() + timedelta(days=amount)
            elif unit == 'week':
                result['date'] = datetime.now() + timedelta(weeks=amount)
            elif unit == 'month':
                result['date'] = datetime.now() + timedelta(days=amount * 30)
        
        # Try absolute time
        time_match = re.search(self.time_patterns['absolute_time'], text)
        if time_match:
            hour = int(time_match.group(1))
            minute = int(time_match.group(2)) if time_match.group(2) else 0
            period = time_match.group(3)
            
            if period == 'pm' and hour < 12:
                hour += 12
            elif period == 'am' and hour == 12:
                hour = 0
            
            base_date = result.get('date', datetime.now())
            result['date'] = base_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        # Convert datetime to ISO format for storage
        if 'date' in result:
            result['datetime'] = result['date'].isoformat()
            result['date'] = result['date'].date().isoformat()
        
        return result if result else None
    
    def _extract_priority(self, text: str) -> Optional[Priority]:
        """Extract priority from text"""
        for priority, keywords in self.priority_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    return priority
        return None
    
    def _extract_title(self, text: str, text_lower: str, intent_type: IntentType) -> str:
        """Extract the main title/subject from text"""
        
        # First, try to find explicit title patterns like "called X", "titled X", "named X", "about X"
        explicit_patterns = [
            r'(?:called|titled|named)\s+["\']?([^"\']+?)["\']?\s*(?:at|on|for|with|tomorrow|today|$)',
            r'(?:called|titled|named)\s+["\']?(.+?)["\']?$',
            r'about\s+["\']?([^"\']+?)["\']?\s*(?:at|on|for|with|tomorrow|today|$)',
            r'meeting\s+(?:with\s+)?["\']?([A-Z][a-zA-Z\s]+)["\']?\s*(?:at|on|for|tomorrow|today|$)',
        ]
        
        for pattern in explicit_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                title = match.group(1).strip()
                if title and len(title) > 2:
                    return title
        
        # Remove common intent phrases
        remove_patterns = [
            r'create\s+(?:a\s+)?task\s+(?:to\s+)?',
            r'add\s+(?:a\s+)?task\s+(?:to\s+)?',
            r'add\s+(?:a\s+)?task\s+(?:called|titled|named)\s+',
            r'schedule\s+(?:a\s+)?(?:meeting|event)\s+(?:about|for|to\s+discuss|called|titled|named)?\s*',
            r'create\s+(?:an?\s+)?event\s+(?:called|titled|named)?\s*',
            r'remind\s+me\s+to\s+',
            r'i\s+need\s+to\s+',
            r'todo:\s*',
            r'task:\s*'
        ]
        
        title = text
        for pattern in remove_patterns:
            title = re.sub(pattern, '', title, flags=re.IGNORECASE)
        
        # Remove time expressions
        for pattern in self.time_patterns.values():
            title = re.sub(pattern, '', title, flags=re.IGNORECASE)
        
        # Remove priority keywords
        for keywords in self.priority_keywords.values():
            for keyword in keywords:
                title = re.sub(r'\b' + keyword + r'\b', '', title, flags=re.IGNORECASE)
        
        # Clean up
        title = re.sub(r'\s+', ' ', title).strip()
        title = title.strip('.,;:!?')
        
        return title if title else "Untitled"
    
    def _calculate_confidence(self, text: str, intent_type: IntentType, entities: Dict) -> float:
        """Calculate confidence score for the extracted intent"""
        confidence = 0.5  # Base confidence
        
        # Increase confidence if we matched intent patterns
        if intent_type in self.intent_patterns:
            for pattern in self.intent_patterns[intent_type]:
                if re.search(pattern, text, re.IGNORECASE):
                    confidence += 0.1
                    break
        
        # Increase confidence based on extracted entities
        if 'title' in entities and len(entities['title']) > 3:
            confidence += 0.1
        if 'datetime' in entities or 'date' in entities:
            confidence += 0.15
        if 'priority' in entities:
            confidence += 0.1
        
        return min(confidence, 1.0)  # Cap at 1.0
