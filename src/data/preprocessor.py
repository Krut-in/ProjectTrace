"""
Data preprocessing module for email and calendar data
Handles loading, cleaning, and validation of input data
"""

import pandas as pd
import json
from typing import Dict, List, Tuple, Optional
from pathlib import Path
from datetime import datetime, timedelta
import logging
from collections import defaultdict
import re

from src.models.schemas import (
    EmailEvent, CalendarEvent, Participant, EventType
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataPreprocessor:
    """
    Production-ready data preprocessing with comprehensive error handling
    """
    
    def __init__(self, email_path: str, calendar_path: str):
        self.email_path = Path(email_path)
        self.calendar_path = Path(calendar_path)
        self._validate_paths()
        
        self.emails: List[EmailEvent] = []
        self.calendar_events: List[CalendarEvent] = []
        self.participants_map: Dict[str, Participant] = {}
        
    def _validate_paths(self) -> None:
        """Validate input file paths"""
        if not self.email_path.exists():
            raise FileNotFoundError(f"Email file not found: {self.email_path}")
        if not self.calendar_path.exists():
            raise FileNotFoundError(f"Calendar file not found: {self.calendar_path}")
            
    def load_data(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Load and validate JSON data with comprehensive error handling
        """
        try:
            logger.info("Loading email data...")
            with open(self.email_path, 'r', encoding='utf-8') as f:
                email_data = json.load(f)
            
            logger.info("Loading calendar data...")
            with open(self.calendar_path, 'r', encoding='utf-8') as f:
                calendar_data = json.load(f)
            
            # Validate and parse emails
            self.emails = self._parse_emails(email_data)
            logger.info(f"Loaded {len(self.emails)} email threads")
            
            # Validate and parse calendar events
            self.calendar_events = self._parse_calendar(calendar_data)
            logger.info(f"Loaded {len(self.calendar_events)} calendar events")
            
            # Build participant map
            self._build_participant_map()
            logger.info(f"Identified {len(self.participants_map)} unique participants")
            
            # Convert to DataFrames
            email_df = pd.DataFrame([e.dict() for e in self.emails])
            calendar_df = pd.DataFrame([c.dict() for c in self.calendar_events])
            
            return email_df, calendar_df
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}")
            raise
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            raise
    
    def _parse_emails(self, data: List[Dict]) -> List[EmailEvent]:
        """Parse and validate email data"""
        parsed_emails = []
        
        for idx, item in enumerate(data):
            try:
                # Skip empty items
                if not item or not item.get('subject'):
                    continue
                
                # Clean participant emails
                cleaned_participants = self._clean_email_list(
                    item.get('participants', [])
                )
                
                # Skip if no valid participants
                if not cleaned_participants:
                    continue
                
                # Parse individual emails in the thread
                individual_emails = []
                email_bodies = []
                
                for email_obj in item.get('emails', []):
                    try:
                        from src.models.schemas import IndividualEmail
                        ind_email = IndividualEmail(
                            **{
                                'from': email_obj.get('from', ''),
                                'to': email_obj.get('to', ''),
                                'cc': email_obj.get('cc', ''),
                                'subject': email_obj.get('subject', ''),
                                'date': email_obj.get('date', ''),
                                'body_text': email_obj.get('body_text', '')
                            }
                        )
                        individual_emails.append(ind_email)
                        email_bodies.append(email_obj.get('body_text', ''))
                    except Exception as e:
                        logger.warning(f"Skipping individual email in thread {idx}: {e}")
                        continue
                
                # Combine all email bodies for analysis
                combined_body = '\n\n---EMAIL SEPARATOR---\n\n'.join(email_bodies)
                
                email = EmailEvent(
                    subject=item.get('subject', 'No Subject'),
                    email_count=item.get('email_count', 0),
                    participants=cleaned_participants,
                    first_date=item.get('first_date'),
                    last_date=item.get('last_date'),
                    thread_id=f"email_thread_{idx}",
                    emails=individual_emails,
                    combined_body_text=combined_body if combined_body else None
                )
                parsed_emails.append(email)
                
            except Exception as e:
                logger.warning(f"Skipping email thread {idx}: {e}")
                continue
        
        return parsed_emails
    
    def _parse_calendar(self, data: Dict) -> List[CalendarEvent]:
        """Parse and validate calendar data"""
        parsed_events = []
        
        events = data.get('events', [])
        for event in events:
            try:
                # Skip empty events
                if not event or not event.get('uid'):
                    continue
                
                calendar_event = CalendarEvent(
                    uid=event['uid'],
                    summary=event.get('summary', 'No Title'),
                    start=event['start'],
                    end=event['end'],
                    organizer=event.get('organizer', ''),
                    attendees=event.get('attendees', []),
                    location=event.get('location', ''),
                    description=event.get('description', ''),
                    has_startupco_in_title=event.get('has_startupco_in_title', False),
                    has_startupco_participant=event.get('has_startupco_participant', False)
                )
                parsed_events.append(calendar_event)
                
            except Exception as e:
                logger.warning(f"Skipping calendar event {event.get('uid', 'unknown')}: {e}")
                continue
        
        return parsed_events
    
    def _clean_email_list(self, emails: List[str]) -> List[str]:
        """Clean and standardize email addresses"""
        cleaned = []
        for email in emails:
            # Extract email from various formats
            match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', str(email))
            if match:
                cleaned.append(match.group(0).lower().strip())
        return list(set(cleaned))  # Remove duplicates
    
    def _build_participant_map(self) -> None:
        """Build comprehensive participant mapping"""
        all_emails = set()
        
        # Collect from email threads
        for email in self.emails:
            all_emails.update(email.participants)
        
        # Collect from calendar
        for event in self.calendar_events:
            if event.organizer:
                all_emails.add(event.organizer)
            all_emails.update(event.attendees)
        
        # Create participant objects
        for email in all_emails:
            if email and '@' in email:
                try:
                    participant = Participant(email=email)
                    self.participants_map[email] = participant
                except Exception as e:
                    logger.warning(f"Could not create participant for {email}: {e}")
    
    def create_unified_timeline(self) -> pd.DataFrame:
        """
        Create a unified timeline merging emails and calendar events
        """
        timeline_events = []
        
        # Add email events
        for email in self.emails:
            timeline_events.append({
                'date': email.first_date,
                'type': EventType.EMAIL.value,
                'event_id': email.thread_id,
                'subject': email.subject,
                'participants': email.participants,
                'participant_count': len(email.participants),
                'email_count': email.email_count,
                'duration_days': (email.last_date - email.first_date).days,
                'body_text': email.combined_body_text  # Include email body text
            })
        
        # Add calendar events
        for event in self.calendar_events:
            timeline_events.append({
                'date': event.start,
                'type': EventType.MEETING.value,
                'event_id': event.uid,
                'subject': event.summary,
                'participants': event.attendees,
                'participant_count': len(event.attendees),
                'duration_hours': (event.end - event.start).total_seconds() / 3600,
                'has_startupco': event.has_startupco_in_title or event.has_startupco_participant
            })
        
        timeline_df = pd.DataFrame(timeline_events)
        timeline_df = timeline_df.sort_values('date').reset_index(drop=True)
        
        logger.info(f"Created unified timeline with {len(timeline_df)} events")
        return timeline_df
    
    def get_participant_statistics(self) -> pd.DataFrame:
        """Generate participant engagement statistics"""
        stats = []
        
        for email, participant in self.participants_map.items():
            email_count = sum(
                1 for e in self.emails if email in e.participants
            )
            meeting_count = sum(
                1 for m in self.calendar_events 
                if email in m.attendees or email == m.organizer
            )
            
            stats.append({
                'email': email,
                'organization': participant.organization,
                'email_threads': email_count,
                'meetings': meeting_count,
                'total_events': email_count + meeting_count
            })
        
        return pd.DataFrame(stats).sort_values('total_events', ascending=False)
