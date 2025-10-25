"""
Main execution pipeline for Email+Calendar Graph System
"""

import sys
import logging
from pathlib import Path
import json
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data.preprocessor import DataPreprocessor
from src.models.graph_builder import ProjectGraph
from src.analysis.burst_detector import CollaborationBurstDetector
from src.analysis.milestone_detector import MilestoneDetector
from src.analysis.phase_detector import PhaseTransitionDetector
from src.analysis.sentiment_analyzer import SentimentAnalyzer
from src.analysis.influence_mapper import InfluenceMapper
from src.analysis.handoff_detector import HandoffDetector

# Setup logging
log_dir = Path("outputs")
log_dir.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('outputs/analysis.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def main():
    """Main execution pipeline"""
    try:
        logger.info("="*60)
        logger.info("Email+Calendar Graph System - Analysis Pipeline")
        logger.info("="*60)
        
        # Create output directories
        output_dirs = ['outputs/graphs', 'outputs/reports', 'outputs/visualizations']
        for dir_path in output_dirs:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
        
        # 1. Data Preprocessing
        logger.info("\n[1/3] Loading and preprocessing data...")
        preprocessor = DataPreprocessor(
            email_path='Antler_Hackathon_Email_Data.json',
            calendar_path='Antler_Hackathon_Calendar_Data.json'
        )
        
        email_df, calendar_df = preprocessor.load_data()
        timeline_df = preprocessor.create_unified_timeline()
        participant_stats = preprocessor.get_participant_statistics()
        
        # Save preprocessed data
        timeline_df.to_csv('outputs/timeline.csv', index=False)
        participant_stats.to_csv('outputs/participant_stats.csv', index=False)
        logger.info(f"✓ Timeline: {len(timeline_df)} events")
        logger.info(f"✓ Participants: {len(participant_stats)}")
        
        # Display top participants
        logger.info("\nTop 5 Most Active Participants:")
        for _, row in participant_stats.head(5).iterrows():
            logger.info(f"  • {row['email']} ({row['organization']}): "
                       f"{row['total_events']} events")
        
        # 2. Build Graph
        logger.info("\n[2/3] Building project graph...")
        graph_builder = ProjectGraph()
        G = graph_builder.build_graph(
            preprocessor.emails,
            preprocessor.calendar_events
        )
        
        # Save graph statistics
        graph_stats = graph_builder.get_statistics()
        with open('outputs/graph_stats.json', 'w') as f:
            json.dump(graph_stats, f, indent=2)
        
        # Export graph
        graph_builder.export_graph('outputs/graphs/project_graph.json', format='json')
        logger.info(f"✓ Graph: {graph_stats['total_nodes']} nodes, "
                   f"{graph_stats['total_edges']} edges")
        logger.info(f"✓ Temporal connections: {graph_stats['temporal_edges']}")
        logger.info(f"✓ Graph density: {graph_stats['density']:.4f}")
        
        # 3. Detect Collaboration Bursts (with adaptive parameters)
        logger.info("\n[3/8] Detecting collaboration bursts...")
        burst_detector = CollaborationBurstDetector(
            adaptive=True,
            timeline_df=timeline_df
        )
        bursts = burst_detector.detect_bursts(timeline_df)
        burst_summary = burst_detector.get_burst_summary(bursts)
        
        if not burst_summary.empty:
            burst_summary.to_csv('outputs/collaboration_bursts.csv', index=False)
            logger.info(f"✓ Detected {len(bursts)} collaboration bursts")
            
            # Display top 3 bursts
            logger.info("\nTop 3 Collaboration Bursts:")
            for _, burst in burst_summary.head(3).iterrows():
                logger.info(f"  • {burst['start'].date()}: {burst['event_count']} events, "
                           f"{burst['participant_count']} participants "
                           f"(confidence: {burst['confidence']:.2f})")
        else:
            logger.warning("✗ No collaboration bursts detected")
        
        # 4. Detect Milestones
        logger.info("\n[4/8] Detecting project milestones...")
        milestone_detector = MilestoneDetector()
        milestone_df = milestone_detector.detect_milestones(
            preprocessor.calendar_events,
            timeline_df
        )
        
        if not milestone_df.empty:
            milestone_df.to_csv('outputs/milestones.csv', index=False)
            logger.info(f"✓ Detected {len(milestone_df)} milestones")
            
            # Display top 3 milestones
            logger.info("\nTop 3 Milestones:")
            for _, milestone in milestone_df.head(3).iterrows():
                logger.info(f"  • {milestone['date'].date()} [{milestone['type']}]: "
                           f"{milestone['title']}")
        else:
            logger.warning("✗ No milestones detected")
        
        # 5. Detect Phase Transitions
        logger.info("\n[5/8] Detecting phase transitions...")
        phase_detector = PhaseTransitionDetector()
        phase_df = phase_detector.detect_transitions(timeline_df)
        
        if not phase_df.empty:
            phase_df.to_csv('outputs/phase_transitions.csv', index=False)
            logger.info(f"✓ Detected {len(phase_df)} phase transitions")
            
            # Display transitions
            logger.info("\nPhase Transitions:")
            for _, phase in phase_df.iterrows():
                logger.info(f"  • {phase['date'].date()}: "
                           f"{phase['previous_phase']} → {phase['new_phase']}")
        else:
            logger.warning("✗ No phase transitions detected")
        
        # 6. Analyze Sentiment
        logger.info("\n[6/8] Analyzing sentiment...")
        sentiment_analyzer = SentimentAnalyzer()
        sentiment_df = sentiment_analyzer.analyze_timeline(timeline_df)
        
        if not sentiment_df.empty:
            # Save full sentiment data
            sentiment_df.to_csv('outputs/sentiment_timeline.csv', index=False)
            
            # Calculate sentiment trends
            sentiment_trends = sentiment_analyzer.get_sentiment_trends(sentiment_df)
            if not sentiment_trends.empty:
                sentiment_trends.to_csv('outputs/sentiment_trends.csv', index=False)
            
            # Get statistics
            sentiment_counts = sentiment_df['sentiment'].value_counts()
            logger.info(f"✓ Sentiment analysis complete: {sentiment_counts.to_dict()}")
        else:
            logger.warning("✗ Sentiment analysis failed")
        
        # 7. Calculate Influence Scores
        logger.info("\n[7/8] Calculating influence scores...")
        influence_mapper = InfluenceMapper()
        influence_df = influence_mapper.calculate_influence(G, timeline_df)
        
        if not influence_df.empty:
            influence_df.to_csv('outputs/influence_scores.csv', index=False)
            logger.info(f"✓ Calculated influence for {len(influence_df)} participants")
            
            # Display top 5 influencers
            logger.info("\nTop 5 Influencers:")
            for _, person in influence_df.head(5).iterrows():
                logger.info(f"  • {person['participant']} [{person['role']}]: "
                           f"score={person['influence_score']:.4f}")
        else:
            logger.warning("✗ Influence calculation failed")
        
        # 8. Detect Handoffs
        logger.info("\n[8/8] Detecting handoff events...")
        handoff_detector = HandoffDetector()
        handoff_df = handoff_detector.detect_handoffs(timeline_df)
        
        if not handoff_df.empty:
            handoff_df.to_csv('outputs/handoffs.csv', index=False)
            logger.info(f"✓ Detected {len(handoff_df)} handoff events")
            
            # Display top 3 handoffs
            logger.info("\nTop 3 Handoffs:")
            for _, handoff in handoff_df.head(3).iterrows():
                logger.info(f"  • {handoff['date'].date()} [{handoff['handoff_type']}]: "
                           f"{handoff['new_count']} joined, {handoff['departed_count']} left")
        else:
            logger.warning("✗ No handoffs detected")
        
        # Generate summary report
        logger.info("\nGenerating comprehensive summary report...")
        generate_summary_report(
            graph_stats,
            participant_stats,
            burst_summary,
            timeline_df,
            milestone_df if not milestone_df.empty else None,
            phase_df if not phase_df.empty else None,
            sentiment_df if not sentiment_df.empty else None,
            influence_df if not influence_df.empty else None,
            handoff_df if not handoff_df.empty else None
        )
        
        logger.info("\n" + "="*60)
        logger.info("✅ Analysis complete!")
        logger.info("="*60)
        logger.info("\nOutput files created:")
        logger.info("  • outputs/timeline.csv - Unified event timeline")
        logger.info("  • outputs/participant_stats.csv - Participant statistics")
        logger.info("  • outputs/graph_stats.json - Graph network statistics")
        logger.info("  • outputs/graphs/project_graph.json - Graph data export")
        logger.info("  • outputs/collaboration_bursts.csv - Detected bursts")
        logger.info("  • outputs/milestones.csv - Project milestones")
        logger.info("  • outputs/phase_transitions.csv - Phase transitions")
        logger.info("  • outputs/sentiment_timeline.csv - Sentiment analysis")
        logger.info("  • outputs/sentiment_trends.csv - Sentiment trends")
        logger.info("  • outputs/influence_scores.csv - Influence rankings")
        logger.info("  • outputs/handoffs.csv - Handoff events")
        logger.info("  • outputs/summary_report.txt - Comprehensive summary")
        logger.info("  • outputs/analysis.log - Detailed execution log")
        
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        logger.error("Make sure the JSON data files are in the project root directory")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


def generate_summary_report(
    graph_stats: dict,
    participant_stats,
    burst_summary,
    timeline_df,
    milestone_df=None,
    phase_df=None,
    sentiment_df=None,
    influence_df=None,
    handoff_df=None
):
    """Generate comprehensive summary report"""
    report = []
    report.append("="*70)
    report.append("     EMAIL+CALENDAR GRAPH SYSTEM - ANALYSIS REPORT")
    report.append("="*70)
    report.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Project Overview
    report.append("\n" + "─"*70)
    report.append("PROJECT OVERVIEW")
    report.append("─"*70)
    report.append(f"Timeline Span: {timeline_df['date'].min().date()} to {timeline_df['date'].max().date()}")
    report.append(f"Total Duration: {(timeline_df['date'].max() - timeline_df['date'].min()).days} days")
    report.append(f"Total Events: {len(timeline_df)}")
    report.append(f"  • Email Threads: {len(timeline_df[timeline_df['type'] == 'email'])}")
    report.append(f"  • Meetings: {len(timeline_df[timeline_df['type'] == 'meeting'])}")
    
    # Graph Statistics
    report.append("\n" + "─"*70)
    report.append("GRAPH NETWORK STATISTICS")
    report.append("─"*70)
    report.append(f"Total Nodes: {graph_stats['total_nodes']}")
    report.append(f"  • People: {graph_stats['person_nodes']}")
    report.append(f"  • Events: {graph_stats['event_nodes']}")
    report.append(f"Total Edges: {graph_stats['total_edges']}")
    report.append(f"  • Temporal Links: {graph_stats['temporal_edges']}")
    report.append(f"Graph Density: {graph_stats['density']:.4f}")
    report.append(f"Average Degree: {graph_stats['avg_degree']:.2f}")
    
    # Top Participants
    report.append("\n" + "─"*70)
    report.append("TOP PARTICIPANTS (by activity)")
    report.append("─"*70)
    top_participants = participant_stats.head(10)
    for idx, row in top_participants.iterrows():
        report.append(
            f"{idx+1:2d}. {row['email']:40s} | {row['organization']:15s} | "
            f"{row['total_events']:3d} events ({row['email_threads']:2d}E, {row['meetings']:2d}M)"
        )
    
    # Collaboration Bursts
    report.append("\n" + "─"*70)
    report.append("COLLABORATION BURSTS")
    report.append("─"*70)
    if not burst_summary.empty:
        report.append(f"Total Bursts Detected: {len(burst_summary)}\n")
        for idx, burst in burst_summary.iterrows():
            report.append(f"Burst #{idx + 1}:")
            report.append(f"  Period: {burst['start'].date()} to {burst['end'].date()}")
            report.append(f"  Duration: {burst['duration_hours']:.1f} hours")
            report.append(f"  Events: {burst['event_count']} ({burst['emails']} emails, {burst['meetings']} meetings)")
            report.append(f"  Participants: {burst['participant_count']}")
            report.append(f"  Confidence: {burst['confidence']:.2f}")
            report.append("")
    else:
        report.append("No collaboration bursts detected with current parameters.")
    
    # Milestones
    if milestone_df is not None and not milestone_df.empty:
        report.append("\n" + "─"*70)
        report.append("PROJECT MILESTONES")
        report.append("─"*70)
        report.append(f"Total Milestones Detected: {len(milestone_df)}\n")
        
        for milestone_type in ['decision_point', 'deliverable', 'planning_phase']:
            subset = milestone_df[milestone_df['type'] == milestone_type]
            if not subset.empty:
                type_name = milestone_type.replace('_', ' ').title()
                report.append(f"\n{type_name}s ({len(subset)}):")
                for _, m in subset.head(5).iterrows():
                    report.append(f"  • {m['date'].date()}: {m['title']}")
                    report.append(f"    Confidence: {m['confidence']:.2%}, "
                                f"Participants: {m['participant_count']}")
    
    # Phase Transitions
    if phase_df is not None and not phase_df.empty:
        report.append("\n" + "─"*70)
        report.append("PHASE TRANSITIONS")
        report.append("─"*70)
        report.append(f"Total Transitions Detected: {len(phase_df)}\n")
        
        for _, phase in phase_df.iterrows():
            report.append(f"• {phase['date'].date()}: "
                        f"{phase['previous_phase']} → {phase['new_phase']}")
            report.append(f"  Confidence: {phase['confidence']:.2%}, "
                        f"Topic Shift: {phase['similarity_score']:.2%} similarity")
            report.append(f"  New Focus: {', '.join(phase['new_keywords'][:3])}\n")
    
    # Sentiment Analysis
    if sentiment_df is not None and not sentiment_df.empty:
        report.append("\n" + "─"*70)
        report.append("SENTIMENT ANALYSIS")
        report.append("─"*70)
        
        sentiment_counts = sentiment_df['sentiment'].value_counts()
        total = len(sentiment_df)
        
        report.append("Overall Distribution:")
        for sentiment_type in ['positive', 'neutral', 'negative']:
            count = sentiment_counts.get(sentiment_type, 0)
            pct = (count / total * 100) if total > 0 else 0
            report.append(f"  {sentiment_type.title()}: {count} ({pct:.1f}%)")
        
        avg_score = sentiment_df['sentiment_score'].mean()
        report.append(f"\nAverage Sentiment Score: {avg_score:.2f} (0=negative, 1=positive)")
    
    # Influence Rankings
    if influence_df is not None and not influence_df.empty:
        report.append("\n" + "─"*70)
        report.append("TOP INFLUENCERS (PageRank)")
        report.append("─"*70)
        
        for _, person in influence_df.head(10).iterrows():
            report.append(f"{person['rank']:2d}. {person['participant']:40s} | "
                        f"{person['role']:17s} | "
                        f"Score: {person['influence_score']:.4f}")
        
        # Role distribution
        report.append("\nRole Distribution:")
        role_counts = influence_df['role'].value_counts()
        for role, count in role_counts.items():
            report.append(f"  {role}: {count}")
    
    # Handoff Events
    if handoff_df is not None and not handoff_df.empty:
        report.append("\n" + "─"*70)
        report.append("HANDOFF EVENTS")
        report.append("─"*70)
        report.append(f"Total Handoffs Detected: {len(handoff_df)}\n")
        
        for _, handoff in handoff_df.head(5).iterrows():
            report.append(f"• {handoff['date'].date()} [{handoff['handoff_type']}]:")
            report.append(f"  {handoff['description']}")
            report.append(f"  Confidence: {handoff['confidence']:.2%}\n")
    
    # Communication Patterns
    report.append("\n" + "─"*70)
    report.append("COMMUNICATION PATTERNS")
    report.append("─"*70)
    
    # Monthly activity
    timeline_df['month'] = timeline_df['date'].dt.to_period('M')
    monthly = timeline_df.groupby('month').size()
    report.append("\nMonthly Activity:")
    for month, count in monthly.head(10).items():
        report.append(f"  {month}: {count} events")
    
    # Event type distribution
    type_dist = timeline_df['type'].value_counts()
    report.append("\nEvent Type Distribution:")
    for event_type, count in type_dist.items():
        pct = (count / len(timeline_df)) * 100
        report.append(f"  {event_type.title()}: {count} ({pct:.1f}%)")
    
    report.append("\n" + "="*70)
    report.append("End of Report")
    report.append("="*70)
    
    # Save report
    report_text = '\n'.join(report)
    with open('outputs/summary_report.txt', 'w') as f:
        f.write(report_text)
    
    # Print to console
    print("\n" + report_text)


if __name__ == "__main__":
    main()
