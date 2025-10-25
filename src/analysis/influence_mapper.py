"""
Influence mapping module
Calculates participant influence using PageRank and classifies roles
"""

import pandas as pd
import networkx as nx
from typing import List, Dict, Tuple
import logging

logger = logging.getLogger(__name__)


class InfluenceMapper:
    """
    Calculate influence scores and classify participant roles
    
    Uses PageRank on collaboration graph to identify:
    - Strategic Leaders: High influence, moderate activity
    - Active Leaders: High influence, high activity  
    - Executors: Low influence, high activity
    - Contributors: Low influence, moderate activity
    """
    
    def __init__(
        self,
        high_influence_threshold: float = 0.03,
        high_activity_threshold: int = 10
    ):
        """
        Initialize influence mapper
        
        Args:
            high_influence_threshold: PageRank score to be considered "high influence"
            high_activity_threshold: Event count to be considered "high activity"
        """
        self.high_influence_threshold = high_influence_threshold
        self.high_activity_threshold = high_activity_threshold
    
    def calculate_influence(
        self,
        graph: nx.Graph,
        timeline_df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Calculate influence scores and classify roles
        
        Returns:
            DataFrame with columns: participant, influence_score, event_count,
            email_count, meeting_count, role, centrality_measures
        """
        logger.info("Calculating participant influence scores...")
        
        if graph is None or graph.number_of_nodes() == 0:
            logger.warning("Empty graph provided")
            return pd.DataFrame()
        
        # Get person nodes only
        person_nodes = [
            n for n, attr in graph.nodes(data=True)
            if attr.get('type') == 'person'
        ]
        
        if not person_nodes:
            logger.warning("No person nodes found in graph")
            return pd.DataFrame()
        
        # Create person-to-person subgraph
        person_graph = self._create_person_subgraph(graph, person_nodes)
        
        # Calculate various centrality measures
        pagerank_scores = nx.pagerank(person_graph, weight='weight')
        degree_centrality = nx.degree_centrality(person_graph)
        betweenness_centrality = nx.betweenness_centrality(person_graph)
        
        # Get activity statistics from timeline
        activity_stats = self._calculate_activity_stats(timeline_df)
        
        # Combine all metrics
        results = []
        
        for person in person_nodes:
            influence_score = pagerank_scores.get(person, 0)
            degree = degree_centrality.get(person, 0)
            betweenness = betweenness_centrality.get(person, 0)
            
            stats = activity_stats.get(person, {
                'total_events': 0,
                'email_count': 0,
                'meeting_count': 0
            })
            
            # Classify role
            role = self._classify_role(
                influence_score,
                stats['total_events']
            )
            
            results.append({
                'participant': person,
                'influence_score': round(influence_score, 4),
                'pagerank': round(influence_score, 4),
                'degree_centrality': round(degree, 4),
                'betweenness_centrality': round(betweenness, 4),
                'event_count': stats['total_events'],
                'email_count': stats['email_count'],
                'meeting_count': stats['meeting_count'],
                'role': role,
                'organization': self._extract_organization(person)
            })
        
        # Convert to DataFrame and sort by influence
        influence_df = pd.DataFrame(results)
        influence_df = influence_df.sort_values('influence_score', ascending=False)
        influence_df = influence_df.reset_index(drop=True)
        influence_df['rank'] = range(1, len(influence_df) + 1)
        
        # Log role distribution
        role_counts = influence_df['role'].value_counts()
        logger.info(f"Role distribution: {role_counts.to_dict()}")
        logger.info(f"Top 3 influencers: {influence_df.head(3)['participant'].tolist()}")
        
        return influence_df
    
    def _create_person_subgraph(
        self,
        graph: nx.Graph,
        person_nodes: List[str]
    ) -> nx.Graph:
        """
        Create weighted person-to-person collaboration graph
        
        Weight = number of shared events between two people
        """
        person_graph = nx.Graph()
        person_graph.add_nodes_from(person_nodes)
        
        # For each pair of people, count shared events
        event_nodes = [
            n for n, attr in graph.nodes(data=True)
            if attr.get('type') in ['email', 'meeting']
        ]
        
        for event in event_nodes:
            # Get all people connected to this event
            people_in_event = [
                n for n in graph.neighbors(event)
                if n in person_nodes
            ]
            
            # Create edges between all pairs
            for i, person1 in enumerate(people_in_event):
                for person2 in people_in_event[i+1:]:
                    if person_graph.has_edge(person1, person2):
                        person_graph[person1][person2]['weight'] += 1
                    else:
                        person_graph.add_edge(person1, person2, weight=1)
        
        logger.info(f"Created person subgraph: {person_graph.number_of_nodes()} nodes, "
                   f"{person_graph.number_of_edges()} edges")
        
        return person_graph
    
    def _calculate_activity_stats(self, timeline_df: pd.DataFrame) -> Dict:
        """
        Calculate activity statistics for each participant
        """
        stats = {}
        
        if timeline_df.empty:
            return stats
        
        for _, row in timeline_df.iterrows():
            participants = row.get('participants', [])
            event_type = row.get('type', 'unknown')
            
            for person in participants:
                if person not in stats:
                    stats[person] = {
                        'total_events': 0,
                        'email_count': 0,
                        'meeting_count': 0
                    }
                
                stats[person]['total_events'] += 1
                
                if event_type == 'email':
                    stats[person]['email_count'] += 1
                elif event_type == 'meeting':
                    stats[person]['meeting_count'] += 1
        
        return stats
    
    def _classify_role(self, influence: float, activity: int) -> str:
        """
        Classify participant role based on influence and activity
        
        Role Matrix:
                        Low Activity    High Activity
        High Influence  Strategic       Active
                       Leader          Leader
        
        Low Influence   Contributor     Executor
        """
        high_influence = influence >= self.high_influence_threshold
        high_activity = activity >= self.high_activity_threshold
        
        if high_influence and high_activity:
            return "Active Leader"
        elif high_influence and not high_activity:
            return "Strategic Leader"
        elif not high_influence and high_activity:
            return "Executor"
        else:
            return "Contributor"
    
    def _extract_organization(self, email: str) -> str:
        """Extract organization from email address"""
        if '@' not in email:
            return "Unknown"
        
        domain = email.split('@')[1]
        
        # Clean up domain
        if domain.startswith('www.'):
            domain = domain[4:]
        
        # Extract main domain name
        parts = domain.split('.')
        if len(parts) >= 2:
            org_name = parts[0]
            return org_name.title()
        
        return domain.title()
    
    def get_influence_summary(self, influence_df: pd.DataFrame) -> str:
        """Generate human-readable influence summary"""
        if influence_df.empty:
            return "No influence data available."
        
        summary = []
        summary.append(f"\n{'='*70}")
        summary.append("INFLUENCE & ROLE ANALYSIS")
        summary.append(f"{'='*70}\n")
        
        # Top influencers
        summary.append("Top 10 Influencers:")
        summary.append("-" * 70)
        
        for _, row in influence_df.head(10).iterrows():
            summary.append(f"\n  {row['rank']}. {row['participant']}")
            summary.append(f"     Role: {row['role']}")
            summary.append(f"     Influence Score: {row['influence_score']:.4f}")
            summary.append(f"     Activity: {row['event_count']} events "
                         f"({row['email_count']} emails, {row['meeting_count']} meetings)")
            summary.append(f"     Organization: {row['organization']}")
        
        # Role distribution
        summary.append(f"\n{'='*70}")
        summary.append("Role Distribution:")
        summary.append("-" * 70)
        
        role_counts = influence_df['role'].value_counts()
        for role, count in role_counts.items():
            percentage = (count / len(influence_df) * 100)
            summary.append(f"  {role}: {count} ({percentage:.1f}%)")
        
        # Organization breakdown
        summary.append(f"\n{'='*70}")
        summary.append("Organization Breakdown:")
        summary.append("-" * 70)
        
        org_counts = influence_df['organization'].value_counts()
        for org, count in org_counts.head(5).items():
            avg_influence = influence_df[influence_df['organization'] == org]['influence_score'].mean()
            summary.append(f"  {org}: {count} people, avg influence: {avg_influence:.4f}")
        
        summary.append(f"\n{'='*70}\n")
        
        return '\n'.join(summary)
    
    def identify_key_connectors(self, influence_df: pd.DataFrame, top_n: int = 5) -> List[str]:
        """
        Identify key connectors (high betweenness centrality)
        These are people who bridge different groups
        """
        if influence_df.empty:
            return []
        
        connectors = influence_df.nlargest(top_n, 'betweenness_centrality')
        return connectors['participant'].tolist()
    
    def identify_team_leaders(self, influence_df: pd.DataFrame) -> Dict[str, List[str]]:
        """Identify leaders per organization"""
        leaders = {}
        
        for org in influence_df['organization'].unique():
            org_df = influence_df[influence_df['organization'] == org]
            org_leaders = org_df[org_df['role'].str.contains('Leader')]['participant'].tolist()
            leaders[org] = org_leaders
        
        return leaders
