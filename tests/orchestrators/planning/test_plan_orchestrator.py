"""
Tests for Plan Orchestrator - Infrastructure Integration

Tests the refactored plan_orchestrator.py that uses:
- PlanningStateDB for state persistence
- StateManager for execution tracking
- OrchestratorRegistry for dynamic discovery

Author: CORTEX
Created: January 3, 2026
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch, call
from datetime import datetime

# Add plan orchestrator to path
PLAN_ROOT = Path(__file__).parent.parent.parent.parent / "cortex-brain/documents/planning/active/CORTEX-5.0"
sys.path.insert(0, str(PLAN_ROOT))

from plan_orchestrator import PlanOrchestrator


# ============================================================================
# Test Group 1: Initialization & Infrastructure Integration (4 tests)
# ============================================================================

class TestInitialization:
    """Test PlanOrchestrator initialization with infrastructure components."""
    
    def test_initialization_creates_infrastructure_components(self):
        """Should initialize PlanningStateDB, StateManager, and OrchestratorRegistry."""
        with patch('plan_orchestrator.PlanningStateDB') as mock_db_class, \
             patch('plan_orchestrator.StateManager') as mock_sm_class, \
             patch('plan_orchestrator.OrchestratorRegistry') as mock_reg_class:
            
            mock_db = Mock()
            mock_db_class.return_value = mock_db
            mock_sm = Mock()
            mock_sm_class.return_value = mock_sm
            mock_reg = Mock()
            mock_reg_class.get_instance.return_value = mock_reg
            
            # Mock _initialize_plan_state to avoid DB operations
            with patch.object(PlanOrchestrator, '_initialize_plan_state'):
                orchestrator = PlanOrchestrator(Path("/test/plan"))
            
            # Verify infrastructure components created
            assert orchestrator.db == mock_db
            assert orchestrator.state_mgr == mock_sm
            assert orchestrator.registry == mock_reg
    
    def test_initialization_discovers_orchestrators(self):
        """Should discover orchestrators from src/orchestrators directory."""
        with patch('plan_orchestrator.PlanningStateDB'), \
             patch('plan_orchestrator.StateManager'), \
             patch('plan_orchestrator.OrchestratorRegistry') as mock_reg_class:
            
            mock_reg = Mock()
            mock_reg_class.get_instance.return_value = mock_reg
            
            with patch.object(PlanOrchestrator, '_initialize_plan_state'):
                PlanOrchestrator(Path("/test/plan"))
            
            # Verify discover called with correct path
            mock_reg.discover.assert_called_once()
            args = mock_reg.discover.call_args[0][0]
            assert len(args) == 1
            assert str(args[0]).endswith("src/orchestrators")
    
    def test_initialization_calls_initialize_plan_state(self):
        """Should call _initialize_plan_state during initialization."""
        with patch('plan_orchestrator.PlanningStateDB'), \
             patch('plan_orchestrator.StateManager'), \
             patch('plan_orchestrator.OrchestratorRegistry.get_instance'), \
             patch.object(PlanOrchestrator, '_initialize_plan_state') as mock_init:
            
            PlanOrchestrator(Path("/test/plan"))
            
            mock_init.assert_called_once()
    
    def test_initialize_plan_state_creates_plan_if_not_exists(self):
        """Should create plan in database if it doesn't exist."""
        with patch('plan_orchestrator.PlanningStateDB') as mock_db_class, \
             patch('plan_orchestrator.StateManager'), \
             patch('plan_orchestrator.OrchestratorRegistry.get_instance'):
            
            mock_db = Mock()
            mock_db_class.return_value = mock_db
            mock_db.get_plan_state.return_value = None  # Plan doesn't exist
            
            orchestrator = PlanOrchestrator(Path("/test/plan"))
            
            # Verify create_plan called with correct parameters
            mock_db.create_plan.assert_called_once()
            call_args = mock_db.create_plan.call_args
            assert call_args[1]['plan_id'] == "cortex-v5-gap-remediation"
            assert call_args[1]['name'] == "CORTEX-5.0 Gap Remediation"
            assert 'session_count' in call_args[1]['metadata']


# ============================================================================
# Test Group 2: Database Integration (5 tests)
# ============================================================================

class TestDatabaseIntegration:
    """Test database queries replace JSON file I/O."""
    
    def test_show_status_queries_database(self, capsys):
        """Should query database for plan state instead of reading JSON files."""
        with patch('plan_orchestrator.PlanningStateDB') as mock_db_class, \
             patch('plan_orchestrator.StateManager'), \
             patch('plan_orchestrator.OrchestratorRegistry.get_instance'), \
             patch.object(PlanOrchestrator, '_initialize_plan_state'):
            
            mock_db = Mock()
            mock_db_class.return_value = mock_db
            mock_db.get_plan_state.return_value = {
                "metadata": {"session_count": 5},
                "updated_at": "2026-01-03T10:00:00"
            }
            mock_db.get_sub_plans.return_value = [
                {"order": "00", "name": "Test Plan", "status": "in_progress", "progress": 50}
            ]
            
            orchestrator = PlanOrchestrator(Path("/test/plan"))
            orchestrator.show_status()
            
            # Verify database queries called
            mock_db.get_plan_state.assert_called_with("cortex-v5-gap-remediation")
            mock_db.get_sub_plans.assert_called_with("cortex-v5-gap-remediation")
            
            # Verify output contains database data
            captured = capsys.readouterr()
            assert "Session Count: 5" in captured.out
            assert "Test Plan" in captured.out
    
    def test_get_next_available_sub_plan_uses_database_query(self):
        """Should use PlanningStateDB.get_next_phase() instead of manual iteration."""
        with patch('plan_orchestrator.PlanningStateDB') as mock_db_class, \
             patch('plan_orchestrator.StateManager'), \
             patch('plan_orchestrator.OrchestratorRegistry.get_instance'), \
             patch.object(PlanOrchestrator, '_initialize_plan_state'):
            
            mock_db = Mock()
            mock_db_class.return_value = mock_db
            mock_db.get_next_phase.return_value = {"order": "01", "name": "Next Phase"}
            
            orchestrator = PlanOrchestrator(Path("/test/plan"))
            result = orchestrator.get_next_available_sub_plan()
            
            # Verify database query used
            mock_db.get_next_phase.assert_called_with("cortex-v5-gap-remediation")
            assert result["order"] == "01"
    
    def test_dependencies_met_queries_database(self):
        """Should query database for dependency status instead of manual dict lookup."""
        with patch('plan_orchestrator.PlanningStateDB') as mock_db_class, \
             patch('plan_orchestrator.StateManager'), \
             patch('plan_orchestrator.OrchestratorRegistry.get_instance'), \
             patch.object(PlanOrchestrator, '_initialize_plan_state'):
            
            mock_db = Mock()
            mock_db_class.return_value = mock_db
            mock_db.get_sub_plan.return_value = {"status": "complete"}
            
            orchestrator = PlanOrchestrator(Path("/test/plan"))
            sub_plan = {"dependencies": ["00"]}
            
            result = orchestrator._dependencies_met(sub_plan)
            
            # Verify database query for dependency
            mock_db.get_sub_plan.assert_called_with("cortex-v5-gap-remediation", "00")
            assert result is True
    
    def test_start_sub_plan_updates_database(self):
        """Should update database state instead of writing JSON files."""
        with patch('plan_orchestrator.PlanningStateDB') as mock_db_class, \
             patch('plan_orchestrator.StateManager') as mock_sm_class, \
             patch('plan_orchestrator.OrchestratorRegistry.get_instance'), \
             patch.object(PlanOrchestrator, '_initialize_plan_state'):
            
            mock_db = Mock()
            mock_db_class.return_value = mock_db
            mock_db.get_sub_plan.return_value = {
                "order": "00",
                "name": "Test",
                "status": "not_started",
                "dependencies": []
            }
            mock_db.get_plan_state.return_value = {"metadata": {}}
            
            mock_sm = Mock()
            mock_sm_class.return_value = mock_sm
            
            orchestrator = PlanOrchestrator(Path("/test/plan"))
            orchestrator.start_sub_plan("00", silent=True)
            
            # Verify database updates
            mock_db.update_sub_plan_status.assert_called_with(
                "cortex-v5-gap-remediation", "00", "in_progress"
            )
    
    def test_complete_sub_plan_updates_database(self):
        """Should mark sub-plan complete in database."""
        with patch('plan_orchestrator.PlanningStateDB') as mock_db_class, \
             patch('plan_orchestrator.StateManager'), \
             patch('plan_orchestrator.OrchestratorRegistry.get_instance'), \
             patch.object(PlanOrchestrator, '_initialize_plan_state'):
            
            mock_db = Mock()
            mock_db_class.return_value = mock_db
            mock_db.get_sub_plan.return_value = {"order": "00", "name": "Test"}
            mock_db.get_sub_plans.return_value = []
            
            orchestrator = PlanOrchestrator(Path("/test/plan"))
            orchestrator.complete_sub_plan("00", silent=True)
            
            # Verify database updates
            mock_db.update_sub_plan_status.assert_called_with(
                "cortex-v5-gap-remediation", "00", "complete"
            )
            mock_db.update_sub_plan_progress.assert_called_with(
                "cortex-v5-gap-remediation", "00", 100
            )


# ============================================================================
# Test Group 3: StateManager Integration (3 tests)
# ============================================================================

class TestStateManagerIntegration:
    """Test StateManager execution tracking."""
    
    def test_start_sub_plan_begins_execution_tracking(self):
        """Should call StateManager.begin_execution when starting sub-plan."""
        with patch('plan_orchestrator.PlanningStateDB') as mock_db_class, \
             patch('plan_orchestrator.StateManager') as mock_sm_class, \
             patch('plan_orchestrator.OrchestratorRegistry.get_instance'), \
             patch.object(PlanOrchestrator, '_initialize_plan_state'):
            
            mock_db = Mock()
            mock_db_class.return_value = mock_db
            mock_db.get_sub_plan.return_value = {
                "order": "00",
                "name": "Test",
                "status": "not_started",
                "dependencies": []
            }
            mock_db.get_plan_state.return_value = {"metadata": {}}
            
            mock_sm = Mock()
            mock_sm_class.return_value = mock_sm
            mock_sm.begin_execution.return_value = "log_123"
            
            orchestrator = PlanOrchestrator(Path("/test/plan"))
            orchestrator.start_sub_plan("00", silent=True)
            
            # Verify StateManager.begin_execution called
            mock_sm.begin_execution.assert_called_once()
            call_args = mock_sm.begin_execution.call_args[1]
            assert call_args['orchestrator_id'] == "subplan_00"
            assert 'sub_plan' in call_args['parameters']
    
    def test_auto_execute_increments_session_count(self):
        """Should increment session count in metadata."""
        with patch('plan_orchestrator.PlanningStateDB') as mock_db_class, \
             patch('plan_orchestrator.StateManager'), \
             patch('plan_orchestrator.OrchestratorRegistry.get_instance'), \
             patch.object(PlanOrchestrator, '_initialize_plan_state'):
            
            mock_db = Mock()
            mock_db_class.return_value = mock_db
            mock_db.get_plan_state.return_value = {"metadata": {"session_count": 5}}
            mock_db.get_next_phase.return_value = None  # No next phase
            
            orchestrator = PlanOrchestrator(Path("/test/plan"))
            orchestrator.auto_execute()
            
            # Verify session count incremented
            mock_db.update_plan_metadata.assert_called_once()
            call_args = mock_db.update_plan_metadata.call_args[0]
            assert call_args[1]["session_count"] == 6
    
    def test_add_note_stores_in_metadata(self):
        """Should store notes in plan metadata."""
        with patch('plan_orchestrator.PlanningStateDB') as mock_db_class, \
             patch('plan_orchestrator.StateManager'), \
             patch('plan_orchestrator.OrchestratorRegistry.get_instance'), \
             patch.object(PlanOrchestrator, '_initialize_plan_state'):
            
            mock_db = Mock()
            mock_db_class.return_value = mock_db
            mock_db.get_plan_state.return_value = {"metadata": {"notes": []}}
            
            orchestrator = PlanOrchestrator(Path("/test/plan"))
            orchestrator.add_note("Test note", silent=True)
            
            # Verify note stored in metadata
            mock_db.update_plan_metadata.assert_called_once()
            call_args = mock_db.update_plan_metadata.call_args[0]
            assert len(call_args[1]["notes"]) == 1
            assert call_args[1]["notes"][0]["note"] == "Test note"


# ============================================================================
# Test Group 4: OrchestratorRegistry Integration (2 tests)
# ============================================================================

class TestOrchestratorRegistryIntegration:
    """Test dynamic orchestrator discovery."""
    
    def test_registry_singleton_pattern(self):
        """Should use OrchestratorRegistry singleton."""
        with patch('plan_orchestrator.PlanningStateDB'), \
             patch('plan_orchestrator.StateManager'), \
             patch('plan_orchestrator.OrchestratorRegistry') as mock_reg_class, \
             patch.object(PlanOrchestrator, '_initialize_plan_state'):
            
            mock_reg = Mock()
            mock_reg_class.get_instance.return_value = mock_reg
            
            orchestrator = PlanOrchestrator(Path("/test/plan"))
            
            # Verify singleton pattern used
            mock_reg_class.get_instance.assert_called_once()
            assert orchestrator.registry == mock_reg
    
    def test_discover_called_on_initialization(self):
        """Should discover orchestrators during initialization."""
        with patch('plan_orchestrator.PlanningStateDB'), \
             patch('plan_orchestrator.StateManager'), \
             patch('plan_orchestrator.OrchestratorRegistry') as mock_reg_class, \
             patch.object(PlanOrchestrator, '_initialize_plan_state'):
            
            mock_reg = Mock()
            mock_reg_class.get_instance.return_value = mock_reg
            
            PlanOrchestrator(Path("/test/plan"))
            
            # Verify discover called
            mock_reg.discover.assert_called_once()


# ============================================================================
# Test Group 5: CLI Interface Compatibility (4 tests)
# ============================================================================

class TestCLICompatibility:
    """Test that CLI interface remains unchanged."""
    
    def test_status_command_displays_plan_status(self, capsys):
        """Should display status when called."""
        with patch('plan_orchestrator.PlanningStateDB') as mock_db_class, \
             patch('plan_orchestrator.StateManager'), \
             patch('plan_orchestrator.OrchestratorRegistry.get_instance'), \
             patch.object(PlanOrchestrator, '_initialize_plan_state'):
            
            mock_db = Mock()
            mock_db_class.return_value = mock_db
            mock_db.get_plan_state.return_value = {"metadata": {}, "updated_at": "2026-01-03"}
            mock_db.get_sub_plans.return_value = []
            
            orchestrator = PlanOrchestrator(Path("/test/plan"))
            orchestrator.show_status()
            
            captured = capsys.readouterr()
            assert "CORTEX-5.0 Plan Orchestrator Status" in captured.out
            assert "Overall Progress" in captured.out
    
    def test_start_command_starts_sub_plan(self):
        """Should start specific sub-plan when requested."""
        with patch('plan_orchestrator.PlanningStateDB') as mock_db_class, \
             patch('plan_orchestrator.StateManager'), \
             patch('plan_orchestrator.OrchestratorRegistry.get_instance'), \
             patch.object(PlanOrchestrator, '_initialize_plan_state'):
            
            mock_db = Mock()
            mock_db_class.return_value = mock_db
            mock_db.get_sub_plan.return_value = {
                "order": "01",
                "name": "Test",
                "status": "not_started",
                "dependencies": []
            }
            mock_db.get_plan_state.return_value = {"metadata": {}}
            
            orchestrator = PlanOrchestrator(Path("/test/plan"))
            result = orchestrator.start_sub_plan("01", silent=True)
            
            assert result is True
    
    def test_update_command_updates_progress(self):
        """Should update progress when requested."""
        with patch('plan_orchestrator.PlanningStateDB') as mock_db_class, \
             patch('plan_orchestrator.StateManager'), \
             patch('plan_orchestrator.OrchestratorRegistry.get_instance'), \
             patch.object(PlanOrchestrator, '_initialize_plan_state'):
            
            mock_db = Mock()
            mock_db_class.return_value = mock_db
            mock_db.get_sub_plan.return_value = {"order": "00"}
            
            orchestrator = PlanOrchestrator(Path("/test/plan"))
            orchestrator.update_progress("00", 75, silent=True)
            
            mock_db.update_sub_plan_progress.assert_called_with(
                "cortex-v5-gap-remediation", "00", 75
            )
    
    def test_complete_command_completes_sub_plan(self):
        """Should complete sub-plan when requested."""
        with patch('plan_orchestrator.PlanningStateDB') as mock_db_class, \
             patch('plan_orchestrator.StateManager'), \
             patch('plan_orchestrator.OrchestratorRegistry.get_instance'), \
             patch.object(PlanOrchestrator, '_initialize_plan_state'):
            
            mock_db = Mock()
            mock_db_class.return_value = mock_db
            mock_db.get_sub_plan.return_value = {"order": "00", "name": "Test"}
            mock_db.get_sub_plans.return_value = []
            
            orchestrator = PlanOrchestrator(Path("/test/plan"))
            orchestrator.complete_sub_plan("00", silent=True)
            
            mock_db.update_sub_plan_status.assert_called_with(
                "cortex-v5-gap-remediation", "00", "complete"
            )


# ============================================================================
# Test Group 6: Error Handling (3 tests)
# ============================================================================

class TestErrorHandling:
    """Test error handling for edge cases."""
    
    def test_start_nonexistent_sub_plan_returns_false(self):
        """Should return False when trying to start non-existent sub-plan."""
        with patch('plan_orchestrator.PlanningStateDB') as mock_db_class, \
             patch('plan_orchestrator.StateManager'), \
             patch('plan_orchestrator.OrchestratorRegistry.get_instance'), \
             patch.object(PlanOrchestrator, '_initialize_plan_state'):
            
            mock_db = Mock()
            mock_db_class.return_value = mock_db
            mock_db.get_sub_plan.return_value = None
            
            orchestrator = PlanOrchestrator(Path("/test/plan"))
            result = orchestrator.start_sub_plan("99", silent=True)
            
            assert result is False
    
    def test_start_already_complete_sub_plan_returns_false(self):
        """Should return False when trying to start already complete sub-plan."""
        with patch('plan_orchestrator.PlanningStateDB') as mock_db_class, \
             patch('plan_orchestrator.StateManager'), \
             patch('plan_orchestrator.OrchestratorRegistry.get_instance'), \
             patch.object(PlanOrchestrator, '_initialize_plan_state'):
            
            mock_db = Mock()
            mock_db_class.return_value = mock_db
            mock_db.get_sub_plan.return_value = {
                "order": "00",
                "status": "complete"
            }
            
            orchestrator = PlanOrchestrator(Path("/test/plan"))
            result = orchestrator.start_sub_plan("00", silent=True)
            
            assert result is False
    
    def test_auto_execute_with_no_available_sub_plans(self, capsys):
        """Should handle case when no sub-plans are available."""
        with patch('plan_orchestrator.PlanningStateDB') as mock_db_class, \
             patch('plan_orchestrator.StateManager'), \
             patch('plan_orchestrator.OrchestratorRegistry.get_instance'), \
             patch.object(PlanOrchestrator, '_initialize_plan_state'):
            
            mock_db = Mock()
            mock_db_class.return_value = mock_db
            mock_db.get_plan_state.return_value = {"metadata": {}}
            mock_db.get_next_phase.return_value = None
            
            orchestrator = PlanOrchestrator(Path("/test/plan"))
            result = orchestrator.auto_execute()
            
            assert result is None
            captured = capsys.readouterr()
            assert "complete or blocked" in captured.out


# ============================================================================
# Summary: 21 Tests Total
# ============================================================================
# Group 1: Initialization & Infrastructure (4 tests)
# Group 2: Database Integration (5 tests)
# Group 3: StateManager Integration (3 tests)
# Group 4: OrchestratorRegistry Integration (2 tests)
# Group 5: CLI Compatibility (4 tests)
# Group 6: Error Handling (3 tests)
