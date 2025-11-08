"""
Unit Tests for CORTEX Workflow Engine

Tests for WorkflowState, StageDefinition, WorkflowDefinition,
DAG validation, topological sort, and WorkflowOrchestrator.

Author: CORTEX Development Team
Date: 2025-11-08
"""

import pytest
import tempfile
import json
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch

from src.workflows.workflow_engine import (
    StageStatus,
    StageResult,
    WorkflowState,
    StageDefinition,
    WorkflowDefinition,
    WorkflowOrchestrator,
    BaseWorkflowStage,
)


class TestWorkflowState:
    """Tests for WorkflowState dataclass"""
    
    def test_create_workflow_state(self):
        """Test creating a workflow state"""
        state = WorkflowState(
            workflow_id="wf-001",
            conversation_id="conv-123",
            user_request="Implement feature X"
        )
        
        assert state.workflow_id == "wf-001"
        assert state.conversation_id == "conv-123"
        assert state.user_request == "Implement feature X"
        assert state.context == {}
        assert state.stage_outputs == {}
        assert state.stage_statuses == {}
    
    def test_set_and_get_stage_output(self):
        """Test setting and getting stage outputs"""
        state = WorkflowState(
            workflow_id="wf-001",
            conversation_id="conv-123",
            user_request="Test"
        )
        
        output = {"files": ["test.py"], "status": "completed"}
        state.set_stage_output("stage1", output)
        
        assert state.get_stage_output("stage1") == output
        assert state.get_stage_output("nonexistent") is None
    
    def test_set_stage_status(self):
        """Test setting stage status"""
        state = WorkflowState(
            workflow_id="wf-001",
            conversation_id="conv-123",
            user_request="Test"
        )
        
        state.set_stage_status("stage1", StageStatus.RUNNING)
        assert state.stage_statuses["stage1"] == StageStatus.RUNNING
        
        state.set_stage_status("stage1", StageStatus.SUCCESS)
        assert state.stage_statuses["stage1"] == StageStatus.SUCCESS
    
    def test_to_dict(self):
        """Test serializing WorkflowState to dict"""
        state = WorkflowState(
            workflow_id="wf-001",
            conversation_id="conv-123",
            user_request="Test",
            start_time="2025-11-08T10:00:00"
        )
        state.set_stage_status("stage1", StageStatus.SUCCESS)
        state.set_stage_output("stage1", {"result": "ok"})
        
        data = state.to_dict()
        
        assert data["workflow_id"] == "wf-001"
        assert data["conversation_id"] == "conv-123"
        assert data["user_request"] == "Test"
        assert data["stage_statuses"]["stage1"] == "success"
        assert data["stage_outputs"]["stage1"] == {"result": "ok"}
    
    def test_from_dict(self):
        """Test deserializing WorkflowState from dict"""
        data = {
            "workflow_id": "wf-002",
            "conversation_id": "conv-456",
            "user_request": "Fix bug Y",
            "context": {"tier1": "data"},
            "stage_outputs": {"stage1": {"files": ["fix.py"]}},
            "stage_statuses": {"stage1": "success", "stage2": "pending"},
            "start_time": "2025-11-08T10:00:00",
            "end_time": None,
            "current_stage": "stage2",
            "config": {"debug": True}
        }
        
        state = WorkflowState.from_dict(data)
        
        assert state.workflow_id == "wf-002"
        assert state.conversation_id == "conv-456"
        assert state.user_request == "Fix bug Y"
        assert state.context == {"tier1": "data"}
        assert state.stage_outputs["stage1"] == {"files": ["fix.py"]}
        assert state.stage_statuses["stage1"] == StageStatus.SUCCESS
        assert state.stage_statuses["stage2"] == StageStatus.PENDING
        assert state.current_stage == "stage2"


class TestStageDefinition:
    """Tests for StageDefinition dataclass"""
    
    def test_create_stage_definition(self):
        """Test creating a stage definition"""
        stage = StageDefinition(
            id="clarify",
            script="clarify_dod_dor.py",
            required=True,
            depends_on=[]
        )
        
        assert stage.id == "clarify"
        assert stage.script == "clarify_dod_dor.py"
        assert stage.required is True
        assert stage.depends_on == []
        assert stage.retryable is False
        assert stage.max_retries == 0
        assert stage.timeout_seconds == 300
    
    def test_stage_with_dependencies(self):
        """Test stage with dependencies"""
        stage = StageDefinition(
            id="test",
            script="run_tests.py",
            depends_on=["plan", "implement"]
        )
        
        assert stage.depends_on == ["plan", "implement"]
    
    def test_stage_with_retry_config(self):
        """Test stage with retry configuration"""
        stage = StageDefinition(
            id="deploy",
            script="deploy.py",
            retryable=True,
            max_retries=3,
            timeout_seconds=600
        )
        
        assert stage.retryable is True
        assert stage.max_retries == 3
        assert stage.timeout_seconds == 600


class TestWorkflowDefinition:
    """Tests for WorkflowDefinition and DAG validation"""
    
    def test_create_workflow_definition(self):
        """Test creating a workflow definition"""
        stages = [
            StageDefinition(id="stage1", script="s1.py"),
            StageDefinition(id="stage2", script="s2.py", depends_on=["stage1"]),
        ]
        
        workflow = WorkflowDefinition(
            workflow_id="wf-test",
            name="Test Workflow",
            description="Test workflow",
            stages=stages
        )
        
        assert workflow.workflow_id == "wf-test"
        assert workflow.name == "Test Workflow"
        assert len(workflow.stages) == 2
        assert workflow.version == "1.0.0"
    
    def test_validate_dag_success(self):
        """Test DAG validation with valid workflow"""
        stages = [
            StageDefinition(id="stage1", script="s1.py"),
            StageDefinition(id="stage2", script="s2.py", depends_on=["stage1"]),
            StageDefinition(id="stage3", script="s3.py", depends_on=["stage2"]),
        ]
        
        workflow = WorkflowDefinition(
            workflow_id="wf-test",
            name="Test Workflow",
            description="Test",
            stages=stages
        )
        
        errors = workflow.validate_dag()
        assert errors == []
    
    def test_validate_dag_missing_dependency(self):
        """Test DAG validation detects missing dependencies"""
        stages = [
            StageDefinition(id="stage1", script="s1.py"),
            StageDefinition(id="stage2", script="s2.py", depends_on=["nonexistent"]),
        ]
        
        workflow = WorkflowDefinition(
            workflow_id="wf-test",
            name="Test Workflow",
            description="Test",
            stages=stages
        )
        
        errors = workflow.validate_dag()
        assert len(errors) == 1
        assert "nonexistent" in errors[0]
    
    def test_validate_dag_cycle_detection(self):
        """Test DAG validation detects circular dependencies"""
        stages = [
            StageDefinition(id="stage1", script="s1.py", depends_on=["stage2"]),
            StageDefinition(id="stage2", script="s2.py", depends_on=["stage1"]),
        ]
        
        workflow = WorkflowDefinition(
            workflow_id="wf-test",
            name="Test Workflow",
            description="Test",
            stages=stages
        )
        
        errors = workflow.validate_dag()
        assert len(errors) == 1
        assert "cycle" in errors[0].lower() or "circular" in errors[0].lower()
    
    def test_topological_sort_linear(self):
        """Test topological sort with linear dependencies"""
        stages = [
            StageDefinition(id="stage1", script="s1.py"),
            StageDefinition(id="stage2", script="s2.py", depends_on=["stage1"]),
            StageDefinition(id="stage3", script="s3.py", depends_on=["stage2"]),
        ]
        
        workflow = WorkflowDefinition(
            workflow_id="wf-test",
            name="Test Workflow",
            description="Test",
            stages=stages
        )
        
        order = workflow.get_execution_order()
        assert order == ["stage1", "stage2", "stage3"]
    
    def test_topological_sort_parallel(self):
        """Test topological sort with parallel stages"""
        stages = [
            StageDefinition(id="stage1", script="s1.py"),
            StageDefinition(id="stage2", script="s2.py", depends_on=["stage1"]),
            StageDefinition(id="stage3", script="s3.py", depends_on=["stage1"]),
            StageDefinition(id="stage4", script="s4.py", depends_on=["stage2", "stage3"]),
        ]
        
        workflow = WorkflowDefinition(
            workflow_id="wf-test",
            name="Test Workflow",
            description="Test",
            stages=stages
        )
        
        order = workflow.get_execution_order()
        
        # stage1 must be first
        assert order[0] == "stage1"
        # stage2 and stage3 can be in any order (both depend only on stage1)
        assert set(order[1:3]) == {"stage2", "stage3"}
        # stage4 must be last
        assert order[3] == "stage4"
    
    def test_from_yaml(self):
        """Test loading workflow from YAML file"""
        yaml_content = """
workflow_id: test-workflow
name: Test Workflow
description: A test workflow
version: 1.0.0
stages:
  - id: stage1
    script: s1.py
    required: true
    depends_on: []
  - id: stage2
    script: s2.py
    required: false
    depends_on: ["stage1"]
    retryable: true
    max_retries: 3
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_content)
            temp_path = Path(f.name)
        
        try:
            workflow = WorkflowDefinition.from_yaml(temp_path)
            
            assert workflow.workflow_id == "test-workflow"
            assert workflow.name == "Test Workflow"
            assert len(workflow.stages) == 2
            assert workflow.stages[0].id == "stage1"
            assert workflow.stages[0].required is True
            assert workflow.stages[1].id == "stage2"
            assert workflow.stages[1].required is False
            assert workflow.stages[1].retryable is True
            assert workflow.stages[1].max_retries == 3
        finally:
            temp_path.unlink()


class MockStage(BaseWorkflowStage):
    """Mock stage for testing"""
    
    def __init__(self, stage_id: str, should_fail: bool = False, output: dict = None):
        super().__init__(stage_id)
        self.should_fail = should_fail
        self.output = output or {}
        self.execute_count = 0
    
    def execute(self, state: WorkflowState) -> StageResult:
        self.execute_count += 1
        
        if self.should_fail:
            return StageResult(
                stage_id=self.stage_id,
                status=StageStatus.FAILED,
                duration_ms=10,
                error="Mock failure"
            )
        
        return StageResult(
            stage_id=self.stage_id,
            status=StageStatus.SUCCESS,
            duration_ms=10,
            output=self.output
        )


class TestWorkflowOrchestrator:
    """Tests for WorkflowOrchestrator"""
    
    def test_create_orchestrator_valid_workflow(self):
        """Test creating orchestrator with valid workflow"""
        stages = [
            StageDefinition(id="stage1", script="s1.py"),
            StageDefinition(id="stage2", script="s2.py", depends_on=["stage1"]),
        ]
        
        workflow = WorkflowDefinition(
            workflow_id="wf-test",
            name="Test",
            description="Test",
            stages=stages
        )
        
        orchestrator = WorkflowOrchestrator(workflow)
        
        assert orchestrator.workflow_def == workflow
        assert orchestrator.execution_order == ["stage1", "stage2"]
    
    def test_create_orchestrator_invalid_workflow(self):
        """Test creating orchestrator with invalid workflow raises error"""
        stages = [
            StageDefinition(id="stage1", script="s1.py", depends_on=["stage2"]),
            StageDefinition(id="stage2", script="s2.py", depends_on=["stage1"]),
        ]
        
        workflow = WorkflowDefinition(
            workflow_id="wf-test",
            name="Test",
            description="Test",
            stages=stages
        )
        
        with pytest.raises(ValueError, match="Invalid workflow DAG"):
            WorkflowOrchestrator(workflow)
    
    def test_register_stage(self):
        """Test registering stage implementations"""
        stages = [StageDefinition(id="stage1", script="s1.py")]
        workflow = WorkflowDefinition(
            workflow_id="wf-test",
            name="Test",
            description="Test",
            stages=stages
        )
        
        orchestrator = WorkflowOrchestrator(workflow)
        mock_stage = MockStage("stage1")
        
        orchestrator.register_stage("stage1", mock_stage)
        
        assert orchestrator._stages["stage1"] == mock_stage
    
    def test_execute_simple_workflow(self):
        """Test executing a simple workflow"""
        stages = [
            StageDefinition(id="stage1", script="s1.py"),
            StageDefinition(id="stage2", script="s2.py", depends_on=["stage1"]),
        ]
        
        workflow = WorkflowDefinition(
            workflow_id="wf-test",
            name="Test",
            description="Test",
            stages=stages
        )
        
        orchestrator = WorkflowOrchestrator(workflow)
        orchestrator.register_stage("stage1", MockStage("stage1", output={"result": "s1"}))
        orchestrator.register_stage("stage2", MockStage("stage2", output={"result": "s2"}))
        
        state = orchestrator.execute(
            user_request="Test request",
            conversation_id="conv-123"
        )
        
        assert state.stage_statuses["stage1"] == StageStatus.SUCCESS
        assert state.stage_statuses["stage2"] == StageStatus.SUCCESS
        assert state.stage_outputs["stage1"] == {"result": "s1"}
        assert state.stage_outputs["stage2"] == {"result": "s2"}
        assert state.end_time is not None
    
    def test_execute_workflow_with_required_stage_failure(self):
        """Test workflow stops when required stage fails"""
        stages = [
            StageDefinition(id="stage1", script="s1.py", required=True),
            StageDefinition(id="stage2", script="s2.py", depends_on=["stage1"]),
        ]
        
        workflow = WorkflowDefinition(
            workflow_id="wf-test",
            name="Test",
            description="Test",
            stages=stages
        )
        
        orchestrator = WorkflowOrchestrator(workflow)
        orchestrator.register_stage("stage1", MockStage("stage1", should_fail=True))
        orchestrator.register_stage("stage2", MockStage("stage2"))
        
        state = orchestrator.execute(
            user_request="Test request",
            conversation_id="conv-123"
        )
        
        assert state.stage_statuses["stage1"] == StageStatus.FAILED
        assert state.stage_statuses["stage2"] == StageStatus.PENDING  # Never executed
    
    def test_execute_workflow_with_optional_stage_failure(self):
        """Test workflow continues when optional stage fails"""
        stages = [
            StageDefinition(id="stage1", script="s1.py", required=False),
            StageDefinition(id="stage2", script="s2.py", depends_on=[]),
        ]
        
        workflow = WorkflowDefinition(
            workflow_id="wf-test",
            name="Test",
            description="Test",
            stages=stages
        )
        
        orchestrator = WorkflowOrchestrator(workflow)
        orchestrator.register_stage("stage1", MockStage("stage1", should_fail=True))
        orchestrator.register_stage("stage2", MockStage("stage2"))
        
        state = orchestrator.execute(
            user_request="Test request",
            conversation_id="conv-123"
        )
        
        assert state.stage_statuses["stage1"] == StageStatus.FAILED
        assert state.stage_statuses["stage2"] == StageStatus.SUCCESS  # Continues
    
    def test_checkpoint_and_resume(self):
        """Test checkpointing and resuming workflow"""
        with tempfile.TemporaryDirectory() as temp_dir:
            checkpoint_dir = Path(temp_dir)
            
            stages = [
                StageDefinition(id="stage1", script="s1.py"),
                StageDefinition(id="stage2", script="s2.py", depends_on=["stage1"]),
                StageDefinition(id="stage3", script="s3.py", depends_on=["stage2"]),
            ]
            
            workflow = WorkflowDefinition(
                workflow_id="wf-test",
                name="Test",
                description="Test",
                stages=stages
            )
            
            orchestrator = WorkflowOrchestrator(workflow, checkpoint_dir=checkpoint_dir)
            
            # Mock stage2 to fail
            orchestrator.register_stage("stage1", MockStage("stage1"))
            orchestrator.register_stage("stage2", MockStage("stage2", should_fail=True))
            orchestrator.register_stage("stage3", MockStage("stage3"))
            
            # Execute - should fail at stage2
            state = orchestrator.execute(
                user_request="Test request",
                conversation_id="conv-123"
            )
            
            workflow_id = state.workflow_id
            
            assert state.stage_statuses["stage1"] == StageStatus.SUCCESS
            assert state.stage_statuses["stage2"] == StageStatus.FAILED
            
            # Fix stage2 and resume
            orchestrator.register_stage("stage2", MockStage("stage2"))  # Now succeeds
            
            resumed_state = orchestrator.resume(workflow_id)
            
            assert resumed_state.stage_statuses["stage1"] == StageStatus.SUCCESS
            assert resumed_state.stage_statuses["stage2"] == StageStatus.SUCCESS
            assert resumed_state.stage_statuses["stage3"] == StageStatus.SUCCESS


class TestBaseWorkflowStage:
    """Tests for BaseWorkflowStage"""
    
    def test_base_stage_execute_not_implemented(self):
        """Test base stage execute raises NotImplementedError"""
        stage = BaseWorkflowStage("test-stage")
        state = WorkflowState(
            workflow_id="wf-001",
            conversation_id="conv-123",
            user_request="Test"
        )
        
        with pytest.raises(NotImplementedError):
            stage.execute(state)
    
    def test_base_stage_validate_input_default(self):
        """Test base stage validate_input returns True by default"""
        stage = BaseWorkflowStage("test-stage")
        state = WorkflowState(
            workflow_id="wf-001",
            conversation_id="conv-123",
            user_request="Test"
        )
        
        assert stage.validate_input(state) is True
    
    def test_base_stage_on_failure_default(self):
        """Test base stage on_failure doesn't raise error"""
        stage = BaseWorkflowStage("test-stage")
        state = WorkflowState(
            workflow_id="wf-001",
            conversation_id="conv-123",
            user_request="Test"
        )
        
        # Should not raise
        stage.on_failure(state, Exception("Test error"))
