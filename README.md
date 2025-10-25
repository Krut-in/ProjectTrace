# 📊 Email+Calendar Graph System

**Production-Ready Multi-Agent Intelligence System for Project Timeline Reconstruction**

[![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)]()
[![Analysis](https://img.shields.io/badge/Analysis-Complete-blue)]()
[![Last Run](https://img.shields.io/badge/Last%20Run-Oct%2025%2C%202025-orange)]()

> Automatically reconstruct project timelines, detect collaboration patterns, identify milestones, and map influence networks from email and calendar data - all with **zero manual annotation**.

## 🎯 What This System Does

- **📅 Timeline Reconstruction**: Merges email and calendar data into unified timeline
- **🔥 Burst Detection**: Identifies collaboration intensity peaks (7 bursts detected)
- **🎯 Milestone Discovery**: Finds key project events automatically (8 milestones found)
- **🔄 Phase Mapping**: Tracks project evolution through phases (4 transitions mapped)
- **💬 Communication Analysis**: 12+ metrics per event including urgency, sentiment, patterns
- **🏆 Influence Scoring**: Ranks participants by network influence (42 people analyzed)
- **🤝 Handoff Detection**: Identifies team transitions and knowledge transfer points (38 events)

## ✨ Latest Analysis Results (Oct 25, 2025)

**Dataset Analyzed:**
- 📧 **47 events** (27 email threads + 20 meetings)
- 👥 **42 participants** across 5+ organizations
- 📅 **1,340 days** (Aug 2022 - Apr 2026)
- 🕸️ **956 connections** in network graph

**Key Findings:**
- ✅ **7 collaboration bursts** detected (avg 66% confidence)
- ✅ **8 milestones** identified (4 deliverables, 4 planning phases)
- ✅ **4 phase transitions** mapped (avg 80% confidence, 93% topic shifts)
- ✅ **44.7% positive sentiment** + 48.9% gratitude expressions
- ✅ **41.2% fast responses** (<24 hours)
- ✅ **12.8% crisis management** events detected

📊 **[See Complete Analysis →](ANALYSIS.md)** (1,593 lines of insights, methodologies, and findings)

---

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Clone repository (if not already done)
git clone https://github.com/Krut-in/ProjectTrace.git
cd ProjectTrace

# Make setup script executable
chmod +x setup.sh

# Run setup (creates directories and installs dependencies)
./setup.sh
```

### 2. Run Complete Analysis

```bash
# Activate virtual environment
source venv/bin/activate  # or source .venv/bin/activate

# Run the full analysis pipeline (~7 seconds)
python src/main.py
```

**Output**: 12 files in `outputs/` directory with complete analysis results

### 3. Launch Interactive Dashboard

```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Launch Streamlit dashboard
streamlit run src/visualization/dashboard.py
```

**Dashboard URL**: `http://localhost:8501`

**6 Interactive Tabs:**
- 📊 **Overview** - Timeline and key metrics
- 🔥 **Bursts** - Collaboration intensity peaks
- 🎯 **Milestones** - Key project events
- 🔄 **Phases** - Phase transitions and topic evolution
- 💬 **Sentiment** - Communication pattern analysis
- 🕸️ **Network** - Interactive collaboration graph

### 4. View Results

Check the `outputs/` directory for all analysis files:

```bash
ls -lh outputs/
```

**Generated Files:**
- 📄 `summary_report.txt` - Comprehensive 267-line report
- 📅 `timeline.csv` - 47 events with full metadata
- 🔥 `collaboration_bursts.csv` - 7 detected bursts
- 🎯 `milestones.csv` - 8 project milestones
- 🔄 `phase_transitions.csv` - 4 phase shifts
- 💬 `sentiment_timeline.csv` - 47 events with 12+ metrics each
- 📈 `sentiment_trends.csv` - Time-series aggregation
- 🏆 `influence_scores.csv` - 42 participants ranked
- 🤝 `handoffs.csv` - 38 team transition events
- 👥 `participant_stats.csv` - Engagement statistics
- 🕸️ `graph_stats.json` - Network metrics
- 📝 `analysis.log` - Detailed execution log

📊 **For in-depth analysis**: Read [ANALYSIS.md](ANALYSIS.md) - Complete breakdown of all outputs, methodologies, and findings.

---

## 🎨 System Features

### ✅ Phase 1: Core Intelligence (COMPLETE)

#### **1. Data Preprocessing**
- Robust JSON parsing with Pydantic validation
- Email thread and calendar event cleaning
- Timezone normalization (all UTC)
- Participant extraction and deduplication
- Graceful error handling (1 malformed thread handled)

#### **2. Multi-Layer Graph Construction**
- **Person nodes** (42) with organization metadata
- **Event nodes** (47) for emails and meetings
- **Temporal edges** (20) linking sequential events
- **Collaboration edges** (936) connecting participants to events
- Graph density: 0.1221 (healthy collaboration network)

#### **3. Adaptive Collaboration Burst Detection** ⭐
- **Innovation**: Dynamic parameter tuning based on data density
- Sliding window analysis (720 hours for sparse data)
- Detects intensity peaks with confidence scoring
- **Result**: 7 bursts vs. 0-1 with fixed parameters

#### **4. Milestone Detection** ⭐
- Pattern matching across 3 categories:
  - **Decision Points**: Large meetings + follow-ups + calm periods
  - **Deliverables**: Presentation/demo keywords + participation
  - **Planning Phases**: Workshops + subsequent activity
- Confidence scoring per milestone
- **Result**: 8 milestones (4 deliverables at 75% confidence)

#### **5. Phase Transition Detection** ⭐
- TF-IDF topic modeling with 30-day windows
- Jaccard similarity for transition detection (<0.4 = shift)
- Automatic phase naming from dominant keywords
- **Result**: 4 major transitions (avg 80% confidence)

#### **6. Multi-Dimensional Communication Analysis** ⭐⭐⭐
- Analyzes **12+ metrics** per event:
  - Urgency detection (25+ keywords)
  - Formality analysis (30+ markers)
  - Collaboration style (directive/balanced/collaborative)
  - Sentiment (40+ keywords)
  - Action items, gratitude, decision-making
  - Problem-solving, handoff language
  - Response time efficiency
- Uses **full email body text** (not just subjects)
- **Result**: 47 events analyzed with rich pattern detection

#### **7. Influence Mapping**
- PageRank on person-to-person collaboration subgraph
- Degree centrality and betweenness centrality
- Role classification (Leaders, Strategists, Executors, Contributors)
- **Result**: 42 participants ranked (9 executors, 33 contributors)

#### **8. Handoff Event Detection**
- Gap resumptions (14+ day silence)
- Team expansions (2+ new members)
- High turnover (>70% change)
- Departures (members leaving)
- **Result**: 38 handoff events detected

#### **9. Interactive Visualization Dashboard**
- Streamlit-based UI with 6 tabs
- Plotly interactive charts
- Pyvis network graph (force-directed layout)
- Real-time filtering and exploration
- Non-technical stakeholder access

---

## 📁 Project Structure

```
hackGraph/
├── src/
│   ├── main.py                       # Main execution pipeline (510 lines)
│   ├── data/
│   │   └── preprocessor.py           # Data loading & validation
│   ├── models/
│   │   ├── schemas.py                # Pydantic data models
│   │   └── graph_builder.py          # Multi-layer graph construction
│   ├── analysis/                     # 6 specialized analysis agents
│   │   ├── burst_detector.py         # Adaptive burst detection
│   │   ├── milestone_detector.py     # Pattern-based milestone finding
│   │   ├── phase_detector.py         # TF-IDF topic modeling
│   │   ├── sentiment_analyzer.py     # Multi-dimensional patterns
│   │   ├── influence_mapper.py       # PageRank & centrality
│   │   └── handoff_detector.py       # Team transition detection
│   └── visualization/
│       ├── dashboard.py              # Streamlit interactive UI
│       └── generate_plots.py         # Static plot generation
├── outputs/                          # All analysis results (generated)
│   ├── *.csv                         # 10 CSV files with analysis data
│   ├── graph_stats.json              # Network metrics
│   ├── summary_report.txt            # 267-line comprehensive report
│   ├── analysis.log                  # Execution log
│   └── graphs/
│       └── project_graph.json        # Exportable graph data
├── data/                             # Raw data directory
├── lib/                              # Dashboard dependencies (vis.js, tom-select)
├── Antler_Hackathon_Email_Data.json  # Email data (required)
├── Antler_Hackathon_Calendar_Data.json # Calendar data (required)
├── requirements.txt                  # Python dependencies
├── setup.sh                          # Automated setup script
├── demo.sh                           # Demo execution script
├── README.md                         # This file ← You are here
├── ANALYSIS.md                       # Complete analysis (1,593 lines) ⭐
├── IMPLEMENTATION_SUMMARY.md         # Technical implementation details
├── NEXT_STEPS.md                     # Future enhancement ideas
└── DASHBOARD_GUIDE.txt               # Dashboard usage guide
```

---

## 🔧 Configuration & Customization

### Burst Detection Parameters

Edit `src/analysis/burst_detector.py` to adjust sensitivity:

```python
burst_detector = CollaborationBurstDetector(
    adaptive=True,              # Enable adaptive parameter tuning
    window_hours=720,           # Time window (auto-adjusted if adaptive)
    min_events=3,               # Minimum events in window
    min_participants=2,         # Minimum participants
    max_participants=20         # Maximum participants
)
```

### Milestone Detection Thresholds

Adjust in `src/analysis/milestone_detector.py`:

```python
milestone_detector = MilestoneDetector(
    large_meeting_threshold=7,      # Participants for "large" meeting
    follow_up_window_hours=48,      # Time to check for follow-ups
    min_follow_ups=2,               # Minimum follow-up events
    deliverable_keywords=[...],     # Add custom keywords
    planning_keywords=[...]         # Add custom keywords
)
```

### Phase Transition Sensitivity

Configure in `src/analysis/phase_detector.py`:

```python
phase_detector = PhaseTransitionDetector(
    window_days=30,             # Window size for topic extraction
    similarity_threshold=0.4,   # Lower = more transitions detected
    min_events_per_window=2     # Minimum events to analyze
)
```

---

## 📊 Sample Output

### Console Output

```
============================================================
Email+Calendar Graph System - Analysis Pipeline
============================================================

[1/3] Loading and preprocessing data...
✓ Timeline: 47 events
✓ Participants: 42

Top 5 Most Active Participants:
  • terry.palmer@consultingco.com (Consultingco): 43 events
  • jamie.adams@startupco.com (Startupco): 29 events
  • hayden.moore@consultingco.com (Consultingco): 21 events

[2/3] Building project graph...
✓ Graph: 89 nodes, 956 edges
✓ Temporal connections: 20
✓ Graph density: 0.1221

[3/8] Detecting collaboration bursts...
✓ Detected 7 collaboration bursts

Top 3 Collaboration Bursts:
  • 2022-08-05: 5 events, 13 participants (confidence: 0.70)
  • 2022-10-19: 7 events, 19 participants (confidence: 0.69)
  • 2022-11-10: 4 events, 12 participants (confidence: 0.64)

[4/8] Detecting project milestones...
✓ Detected 8 milestones

[5/8] Detecting phase transitions...
✓ Detected 4 phase transitions

Phase Transitions:
  • 2022-08-22: Design → Planning
  • 2023-01-04: Design → Scoping
  • 2023-09-15: Small Favor → Opinion Important
  • 2024-06-07: Opinion Important → Design

[6/8] Analyzing sentiment...
✓ Pattern analysis complete: {'routine': 32, 'crisis_management': 6, 'problem_solving': 5}
✓ Urgency distribution: {'low': 28, 'medium': 10, 'high': 9}

[7/8] Calculating influence scores...
✓ Calculated influence for 42 participants

[8/8] Detecting handoff events...
✓ Detected 38 handoff events

✅ Analysis complete!
============================================================
```

---

## 🛠️ Technology Stack

### Core Libraries

| Category | Libraries | Purpose |
|----------|-----------|---------|
| **Data Processing** | pandas, numpy, python-dateutil | Data manipulation & analysis |
| **Graph Analysis** | networkx | Graph construction & algorithms |
| **Validation** | pydantic | Data validation & schemas |
| **NLP** | scikit-learn | TF-IDF topic modeling |
| **Visualization** | streamlit, plotly, pyvis | Interactive dashboards & charts |
| **Utilities** | logging, pathlib, json | System utilities |

### Python Version

- **Required**: Python 3.8+
- **Tested on**: Python 3.13.5

### Dependencies

See `requirements.txt` for complete list. Key dependencies:
- `networkx>=3.0`
- `pandas>=2.0.0`
- `pydantic>=2.0.0`
- `streamlit>=1.28.0`
- `scikit-learn>=1.3.0`

---

## 🔍 Advanced Usage

### Export Graph for External Visualization

The graph is automatically exported to `outputs/graphs/project_graph.json`. Import into:

- **[Gephi](https://gephi.org/)** - Professional graph visualization
- **[Cytoscape](https://cytoscape.org/)** - Network analysis
- **D3.js / vis.js** - Web-based visualization
- **NetworkX** - Python graph analysis

### Custom Analysis Script

```python
from src.data.preprocessor import DataPreprocessor
from src.models.graph_builder import ProjectGraph
from src.analysis.burst_detector import CollaborationBurstDetector

# Load data
preprocessor = DataPreprocessor(
    email_path='Antler_Hackathon_Email_Data.json',
    calendar_path='Antler_Hackathon_Calendar_Data.json'
)
email_df, calendar_df = preprocessor.load_data()
timeline_df = preprocessor.create_unified_timeline()

# Build graph
graph_builder = ProjectGraph()
G = graph_builder.build_graph(
    preprocessor.emails,
    preprocessor.calendar_events
)

# Custom analysis
import networkx as nx
pagerank = nx.pagerank(G)
communities = nx.community.louvain_communities(G)

# Run burst detection with custom parameters
burst_detector = CollaborationBurstDetector(
    window_hours=168,  # 7 days
    min_events=3
)
bursts = burst_detector.detect_bursts(timeline_df)
```

### Programmatic Access to Results

```python
import pandas as pd
import json

# Load analysis results
timeline = pd.read_csv('outputs/timeline.csv')
bursts = pd.read_csv('outputs/collaboration_bursts.csv')
milestones = pd.read_csv('outputs/milestones.csv')
sentiment = pd.read_csv('outputs/sentiment_timeline.csv')

with open('outputs/graph_stats.json') as f:
    graph_stats = json.load(f)

# Analyze
print(f"Total events: {len(timeline)}")
print(f"Average burst confidence: {bursts['confidence'].mean():.2f}")
print(f"Positive sentiment: {(sentiment['sentiment']=='positive').sum()}")
```

---

## 📝 Future Enhancement Ideas

### 1. **Sentiment Deep Dive**
- Track sentiment changes over time per person
- Detect frustration/enthusiasm patterns
- Correlation with project phases

### 2. **Predictive Analytics**
- Forecast next collaboration burst
- Predict milestone completion dates
- Identify at-risk projects early

### 3. **Blocker Identification**
- Detect recurring issues without resolution
- Topic clustering + temporal persistence
- Auto-flag blockers for project managers

### 4. **Comparative Analysis**
- Benchmark against similar projects
- Industry-standard collaboration patterns
- Best practice identification

### 5. **Real-Time Monitoring**
- Incremental updates as new emails/meetings arrive
- Live dashboard with alerts
- Scheduled analysis runs

### 6. **Integration APIs**
- REST API for programmatic access
- Webhook notifications for key events
- Export to project management tools

---

## ⚠️ Error Handling & Robustness

### Built-In Safeguards

- ✅ **Pydantic validation** - Data integrity checks
- ✅ **Try-except blocks** - Comprehensive error catching
- ✅ **Logging** - INFO/WARNING/ERROR levels
- ✅ **Graceful degradation** - Analysis continues if components fail
- ✅ **Empty result handling** - No crashes on missing data

### Common Issues & Solutions

**Issue**: No collaboration bursts detected  
**Solution**: Lower `min_events` threshold or adjust `window_hours`

**Issue**: File not found error  
**Solution**: Ensure JSON files are in project root directory

**Issue**: Import errors  
**Solution**: Run `./setup.sh` again or `pip install -r requirements.txt`

**Issue**: Streamlit command not found  
**Solution**: Activate virtual environment first (`source venv/bin/activate`)

**Issue**: Dashboard not loading  
**Solution**: Check port 8501 is available, or use `streamlit run src/visualization/dashboard.py --server.port 8502`

---

## 📄 Documentation Files

| File | Purpose | Lines |
|------|---------|-------|
| `README.md` | This file - Quick start & features | ~400 |
| `ANALYSIS.md` | Complete analysis report & insights | 1,593 |
| `IMPLEMENTATION_SUMMARY.md` | Technical implementation details | ~470 |
| `NEXT_STEPS.md` | Future enhancement ideas | ~440 |
| `DASHBOARD_GUIDE.txt` | Dashboard usage instructions | ~100 |

---

## 🎉 Production Ready!

### System Capabilities

✅ **Automated Analysis** - Zero manual annotation required  
✅ **Traceability** - All inferences reference source events  
✅ **Explainability** - Confidence scores and reasoning included  
✅ **Multi-Agent Architecture** - 6 specialized analysis agents  
✅ **Production-Ready** - Comprehensive error handling  
✅ **Extensible** - Easy to add new detection patterns  
✅ **Fast Execution** - ~7 seconds for complete analysis  
✅ **Interactive UI** - Streamlit dashboard for stakeholders

### Performance Metrics

- **Execution Time**: ~7 seconds (47 events)
- **Scalability**: Linear O(n) for most algorithms
- **Memory**: <100 MB for this dataset
- **Accuracy**: 66-80% confidence on detections

### Use Cases

- 📊 **Consulting Firms** - Analyze client engagement patterns
- 🏢 **Project Management** - Monitor team collaboration health
- 💼 **Executive Dashboards** - Track communication efficiency
- 🔍 **HR Analytics** - Understand team dynamics
- 📈 **Research** - Study communication patterns

---

## 🏆 Antler Hackathon - Track 9

This implementation was built for the **Antler Hackathon - Track 9: Email+Calendar Graph System**

### Requirements Met

- ✅ **Traceability**: All inferences reference source events
- ✅ **Explainability**: Confidence scores and reasoning included
- ✅ **Multi-step Processing**: Planning → Parsing → Linking → Reasoning
- ✅ **Production-Ready**: Comprehensive error handling & logging
- ✅ **Extensible**: Modular architecture for easy additions

### Development Time

- **Phase 1 (Graph + Burst Detection)**: 3-4 hours
- **Phase 2 (6 Analysis Agents)**: 6-8 hours
- **Phase 3 (Dashboard + Docs)**: 4-6 hours
- **Total**: ~15-18 hours

---

## 📄 License

MIT License - Feel free to use, modify, and distribute!

---

## 🙏 Acknowledgments

- **Antler Hackathon** for the challenge
- **NetworkX** for graph algorithms
- **Streamlit** for rapid dashboard development
- **Pydantic** for data validation

---

## 📞 Contact & Support

- **Repository**: [github.com/Krut-in/ProjectTrace](https://github.com/Krut-in/ProjectTrace)
- **Issues**: Open an issue on GitHub
- **Documentation**: See ANALYSIS.md for comprehensive details

---

**🚀 Ready to analyze your project communications? Run `python src/main.py` to get started!**

*Last Updated: October 25, 2025*  
*Version: 2.0 (Production Release)*
