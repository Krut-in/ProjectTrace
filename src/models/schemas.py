"""
Data models and schemas using Pydantic for validation
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from enum import Enum


class EventType(str, Enum):
    EMAIL = "email"
    MEETING = "meeting"
    COLLABORATION_BURST = "collaboration_burst"
    MILESTONE = "milestone"
    PHASE_TRANSITION = "phase_transition"


class Participant(BaseModel):
    email: str
    name: Optional[str] = None
    organization: Optional[str] = None
    
    @validator('email')
    def validate_email(cls, v):
        if '@' not in v:
            raise ValueError('Invalid email format')
        return v.lower().strip()
    
    @validator('organization', always=True)
    def extract_org(cls, v, values):
        if v is None and 'email' in values:
            domain = values['email'].split('@')[1]
            return domain.split('.')[0].title()
        return v


class EmailEvent(BaseModel):
    subject: str
    email_count: int
    participants: List[str]
    first_date: datetime
    last_date: datetime
    thread_id: Optional[str] = None
    
    @validator('first_date', 'last_date', pre=True)
    def parse_date(cls, v):
        if isinstance(v, str):
            from dateutil import parser
            try:
                dt = parser.parse(v)
                # Remove timezone info to avoid comparison issues
                if dt.tzinfo is not None:
                    dt = dt.replace(tzinfo=None)
                return dt
            except Exception:
                # Skip invalid dates
                return None
        return v


class CalendarEvent(BaseModel):
    uid: str
    summary: str
    start: datetime
    end: datetime
    organizer: str
    attendees: List[str]
    location: Optional[str] = ""
    description: Optional[str] = ""
    has_startupco_in_title: bool = False
    has_startupco_participant: bool = False
    
    @validator('start', 'end', pre=True)
    def parse_datetime(cls, v):
        if isinstance(v, str):
            from dateutil import parser
            dt = parser.parse(v)
            # Remove timezone info to avoid comparison issues
            if dt.tzinfo is not None:
                dt = dt.replace(tzinfo=None)
            return dt
        return v
    
    @validator('organizer', pre=True)
    def clean_organizer(cls, v):
        if isinstance(v, str):
            return v.replace('mailto:', '').lower().strip()
        return v
    
    @validator('attendees', pre=True)
    def clean_attendees(cls, v):
        if isinstance(v, list):
            return [email.replace('mailto:', '').lower().strip() for email in v]
        return v


class CollaborationBurst(BaseModel):
    start_date: datetime
    end_date: datetime
    participants: List[str]
    event_count: int
    event_types: List[str]
    confidence: float = Field(ge=0.0, le=1.0)
    trigger_events: List[str] = Field(default_factory=list)


class Milestone(BaseModel):
    date: datetime
    event_id: str
    event_type: str
    participants: List[str]
    follow_up_count: int
    pattern_type: str
    confidence: float = Field(ge=0.0, le=1.0)
    description: str


class PhaseTransition(BaseModel):
    date: datetime
    old_topics: List[str]
    new_topics: List[str]
    similarity_score: float
    confidence: float = Field(ge=0.0, le=1.0)
    events_in_window: int
