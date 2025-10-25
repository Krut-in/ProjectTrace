"""
Advanced Communication Pattern Analysis Module
Analyzes urgency, collaboration style, formality, and working dynamics
"""

import pandas as pd
from typing import List, Dict, Tuple
from datetime import datetime, timedelta
import logging
import re
from collections import Counter

logger = logging.getLogger(__name__)


class SentimentAnalyzer:
    """
    Analyze communication patterns, urgency levels, and collaboration styles
    
    Goes beyond basic sentiment to understand:
    - Urgency and time pressure
    - Formality and professionalism
    - Collaboration intensity
    - Communication efficiency
    - Working relationship dynamics
    """
    
    def __init__(self):
        """Initialize analyzer with pattern dictionaries"""
        
        # Urgency indicators (time-sensitive communication)
        self.urgency_high = {
            'urgent', 'asap', 'immediately', 'critical', 'emergency',
            'deadline', 'rush', 'priority', 'time-sensitive', 'quickly',
            'hurry', 'pressing', 'crucial', 'now', 'today', 'right away',
            'time is of the essence', 'by end of day', 'eod', 'need asap'
        }
        
        self.urgency_medium = {
            'soon', 'upcoming', 'next', 'follow up', 'followup',
            'reminder', 'pending', 'waiting', 'response needed',
            'at your earliest', 'when you can', 'please advise'
        }
        
        # Positive sentiment indicators
        self.positive_keywords = {
            'great', 'excellent', 'fantastic', 'wonderful', 'perfect',
            'thank', 'thanks', 'appreciate', 'grateful', 'pleased',
            'happy', 'excited', 'looking forward', 'approved', 'confirmed',
            'successful', 'completed', 'achieved', 'congratulations',
            'well done', 'impressive', 'outstanding', 'brilliant'
        }
        
        # Negative sentiment indicators  
        self.negative_keywords = {
            'issue', 'problem', 'concern', 'worry', 'unfortunately',
            'delay', 'late', 'missed', 'failed', 'error', 'mistake',
            'confused', 'unclear', 'difficulty', 'trouble', 'stuck',
            'blocked', 'frustrated', 'disappointed', 'wrong', 'incorrect',
            'apologize', 'sorry', 'regret'
        }
        
        # Formality indicators
        self.formal_markers = {
            'presentation', 'strategy', 'proposal', 'professional',
            'corporate', 'official', 'formal', 'executive', 'board',
            'quarterly', 'annual', 'report', 'analysis', 'review',
            'respectfully', 'sincerely', 'regards', 'dear', 'pursuant'
        }
        
        self.casual_markers = {
            'chat', 'quick', 'favor', 'fyi', 'heads up', 'catch up',
            'sync', 'coffee', 'informal', 'casual', 'brief', 'hey',
            'hi', 'thanks!', 'cool', 'awesome', 'nice'
        }
        
        # Collaboration style indicators
        self.collaborative_markers = {
            'workshop', 'brainstorm', 'discussion', 'team', 'together',
            'collaboration', 'group', 'joint', 'collective', 'session',
            'working session', 'roundtable', 'meeting', 'let\'s discuss',
            'input', 'feedback', 'thoughts', 'ideas', 'collaborate'
        }
        
        self.directive_markers = {
            'briefing', 'update', 'report', 'status', 'checkpoint',
            'review', 'feedback', 'approval', 'sign-off', 'decision',
            'please provide', 'need', 'require', 'must', 'should'
        }
        
        # Action/request indicators
        self.action_keywords = {
            'please', 'kindly', 'could you', 'can you', 'would you',
            'need', 'require', 'request', 'action required', 'to do',
            'next steps', 'action items', 'deliverables'
        }
        
        # Gratitude indicators
        self.gratitude_keywords = {
            'thank', 'thanks', 'appreciate', 'grateful', 'gratitude',
            'acknowledgment', 'credit', 'recognition'
        }
        
        # Handoff/CC indicators
        self.handoff_keywords = {
            'adding', 'looping in', 'cc\'ing', 'cc\'d', 'including',
            'bringing in', 'forwarding', 'fwd', 'introducing',
            'connecting you with', 'hand off', 'handoff', 'transition'
        }
        
        # Project phase indicators
        self.initiation_markers = {
            'kickoff', 'introduction', 'intro', 'welcome', 'onboarding',
            'initial', 'first', 'beginning', 'start', 'launch'
        }
        
        self.development_markers = {
            'design', 'development', 'building', 'creating', 'iteration',
            'draft', 'prototype', 'version', 'working on'
        }
        
        self.finalization_markers = {
            'final', 'completed', 'finished', 'done', 'delivery',
            'submission', 'handoff', 'conclusion', 'wrap up', 'closing'
        }
        
        # Decision-making indicators
        self.decision_markers = {
            'decide', 'decision', 'choice', 'select', 'determine',
            'agree', 'consensus', 'resolve', 'conclude', 'approve'
        }
        
        # Problem/issue indicators
        self.problem_markers = {
            'issue', 'problem', 'concern', 'challenge', 'obstacle',
            'blocker', 'difficulty', 'confusion', 'unclear', 'question'
        }
    
    def analyze_timeline(self, timeline_df: pd.DataFrame) -> pd.DataFrame:
        """
        Analyze communication patterns across entire timeline
        
        Returns:
            DataFrame with pattern analysis including urgency, formality,
            collaboration style, and project phase
        """
        logger.info("Analyzing communication patterns across timeline...")
        
        if timeline_df.empty:
            logger.warning("Empty timeline provided")
            return timeline_df
        
        results = []
        df = timeline_df.sort_values('date').copy()
        
        # Calculate response times for emails
        response_times = self._calculate_response_times(df)
        
        for idx, row in df.iterrows():
            subject = row.get('subject', '')
            body_text = row.get('body_text', '')  # Get email body text
            event_type = row.get('type', 'unknown')
            participant_count = row.get('participant_count', 0)
            
            # Combine subject and body for analysis
            combined_text = f"{subject}\n{body_text}" if body_text else subject
            
            if pd.isna(combined_text) or combined_text.strip() == '':
                analysis = self._get_default_analysis()
            else:
                analysis = self.analyze_communication(
                    combined_text,  # Use combined text instead of just subject
                    event_type, 
                    participant_count,
                    response_times.get(idx)
                )
            
            # Combine original row with analysis
            result = row.to_dict()
            result.update(analysis)
            results.append(result)
        
        analysis_df = pd.DataFrame(results)
        
        # Log insights
        self._log_pattern_insights(analysis_df)
        
        return analysis_df
    
    def _calculate_response_times(self, df: pd.DataFrame) -> Dict:
        """Calculate response time patterns for email threads"""
        response_times = {}
        
        email_threads = df[df['type'] == 'email'].copy()
        
        for idx, row in email_threads.iterrows():
            email_count = row.get('email_count', 1)
            duration_days = row.get('duration_days', 0)
            
            if email_count and email_count > 1 and duration_days:
                # Average response time in hours
                avg_response = (duration_days * 24) / (email_count - 1)
                response_times[idx] = avg_response
        
        return response_times
    
    def analyze_communication(
        self, 
        text: str, 
        event_type: str = 'unknown',
        participant_count: int = 0,
        response_time: float = None
    ) -> Dict:
        """
        Analyze communication patterns and dynamics
        
        Returns comprehensive analysis including:
        - Urgency level
        - Formality score
        - Collaboration style
        - Project phase
        - Communication efficiency
        - Sentiment (positive/negative/neutral)
        - Action items presence
        - Gratitude indicators
        """
        if not text or text.strip() == '':
            return self._get_default_analysis()
        
        text_lower = text.lower()
        
        # Urgency Analysis
        urgency_level, urgency_score = self._analyze_urgency(text_lower)
        
        # Formality Analysis
        formality_level, formality_score = self._analyze_formality(text_lower, event_type)
        
        # Collaboration Style
        collab_style, collab_score = self._analyze_collaboration_style(
            text_lower, event_type, participant_count
        )
        
        # Project Phase
        phase = self._detect_project_phase(text_lower)
        
        # Sentiment Analysis
        sentiment, sentiment_score = self._analyze_sentiment(text_lower)
        
        # Decision-making presence
        has_decision = any(marker in text_lower for marker in self.decision_markers)
        
        # Problem/issue presence
        has_problem = any(marker in text_lower for marker in self.problem_markers)
        
        # Action items presence
        has_actions = any(keyword in text_lower for keyword in self.action_keywords)
        
        # Gratitude presence
        has_gratitude = any(keyword in text_lower for keyword in self.gratitude_keywords)
        
        # Handoff indicators
        has_handoff = any(keyword in text_lower for keyword in self.handoff_keywords)
        
        # Communication efficiency (based on response time)
        efficiency = self._calculate_efficiency(response_time)
        
        # Overall pattern classification
        pattern_type = self._classify_pattern(
            urgency_level, formality_level, collab_style, has_decision, 
            has_problem, sentiment
        )
        
        return {
            'urgency_level': urgency_level,
            'urgency_score': round(urgency_score, 3),
            'formality_level': formality_level,
            'formality_score': round(formality_score, 3),
            'collaboration_style': collab_style,
            'collaboration_score': round(collab_score, 3),
            'project_phase': phase,
            'sentiment': sentiment,
            'sentiment_score': round(sentiment_score, 3),
            'has_decision_making': has_decision,
            'has_problem_solving': has_problem,
            'has_action_items': has_actions,
            'has_gratitude': has_gratitude,
            'has_handoff_language': has_handoff,
            'communication_efficiency': efficiency,
            'pattern_type': pattern_type,
            'response_time_hours': round(response_time, 2) if response_time else None
        }
    
    def _get_default_analysis(self) -> Dict:
        """Return default analysis for empty/invalid text"""
        return {
            'urgency_level': 'low',
            'urgency_score': 0.0,
            'formality_level': 'neutral',
            'formality_score': 0.5,
            'collaboration_style': 'unknown',
            'collaboration_score': 0.0,
            'project_phase': 'unknown',
            'sentiment': 'neutral',
            'sentiment_score': 0.5,
            'has_decision_making': False,
            'has_problem_solving': False,
            'has_action_items': False,
            'has_gratitude': False,
            'has_handoff_language': False,
            'communication_efficiency': 'unknown',
            'pattern_type': 'routine',
            'response_time_hours': None
        }
    
    def _analyze_sentiment(self, text: str) -> Tuple[str, float]:
        """Analyze overall sentiment of text"""
        positive_matches = sum(1 for kw in self.positive_keywords if kw in text)
        negative_matches = sum(1 for kw in self.negative_keywords if kw in text)
        
        # Calculate sentiment score
        total_sentiment = positive_matches + negative_matches
        
        if total_sentiment == 0:
            return 'neutral', 0.5
        
        positive_ratio = positive_matches / total_sentiment
        
        if positive_matches > negative_matches:
            sentiment = 'positive'
            score = 0.5 + (positive_ratio * 0.5)  # 0.5 to 1.0
        elif negative_matches > positive_matches:
            sentiment = 'negative'
            score = 0.5 - (positive_ratio * 0.5)  # 0.0 to 0.5
        else:
            sentiment = 'neutral'
            score = 0.5
        
        return sentiment, score
    
    def _analyze_urgency(self, text: str) -> Tuple[str, float]:
        """Analyze urgency level of communication"""
        high_matches = sum(1 for kw in self.urgency_high if kw in text)
        medium_matches = sum(1 for kw in self.urgency_medium if kw in text)
        
        score = (high_matches * 3 + medium_matches * 1.5) / 10
        score = min(1.0, score)
        
        if score > 0.5:
            level = 'high'
        elif score > 0.2:
            level = 'medium'
        else:
            level = 'low'
        
        return level, score
    
    def _analyze_formality(self, text: str, event_type: str) -> Tuple[str, float]:
        """Analyze formality level"""
        formal_matches = sum(1 for kw in self.formal_markers if kw in text)
        casual_matches = sum(1 for kw in self.casual_markers if kw in text)
        
        # Meetings tend to be more formal
        base_score = 0.6 if event_type == 'meeting' else 0.5
        
        # Adjust based on keywords
        adjustment = (formal_matches - casual_matches) * 0.1
        score = base_score + adjustment
        score = max(0.0, min(1.0, score))
        
        if score > 0.7:
            level = 'formal'
        elif score < 0.3:
            level = 'casual'
        else:
            level = 'neutral'
        
        return level, score
    
    def _analyze_collaboration_style(
        self, text: str, event_type: str, participant_count: int
    ) -> Tuple[str, float]:
        """Analyze collaboration style and intensity"""
        collaborative_matches = sum(1 for kw in self.collaborative_markers if kw in text)
        directive_matches = sum(1 for kw in self.directive_markers if kw in text)
        
        # Factor in participant count
        size_factor = min(1.0, participant_count / 10) if participant_count > 0 else 0.5
        
        if collaborative_matches > directive_matches:
            style = 'collaborative'
            score = (collaborative_matches / 5 + size_factor) / 2
        elif directive_matches > collaborative_matches:
            style = 'directive'
            score = (directive_matches / 5) * 0.7
        else:
            style = 'balanced'
            score = 0.5
        
        score = min(1.0, score)
        
        return style, score
    
    def _detect_project_phase(self, text: str) -> str:
        """Detect which project phase this communication belongs to"""
        init_score = sum(1 for kw in self.initiation_markers if kw in text)
        dev_score = sum(1 for kw in self.development_markers if kw in text)
        final_score = sum(1 for kw in self.finalization_markers if kw in text)
        
        scores = {
            'initiation': init_score,
            'development': dev_score,
            'finalization': final_score
        }
        
        max_score = max(scores.values())
        
        if max_score == 0:
            return 'maintenance'
        
        # Return phase with highest score
        return max(scores, key=scores.get)
    
    def _calculate_efficiency(self, response_time: float) -> str:
        """Calculate communication efficiency based on response time"""
        if response_time is None:
            return 'unknown'
        
        if response_time < 2:  # < 2 hours
            return 'very_fast'
        elif response_time < 24:  # < 1 day
            return 'fast'
        elif response_time < 72:  # < 3 days
            return 'moderate'
        else:
            return 'slow'
    
    def _classify_pattern(
        self, 
        urgency: str, 
        formality: str, 
        collab_style: str,
        has_decision: bool,
        has_problem: bool,
        sentiment: str
    ) -> str:
        """Classify overall communication pattern"""
        
        if urgency == 'high' and has_problem:
            return 'crisis_management'
        elif urgency == 'high' and has_decision:
            return 'urgent_decision'
        elif has_decision and formality == 'formal':
            return 'strategic_decision'
        elif collab_style == 'collaborative' and formality == 'casual':
            return 'creative_session'
        elif collab_style == 'collaborative' and formality == 'formal':
            return 'structured_workshop'
        elif collab_style == 'directive' and formality == 'formal':
            return 'status_review'
        elif has_problem:
            return 'problem_solving'
        elif sentiment == 'positive' and formality == 'casual':
            return 'positive_update'
        elif sentiment == 'negative':
            return 'concern_raised'
        elif formality == 'casual':
            return 'informal_sync'
        else:
            return 'routine'
    
    def _log_pattern_insights(self, df: pd.DataFrame):
        """Log interesting insights about communication patterns"""
        if df.empty:
            return
        
        total = len(df)
        
        # Urgency distribution
        urgency_counts = df['urgency_level'].value_counts()
        logger.info(f"Urgency levels: {urgency_counts.to_dict()}")
        
        # Pattern types
        pattern_counts = df['pattern_type'].value_counts()
        logger.info(f"Communication patterns: {pattern_counts.to_dict()}")
        
        # Efficiency
        if 'communication_efficiency' in df.columns:
            efficiency_counts = df[df['communication_efficiency'] != 'unknown']['communication_efficiency'].value_counts()
            if not efficiency_counts.empty:
                logger.info(f"Response efficiency: {efficiency_counts.to_dict()}")
        
        # Collaboration styles
        collab_counts = df['collaboration_style'].value_counts()
        logger.info(f"Collaboration styles: {collab_counts.to_dict()}")
    
    def get_sentiment_trends(
        self, 
        sentiment_df: pd.DataFrame,
        window_days: int = 30
    ) -> pd.DataFrame:
        """
        Calculate communication pattern trends over time
        
        Returns:
            DataFrame with aggregated pattern metrics over time
        """
        if sentiment_df.empty:
            return pd.DataFrame()
        
        df = sentiment_df.copy()
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        df.set_index('date', inplace=True)
        
        # Resample to daily
        daily = df.resample('D').agg({
            'urgency_score': 'mean',
            'formality_score': 'mean',
            'collaboration_score': 'mean'
        }).fillna(method='ffill')
        
        # Calculate rolling averages
        window = f'{window_days}D'
        trends = pd.DataFrame()
        trends['date'] = daily.index
        trends['avg_urgency'] = daily['urgency_score'].rolling(
            window=window, min_periods=1
        ).mean()
        trends['avg_formality'] = daily['formality_score'].rolling(
            window=window, min_periods=1
        ).mean()
        trends['avg_collaboration'] = daily['collaboration_score'].rolling(
            window=window, min_periods=1
        ).mean()
        
        # Add pattern type percentages
        pattern_counts = df.groupby(
            pd.Grouper(freq=window)
        )['pattern_type'].value_counts(normalize=True).unstack(fill_value=0)
        
        for col in pattern_counts.columns:
            trends = trends.merge(
                pattern_counts[[col]].rename(columns={col: f'{col}_pct'}),
                left_on='date',
                right_index=True,
                how='left'
            )
        
        trends = trends.fillna(0)
        trends = trends.reset_index(drop=True)
        
        return trends
    
    def detect_sentiment_shifts(
        self,
        sentiment_df: pd.DataFrame,
        threshold: float = 0.3
    ) -> List[Dict]:
        """
        Detect significant shifts in communication patterns
        
        Returns:
            List of notable pattern changes
        """
        if sentiment_df.empty or len(sentiment_df) < 2:
            return []
        
        shifts = []
        df = sentiment_df.sort_values('date').copy()
        
        # Track urgency changes
        df['urgency_ma'] = df['urgency_score'].rolling(window=5, min_periods=1).mean()
        
        for i in range(5, len(df)):
            prev_urgency = df.iloc[i-5:i]['urgency_ma'].mean()
            curr_urgency = df.iloc[i]['urgency_ma']
            
            change = curr_urgency - prev_urgency
            
            if abs(change) >= threshold:
                direction = 'increased' if change > 0 else 'decreased'
                
                shifts.append({
                    'date': df.iloc[i]['date'],
                    'metric': 'urgency',
                    'direction': direction,
                    'magnitude': round(abs(change), 3),
                    'previous_value': round(prev_urgency, 3),
                    'new_value': round(curr_urgency, 3),
                    'subject': df.iloc[i].get('subject', 'N/A'),
                    'description': f"Urgency {direction} by {abs(change):.2f}"
                })
        
        return shifts
    
    def get_person_communication_style(
        self, 
        timeline_df: pd.DataFrame, 
        sentiment_df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Analyze communication style for each person
        
        Returns DataFrame with per-person communication patterns
        """
        if sentiment_df.empty or timeline_df.empty:
            return pd.DataFrame()
        
        person_patterns = []
        
        # Parse participants and aggregate patterns
        for idx, row in sentiment_df.iterrows():
            participants = row.get('participants', [])
            
            if isinstance(participants, str):
                # Parse string representation of list
                participants = eval(participants) if participants.startswith('[') else [participants]
            
            for person in participants:
                person_patterns.append({
                    'person': person,
                    'urgency_score': row.get('urgency_score', 0),
                    'formality_score': row.get('formality_score', 0.5),
                    'collaboration_score': row.get('collaboration_score', 0),
                    'pattern_type': row.get('pattern_type', 'routine'),
                    'has_decision': row.get('has_decision_making', False),
                    'has_problem': row.get('has_problem_solving', False)
                })
        
        if not person_patterns:
            return pd.DataFrame()
        
        patterns_df = pd.DataFrame(person_patterns)
        
        # Aggregate by person
        person_stats = patterns_df.groupby('person').agg({
            'urgency_score': 'mean',
            'formality_score': 'mean',
            'collaboration_score': 'mean',
            'has_decision': 'sum',
            'has_problem': 'sum'
        }).reset_index()
        
        person_stats.columns = [
            'person', 'avg_urgency', 'avg_formality', 
            'avg_collaboration', 'decision_count', 'problem_count'
        ]
        
        # Count events per person
        event_counts = patterns_df.groupby('person').size().reset_index(name='event_count')
        person_stats = person_stats.merge(event_counts, on='person')
        
        # Classify communication style
        person_stats['communication_style'] = person_stats.apply(
            self._classify_person_style, axis=1
        )
        
        # Sort by event count
        person_stats = person_stats.sort_values('event_count', ascending=False)
        
        return person_stats
    
    def _classify_person_style(self, row) -> str:
        """Classify a person's overall communication style"""
        urgency = row['avg_urgency']
        formality = row['avg_formality']
        collab = row['avg_collaboration']
        decisions = row['decision_count']
        problems = row['problem_count']
        events = row['event_count']
        
        if decisions > events * 0.3:
            return 'decision_maker'
        elif problems > events * 0.3:
            return 'problem_solver'
        elif collab > 0.6:
            return 'collaborator'
        elif formality > 0.7:
            return 'formal_professional'
        elif urgency > 0.5:
            return 'action_oriented'
        else:
            return 'balanced'
    
    def get_sentiment_summary(self, sentiment_df: pd.DataFrame) -> str:
        """Generate human-readable communication pattern summary"""
        if sentiment_df.empty:
            return "No communication data available."
        
        summary = []
        summary.append(f"\n{'='*70}")
        summary.append("COMMUNICATION PATTERN ANALYSIS")
        summary.append(f"{'='*70}\n")
        
        total = len(sentiment_df)
        
        # Urgency Analysis
        summary.append("📊 URGENCY LEVELS:")
        urgency_counts = sentiment_df['urgency_level'].value_counts()
        for level in ['high', 'medium', 'low']:
            count = urgency_counts.get(level, 0)
            pct = (count / total * 100) if total > 0 else 0
            summary.append(f"  {level.title()}: {count} ({pct:.1f}%)")
        
        # Pattern Types
        summary.append("\n💬 COMMUNICATION PATTERNS:")
        pattern_counts = sentiment_df['pattern_type'].value_counts().head(5)
        for pattern, count in pattern_counts.items():
            pct = (count / total * 100) if total > 0 else 0
            pattern_display = pattern.replace('_', ' ').title()
            summary.append(f"  {pattern_display}: {count} ({pct:.1f}%)")
        
        # Formality Distribution
        summary.append("\n🎩 FORMALITY:")
        formality_counts = sentiment_df['formality_level'].value_counts()
        for level in ['formal', 'neutral', 'casual']:
            count = formality_counts.get(level, 0)
            pct = (count / total * 100) if total > 0 else 0
            summary.append(f"  {level.title()}: {count} ({pct:.1f}%)")
        
        # Collaboration Styles
        summary.append("\n🤝 COLLABORATION STYLES:")
        collab_counts = sentiment_df['collaboration_style'].value_counts()
        for style in ['collaborative', 'directive', 'balanced', 'unknown']:
            count = collab_counts.get(style, 0)
            if count > 0:
                pct = (count / total * 100) if total > 0 else 0
                summary.append(f"  {style.title()}: {count} ({pct:.1f}%)")
        
        # Project Phases
        summary.append("\n🚀 PROJECT PHASES:")
        phase_counts = sentiment_df['project_phase'].value_counts()
        for phase, count in phase_counts.items():
            pct = (count / total * 100) if total > 0 else 0
            summary.append(f"  {phase.title()}: {count} ({pct:.1f}%)")
        
        # Decision Making & Problem Solving
        decision_count = sentiment_df['has_decision_making'].sum()
        problem_count = sentiment_df['has_problem_solving'].sum()
        summary.append(f"\n🎯 KEY ACTIVITIES:")
        summary.append(f"  Decision-making events: {decision_count} ({decision_count/total*100:.1f}%)")
        summary.append(f"  Problem-solving events: {problem_count} ({problem_count/total*100:.1f}%)")
        
        # Response Efficiency (for emails)
        email_data = sentiment_df[
            (sentiment_df['type'] == 'email') & 
            (sentiment_df['communication_efficiency'] != 'unknown')
        ]
        if not email_data.empty:
            summary.append(f"\n⚡ EMAIL RESPONSE EFFICIENCY:")
            efficiency_counts = email_data['communication_efficiency'].value_counts()
            for eff in ['very_fast', 'fast', 'moderate', 'slow']:
                count = efficiency_counts.get(eff, 0)
                if count > 0:
                    pct = (count / len(email_data) * 100)
                    eff_display = eff.replace('_', ' ').title()
                    summary.append(f"  {eff_display}: {count} ({pct:.1f}%)")
            
            # Average response time
            avg_response = email_data['response_time_hours'].mean()
            if not pd.isna(avg_response):
                summary.append(f"  Average response time: {avg_response:.1f} hours")
        
        # Most urgent communication
        high_urgency = sentiment_df[sentiment_df['urgency_level'] == 'high']
        if not high_urgency.empty:
            most_urgent = high_urgency.nlargest(1, 'urgency_score').iloc[0]
            summary.append(f"\n🚨 HIGHEST URGENCY:")
            summary.append(f"  Date: {most_urgent['date'].strftime('%Y-%m-%d')}")
            summary.append(f"  Subject: {most_urgent.get('subject', 'N/A')}")
            summary.append(f"  Urgency Score: {most_urgent['urgency_score']:.2f}")
        
        # Most collaborative event
        most_collab = sentiment_df.nlargest(1, 'collaboration_score').iloc[0]
        summary.append(f"\n🌟 MOST COLLABORATIVE:")
        summary.append(f"  Date: {most_collab['date'].strftime('%Y-%m-%d')}")
        summary.append(f"  Subject: {most_collab.get('subject', 'N/A')}")
        summary.append(f"  Participants: {most_collab.get('participant_count', 'N/A')}")
        summary.append(f"  Collaboration Score: {most_collab['collaboration_score']:.2f}")
        
        summary.append(f"\n{'='*70}\n")
        
        return '\n'.join(summary)
