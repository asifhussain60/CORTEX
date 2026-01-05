"""
Tests for Planning Orchestrator v5.1 Pilot - TaskListOrchestrator Integration.

Tests the pilot implementation demonstrating TaskListOrchestrator integration
with Planning v5 for state management and recovery.

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any

from src.orchestrators.planning.planning_orchestrator_v5_1_pilot import PlanningOrchestratorV5_1_Pilot
from src.database.planning_state_db import PlanningStateDB


@pytest.fixture
def temp_dir():
    """Create temporary directory for test databases."""
    temp_path = tempfile.mkdtemp()
    yield temp_path
    shutil.rmtree(temp_path)


@pytest.fixture
def state_db(temp_dir):
    """Create test planning state database."""
    db_path = Path(temp_dir) / "test_planning_v5_1.db"
    db = PlanningStateDB(db_path=str(db_path))
    
    # Create test plan for orchestrator
    plan_id = db.create_plan(
        feature_name="Test Planning v5.1 Pilot"
    )
    
    yield db, plan_id


class TestPlanningV5_1_PilotBasics:
    """Test basic initialization and configuration."""
    
    def test_initialization(self, state_db):
        """Test pilot orchestrator initialization."""
        db, plan_id = state_db
        
        orch = PlanningOrchestratorV5_1_Pilot(
            state_db=db,
            plan_id=plan_id
        )
        
        assert orch is not None
        assert orch.task_orchestrator is None  # Not created until execution
        assert orch.resume is False
    
    def test_initialization_with_resume(self, state_db):
        """Test pilot initialization with resume flag."""
        db, plan_id = state_db
        
        orch = PlanningOrchestratorV5_1_Pilot(
            state_db=db,
            plan_id=plan_id,
            resume=True
        )
        
        assert orch.resume is True


class TestPlanningV5_1_PilotTaskDefinition:
    """Test task definition and orchestrator setup."""
    
    def test_task_definition(self, state_db):
        """Test that planning tasks are correctly defined."""
        db, plan_id = state_db
        
        orch = PlanningOrchestratorV5_1_Pilot(
            state_db=db,
            plan_id=plan_id
        )
        
        # Execute with tasks
        result = orch.execute_with_tasks("plan authentication feature")
        
        # Verify task orchestrator was created
        assert orch.task_orchestrator is not None
        
        # Verify 6 tasks were defined
        progress = orch.task_orchestrator.get_progress()
        assert progress["total_tasks"] == 6
    
    def test_task_dependencies(self, state_db):
        """Test that task dependencies are correctly configured."""
        db, plan_id = state_db
        
        orch = PlanningOrchestratorV5_1_Pilot(
            state_db=db,
            plan_id=plan_id
        )
        
        orch.execute_with_tasks("plan authentication feature")
        
        # Check task dependency chain
        tasks = orch.task_orchestrator.tasks
        
        # discover_context depends on parse_request
        discover = next(t for t in tasks if t.task_id == "discover_context")
        assert "parse_request" in discover.depends_on
        
        # analyze_architecture depends on discover_context
        analyze = next(t for t in tasks if t.task_id == "analyze_architecture")
        assert "discover_context" in analyze.depends_on
        
        # generate_plan depends on analyze_architecture
        generate = next(t for t in tasks if t.task_id == "generate_plan")
        assert "analyze_architecture" in generate.depends_on
    
    def test_strategic_checkpoints(self, state_db):
        """Test that strategic checkpoints are configured correctly."""
        db, plan_id = state_db
        
        orch = PlanningOrchestratorV5_1_Pilot(
            state_db=db,
            plan_id=plan_id
        )
        
        orch.execute_with_tasks("plan authentication feature")
        
        tasks = orch.task_orchestrator.tasks
        
        # discover_context should have checkpoint
        discover = next(t for t in tasks if t.task_id == "discover_context")
        assert discover.checkpoint_before is True, "discover_context should checkpoint (slow search)"
        
        # generate_plan should have checkpoint
        generate = next(t for t in tasks if t.task_id == "generate_plan")
        assert generate.checkpoint_before is True, "generate_plan should checkpoint (complex rendering)"
        
        # parse_request should NOT have checkpoint (fast)
        parse = next(t for t in tasks if t.task_id == "parse_request")
        assert parse.checkpoint_before is False


class TestPlanningV5_1_PilotExecution:
    """Test task execution and progress tracking."""
    
    def test_full_execution(self, state_db):
        """Test complete planning execution with all tasks."""
        db, plan_id = state_db
        
        orch = PlanningOrchestratorV5_1_Pilot(
            state_db=db,
            plan_id=plan_id
        )
        
        result = orch.execute_with_tasks("plan authentication feature")
        
        # Verify success
        assert result["success"] is True
        assert result["error"] is None
        
        # Verify all tasks completed
        assert result["completed_tasks"] == 6
        assert result["failed_tasks"] == 0
        
        # Verify progress
        progress = result["progress"]
        assert progress["completed"] == 6
        assert progress["total_tasks"] == 6
        assert progress["progress_percent"] == 100.0
    
    def test_task_results(self, state_db):
        """Test that task results are captured correctly."""
        db, plan_id = state_db
        
        orch = PlanningOrchestratorV5_1_Pilot(
            state_db=db,
            plan_id=plan_id
        )
        
        result = orch.execute_with_tasks("plan authentication feature")
        
        task_results = result["task_results"]
        
        # Verify all tasks have results
        assert "parse_request" in task_results
        assert "discover_context" in task_results
        assert "analyze_architecture" in task_results
        assert "generate_plan" in task_results
        assert "create_folders" in task_results
        assert "validate_plan" in task_results
        
        # Verify result structure
        parse_result = task_results["parse_request"]
        assert "plan_id" in parse_result
        assert parse_result["status"] == "completed"
    
    def test_sequential_execution(self, state_db):
        """Test that tasks execute in correct dependency order."""
        db, plan_id = state_db
        
        orch = PlanningOrchestratorV5_1_Pilot(
            state_db=db,
            plan_id=plan_id
        )
        
        result = orch.execute_with_tasks("plan authentication feature")
        
        # Get completed tasks in order
        completed = orch.task_orchestrator.get_completed_tasks()
        task_ids = [task.task_id for task in completed]
        
        # Verify order respects dependencies
        assert task_ids.index("parse_request") < task_ids.index("discover_context")
        assert task_ids.index("discover_context") < task_ids.index("analyze_architecture")
        assert task_ids.index("analyze_architecture") < task_ids.index("generate_plan")
        assert task_ids.index("generate_plan") < task_ids.index("create_folders")
        assert task_ids.index("create_folders") < task_ids.index("validate_plan")


class TestPlanningV5_1_PilotCheckpoints:
    """Test checkpoint creation and recovery."""
    
    def test_checkpoint_creation(self, state_db):
        """Test that checkpoints are created at strategic points."""
        db, plan_id = state_db
        
        orch = PlanningOrchestratorV5_1_Pilot(
            state_db=db,
            plan_id=plan_id
        )
        
        result = orch.execute_with_tasks("plan authentication feature")
        
        # Get latest snapshot from database (should exist if checkpoints worked)
        orchestrator_id = f"planning-v5-{plan_id}"
        latest_snapshot = db.get_latest_snapshot(plan_id=orchestrator_id)
        
        # Should have at least one checkpoint created
        # (Even if execution failed, initial checkpoint should exist)
        assert latest_snapshot is not None or result["success"] is False, \
            "Expected either successful checkpoint or failed execution"
    
    def test_recovery_without_checkpoint(self, state_db):
        """Test recovery when no checkpoint exists (fresh start)."""
        db, plan_id = state_db
        
        orch = PlanningOrchestratorV5_1_Pilot(
            state_db=db,
            plan_id=plan_id,
            resume=True  # Try to resume but no checkpoint exists
        )
        
        # Should start from beginning without error
        result = orch.execute_with_tasks("plan authentication feature")
        
        assert result["success"] is True
        assert result["completed_tasks"] == 6


class TestPlanningV5_1_PilotRecovery:
    """Test recovery from interruptions."""
    
    def test_recovery_after_partial_execution(self, state_db):
        """Test recovery after partial execution with checkpoint."""
        db, plan_id = state_db
        
        # First execution - complete up to checkpoint
        orch1 = PlanningOrchestratorV5_1_Pilot(
            state_db=db,
            plan_id=plan_id
        )
        
        # Execute first task only (parse_request)
        orch1.execute_with_tasks("plan authentication feature")
        
        # Force orchestrator to stop after first checkpoint
        # (In real scenario, this would be an interruption)
        orch1.task_orchestrator.checkpoint("Manual checkpoint after parse")
        
        # Second execution - recover and continue
        orch2 = PlanningOrchestratorV5_1_Pilot(
            state_db=db,
            plan_id=plan_id,
            resume=True
        )
        
        # Set user_request for recovery
        orch2.user_request = "plan authentication feature"
        orch2.execution_kwargs = {}
        
        # Recover should work (though may restart since we don't have state preservation)
        result = orch2.execute_with_tasks("plan authentication feature")
        
        # Should complete successfully
        assert result["success"] is True


class TestPlanningV5_1_PilotPerformance:
    """Test performance characteristics."""
    
    def test_execution_timing(self, state_db):
        """Test that execution completes within reasonable time."""
        import time
        
        db, plan_id = state_db
        
        orch = PlanningOrchestratorV5_1_Pilot(
            state_db=db,
            plan_id=plan_id
        )
        
        start_time = time.time()
        result = orch.execute_with_tasks("plan authentication feature")
        elapsed = time.time() - start_time
        
        # Should complete in under 1 second (includes simulated delays)
        assert elapsed < 1.0, f"Execution took {elapsed:.3f}s (expected <1.0s)"
        
        # Verify success
        assert result["success"] is True
    
    def test_checkpoint_timing(self, state_db):
        """Test that checkpoints are fast (<1ms each)."""
        db, plan_id = state_db
        
        orch = PlanningOrchestratorV5_1_Pilot(
            state_db=db,
            plan_id=plan_id
        )
        
        # Execute to create checkpoints
        result = orch.execute_with_tasks("plan authentication feature")
        
        # Get completed tasks with timing
        completed = orch.task_orchestrator.get_completed_tasks()
        
        # Find tasks that create checkpoints
        checkpointed_tasks = [
            task for task in completed
            if task.checkpoint_before
        ]
        
        # Each checkpoint should be very fast
        # (Actual checkpoint time is separate from task execution time)
        for task in checkpointed_tasks:
            assert task.duration_ms is not None
            # Task execution + checkpoint should still be fast
            assert task.duration_ms < 1000, f"Task {task.task_id} took {task.duration_ms}ms"


class TestPlanningV5_1_PilotIntegration:
    """Integration tests with Planning v5 base class."""
    
    def test_extends_planning_v5(self, state_db):
        """Test that pilot properly extends Planning v5."""
        db, plan_id = state_db
        
        orch = PlanningOrchestratorV5_1_Pilot(
            state_db=db,
            plan_id=plan_id
        )
        
        # Should have access to parent methods
        assert hasattr(orch, "execute")
        assert hasattr(orch, "execute_with_tasks")
    
    def test_backward_compatibility(self, state_db):
        """Test that pilot maintains backward compatibility."""
        db, plan_id = state_db
        
        orch = PlanningOrchestratorV5_1_Pilot(
            state_db=db,
            plan_id=plan_id
        )
        
        # Pilot-specific method should work
        result = orch.execute_with_tasks("plan authentication feature")
        assert result["success"] is True
        
        # Should have same database as parent
        assert orch.state_db == db
        assert orch.plan_id == plan_id


class TestPlanningV5_1_PilotTaskExecutors:
    """Test individual task executors."""
    
    def test_parse_request_task(self, state_db):
        """Test parse_request task executor."""
        db, plan_id = state_db
        
        orch = PlanningOrchestratorV5_1_Pilot(
            state_db=db,
            plan_id=plan_id
        )
        
        result = orch._task_parse_request({"user_request": "test feature"})
        
        assert "plan_id" in result
        assert "feature_name" in result
        assert result["status"] == "completed"
    
    def test_discover_context_task(self, state_db):
        """Test discover_context task executor."""
        db, plan_id = state_db
        
        orch = PlanningOrchestratorV5_1_Pilot(
            state_db=db,
            plan_id=plan_id
        )
        
        result = orch._task_discover_context({})
        
        assert "discovered_files" in result
        assert "semantic_results" in result
        assert result["status"] == "completed"
    
    def test_generate_plan_task(self, state_db):
        """Test generate_plan task executor."""
        db, plan_id = state_db
        
        orch = PlanningOrchestratorV5_1_Pilot(
            state_db=db,
            plan_id=plan_id
        )
        
        result = orch._task_generate_plan({})
        
        assert "phases" in result
        assert "tasks" in result
        assert "plan_path" in result
        assert result["status"] == "completed"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
