"""
Phase transition detection module
Identifies project phase changes through topic modeling
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Tuple
from datetime import datetime, timedelta
from collections import Counter
import logging
import re

from sklearn.feature_extraction.text import TfidfVectorizer

logger = logging.getLogger(__name__)


class PhaseTransitionDetector:
    """
    Detect project phase transitions via topic shift analysis
    
    Uses TF-IDF on email/meeting subjects to identify when
    the team shifts focus to different topics (planning → design → implementation)
    """
    
    def __init__(
        self,
        window_days: int = 30,
        step_days: int = 15,
        similarity_threshold: float = 0.4,
        min_events_per_window: int = 3,
        top_keywords: int = 10
    ):
        """
        Initialize phase transition detector
        
        Args:
            window_days: Size of analysis window
            step_days: Step size for sliding window (overlap = window - step)
            similarity_threshold: Jaccard similarity threshold (lower = more sensitive)
            min_events_per_window: Minimum events required in window
            top_keywords: Number of top keywords to extract per phase
        """
        self.window_days = window_days
        self.step_days = step_days
        self.similarity_threshold = similarity_threshold
        self.min_events_per_window = min_events_per_window
        self.top_keywords = top_keywords
    
    def detect_transitions(self, timeline_df: pd.DataFrame) -> pd.DataFrame:
        """
        Main detection method
        
        Returns:
            DataFrame with columns: date, phase_id, keywords, similarity_to_prev,
            confidence, event_count, description
        """
        logger.info("Detecting phase transitions...")
        
        if timeline_df.empty or len(timeline_df) < self.min_events_per_window:
            logger.warning("Insufficient data for phase detection")
            return pd.DataFrame()
        
        # Create time windows
        windows = self._create_time_windows(timeline_df)
        
        if len(windows) < 2:
            logger.warning("Need at least 2 time windows for transition detection")
            return pd.DataFrame()
        
        logger.info(f"Created {len(windows)} time windows for analysis")
        
        # Extract topics per window
        window_topics = self._extract_window_topics(windows)
        
        if len(window_topics) < 2:
            logger.warning("Could not extract topics from windows")
            return pd.DataFrame()
        
        # Identify transitions
        transitions = self._identify_transitions(window_topics)
        
        if not transitions:
            logger.warning("No phase transitions detected")
            return pd.DataFrame()
        
        # Convert to DataFrame
        transition_df = pd.DataFrame(transitions)
        transition_df = transition_df.sort_values('date').reset_index(drop=True)
        transition_df['transition_id'] = range(len(transition_df))
        
        logger.info(f"Detected {len(transition_df)} phase transitions")
        return transition_df
    
    def _create_time_windows(self, timeline_df: pd.DataFrame) -> List[pd.DataFrame]:
        """
        Create overlapping time windows for analysis
        50% overlap for smoother transition detection
        """
        windows = []
        start_date = timeline_df['date'].min()
        end_date = timeline_df['date'].max()
        
        current = start_date
        window_id = 0
        
        while current < end_date:
            window_end = current + timedelta(days=self.window_days)
            
            window = timeline_df[
                (timeline_df['date'] >= current) &
                (timeline_df['date'] < window_end)
            ].copy()
            
            if len(window) >= self.min_events_per_window:
                window['window_id'] = window_id
                windows.append(window)
                window_id += 1
            
            current += timedelta(days=self.step_days)
        
        return windows
    
    def _extract_window_topics(self, windows: List[pd.DataFrame]) -> List[Dict]:
        """
        Extract dominant topics from each window using TF-IDF
        """
        window_topics = []
        
        for i, window in enumerate(windows):
            # Get all subjects in window
            subjects = window['subject'].fillna('').tolist()
            
            if not subjects or all(s == '' for s in subjects):
                continue
            
            # Clean subjects
            cleaned_subjects = [self._clean_text(s) for s in subjects]
            cleaned_subjects = [s for s in cleaned_subjects if s]
            
            if not cleaned_subjects:
                continue
            
            try:
                # TF-IDF extraction
                vectorizer = TfidfVectorizer(
                    max_features=50,
                    stop_words='english',
                    ngram_range=(1, 2),
                    min_df=1,
                    max_df=0.9,
                    token_pattern=r'(?u)\b[a-zA-Z][a-zA-Z]+\b'
                )
                
                tfidf_matrix = vectorizer.fit_transform(cleaned_subjects)
                feature_names = vectorizer.get_feature_names_out()
                
                # Get top keywords by average TF-IDF score
                mean_scores = np.asarray(tfidf_matrix.mean(axis=0)).flatten()
                top_indices = mean_scores.argsort()[-self.top_keywords:][::-1]
                top_keywords = [feature_names[idx] for idx in top_indices]
                
                # Also get most common words as backup
                all_words = []
                for subj in cleaned_subjects:
                    all_words.extend(subj.split())
                
                word_freq = Counter(all_words)
                common_words = [w for w, _ in word_freq.most_common(self.top_keywords)]
                
                # Combine and deduplicate
                combined_keywords = list(dict.fromkeys(top_keywords + common_words))[:self.top_keywords]
                
                window_topics.append({
                    'window_id': i,
                    'start': window['date'].min(),
                    'end': window['date'].max(),
                    'keywords': combined_keywords,
                    'event_count': len(window),
                    'subjects': cleaned_subjects
                })
                
            except Exception as e:
                logger.debug(f"Could not extract topics from window {i}: {e}")
                continue
        
        return window_topics
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text for topic extraction"""
        # Convert to lowercase
        text = text.lower()
        
        # Remove email addresses
        text = re.sub(r'\S+@\S+', '', text)
        
        # Remove URLs
        text = re.sub(r'http\S+|www\.\S+', '', text)
        
        # Remove special characters but keep spaces
        text = re.sub(r'[^a-z0-9\s]', ' ', text)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Remove very common project-agnostic words
        stop_words = {'re', 'fw', 'fwd', 'meeting', 'call', 'update', 'discussion'}
        words = [w for w in text.split() if w not in stop_words and len(w) > 2]
        
        return ' '.join(words)
    
    def _identify_transitions(self, window_topics: List[Dict]) -> List[Dict]:
        """
        Find topic shifts between consecutive windows
        Low Jaccard similarity = phase transition
        """
        transitions = []
        
        for i in range(1, len(window_topics)):
            prev_window = window_topics[i-1]
            curr_window = window_topics[i]
            
            # Calculate Jaccard similarity between keyword sets
            set1 = set(prev_window['keywords'])
            set2 = set(curr_window['keywords'])
            
            intersection = len(set1 & set2)
            union = len(set1 | set2)
            
            similarity = intersection / union if union > 0 else 0
            
            # Low similarity indicates phase shift
            if similarity < self.similarity_threshold:
                # Determine phase names from keywords
                prev_phase = self._infer_phase_name(prev_window['keywords'])
                curr_phase = self._infer_phase_name(curr_window['keywords'])
                
                # Calculate confidence
                # Lower similarity = higher confidence in transition
                similarity_score = 1 - similarity
                event_density_score = min(1.0, curr_window['event_count'] / 10)
                keyword_quality_score = min(1.0, len(curr_window['keywords']) / self.top_keywords)
                
                confidence = (0.5 * similarity_score + 
                            0.3 * event_density_score + 
                            0.2 * keyword_quality_score)
                
                transitions.append({
                    'date': curr_window['start'],
                    'previous_phase': prev_phase,
                    'new_phase': curr_phase,
                    'previous_keywords': prev_window['keywords'][:5],
                    'new_keywords': curr_window['keywords'][:5],
                    'similarity_score': round(similarity, 3),
                    'confidence': round(confidence, 3),
                    'event_count': curr_window['event_count'],
                    'description': f"Phase transition from {prev_phase} to {curr_phase} "
                                 f"(similarity: {similarity:.2%})"
                })
        
        return transitions
    
    def _infer_phase_name(self, keywords: List[str]) -> str:
        """
        Infer project phase from dominant keywords
        """
        keywords_lower = [k.lower() for k in keywords]
        keywords_str = ' '.join(keywords_lower)
        
        # Phase detection patterns
        if any(word in keywords_str for word in ['workshop', 'kickoff', 'briefing', 'discovery', 'planning']):
            return "Planning"
        
        if any(word in keywords_str for word in ['design', 'brand', 'identity', 'visual', 'creative']):
            return "Design"
        
        if any(word in keywords_str for word in ['architecture', 'technical', 'implementation', 'development']):
            return "Development"
        
        if any(word in keywords_str for word in ['presentation', 'review', 'demo', 'delivery']):
            return "Delivery"
        
        if any(word in keywords_str for word in ['scope', 'requirements', 'specification', 'documentation']):
            return "Scoping"
        
        if any(word in keywords_str for word in ['launch', 'release', 'deployment', 'live']):
            return "Launch"
        
        if any(word in keywords_str for word in ['maintenance', 'support', 'update', 'iteration']):
            return "Maintenance"
        
        # Default: use most prominent keyword
        if keywords:
            return keywords[0].title()
        
        return "Unknown"
    
    def get_phase_summary(self, transition_df: pd.DataFrame) -> str:
        """Generate human-readable summary of phase transitions"""
        if transition_df.empty:
            return "No phase transitions detected."
        
        summary = []
        summary.append(f"\n{'='*70}")
        summary.append("PROJECT PHASE TRANSITIONS")
        summary.append(f"{'='*70}\n")
        
        for _, row in transition_df.iterrows():
            date_str = row['date'].strftime('%Y-%m-%d')
            summary.append(f"\n[{date_str}] {row['previous_phase']} → {row['new_phase']}")
            summary.append(f"  Confidence: {row['confidence']:.2%}")
            summary.append(f"  Topic Shift: {row['similarity_score']:.2%} similarity")
            summary.append(f"  Previous Focus: {', '.join(row['previous_keywords'])}")
            summary.append(f"  New Focus: {', '.join(row['new_keywords'])}")
            summary.append(f"  Events in New Phase: {row['event_count']}")
        
        summary.append(f"\n{'='*70}\n")
        
        return '\n'.join(summary)
