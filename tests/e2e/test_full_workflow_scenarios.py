"""
End-to-End Test Suite - Full Workflow Scenarios

Tests complete workflows from start to finish:
- Planning workflow (DoR → Implementation → DoD)
- TDD workflow (RED → GREEN → REFACTOR)
- Rollback workflow (checkpoint → validate → execute)
- Combined workflows (planning + TDD + rollback)

Author: Asif Hussain
Created: 2025-11-28
Increment: 23 (End-to-End Test Suite)
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import subprocess

from src.orchestrators.phase_checkpoint_manager import PhaseCheckpointManager
from src.orchestrators.rollback_orchestrator import RollbackOrchestrator
from src.enrichers.git_history_enricher import GitHistoryEnricher
from src.utils.progress_bar import ProgressBar
from src.utils.template_renderer import TemplateRenderer


class TestPlanningWorkflowE2E:
    """End-to-end tests for complete planning workflow."""
    
    def test_full_planning_workflow_with_checkpoints(self):
        """Should execute full planning workflow from DoR to DoD with checkpoints."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cortex_root = Path(tmpdir)
            checkpoint_mgr = PhaseCheckpointManager(cortex_root=cortex_root)
            
            session_id = "planning-e2e-001"
            
            # Phase 1: Definition of Ready (DoR)
            checkpoint_mgr.store_checkpoint_metadata(
                session_id=session_id,
                phase="DoR",
                checkpoint_id="dor-checkpoint",
                commit_sha="abc123",
                metrics={"requirements_validated": True, "acceptance_criteria_count": 5}
            )
            
            # Phase 2: Implementation
            checkpoint_mgr.store_checkpoint_metadata(
                session_id=session_id,
                phase="Implementation",
                checkpoint_id="impl-checkpoint",
                commit_sha="def456",
                metrics={"features_completed": 3, "tests_passing": 25}
            )
            
            # Phase 3: Definition of Done (DoD)
            checkpoint_mgr.store_checkpoint_metadata(
                session_id=session_id,
                phase="DoD",
                checkpoint_id="dod-checkpoint",
                commit_sha="ghi789",
                metrics={"code_reviewed": True, "docs_updated": True, "tests_passing": 30}
            )
            
            # Verify all phases recorded
            checkpoints = checkpoint_mgr.list_checkpoints(session_id)
            assert len(checkpoints) == 3
            
            # Verify phase progression
            phases = [cp['phase'] for cp in checkpoints]
            assert phases == ["DoR", "Implementation", "DoD"]
            
            # Verify metrics accumulation
            dod_checkpoint = checkpoint_mgr.get_checkpoint_metadata(session_id, "DoD")
            assert dod_checkpoint['metrics']['tests_passing'] == 30
    
    def test_planning_workflow_with_rollback_to_dor(self):
        """Should allow rollback from Implementation to DoR."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cortex_root = Path(tmpdir)
            checkpoint_mgr = PhaseCheckpointManager(cortex_root=cortex_root)
            rollback_orch = RollbackOrchestrator(cortex_dir=cortex_root)
            
            session_id = "planning-rollback-001"
            
            # Store DoR checkpoint
            checkpoint_mgr.store_checkpoint_metadata(
                session_id=session_id,
                phase="DoR",
                checkpoint_id="dor-checkpoint",
                commit_sha="abc123",
                metrics={}
            )
            
            # Store Implementation checkpoint
            checkpoint_mgr.store_checkpoint_metadata(
                session_id=session_id,
                phase="Implementation",
                checkpoint_id="impl-checkpoint",
                commit_sha="def456",
                metrics={}
            )
            
            # Validate can rollback to DoR
            is_valid = rollback_orch.validate_checkpoint(session_id, "dor-checkpoint")
            assert is_valid is True
            
            # Format summary for user confirmation
            summary = rollback_orch.format_checkpoint_summary(session_id, "dor-checkpoint")
            assert "dor-checkpoint" in summary
            assert "DoR" in summary


class TestTDDWorkflowE2E:
    """End-to-end tests for complete TDD workflow."""
    
    def test_full_tdd_workflow_red_green_refactor(self):
        """Should execute full TDD workflow through RED → GREEN → REFACTOR."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cortex_root = Path(tmpdir)
            checkpoint_mgr = PhaseCheckpointManager(cortex_root=cortex_root)
            
            session_id = "tdd-e2e-001"
            
            # RED Phase: Test fails
            checkpoint_mgr.store_checkpoint_metadata(
                session_id=session_id,
                phase="RED",
                checkpoint_id="red-checkpoint",
                commit_sha="red123",
                metrics={"tests_failing": 1, "tests_passing": 0}
            )
            
            # GREEN Phase: Test passes
            checkpoint_mgr.store_checkpoint_metadata(
                session_id=session_id,
                phase="GREEN",
                checkpoint_id="green-checkpoint",
                commit_sha="green456",
                metrics={"tests_failing": 0, "tests_passing": 1}
            )
            
            # REFACTOR Phase: Code improved
            checkpoint_mgr.store_checkpoint_metadata(
                session_id=session_id,
                phase="REFACTOR",
                checkpoint_id="refactor-checkpoint",
                commit_sha="refactor789",
                metrics={"tests_failing": 0, "tests_passing": 1, "code_quality": 95}
            )
            
            # Verify TDD progression
            checkpoints = checkpoint_mgr.list_checkpoints(session_id)
            assert len(checkpoints) == 3
            
            phases = [cp['phase'] for cp in checkpoints]
            assert phases == ["RED", "GREEN", "REFACTOR"]
            
            # Verify test progression
            red_metrics = checkpoint_mgr.get_checkpoint_metadata(session_id, "RED")['metrics']
            green_metrics = checkpoint_mgr.get_checkpoint_metadata(session_id, "GREEN")['metrics']
            refactor_metrics = checkpoint_mgr.get_checkpoint_metadata(session_id, "REFACTOR")['metrics']
            
            assert red_metrics['tests_failing'] == 1
            assert green_metrics['tests_passing'] == 1
            assert refactor_metrics['code_quality'] == 95
    
    def test_tdd_workflow_with_rollback_to_green(self):
        """Should allow rollback from REFACTOR to GREEN when refactoring breaks tests."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cortex_root = Path(tmpdir)
            checkpoint_mgr = PhaseCheckpointManager(cortex_root=cortex_root)
            rollback_orch = RollbackOrchestrator(cortex_dir=cortex_root)
            
            session_id = "tdd-rollback-001"
            
            # Store GREEN checkpoint (all tests passing)
            checkpoint_mgr.store_checkpoint_metadata(
                session_id=session_id,
                phase="GREEN",
                checkpoint_id="green-safe",
                commit_sha="green123",
                metrics={"tests_passing": 10}
            )
            
            # Validate can rollback to GREEN
            is_valid = rollback_orch.validate_checkpoint(session_id, "green-safe")
            assert is_valid is True


class TestRollbackWorkflowE2E:
    """End-to-end tests for complete rollback workflow."""
    
    def test_full_rollback_workflow_with_safety_checks(self):
        """Should execute full rollback workflow with validation and safety checks."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cortex_root = Path(tmpdir)
            project_root = Path(tmpdir)
            checkpoint_mgr = PhaseCheckpointManager(cortex_root=cortex_root)
            rollback_orch = RollbackOrchestrator(cortex_dir=cortex_root, project_root=project_root)
            
            session_id = "rollback-e2e-001"
            checkpoint_id = "safe-checkpoint"
            
            # Step 1: Store checkpoint
            checkpoint_mgr.store_checkpoint_metadata(
                session_id=session_id,
                phase="Implementation",
                checkpoint_id=checkpoint_id,
                commit_sha="abc123",
                metrics={"tests_passing": 15}
            )
            
            # Step 2: Validate checkpoint exists
            is_valid = rollback_orch.validate_checkpoint(session_id, checkpoint_id)
            assert is_valid is True
            
            # Step 3: Check rollback safety
            with patch.object(rollback_orch, '_get_git_status') as mock_status:
                mock_status.return_value = {
                    'clean': True,
                    'uncommitted_changes': [],
                    'merge_in_progress': False
                }
                
                safety = rollback_orch.check_rollback_safety(checkpoint_id)
                assert safety['safe'] is True
            
            # Step 4: Execute dry-run
            with patch.object(rollback_orch, '_get_git_diff') as mock_diff:
                mock_diff.return_value = "diff output"
                
                result = rollback_orch.execute_rollback(
                    checkpoint_id=checkpoint_id,
                    dry_run=True
                )
                
                assert result['executed'] is False
                assert 'dry-run' in result['message'].lower()
    
    def test_rollback_workflow_blocked_by_safety_check(self):
        """Should block rollback when safety checks fail."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cortex_root = Path(tmpdir)
            project_root = Path(tmpdir)
            rollback_orch = RollbackOrchestrator(cortex_dir=cortex_root, project_root=project_root)
            
            checkpoint_id = "blocked-checkpoint"
            
            # Mock uncommitted changes
            with patch.object(rollback_orch, '_get_git_status') as mock_status:
                mock_status.return_value = {
                    'clean': False,
                    'uncommitted_changes': ['file1.py', 'file2.py'],
                    'merge_in_progress': False
                }
                
                safety = rollback_orch.check_rollback_safety(checkpoint_id)
                
                assert safety['safe'] is False
                assert 'Uncommitted changes' in safety['warning']


class TestCombinedWorkflowsE2E:
    """End-to-end tests for combined workflow scenarios."""
    
    def test_planning_and_tdd_workflow_combined(self):
        """Should execute planning workflow with embedded TDD cycles."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cortex_root = Path(tmpdir)
            checkpoint_mgr = PhaseCheckpointManager(cortex_root=cortex_root)
            
            session_id = "combined-e2e-001"
            
            # Planning: DoR phase
            checkpoint_mgr.store_checkpoint_metadata(
                session_id=session_id,
                phase="DoR",
                checkpoint_id="dor-1",
                commit_sha="dor123",
                metrics={"requirements_validated": True}
            )
            
            # Implementation with TDD cycles
            # TDD Cycle 1: Feature A
            checkpoint_mgr.store_checkpoint_metadata(
                session_id=session_id,
                phase="TDD-Feature-A-RED",
                checkpoint_id="tdd-a-red",
                commit_sha="tdd-a-red-123",
                metrics={"tests_failing": 3}
            )
            
            checkpoint_mgr.store_checkpoint_metadata(
                session_id=session_id,
                phase="TDD-Feature-A-GREEN",
                checkpoint_id="tdd-a-green",
                commit_sha="tdd-a-green-456",
                metrics={"tests_passing": 3}
            )
            
            # TDD Cycle 2: Feature B
            checkpoint_mgr.store_checkpoint_metadata(
                session_id=session_id,
                phase="TDD-Feature-B-RED",
                checkpoint_id="tdd-b-red",
                commit_sha="tdd-b-red-789",
                metrics={"tests_failing": 2}
            )
            
            checkpoint_mgr.store_checkpoint_metadata(
                session_id=session_id,
                phase="TDD-Feature-B-GREEN",
                checkpoint_id="tdd-b-green",
                commit_sha="tdd-b-green-abc",
                metrics={"tests_passing": 5}
            )
            
            # Planning: DoD phase
            checkpoint_mgr.store_checkpoint_metadata(
                session_id=session_id,
                phase="DoD",
                checkpoint_id="dod-1",
                commit_sha="dod789",
                metrics={"all_tests_passing": 5, "code_reviewed": True}
            )
            
            # Verify combined workflow
            checkpoints = checkpoint_mgr.list_checkpoints(session_id)
            assert len(checkpoints) == 6  # DoR + 4 TDD phases + DoD
            
            # Verify can access any checkpoint
            dor = checkpoint_mgr.get_checkpoint_metadata(session_id, "DoR")
            assert dor is not None
            
            tdd_green = checkpoint_mgr.get_checkpoint_metadata(session_id, "TDD-Feature-B-GREEN")
            assert tdd_green['metrics']['tests_passing'] == 5
    
    def test_full_workflow_with_progress_tracking(self):
        """Should track progress through full workflow."""
        # Simulate workflow phases
        phases = ["DoR", "Implementation", "Testing", "DoD"]
        total = len(phases)
        
        progress_updates = []
        for i, phase in enumerate(phases, 1):
            progress_bar = ProgressBar(current=i, total=total)
            bar = progress_bar.render()
            progress_updates.append(bar)
            assert f"{(i/total)*100:.0f}%" in bar
        
        # Verify final progress is 100%
        assert "100%" in progress_updates[-1]
        assert "█" * 20 in progress_updates[-1]
    
    def test_workflow_with_template_rendering(self):
        """Should render templates with workflow status."""
        renderer = TemplateRenderer()
        
        template = """
        # Workflow Status
        
        Current Phase: Implementation
        Progress: {progress}
        Tests Passing: 25
        """
        
        rendered = renderer.render_with_progress(template, current=2, total=5)
        
        assert 'Implementation' in rendered
        assert '40%' in rendered  # Progress bar rendered
        assert '{progress}' not in rendered  # Placeholder replaced


class TestWorkflowRecoveryE2E:
    """End-to-end tests for workflow recovery scenarios."""
    
    def test_recover_from_failed_implementation(self):
        """Should allow recovery from failed implementation by rolling back."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cortex_root = Path(tmpdir)
            checkpoint_mgr = PhaseCheckpointManager(cortex_root=cortex_root)
            rollback_orch = RollbackOrchestrator(cortex_dir=cortex_root)
            
            session_id = "recovery-e2e-001"
            
            # Store DoR checkpoint (last known good state)
            checkpoint_mgr.store_checkpoint_metadata(
                session_id=session_id,
                phase="DoR",
                checkpoint_id="last-good-state",
                commit_sha="good123",
                metrics={"requirements_validated": True}
            )
            
            # Simulate failed implementation (not stored as checkpoint)
            # User realizes implementation is wrong
            
            # Verify can rollback to last good state
            is_valid = rollback_orch.validate_checkpoint(session_id, "last-good-state")
            assert is_valid is True
            
            # List available checkpoints
            checkpoints = rollback_orch.list_checkpoints(session_id)
            assert len(checkpoints) >= 1
            assert checkpoints[0]['checkpoint_id'] == "last-good-state"
    
    def test_resume_workflow_after_interruption(self):
        """Should resume workflow from last checkpoint after interruption."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cortex_root = Path(tmpdir)
            checkpoint_mgr = PhaseCheckpointManager(cortex_root=cortex_root)
            
            session_id = "resume-e2e-001"
            
            # Session 1: Start workflow, interrupted after Phase 1
            checkpoint_mgr.store_checkpoint_metadata(
                session_id=session_id,
                phase="Phase-1",
                checkpoint_id="phase-1-complete",
                commit_sha="phase1-abc",
                metrics={"phase_1_complete": True}
            )
            
            # Session 2: Resume and continue
            # List checkpoints to find last state
            checkpoints = checkpoint_mgr.list_checkpoints(session_id)
            assert len(checkpoints) == 1
            
            last_checkpoint = checkpoints[-1]
            assert last_checkpoint['phase'] == "Phase-1"
            assert last_checkpoint['metrics']['phase_1_complete'] is True
            
            # Continue from Phase 2
            checkpoint_mgr.store_checkpoint_metadata(
                session_id=session_id,
                phase="Phase-2",
                checkpoint_id="phase-2-complete",
                commit_sha="phase2-def",
                metrics={"phase_2_complete": True}
            )
            
            # Verify workflow continuity
            all_checkpoints = checkpoint_mgr.list_checkpoints(session_id)
            assert len(all_checkpoints) == 2
            phases = [cp['phase'] for cp in all_checkpoints]
            assert phases == ["Phase-1", "Phase-2"]
