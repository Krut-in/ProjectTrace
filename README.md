# Email+Calendar Graph System

Production-ready multi-agent system for reconstructing project timelines from communication data.

## 🚀 Quick Start

### 1. Setup

```bash
# Make setup script executable
chmod +x setup.sh

# Run setup (creates directories and installs dependencies)
./setup.sh
```

### 2. Run Analysis

```bash
# Activate virtual environment
source venv/bin/activate

# Run the analysis pipeline
python src/main.py
```

### 3. Launch Interactive Dashboard

```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Launch Streamlit dashboard
streamlit run src/visualization/dashboard.py
```

Then open your browser to `http://localhost:8501` to explore the interactive dashboard with 6 tabs:

- **Overview:** Timeline and key metrics
- **Bursts:** Collaboration burst detection
- **Milestones:** Key project events
- **Phases:** Phase transitions
- **Sentiment:** Sentiment analysis
- **Network:** Interactive collaboration graph

### 4. View Results

Check the `outputs/` directory for analysis results:

- `summary_report.txt` - Comprehensive analysis report
- `timeline.csv` - Unified event timeline
- `collaboration_bursts.csv` - Detected collaboration bursts
- `milestones.csv` - Project milestones and deliverables
- `phase_transitions.csv` - Project phase shifts
- `sentiment_timeline.csv` - Sentiment analysis per event
- `influence_scores.csv` - Participant influence rankings
- `handoffs.csv` - Team handoff events
- `participant_stats.csv` - Participant engagement statistics
- `graph_stats.json` - Graph network statistics
- `visualizations/*.png` - Timeline, bursts, participants charts
- `analysis.log` - Detailed execution log

📊 **For detailed analysis and insights, see [ANALYSIS.md](ANALYSIS.md)** - A comprehensive breakdown of all outputs, methodologies, and findings.

## 📁 Project Structure

```
hackGraph/
├── src/
│   ├── data/
│   │   └── preprocessor.py          # Data loading and cleaning
│   ├── models/
│   │   ├── schemas.py                # Pydantic data models
│   │   └── graph_builder.py          # Multi-layer graph construction
│   ├── analysis/
│   │   └── burst_detector.py         # Collaboration burst detection
│   └── main.py                       # Main execution pipeline
├── outputs/                          # Analysis results (generated)
├── Antler_Hackathon_Email_Data.json  # Email data (required)
├── Antler_Hackathon_Calendar_Data.json # Calendar data (required)
├── requirements.txt                  # Python dependencies
├── setup.sh                          # Setup script
└── README.md                         # This file
```

## ✨ Features Implemented

### Phase 1 (Current)

✅ **Data Preprocessing**

- Robust JSON parsing with Pydantic validation
- Email and calendar data cleaning
- Unified timeline generation
- Participant extraction and statistics

✅ **Multi-Layer Graph Construction**

- Person nodes with organization metadata
- Event nodes (emails and meetings)
- Temporal proximity edges (events within 48 hours)
- Collaboration edges (person-to-person)
- Graph export in multiple formats (JSON, GEXF, GraphML)

✅ **Collaboration Burst Detection**

- Sliding window analysis (48-hour windows)
- Detects 8+ events with 3-8 participants
- Confidence scoring based on:
  - Event density
  - Participant balance (Gini coefficient)
  - Communication type diversity
- Duplicate detection and removal

### Phase 2 (Next Steps)

🔄 **Milestone Detection** (Ready to implement)

- Large meeting → email flurry → calm pattern
- Presentation and deliverable identification
- Planning phase detection

🔄 **Phase Transition Detection** (Ready to implement)

- Topic modeling with TF-IDF
- Keyword clustering over time windows
- Phase shift identification

## 🎯 Key Insights

### Project Overview

- **Timeline**: August 2022 - September 2025 (3+ years)
- **Project**: ConsultingCo → StartupCo brand strategy and identity
- **Key Players**:
  - Terry Palmer (ConsultingCo CEO)
  - Jamie Adams (StartupCo CEO)
  - Multiple team rotations

### Communication Patterns

- Early intensive collaboration (Aug-Nov 2022)
- Multiple design iteration phases
- Long-term maintenance relationship
- Consistent 1-on-1 check-ins between executives

## 🔧 Configuration

### Burst Detection Parameters

Edit `src/main.py` to adjust detection sensitivity:

```python
burst_detector = CollaborationBurstDetector(
    window_hours=48,        # Time window for burst detection
    min_events=8,           # Minimum events in window
    min_participants=3,     # Minimum participants
    max_participants=8      # Maximum participants
)
```

## 📊 Sample Output

```
[GRAPH STATISTICS]
Total Nodes: 45
Total Edges: 328
People: 25
Events: 20
Graph Density: 0.1637

[TOP PARTICIPANTS]
1. jamie.adams@StartupCo.com        | StartupCo      | 18 events
2. terry.palmer@ConsultingCo.com    | ConsultingCo   | 16 events
3. kelly.underwood@ConsultingCo.com | ConsultingCo   | 12 events

[COLLABORATION BURSTS]
Burst #1:
  Period: 2022-09-05 to 2022-09-20
  Duration: 360.5 hours
  Events: 12 (7 emails, 5 meetings)
  Participants: 6
  Confidence: 0.78
```

## 🛠️ Tech Stack

- **Data Processing**: pandas, numpy
- **Graph Analysis**: networkx
- **Validation**: pydantic
- **NLP**: scikit-learn, sentence-transformers
- **Visualization**: plotly, matplotlib, seaborn

## 🔍 Advanced Usage

### Export Graph for Visualization

The graph is automatically exported to `outputs/graphs/project_graph.json` and can be visualized using:

- [Gephi](https://gephi.org/) (import GEXF format)
- [Cytoscape](https://cytoscape.org/)
- D3.js or vis.js for web visualization

### Custom Analysis

```python
from src.data.preprocessor import DataPreprocessor
from src.models.graph_builder import ProjectGraph

# Load data
preprocessor = DataPreprocessor(
    email_path='Antler_Hackathon_Email_Data.json',
    calendar_path='Antler_Hackathon_Calendar_Data.json'
)
email_df, calendar_df = preprocessor.load_data()

# Build graph
graph_builder = ProjectGraph()
G = graph_builder.build_graph(
    preprocessor.emails,
    preprocessor.calendar_events
)

# Custom analysis
person_subgraph = graph_builder.get_subgraph(['person'])
# Run PageRank, community detection, etc.
```

## 📝 Next Stage Ideas

### 1. Sentiment Tracking

- Analyze email tone changes over time
- Detect frustration spikes
- Implementation: sentence-transformers for semantic analysis

### 2. Influence Mapping

- PageRank on collaboration graph
- Distinguish decision-makers from executors
- Implementation: `nx.pagerank(G)` on person-person subgraph

### 3. Handoff Event Detection

- Pattern: New participant + context shift
- Look for "adding [name]" in communications
- Implementation: Regex + participant set difference

### 4. Blocker Identification

- Same issue across 3+ communications without resolution
- Implementation: Topic clustering + temporal persistence

### 5. Communication Health Dashboard

- Response time trends
- Meeting-to-email ratio
- Participant balance metrics
- Implementation: Streamlit + Plotly

## ⚠️ Error Handling

All modules include:

- Pydantic validation for data integrity
- Comprehensive try-except blocks
- Detailed logging (INFO/WARNING/ERROR levels)
- Graceful degradation (analysis continues if one component fails)

## 🚨 Troubleshooting

**Issue**: No collaboration bursts detected

- **Solution**: Lower `min_events` threshold in `src/main.py`

**Issue**: File not found error

- **Solution**: Ensure JSON files are in project root directory

**Issue**: Import errors

- **Solution**: Run `./setup.sh` again or `pip install -r requirements.txt`

## 📄 License

MIT License - Feel free to use for hackathons and beyond!

## 🎉 Hackathon Ready!

This implementation is designed for the **Antler Hackathon - Track 9: Email+Calendar Graph System**

- ✅ Traceability: All inferences reference source events
- ✅ Explainability: Confidence scores and reasoning included
- ✅ Multi-step processing: Planning → Parsing → Linking → Reasoning
- ✅ Production-ready: Comprehensive error handling
- ✅ Extensible: Easy to add milestone/phase detection

**Time to implement**: ~3-4 hours (as planned!)
