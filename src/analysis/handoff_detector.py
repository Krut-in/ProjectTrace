"""
Handoff detection module
Identifies when work is transferred between team members
"""

import pandas as pd
from typing import List, Dict, Set
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class HandoffDetector:
    """
    Detect handoff events where work is transferred between participants
    
    Patterns:
    1. New participants join after time gap (> 14 days)
    2. Large change in participant set (2+ new people)
    3. Complete participant turnover
    """
    
    def __init__(
        self,
        time_gap_days: int = 14,
        min_new_participants: int = 2,
        turnover_threshold: float = 0.7
    ):
        """
        Initialize handoff detector
        
        Args:
            time_gap_days: Minimum days between events to consider gap
            min_new_participants: Minimum new people to flag handoff
            turnover_threshold: % of new participants to consider turnover
        """
        self.time_gap_days = time_gap_days
        self.min_new_participants = min_new_participants
        self.turnover_threshold = turnover_threshold
    
    def detect_handoffs(self, timeline_df: pd.DataFrame) -> pd.DataFrame:
        """
        Detect handoff events in timeline
        
        Returns:
            DataFrame with columns: date, handoff_type, new_participants,
            departed_participants, event_subject, confidence
        """
        logger.info("Detecting handoff events...")
        
        if timeline_df.empty or len(timeline_df) < 2:
            logger.warning("Insufficient data for handoff detection")
            return pd.DataFrame()
        
        # Sort by date
        df = timeline_df.sort_values('date').copy()
        
        handoffs = []
        
        # Track participant set over time
        for i in range(1, len(df)):
            prev_row = df.iloc[i-1]
            curr_row = df.iloc[i]
            
            # Get participant sets
            prev_participants = set(prev_row.get('participants', []))
            curr_participants = set(curr_row.get('participants', []))
            
            # Calculate changes
            new_people = curr_participants - prev_participants
            departed_people = prev_participants - curr_participants
            
            # Check for handoff patterns
            handoff = self._analyze_participant_change(
                prev_row,
                curr_row,
                prev_participants,
                curr_participants,
                new_people,
                departed_people
            )
            
            if handoff:
                handoffs.append(handoff)
        
        if not handoffs:
            logger.info("No handoffs detected")
            return pd.DataFrame()
        
        # Convert to DataFrame
        handoff_df = pd.DataFrame(handoffs)
        handoff_df = handoff_df.sort_values('date').reset_index(drop=True)
        handoff_df['handoff_id'] = range(len(handoff_df))
        
        logger.info(f"Detected {len(handoff_df)} handoff events")
        
        # Log handoff type distribution
        type_counts = handoff_df['handoff_type'].value_counts()
        logger.info(f"Handoff types: {type_counts.to_dict()}")
        
        return handoff_df
    
    def _analyze_participant_change(
        self,
        prev_row: pd.Series,
        curr_row: pd.Series,
        prev_participants: Set[str],
        curr_participants: Set[str],
        new_people: Set[str],
        departed_people: Set[str]
    ) -> Dict:
        """
        Analyze participant change for handoff patterns
        """
        # Skip if no participant change
        if not new_people and not departed_people:
            return None
        
        # Calculate time gap
        time_gap = (curr_row['date'] - prev_row['date']).days
        
        # Calculate turnover rate
        total_prev = len(prev_participants)
        turnover_rate = len(departed_people) / total_prev if total_prev > 0 else 0
        
        handoff = None
        
        # Pattern 1: New people after long gap
        if time_gap > self.time_gap_days and len(new_people) >= 1:
            handoff = {
                'date': curr_row['date'],
                'handoff_type': 'gap_resumption',
                'new_participants': list(new_people),
                'departed_participants': list(departed_people),
                'new_count': len(new_people),
                'departed_count': len(departed_people),
                'time_gap_days': time_gap,
                'event_subject': curr_row.get('subject', 'N/A'),
                'event_type': curr_row.get('type', 'unknown'),
                'confidence': min(1.0, (len(new_people) / 3) * (time_gap / 30)),
                'description': f"{len(new_people)} new participant(s) after {time_gap}-day gap"
            }
        
        # Pattern 2: Significant new participants (without long gap)
        elif len(new_people) >= self.min_new_participants:
            handoff = {
                'date': curr_row['date'],
                'handoff_type': 'team_expansion',
                'new_participants': list(new_people),
                'departed_participants': list(departed_people),
                'new_count': len(new_people),
                'departed_count': len(departed_people),
                'time_gap_days': time_gap,
                'event_subject': curr_row.get('subject', 'N/A'),
                'event_type': curr_row.get('type', 'unknown'),
                'confidence': min(1.0, len(new_people) / 5),
                'description': f"Team expanded by {len(new_people)} people"
            }
        
        # Pattern 3: High turnover (many people left, new people joined)
        elif turnover_rate >= self.turnover_threshold and len(new_people) >= 1:
            handoff = {
                'date': curr_row['date'],
                'handoff_type': 'team_turnover',
                'new_participants': list(new_people),
                'departed_participants': list(departed_people),
                'new_count': len(new_people),
                'departed_count': len(departed_people),
                'time_gap_days': time_gap,
                'event_subject': curr_row.get('subject', 'N/A'),
                'event_type': curr_row.get('type', 'unknown'),
                'confidence': turnover_rate,
                'description': f"Team turnover: {len(departed_people)} left, {len(new_people)} joined"
            }
        
        # Pattern 4: Key person departure (someone with many connections leaves)
        elif len(departed_people) >= 1 and not new_people:
            # This is just a departure, not a handoff, but worth noting
            handoff = {
                'date': curr_row['date'],
                'handoff_type': 'departure',
                'new_participants': [],
                'departed_participants': list(departed_people),
                'new_count': 0,
                'departed_count': len(departed_people),
                'time_gap_days': time_gap,
                'event_subject': curr_row.get('subject', 'N/A'),
                'event_type': curr_row.get('type', 'unknown'),
                'confidence': min(1.0, len(departed_people) / 3),
                'description': f"{len(departed_people)} participant(s) departed"
            }
        
        return handoff
    
    def detect_role_transitions(
        self,
        timeline_df: pd.DataFrame,
        influence_df: pd.DataFrame
    ) -> List[Dict]:
        """
        Detect when high-influence people hand off to others
        Requires influence scores from InfluenceMapper
        """
        if timeline_df.empty or influence_df.empty:
            return []
        
        role_transitions = []
        
        # Get high-influence people
        leaders = influence_df[
            influence_df['role'].str.contains('Leader')
        ]['participant'].tolist()
        
        df = timeline_df.sort_values('date').copy()
        
        for i in range(1, len(df)):
            prev_participants = set(df.iloc[i-1].get('participants', []))
            curr_participants = set(df.iloc[i].get('participants', []))
            
            # Check if a leader left and new people joined
            leaders_left = prev_participants.intersection(leaders) - curr_participants
            new_people = curr_participants - prev_participants
            
            if leaders_left and new_people:
                role_transitions.append({
                    'date': df.iloc[i]['date'],
                    'leader_departed': list(leaders_left),
                    'new_members': list(new_people),
                    'event': df.iloc[i].get('subject', 'N/A'),
                    'confidence': 0.8
                })
        
        logger.info(f"Detected {len(role_transitions)} role transitions")
        return role_transitions
    
    def analyze_participation_patterns(
        self,
        timeline_df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Analyze when each participant was active
        Useful for understanding project phases and involvement
        """
        if timeline_df.empty:
            return pd.DataFrame()
        
        participation = {}
        
        for _, row in timeline_df.iterrows():
            date = row['date']
            participants = row.get('participants', [])
            
            for person in participants:
                if person not in participation:
                    participation[person] = {
                        'first_appearance': date,
                        'last_appearance': date,
                        'total_events': 0,
                        'active_dates': []
                    }
                
                participation[person]['last_appearance'] = date
                participation[person]['total_events'] += 1
                participation[person]['active_dates'].append(date)
        
        # Calculate tenure and activity span
        results = []
        for person, stats in participation.items():
            tenure_days = (stats['last_appearance'] - stats['first_appearance']).days
            
            results.append({
                'participant': person,
                'first_seen': stats['first_appearance'],
                'last_seen': stats['last_appearance'],
                'tenure_days': tenure_days,
                'total_events': stats['total_events'],
                'activity_frequency': stats['total_events'] / max(tenure_days, 1)
            })
        
        participation_df = pd.DataFrame(results)
        participation_df = participation_df.sort_values('first_seen')
        
        return participation_df
    
    def get_handoff_summary(self, handoff_df: pd.DataFrame) -> str:
        """Generate human-readable handoff summary"""
        if handoff_df.empty:
            return "No handoffs detected."
        
        summary = []
        summary.append(f"\n{'='*70}")
        summary.append("HANDOFF EVENTS SUMMARY")
        summary.append(f"{'='*70}\n")
        
        # Group by handoff type
        for handoff_type in handoff_df['handoff_type'].unique():
            subset = handoff_df[handoff_df['handoff_type'] == handoff_type]
            
            type_name = handoff_type.replace('_', ' ').title()
            summary.append(f"\n{type_name} ({len(subset)} events):")
            summary.append("-" * 70)
            
            for _, row in subset.iterrows():
                date_str = row['date'].strftime('%Y-%m-%d')
                summary.append(f"\n  [{date_str}] {row['event_subject']}")
                summary.append(f"    Confidence: {row['confidence']:.2%}")
                summary.append(f"    {row['description']}")
                
                if row['new_count'] > 0:
                    new_names = ', '.join(row['new_participants'][:3])
                    if row['new_count'] > 3:
                        new_names += f" (+ {row['new_count'] - 3} more)"
                    summary.append(f"    New: {new_names}")
                
                if row['departed_count'] > 0:
                    dept_names = ', '.join(row['departed_participants'][:3])
                    if row['departed_count'] > 3:
                        dept_names += f" (+ {row['departed_count'] - 3} more)"
                    summary.append(f"    Departed: {dept_names}")
        
        summary.append(f"\n{'='*70}\n")
        
        return '\n'.join(summary)
