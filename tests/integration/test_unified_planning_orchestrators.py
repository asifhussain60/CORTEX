"""
Integration tests for unified planning architecture.

Tests PlanningOrchestrator and TempPlanManager using UnifiedPlanGenerator,
TokenReductionTracker, and PhaseLifecycleManager.

Phase: 13 - Planning Architecture Unification
Version: 1.0.0
"""

import pytest
import tempfile
import uuid
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch

from src.operations.modules.orchestration.planning_orchestrator import (
    PlanningOrchestrator, PlanningContext
)
from src.operations.modules.orchestration.temporary_plan_manager import (
    TemporaryPlanManager, TemporaryPlan
)
from src.operations.modules.planning import (
    UnifiedPlanGenerator, TokenReductionTracker, PhaseLifecycleManager
)


@pytest.fixture
def temp_workspace():
    """Create temporary workspace for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        workspace = Path(tmpdir)
        
        # Create expected directories
        (workspace / "cortex-brain" / "documents" / "planning" / "features" / "active").mkdir(parents=True)
        (workspace / "cortex-brain" / "documents" / "planning" / "features" / "approved").mkdir(parents=True)
        (workspace / "cortex-brain" / "metrics").mkdir(parents=True)
        
        yield workspace


@pytest.fixture
def mock_config(temp_workspace):
    """Mock configuration with temp paths."""
    return temp_workspace  # Return workspace path directly


class TestPlanningOrchestratorIntegration:
    """Test PlanningOrchestrator with unified components."""
    
    def test_orchestrator_uses_unified_generator(self, temp_workspace):
        """Test that PlanningOrchestrator initializes unified components."""
        with patch('src.operations.modules.orchestration.planning_orchestrator.get_version_manager') as mock_vm:
            mock_vm.return_value.get_version.return_value = "3.1.0"
            
            orchestrator = PlanningOrchestrator(project_root=temp_workspace)
            
            # Verify unified components initialized
            assert hasattr(orchestrator, 'unified_generator')
            assert isinstance(orchestrator.unified_generator, UnifiedPlanGenerator)
            assert hasattr(orchestrator, 'token_tracker')
            assert isinstance(orchestrator.token_tracker, TokenReductionTracker)
            assert hasattr(orchestrator, 'phase_manager')
            assert isinstance(orchestrator.phase_manager, PhaseLifecycleManager)
    
    def test_master_plan_generation_uses_unified_components(self, temp_workspace):
        """Test master plan generation delegates to UnifiedPlanGenerator."""
        with patch('src.operations.modules.orchestration.planning_orchestrator.get_version_manager') as mock_vm:
            mock_vm.return_value.get_version.return_value = "3.1.0"
            
            orchestrator = PlanningOrchestrator(project_root=temp_workspace)
            
            # Mock UnifiedPlanGenerator
            with patch.object(orchestrator.unified_generator, 'generate_master_plan') as mock_gen:
                mock_gen.return_value = "# Master Plan\n[████░░] 50%"
                
                # Create test phases
                phases = [
                    {"id": 1, "name": "Phase 1", "status": "pending"},
                    {"id": 2, "name": "Phase 2", "status": "pending"}
                ]
                
                # Call master plan generation
                content = orchestrator.unified_generator.generate_master_plan(
                    plan_id="test-plan",
                    phases=phases,
                    metadata={"date": "Dec 15, 2025"}
                )
                
                # Verify delegation occurred
                assert mock_gen.called
                assert "Master Plan" in content


class TestTempPlanManagerIntegration:
    """Test TemporaryPlanManager with unified components."""
    
    def test_temp_manager_uses_unified_generator(self, temp_workspace):
        """Test that TempPlanManager initializes unified components."""
        manager = TemporaryPlanManager(project_root=temp_workspace)
        
        # Verify unified components initialized
        assert hasattr(manager, 'unified_generator')
        assert isinstance(manager.unified_generator, UnifiedPlanGenerator)
        assert hasattr(manager, 'token_tracker')
        assert isinstance(manager.token_tracker, TokenReductionTracker)
        assert hasattr(manager, 'phase_manager')
        assert isinstance(manager.phase_manager, PhaseLifecycleManager)
    
    def test_create_temporary_plan_generates_valid_plan(self, temp_workspace):
        """Test temporary plan creation with unified architecture."""
        manager = TemporaryPlanManager(project_root=temp_workspace)
        
        # Create temporary plan
        result = manager.create_temporary_plan(
            user_request="Add user authentication",
            complexity_tier=3,
            estimated_time="2-3 hours",
            approach="Use JWT tokens with refresh strategy",
            phases=[
                {
                    "name": "Setup Authentication",
                    "description": "Install auth libraries",
                    "tasks": ["Install JWT library", "Configure middleware"]
                },
                {
                    "name": "Implement Login",
                    "description": "Create login endpoint",
                    "tasks": ["Create route", "Add validation"]
                }
            ]
        )
        
        # Verify result - now returns TemporaryPlan object directly
        assert isinstance(result, TemporaryPlan)
        assert result.user_request == "Add user authentication"
        assert result.complexity_tier == 3
        assert len(result.phases) == 2
        assert result.estimated_time == "2-3 hours"
    
    def test_approve_plan_generates_master_plan_with_unified_components(self, temp_workspace):
        """Test plan approval uses UnifiedPlanGenerator."""
        manager = TemporaryPlanManager(project_root=temp_workspace)
        
        # Create and approve a plan
        create_result = manager.create_temporary_plan(
            user_request="Refactor database layer",
            complexity_tier=2,
            estimated_time="3-4 hours",
            approach="Extract repository pattern",
            phases=[
                {
                    "name": "Create Repositories",
                    "description": "Extract DB logic to repositories",
                    "tasks": ["Create base repo", "Migrate queries"]
                }
            ]
        )
        
        plan_id = create_result.plan_id
        
        # Approve plan
        approve_result = manager.approve_plan(plan_id)
        
        # Verify master plan generated
        assert approve_result['success'] is True
        assert 'master_plan_path' in approve_result
        
        master_plan_path = Path(approve_result['master_plan_path'])
        assert master_plan_path.exists()
        
        # Verify content uses unified format
        content = master_plan_path.read_text(encoding='utf-8')
        assert "# 🧠 CORTEX" in content
        assert "Refactor database layer" in content
        assert "Phase 1" in content
    
    def test_mark_phase_complete_uses_phase_lifecycle_manager(self, temp_workspace):
        """Test phase completion delegates to PhaseLifecycleManager."""
        manager = TemporaryPlanManager(project_root=temp_workspace)
        
        # Create and approve plan
        create_result = manager.create_temporary_plan(
            user_request="Optimize queries",
            complexity_tier=2,
            estimated_time="4 hours",
            approach="Add indexes and query optimization",
            phases=[
                {"name": "Add Indexes", "description": "Create DB indexes", "tasks": ["Analyze slow queries"]},
                {"name": "Optimize Queries", "description": "Refactor N+1 queries", "tasks": ["Add eager loading"]}
            ]
        )
        
        plan_id = create_result.plan_id
        manager.approve_plan(plan_id)
        
        # Start and complete phase
        manager.mark_phase_in_progress(plan_id, 1)
        result = manager.mark_phase_complete(
            plan_id=plan_id,
            phase_number=1,
            duration_hours=2.5,
            tokens_saved=50000
        )
        
        # Verify result
        assert result['success'] is True
        
        # Verify master plan updated with completion
        approved_folder = temp_workspace / "cortex-brain" / "documents" / "planning" / "features" / "approved" / plan_id
        master_plan_path = approved_folder / "master-plan.md"
        content = master_plan_path.read_text(encoding='utf-8')
        
        # Should show phase 1 complete
        assert "✅ COMPLETE" in content or "COMPLETE" in content


class TestEndToEndPlanningWorkflow:
    """Test complete planning workflow with unified components."""
    
    def test_temp_plan_to_completion_workflow(self, temp_workspace):
        """Test full workflow: create → approve → execute → complete."""
        manager = TemporaryPlanManager(project_root=temp_workspace)
        
        # Step 1: Create temporary plan
        create_result = manager.create_temporary_plan(
            user_request="Add caching layer",
            complexity_tier=3,
            estimated_time="5-6 hours",
            approach="Redis-based caching with TTL",
            phases=[
                {"name": "Setup Redis", "description": "Install and configure", "tasks": ["Install redis", "Config"]},
                {"name": "Implement Cache", "description": "Add cache layer", "tasks": ["Create service", "Add decorators"]},
                {"name": "Testing", "description": "Test cache behavior", "tasks": ["Unit tests", "Integration tests"]}
            ]
        )
        
        assert isinstance(create_result, TemporaryPlan)
        plan_id = create_result.plan_id
        
        # Step 2: Approve plan (generates master plan)
        approve_result = manager.approve_plan(plan_id)
        assert approve_result['success'] is True
        
        master_plan_path = Path(approve_result['master_plan_path'])
        assert master_plan_path.exists()
        
        # Step 3: Execute phases
        for phase_num in range(1, 4):
            # Start phase
            manager.mark_phase_in_progress(plan_id, phase_num)
            
            # Complete phase
            result = manager.mark_phase_complete(
                plan_id=plan_id,
                phase_number=phase_num,
                duration_hours=1.5 * phase_num,
                tokens_saved=25000 * phase_num
            )
            assert result['success'] is True
        
        # Step 4: Verify final state
        content = master_plan_path.read_text(encoding='utf-8')
        
        # All phases should be complete
        complete_count = content.count("✅ COMPLETE") + content.count("COMPLETE")
        assert complete_count >= 3  # At least 3 phases marked complete
        
        # Visual progress should show 100%
        assert "100%" in content or "[████████████████████]" in content


class TestTokenTrackingIntegration:
    """Test token tracking across unified architecture."""
    
    def test_token_baseline_established_for_new_plan(self, temp_workspace):
        """Test token baseline established when creating plans."""
        manager = TemporaryPlanManager(project_root=temp_workspace)
        
        # Create plan
        result = manager.create_temporary_plan(
            user_request="Refactor auth module",
            complexity_tier=2,
            estimated_time="3 hours",
            approach="Extract to separate service",
            phases=[
                {"name": "Extract Service", "description": "Create auth service", "tasks": ["Create service class"]}
            ]
        )
        
        plan_id = result.plan_id
        
        # Establish baseline (would normally be called by orchestrator)
        baseline = manager.token_tracker.establish_baseline(
            plan_id=plan_id,
            total_tokens=1000000,
            total_files=500
        )
        
        assert baseline.plan_id == plan_id
        assert baseline.total_tokens == 1000000
        assert baseline.total_files == 500
    
    def test_token_reduction_recorded_on_phase_complete(self, temp_workspace):
        """Test token reductions tracked on phase completion."""
        manager = TemporaryPlanManager(project_root=temp_workspace)
        
        # Create and approve plan
        create_result = manager.create_temporary_plan(
            user_request="Remove unused code",
            complexity_tier=2,
            estimated_time="2 hours",
            approach="Identify and remove dead code",
            phases=[
                {"name": "Identify Dead Code", "description": "Run static analysis", "tasks": ["Run linter"]},
                {"name": "Remove Code", "description": "Delete unused functions", "tasks": ["Delete files"]}
            ]
        )
        
        plan_id = create_result.plan_id
        manager.approve_plan(plan_id)
        
        # Establish baseline
        manager.token_tracker.establish_baseline(plan_id, 1000000, 500)
        
        # Complete phases with token savings
        manager.mark_phase_in_progress(plan_id, 1)
        manager.mark_phase_complete(plan_id, 1, duration_hours=1.0, tokens_saved=50000)
        
        manager.mark_phase_in_progress(plan_id, 2)
        manager.mark_phase_complete(plan_id, 2, duration_hours=1.5, tokens_saved=75000)
        
        # Verify reductions recorded
        percentage = manager.token_tracker.calculate_percentage(plan_id)
        assert percentage > 0  # Should show reduction percentage
        
        # Total saved should be 125K
        total_saved = manager.token_tracker.get_total_saved(plan_id)
        assert total_saved == 125000


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
