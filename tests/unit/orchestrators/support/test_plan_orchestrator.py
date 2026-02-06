"""
Unit Tests for PlanOrchestrator - Phase 25 Stage 4

Tests setup/teardown hooks, phase operations, and dashboard sync integration.

AC-ID: PHASE-25-STAGE-4-003
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, call
from pathlib import Path

from cortex.orchestrators.support.plan_orchestrator import (
    PlanOrchestrator,
    PlanSetupResult,
    PlanTeardownResult,
)
from cortex.registry.phase_manager import PhaseResolutionResult, PhaseOperation
from cortex.models.canonical_enums import IntentType


@pytest.fixture
def mock_phase_manager():
    """Mock PhaseManager for testing."""
    manager = Mock()
    manager.resolve_phase_operation = Mock()
    manager.create_phase = Mock()
    manager.update_phase = Mock()
    manager.complete_phase = Mock()
    manager.verify_sync_before_completion = Mock(return_value=True)
    return manager


@pytest.fixture
def mock_dashboard_generator():
    """Mock DashboardGenerator for testing."""
    generator = Mock()
    generator.sync_dashboard = Mock(return_value=True)
    return generator


@pytest.fixture
def mock_vacuum_orchestrator():
    """Mock VacuumOrchestrator for testing."""
    orchestrator = Mock()
    orchestrator.cleanup = Mock()
    return orchestrator


@pytest.fixture
def plan_orchestrator(tmp_path):
    """Create PlanOrchestrator instance with temporary registry."""
    registry_root = str(tmp_path / "registry")
    Path(registry_root).mkdir(parents=True, exist_ok=True)
    
    with patch('cortex.orchestrators.support.plan_orchestrator.PhaseManager') as MockPhaseManager, \
         patch('cortex.orchestrators.support.plan_orchestrator.DashboardGenerator') as MockDashGen:
        
        orchestrator = PlanOrchestrator(registry_root=registry_root)
        yield orchestrator


class TestPlanOrchestratorInitialization:
    """Test PlanOrchestrator initialization."""
    
    def test_initialization_with_default_registry(self):
        """Test initialization with default registry path."""
        with patch('cortex.orchestrators.support.plan_orchestrator.PhaseManager'), \
             patch('cortex.orchestrators.support.plan_orchestrator.DashboardGenerator'):
            orchestrator = PlanOrchestrator()
            assert str(orchestrator.registry_root) == "cortex-registry/_cortex-master"
    
    def test_initialization_with_custom_registry(self, tmp_path):
        """Test initialization with custom registry path."""
        custom_root = str(tmp_path / "custom")
        Path(custom_root).mkdir(parents=True, exist_ok=True)
        
        with patch('cortex.orchestrators.support.plan_orchestrator.PhaseManager'), \
             patch('cortex.orchestrators.support.plan_orchestrator.DashboardGenerator'):
            orchestrator = PlanOrchestrator(registry_root=custom_root)
            assert str(orchestrator.registry_root) == custom_root
    
    def test_phase_manager_initialized(self, plan_orchestrator):
        """Test that PhaseManager is initialized."""
        assert plan_orchestrator.phase_manager is not None
    
    def test_dashboard_generator_initialized(self, plan_orchestrator):
        """Test that DashboardGenerator is initialized."""
        assert plan_orchestrator.dashboard_generator is not None


class TestSetupPhase:
    """Test setup_phase pre-implementation hook."""
    
    def test_setup_phase_success(self, plan_orchestrator, mock_vacuum_orchestrator):
        """Test successful setup hook execution."""
        phase_id = "phase-25-test"
        
        with patch.object(plan_orchestrator, '_create_git_checkpoint', return_value=True), \
             patch.object(plan_orchestrator, '_run_vacuum_cleanup', return_value=True):
            
            result = plan_orchestrator.setup_phase(phase_id)
            
            assert result.success is True
            assert result.phase_id == phase_id
            assert result.checkpoint_created is True
            assert result.cleanup_performed is True
            assert result.error_message is None
    
    def test_setup_phase_checkpoint_failure(self, plan_orchestrator):
        """Test setup hook when git checkpoint fails."""
        phase_id = "phase-25-test"
        
        with patch.object(plan_orchestrator, '_create_git_checkpoint', return_value=False), \
             patch.object(plan_orchestrator, '_run_vacuum_cleanup', return_value=True):
            
            result = plan_orchestrator.setup_phase(phase_id)
            
            assert result.success is True  # Non-critical failure
            assert result.checkpoint_created is False
            assert result.cleanup_performed is True
    
    def test_setup_phase_vacuum_failure(self, plan_orchestrator):
        """Test setup hook when vacuum cleanup fails."""
        phase_id = "phase-25-test"
        
        with patch.object(plan_orchestrator, '_create_git_checkpoint', return_value=True), \
             patch.object(plan_orchestrator, '_run_vacuum_cleanup', return_value=False):
            
            result = plan_orchestrator.setup_phase(phase_id)
            
            assert result.success is True  # Non-critical failure
            assert result.checkpoint_created is True
            assert result.cleanup_performed is False
    
    def test_setup_phase_exception_handling(self, plan_orchestrator):
        """Test setup hook exception handling."""
        phase_id = "phase-25-test"
        
        with patch.object(plan_orchestrator, '_create_git_checkpoint', side_effect=Exception("Test error")):
            
            result = plan_orchestrator.setup_phase(phase_id)
            
            assert result.success is False
            assert "Test error" in result.error_message


class TestTeardownPhase:
    """Test teardown_phase post-completion hook."""
    
    def test_teardown_phase_success(self, plan_orchestrator):
        """Test successful teardown hook execution."""
        phase_id = "phase-25-test"
        
        with patch.object(plan_orchestrator, '_verify_deliverables', return_value=True), \
             patch.object(plan_orchestrator, '_run_vacuum_cleanup', return_value=True), \
             patch.object(plan_orchestrator, '_archive_artifacts', return_value=5), \
             patch.object(plan_orchestrator.dashboard_generator, 'sync_dashboard', return_value=True), \
             patch.object(plan_orchestrator, '_log_audit_trail', return_value=True):
            
            result = plan_orchestrator.teardown_phase(phase_id)
            
            assert result.success is True
            assert result.artifacts_cleaned == 5
            assert result.dashboard_synced is True
            assert result.audit_logged is True
            assert result.error_message is None
    
    def test_teardown_phase_deliverables_failure(self, plan_orchestrator):
        """Test teardown hook when deliverables verification fails."""
        phase_id = "phase-25-test"
        
        with patch.object(plan_orchestrator, '_verify_deliverables', return_value=False):
            
            result = plan_orchestrator.teardown_phase(phase_id)
            
            assert result.success is False
            assert "Deliverables verification failed" in result.error_message
    
    def test_teardown_phase_dashboard_sync_failure(self, plan_orchestrator):
        """Test teardown hook when dashboard sync fails."""
        phase_id = "phase-25-test"
        
        with patch.object(plan_orchestrator, '_verify_deliverables', return_value=True), \
             patch.object(plan_orchestrator, '_run_vacuum_cleanup', return_value=True), \
             patch.object(plan_orchestrator, '_archive_artifacts', return_value=3), \
             patch.object(plan_orchestrator.dashboard_generator, 'sync_dashboard', return_value=False), \
             patch.object(plan_orchestrator, '_log_audit_trail', return_value=True):
            
            result = plan_orchestrator.teardown_phase(phase_id)
            
            assert result.success is True  # Non-critical failure
            assert result.dashboard_synced is False
    
    def test_teardown_phase_exception_handling(self, plan_orchestrator):
        """Test teardown hook exception handling."""
        phase_id = "phase-25-test"
        
        with patch.object(plan_orchestrator, '_verify_deliverables', side_effect=Exception("Test error")):
            
            result = plan_orchestrator.teardown_phase(phase_id)
            
            assert result.success is False
            assert "Test error" in result.error_message


class TestResolvePhaseOperation:
    """Test resolve_phase_operation intelligent resolution."""
    
    def test_resolve_phase_operation_delegates_to_phase_manager(self, plan_orchestrator):
        """Test that resolution delegates to PhaseManager."""
        user_request = "continue with phase 25"
        
        mock_result = PhaseResolutionResult(
            operation=PhaseOperation.UPDATE,
            matched_phase_id="phase-25-test",
            match_score=0.85,
            rationale="High keyword match",
            confidence=0.9
        )
        
        plan_orchestrator.phase_manager.resolve_phase_operation = Mock(return_value=mock_result)
        
        result = plan_orchestrator.resolve_phase_operation(user_request)
        
        plan_orchestrator.phase_manager.resolve_phase_operation.assert_called_once_with(user_request)
        assert result == mock_result
    
    def test_resolve_phase_operation_exception_handling(self, plan_orchestrator):
        """Test resolution exception handling."""
        user_request = "invalid request"
        
        plan_orchestrator.phase_manager.resolve_phase_operation = Mock(
            side_effect=Exception("Resolution error")
        )
        
        with pytest.raises(Exception, match="Resolution error"):
            plan_orchestrator.resolve_phase_operation(user_request)


class TestPhaseOperations:
    """Test CRUD phase operations with auto-sync."""
    
    def test_create_phase_with_dashboard_sync(self, plan_orchestrator):
        """Test create_phase triggers dashboard sync."""
        phase_data = {
            "id": "phase-26-test",
            "title": "Test Phase",
            "description": "Test phase for unit tests"
        }
        
        plan_orchestrator.phase_manager.create_phase = Mock(return_value=True)
        plan_orchestrator.dashboard_generator.sync_dashboard = Mock(return_value=True)
        
        result = plan_orchestrator.create_phase(phase_data)
        
        assert result is True
        plan_orchestrator.phase_manager.create_phase.assert_called_once_with(phase_data)
        plan_orchestrator.dashboard_generator.sync_dashboard.assert_called_once()
    
    def test_update_phase_with_dashboard_sync(self, plan_orchestrator):
        """Test update_phase triggers dashboard sync."""
        phase_id = "phase-25-test"
        updates = {"status": "in_progress", "progress": 50}
        
        plan_orchestrator.phase_manager.update_phase = Mock(return_value=True)
        plan_orchestrator.dashboard_generator.sync_dashboard = Mock(return_value=True)
        
        result = plan_orchestrator.update_phase(phase_id, updates)
        
        assert result is True
        plan_orchestrator.phase_manager.update_phase.assert_called_once_with(phase_id, updates)
        plan_orchestrator.dashboard_generator.sync_dashboard.assert_called_once()
    
    def test_complete_phase_with_dashboard_sync(self, plan_orchestrator):
        """Test complete_phase triggers dashboard sync."""
        phase_id = "phase-25-test"
        
        plan_orchestrator.phase_manager.complete_phase = Mock(return_value=True)
        plan_orchestrator.dashboard_generator.sync_dashboard = Mock(return_value=True)
        
        result = plan_orchestrator.complete_phase(phase_id)
        
        assert result is True
        plan_orchestrator.phase_manager.complete_phase.assert_called_once_with(phase_id)
        plan_orchestrator.dashboard_generator.sync_dashboard.assert_called_once()
    
    def test_phase_operation_without_auto_sync(self, plan_orchestrator):
        """Test phase operation with auto_sync=False."""
        phase_id = "phase-25-test"
        updates = {"status": "in_progress"}
        
        plan_orchestrator.phase_manager.update_phase = Mock(return_value=True)
        plan_orchestrator.dashboard_generator.sync_dashboard = Mock()
        
        result = plan_orchestrator.update_phase(phase_id, updates, auto_sync=False)
        
        assert result is True
        plan_orchestrator.phase_manager.update_phase.assert_called_once()
        plan_orchestrator.dashboard_generator.sync_dashboard.assert_not_called()


class TestSyncDashboard:
    """Test manual dashboard sync."""
    
    def test_sync_dashboard_success(self, plan_orchestrator):
        """Test successful manual dashboard sync."""
        plan_orchestrator.dashboard_generator.sync_dashboard = Mock(return_value=True)
        
        result = plan_orchestrator.sync_dashboard()
        
        assert result is True
        plan_orchestrator.dashboard_generator.sync_dashboard.assert_called_once()
    
    def test_sync_dashboard_failure(self, plan_orchestrator):
        """Test dashboard sync failure."""
        plan_orchestrator.dashboard_generator.sync_dashboard = Mock(return_value=False)
        
        result = plan_orchestrator.sync_dashboard()
        
        assert result is False


class TestPrioritizePendingPhases:
    """Test prioritize_pending_phases ROI-based sorting."""
    
    def test_prioritize_phases_by_roi(self, plan_orchestrator):
        """Test phases are prioritized by ROI score."""
        phases = [
            {"id": "phase-1", "roi_score": 0.5},
            {"id": "phase-2", "roi_score": 0.9},
            {"id": "phase-3", "roi_score": 0.7}
        ]
        
        # Mock the phase_manager method to return sorted phases
        sorted_phases = sorted(phases, key=lambda p: p.get("roi_score", 0.0), reverse=True)
        plan_orchestrator.phase_manager.prioritize_pending_phases = Mock(return_value=sorted_phases)
        
        result = plan_orchestrator.prioritize_pending_phases()
        
        # Should be sorted descending by ROI
        assert result[0]["id"] == "phase-2"  # 0.9
        assert result[1]["id"] == "phase-3"  # 0.7
        assert result[2]["id"] == "phase-1"  # 0.5
    
    def test_prioritize_phases_empty_list(self, plan_orchestrator):
        """Test prioritization with no pending phases."""
        plan_orchestrator.phase_manager.prioritize_pending_phases = Mock(return_value=[])
        result = plan_orchestrator.prioritize_pending_phases()
        assert result == []


class TestHelperMethods:
    """Test private helper methods."""
    
    def test_create_git_checkpoint(self, plan_orchestrator):
        """Test git checkpoint creation."""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(returncode=0)
            
            result = plan_orchestrator._create_git_checkpoint("test-checkpoint")
            
            assert result is True
            assert mock_run.call_count >= 1  # At least git status
    
    def test_run_vacuum_cleanup(self, plan_orchestrator):
        """Test vacuum cleanup execution."""
        # Placeholder test - VacuumOrchestrator integration pending
        result = plan_orchestrator._run_vacuum_cleanup()
        
        # Should return True (no-op until Stage 5)
        assert result is True
    
    def test_verify_deliverables(self, plan_orchestrator):
        """Test deliverables verification."""
        phase_id = "phase-25-test"
        
        # Placeholder test - verification logic pending
        result = plan_orchestrator._verify_deliverables(phase_id)
        
        # Should return True (basic implementation)
        assert result is True
    
    def test_archive_artifacts(self, plan_orchestrator):
        """Test artifact archival."""
        phase_id = "phase-25-test"
        
        # Placeholder test - archival logic pending
        result = plan_orchestrator._archive_artifacts(phase_id)
        
        # Should return count (0 for now)
        assert result >= 0
    
    def test_log_audit_trail(self, plan_orchestrator):
        """Test audit trail logging."""
        phase_id = "phase-25-test"
        operation = "COMPLETE"
        
        result = plan_orchestrator._log_audit_trail(phase_id, operation)
        
        # Should return True (logging successful)
        assert result is True


class TestIntegrationScenarios:
    """Test end-to-end integration scenarios."""
    
    def test_full_phase_lifecycle(self, plan_orchestrator):
        """Test complete phase lifecycle: setup → update → teardown."""
        phase_id = "phase-test-lifecycle"
        
        # Setup phase
        with patch.object(plan_orchestrator, '_create_git_checkpoint', return_value=True), \
             patch.object(plan_orchestrator, '_run_vacuum_cleanup', return_value=True):
            
            setup_result = plan_orchestrator.setup_phase(phase_id)
            assert setup_result.success is True
        
        # Update phase
        plan_orchestrator.phase_manager.update_phase = Mock(return_value=True)
        plan_orchestrator.dashboard_generator.sync_dashboard = Mock(return_value=True)
        
        update_result = plan_orchestrator.update_phase(phase_id, {"progress": 50})
        assert update_result is True
        
        # Teardown phase
        with patch.object(plan_orchestrator, '_verify_deliverables', return_value=True), \
             patch.object(plan_orchestrator, '_run_vacuum_cleanup', return_value=True), \
             patch.object(plan_orchestrator, '_archive_artifacts', return_value=3), \
             patch.object(plan_orchestrator.dashboard_generator, 'sync_dashboard', return_value=True), \
             patch.object(plan_orchestrator, '_log_audit_trail', return_value=True):
            
            teardown_result = plan_orchestrator.teardown_phase(phase_id)
            assert teardown_result.success is True
            assert teardown_result.artifacts_cleaned == 3
    
    def test_phase_creation_workflow(self, plan_orchestrator):
        """Test creating a new phase with full integration."""
        phase_data = {
            "id": "phase-27-test",
            "title": "New Test Phase",
            "description": "Integration test phase",
            "priority": "high"
        }
        
        # Mock PhaseManager and DashboardGenerator
        plan_orchestrator.phase_manager.create_phase = Mock(return_value=True)
        plan_orchestrator.dashboard_generator.sync_dashboard = Mock(return_value=True)
        
        # Create phase
        result = plan_orchestrator.create_phase(phase_data)
        
        # Verify integration
        assert result is True
        plan_orchestrator.phase_manager.create_phase.assert_called_once_with(phase_data)
        plan_orchestrator.dashboard_generator.sync_dashboard.assert_called_once()
