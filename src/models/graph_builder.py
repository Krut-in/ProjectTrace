"""
Multi-layer graph construction module
Builds comprehensive graph representation of project communications
"""

import networkx as nx
from typing import Dict, List, Set, Tuple, Optional
from datetime import datetime, timedelta
import logging
from collections import defaultdict

from src.models.schemas import EmailEvent, CalendarEvent, EventType

logger = logging.getLogger(__name__)


class ProjectGraph:
    """
    Multi-layer graph representation of project communications
    Includes person nodes, event nodes, and various relationship edges
    """
    
    def __init__(self):
        self.G = nx.MultiDiGraph()
        self.person_nodes: Set[str] = set()
        self.event_nodes: Set[str] = set()
        self.temporal_edges: List[Tuple] = []
        
    def build_graph(
        self, 
        emails: List[EmailEvent], 
        calendar_events: List[CalendarEvent]
    ) -> nx.MultiDiGraph:
        """
        Build multi-layer graph with comprehensive relationships
        """
        logger.info("Building project graph...")
        
        # Add person nodes
        self._add_person_nodes(emails, calendar_events)
        
        # Add email event nodes
        self._add_email_events(emails)
        
        # Add calendar event nodes
        self._add_calendar_events(calendar_events)
        
        # Create temporal connections
        self._create_temporal_links(emails, calendar_events)
        
        # Create collaboration links
        self._create_collaboration_links()
        
        logger.info(f"Graph built: {self.G.number_of_nodes()} nodes, "
                   f"{self.G.number_of_edges()} edges")
        
        return self.G
    
    def _add_person_nodes(
        self, 
        emails: List[EmailEvent], 
        calendar_events: List[CalendarEvent]
    ) -> None:
        """Add person nodes with attributes"""
        all_people = set()
        
        for email in emails:
            all_people.update(email.participants)
        
        for event in calendar_events:
            if event.organizer:
                all_people.add(event.organizer)
            all_people.update(event.attendees)
        
        for person in all_people:
            if person and '@' in person:
                org = person.split('@')[1].split('.')[0].title()
                self.G.add_node(
                    person,
                    type='person',
                    organization=org,
                    email=person
                )
                self.person_nodes.add(person)
        
        logger.info(f"Added {len(self.person_nodes)} person nodes")
    
    def _add_email_events(self, emails: List[EmailEvent]) -> None:
        """Add email thread nodes"""
        for email in emails:
            node_id = email.thread_id
            
            self.G.add_node(
                node_id,
                type='email',
                subject=email.subject,
                date=email.first_date,
                end_date=email.last_date,
                participant_count=len(email.participants),
                email_count=email.email_count,
                duration=(email.last_date - email.first_date).total_seconds()
            )
            self.event_nodes.add(node_id)
            
            # Link participants to email
            for participant in email.participants:
                if participant in self.person_nodes:
                    self.G.add_edge(
                        participant,
                        node_id,
                        relation='participated',
                        timestamp=email.first_date
                    )
    
    def _add_calendar_events(self, calendar_events: List[CalendarEvent]) -> None:
        """Add calendar meeting nodes"""
        for event in calendar_events:
            node_id = event.uid
            
            self.G.add_node(
                node_id,
                type='meeting',
                subject=event.summary,
                date=event.start,
                end_date=event.end,
                participant_count=len(event.attendees),
                duration=(event.end - event.start).total_seconds(),
                has_startupco=event.has_startupco_in_title or event.has_startupco_participant
            )
            self.event_nodes.add(node_id)
            
            # Link organizer
            if event.organizer and event.organizer in self.person_nodes:
                self.G.add_edge(
                    event.organizer,
                    node_id,
                    relation='organized',
                    timestamp=event.start
                )
            
            # Link attendees
            for attendee in event.attendees:
                if attendee in self.person_nodes:
                    self.G.add_edge(
                        attendee,
                        node_id,
                        relation='attended',
                        timestamp=event.start
                    )
    
    def _create_temporal_links(
        self, 
        emails: List[EmailEvent], 
        calendar_events: List[CalendarEvent]
    ) -> None:
        """
        Create temporal links between events happening close in time
        with shared participants
        """
        all_events = []
        
        # Collect all events with timestamps
        for email in emails:
            all_events.append({
                'id': email.thread_id,
                'date': email.first_date,
                'participants': set(email.participants),
                'type': 'email'
            })
        
        for event in calendar_events:
            all_events.append({
                'id': event.uid,
                'date': event.start,
                'participants': set(event.attendees),
                'type': 'meeting'
            })
        
        # Sort by date
        all_events.sort(key=lambda x: x['date'])
        
        # Create temporal links
        window_hours = 48
        for i, event1 in enumerate(all_events):
            for event2 in all_events[i+1:]:
                time_diff = (event2['date'] - event1['date']).total_seconds() / 3600
                
                if time_diff > window_hours:
                    break
                
                # Check for shared participants
                shared = event1['participants'] & event2['participants']
                if shared:
                    self.G.add_edge(
                        event1['id'],
                        event2['id'],
                        relation='temporal_proximity',
                        time_diff_hours=time_diff,
                        shared_participants=len(shared),
                        confidence=min(1.0, len(shared) / 3)
                    )
                    self.temporal_edges.append((event1['id'], event2['id']))
        
        logger.info(f"Created {len(self.temporal_edges)} temporal links")
    
    def _create_collaboration_links(self) -> None:
        """Create person-to-person collaboration edges"""
        for person in self.person_nodes:
            # Get all events this person participated in
            person_events = [
                node for node in self.G.successors(person)
                if self.G.nodes[node].get('type') in ['email', 'meeting']
            ]
            
            # Find co-participants
            collaborators = defaultdict(int)
            for event in person_events:
                for collaborator in self.G.predecessors(event):
                    if collaborator != person and collaborator in self.person_nodes:
                        collaborators[collaborator] += 1
            
            # Add collaboration edges
            for collaborator, count in collaborators.items():
                self.G.add_edge(
                    person,
                    collaborator,
                    relation='collaborated',
                    event_count=count,
                    weight=count
                )
        
        logger.info(f"Created collaboration network")
    
    def get_subgraph(self, node_types: List[str]) -> nx.Graph:
        """Extract subgraph containing only specific node types"""
        nodes = [
            n for n, attr in self.G.nodes(data=True)
            if attr.get('type') in node_types
        ]
        return self.G.subgraph(nodes)
    
    def get_statistics(self) -> Dict:
        """Get graph statistics"""
        return {
            'total_nodes': self.G.number_of_nodes(),
            'total_edges': self.G.number_of_edges(),
            'person_nodes': len(self.person_nodes),
            'event_nodes': len(self.event_nodes),
            'temporal_edges': len(self.temporal_edges),
            'density': nx.density(self.G),
            'avg_degree': sum(dict(self.G.degree()).values()) / len(self.G.nodes()) if self.G.nodes() else 0
        }
    
    def export_graph(self, output_path: str, format: str = 'gexf') -> None:
        """Export graph to file"""
        try:
            if format == 'gexf':
                nx.write_gexf(self.G, output_path)
            elif format == 'graphml':
                nx.write_graphml(self.G, output_path)
            elif format == 'json':
                import json
                from networkx.readwrite import json_graph
                data = json_graph.node_link_data(self.G)
                with open(output_path, 'w') as f:
                    json.dump(data, f, indent=2)
            logger.info(f"Graph exported to {output_path}")
        except Exception as e:
            logger.error(f"Error exporting graph: {e}")
