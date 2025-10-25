"""
Interactive Streamlit Dashboard for Project Timeline Analysis
Real-time visualization and exploration of all detected patterns
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import networkx as nx
from pyvis.network import Network
import json
from pathlib import Path
from datetime import datetime
import tempfile

# Page configuration
st.set_page_config(
    page_title="Project Timeline Analysis",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .section-header {
        color: #2c3e50;
        border-bottom: 2px solid #3498db;
        padding-bottom: 0.5rem;
        margin-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Load all analysis outputs"""
    data = {}
    output_dir = Path("outputs")
    
    try:
        data['timeline'] = pd.read_csv(output_dir / "timeline.csv", parse_dates=['date'])
        data['participants'] = pd.read_csv(output_dir / "participant_stats.csv")
        data['bursts'] = pd.read_csv(output_dir / "collaboration_bursts.csv", parse_dates=['start', 'end'])
        
        # Optional files
        optional_files = {
            'milestones': 'milestones.csv',
            'phases': 'phase_transitions.csv',
            'sentiment': 'sentiment_timeline.csv',
            'influence': 'influence_scores.csv',
            'handoffs': 'handoffs.csv'
        }
        
        for key, filename in optional_files.items():
            filepath = output_dir / filename
            if filepath.exists():
                if key in ['milestones', 'phases', 'handoffs', 'sentiment']:
                    data[key] = pd.read_csv(filepath, parse_dates=['date'])
                else:
                    data[key] = pd.read_csv(filepath)
        
        # Load graph stats
        with open(output_dir / "graph_stats.json", 'r') as f:
            data['graph_stats'] = json.load(f)
        
        return data
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

def create_timeline_chart(timeline_df):
    """Create interactive timeline visualization"""
    fig = px.scatter(
        timeline_df,
        x='date',
        y='participant_count',
        color='type',
        size='participant_count',
        hover_data=['subject', 'participants'],
        title="Communication Timeline",
        labels={'participant_count': 'Participants', 'date': 'Date'},
        color_discrete_map={'email': '#ff7f0e', 'meeting': '#2ca02c'}
    )
    
    fig.update_traces(marker=dict(size=12, line=dict(width=1, color='white')))
    fig.update_layout(
        height=500,
        hovermode='closest',
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    return fig

def create_burst_timeline(timeline_df, burst_df):
    """Create timeline with burst highlighting"""
    fig = go.Figure()
    
    # Add all events
    fig.add_trace(go.Scatter(
        x=timeline_df['date'],
        y=timeline_df['participant_count'],
        mode='markers',
        name='Events',
        marker=dict(size=8, color='lightgray', opacity=0.5),
        hovertemplate='<b>%{hovertext}</b><br>Participants: %{y}<extra></extra>',
        hovertext=timeline_df['subject']
    ))
    
    # Highlight burst periods
    if not burst_df.empty:
        for _, burst in burst_df.iterrows():
            burst_events = timeline_df[
                (timeline_df['date'] >= burst['start']) &
                (timeline_df['date'] <= burst['end'])
            ]
            
            fig.add_trace(go.Scatter(
                x=burst_events['date'],
                y=burst_events['participant_count'],
                mode='markers',
                name=f"Burst ({burst['start'].date()})",
                marker=dict(size=12, color='red', symbol='star'),
                hovertemplate='<b>BURST</b><br>%{hovertext}<br>Participants: %{y}<extra></extra>',
                hovertext=burst_events['subject']
            ))
            
            # Add burst span
            fig.add_vrect(
                x0=burst['start'],
                x1=burst['end'],
                fillcolor="red",
                opacity=0.1,
                layer="below",
                line_width=0
            )
    
    fig.update_layout(
        title="Collaboration Bursts Highlighted",
        xaxis_title="Date",
        yaxis_title="Participants",
        height=500,
        hovermode='closest'
    )
    
    return fig

def create_participant_network(influence_df, timeline_df):
    """Create interactive network graph of participant collaborations"""
    if influence_df is None or influence_df.empty:
        return None
    
    # Create network
    net = Network(height="600px", width="100%", bgcolor="#ffffff", font_color="black")
    net.barnes_hut()
    
    # Add nodes (top 20 participants)
    top_participants = influence_df.head(20)
    
    for _, person in top_participants.iterrows():
        size = 10 + (person['influence_score'] * 500)
        
        # Color by role
        role_colors = {
            'Active Leader': '#e74c3c',
            'Strategic Leader': '#3498db',
            'Executor': '#2ecc71',
            'Contributor': '#95a5a6'
        }
        color = role_colors.get(person['role'], '#95a5a6')
        
        net.add_node(
            person['participant'],
            label=person['participant'].split('@')[0],
            title=f"{person['role']}<br>Influence: {person['influence_score']:.4f}<br>Events: {person['event_count']}",
            size=size,
            color=color
        )
    
    # Add edges (collaborations)
    top_emails = top_participants['participant'].tolist()
    
    for _, event in timeline_df.iterrows():
        participants = event.get('participants', [])
        # Create edges between all pairs in this event
        participants_in_top = [p for p in participants if p in top_emails]
        
        for i, p1 in enumerate(participants_in_top):
            for p2 in participants_in_top[i+1:]:
                try:
                    net.add_edge(p1, p2, value=1)
                except:
                    pass  # Edge may already exist
    
    # Save to temp file and read HTML
    with tempfile.NamedTemporaryFile(delete=False, suffix='.html', mode='w') as f:
        net.save_graph(f.name)
        with open(f.name, 'r') as html_file:
            html_content = html_file.read()
    
    return html_content

def main():
    # Header
    st.markdown('<div class="main-header">📊 Email+Calendar Graph System</div>', unsafe_allow_html=True)
    st.markdown("*Reconstructing project timelines through multi-agent reasoning*")
    
    # Load data
    with st.spinner('Loading analysis data...'):
        data = load_data()
    
    if data is None:
        st.error("❌ Could not load data. Please run `python src/main.py` first to generate analysis outputs.")
        return
    
    # Sidebar
    with st.sidebar:
        st.header("📋 Analysis Controls")
        
        # Date range filter
        min_date = data['timeline']['date'].min().date()
        max_date = data['timeline']['date'].max().date()
        
        date_range = st.date_input(
            "Date Range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )
        
        st.markdown("---")
        
        # Participant filter
        all_participants = sorted(data['participants']['email'].tolist())
        selected_participants = st.multiselect(
            "Filter Participants",
            options=all_participants,
            default=[]
        )
        
        st.markdown("---")
        
        # Export options
        st.subheader("📥 Export Data")
        if st.button("Download All CSV Files"):
            st.success("CSV files available in outputs/ directory")
    
    # Filter data based on selections
    filtered_timeline = data['timeline'].copy()
    if len(date_range) == 2:
        filtered_timeline = filtered_timeline[
            (filtered_timeline['date'].dt.date >= date_range[0]) &
            (filtered_timeline['date'].dt.date <= date_range[1])
        ]
    
    # Main tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 Overview",
        "🔥 Bursts",
        "🎯 Milestones",
        "📈 Phases",
        "💭 Sentiment",
        "🕸️ Network"
    ])
    
    # TAB 1: OVERVIEW
    with tab1:
        st.header("Project Overview")
        
        # Key metrics
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("Total Events", len(filtered_timeline))
        
        with col2:
            st.metric("Participants", len(data['participants']))
        
        with col3:
            st.metric("Email Threads", len(filtered_timeline[filtered_timeline['type'] == 'email']))
        
        with col4:
            st.metric("Meetings", len(filtered_timeline[filtered_timeline['type'] == 'meeting']))
        
        with col5:
            bursts_count = len(data['bursts']) if 'bursts' in data and not data['bursts'].empty else 0
            st.metric("Bursts Detected", bursts_count)
        
        # Timeline visualization
        st.subheader("📅 Communication Timeline")
        fig = create_timeline_chart(filtered_timeline)
        st.plotly_chart(fig, use_container_width=True)
        
        # Top participants
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("👥 Top 10 Participants")
            top_10 = data['participants'].head(10)[['email', 'organization', 'total_events']]
            st.dataframe(top_10, use_container_width=True)
        
        with col2:
            st.subheader("📊 Event Distribution")
            event_dist = filtered_timeline['type'].value_counts().reset_index()
            event_dist.columns = ['Type', 'Count']
            fig_pie = px.pie(event_dist, values='Count', names='Type', 
                            color_discrete_map={'email': '#ff7f0e', 'meeting': '#2ca02c'})
            st.plotly_chart(fig_pie, use_container_width=True)
    
    # TAB 2: BURSTS
    with tab2:
        st.header("🔥 Collaboration Bursts")
        
        if 'bursts' in data and not data['bursts'].empty:
            st.info(f"Detected {len(data['bursts'])} periods of intense collaboration")
            
            # Burst timeline
            fig_burst = create_burst_timeline(filtered_timeline, data['bursts'])
            st.plotly_chart(fig_burst, use_container_width=True)
            
            # Burst details
            st.subheader("Burst Details")
            for idx, burst in data['bursts'].iterrows():
                with st.expander(f"Burst #{idx+1}: {burst['start'].date()} - {burst['end'].date()}"):
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Events", int(burst['event_count']))
                    with col2:
                        st.metric("Participants", int(burst['participant_count']))
                    with col3:
                        st.metric("Duration (hrs)", f"{burst['duration_hours']:.1f}")
                    with col4:
                        st.metric("Confidence", f"{burst['confidence']:.2%}")
        else:
            st.warning("No collaboration bursts detected. Try running analysis with adaptive parameters.")
    
    # TAB 3: MILESTONES
    with tab3:
        st.header("🎯 Project Milestones")
        
        if 'milestones' in data and not data['milestones'].empty:
            # Milestone timeline
            fig_milestone = px.scatter(
                data['milestones'],
                x='date',
                y='confidence',
                color='type',
                size='participant_count',
                hover_data=['title', 'description'],
                title="Milestone Timeline",
                labels={'confidence': 'Confidence', 'date': 'Date'}
            )
            fig_milestone.update_traces(marker=dict(size=15, line=dict(width=1, color='white')))
            st.plotly_chart(fig_milestone, use_container_width=True)
            
            # Milestone breakdown
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Milestone Types")
                type_counts = data['milestones']['type'].value_counts().reset_index()
                type_counts.columns = ['Type', 'Count']
                st.bar_chart(type_counts.set_index('Type'))
            
            with col2:
                st.subheader("All Milestones")
                milestone_display = data['milestones'][['date', 'type', 'title', 'confidence']].copy()
                milestone_display['date'] = milestone_display['date'].dt.date
                milestone_display['confidence'] = milestone_display['confidence'].apply(lambda x: f"{x:.1%}")
                st.dataframe(milestone_display, use_container_width=True)
        else:
            st.info("No milestone data available. Milestones are detected from large meetings and deliverables.")
    
    # TAB 4: PHASES
    with tab4:
        st.header("📈 Phase Transitions")
        
        if 'phases' in data and not data['phases'].empty:
            # Phase flow
            st.subheader("Project Phase Evolution")
            
            phase_flow = data['phases'][['date', 'previous_phase', 'new_phase', 'confidence']].copy()
            phase_flow['date'] = phase_flow['date'].dt.date
            
            for idx, row in phase_flow.iterrows():
                col1, col2, col3 = st.columns([2, 1, 2])
                
                with col1:
                    st.markdown(f"**{row['previous_phase']}**")
                with col2:
                    st.markdown(f"➡️ *{row['date']}*")
                with col3:
                    st.markdown(f"**{row['new_phase']}** ({row['confidence']:.1%})")
                
                if idx < len(phase_flow) - 1:
                    st.markdown("---")
            
            # Phase keywords
            st.subheader("Phase Focus Areas")
            for _, phase in data['phases'].iterrows():
                with st.expander(f"{phase['date'].date()}: {phase['previous_phase']} → {phase['new_phase']}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**Previous Focus:**")
                        st.write(", ".join(phase['previous_keywords']))
                    
                    with col2:
                        st.markdown("**New Focus:**")
                        st.write(", ".join(phase['new_keywords']))
        else:
            st.info("No phase transition data available. Phases are detected through topic modeling of communication subjects.")
    
    # TAB 5: SENTIMENT
    with tab5:
        st.header("💭 Sentiment Analysis")
        
        if 'sentiment' in data and not data['sentiment'].empty:
            # Sentiment distribution
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Overall Sentiment")
                sentiment_counts = data['sentiment']['sentiment'].value_counts().reset_index()
                sentiment_counts.columns = ['Sentiment', 'Count']
                
                fig_sent = px.pie(
                    sentiment_counts,
                    values='Count',
                    names='Sentiment',
                    color='Sentiment',
                    color_discrete_map={'positive': '#2ecc71', 'neutral': '#95a5a6', 'negative': '#e74c3c'}
                )
                st.plotly_chart(fig_sent, use_container_width=True)
            
            with col2:
                st.subheader("Sentiment Statistics")
                avg_sentiment = data['sentiment']['sentiment_score'].mean()
                st.metric("Average Sentiment Score", f"{avg_sentiment:.2f}", 
                         help="Scale: 0 (negative) to 1 (positive)")
                
                positive_pct = (data['sentiment']['sentiment'] == 'positive').sum() / len(data['sentiment']) * 100
                neutral_pct = (data['sentiment']['sentiment'] == 'neutral').sum() / len(data['sentiment']) * 100
                negative_pct = (data['sentiment']['sentiment'] == 'negative').sum() / len(data['sentiment']) * 100
                
                st.write(f"✅ Positive: {positive_pct:.1f}%")
                st.write(f"⚪ Neutral: {neutral_pct:.1f}%")
                st.write(f"❌ Negative: {negative_pct:.1f}%")
            
            # Sentiment over time
            st.subheader("Sentiment Trend Over Time")
            sentiment_timeline = data['sentiment'].copy()
            sentiment_timeline['month'] = pd.to_datetime(sentiment_timeline['date']).dt.to_period('M').astype(str)
            
            monthly_sentiment = sentiment_timeline.groupby('month')['sentiment_score'].mean().reset_index()
            
            fig_trend = px.line(
                monthly_sentiment,
                x='month',
                y='sentiment_score',
                title="Monthly Average Sentiment",
                labels={'sentiment_score': 'Sentiment Score', 'month': 'Month'}
            )
            fig_trend.add_hline(y=0.5, line_dash="dash", line_color="gray", annotation_text="Neutral")
            st.plotly_chart(fig_trend, use_container_width=True)
        else:
            st.info("No sentiment data available. Sentiment is analyzed from communication subjects.")
    
    # TAB 6: NETWORK
    with tab6:
        st.header("🕸️ Collaboration Network")
        
        if 'influence' in data and not data['influence'].empty:
            # Influence rankings
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.subheader("Top 10 Influencers")
                top_influence = data['influence'].head(10)[['rank', 'participant', 'role', 'influence_score']].copy()
                top_influence['influence_score'] = top_influence['influence_score'].apply(lambda x: f"{x:.4f}")
                st.dataframe(top_influence, use_container_width=True)
                
                # Role distribution
                st.subheader("Role Distribution")
                role_dist = data['influence']['role'].value_counts().reset_index()
                role_dist.columns = ['Role', 'Count']
                st.bar_chart(role_dist.set_index('Role'))
            
            with col2:
                st.subheader("Interactive Network Graph")
                st.info("Showing top 20 participants. Node size = influence, Color = role")
                
                with st.spinner("Generating network visualization..."):
                    html_content = create_participant_network(data['influence'], data['timeline'])
                    
                    if html_content:
                        st.components.v1.html(html_content, height=600)
                    else:
                        st.warning("Could not generate network visualization")
        else:
            st.info("No influence data available. Influence is calculated using PageRank on the collaboration graph.")
        
        # Graph statistics
        if 'graph_stats' in data:
            st.subheader("📊 Graph Statistics")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Nodes", data['graph_stats']['total_nodes'])
            with col2:
                st.metric("Total Edges", data['graph_stats']['total_edges'])
            with col3:
                st.metric("Density", f"{data['graph_stats']['density']:.4f}")
            with col4:
                st.metric("Avg Degree", f"{data['graph_stats']['avg_degree']:.2f}")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #7f8c8d; padding: 1rem;'>
        <p>Built for Antler Hackathon - Track 9: Email+Calendar Graph System</p>
        <p>Reconstructing Project Timelines with Multi-Agent AI</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
