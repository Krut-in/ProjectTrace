# Next Steps: Milestone & Phase Detection Implementation

## Quick Reference for Next Features

### 1. Milestone Detection (30-45 minutes)

#### File: `src/analysis/milestone_detector.py`

```python
"""
Milestone detection module
Pattern-based identification of key project events
"""

import pandas as pd
from typing import List
from datetime import timedelta
from src.models.schemas import Milestone, CalendarEvent

class MilestoneDetector:
    """
    Detect project milestones from communication patterns
    
    Patterns:
    1. Decision Point: Large meeting → Email flurry → Calm
    2. Deliverable: Presentation keywords + follow-ups
    3. Planning Phase: Workshop → Intense activity
    """
    
    def __init__(
        self,
        large_meeting_threshold: int = 7,
        follow_up_window_hours: int = 48,
        min_follow_ups: int = 3
    ):
        self.large_meeting_threshold = large_meeting_threshold
        self.follow_up_window_hours = follow_up_window_hours
        self.min_follow_ups = min_follow_ups
    
    def detect_milestones(
        self,
        calendar_events: List[CalendarEvent],
        timeline_df: pd.DataFrame
    ) -> List[Milestone]:
        """Main detection method"""
        milestones = []
        
        # Pattern 1: Decision points
        milestones.extend(self._detect_decision_points(calendar_events, timeline_df))
        
        # Pattern 2: Deliverables
        milestones.extend(self._detect_deliverables(calendar_events, timeline_df))
        
        # Pattern 3: Planning phases
        milestones.extend(self._detect_planning_phases(calendar_events, timeline_df))
        
        return milestones
    
    def _detect_decision_points(self, calendar_events, timeline_df):
        """Pattern: Large meeting → activity → calm"""
        decision_points = []
        
        large_meetings = [
            e for e in calendar_events
            if len(e.attendees) >= self.large_meeting_threshold
        ]
        
        for meeting in large_meetings:
            # Count follow-up emails
            follow_ups = timeline_df[
                (timeline_df['date'] > meeting.start) &
                (timeline_df['date'] <= meeting.start + timedelta(hours=self.follow_up_window_hours)) &
                (timeline_df['type'] == 'email')
            ]
            
            # Check for calm period after
            calm_start = meeting.start + timedelta(hours=self.follow_up_window_hours)
            calm_events = timeline_df[
                (timeline_df['date'] > calm_start) &
                (timeline_df['date'] <= calm_start + timedelta(hours=72))
            ]
            
            if len(follow_ups) >= self.min_follow_ups and len(calm_events) <= 3:
                milestone = Milestone(
                    date=meeting.start,
                    event_id=meeting.uid,
                    event_type='meeting',
                    participants=meeting.attendees,
                    follow_up_count=len(follow_ups),
                    pattern_type='decision_point',
                    confidence=min(1.0, len(follow_ups) / 10),
                    description=f"Major decision: {meeting.summary}"
                )
                decision_points.append(milestone)
        
        return decision_points
```

#### Integration in `src/main.py`:

```python
# Add after burst detection
from src.analysis.milestone_detector import MilestoneDetector

logger.info("\n[4/5] Detecting project milestones...")
milestone_detector = MilestoneDetector(
    large_meeting_threshold=7,
    follow_up_window_hours=48,
    min_follow_ups=3
)
milestones = milestone_detector.detect_milestones(
    preprocessor.calendar_events,
    timeline_df
)

if milestones:
    milestone_df = pd.DataFrame([m.dict() for m in milestones])
    milestone_df.to_csv('outputs/milestones.csv', index=False)
    logger.info(f"✓ Detected {len(milestones)} milestones")
else:
    logger.warning("✗ No milestones detected")
```

---

### 2. Phase Transition Detection (45-60 minutes)

#### File: `src/analysis/phase_detector.py`

```python
"""
Phase transition detection using topic modeling
"""

import pandas as pd
from typing import List
from datetime import timedelta
from sklearn.feature_extraction.text import TfidfVectorizer
from src.models.schemas import PhaseTransition

class PhaseTransitionDetector:
    """
    Detect project phase transitions via topic shift analysis
    """
    
    def __init__(
        self,
        window_weeks: int = 3,
        similarity_threshold: float = 0.4,
        min_events_per_window: int = 5
    ):
        self.window_weeks = window_weeks
        self.similarity_threshold = similarity_threshold
        self.min_events_per_window = min_events_per_window
    
    def detect_transitions(self, timeline_df: pd.DataFrame) -> List[PhaseTransition]:
        """Main detection method"""
        if timeline_df.empty:
            return []
        
        # Create time windows
        windows = self._create_time_windows(timeline_df)
        
        # Extract topics per window
        window_topics = self._extract_window_topics(windows)
        
        # Identify transitions
        transitions = self._identify_transitions(window_topics)
        
        return transitions
    
    def _create_time_windows(self, timeline_df):
        """Create overlapping 3-week windows"""
        windows = []
        start_date = timeline_df['date'].min()
        end_date = timeline_df['date'].max()
        
        current = start_date
        while current < end_date:
            window_end = current + timedelta(weeks=self.window_weeks)
            window = timeline_df[
                (timeline_df['date'] >= current) &
                (timeline_df['date'] < window_end)
            ]
            
            if len(window) >= self.min_events_per_window:
                windows.append(window)
            
            current += timedelta(weeks=2)  # 50% overlap
        
        return windows
    
    def _extract_window_topics(self, windows):
        """Extract topics using TF-IDF"""
        window_topics = []
        
        for i, window in enumerate(windows):
            subjects = window['subject'].fillna('').tolist()
            
            if not subjects:
                continue
            
            vectorizer = TfidfVectorizer(
                max_features=15,
                stop_words='english',
                ngram_range=(1, 2),
                min_df=1
            )
            
            try:
                tfidf = vectorizer.fit_transform(subjects)
                keywords = vectorizer.get_feature_names_out()
                
                # Get top keywords
                mean_scores = tfidf.mean(axis=0).A1
                top_idx = mean_scores.argsort()[-10:][::-1]
                top_keywords = [keywords[idx] for idx in top_idx]
                
                window_topics.append({
                    'index': i,
                    'start': window['date'].min(),
                    'end': window['date'].max(),
                    'keywords': top_keywords,
                    'event_count': len(window)
                })
            except:
                continue
        
        return window_topics
    
    def _identify_transitions(self, window_topics):
        """Find topic shifts between windows"""
        transitions = []
        
        for i in range(1, len(window_topics)):
            prev = window_topics[i-1]
            curr = window_topics[i]
            
            # Calculate Jaccard similarity
            set1 = set(prev['keywords'])
            set2 = set(curr['keywords'])
            
            intersection = len(set1 & set2)
            union = len(set1 | set2)
            similarity = intersection / union if union > 0 else 0
            
            # Low similarity = phase shift
            if similarity < self.similarity_threshold:
                transition = PhaseTransition(
                    date=curr['start'],
                    old_topics=prev['keywords'][:5],
                    new_topics=curr['keywords'][:5],
                    similarity_score=similarity,
                    confidence=1 - similarity,
                    events_in_window=curr['event_count']
                )
                transitions.append(transition)
        
        return transitions
```

---

### 3. Interactive Dashboard (Optional - 45 minutes)

#### File: `src/visualization/dashboard.py`

```python
"""
Interactive Streamlit dashboard
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def main():
    st.set_page_config(page_title="Project Timeline Reconstruction", layout="wide")
    
    st.title("📊 Email+Calendar Graph System")
    st.markdown("*Reconstructing project timelines through multi-agent reasoning*")
    
    # Load data
    timeline = pd.read_csv('outputs/timeline.csv')
    timeline['date'] = pd.to_datetime(timeline['date'])
    
    participants = pd.read_csv('outputs/participant_stats.csv')
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Events", len(timeline))
    col2.metric("Participants", len(participants))
    col3.metric("Email Threads", len(timeline[timeline['type'] == 'email']))
    col4.metric("Meetings", len(timeline[timeline['type'] == 'meeting']))
    
    # Timeline
    st.subheader("📅 Project Timeline")
    fig = px.scatter(
        timeline,
        x='date',
        y='participant_count',
        color='type',
        hover_data=['subject'],
        title="Communication Events Over Time"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Top participants
    st.subheader("👥 Top Participants")
    fig2 = px.bar(
        participants.head(10),
        x='total_events',
        y='email',
        orientation='h',
        title="Most Active Participants"
    )
    st.plotly_chart(fig2, use_container_width=True)

if __name__ == "__main__":
    main()
```

**Run with**: `streamlit run src/visualization/dashboard.py`

---

## Testing Your Implementation

### Test Milestone Detection
```bash
python -c "
from src.data.preprocessor import DataPreprocessor
from src.analysis.milestone_detector import MilestoneDetector

preprocessor = DataPreprocessor(
    'Antler_Hackathon_Email_Data.json',
    'Antler_Hackathon_Calendar_Data.json'
)
email_df, calendar_df = preprocessor.load_data()
timeline_df = preprocessor.create_unified_timeline()

detector = MilestoneDetector()
milestones = detector.detect_milestones(
    preprocessor.calendar_events,
    timeline_df
)

print(f'Detected {len(milestones)} milestones')
for m in milestones:
    print(f'  - {m.date.date()}: {m.description}')
"
```

### Test Phase Detection
```bash
python -c "
from src.data.preprocessor import DataPreprocessor
from src.analysis.phase_detector import PhaseTransitionDetector

preprocessor = DataPreprocessor(
    'Antler_Hackathon_Email_Data.json',
    'Antler_Hackathon_Calendar_Data.json'
)
email_df, calendar_df = preprocessor.load_data()
timeline_df = preprocessor.create_unified_timeline()

detector = PhaseTransitionDetector()
transitions = detector.detect_transitions(timeline_df)

print(f'Detected {len(transitions)} phase transitions')
for t in transitions:
    print(f'  - {t.date.date()}: {t.old_topics[:3]} → {t.new_topics[:3]}')
"
```

---

## Expected Results

### Milestones
Based on the dataset, you should detect:
1. **September 7, 2022**: Brand strategy workshop (10 attendees)
2. **October 7, 2022**: Brand identity presentation (13 attendees)
3. **October 19, 2022**: Strategy presentation (15 attendees)

### Phase Transitions
Expected transitions:
1. **August → September 2022**: Kickoff → Active development
2. **October → November 2022**: Design → Iteration
3. **December 2022 → 2023**: Active → Maintenance

---

## Time Estimate

| Task | Time | Status |
|------|------|--------|
| Milestone detection code | 20 mins | 🟢 Ready |
| Milestone integration | 10 mins | 🟢 Ready |
| Phase detection code | 30 mins | 🟢 Ready |
| Phase integration | 15 mins | 🟢 Ready |
| Testing & refinement | 20 mins | 🟡 Needed |
| **Total** | **95 mins** | |

---

## Success Criteria

✅ Milestone detection finds 3+ events
✅ Phase detection identifies 2+ transitions
✅ All outputs have confidence scores
✅ Results exported to CSV
✅ Updated in summary report

---

## Quick Integration Checklist

- [ ] Create `src/analysis/milestone_detector.py`
- [ ] Create `src/analysis/phase_detector.py`
- [ ] Update `src/main.py` to call both detectors
- [ ] Update `generate_summary_report()` to include new results
- [ ] Test with provided dataset
- [ ] Adjust thresholds if needed
- [ ] Generate visualizations for milestones/phases
- [ ] Update documentation

---

**Ready to extend? Start with milestone detection - it's the easiest and gives immediate insights!** 🚀
