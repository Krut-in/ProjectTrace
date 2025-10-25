"""
Sentiment analysis module
Analyzes emotional tone of communications using keyword-based approach
"""

import pandas as pd
from typing import List, Dict, Tuple
from datetime import datetime
import logging
import re

logger = logging.getLogger(__name__)


class SentimentAnalyzer:
    """
    Analyze sentiment of email subjects and meeting titles
    
    Uses keyword-based approach since email bodies are not available
    Tracks positive, negative, and neutral sentiment over time
    """
    
    def __init__(self):
        """Initialize sentiment analyzer with keyword dictionaries"""
        
        # Positive indicators
        self.positive_keywords = {
            'great', 'thanks', 'thank', 'approved', 'confirmed', 'ready',
            'excited', 'looking forward', 'excellent', 'perfect', 'success',
            'completed', 'done', 'finished', 'congratulations', 'agree',
            'good', 'wonderful', 'amazing', 'fantastic', 'pleased',
            'happy', 'love', 'appreciate', 'brilliant', 'awesome'
        }
        
        # Negative indicators
        self.negative_keywords = {
            'issue', 'problem', 'concern', 'delay', 'late', 'waiting',
            'urgent', 'confused', 'unclear', 'stuck', 'blocked', 'error',
            'failed', 'failure', 'wrong', 'incorrect', 'missing', 'urgent',
            'help', 'asap', 'immediately', 'critical', 'emergency',
            'worried', 'disappointed', 'frustrated', 'difficult'
        }
        
        # Neutral indicators (questions, status updates)
        self.neutral_keywords = {
            'update', 'meeting', 'review', 'discussion', 'agenda',
            'schedule', 'planning', 'status', 'report', 'summary',
            'overview', 'sync', 'followup', 'follow-up', 'check-in',
            'question', 'clarification', 'information', 'details'
        }
        
        # Intensifiers
        self.intensifiers = {
            'very', 'extremely', 'really', 'highly', 'absolutely',
            'completely', 'totally', 'seriously', 'desperately'
        }
    
    def analyze_timeline(self, timeline_df: pd.DataFrame) -> pd.DataFrame:
        """
        Analyze sentiment across entire timeline
        
        Returns:
            DataFrame with original columns plus: sentiment, sentiment_score,
            positive_keywords, negative_keywords
        """
        logger.info("Analyzing sentiment across timeline...")
        
        if timeline_df.empty:
            logger.warning("Empty timeline provided")
            return timeline_df
        
        results = []
        
        for _, row in timeline_df.iterrows():
            subject = row.get('subject', '')
            
            if pd.isna(subject) or subject == '':
                sentiment_info = {
                    'sentiment': 'neutral',
                    'sentiment_score': 0.5,
                    'positive_keywords': [],
                    'negative_keywords': [],
                    'confidence': 0.0
                }
            else:
                sentiment_info = self.analyze_text(subject)
            
            # Combine original row with sentiment
            result = row.to_dict()
            result.update(sentiment_info)
            results.append(result)
        
        sentiment_df = pd.DataFrame(results)
        
        # Calculate sentiment statistics
        sentiment_counts = sentiment_df['sentiment'].value_counts()
        logger.info(f"Sentiment distribution: {sentiment_counts.to_dict()}")
        
        return sentiment_df
    
    def analyze_text(self, text: str) -> Dict:
        """
        Analyze sentiment of a single text
        
        Returns:
            Dict with sentiment, score, matched keywords, confidence
        """
        if not text or text.strip() == '':
            return {
                'sentiment': 'neutral',
                'sentiment_score': 0.5,
                'positive_keywords': [],
                'negative_keywords': [],
                'confidence': 0.0
            }
        
        text_lower = text.lower()
        
        # Find matches
        positive_matches = [kw for kw in self.positive_keywords if kw in text_lower]
        negative_matches = [kw for kw in self.negative_keywords if kw in text_lower]
        neutral_matches = [kw for kw in self.neutral_keywords if kw in text_lower]
        
        # Check for intensifiers
        has_intensifier = any(intensifier in text_lower for intensifier in self.intensifiers)
        intensifier_mult = 1.5 if has_intensifier else 1.0
        
        # Calculate scores
        pos_score = len(positive_matches) * intensifier_mult
        neg_score = len(negative_matches) * intensifier_mult
        
        # Determine sentiment
        if neg_score > pos_score:
            sentiment = 'negative'
            raw_score = neg_score / (pos_score + neg_score + 1)
            sentiment_score = 1.0 - raw_score  # Invert for 0-1 scale where 1 is positive
            confidence = min(1.0, neg_score / 3)
        elif pos_score > neg_score:
            sentiment = 'positive'
            raw_score = pos_score / (pos_score + neg_score + 1)
            sentiment_score = 0.5 + (raw_score * 0.5)  # 0.5 to 1.0 range
            confidence = min(1.0, pos_score / 3)
        else:
            sentiment = 'neutral'
            sentiment_score = 0.5
            confidence = min(1.0, len(neutral_matches) / 2) if neutral_matches else 0.3
        
        return {
            'sentiment': sentiment,
            'sentiment_score': round(sentiment_score, 3),
            'positive_keywords': positive_matches,
            'negative_keywords': negative_matches,
            'confidence': round(confidence, 3)
        }
    
    def get_sentiment_trends(
        self, 
        sentiment_df: pd.DataFrame,
        window_days: int = 30
    ) -> pd.DataFrame:
        """
        Calculate sentiment trends over time using rolling window
        
        Returns:
            DataFrame with date, avg_sentiment_score, positive_pct, 
            negative_pct, neutral_pct
        """
        if sentiment_df.empty:
            return pd.DataFrame()
        
        # Ensure date column is datetime
        df = sentiment_df.copy()
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        
        # Set date as index for rolling calculations
        df.set_index('date', inplace=True)
        
        # Resample to daily and forward fill
        daily = df.resample('D').agg({
            'sentiment_score': 'mean',
            'sentiment': lambda x: x.mode()[0] if len(x) > 0 else 'neutral'
        }).fillna(method='ffill')
        
        # Calculate rolling averages
        window = f'{window_days}D'
        trends = pd.DataFrame()
        trends['date'] = daily.index
        trends['avg_sentiment_score'] = daily['sentiment_score'].rolling(
            window=window, 
            min_periods=1
        ).mean()
        
        # Calculate sentiment percentages
        sentiment_counts = df.groupby(
            pd.Grouper(freq=window)
        )['sentiment'].value_counts(normalize=True).unstack(fill_value=0)
        
        if 'positive' in sentiment_counts.columns:
            trends = trends.merge(
                sentiment_counts[['positive']].rename(columns={'positive': 'positive_pct'}),
                left_on='date',
                right_index=True,
                how='left'
            )
        else:
            trends['positive_pct'] = 0
        
        if 'negative' in sentiment_counts.columns:
            trends = trends.merge(
                sentiment_counts[['negative']].rename(columns={'negative': 'negative_pct'}),
                left_on='date',
                right_index=True,
                how='left'
            )
        else:
            trends['negative_pct'] = 0
        
        if 'neutral' in sentiment_counts.columns:
            trends = trends.merge(
                sentiment_counts[['neutral']].rename(columns={'neutral': 'neutral_pct'}),
                left_on='date',
                right_index=True,
                how='left'
            )
        else:
            trends['neutral_pct'] = 0
        
        trends = trends.fillna(0)
        trends = trends.reset_index(drop=True)
        
        return trends
    
    def detect_sentiment_shifts(
        self,
        sentiment_df: pd.DataFrame,
        threshold: float = 0.3
    ) -> List[Dict]:
        """
        Detect significant sentiment shifts over time
        
        Args:
            sentiment_df: DataFrame with sentiment analysis
            threshold: Minimum score change to consider a shift
        
        Returns:
            List of sentiment shift events
        """
        if sentiment_df.empty or len(sentiment_df) < 2:
            return []
        
        shifts = []
        df = sentiment_df.sort_values('date').copy()
        
        # Calculate moving average with 7-day window
        df['sentiment_ma'] = df['sentiment_score'].rolling(
            window=7,
            min_periods=1
        ).mean()
        
        # Find significant changes
        for i in range(7, len(df)):
            prev_avg = df.iloc[i-7:i]['sentiment_ma'].mean()
            curr_avg = df.iloc[i]['sentiment_ma']
            
            change = curr_avg - prev_avg
            
            if abs(change) >= threshold:
                direction = 'improvement' if change > 0 else 'decline'
                
                shifts.append({
                    'date': df.iloc[i]['date'],
                    'direction': direction,
                    'magnitude': round(abs(change), 3),
                    'previous_score': round(prev_avg, 3),
                    'new_score': round(curr_avg, 3),
                    'subject': df.iloc[i].get('subject', 'N/A'),
                    'description': f"Sentiment {direction} of {abs(change):.1%}"
                })
        
        return shifts
    
    def get_sentiment_summary(self, sentiment_df: pd.DataFrame) -> str:
        """Generate human-readable sentiment summary"""
        if sentiment_df.empty:
            return "No sentiment data available."
        
        summary = []
        summary.append(f"\n{'='*70}")
        summary.append("SENTIMENT ANALYSIS SUMMARY")
        summary.append(f"{'='*70}\n")
        
        # Overall statistics
        total = len(sentiment_df)
        sentiment_counts = sentiment_df['sentiment'].value_counts()
        
        summary.append("Overall Sentiment Distribution:")
        for sentiment_type in ['positive', 'neutral', 'negative']:
            count = sentiment_counts.get(sentiment_type, 0)
            percentage = (count / total * 100) if total > 0 else 0
            summary.append(f"  {sentiment_type.title()}: {count} ({percentage:.1f}%)")
        
        # Average sentiment score
        avg_score = sentiment_df['sentiment_score'].mean()
        summary.append(f"\nAverage Sentiment Score: {avg_score:.2f} (0=negative, 1=positive)")
        
        # Most positive communication
        most_positive = sentiment_df.nlargest(1, 'sentiment_score')
        if not most_positive.empty:
            row = most_positive.iloc[0]
            summary.append(f"\nMost Positive Communication:")
            summary.append(f"  Date: {row['date'].strftime('%Y-%m-%d')}")
            summary.append(f"  Subject: {row.get('subject', 'N/A')}")
            summary.append(f"  Score: {row['sentiment_score']:.2f}")
        
        # Most negative communication
        most_negative = sentiment_df.nsmallest(1, 'sentiment_score')
        if not most_negative.empty:
            row = most_negative.iloc[0]
            summary.append(f"\nMost Negative Communication:")
            summary.append(f"  Date: {row['date'].strftime('%Y-%m-%d')}")
            summary.append(f"  Subject: {row.get('subject', 'N/A')}")
            summary.append(f"  Score: {row['sentiment_score']:.2f}")
        
        summary.append(f"\n{'='*70}\n")
        
        return '\n'.join(summary)
