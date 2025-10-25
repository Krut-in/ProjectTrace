"""
Quick visualization script for Email+Calendar Graph System
Generates basic plots from analysis results
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import json

# Set style
sns.set_theme(style="whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)

def visualize_timeline():
    """Create timeline visualization"""
    df = pd.read_csv('outputs/timeline.csv')
    df['date'] = pd.to_datetime(df['date'])
    df['month'] = df['date'].dt.to_period('M')
    
    # Monthly activity
    monthly = df.groupby(['month', 'type']).size().unstack(fill_value=0)
    
    fig, ax = plt.subplots(figsize=(14, 6))
    monthly.plot(kind='bar', stacked=True, ax=ax, color=['#3498db', '#2ecc71'])
    ax.set_title('Project Communication Timeline', fontsize=16, fontweight='bold')
    ax.set_xlabel('Month', fontsize=12)
    ax.set_ylabel('Number of Events', fontsize=12)
    ax.legend(['Email Threads', 'Meetings'], frameon=True)
    ax.grid(axis='y', alpha=0.3)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig('outputs/visualizations/timeline.png', dpi=300, bbox_inches='tight')
    print("✓ Timeline visualization saved: outputs/visualizations/timeline.png")
    plt.close()


def visualize_participants():
    """Create participant engagement chart"""
    df = pd.read_csv('outputs/participant_stats.csv')
    top_10 = df.head(10).copy()
    
    # Clean names
    top_10['name'] = top_10['email'].apply(lambda x: x.split('@')[0].replace('.', ' ').title())
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # Total events
    colors = ['#e74c3c' if x == top_10['total_events'].max() else '#3498db' for x in top_10['total_events']]
    ax1.barh(top_10['name'], top_10['total_events'], color=colors)
    ax1.set_title('Top 10 Most Active Participants', fontsize=14, fontweight='bold')
    ax1.set_xlabel('Total Events', fontsize=12)
    ax1.grid(axis='x', alpha=0.3)
    
    # Email vs Meeting breakdown
    x = range(len(top_10))
    ax2.bar(x, top_10['email_threads'], label='Email Threads', color='#3498db', alpha=0.8)
    ax2.bar(x, top_10['meetings'], bottom=top_10['email_threads'], label='Meetings', color='#2ecc71', alpha=0.8)
    ax2.set_title('Communication Type Breakdown', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Participants', fontsize=12)
    ax2.set_ylabel('Events', fontsize=12)
    ax2.set_xticks(x)
    ax2.set_xticklabels(top_10['name'], rotation=45, ha='right')
    ax2.legend(frameon=True)
    ax2.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('outputs/visualizations/participants.png', dpi=300, bbox_inches='tight')
    print("✓ Participant visualization saved: outputs/visualizations/participants.png")
    plt.close()


def visualize_bursts():
    """Create burst detection visualization"""
    try:
        bursts_df = pd.read_csv('outputs/collaboration_bursts.csv')
        if bursts_df.empty:
            print("⚠ No bursts detected to visualize")
            return
        
        timeline_df = pd.read_csv('outputs/timeline.csv')
        timeline_df['date'] = pd.to_datetime(timeline_df['date'])
        bursts_df['start'] = pd.to_datetime(bursts_df['start'])
        bursts_df['end'] = pd.to_datetime(bursts_df['end'])
        
        # Create figure
        fig, ax = plt.subplots(figsize=(16, 6))
        
        # Plot timeline
        emails = timeline_df[timeline_df['type'] == 'email']
        meetings = timeline_df[timeline_df['type'] == 'meeting']
        
        ax.scatter(emails['date'], [1]*len(emails), s=100, alpha=0.6, 
                  c='#3498db', label='Email Threads', marker='o')
        ax.scatter(meetings['date'], [1]*len(meetings), s=150, alpha=0.6, 
                  c='#2ecc71', label='Meetings', marker='s')
        
        # Highlight bursts
        for idx, burst in bursts_df.iterrows():
            ax.axvspan(burst['start'], burst['end'], alpha=0.2, color='red', 
                      label='Collaboration Burst' if idx == 0 else '')
            ax.text(burst['start'], 1.15, f"Burst #{idx+1}\n{burst['event_count']} events", 
                   fontsize=10, ha='left', fontweight='bold')
        
        ax.set_ylim(0.5, 1.5)
        ax.set_xlabel('Date', fontsize=12, fontweight='bold')
        ax.set_title('Project Timeline with Collaboration Bursts', fontsize=16, fontweight='bold')
        ax.legend(loc='upper left', frameon=True)
        ax.set_yticks([])
        ax.grid(axis='x', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('outputs/visualizations/bursts.png', dpi=300, bbox_inches='tight')
        print("✓ Burst visualization saved: outputs/visualizations/bursts.png")
        plt.close()
        
    except Exception as e:
        print(f"⚠ Could not create burst visualization: {e}")


def generate_summary_stats():
    """Generate summary statistics visualization"""
    with open('outputs/graph_stats.json', 'r') as f:
        stats = json.load(f)
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
    
    # Graph composition
    labels = ['People', 'Events']
    sizes = [stats['person_nodes'], stats['event_nodes']]
    colors = ['#3498db', '#2ecc71']
    ax1.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors, startangle=90)
    ax1.set_title('Graph Node Composition', fontsize=12, fontweight='bold')
    
    # Edge types
    edge_types = ['Temporal Links', 'Other Edges']
    edge_sizes = [stats['temporal_edges'], stats['total_edges'] - stats['temporal_edges']]
    colors2 = ['#e74c3c', '#95a5a6']
    ax2.pie(edge_sizes, labels=edge_types, autopct='%1.1f%%', colors=colors2, startangle=90)
    ax2.set_title('Edge Type Distribution', fontsize=12, fontweight='bold')
    
    # Key metrics
    metrics = ['Total\nNodes', 'Total\nEdges', 'Temporal\nLinks', 'Avg\nDegree']
    values = [stats['total_nodes'], stats['total_edges'], 
              stats['temporal_edges'], round(stats['avg_degree'], 1)]
    colors3 = ['#3498db', '#2ecc71', '#e74c3c', '#f39c12']
    ax3.bar(metrics, values, color=colors3, alpha=0.7)
    ax3.set_title('Graph Statistics Summary', fontsize=12, fontweight='bold')
    ax3.set_ylabel('Count', fontsize=10)
    ax3.grid(axis='y', alpha=0.3)
    
    # Density gauge
    density = stats['density']
    ax4.barh(['Graph Density'], [density], color='#9b59b6', alpha=0.7)
    ax4.set_xlim(0, 1)
    ax4.set_title('Network Density', fontsize=12, fontweight='bold')
    ax4.set_xlabel('Density Score (0-1)', fontsize=10)
    ax4.text(density + 0.05, 0, f'{density:.3f}', va='center', fontsize=12, fontweight='bold')
    ax4.grid(axis='x', alpha=0.3)
    
    plt.suptitle('Email+Calendar Graph System - Network Statistics', 
                 fontsize=16, fontweight='bold', y=0.995)
    plt.tight_layout()
    plt.savefig('outputs/visualizations/statistics.png', dpi=300, bbox_inches='tight')
    print("✓ Statistics visualization saved: outputs/visualizations/statistics.png")
    plt.close()


def main():
    """Generate all visualizations"""
    print("\n" + "="*60)
    print("Generating Visualizations for Email+Calendar Graph System")
    print("="*60 + "\n")
    
    try:
        visualize_timeline()
        visualize_participants()
        visualize_bursts()
        generate_summary_stats()
        
        print("\n" + "="*60)
        print("✅ All visualizations generated successfully!")
        print("="*60)
        print("\nView files in: outputs/visualizations/")
        print("  • timeline.png")
        print("  • participants.png")
        print("  • bursts.png")
        print("  • statistics.png")
        
    except Exception as e:
        print(f"\n❌ Error generating visualizations: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
