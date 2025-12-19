"""
Tests for Plan Lifecycle Manager

Tests plan state machine, DoR approval workflow, folder transitions,
and progress persistence.

Author: Asif Hussain
Date: December 15, 2025
"""

import pytest
import json
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
import tempfile
import shutil

from src.planning.plan_lifecycle_manager import (
    PlanLifecycleManager,
    PlanState,
    ApprovalResult,
    LifecycleTransitionError
)


class TestPlanLifecycleManager:
    """Test PlanLifecycleManager core functionality."""
    
    @pytest.fixture
    def temp_workspace(self):
        """Create temporary workspace."""
        tmpdir = tempfile.mkdtemp()
        workspace = Path(tmpdir)
        
        # Create folder structure
        (workspace / "cortex-brain" / "documents" / "planning" / "temp-plans").mkdir(parents=True)
        (workspace / "cortex-brain" / "documents" / "planning" / "active").mkdir(parents=True)
        (workspace / "cortex-brain" / "documents" / "planning" / "completed").mkdir(parents=True)
        (workspace / "cortex-brain" / "documents" / "planning" / "archived").mkdir(parents=True)
        
        yield workspace
        
        # Cleanup
        shutil.rmtree(tmpdir)
    
    @pytest.fixture
    def lifecycle_manager(self, temp_workspace):
        """Create PlanLifecycleManager instance."""
        return PlanLifecycleManager(project_root=temp_workspace)
    
    def test_state_machine_initialization(self, lifecycle_manager):
        """Test FSM initializes in TEMP state."""
        plan_id = "test-plan-001"
        
        # New plan should start in TEMP
        state = lifecycle_manager.get_current_state(plan_id)
        
        assert state == PlanState.TEMP
    
    def test_temp_to_awaiting_approval_transition(self, lifecycle_manager, temp_workspace):
        """Test transition from TEMP to AWAITING_APPROVAL."""
        plan_id = "test-plan-002"
        
        # Create plan folder in temp-plans/
        plan_folder = temp_workspace / "cortex-brain" / "documents" / "planning" / "temp-plans" / plan_id
        plan_folder.mkdir(parents=True)
        
        # Initialize progress tracker
        lifecycle_manager.initialize_plan(plan_id, PlanState.TEMP)
        
        # Request approval
        success = lifecycle_manager.transition_to(plan_id, PlanState.AWAITING_APPROVAL)
        
        assert success is True
        assert lifecycle_manager.get_current_state(plan_id) == PlanState.AWAITING_APPROVAL
    
    def test_awaiting_approval_to_active_requires_approval(self, lifecycle_manager, temp_workspace):
        """Test transition to ACTIVE requires approval."""
        plan_id = "test-plan-003"
        
        # Create plan in awaiting approval state
        plan_folder = temp_workspace / "cortex-brain" / "documents" / "planning" / "temp-plans" / plan_id
        plan_folder.mkdir(parents=True)
        lifecycle_manager.initialize_plan(plan_id, PlanState.AWAITING_APPROVAL)
        
        # Attempt transition without approval
        with pytest.raises(LifecycleTransitionError, match="requires approval"):
            lifecycle_manager.transition_to(plan_id, PlanState.ACTIVE)
    
    def test_active_to_completed_transition(self, lifecycle_manager, temp_workspace):
        """Test valid completion flow."""
        plan_id = "test-plan-004"
        
        # Create plan in active state
        plan_folder = temp_workspace / "cortex-brain" / "documents" / "planning" / "active" / plan_id
        plan_folder.mkdir(parents=True)
        lifecycle_manager.initialize_plan(plan_id, PlanState.ACTIVE)
        
        # Transition to in_progress
        lifecycle_manager.transition_to(plan_id, PlanState.IN_PROGRESS)
        
        # Transition to completed
        success = lifecycle_manager.transition_to(plan_id, PlanState.COMPLETED)
        
        assert success is True
        assert lifecycle_manager.get_current_state(plan_id) == PlanState.COMPLETED
    
    def test_invalid_transitions_rejected(self, lifecycle_manager, temp_workspace):
        """Test invalid transitions are rejected (skip prevention)."""
        plan_id = "test-plan-005"
        
        # Create plan in TEMP state
        plan_folder = temp_workspace / "cortex-brain" / "documents" / "planning" / "temp-plans" / plan_id
        plan_folder.mkdir(parents=True)
        lifecycle_manager.initialize_plan(plan_id, PlanState.TEMP)
        
        # Attempt to skip directly to COMPLETED (invalid)
        with pytest.raises(LifecycleTransitionError, match="Invalid transition"):
            lifecycle_manager.transition_to(plan_id, PlanState.COMPLETED)
    
    def test_folder_movement_on_transition(self, lifecycle_manager, temp_workspace):
        """Test physical file moves on state transitions."""
        plan_id = "test-plan-006"
        
        # Create plan in temp-plans/
        temp_folder = temp_workspace / "cortex-brain" / "documents" / "planning" / "temp-plans" / plan_id
        temp_folder.mkdir(parents=True)
        (temp_folder / "00-master-plan.md").write_text("# Test Plan")
        
        lifecycle_manager.initialize_plan(plan_id, PlanState.TEMP)
        
        # Transition to active (with approval)
        lifecycle_manager.transition_to(plan_id, PlanState.AWAITING_APPROVAL)
        lifecycle_manager.approve_plan(plan_id, approved_by="user")
        lifecycle_manager.transition_to(plan_id, PlanState.ACTIVE)
        
        # Verify folder moved
        active_folder = temp_workspace / "cortex-brain" / "documents" / "planning" / "active" / plan_id
        assert active_folder.exists()
        assert (active_folder / "00-master-plan.md").exists()
        assert not temp_folder.exists()
    
    def test_progress_persistence(self, lifecycle_manager, temp_workspace):
        """Test state survives restarts."""
        plan_id = "test-plan-007"
        
        # Create and initialize plan
        plan_folder = temp_workspace / "cortex-brain" / "documents" / "planning" / "temp-plans" / plan_id
        plan_folder.mkdir(parents=True)
        (plan_folder / "tracking").mkdir(exist_ok=True)
        
        lifecycle_manager.initialize_plan(plan_id, PlanState.TEMP)
        lifecycle_manager.transition_to(plan_id, PlanState.AWAITING_APPROVAL)
        
        # Create new manager instance (simulate restart)
        new_manager = PlanLifecycleManager(project_root=temp_workspace)
        restored_state = new_manager.restore_state(plan_id)
        
        assert restored_state == PlanState.AWAITING_APPROVAL
    
    def test_lifecycle_history_tracking(self, lifecycle_manager, temp_workspace):
        """Test all transitions are recorded in history."""
        plan_id = "test-plan-008"
        
        # Create plan and go through lifecycle
        plan_folder = temp_workspace / "cortex-brain" / "documents" / "planning" / "temp-plans" / plan_id
        plan_folder.mkdir(parents=True)
        (plan_folder / "tracking").mkdir(exist_ok=True)
        
        lifecycle_manager.initialize_plan(plan_id, PlanState.TEMP)
        lifecycle_manager.transition_to(plan_id, PlanState.AWAITING_APPROVAL)
        lifecycle_manager.approve_plan(plan_id, approved_by="user")
        lifecycle_manager.transition_to(plan_id, PlanState.ACTIVE)
        
        # Check history
        history = lifecycle_manager.get_lifecycle_history(plan_id)
        
        assert len(history) == 2  # TEMP→AWAITING, AWAITING→ACTIVE
        assert history[0]["from"] == "temp"
        assert history[0]["to"] == "awaiting_approval"
        assert history[1]["from"] == "awaiting_approval"
        assert history[1]["to"] == "active"
    
    def test_get_valid_next_states(self, lifecycle_manager):
        """Test getting valid next states from current state."""
        plan_id = "test-plan-009"
        
        lifecycle_manager.initialize_plan(plan_id, PlanState.TEMP)
        
        valid_states = lifecycle_manager.get_valid_next_states(plan_id)
        
        assert PlanState.AWAITING_APPROVAL in valid_states
        assert PlanState.COMPLETED not in valid_states


class TestDoRApprovalWorkflow:
    """Test Definition of Ready approval workflow."""
    
    @pytest.fixture
    def temp_workspace(self):
        """Create temporary workspace."""
        tmpdir = tempfile.mkdtemp()
        workspace = Path(tmpdir)
        
        # Create folder structure
        (workspace / "cortex-brain" / "documents" / "planning" / "temp-plans").mkdir(parents=True)
        (workspace / "cortex-brain" / "documents" / "planning" / "active").mkdir(parents=True)
        
        yield workspace
        
        # Cleanup
        shutil.rmtree(tmpdir)
    
    @pytest.fixture
    def lifecycle_manager(self, temp_workspace):
        """Create PlanLifecycleManager instance."""
        return PlanLifecycleManager(project_root=temp_workspace)
    
    def test_dor_checklist_validation(self, lifecycle_manager, temp_workspace):
        """Test DoR checklist validation."""
        plan_id = "test-plan-010"
        
        # Create plan with incomplete DoR
        plan_folder = temp_workspace / "cortex-brain" / "documents" / "planning" / "temp-plans" / plan_id
        plan_folder.mkdir(parents=True)
        
        dor_checklist = {
            "problem_statement_clear": True,
            "success_criteria_defined": False,  # Missing
            "phases_breakdown_logical": True,
            "estimated_time_reasonable": True,
            "dependencies_identified": True,
            "risks_assessed": False  # Missing
        }
        
        is_complete = lifecycle_manager.validate_dor_checklist(plan_id, dor_checklist)
        
        assert is_complete is False
    
    def test_user_approval_required(self, lifecycle_manager, temp_workspace):
        """Test user approval is required for tier 3-4 plans."""
        plan_id = "test-plan-011"
        
        # Create tier 4 plan
        plan_folder = temp_workspace / "cortex-brain" / "documents" / "planning" / "temp-plans" / plan_id
        plan_folder.mkdir(parents=True)
        
        lifecycle_manager.initialize_plan(plan_id, PlanState.AWAITING_APPROVAL, complexity_tier=4)
        
        # Check if approval required
        requires_approval = lifecycle_manager.requires_user_approval(plan_id)
        
        assert requires_approval is True
    
    def test_auto_approve_for_tier_1_2(self, lifecycle_manager, temp_workspace):
        """Test auto-approval for lightweight plans."""
        plan_id = "test-plan-012"
        
        # Create tier 2 plan
        plan_folder = temp_workspace / "cortex-brain" / "documents" / "planning" / "temp-plans" / plan_id
        plan_folder.mkdir(parents=True)
        
        lifecycle_manager.initialize_plan(plan_id, PlanState.AWAITING_APPROVAL, complexity_tier=2)
        
        # Complete DoR checklist
        dor_checklist = {
            "problem_statement_clear": True,
            "success_criteria_defined": True,
            "phases_breakdown_logical": True,
            "estimated_time_reasonable": True,
            "dependencies_identified": True,
            "risks_assessed": True
        }
        
        # Auto-approve
        result = lifecycle_manager.request_dor_approval(plan_id, dor_checklist, auto_approve=True)
        
        assert result.approved is True
        assert result.auto_approved is True
    
    def test_approval_rejection_returns_to_temp(self, lifecycle_manager, temp_workspace):
        """Test rejection returns plan to TEMP state."""
        plan_id = "test-plan-013"
        
        # Create plan in awaiting approval
        plan_folder = temp_workspace / "cortex-brain" / "documents" / "planning" / "temp-plans" / plan_id
        plan_folder.mkdir(parents=True)
        
        lifecycle_manager.initialize_plan(plan_id, PlanState.AWAITING_APPROVAL)
        
        # Reject approval
        lifecycle_manager.reject_approval(plan_id, reason="Needs more detail on risks")
        
        # Should return to TEMP
        current_state = lifecycle_manager.get_current_state(plan_id)
        assert current_state == PlanState.TEMP
    
    def test_approval_metadata_persisted(self, lifecycle_manager, temp_workspace):
        """Test approval metadata is saved to progress tracker."""
        plan_id = "test-plan-014"
        
        # Create plan
        plan_folder = temp_workspace / "cortex-brain" / "documents" / "planning" / "temp-plans" / plan_id
        plan_folder.mkdir(parents=True)
        (plan_folder / "tracking").mkdir(exist_ok=True)
        
        lifecycle_manager.initialize_plan(plan_id, PlanState.AWAITING_APPROVAL)
        
        # Approve
        lifecycle_manager.approve_plan(plan_id, approved_by="john.doe@example.com")
        
        # Check metadata
        metadata = lifecycle_manager.get_approval_metadata(plan_id)
        
        assert metadata["approved_by"] == "john.doe@example.com"
        assert "approval_timestamp" in metadata
        assert metadata["dor_checklist_complete"] is True
    
    def test_interactive_approval_prompt(self, lifecycle_manager, temp_workspace):
        """Test interactive approval displays plan summary."""
        plan_id = "test-plan-015"
        
        # Create plan
        plan_folder = temp_workspace / "cortex-brain" / "documents" / "planning" / "temp-plans" / plan_id
        plan_folder.mkdir(parents=True)
        
        lifecycle_manager.initialize_plan(plan_id, PlanState.AWAITING_APPROVAL)
        
        # Mock user input (approval)
        with patch('builtins.input', return_value='y'):
            result = lifecycle_manager.request_dor_approval_interactive(plan_id)
        
        assert result.approved is True
        assert result.approved_by == "user"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
