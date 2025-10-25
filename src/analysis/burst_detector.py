"""
Collaboration burst detection module
Identifies periods of intense collaboration based on communication patterns
"""

import pandas as pd
from typing import List, Dict, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import logging

from src.models.schemas import CollaborationBurst

logger = logging.getLogger(__name__)


class CollaborationBurstDetector:
    """
    Detect periods of intense collaboration based on communication patterns
    
    Modified definition for consulting project context:
    - 8+ communication events in 48 hours (lowered threshold for realistic detection)
    - 3-8 participants (broader range for consulting teams)
    - Mixed email and meeting activity
    
    Supports adaptive parameter tuning based on dataset characteristics
    """
    
    def __init__(
        self,
        window_hours: int = 48,
        min_events: int = 8,
        min_participants: int = 3,
        max_participants: int = 8,
        adaptive: bool = False,
        timeline_df: pd.DataFrame = None
    ):
        """
        Initialize burst detector
        
        Args:
            window_hours: Sliding window size in hours
            min_events: Minimum events to qualify as burst
            min_participants: Minimum participants required
            max_participants: Maximum participants (filters out mass emails)
            adaptive: If True, calculate parameters from dataset
            timeline_df: Required if adaptive=True
        """
        if adaptive and timeline_df is not None:
            # Calculate adaptive parameters
            params = self._calculate_adaptive_params(timeline_df)
            self.window_hours = params['window_hours']
            self.min_events = params['min_events']
            self.min_participants = params['min_participants']
            self.max_participants = params['max_participants']
            logger.info(f"Adaptive parameters: window={self.window_hours}h, "
                       f"min_events={self.min_events}, "
                       f"participants={self.min_participants}-{self.max_participants}")
        else:
            self.window_hours = window_hours
            self.min_events = min_events
            self.min_participants = min_participants
            self.max_participants = max_participants
    
    def _calculate_adaptive_params(self, timeline_df: pd.DataFrame) -> Dict[str, int]:
        """
        Calculate adaptive parameters based on dataset density
        
        Strategy:
        - Sparse datasets (< 0.1 events/day): Use 30-day windows, lower thresholds
        - Medium datasets (0.1-0.5 events/day): Use 14-day windows
        - Dense datasets (> 0.5 events/day): Use 7-day windows, higher thresholds
        """
        if timeline_df.empty:
            return {
                'window_hours': 168,
                'min_events': 5,
                'min_participants': 2,
                'max_participants': 15
            }
        
        # Calculate event density
        total_days = (timeline_df['date'].max() - timeline_df['date'].min()).days
        total_days = max(total_days, 1)  # Avoid division by zero
        event_density = len(timeline_df) / total_days
        
        logger.info(f"Dataset statistics: {len(timeline_df)} events over {total_days} days "
                   f"(density: {event_density:.3f} events/day)")
        
        if event_density < 0.1:
            # Sparse dataset: consulting projects with periodic meetings
            return {
                'window_hours': 30 * 24,  # 30-day window
                'min_events': 3,
                'min_participants': 2,
                'max_participants': 20
            }
        elif event_density < 0.5:
            # Medium density: regular project work
            return {
                'window_hours': 14 * 24,  # 14-day window
                'min_events': 5,
                'min_participants': 3,
                'max_participants': 15
            }
        else:
            # Dense dataset: active development
            return {
                'window_hours': 7 * 24,  # 7-day window
                'min_events': 8,
                'min_participants': 3,
                'max_participants': 10
            }
    
    def detect_bursts(self, timeline_df: pd.DataFrame) -> List[CollaborationBurst]:
        """
        Detect collaboration bursts using sliding window approach
        """
        logger.info("Detecting collaboration bursts...")
        
        if timeline_df.empty:
            logger.warning("Empty timeline provided")
            return []
        
        bursts = []
        timeline = timeline_df.sort_values('date').to_dict('records')
        
        # Sliding window approach
        for i in range(len(timeline)):
            window_start = timeline[i]['date']
            window_end = window_start + timedelta(hours=self.window_hours)
            
            # Collect events in window
            window_events = []
            all_participants = set()
            
            for j in range(i, len(timeline)):
                if timeline[j]['date'] <= window_end:
                    window_events.append(timeline[j])
                    all_participants.update(timeline[j]['participants'])
                else:
                    break
            
            # Check burst criteria
            if (len(window_events) >= self.min_events and
                self.min_participants <= len(all_participants) <= self.max_participants):
                
                # Calculate confidence based on intensity and participant engagement
                confidence = self._calculate_burst_confidence(
                    window_events, 
                    all_participants
                )
                
                burst = CollaborationBurst(
                    start_date=window_start,
                    end_date=window_events[-1]['date'],
                    participants=list(all_participants),
                    event_count=len(window_events),
                    event_types=[e['type'] for e in window_events],
                    confidence=confidence,
                    trigger_events=[e['event_id'] for e in window_events]
                )
                
                # Avoid duplicate overlapping bursts
                if not self._overlaps_with_existing(burst, bursts):
                    bursts.append(burst)
                    logger.info(f"Burst detected: {len(window_events)} events, "
                              f"{len(all_participants)} participants, "
                              f"confidence: {confidence:.2f}")
        
        logger.info(f"Detected {len(bursts)} collaboration bursts")
        return bursts
    
    def _calculate_burst_confidence(
        self, 
        events: List[Dict], 
        participants: set
    ) -> float:
        """
        Calculate confidence score based on:
        - Event density (events per hour)
        - Participant balance (not dominated by one person)
        - Mix of communication types (email + meetings)
        """
        if not events:
            return 0.0
        
        # Event density score
        duration_hours = (events[-1]['date'] - events[0]['date']).total_seconds() / 3600
        duration_hours = max(duration_hours, 1)  # Avoid division by zero
        density_score = min(1.0, len(events) / (duration_hours * 2))
        
        # Participant balance score (Gini coefficient inverse)
        participant_counts = defaultdict(int)
        for event in events:
            for p in event['participants']:
                participant_counts[p] += 1
        
        if participant_counts:
            counts = list(participant_counts.values())
            gini = self._calculate_gini(counts)
            balance_score = 1 - gini
        else:
            balance_score = 0.0
        
        # Communication mix score
        event_types = [e['type'] for e in events]
        type_diversity = len(set(event_types)) / 2  # 2 types possible
        
        # Weighted average
        confidence = (
            0.4 * density_score +
            0.3 * balance_score +
            0.3 * type_diversity
        )
        
        return min(1.0, confidence)
    
    def _calculate_gini(self, values: List[int]) -> float:
        """Calculate Gini coefficient for inequality measurement"""
        if not values:
            return 0.0
        
        sorted_values = sorted(values)
        n = len(values)
        cumsum = 0
        
        for i, val in enumerate(sorted_values):
            cumsum += (n - i) * val
        
        total = sum(values)
        if total == 0:
            return 0.0
        
        return (2 * cumsum) / (n * total) - (n + 1) / n
    
    def _overlaps_with_existing(
        self, 
        new_burst: CollaborationBurst, 
        existing_bursts: List[CollaborationBurst]
    ) -> bool:
        """Check if burst overlaps significantly with existing bursts"""
        for existing in existing_bursts:
            # Check temporal overlap
            overlap_start = max(new_burst.start_date, existing.start_date)
            overlap_end = min(new_burst.end_date, existing.end_date)
            
            if overlap_start < overlap_end:
                overlap_duration = (overlap_end - overlap_start).total_seconds()
                new_duration = (new_burst.end_date - new_burst.start_date).total_seconds()
                
                # If >70% overlap, consider it duplicate
                if new_duration > 0 and overlap_duration / new_duration > 0.7:
                    return True
        
        return False
    
    def get_burst_summary(self, bursts: List[CollaborationBurst]) -> pd.DataFrame:
        """Generate summary statistics for detected bursts"""
        if not bursts:
            return pd.DataFrame()
        
        summary_data = []
        for i, burst in enumerate(bursts):
            summary_data.append({
                'burst_id': i,
                'start': burst.start_date,
                'end': burst.end_date,
                'duration_hours': (burst.end_date - burst.start_date).total_seconds() / 3600,
                'event_count': burst.event_count,
                'participant_count': len(burst.participants),
                'confidence': burst.confidence,
                'emails': burst.event_types.count('email'),
                'meetings': burst.event_types.count('meeting')
            })
        
        return pd.DataFrame(summary_data)
