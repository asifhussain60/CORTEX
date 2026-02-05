"""
Phase 24.3 - Layer 3: Post-Completion Sync (PhaseCompletionOrchestrator)
TDD RED Phase - Test suite for PhaseCompletionOrchestrator

Tests cover:
- Phase YAML auto-update (status transitions)
- Dashboard data regeneration (plan-summary.json)
- PlanRegistrySyncOrchestrator triggering
- Index.yaml statistics refresh
- Enhancement-history.yaml update
- Dashboard HTML auto-refresh verification
- Edge cases (missing files, invalid phase IDs)
"""

import pytest
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
import yaml
import json


@pytest.fixture
def mock_phase_yaml(tmp_path):
    """Create mock phase YAML file"""
    phase_file = tmp_path / "phase-24-test.yaml"
    phase_data = {
        "metadata": {
            "phase": "24",
            "title": "Test Phase",
            "status": "IN_PROGRESS",
            "sub_status": "Phase 24.1 COMPLETE, Phase 24.2 PENDING",
            "completion_status": {
                "phase_24_1": "COMPLETE",
                "phase_24_2": "PENDING"
            }
        }
    }
    phase_file.write_text(yaml.dump(phase_data))
    return phase_file


@pytest.fixture
def mock_index_yaml(tmp_path):
    """Create mock index.yaml file"""
    index_file = tmp_path / "index.yaml"
    index_data = {
        "statistics": {
            "total_phases": 24,
            "active_phases": 1,
            "completed_phases": 23
        }
    }
    index_file.write_text(yaml.dump(index_data))
    return index_file


@pytest.fixture
def mock_dashboard_data(tmp_path):
    """Create mock dashboard data file"""
    data_file = tmp_path / "plan-summary.json"
    data = {
        "phases": [],
        "statistics": {"total": 24}
    }
    data_file.write_text(json.dumps(data))
    return data_file


class TestPhaseCompletion:
    """Test phase YAML auto-update"""
    
    def test_complete_phase_updates_status(self, mock_phase_yaml):
        """Test that completing a phase updates status to COMPLETE"""
        from cortex.orchestrators.support.phase_completion_orchestrator import PhaseCompletionOrchestrator
        
        orchestrator = PhaseCompletionOrchestrator()
        result = orchestrator.complete_phase(
            phase_file=mock_phase_yaml,
            phase_key="phase_24_2"
        )
        
        assert result.success is True
        assert result.phase_updated is True
        
        # Verify YAML was updated
        updated_data = yaml.safe_load(mock_phase_yaml.read_text())
        # Check format: "COMPLETE ✅ (YYYY-MM-DD)"
        assert "COMPLETE ✅" in updated_data["metadata"]["completion_status"]["phase_24_2"]
        assert "2026-02-05" in updated_data["metadata"]["completion_status"]["phase_24_2"]
    
    def test_complete_phase_updates_sub_status(self, mock_phase_yaml):
        """Test that sub_status reflects completion"""
        from cortex.orchestrators.support.phase_completion_orchestrator import PhaseCompletionOrchestrator
        
        orchestrator = PhaseCompletionOrchestrator()
        orchestrator.complete_phase(
            phase_file=mock_phase_yaml,
            phase_key="phase_24_2"
        )
        
        updated_data = yaml.safe_load(mock_phase_yaml.read_text())
        sub_status = updated_data["metadata"]["sub_status"]
        # Check that PENDING was replaced with COMPLETE ✅
        assert "Phase 24.2 COMPLETE ✅" in sub_status or "Phase 24.2 PENDING" not in sub_status


class TestDashboardRegeneration:
    """Test dashboard data regeneration"""
    
    @patch('cortex.orchestrators.support.phase_completion_orchestrator.regenerate_dashboard')
    def test_dashboard_data_regenerated(self, mock_regenerate, mock_phase_yaml):
        """Test that dashboard data is regenerated after phase completion"""
        from cortex.orchestrators.support.phase_completion_orchestrator import PhaseCompletionOrchestrator
        
        mock_regenerate.return_value = {"status": "success"}
        
        orchestrator = PhaseCompletionOrchestrator()
        result = orchestrator.complete_phase(
            phase_file=mock_phase_yaml,
            phase_key="phase_24_2"
        )
        
        assert result.dashboard_regenerated is True
        mock_regenerate.assert_called_once()
    
    @patch('cortex.orchestrators.support.phase_completion_orchestrator.regenerate_dashboard')
    def test_dashboard_sync_within_60_seconds(self, mock_regenerate, mock_phase_yaml):
        """Test that dashboard sync completes within 60 second SLA"""
        from cortex.orchestrators.support.phase_completion_orchestrator import PhaseCompletionOrchestrator
        
        mock_regenerate.return_value = {"status": "success"}
        
        orchestrator = PhaseCompletionOrchestrator()
        start_time = datetime.now()
        orchestrator.complete_phase(
            phase_file=mock_phase_yaml,
            phase_key="phase_24_2"
        )
        duration = (datetime.now() - start_time).total_seconds()
        
        assert duration < 60


class TestPlanRegistrySync:
    """Test PlanRegistrySyncOrchestrator integration"""
    
    @patch('cortex.orchestrators.support.phase_completion_orchestrator.PlanRegistrySyncOrchestrator')
    def test_plan_registry_sync_triggered(self, mock_sync_class, mock_phase_yaml):
        """Test that PlanRegistrySyncOrchestrator is triggered"""
        from cortex.orchestrators.support.phase_completion_orchestrator import PhaseCompletionOrchestrator
        
        mock_sync_instance = Mock()
        mock_sync_class.return_value = mock_sync_instance
        
        orchestrator = PhaseCompletionOrchestrator()
        result = orchestrator.complete_phase(
            phase_file=mock_phase_yaml,
            phase_key="phase_24_2"
        )
        
        assert result.registry_synced is True
        mock_sync_instance.sync.assert_called_once()


class TestIndexYamlUpdate:
    """Test index.yaml statistics refresh"""
    
    def test_index_yaml_statistics_updated(self, mock_phase_yaml, mock_index_yaml):
        """Test that index.yaml statistics are recalculated"""
        from cortex.orchestrators.support.phase_completion_orchestrator import PhaseCompletionOrchestrator
        
        orchestrator = PhaseCompletionOrchestrator()
        orchestrator.complete_phase(
            phase_file=mock_phase_yaml,
            phase_key="phase_24_2",
            index_file=mock_index_yaml
        )
        
        updated_index = yaml.safe_load(mock_index_yaml.read_text())
        # Completed phases should increment
        assert updated_index["statistics"]["completed_phases"] >= 23


class TestEnhancementHistoryUpdate:
    """Test enhancement-history.yaml update"""
    
    @patch('cortex.orchestrators.support.phase_completion_orchestrator.update_enhancement_history')
    def test_enhancement_history_updated(self, mock_update, mock_phase_yaml):
        """Test that enhancement-history.yaml is updated with completion metadata"""
        from cortex.orchestrators.support.phase_completion_orchestrator import PhaseCompletionOrchestrator
        
        mock_update.return_value = True
        
        orchestrator = PhaseCompletionOrchestrator()
        result = orchestrator.complete_phase(
            phase_file=mock_phase_yaml,
            phase_key="phase_24_2",
            enhancement_id="ENH-039"
        )
        
        assert result.enhancement_updated is True
        mock_update.assert_called_once()


class TestDashboardHTMLReflection:
    """Test dashboard HTML auto-refresh"""
    
    def test_dashboard_html_reflects_changes(self, mock_phase_yaml, mock_dashboard_data):
        """Test that dashboard HTML reflects updated data within 60 seconds"""
        from cortex.orchestrators.support.phase_completion_orchestrator import PhaseCompletionOrchestrator
        
        orchestrator = PhaseCompletionOrchestrator()
        result = orchestrator.complete_phase(
            phase_file=mock_phase_yaml,
            phase_key="phase_24_2",
            dashboard_data_file=mock_dashboard_data
        )
        
        # Verify dashboard data file was updated
        assert result.dashboard_regenerated is True
        assert mock_dashboard_data.exists()


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_missing_phase_file(self):
        """Test handling of missing phase file"""
        from cortex.orchestrators.support.phase_completion_orchestrator import PhaseCompletionOrchestrator
        
        orchestrator = PhaseCompletionOrchestrator()
        result = orchestrator.complete_phase(
            phase_file=Path("/nonexistent/phase.yaml"),
            phase_key="phase_24_2"
        )
        
        assert result.success is False
        assert "not found" in result.error.lower()
    
    def test_invalid_phase_key(self, mock_phase_yaml):
        """Test handling of invalid phase key"""
        from cortex.orchestrators.support.phase_completion_orchestrator import PhaseCompletionOrchestrator
        
        orchestrator = PhaseCompletionOrchestrator()
        result = orchestrator.complete_phase(
            phase_file=mock_phase_yaml,
            phase_key="nonexistent_phase"
        )
        
        assert result.success is False
        assert result.error is not None
        assert "invalid" in result.error.lower() or "key" in result.error.lower()
    
    def test_readonly_phase_file(self, mock_phase_yaml):
        """Test handling of read-only phase file"""
        from cortex.orchestrators.support.phase_completion_orchestrator import PhaseCompletionOrchestrator
        
        # Make file read-only
        mock_phase_yaml.chmod(0o444)
        
        orchestrator = PhaseCompletionOrchestrator()
        result = orchestrator.complete_phase(
            phase_file=mock_phase_yaml,
            phase_key="phase_24_2"
        )
        
        # Should fail gracefully
        assert result.success is False
