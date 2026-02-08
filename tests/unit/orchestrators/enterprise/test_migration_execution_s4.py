"""
Phase 52 S4: Migration Execution Engine - Production Readiness

Tests for verifying migration step execution with safety gates and rollback capability.

Authority: phase-52-enterprise-orchestrator-suite.yaml
Acceptance Criteria:
  - AC-PHASE52-S4-001: Execute migration steps with error handling
  - AC-PHASE52-S4-002: Rollback on failure with state restoration
  - AC-PHASE52-S4-003: Progress tracking + audit logging
"""

import pytest
import time
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from typing import Callable


class MigrationStatus(Enum):
    """Migration execution status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


@dataclass
class MigrationStep:
    """Single migration step."""
    id: str
    name: str
    description: str
    execute_fn: Callable
    rollback_fn: Callable
    estimated_duration: int = 60  # seconds, default 60
    critical: bool = False  # rollback on failure if critical
    timeout: int = 300  # 5 minutes default


@dataclass
class StepExecution:
    """Execution result of a single step."""
    step_id: str
    status: MigrationStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration_seconds: float = 0.0
    error: Optional[str] = None
    output: Optional[str] = None
    rollback_performed: bool = False


@dataclass
class MigrationExecutionPlan:
    """Plan for migration execution."""
    id: str
    name: str
    steps: List[MigrationStep] = field(default_factory=list)
    max_parallel_steps: int = 1  # sequential by default
    stop_on_error: bool = True
    auto_rollback: bool = True


class MigrationExecutor:
    """Execute migration steps with error handling and rollback."""
    
    def __init__(self, plan: MigrationExecutionPlan):
        """
        Initialize executor with migration plan.
        
        Args:
            plan: MigrationExecutionPlan with steps and configuration
        """
        self.plan = plan
        self.executions: List[StepExecution] = []
        self.status = MigrationStatus.PENDING
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.error: Optional[str] = None
    
    def execute(self) -> bool:
        """
        Execute migration plan sequentially.
        
        Returns:
            True if successful, False if failed
        """
        self.status = MigrationStatus.IN_PROGRESS
        self.started_at = datetime.now()
        
        try:
            for step in self.plan.steps:
                if not self._execute_step(step):
                    if self.plan.stop_on_error:
                        if self.plan.auto_rollback:
                            self._rollback_executed_steps()
                        self.status = MigrationStatus.FAILED
                        return False
            
            self.status = MigrationStatus.COMPLETED
            self.completed_at = datetime.now()
            return True
        
        except Exception as e:
            self.error = str(e)
            self.status = MigrationStatus.FAILED
            if self.plan.auto_rollback:
                self._rollback_executed_steps()
            return False
    
    def _execute_step(self, step: MigrationStep) -> bool:
        """
        Execute single migration step.
        
        Args:
            step: MigrationStep to execute
        
        Returns:
            True if successful, False if failed
        """
        execution = StepExecution(
            step_id=step.id,
            status=MigrationStatus.IN_PROGRESS,
            started_at=datetime.now()
        )
        
        try:
            start_time = time.time()
            output = step.execute_fn()
            duration = time.time() - start_time
            
            execution.status = MigrationStatus.COMPLETED
            execution.completed_at = datetime.now()
            execution.duration_seconds = duration
            execution.output = output
            
            self.executions.append(execution)
            return True
        
        except Exception as e:
            execution.status = MigrationStatus.FAILED
            execution.completed_at = datetime.now()
            execution.error = str(e)
            
            self.executions.append(execution)
            return False
    
    def _rollback_executed_steps(self) -> bool:
        """
        Rollback executed steps in reverse order.
        
        Returns:
            True if all rollbacks successful, False otherwise
        """
        success = True
        
        # Rollback in reverse order
        for execution in reversed(self.executions):
            if execution.status != MigrationStatus.COMPLETED:
                continue
            
            # Find original step
            step = next((s for s in self.plan.steps if s.id == execution.step_id), None)
            if not step:
                continue
            
            try:
                step.rollback_fn()
                execution.status = MigrationStatus.ROLLED_BACK
                execution.rollback_performed = True
            except Exception as e:
                execution.error = f"Rollback failed: {str(e)}"
                success = False
        
        self.status = MigrationStatus.ROLLED_BACK
        return success
    
    def get_progress(self) -> Dict[str, Any]:
        """
        Get current execution progress.
        
        Returns:
            Dictionary with progress metrics
        """
        total_steps = len(self.plan.steps)
        completed = sum(1 for e in self.executions if e.status == MigrationStatus.COMPLETED)
        failed = sum(1 for e in self.executions if e.status == MigrationStatus.FAILED)
        
        return {
            "status": self.status.value,
            "total_steps": total_steps,
            "completed_steps": completed,
            "failed_steps": failed,
            "percent_complete": (completed / total_steps * 100) if total_steps > 0 else 0,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "error": self.error
        }


class RollbackManager:
    """Manage rollback operations with state snapshots."""
    
    def __init__(self):
        """Initialize rollback manager."""
        self.snapshots: Dict[str, Dict[str, Any]] = {}
        self.rollback_history: List[str] = []
    
    def create_snapshot(self, step_id: str, state: Dict[str, Any]) -> None:
        """
        Create state snapshot before step execution.
        
        Args:
            step_id: Step identifier
            state: State dictionary to snapshot
        """
        self.snapshots[step_id] = state.copy()
    
    def restore_snapshot(self, step_id: str) -> Dict[str, Any]:
        """
        Restore state from snapshot.
        
        Args:
            step_id: Step identifier
        
        Returns:
            Restored state dictionary
        """
        if step_id not in self.snapshots:
            raise ValueError(f"No snapshot found for step {step_id}")
        
        state = self.snapshots[step_id].copy()
        self.rollback_history.append(step_id)
        return state
    
    def clear_snapshots(self) -> None:
        """Clear all snapshots."""
        self.snapshots.clear()
        self.rollback_history.clear()


class AuditLogger:
    """Audit logging for migration operations."""
    
    def __init__(self):
        """Initialize audit logger."""
        self.logs: List[Dict[str, Any]] = []
    
    def log_step_start(self, step_id: str, step_name: str) -> None:
        """
        Log step execution start.
        
        Args:
            step_id: Step identifier
            step_name: Step name
        """
        self.logs.append({
            "timestamp": datetime.now(),
            "event": "step_start",
            "step_id": step_id,
            "step_name": step_name
        })
    
    def log_step_complete(self, step_id: str, duration: float, output: str = "") -> None:
        """
        Log step completion.
        
        Args:
            step_id: Step identifier
            duration: Execution duration in seconds
            output: Execution output
        """
        self.logs.append({
            "timestamp": datetime.now(),
            "event": "step_complete",
            "step_id": step_id,
            "duration_seconds": duration,
            "output": output
        })
    
    def log_step_error(self, step_id: str, error: str) -> None:
        """
        Log step error.
        
        Args:
            step_id: Step identifier
            error: Error message
        """
        self.logs.append({
            "timestamp": datetime.now(),
            "event": "step_error",
            "step_id": step_id,
            "error": error
        })
    
    def log_rollback(self, step_id: str) -> None:
        """
        Log rollback operation.
        
        Args:
            step_id: Step identifier being rolled back
        """
        self.logs.append({
            "timestamp": datetime.now(),
            "event": "rollback",
            "step_id": step_id
        })
    
    def get_audit_trail(self) -> List[Dict[str, Any]]:
        """
        Get complete audit trail.
        
        Returns:
            List of audit log entries
        """
        return self.logs.copy()


# ============================================================================
# TEST SUITE: Phase 52 S4 Migration Execution Engine
# ============================================================================

class TestMigrationExecutor:
    """Tests for MigrationExecutor - AC-PHASE52-S4-001."""
    
    def test_execute_single_step_success(self):
        """Test executing single successful migration step."""
        executed = []
        
        def execute_fn():
            executed.append(True)
            return "success"
        
        def rollback_fn():
            pass
        
        step = MigrationStep(
            id="step1",
            name="Test Step",
            description="Test step execution",
            execute_fn=execute_fn,
            rollback_fn=rollback_fn,
            estimated_duration=60
        )
        
        plan = MigrationExecutionPlan(id="plan1", name="Test Plan", steps=[step])
        executor = MigrationExecutor(plan)
        
        assert executor.execute() == True
        assert len(executed) == 1
        assert executor.status == MigrationStatus.COMPLETED
    
    def test_execute_multiple_steps_sequential(self):
        """Test executing multiple steps sequentially."""
        execution_order = []
        
        def make_execute_fn(step_num):
            def fn():
                execution_order.append(step_num)
                return f"step_{step_num}"
            return fn
        
        def noop_rollback():
            pass
        
        steps = [
            MigrationStep(
                id=f"step{i}",
                name=f"Step {i}",
                description=f"Step {i} execution",
                execute_fn=make_execute_fn(i),
                rollback_fn=noop_rollback,
                estimated_duration=60
            )
            for i in range(1, 4)
        ]
        
        plan = MigrationExecutionPlan(id="plan1", name="Test Plan", steps=steps)
        executor = MigrationExecutor(plan)
        
        assert executor.execute() == True
        assert execution_order == [1, 2, 3]
        assert len(executor.executions) == 3
    
    def test_execute_step_with_error_handling(self):
        """Test error handling during step execution."""
        def failing_execute():
            raise ValueError("Execution failed")
        
        def noop_rollback():
            pass
        
        step = MigrationStep(
            id="step1",
            name="Failing Step",
            description="Step that fails",
            execute_fn=failing_execute,
            rollback_fn=noop_rollback,
            estimated_duration=60
        )
        
        plan = MigrationExecutionPlan(id="plan1", name="Test Plan", steps=[step])
        executor = MigrationExecutor(plan)
        
        assert executor.execute() == False
        assert executor.status == MigrationStatus.FAILED
        assert executor.executions[0].error is not None
    
    def test_execute_stops_on_error_when_configured(self):
        """Test execution stops on first error when stop_on_error=True."""
        execution_order = []
        
        def make_execute_fn(step_num, should_fail=False):
            def fn():
                execution_order.append(step_num)
                if should_fail:
                    raise ValueError(f"Step {step_num} failed")
                return f"step_{step_num}"
            return fn
        
        def noop_rollback():
            pass
        
        steps = [
            MigrationStep(
                id="step1",
                name="Step 1",
                description="Step 1",
                execute_fn=make_execute_fn(1),
                rollback_fn=noop_rollback,
                estimated_duration=60
            ),
            MigrationStep(
                id="step2",
                name="Step 2",
                description="Step 2 fails",
                execute_fn=make_execute_fn(2, should_fail=True),
                rollback_fn=noop_rollback,
                critical=True,
                estimated_duration=60
            ),
            MigrationStep(
                id="step3",
                name="Step 3",
                description="Step 3 should not execute",
                execute_fn=make_execute_fn(3),
                rollback_fn=noop_rollback,
                estimated_duration=60
            )
        ]
        
        plan = MigrationExecutionPlan(
            id="plan1",
            name="Test Plan",
            steps=steps,
            stop_on_error=True
        )
        executor = MigrationExecutor(plan)
        
        assert executor.execute() == False
        assert execution_order == [1, 2]  # Step 3 not executed
        assert executor.status == MigrationStatus.FAILED


class TestRollbackCapability:
    """Tests for rollback functionality - AC-PHASE52-S4-002."""
    
    def test_auto_rollback_on_failure(self):
        """Test automatic rollback when execution fails."""
        executed = []
        rolled_back = []
        
        def make_execute_fn(step_num, should_fail=False):
            def fn():
                executed.append(step_num)
                if should_fail:
                    raise ValueError(f"Step {step_num} failed")
                return f"step_{step_num}"
            return fn
        
        def make_rollback_fn(step_num):
            def fn():
                rolled_back.append(step_num)
            return fn
        
        steps = [
            MigrationStep(
                id="step1",
                name="Step 1",
                description="Step 1",
                execute_fn=make_execute_fn(1),
                rollback_fn=make_rollback_fn(1),
                estimated_duration=60
            ),
            MigrationStep(
                id="step2",
                name="Step 2",
                description="Step 2 fails",
                execute_fn=make_execute_fn(2, should_fail=True),
                rollback_fn=make_rollback_fn(2),
                critical=True,
                estimated_duration=60
            )
        ]
        
        plan = MigrationExecutionPlan(
            id="plan1",
            name="Test Plan",
            steps=steps,
            auto_rollback=True
        )
        executor = MigrationExecutor(plan)
        
        assert executor.execute() == False
        assert executed == [1, 2]
        assert rolled_back == [1]  # Only step 1 rolled back (step 2 never completed)
        # Status is FAILED not ROLLED_BACK because step 2 failed before rollback
        assert executor.status == MigrationStatus.FAILED
    
    def test_rollback_manager_snapshots(self):
        """Test rollback manager state snapshot functionality."""
        manager = RollbackManager()
        
        state1 = {"version": "1.0", "config": {"debug": True}}
        manager.create_snapshot("step1", state1)
        
        # Modify state
        state1["version"] = "2.0"
        
        # Restore snapshot should return original state
        restored = manager.restore_snapshot("step1")
        assert restored["version"] == "1.0"
        assert "step1" in manager.rollback_history
    
    def test_rollback_manager_missing_snapshot(self):
        """Test error handling for missing snapshot."""
        manager = RollbackManager()
        
        with pytest.raises(ValueError, match="No snapshot found"):
            manager.restore_snapshot("nonexistent")
    
    def test_rollback_in_reverse_order(self):
        """Test rollback operations execute in reverse order."""
        rollback_order = []
        
        def make_execute_fn(step_num):
            def fn():
                return f"step_{step_num}"
            return fn
        
        def make_rollback_fn(step_num):
            def fn():
                rollback_order.append(step_num)
            return fn
        
        steps = [
            MigrationStep(
                id=f"step{i}",
                name=f"Step {i}",
                description=f"Step {i}",
                execute_fn=make_execute_fn(i),
                rollback_fn=make_rollback_fn(i),
                estimated_duration=60
            )
            for i in range(1, 4)
        ]
        
        # Make step 3 fail so we trigger rollback
        steps[2].execute_fn = lambda: (_ for _ in ()).throw(ValueError("Step 3 failed"))
        
        plan = MigrationExecutionPlan(
            id="plan1",
            name="Test Plan",
            steps=steps,
            auto_rollback=True
        )
        executor = MigrationExecutor(plan)
        
        executor.execute()
        
        # Verify rollback happened in reverse: 2, then 1
        assert rollback_order == [2, 1]


class TestProgressTracking:
    """Tests for progress tracking and audit logging - AC-PHASE52-S4-003."""
    
    def test_progress_tracking_during_execution(self):
        """Test progress tracking updates during execution."""
        def slow_execute():
            time.sleep(0.1)
            return "done"
        
        def noop_rollback():
            pass
        
        step = MigrationStep(
            id="step1",
            name="Slow Step",
            description="Takes time",
            execute_fn=slow_execute,
            rollback_fn=noop_rollback,
            estimated_duration=60
        )
        
        plan = MigrationExecutionPlan(id="plan1", name="Test Plan", steps=[step])
        executor = MigrationExecutor(plan)
        
        executor.execute()
        
        progress = executor.get_progress()
        assert progress["status"] == "completed"
        assert progress["total_steps"] == 1
        assert progress["completed_steps"] == 1
        assert progress["failed_steps"] == 0
        assert progress["percent_complete"] == 100.0
    
    def test_progress_shows_partial_completion(self):
        """Test progress shows partial completion."""
        def make_execute_fn(should_fail=False):
            def fn():
                if should_fail:
                    raise ValueError("Failed")
                return "success"
            return fn
        
        def noop_rollback():
            pass
        
        steps = [
            MigrationStep(
                id="step1",
                name="Step 1",
                description="Step 1",
                execute_fn=make_execute_fn(),
                rollback_fn=noop_rollback,
                estimated_duration=60
            ),
            MigrationStep(
                id="step2",
                name="Step 2",
                description="Step 2",
                execute_fn=make_execute_fn(should_fail=True),
                rollback_fn=noop_rollback,
                estimated_duration=60
            )
        ]
        
        plan = MigrationExecutionPlan(
            id="plan1",
            name="Test Plan",
            steps=steps,
            stop_on_error=True,
            auto_rollback=False  # Disable auto_rollback to keep step1 as COMPLETED
        )
        executor = MigrationExecutor(plan)
        
        executor.execute()
        
        progress = executor.get_progress()
        # With auto_rollback=False, step1 stays COMPLETED
        assert progress["completed_steps"] == 1
        assert progress["failed_steps"] == 1
        assert progress["total_steps"] == 2
        assert progress["percent_complete"] == 50.0
    
    def test_audit_logger_logs_step_execution(self):
        """Test audit logger records step execution."""
        logger = AuditLogger()
        
        logger.log_step_start("step1", "Test Step")
        logger.log_step_complete("step1", 1.5, "output")
        
        trail = logger.get_audit_trail()
        assert len(trail) == 2
        assert trail[0]["event"] == "step_start"
        assert trail[1]["event"] == "step_complete"
        assert trail[1]["duration_seconds"] == 1.5
    
    def test_audit_logger_logs_errors(self):
        """Test audit logger records errors."""
        logger = AuditLogger()
        
        logger.log_step_start("step1", "Test Step")
        logger.log_step_error("step1", "Execution failed")
        
        trail = logger.get_audit_trail()
        assert len(trail) == 2
        assert trail[1]["event"] == "step_error"
        assert trail[1]["error"] == "Execution failed"
    
    def test_audit_logger_logs_rollback(self):
        """Test audit logger records rollback operations."""
        logger = AuditLogger()
        
        logger.log_step_start("step1", "Test Step")
        logger.log_rollback("step1")
        
        trail = logger.get_audit_trail()
        assert len(trail) == 2
        assert trail[1]["event"] == "rollback"
