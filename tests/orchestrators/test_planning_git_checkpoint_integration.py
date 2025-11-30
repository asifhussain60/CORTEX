"""
Test git checkpoint integration with PlanningOrchestrator.

Purpose: Verify automatic git checkpoints are created during planning operations
Author: Asif Hussain
Version: 1.0
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, call
from pathlib import Path
from datetime import datetime

from src.orchestrators.planning_orchestrator import PlanningOrchestrator


class TestPlanningGitCheckpointIntegration:
    """Test git checkpoint integration in planning workflow."""
    
    @pytest.fixture
    def orchestrator(self, tmp_path):
        """Create PlanningOrchestrator instance with mocked git checkpoint."""
        cortex_root = tmp_path / "cortex"
        cortex_root.mkdir()
        
        # Create required directories
        (cortex_root / "cortex-brain" / "documents" / "planning").mkdir(parents=True)
        
        # Create schema file
        schema_path = cortex_root / "cortex-brain" / "planning-schema.yaml"
        schema_path.write_text("""
metadata:
  version: "2.0"
  
phases:
  - name: "Foundation"
    sections:
      - requirements
      - dependencies
      - architecture
""")
        
        with patch('src.orchestrators.planning_orchestrator.GitCheckpointOrchestrator') as mock_git:
            mock_instance = Mock()
            mock_git.return_value = mock_instance
            
            orch = PlanningOrchestrator(cortex_root=cortex_root)
            orch.git_checkpoint = mock_instance
            
            yield orch, mock_instance
    
    # ========================================================================
    # UNIT TESTS - generate_incremental_plan checkpoint
    # ========================================================================
    
    def test_generate_incremental_plan_creates_checkpoint(self, orchestrator):
        """Test checkpoint created before plan generation."""
        orch, mock_checkpoint = orchestrator
        
        # Mock checkpoint_callback to auto-approve all phases
        def auto_approve(checkpoint_id, section_name, preview):
            return True
        
        # Call generate_incremental_plan
        success, path, msg = orch.generate_incremental_plan(
            feature_requirements="User authentication with JWT tokens",
            checkpoint_callback=auto_approve
        )
        
        # Verify checkpoint was called
        mock_checkpoint.create_auto_checkpoint.assert_called()
        
        # Get first call arguments
        first_call = mock_checkpoint.create_auto_checkpoint.call_args_list[0]
        operation = first_call[1]['operation']
        message = first_call[1]['message']
        
        assert operation == "plan"
        assert "User authentication" in message
        assert "Starting plan generation" in message
    
    def test_generate_incremental_plan_checkpoint_with_long_feature_name(self, orchestrator):
        """Test checkpoint message truncates long feature names."""
        orch, mock_checkpoint = orchestrator
        
        long_feature = "This is a very long feature requirement that exceeds fifty characters and should be truncated for checkpoint message clarity"
        
        def auto_approve(checkpoint_id, section_name, preview):
            return True
        
        success, path, msg = orch.generate_incremental_plan(
            feature_requirements=long_feature,
            checkpoint_callback=auto_approve
        )
        
        # Verify truncation (should end with "...")
        first_call = mock_checkpoint.create_auto_checkpoint.call_args_list[0]
        message = first_call[1]['message']
        
        assert len(message.split(": ")[1]) <= 50  # Feature name part <= 50 chars
        assert message.endswith("...")
    
    def test_generate_incremental_plan_continues_on_checkpoint_failure(self, orchestrator):
        """Test planning continues if checkpoint fails."""
        orch, mock_checkpoint = orchestrator
        
        # Make checkpoint raise exception
        mock_checkpoint.create_auto_checkpoint.side_effect = Exception("Git unavailable")
        
        def auto_approve(checkpoint_id, section_name, preview):
            return True
        
        # Planning should still succeed
        success, path, msg = orch.generate_incremental_plan(
            feature_requirements="Test feature",
            checkpoint_callback=auto_approve
        )
        
        # Verify planning succeeded despite checkpoint failure
        assert success is True
        assert path is not None
    
    # ========================================================================
    # UNIT TESTS - approve_plan checkpoint
    # ========================================================================
    
    def test_approve_plan_creates_checkpoint(self, orchestrator, tmp_path):
        """Test checkpoint created after plan approval."""
        orch, mock_checkpoint = orchestrator
        
        # Create test plan in active directory
        active_dir = tmp_path / "cortex" / "cortex-brain" / "documents" / "planning" / "active"
        active_dir.mkdir(parents=True)
        
        plan_file = active_dir / "PLAN-20251130-test-feature.md"
        plan_file.write_text("""---
status: active
created: 2025-11-30
---

# Test Feature Plan
""")
        
        # Create approved directory
        approved_dir = tmp_path / "cortex" / "cortex-brain" / "documents" / "planning" / "approved"
        approved_dir.mkdir(parents=True)
        
        # Call approve_plan
        result = orch.approve_plan("PLAN-20251130-test-feature.md")
        
        # Verify checkpoint was called
        mock_checkpoint.create_auto_checkpoint.assert_called_with(
            operation="approve",
            message="Plan approved: PLAN-20251130-test-feature.md"
        )
        
        # Verify approval succeeded
        assert result['success'] is True
        assert result['new_status'] == 'approved'
    
    def test_approve_plan_checkpoint_includes_filename(self, orchestrator, tmp_path):
        """Test checkpoint message includes plan filename."""
        orch, mock_checkpoint = orchestrator
        
        # Create test plan
        active_dir = tmp_path / "cortex" / "cortex-brain" / "documents" / "planning" / "active"
        active_dir.mkdir(parents=True)
        
        plan_file = active_dir / "PLAN-20251130-authentication.md"
        plan_file.write_text("---\nstatus: active\n---\n# Auth Plan")
        
        approved_dir = tmp_path / "cortex" / "cortex-brain" / "documents" / "planning" / "approved"
        approved_dir.mkdir(parents=True)
        
        # Call approve_plan
        orch.approve_plan("PLAN-20251130-authentication.md")
        
        # Verify message contains filename
        call_args = mock_checkpoint.create_auto_checkpoint.call_args
        message = call_args[1]['message']
        
        assert "PLAN-20251130-authentication.md" in message
        assert "Plan approved" in message
    
    def test_approve_plan_continues_on_checkpoint_failure(self, orchestrator, tmp_path):
        """Test approval continues if checkpoint fails."""
        orch, mock_checkpoint = orchestrator
        
        # Make checkpoint raise exception
        mock_checkpoint.create_auto_checkpoint.side_effect = Exception("Git error")
        
        # Create test plan
        active_dir = tmp_path / "cortex" / "cortex-brain" / "documents" / "planning" / "active"
        active_dir.mkdir(parents=True)
        
        plan_file = active_dir / "PLAN-20251130-test.md"
        plan_file.write_text("---\nstatus: active\n---\n# Test")
        
        approved_dir = tmp_path / "cortex" / "cortex-brain" / "documents" / "planning" / "approved"
        approved_dir.mkdir(parents=True)
        
        # Approval should succeed despite checkpoint failure
        result = orch.approve_plan("PLAN-20251130-test.md")
        
        assert result['success'] is True
        assert result['new_status'] == 'approved'
    
    # ========================================================================
    # UNIT TESTS - complete_plan checkpoint
    # ========================================================================
    
    def test_complete_plan_creates_checkpoint(self, orchestrator, tmp_path):
        """Test checkpoint created after plan completion."""
        orch, mock_checkpoint = orchestrator
        
        # Create test plan in approved directory
        approved_dir = tmp_path / "cortex" / "cortex-brain" / "documents" / "planning" / "approved"
        approved_dir.mkdir(parents=True)
        
        plan_file = approved_dir / "PLAN-20251130-test-feature.md"
        plan_file.write_text("""---
status: approved
created: 2025-11-30
---

# Test Feature Plan
""")
        
        # Create completed directory
        completed_dir = tmp_path / "cortex" / "cortex-brain" / "documents" / "planning" / "completed"
        completed_dir.mkdir(parents=True)
        
        # Call complete_plan
        result = orch.complete_plan("PLAN-20251130-test-feature.md")
        
        # Verify checkpoint was called
        mock_checkpoint.create_auto_checkpoint.assert_called_with(
            operation="complete",
            message="Plan completed: PLAN-20251130-test-feature.md"
        )
        
        # Verify completion succeeded
        assert result['success'] is True
        assert result['new_status'] == 'completed'
    
    def test_complete_plan_checkpoint_includes_filename(self, orchestrator, tmp_path):
        """Test checkpoint message includes plan filename."""
        orch, mock_checkpoint = orchestrator
        
        # Create test plan
        approved_dir = tmp_path / "cortex" / "cortex-brain" / "documents" / "planning" / "approved"
        approved_dir.mkdir(parents=True)
        
        plan_file = approved_dir / "PLAN-20251130-payment-integration.md"
        plan_file.write_text("---\nstatus: approved\n---\n# Payment Plan")
        
        completed_dir = tmp_path / "cortex" / "cortex-brain" / "documents" / "planning" / "completed"
        completed_dir.mkdir(parents=True)
        
        # Call complete_plan
        orch.complete_plan("PLAN-20251130-payment-integration.md")
        
        # Verify message contains filename
        call_args = mock_checkpoint.create_auto_checkpoint.call_args
        message = call_args[1]['message']
        
        assert "PLAN-20251130-payment-integration.md" in message
        assert "Plan completed" in message
    
    def test_complete_plan_continues_on_checkpoint_failure(self, orchestrator, tmp_path):
        """Test completion continues if checkpoint fails."""
        orch, mock_checkpoint = orchestrator
        
        # Make checkpoint raise exception
        mock_checkpoint.create_auto_checkpoint.side_effect = Exception("Git error")
        
        # Create test plan
        approved_dir = tmp_path / "cortex" / "cortex-brain" / "documents" / "planning" / "approved"
        approved_dir.mkdir(parents=True)
        
        plan_file = approved_dir / "PLAN-20251130-test.md"
        plan_file.write_text("---\nstatus: approved\n---\n# Test")
        
        completed_dir = tmp_path / "cortex" / "cortex-brain" / "documents" / "planning" / "completed"
        completed_dir.mkdir(parents=True)
        
        # Completion should succeed despite checkpoint failure
        result = orch.complete_plan("PLAN-20251130-test.md")
        
        assert result['success'] is True
        assert result['new_status'] == 'completed'
    
    # ========================================================================
    # INTEGRATION TEST - Full workflow with checkpoints
    # ========================================================================
    
    def test_full_planning_workflow_creates_all_checkpoints(self, orchestrator, tmp_path):
        """Test complete planning workflow creates all 3 checkpoints."""
        orch, mock_checkpoint = orchestrator
        
        # Phase 1: Generate plan
        def auto_approve(checkpoint_id, section_name, preview):
            return True
        
        success, path, msg = orch.generate_incremental_plan(
            feature_requirements="Complete workflow test",
            checkpoint_callback=auto_approve
        )
        
        assert success is True
        
        # Verify plan checkpoint called
        assert any(
            call[1]['operation'] == 'plan' and 'Starting plan generation' in call[1]['message']
            for call in mock_checkpoint.create_auto_checkpoint.call_args_list
        )
        
        # Reset mock for next phase
        mock_checkpoint.reset_mock()
        
        # Phase 2: Approve plan
        # Move generated plan to active directory for approval test
        if path:
            active_dir = tmp_path / "cortex" / "cortex-brain" / "documents" / "planning" / "active"
            active_dir.mkdir(parents=True, exist_ok=True)
            
            plan_filename = path.name
            active_file = active_dir / plan_filename
            
            # Copy content with active status
            content = path.read_text()
            active_file.write_text(content.replace('status: active', 'status: active'))
            
            # Create approved directory
            approved_dir = tmp_path / "cortex" / "cortex-brain" / "documents" / "planning" / "approved"
            approved_dir.mkdir(parents=True, exist_ok=True)
            
            result = orch.approve_plan(plan_filename)
            
            # Verify approve checkpoint called
            mock_checkpoint.create_auto_checkpoint.assert_called_with(
                operation="approve",
                message=f"Plan approved: {plan_filename}"
            )
            
            # Reset mock for next phase
            mock_checkpoint.reset_mock()
            
            # Phase 3: Complete plan
            completed_dir = tmp_path / "cortex" / "cortex-brain" / "documents" / "planning" / "completed"
            completed_dir.mkdir(parents=True, exist_ok=True)
            
            result = orch.complete_plan(plan_filename)
            
            # Verify complete checkpoint called
            mock_checkpoint.create_auto_checkpoint.assert_called_with(
                operation="complete",
                message=f"Plan completed: {plan_filename}"
            )
    
    # ========================================================================
    # EDGE CASE TESTS
    # ========================================================================
    
    def test_checkpoint_with_special_characters_in_filename(self, orchestrator, tmp_path):
        """Test checkpoint handles filenames with special characters."""
        orch, mock_checkpoint = orchestrator
        
        # Create test plan with special characters
        active_dir = tmp_path / "cortex" / "cortex-brain" / "documents" / "planning" / "active"
        active_dir.mkdir(parents=True)
        
        plan_file = active_dir / "PLAN-20251130-feature-with-dashes_and_underscores.md"
        plan_file.write_text("---\nstatus: active\n---\n# Test")
        
        approved_dir = tmp_path / "cortex" / "cortex-brain" / "documents" / "planning" / "approved"
        approved_dir.mkdir(parents=True)
        
        # Should handle special characters without error
        result = orch.approve_plan("PLAN-20251130-feature-with-dashes_and_underscores.md")
        
        assert result['success'] is True
        
        call_args = mock_checkpoint.create_auto_checkpoint.call_args
        message = call_args[1]['message']
        
        assert "dashes_and_underscores" in message
    
    def test_multiple_checkpoints_in_sequence(self, orchestrator, tmp_path):
        """Test multiple planning operations create separate checkpoints."""
        orch, mock_checkpoint = orchestrator
        
        # Create multiple plans
        active_dir = tmp_path / "cortex" / "cortex-brain" / "documents" / "planning" / "active"
        active_dir.mkdir(parents=True)
        
        approved_dir = tmp_path / "cortex" / "cortex-brain" / "documents" / "planning" / "approved"
        approved_dir.mkdir(parents=True)
        
        for i in range(3):
            plan_file = active_dir / f"PLAN-2025113{i}-test-{i}.md"
            plan_file.write_text(f"---\nstatus: active\n---\n# Test {i}")
            
            orch.approve_plan(f"PLAN-2025113{i}-test-{i}.md")
        
        # Verify 3 separate checkpoint calls
        assert mock_checkpoint.create_auto_checkpoint.call_count == 3
        
        # Verify each has unique message
        messages = [call[1]['message'] for call in mock_checkpoint.create_auto_checkpoint.call_args_list]
        assert len(set(messages)) == 3  # All unique
