"""
Milestone detection module
Identifies key project events based on communication patterns
"""

import pandas as pd
from typing import List, Dict, Set
from datetime import datetime, timedelta
from collections import defaultdict
import logging
import re

from src.models.schemas import CalendarEvent

logger = logging.getLogger(__name__)


class MilestoneDetector:
    """
    Detect project milestones from communication patterns
    
    Detects three types of milestones:
    1. Decision Points: Large meetings followed by email activity
    2. Deliverable Events: Presentations, reviews, demos
    3. Planning Phases: Workshops and strategy sessions
    """
    
    def __init__(
        self,
        large_meeting_threshold: int = 7,
        follow_up_window_hours: int = 48,
        min_follow_ups: int = 3,
        deliverable_keywords: List[str] = None,
        planning_keywords: List[str] = None
    ):
        """
        Initialize milestone detector
        
        Args:
            large_meeting_threshold: Min attendees to consider "large meeting"
            follow_up_window_hours: Time window to check for follow-ups
            min_follow_ups: Min follow-up emails for decision point
            deliverable_keywords: Keywords indicating deliverable events
            planning_keywords: Keywords indicating planning events
        """
        self.large_meeting_threshold = large_meeting_threshold
        self.follow_up_window_hours = follow_up_window_hours
        self.min_follow_ups = min_follow_ups
        
        self.deliverable_keywords = deliverable_keywords or [
            'presentation', 'demo', 'review', 'showcase', 'deliverable',
            'launch', 'release', 'delivery', 'final', 'approval'
        ]
        
        self.planning_keywords = planning_keywords or [
            'workshop', 'briefing', 'kickoff', 'strategy', 'planning',
            'brainstorm', 'discovery', 'scoping', 'roadmap', 'alignment'
        ]
    
    def detect_milestones(
        self,
        calendar_events: List[CalendarEvent],
        timeline_df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Main detection method
        
        Returns:
            DataFrame with columns: date, type, title, participants, 
            confidence, description, follow_up_count
        """
        logger.info("Detecting project milestones...")
        
        milestones = []
        
        # Pattern 1: Decision points
        decision_points = self._detect_decision_points(calendar_events, timeline_df)
        milestones.extend(decision_points)
        logger.info(f"Detected {len(decision_points)} decision points")
        
        # Pattern 2: Deliverable events
        deliverables = self._detect_deliverables(calendar_events, timeline_df)
        milestones.extend(deliverables)
        logger.info(f"Detected {len(deliverables)} deliverable events")
        
        # Pattern 3: Planning phases
        planning_phases = self._detect_planning_phases(calendar_events, timeline_df)
        milestones.extend(planning_phases)
        logger.info(f"Detected {len(planning_phases)} planning phases")
        
        if not milestones:
            logger.warning("No milestones detected")
            return pd.DataFrame()
        
        # Convert to DataFrame and sort
        milestone_df = pd.DataFrame(milestones)
        milestone_df = milestone_df.sort_values('date').reset_index(drop=True)
        milestone_df['milestone_id'] = range(len(milestone_df))
        
        logger.info(f"Total milestones detected: {len(milestone_df)}")
        return milestone_df
    
    def _detect_decision_points(
        self,
        calendar_events: List[CalendarEvent],
        timeline_df: pd.DataFrame
    ) -> List[Dict]:
        """
        Pattern: Large meeting → activity spike → calm period
        Indicates major decision was made
        """
        decision_points = []
        
        # Find large meetings
        large_meetings = [
            e for e in calendar_events
            if len(e.attendees) >= self.large_meeting_threshold
        ]
        
        for meeting in large_meetings:
            # Count follow-up emails within window
            follow_up_start = meeting.start
            follow_up_end = meeting.start + timedelta(hours=self.follow_up_window_hours)
            
            follow_ups = timeline_df[
                (timeline_df['date'] > follow_up_start) &
                (timeline_df['date'] <= follow_up_end) &
                (timeline_df['type'] == 'email')
            ]
            
            # Check for calm period after follow-ups
            calm_start = follow_up_end
            calm_end = calm_start + timedelta(hours=72)
            calm_events = timeline_df[
                (timeline_df['date'] > calm_start) &
                (timeline_df['date'] <= calm_end)
            ]
            
            # Decision point criteria: lots of follow-ups + calm after
            if len(follow_ups) >= self.min_follow_ups and len(calm_events) <= 3:
                # Calculate confidence
                follow_up_score = min(1.0, len(follow_ups) / 10)
                size_score = min(1.0, len(meeting.attendees) / 15)
                calm_score = 1.0 - min(1.0, len(calm_events) / 3)
                
                confidence = (0.4 * follow_up_score + 
                            0.4 * size_score + 
                            0.2 * calm_score)
                
                decision_points.append({
                    'date': meeting.start,
                    'type': 'decision_point',
                    'title': meeting.summary,
                    'participants': meeting.attendees,
                    'participant_count': len(meeting.attendees),
                    'confidence': round(confidence, 3),
                    'description': f"Major decision meeting with {len(meeting.attendees)} participants, "
                                 f"{len(follow_ups)} follow-up communications",
                    'follow_up_count': len(follow_ups),
                    'event_id': meeting.uid
                })
        
        return decision_points
    
    def _detect_deliverables(
        self,
        calendar_events: List[CalendarEvent],
        timeline_df: pd.DataFrame
    ) -> List[Dict]:
        """
        Pattern: Meeting with deliverable keywords + cross-org attendance
        Indicates formal deliverable or milestone
        """
        deliverables = []
        
        for meeting in calendar_events:
            # Check for deliverable keywords
            summary_lower = meeting.summary.lower()
            keyword_matches = [
                kw for kw in self.deliverable_keywords 
                if kw in summary_lower
            ]
            
            if not keyword_matches:
                continue
            
            # Check for cross-organization participation
            attendee_orgs = set()
            for attendee in meeting.attendees:
                if '@' in attendee:
                    domain = attendee.split('@')[1]
                    attendee_orgs.add(domain)
            
            cross_org = len(attendee_orgs) > 1
            
            # Calculate confidence
            keyword_score = min(1.0, len(keyword_matches) / 2)
            size_score = min(1.0, len(meeting.attendees) / 10)
            cross_org_score = 1.0 if cross_org else 0.5
            
            confidence = (0.5 * keyword_score + 
                        0.3 * size_score + 
                        0.2 * cross_org_score)
            
            # Only include high-confidence deliverables
            if confidence >= 0.5:
                deliverables.append({
                    'date': meeting.start,
                    'type': 'deliverable',
                    'title': meeting.summary,
                    'participants': meeting.attendees,
                    'participant_count': len(meeting.attendees),
                    'confidence': round(confidence, 3),
                    'description': f"Deliverable event: {', '.join(keyword_matches)}",
                    'follow_up_count': 0,
                    'event_id': meeting.uid,
                    'keywords': keyword_matches
                })
        
        return deliverables
    
    def _detect_planning_phases(
        self,
        calendar_events: List[CalendarEvent],
        timeline_df: pd.DataFrame
    ) -> List[Dict]:
        """
        Pattern: Workshop/briefing + subsequent activity burst
        Indicates start of new project phase
        """
        planning_phases = []
        
        for meeting in calendar_events:
            # Check for planning keywords
            summary_lower = meeting.summary.lower()
            keyword_matches = [
                kw for kw in self.planning_keywords 
                if kw in summary_lower
            ]
            
            if not keyword_matches:
                continue
            
            # Check for activity burst after meeting
            burst_window_start = meeting.start
            burst_window_end = meeting.start + timedelta(days=7)
            
            subsequent_events = timeline_df[
                (timeline_df['date'] > burst_window_start) &
                (timeline_df['date'] <= burst_window_end)
            ]
            
            # Calculate confidence
            keyword_score = min(1.0, len(keyword_matches) / 2)
            size_score = min(1.0, len(meeting.attendees) / 12)
            activity_score = min(1.0, len(subsequent_events) / 10)
            
            confidence = (0.4 * keyword_score + 
                        0.3 * size_score + 
                        0.3 * activity_score)
            
            # Only include if there's subsequent activity
            if len(subsequent_events) >= 2:
                planning_phases.append({
                    'date': meeting.start,
                    'type': 'planning_phase',
                    'title': meeting.summary,
                    'participants': meeting.attendees,
                    'participant_count': len(meeting.attendees),
                    'confidence': round(confidence, 3),
                    'description': f"Planning phase: {', '.join(keyword_matches)}, "
                                 f"{len(subsequent_events)} subsequent events",
                    'follow_up_count': len(subsequent_events),
                    'event_id': meeting.uid,
                    'keywords': keyword_matches
                })
        
        return planning_phases
    
    def get_milestone_summary(self, milestone_df: pd.DataFrame) -> str:
        """Generate human-readable summary of milestones"""
        if milestone_df.empty:
            return "No milestones detected."
        
        summary = []
        summary.append(f"\n{'='*70}")
        summary.append("PROJECT MILESTONES SUMMARY")
        summary.append(f"{'='*70}\n")
        
        # Group by type
        for milestone_type in ['decision_point', 'deliverable', 'planning_phase']:
            subset = milestone_df[milestone_df['type'] == milestone_type]
            if subset.empty:
                continue
            
            type_name = milestone_type.replace('_', ' ').title()
            summary.append(f"\n{type_name}s ({len(subset)}):")
            summary.append("-" * 70)
            
            for _, row in subset.iterrows():
                date_str = row['date'].strftime('%Y-%m-%d')
                summary.append(f"\n  [{date_str}] {row['title']}")
                summary.append(f"    Confidence: {row['confidence']:.2%}")
                summary.append(f"    Participants: {row['participant_count']}")
                summary.append(f"    {row['description']}")
        
        summary.append(f"\n{'='*70}\n")
        
        return '\n'.join(summary)
