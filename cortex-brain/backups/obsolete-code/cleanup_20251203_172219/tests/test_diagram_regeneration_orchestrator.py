"""
Comprehensive tests for DiagramRegenerationOrchestrator

Validates diagram scanning, status analysis, dashboard generation, and report building.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

from src.operations.modules.diagrams.diagram_regeneration_orchestrator import (
    DiagramRegenerationOrchestrator,
    DiagramStatus,
    DiagramRegenerationReport
)


class TestDiagramStatus:
    """Test DiagramStatus dataclass"""
    
    def test_completion_percentage_all_complete(self):
        """Test 100% completion when all components exist"""
        status = DiagramStatus(
            id="01",
            name="test-diagram",
            title="Test Diagram",
            has_prompt=True,
            has_narrative=True,
            has_mermaid=True,
            has_image=True
        )
        assert status.completion_percentage == 100
        assert status.status == "complete"
    
    def test_completion_percentage_partial(self):
        """Test partial completion percentage"""
        status = DiagramStatus(
            id="02",
            name="partial-diagram",
            title="Partial Diagram",
            has_prompt=True,
            has_narrative=True,
            has_mermaid=False,
            has_image=False
        )
        assert status.completion_percentage == 50  # 2/4 = 50%
        assert status.status == "partial"  # 50% = partial not incomplete
    
    def test_completion_percentage_empty(self):
        """Test 0% completion when no components exist"""
        status = DiagramStatus(
            id="03",
            name="empty-diagram",
            title="Empty Diagram",
            has_prompt=False,
            has_narrative=False,
            has_mermaid=False,
            has_image=False
        )
        assert status.completion_percentage == 0
        assert status.status == "incomplete"


class TestDiagramRegenerationOrchestrator:
    """Test DiagramRegenerationOrchestrator core methods"""
    
    def test_initialization(self):
        """Test orchestrator initializes correctly"""
        orchestrator = DiagramRegenerationOrchestrator()
        assert orchestrator.cortex_root is not None
        assert isinstance(orchestrator.cortex_root, Path)
    
    def test_initialization_with_custom_root(self):
        """Test initialization with custom root path"""
        custom_root = Path("/custom/path")
        orchestrator = DiagramRegenerationOrchestrator(cortex_root=custom_root)
        assert orchestrator.cortex_root == custom_root
    
    def test_execute_returns_report(self):
        """Test execute() method returns DiagramRegenerationReport"""
        orchestrator = DiagramRegenerationOrchestrator()
        
        with patch.object(orchestrator, '_scan_diagrams', return_value=[]):
            with patch.object(orchestrator, '_generate_interactive_dashboard'):
                report = orchestrator.execute()
        
        assert isinstance(report, DiagramRegenerationReport)
        assert hasattr(report, 'timestamp')
        assert hasattr(report, 'diagrams')
        assert hasattr(report, 'overall_completion')
    
    def test_scan_diagrams_returns_list(self):
        """Test _scan_diagrams() returns list of DiagramStatus"""
        orchestrator = DiagramRegenerationOrchestrator()
        
        with patch('pathlib.Path.exists', return_value=True):
            with patch('pathlib.Path.stat'):
                statuses = orchestrator._scan_diagrams()
        
        assert isinstance(statuses, list)
        assert len(statuses) > 0
        assert all(isinstance(s, DiagramStatus) for s in statuses)
    
    def test_scan_diagrams_handles_missing_files(self):
        """Test _scan_diagrams() handles missing diagram files"""
        orchestrator = DiagramRegenerationOrchestrator()
        
        with patch.object(Path, 'exists', return_value=False):
            statuses = orchestrator._scan_diagrams()
        
        assert isinstance(statuses, list)
    
    def test_generate_interactive_dashboard_no_error(self):
        """Test interactive dashboard generation doesn't raise errors"""
        orchestrator = DiagramRegenerationOrchestrator()
        
        report = DiagramRegenerationReport(
            timestamp=datetime.now(),
            diagrams=[],
            total_diagrams=4,
            complete_diagrams=3,
            incomplete_diagrams=1,
            regenerated_count=0,
            failed_count=0,
            duration_seconds=1.5
        )
        
        with patch.object(orchestrator, '_build_diagram_overview', return_value={}):
            with patch.object(orchestrator, '_build_diagram_visualizations', return_value={}):
                with patch.object(orchestrator, '_build_diagram_recommendations', return_value=[]):
                    with patch.object(orchestrator, '_build_diagram_data_tables', return_value=[]):
                        with patch.object(orchestrator, '_build_diagram_diagrams', return_value=[]):
                            orchestrator._generate_interactive_dashboard(report)
    
    def test_build_diagram_overview(self):
        """Test building diagram overview data"""
        orchestrator = DiagramRegenerationOrchestrator()
        
        test_diagram = DiagramStatus(
            id="01", name="test", title="Test",
            has_prompt=True, has_narrative=True,
            has_mermaid=True, has_image=True
        )
        
        report = DiagramRegenerationReport(
            timestamp=datetime.now(),
            diagrams=[test_diagram],
            total_diagrams=5,
            complete_diagrams=4,
            incomplete_diagrams=1,
            regenerated_count=0,
            failed_count=0,
            duration_seconds=1.5
        )
        
        overview = orchestrator._build_diagram_overview(report)
        
        assert isinstance(overview, dict)
        assert 'executiveSummary' in overview
        assert 'keyMetrics' in overview
        assert 'statusIndicator' in overview
    
    def test_build_diagram_visualizations(self):
        """Test building visualization data"""
        orchestrator = DiagramRegenerationOrchestrator()
        
        status = DiagramStatus(
            id="01",
            name="test",
            title="Test",
            has_prompt=True,
            has_narrative=True,
            has_mermaid=False,
            has_image=False
        )
        
        report = DiagramRegenerationReport(
            timestamp=datetime.now(),
            diagrams=[status],
            total_diagrams=1,
            complete_diagrams=0,
            incomplete_diagrams=1,
            regenerated_count=0,
            failed_count=0,
            duration_seconds=1.5
        )
        
        viz_data = orchestrator._build_diagram_visualizations(report)
        
        assert isinstance(viz_data, dict)
        assert 'forceGraph' in viz_data
        assert 'timeSeries' in viz_data
    
    def test_build_diagram_recommendations(self):
        """Test building recommendations from report"""
        orchestrator = DiagramRegenerationOrchestrator()
        
        incomplete_diagram = DiagramStatus(
            id="01",
            name="test-diagram",
            title="Test Diagram",
            has_prompt=True,
            has_narrative=False,
            has_mermaid=False,
            has_image=False
        )
        
        report = DiagramRegenerationReport(
            timestamp=datetime.now(),
            diagrams=[incomplete_diagram],
            total_diagrams=1,
            complete_diagrams=0,
            incomplete_diagrams=1,
            regenerated_count=0,
            failed_count=0,
            duration_seconds=1.5
        )
        
        recommendations = orchestrator._build_diagram_recommendations(report)
        
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
    
    def test_build_diagram_data_tables(self):
        """Test building data tables"""
        orchestrator = DiagramRegenerationOrchestrator()
        
        status = DiagramStatus(
            id="01",
            name="test",
            title="Test",
            has_prompt=True,
            has_narrative=True,
            has_mermaid=True,
            has_image=True
        )
        
        report = DiagramRegenerationReport(
            timestamp=datetime.now(),
            diagrams=[status],
            total_diagrams=1,
            complete_diagrams=1,
            incomplete_diagrams=0,
            regenerated_count=0,
            failed_count=0,
            duration_seconds=1.5
        )
        
        tables = orchestrator._build_diagram_data_tables(report)
        
        assert isinstance(tables, list)


class TestDiagramRegenerationReport:
    """Test DiagramRegenerationReport dataclass"""
    
    def test_overall_completion_calculation(self):
        """Test overall completion percentage calculation"""
        status1 = DiagramStatus(
            id="01", name="d1", title="D1",
            has_prompt=True, has_narrative=True,
            has_mermaid=True, has_image=True
        )
        status2 = DiagramStatus(
            id="02", name="d2", title="D2",
            has_prompt=True, has_narrative=False,
            has_mermaid=False, has_image=False
        )
        
        report = DiagramRegenerationReport(
            timestamp=datetime.now(),
            diagrams=[status1, status2],
            total_diagrams=2,
            complete_diagrams=1,  # Only status1 is 100% complete
            incomplete_diagrams=1,  # status2 is 25% incomplete
            regenerated_count=0,
            failed_count=0,
            duration_seconds=1.5
        )
        
        # Overall completion = complete_diagrams / total_diagrams * 100
        # = 1 / 2 * 100 = 50%
        assert report.overall_completion == 50.0


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_empty_diagram_list(self):
        """Test handling empty diagram list"""
        orchestrator = DiagramRegenerationOrchestrator()
        
        with patch.object(orchestrator, '_scan_diagrams', return_value=[]):
            with patch.object(orchestrator, '_generate_interactive_dashboard'):
                report = orchestrator.execute()
        
        assert report.overall_completion == 0.0
        assert report.complete_diagrams == 0
    
    def test_all_diagrams_complete(self):
        """Test when all diagrams are complete"""
        complete_status = DiagramStatus(
            id="01", name="test", title="Test",
            has_prompt=True, has_narrative=True,
            has_mermaid=True, has_image=True
        )
        
        orchestrator = DiagramRegenerationOrchestrator()
        
        with patch.object(orchestrator, '_scan_diagrams', return_value=[complete_status]):
            with patch.object(orchestrator, '_generate_interactive_dashboard'):
                report = orchestrator.execute()
        
        assert report.overall_completion == 100.0
        assert report.complete_diagrams == 1
        assert report.incomplete_diagrams == 0
    
    def test_build_diagram_diagrams(self):
        """Test building Mermaid diagrams"""
        orchestrator = DiagramRegenerationOrchestrator()
        
        report = DiagramRegenerationReport(
            timestamp=datetime.now(),
            diagrams=[],
            total_diagrams=10,
            complete_diagrams=7,
            incomplete_diagrams=3,
            regenerated_count=0,
            failed_count=0,
            duration_seconds=2.5
        )
        
        diagrams = orchestrator._build_diagram_diagrams(report)
        
        assert isinstance(diagrams, list)
        assert len(diagrams) > 0
        assert diagrams[0]['type'] == 'mermaid'
        assert '7/10 Complete' in diagrams[0]['content']
    
    def test_status_indicator_success(self):
        """Test status indicator for >90% completion"""
        orchestrator = DiagramRegenerationOrchestrator()
        
        complete_diagram = DiagramStatus(
            id="01", name="test", title="Test",
            has_prompt=True, has_narrative=True,
            has_mermaid=True, has_image=True
        )
        
        report = DiagramRegenerationReport(
            timestamp=datetime.now(),
            diagrams=[complete_diagram],
            total_diagrams=10,
            complete_diagrams=10,
            incomplete_diagrams=0,
            regenerated_count=0,
            failed_count=0,
            duration_seconds=1.0
        )
        
        overview = orchestrator._build_diagram_overview(report)
        
        assert overview['statusIndicator']['status'] == 'success'
        assert overview['statusIndicator']['color'] == '#22c55e'
    
    def test_status_indicator_warning(self):
        """Test status indicator for 70-89% completion"""
        orchestrator = DiagramRegenerationOrchestrator()
        
        partial_diagram = DiagramStatus(
            id="01", name="test", title="Test",
            has_prompt=True, has_narrative=True,
            has_mermaid=False, has_image=False
        )
        
        report = DiagramRegenerationReport(
            timestamp=datetime.now(),
            diagrams=[partial_diagram],
            total_diagrams=10,
            complete_diagrams=8,
            incomplete_diagrams=2,
            regenerated_count=0,
            failed_count=0,
            duration_seconds=1.0
        )
        
        overview = orchestrator._build_diagram_overview(report)
        
        assert overview['statusIndicator']['status'] == 'warning'
        assert overview['statusIndicator']['color'] == '#f59e0b'
    
    def test_status_indicator_critical(self):
        """Test status indicator for <70% completion"""
        orchestrator = DiagramRegenerationOrchestrator()
        
        incomplete_diagram = DiagramStatus(
            id="01", name="test", title="Test",
            has_prompt=False, has_narrative=False,
            has_mermaid=False, has_image=False
        )
        
        report = DiagramRegenerationReport(
            timestamp=datetime.now(),
            diagrams=[incomplete_diagram],
            total_diagrams=10,
            complete_diagrams=5,
            incomplete_diagrams=5,
            regenerated_count=0,
            failed_count=0,
            duration_seconds=1.0
        )
        
        overview = orchestrator._build_diagram_overview(report)
        
        assert overview['statusIndicator']['status'] == 'critical'
        assert overview['statusIndicator']['color'] == '#ef4444'
    
    def test_recommendations_with_healthy_system(self):
        """Test recommendations when all diagrams complete"""
        orchestrator = DiagramRegenerationOrchestrator()
        
        complete_diagram = DiagramStatus(
            id="01", name="test", title="Test",
            has_prompt=True, has_narrative=True,
            has_mermaid=True, has_image=True
        )
        
        report = DiagramRegenerationReport(
            timestamp=datetime.now(),
            diagrams=[complete_diagram],
            total_diagrams=1,
            complete_diagrams=1,
            incomplete_diagrams=0,
            regenerated_count=0,
            failed_count=0,
            duration_seconds=1.0
        )
        
        recommendations = orchestrator._build_diagram_recommendations(report)
        
        assert len(recommendations) == 1
        assert recommendations[0]['priority'] == 'low'
        assert 'healthy' in recommendations[0]['title'].lower()
