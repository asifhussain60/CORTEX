"""
CORTEX 3.0 Milestone 2 - Fusion Integration API

Simple integration layer that makes temporal correlation features
accessible through WorkingMemory and provides higher-level fusion
operations for the dual-channel memory system.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms
"""

from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

from .temporal_correlator import TemporalCorrelator, CorrelationResult

logger = logging.getLogger(__name__)


class FusionManager:
    """
    High-level API for CORTEX 3.0 dual-channel memory fusion operations.
    
    Provides simple methods to correlate conversations with ambient events,
    generate development narratives, and create unified timelines.
    """
    
    def __init__(self, db_path: str):
        """
        Initialize fusion manager.
        
        Args:
            db_path: Path to Tier 1 working memory database
        """
        self.db_path = db_path
        self.temporal_correlator = TemporalCorrelator(db_path)
    
    def correlate_imported_conversation(
        self, 
        conversation_id: str,
        auto_correlate: bool = True
    ) -> Dict[str, Any]:
        """
        Correlate an imported conversation with ambient events.
        
        Args:
            conversation_id: ID of imported conversation
            auto_correlate: If True, run correlation automatically
            
        Returns:
            Correlation summary with results and statistics
        """
        if not auto_correlate:
            logger.info(f"Auto-correlation disabled for {conversation_id}")
            return {
                'conversation_id': conversation_id,
                'correlations': [],
                'auto_correlate': False,
                'message': 'Auto-correlation disabled'
            }
        
        logger.info(f"Starting fusion correlation for conversation {conversation_id}")
        
        try:
            # Run temporal correlation
            correlations = self.temporal_correlator.correlate_conversation(conversation_id)
            
            # Calculate statistics
            stats = self._calculate_correlation_stats(correlations)
            
            # Generate summary
            summary = self._generate_correlation_summary(conversation_id, correlations, stats)
            
            return {
                'conversation_id': conversation_id,
                'correlations': len(correlations),
                'high_confidence': stats['high_confidence_count'],
                'file_matches': stats['file_match_count'],
                'plan_verifications': stats['plan_verification_count'],
                'temporal_correlations': stats['temporal_count'],
                'confidence_distribution': stats['confidence_distribution'],
                'summary': summary,
                'auto_correlate': True
            }
            
        except Exception as e:
            logger.error(f"Fusion correlation failed for {conversation_id}: {e}")
            return {
                'conversation_id': conversation_id,
                'correlations': 0,
                'error': str(e),
                'auto_correlate': True,
                'summary': 'Correlation failed'
            }
    
    def get_conversation_development_story(self, conversation_id: str) -> Dict[str, Any]:
        """
        Generate complete development story for a conversation.
        
        Combines conversation content with correlated ambient events
        to create a narrative that shows both the planning (WHY) and
        execution (WHAT) sides of development.
        
        Args:
            conversation_id: ID of conversation to narrate
            
        Returns:
            Development story with timeline and narrative
        """
        logger.info(f"Generating development story for conversation {conversation_id}")
        
        # Get timeline data
        timeline_data = self.temporal_correlator.get_conversation_timeline(conversation_id)
        
        if not timeline_data['timeline']:
            return {
                'conversation_id': conversation_id,
                'story': 'No development activity found',
                'timeline': [],
                'summary': 'Empty story'
            }
        
        # Generate narrative sections
        narrative = self._generate_development_narrative(timeline_data)
        
        return {
            'conversation_id': conversation_id,
            'story': narrative,
            'timeline': timeline_data['timeline'],
            'correlations_count': timeline_data.get('correlations_count', 0),
            'high_confidence_count': timeline_data.get('high_confidence_count', 0),
            'summary': timeline_data.get('summary', 'Development story generated')
        }
    
    def get_fusion_insights(
        self, 
        conversation_id: str,
        include_recommendations: bool = True
    ) -> Dict[str, Any]:
        """
        Generate fusion insights for a conversation.
        
        Analyzes correlation patterns to provide insights about
        development effectiveness, plan execution, and areas for improvement.
        
        Args:
            conversation_id: ID of conversation to analyze
            include_recommendations: If True, include actionable recommendations
            
        Returns:
            Fusion insights and recommendations
        """
        logger.info(f"Generating fusion insights for conversation {conversation_id}")
        
        # Get correlations
        correlations = self.temporal_correlator.correlate_conversation(conversation_id)
        
        if not correlations:
            return {
                'conversation_id': conversation_id,
                'insights': ['No correlations found - conversation may be purely strategic'],
                'recommendations': ['Consider manual verification of planned actions'],
                'execution_score': 0,
                'planning_effectiveness': 'Unknown'
            }
        
        # Analyze correlation patterns
        insights = []
        recommendations = []
        
        # File mention analysis
        file_correlations = [c for c in correlations if c.correlation_type == 'file_mention']
        if file_correlations:
            high_confidence_files = [c for c in file_correlations if c.confidence_score > 0.8]
            insights.append(f"Found {len(file_correlations)} file correlations ({len(high_confidence_files)} high-confidence)")
            
            if len(high_confidence_files) / len(file_correlations) > 0.7:
                insights.append("Excellent file planning accuracy - mentioned files were actually implemented")
            else:
                insights.append("Some file mentions didn't match implementation - planning could be more precise")
                if include_recommendations:
                    recommendations.append("Review file path accuracy in planning discussions")
        
        # Plan verification analysis
        plan_correlations = [c for c in correlations if c.correlation_type == 'plan_verification']
        if plan_correlations:
            avg_confidence = sum(c.confidence_score for c in plan_correlations) / len(plan_correlations)
            insights.append(f"Plan execution correlation: {avg_confidence:.2f} average confidence")
            
            if avg_confidence > 0.7:
                insights.append("Strong correlation between planned phases and actual implementation")
            else:
                insights.append("Weak plan-to-execution correlation - implementation may have diverged from plan")
                if include_recommendations:
                    recommendations.append("Consider more frequent plan validation during execution")
        
        # Temporal analysis
        temporal_correlations = [c for c in correlations if c.correlation_type == 'temporal']
        time_gaps = [c.time_diff_seconds for c in temporal_correlations]
        
        if time_gaps:
            avg_gap = sum(time_gaps) / len(time_gaps)
            insights.append(f"Average time from discussion to implementation: {avg_gap/60:.1f} minutes")
            
            if avg_gap < 1800:  # 30 minutes
                insights.append("Fast execution turnaround - good development momentum")
            elif avg_gap > 7200:  # 2 hours
                insights.append("Long execution delays - consider breaking down tasks")
                if include_recommendations:
                    recommendations.append("Plan smaller, more immediate implementation steps")
        
        # Overall execution score
        all_scores = [c.confidence_score for c in correlations]
        execution_score = int(sum(all_scores) / len(all_scores) * 100) if all_scores else 0
        
        # Planning effectiveness assessment
        if execution_score >= 80:
            effectiveness = "Excellent"
        elif execution_score >= 60:
            effectiveness = "Good"
        elif execution_score >= 40:
            effectiveness = "Fair"
        else:
            effectiveness = "Poor"
        
        return {
            'conversation_id': conversation_id,
            'insights': insights,
            'recommendations': recommendations if include_recommendations else [],
            'execution_score': execution_score,
            'planning_effectiveness': effectiveness,
            'total_correlations': len(correlations),
            'correlation_types': {
                'file_mention': len(file_correlations),
                'plan_verification': len(plan_correlations), 
                'temporal': len(temporal_correlations)
            }
        }
    
    def _calculate_correlation_stats(self, correlations: List[CorrelationResult]) -> Dict[str, Any]:
        """Calculate statistics for correlation results."""
        if not correlations:
            return {
                'high_confidence_count': 0,
                'file_match_count': 0,
                'plan_verification_count': 0,
                'temporal_count': 0,
                'confidence_distribution': {}
            }
        
        high_confidence_count = len([c for c in correlations if c.confidence_score > 0.7])
        file_match_count = len([c for c in correlations if c.correlation_type == 'file_mention'])
        plan_verification_count = len([c for c in correlations if c.correlation_type == 'plan_verification'])
        temporal_count = len([c for c in correlations if c.correlation_type == 'temporal'])
        
        # Confidence distribution
        confidence_ranges = {
            'excellent': len([c for c in correlations if c.confidence_score >= 0.9]),
            'high': len([c for c in correlations if 0.7 <= c.confidence_score < 0.9]),
            'medium': len([c for c in correlations if 0.5 <= c.confidence_score < 0.7]),
            'low': len([c for c in correlations if c.confidence_score < 0.5])
        }
        
        return {
            'high_confidence_count': high_confidence_count,
            'file_match_count': file_match_count,
            'plan_verification_count': plan_verification_count,
            'temporal_count': temporal_count,
            'confidence_distribution': confidence_ranges
        }
    
    def _generate_correlation_summary(
        self, 
        conversation_id: str, 
        correlations: List[CorrelationResult],
        stats: Dict[str, Any]
    ) -> str:
        """Generate human-readable correlation summary."""
        if not correlations:
            return "No correlations found - conversation appears to be purely strategic"
        
        summary_parts = []
        
        # Overall correlation count
        summary_parts.append(f"Found {len(correlations)} correlations")
        
        # High confidence correlations
        if stats['high_confidence_count'] > 0:
            summary_parts.append(f"{stats['high_confidence_count']} high-confidence matches")
        
        # File correlations
        if stats['file_match_count'] > 0:
            summary_parts.append(f"{stats['file_match_count']} file mentions verified")
        
        # Plan correlations
        if stats['plan_verification_count'] > 0:
            summary_parts.append(f"{stats['plan_verification_count']} plan elements tracked")
        
        # Quality assessment
        if stats['high_confidence_count'] / len(correlations) > 0.5:
            summary_parts.append("Strong correlation quality")
        else:
            summary_parts.append("Mixed correlation quality")
        
        return "; ".join(summary_parts)
    
    def _generate_development_narrative(self, timeline_data: Dict[str, Any]) -> str:
        """Generate development narrative from timeline data."""
        timeline = timeline_data['timeline']
        
        if not timeline:
            return "No development activity found"
        
        # Separate conversation turns and events
        conversation_items = [item for item in timeline if item['type'] == 'conversation_turn']
        event_items = [item for item in timeline if item['type'] == 'ambient_event']
        
        narrative_parts = []
        
        # Introduction
        narrative_parts.append(f"# Development Story: {timeline_data['conversation_id']}")
        narrative_parts.append("")
        
        if conversation_items:
            narrative_parts.append("## Strategic Planning")
            for item in conversation_items[:2]:  # First 2 conversation turns
                content = item['content'][:150] + "..." if len(item['content']) > 150 else item['content']
                narrative_parts.append(f"**{item['timestamp'].strftime('%H:%M')}** - {content}")
                
                if item.get('files_mentioned'):
                    narrative_parts.append(f"  → Files planned: {', '.join(item['files_mentioned'][:3])}")
                
                if item.get('phases_mentioned'):
                    narrative_parts.append(f"  → Phases outlined: {', '.join(item['phases_mentioned'])}")
            
            narrative_parts.append("")
        
        if event_items:
            narrative_parts.append("## Implementation Activity")
            
            # Group events by type
            by_type = {}
            for item in event_items:
                event_type = item.get('event_type', 'unknown')
                by_type.setdefault(event_type, []).append(item)
            
            for event_type, events in by_type.items():
                narrative_parts.append(f"### {event_type.replace('_', ' ').title()} Events")
                
                for event in events[:5]:  # Top 5 events per type
                    timestamp = event['timestamp'].strftime('%H:%M')
                    summary = event.get('summary', 'No summary')
                    file_path = event.get('file_path', 'N/A')
                    confidence = event.get('confidence_score', 0)
                    
                    narrative_parts.append(f"**{timestamp}** - {summary}")
                    if file_path != 'N/A':
                        narrative_parts.append(f"  → File: {file_path}")
                    narrative_parts.append(f"  → Correlation confidence: {confidence:.2f}")
                
                narrative_parts.append("")
        
        # Summary
        narrative_parts.append("## Summary")
        
        if event_items and conversation_items:
            narrative_parts.append(f"Successfully correlated {len(conversation_items)} strategic discussions with {len(event_items)} implementation events.")
            
            high_confidence = len([e for e in event_items if e.get('confidence_score', 0) > 0.7])
            if high_confidence > 0:
                narrative_parts.append(f"{high_confidence} events show strong correlation with planned activities.")
        else:
            narrative_parts.append("Limited correlation data available.")
        
        return "\n".join(narrative_parts)