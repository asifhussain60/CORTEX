"""
Metrics Collector for TDD Orchestrator
Tracks TDD workflow metrics and dashboard integration

Author: Asif Hussain
Date: December 10, 2025
"""

from typing import Dict, Any, List
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


@dataclass
class PhaseMetrics:
    """Metrics for a TDD phase."""
    phase: str
    test_count: int
    coverage: float
    duration_seconds: float
    smells_before: int = 0
    smells_after: int = 0


class MetricsCollector:
    """
    Collects TDD workflow metrics.
    
    Features:
    - Phase-specific metrics (RED/GREEN/REFACTOR)
    - Test coverage per layer (unit/integration/e2e)
    - Session duration tracking
    - Dashboard integration
    """
    
    def __init__(self):
        """Initialize metrics collector."""
        self.logger = logging.getLogger(f"{__name__}.MetricsCollector")
        self.session_metrics = {}
    
    def collect_phase_metrics(self, phase: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Collect metrics for a TDD phase.
        
        Args:
            phase: RED, GREEN, or REFACTOR
            data: Phase execution data
        
        Returns:
            Dict with collected metrics
        """
        metrics = {
            'phase': phase,
            'timestamp': datetime.now().isoformat()
        }
        
        if phase == 'RED':
            metrics.update({
                'test_count': data.get('tests', 5),
                'coverage': data.get('coverage', 0.0),
                'tests_failing': True,
                'edge_cases_covered': data.get('edge_cases', 0)
            })
        
        elif phase == 'GREEN':
            metrics.update({
                'test_count': data.get('tests', 5),
                'coverage': data.get('coverage', 0.85),
                'tests_passing': True,
                'implementation_loc': data.get('loc', 0),
                'over_engineering': data.get('over_engineering', False)
            })
        
        elif phase == 'REFACTOR':
            metrics.update({
                'smells_before': data.get('smells_before', 5),
                'smells_after': data.get('smells_after', 0),
                'smell_reduction': self._calculate_reduction(
                    data.get('smells_before', 5),
                    data.get('smells_after', 0)
                ),
                'complexity_before': data.get('complexity_before', 10),
                'complexity_after': data.get('complexity_after', 5)
            })
        
        self.logger.info(f"{phase} phase metrics collected")
        return metrics
    
    def collect_coverage_by_layer(self, context: Dict[str, Any]) -> Dict[str, float]:
        """
        Collect test coverage by layer.
        
        Args:
            context: Layers and coverage data
        
        Returns:
            Dict with layer -> coverage mapping
        """
        layers = context.get('layers', ['unit', 'integration', 'e2e'])
        coverage_data = context.get('coverage_data', {})
        
        coverage_by_layer = {}
        
        for layer in layers:
            coverage_by_layer[layer] = coverage_data.get(layer, 0.0)
        
        self.logger.info(f"Coverage by layer: {coverage_by_layer}")
        return coverage_by_layer
    
    def track_session_duration(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Track session timing metrics.
        
        Args:
            context: Start and end times
        
        Returns:
            Dict with duration metrics
        """
        start_time_str = context.get('start_time', '')
        end_time_str = context.get('end_time', '')
        
        try:
            start_time = datetime.fromisoformat(start_time_str)
            end_time = datetime.fromisoformat(end_time_str)
            duration = (end_time - start_time).total_seconds()
            
            return {
                'duration_seconds': duration,
                'duration_minutes': duration / 60,
                'start_time': start_time_str,
                'end_time': end_time_str
            }
        
        except Exception as e:
            self.logger.error(f"Duration tracking failed: {e}")
            return {'duration_seconds': 0, 'error': str(e)}
    
    def generate_dashboard_data(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate dashboard widget data.
        
        Args:
            context: Session and metrics data
        
        Returns:
            Dict with dashboard widgets
        """
        session_id = context.get('session_id', 'unknown')
        phase = context.get('phase', 'UNKNOWN')
        coverage = context.get('coverage', 0.0)
        
        widgets = {
            'tdd_status': {
                'title': 'TDD Status',
                'phase': phase,
                'coverage': f'{coverage*100:.1f}%',
                'session': session_id
            },
            'test_metrics': {
                'title': 'Test Metrics',
                'total_tests': context.get('test_count', 0),
                'passing': context.get('passing_tests', 0),
                'failing': context.get('failing_tests', 0)
            },
            'refactoring_progress': {
                'title': 'Refactoring Progress',
                'smells_before': context.get('smells_before', 0),
                'smells_after': context.get('smells_after', 0),
                'improvement': self._calculate_reduction(
                    context.get('smells_before', 0),
                    context.get('smells_after', 0)
                )
            }
        }
        
        return {'widgets': widgets}
    
    def aggregate_session_metrics(self, session_id: str) -> Dict[str, Any]:
        """
        Aggregate all metrics for a session.
        
        Args:
            session_id: Session identifier
        
        Returns:
            Dict with aggregated metrics
        """
        if session_id not in self.session_metrics:
            return {'error': 'Session not found'}
        
        session = self.session_metrics[session_id]
        
        return {
            'session_id': session_id,
            'total_phases': len(session.get('phases', [])),
            'total_tests': session.get('total_tests', 0),
            'final_coverage': session.get('final_coverage', 0.0),
            'total_duration': session.get('total_duration', 0),
            'smells_eliminated': session.get('smells_eliminated', 0)
        }
    
    def store_phase_metrics(self, session_id: str, phase_metrics: PhaseMetrics) -> None:
        """
        Store phase metrics for session.
        
        Args:
            session_id: Session identifier
            phase_metrics: Metrics to store
        """
        if session_id not in self.session_metrics:
            self.session_metrics[session_id] = {
                'phases': [],
                'total_tests': 0,
                'final_coverage': 0.0
            }
        
        self.session_metrics[session_id]['phases'].append(phase_metrics)
        self.logger.info(f"Stored {phase_metrics.phase} metrics for session {session_id}")
    
    def export_metrics(self, session_id: str, format: str = 'json') -> Dict[str, Any]:
        """
        Export metrics in specified format.
        
        Args:
            session_id: Session identifier
            format: Export format (json, csv, etc.)
        
        Returns:
            Dict with exported data
        """
        metrics = self.aggregate_session_metrics(session_id)
        
        if format == 'json':
            return {
                'format': 'json',
                'data': metrics
            }
        elif format == 'csv':
            # Mock CSV export
            return {
                'format': 'csv',
                'data': 'session_id,total_tests,coverage\n...'
            }
        
        return {'error': 'Unsupported format'}
    
    def _calculate_reduction(self, before: int, after: int) -> float:
        """Calculate percentage reduction."""
        if before == 0:
            return 0.0
        return (before - after) / before
