"""
Unit tests for ExecutionEngine.

Test-first approach per CORTEX SKULL rules.

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import pytest
from datetime import datetime
from typing import Dict, Any
from src.orchestrators.execution_engine import (
    ExecutionEngine,
    ExecutionContext,
    ExecutionResult,
    ExecutionStatus,
    ExecutionError,
    PhaseExecutor,
    TaskExecutor
)


class TestExecutionEngine:
    """Test suite for ExecutionEngine."""
    
    @pytest.fixture
    def execution_engine(self, tmp_path):
        """Create ExecutionEngine instance."""
        return ExecutionEngine(metrics_dir=str(tmp_path))
    
    def test_initialization(self, execution_engine):
        """Test ExecutionEngine initializes correctly."""
        assert execution_engine is not None
        assert hasattr(execution_engine, 'metrics_dir')
        assert hasattr(execution_engine, 'active_executions')
    
    def test_create_execution_context(self, execution_engine):
        """Test creating execution context."""
        context = ExecutionContext(
            execution_id="exec_123",
            plan_id="plan_456",
            phase_number=1,
            started_at=datetime.now()
        )
        
        assert context.execution_id == "exec_123"
        assert context.plan_id == "plan_456"
        assert context.phase_number == 1
    
    def test_execute_phase_success(self, execution_engine):
        """Test successful phase execution."""
        context = ExecutionContext(
            execution_id="exec_1",
            plan_id="plan_1",
            phase_number=1,
            started_at=datetime.now()
        )
        
        def mock_phase():
            return {"status": "success"}
        
        result = execution_engine.execute_phase(context, mock_phase)
        
        assert result.status == ExecutionStatus.SUCCESS
        assert result.execution_id == "exec_1"
    
    def test_execute_phase_failure(self, execution_engine):
        """Test phase execution failure handling."""
        context = ExecutionContext(
            execution_id="exec_1",
            plan_id="plan_1",
            phase_number=1,
            started_at=datetime.now()
        )
        
        def failing_phase():
            raise Exception("Phase failed")
        
        result = execution_engine.execute_phase(context, failing_phase)
        
        assert result.status == ExecutionStatus.FAILED
        assert result.error is not None
    
    def test_execute_task(self, execution_engine):
        """Test task execution."""
        def sample_task():
            return "Task completed"
        
        result = execution_engine.execute_task("task_1", sample_task)
        
        assert result.status == ExecutionStatus.SUCCESS
        assert result.output == "Task completed"
    
    def test_execute_task_with_timeout(self, execution_engine):
        """Test task execution with timeout."""
        import time
        
        def slow_task():
            time.sleep(5)
            return "Done"
        
        result = execution_engine.execute_task(
            "task_1", 
            slow_task, 
            timeout=1
        )
        
        assert result.status == ExecutionStatus.TIMEOUT
    
    def test_record_execution_metrics(self, execution_engine):
        """Test recording execution metrics."""
        context = ExecutionContext(
            execution_id="exec_1",
            plan_id="plan_1",
            phase_number=1,
            started_at=datetime.now()
        )
        
        result = ExecutionResult(
            execution_id="exec_1",
            status=ExecutionStatus.SUCCESS,
            started_at=datetime.now(),
            completed_at=datetime.now(),
            output={}
        )
        
        success = execution_engine.record_metrics(context, result)
        
        assert success is True
    
    def test_get_execution_status(self, execution_engine):
        """Test retrieving execution status."""
        context = ExecutionContext(
            execution_id="exec_1",
            plan_id="plan_1",
            phase_number=1,
            started_at=datetime.now()
        )
        
        execution_engine.active_executions["exec_1"] = context
        
        status = execution_engine.get_execution_status("exec_1")
        
        assert status is not None
        assert status.execution_id == "exec_1"
    
    def test_cancel_execution(self, execution_engine):
        """Test canceling active execution."""
        context = ExecutionContext(
            execution_id="exec_1",
            plan_id="plan_1",
            phase_number=1,
            started_at=datetime.now()
        )
        
        execution_engine.active_executions["exec_1"] = context
        
        success = execution_engine.cancel_execution("exec_1")
        
        assert success is True
        assert "exec_1" not in execution_engine.active_executions
    
    def test_list_active_executions(self, execution_engine):
        """Test listing active executions."""
        ctx1 = ExecutionContext(
            execution_id="exec_1",
            plan_id="plan_1",
            phase_number=1,
            started_at=datetime.now()
        )
        ctx2 = ExecutionContext(
            execution_id="exec_2",
            plan_id="plan_2",
            phase_number=2,
            started_at=datetime.now()
        )
        
        execution_engine.active_executions["exec_1"] = ctx1
        execution_engine.active_executions["exec_2"] = ctx2
        
        active = execution_engine.list_active_executions()
        
        assert len(active) == 2
        assert "exec_1" in [e.execution_id for e in active]
        assert "exec_2" in [e.execution_id for e in active]
    
    def test_get_execution_metrics(self, execution_engine):
        """Test retrieving execution metrics."""
        metrics = execution_engine.get_metrics()
        
        assert "total_executions" in metrics
        assert "active_executions" in metrics
        assert "completed_executions" in metrics


class TestPhaseExecutor:
    """Test suite for PhaseExecutor."""
    
    def test_phase_executor_creation(self):
        """Test PhaseExecutor can be created."""
        executor = PhaseExecutor()
        assert executor is not None
    
    def test_execute_phase_with_tasks(self):
        """Test executing phase with multiple tasks."""
        executor = PhaseExecutor()
        
        tasks = [
            lambda: "Task 1",
            lambda: "Task 2",
            lambda: "Task 3"
        ]
        
        result = executor.execute(tasks)
        
        assert result.status == ExecutionStatus.SUCCESS
        assert len(result.task_results) == 3


class TestTaskExecutor:
    """Test suite for TaskExecutor."""
    
    def test_task_executor_creation(self):
        """Test TaskExecutor can be created."""
        executor = TaskExecutor()
        assert executor is not None
    
    def test_execute_single_task(self):
        """Test executing single task."""
        executor = TaskExecutor()
        
        def sample_task():
            return {"result": "success"}
        
        result = executor.execute(sample_task)
        
        assert result.status == ExecutionStatus.SUCCESS
        assert result.output["result"] == "success"
