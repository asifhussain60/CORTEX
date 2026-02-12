"""
Unit tests for DashboardGenerator - Phase 25 Stage 2

Tests dashboard data generation, HTML updates, and sync verification.

AC-ID: PHASE-25-STAGE-2-TEST-001
"""

import pytest
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, mock_open
from datetime import datetime

from cortex.registry.dashboard_generator import (
    DashboardGenerator,
    DashboardData,
    PhaseSummary,
    DashboardSyncResult,
)


@pytest.fixture
def dashboard_generator():
    """Create DashboardGenerator instance."""
    return DashboardGenerator(registry_root="/fake/registry")


@pytest.fixture
def sample_index_data():
    """Sample index.yaml data for testing."""
    return {
        "version": "1.0",
        "registry_name": "_cortex-master",
        "last_updated": "2026-02-06",
        "active_phases": [
            {
                "id": "phase-25",
                "name": "PLAN MODE Enhancement",
                "status": "in-progress",
                "priority": "P0",
                "progress": "55%",
                "description": "Add PLAN MODE with mandatory registry integration",
            },
            {
                "id": "phase-27",
                "name": "Company Domain Integration",
                "status": "planned",
                "priority": "P1",
            }
        ],
        "completed_phases_2026": {
            "count": 13,
            "phases": ["phase-26", "phase-28", "phase-32"]
        },
        "statistics": {
            "total_phases": 25,
            "active_phases": 2,
            "completed_phases": 23,
        }
    }


class TestDashboardDataGeneration:
    """Tests for dashboard data generation from index.yaml."""

    def test_generate_from_index_creates_valid_json(self, dashboard_generator, sample_index_data):
        """Test: Generate dashboard data from index.yaml."""
        with patch.object(dashboard_generator, '_load_index', return_value=sample_index_data):
            dashboard_data = dashboard_generator.generate_dashboard_data()
            
            assert dashboard_data.total_phases == 25
            assert dashboard_data.active_phases == 2
            assert dashboard_data.completed_phases == 23
            assert len(dashboard_data.phases) == 2

    def test_phase_summary_includes_all_fields(self, dashboard_generator, sample_index_data):
        """Test: Phase summaries include all required fields."""
        with patch.object(dashboard_generator, '_load_index', return_value=sample_index_data):
            dashboard_data = dashboard_generator.generate_dashboard_data()
            
            phase = dashboard_data.phases[0]
            assert phase.id == "phase-25"
            assert phase.name == "PLAN MODE Enhancement"
            assert phase.status == "in-progress"
            assert phase.priority == "P0"
            assert phase.progress == "55%"

    def test_statistics_calculated_correctly(self, dashboard_generator, sample_index_data):
        """Test: Statistics calculated from phase data."""
        with patch.object(dashboard_generator, '_load_index', return_value=sample_index_data):
            dashboard_data = dashboard_generator.generate_dashboard_data()
            
            assert dashboard_data.completion_rate == pytest.approx(92.0, 0.1)  # 23/25
            assert dashboard_data.in_progress_count == 1
            assert dashboard_data.planned_count == 1

    def test_save_dashboard_json_writes_file(self, dashboard_generator):
        """Test: Dashboard JSON saved to correct location."""
        dashboard_data = DashboardData(
            total_phases=25,
            active_phases=2,
            completed_phases=23,
            completion_rate=92.0,
            phases=[]
        )
        
        mock_file = mock_open()
        with patch('builtins.open', mock_file):
            with patch('cortex.registry.dashboard_generator.Path.mkdir'):
                dashboard_generator.save_dashboard_json(dashboard_data)
                
                mock_file.assert_called_once()
                # Verify JSON was written
                written_data = ''.join(call.args[0] for call in mock_file().write.call_args_list)
                assert '"total_phases": 25' in written_data

    def test_dashboard_json_is_valid_json(self, dashboard_generator, sample_index_data):
        """Test: Generated JSON is parseable."""
        with patch.object(dashboard_generator, '_load_index', return_value=sample_index_data):
            dashboard_data = dashboard_generator.generate_dashboard_data()
            json_str = dashboard_generator.to_json(dashboard_data)
            
            # Should be valid JSON
            parsed = json.loads(json_str)
            assert parsed['total_phases'] == 25
            assert 'phases' in parsed


class TestDashboardHTMLUpdate:
    """Tests for dashboard HTML statistics update."""

    def test_update_html_statistics_replaces_values(self, dashboard_generator):
        """Test: HTML statistics updated with new values."""
        original_html = """
        <div class="stat-card">
            <div class="stat-value">{{TOTAL_PHASES}}</div>
            <div class="stat-label">Total Phases</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{{ACTIVE_PHASES}}</div>
            <div class="stat-label">Active</div>
        </div>
        """
        
        dashboard_data = DashboardData(
            total_phases=25,
            active_phases=2,
            completed_phases=23,
            completion_rate=92.0,
            phases=[]
        )
        
        updated_html = dashboard_generator.update_html_statistics(original_html, dashboard_data)
        
        assert "{{TOTAL_PHASES}}" not in updated_html
        assert "25" in updated_html
        assert "2" in updated_html

    def test_update_html_preserves_structure(self, dashboard_generator):
        """Test: HTML structure preserved during update."""
        original_html = '<div class="dashboard">{{TOTAL_PHASES}}</div>'
        
        dashboard_data = DashboardData(
            total_phases=25,
            active_phases=2,
            completed_phases=23,
            completion_rate=92.0,
            phases=[]
        )
        
        updated_html = dashboard_generator.update_html_statistics(original_html, dashboard_data)
        
        assert '<div class="dashboard">' in updated_html
        assert '</div>' in updated_html

    def test_save_updated_html_writes_file(self, dashboard_generator):
        """Test: Updated HTML saved to correct location."""
        html_content = "<html>Updated content</html>"
        
        mock_file = mock_open()
        with patch('builtins.open', mock_file):
            with patch('cortex.registry.dashboard_generator.Path.mkdir'):
                dashboard_generator.save_updated_html(html_content)
                
                mock_file.assert_called_once()
                mock_file().write.assert_called_with(html_content)


class TestDashboardSync:
    """Tests for dashboard sync operations."""

    def test_sync_dashboard_updates_both_json_and_html(self, dashboard_generator, sample_index_data):
        """Test: Sync updates both JSON data and HTML."""
        with patch.object(dashboard_generator, '_load_index', return_value=sample_index_data):
            with patch.object(dashboard_generator, 'save_dashboard_json') as mock_json:
                with patch.object(dashboard_generator, '_load_html_template', return_value="<html>{{TOTAL_PHASES}}</html>"):
                    with patch.object(dashboard_generator, 'save_updated_html') as mock_html:
                        result = dashboard_generator.sync_dashboard()
                        
                        assert result.success is True
                        mock_json.assert_called_once()
                        mock_html.assert_called_once()

    def test_sync_dashboard_handles_errors_gracefully(self, dashboard_generator):
        """Test: Sync errors handled gracefully."""
        with patch.object(dashboard_generator, '_load_index', side_effect=Exception("File error")):
            result = dashboard_generator.sync_dashboard()
            
            assert result.success is False
            assert "File error" in result.error_message

    def test_verify_sync_checks_json_html_consistency(self, dashboard_generator):
        """Test: Verify sync checks JSON/HTML consistency."""
        with patch.object(dashboard_generator, '_load_dashboard_json') as mock_json:
            with patch.object(dashboard_generator, '_load_dashboard_html') as mock_html:
                mock_json.return_value = {"total_phases": 25}
                mock_html.return_value = "<html>25</html>"
                
                is_synced = dashboard_generator.verify_sync()
                
                # Should check both files exist
                assert mock_json.called
                assert mock_html.called


class TestDashboardIntegration:
    """Integration tests for dashboard sync with PhaseManager."""

class TestDashboardData:
    """Tests for DashboardData model."""

    def test_dashboard_data_to_dict(self):
        """Test: DashboardData converts to dictionary."""
        data = DashboardData(
            total_phases=25,
            active_phases=2,
            completed_phases=23,
            completion_rate=92.0,
            phases=[]
        )
        
        data_dict = data.to_dict()
        
        assert data_dict['total_phases'] == 25
        assert data_dict['completion_rate'] == 92.0

    def test_phase_summary_to_dict(self):
        """Test: PhaseSummary converts to dictionary."""
        phase = PhaseSummary(
            id="phase-25",
            name="PLAN MODE",
            status="in-progress",
            priority="P0",
            progress="55%"
        )
        
        phase_dict = phase.to_dict()
        
        assert phase_dict['id'] == "phase-25"
        assert phase_dict['status'] == "in-progress"


class TestDashboardPaths:
    """Tests for dashboard file path resolution."""

    def test_dashboard_data_path_correct(self, dashboard_generator):
        """Test: Dashboard data path resolves correctly."""
        expected_path = Path("/fake/registry/dashboard/data/plan-summary.json")
        assert dashboard_generator.dashboard_data_path == expected_path

    def test_dashboard_html_path_correct(self, dashboard_generator):
        """Test: Dashboard HTML path resolves correctly."""
        expected_path = Path("/fake/registry/dashboard/index.html")
        assert dashboard_generator.dashboard_html_path == expected_path
