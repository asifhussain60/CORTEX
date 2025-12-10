"""
Unit tests for BaseOrchestrator
Tests DoR/DoD validation, workflow execution, error handling
"""

import pytest
from unittest.mock import Mock
from orchestration_3_0.core.base_orchestrator import (
    BaseOrchestrator,
    OrchestratorResult,
    ValidationResult,
    WorkflowContext
)
from orchestration_3_0.core.state_machine import create_basic_orchestrator_fsm


class MockOrchestrator(BaseOrchestrator):
    """Mock orchestrator for testing."""
    
    def __init__(self, fsm, session_manager, container):
        super().__init__("MockOrchestrator", fsm, session_manager, container)
        self.dor_should_pass = True
        self.dod_should_pass = True
        self.workflow_should_succeed = True
        self.workflow_outputs = {"result": "success"}
    
    def validate_dor(self, context: WorkflowContext) -> ValidationResult:
        """Mock DoR validation."""
        if self.dor_should_pass:
            return ValidationResult(passed=True, errors=[], warnings=[])
        else:
            return ValidationResult(
                passed=False,
                errors=["DoR validation failed"],
                warnings=["Missing prerequisite"]
            )
    
    def validate_dod(self, context: WorkflowContext) -> ValidationResult:
        """Mock DoD validation."""
        if self.dod_should_pass:
            return ValidationResult(passed=True, errors=[], warnings=[])
        else:
            return ValidationResult(
                passed=False,
                errors=["DoD validation failed"],
                warnings=["Incomplete output"]
            )
    
    def execute_workflow(self, context: WorkflowContext) -> dict:
        """Mock workflow execution."""
        if not self.workflow_should_succeed:
            raise RuntimeError("Workflow execution failed")
        return self.workflow_outputs


class TestBaseOrchestrator:
    """Test BaseOrchestrator core functionality."""
    
    def test_successful_execution(self, basic_fsm, fresh_session_manager, fresh_container):
        """Test successful orchestrator execution (DoR → Execute → DoD)."""
        orchestrator = MockOrchestrator(basic_fsm, fresh_session_manager, fresh_container)
        
        result = orchestrator.execute(
            tenant_id="tenant-1",
            project_id="proj-1",
            user_id="user-1",
            inputs={"feature": "authentication"}
        )
        
        assert result.success is True
        assert result.orchestrator_name == "MockOrchestrator"
        assert result.final_state == "COMPLETED"
        assert result.outputs["result"] == "success"
        assert len(result.errors) == 0
    
    def test_dor_validation_failure(self, basic_fsm, fresh_session_manager, fresh_container):
        """Test execution fails when DoR validation fails."""
        orchestrator = MockOrchestrator(basic_fsm, fresh_session_manager, fresh_container)
        orchestrator.dor_should_pass = False
        
        result = orchestrator.execute(
            tenant_id="tenant-1",
            project_id="proj-1",
            user_id="user-1",
            inputs={"feature": "authentication"}
        )
        
        assert result.success is False
        assert result.final_state == "FAILED"
        assert "DoR validation failed" in result.errors
    
    def test_dod_validation_failure(self, basic_fsm, fresh_session_manager, fresh_container):
        """Test execution fails when DoD validation fails."""
        orchestrator = MockOrchestrator(basic_fsm, fresh_session_manager, fresh_container)
        orchestrator.dod_should_pass = False
        
        result = orchestrator.execute(
            tenant_id="tenant-1",
            project_id="proj-1",
            user_id="user-1",
            inputs={"feature": "authentication"}
        )
        
        assert result.success is False
        assert result.final_state == "FAILED"
        assert "DoD validation failed" in result.errors
    
    def test_workflow_execution_exception(self, basic_fsm, fresh_session_manager, fresh_container):
        """Test execution handles workflow exceptions."""
        orchestrator = MockOrchestrator(basic_fsm, fresh_session_manager, fresh_container)
        orchestrator.workflow_should_succeed = False
        
        result = orchestrator.execute(
            tenant_id="tenant-1",
            project_id="proj-1",
            user_id="user-1",
            inputs={"feature": "authentication"}
        )
        
        assert result.success is False
        assert result.final_state == "FAILED"
        assert any("Workflow execution failed" in err for err in result.errors)
    
    def test_session_creation(self, basic_fsm, fresh_session_manager, fresh_container):
        """Test session is created for orchestrator execution."""
        orchestrator = MockOrchestrator(basic_fsm, fresh_session_manager, fresh_container)
        
        result = orchestrator.execute(
            tenant_id="tenant-1",
            project_id="proj-1",
            user_id="user-1",
            inputs={"feature": "authentication"}
        )
        
        # Verify session exists
        session = fresh_session_manager.get_session(result.session_id)
        assert session is not None
        assert session.orchestrator_name == "MockOrchestrator"
        assert session.tenant_id == "tenant-1"
    
    def test_session_completion(self, basic_fsm, fresh_session_manager, fresh_container):
        """Test session is marked completed on success."""
        orchestrator = MockOrchestrator(basic_fsm, fresh_session_manager, fresh_container)
        
        result = orchestrator.execute(
            tenant_id="tenant-1",
            project_id="proj-1",
            user_id="user-1",
            inputs={"feature": "authentication"}
        )
        
        session = fresh_session_manager.get_session(result.session_id)
        assert session.status.value == "COMPLETED"
    
    def test_session_failure(self, basic_fsm, fresh_session_manager, fresh_container):
        """Test session is marked failed on error."""
        orchestrator = MockOrchestrator(basic_fsm, fresh_session_manager, fresh_container)
        orchestrator.workflow_should_succeed = False
        
        result = orchestrator.execute(
            tenant_id="tenant-1",
            project_id="proj-1",
            user_id="user-1",
            inputs={"feature": "authentication"}
        )
        
        session = fresh_session_manager.get_session(result.session_id)
        assert session.status.value == "FAILED"
    
    def test_execution_timing(self, basic_fsm, fresh_session_manager, fresh_container):
        """Test execution time is recorded."""
        orchestrator = MockOrchestrator(basic_fsm, fresh_session_manager, fresh_container)
        
        result = orchestrator.execute(
            tenant_id="tenant-1",
            project_id="proj-1",
            user_id="user-1",
            inputs={"feature": "authentication"}
        )
        
        assert result.execution_time_seconds > 0
        assert result.execution_time_seconds < 1.0  # Should be very fast for mock


class TestWorkflowContext:
    """Test WorkflowContext data structure."""
    
    def test_context_creation(self):
        """Test creating workflow context."""
        context = WorkflowContext(
            tenant_id="tenant-1",
            project_id="proj-1",
            user_id="user-1",
            inputs={"feature": "authentication"}
        )
        
        assert context.tenant_id == "tenant-1"
        assert context.project_id == "proj-1"
        assert context.user_id == "user-1"
        assert context.inputs["feature"] == "authentication"
        assert context.outputs == {}
    
    def test_context_with_outputs(self):
        """Test context with outputs."""
        context = WorkflowContext(
            tenant_id="tenant-1",
            project_id="proj-1",
            user_id="user-1",
            inputs={"feature": "authentication"},
            outputs={"implementation": "def login(): pass"}
        )
        
        assert context.outputs["implementation"] == "def login(): pass"


class TestValidationResult:
    """Test ValidationResult data structure."""
    
    def test_validation_passed(self):
        """Test validation result for passed validation."""
        result = ValidationResult(passed=True, errors=[], warnings=[])
        
        assert result.passed is True
        assert len(result.errors) == 0
        assert len(result.warnings) == 0
    
    def test_validation_failed_with_errors(self):
        """Test validation result with errors."""
        result = ValidationResult(
            passed=False,
            errors=["Missing prerequisite", "Invalid input"],
            warnings=["Consider using X"]
        )
        
        assert result.passed is False
        assert len(result.errors) == 2
        assert len(result.warnings) == 1


class TestOrchestratorResult:
    """Test OrchestratorResult data structure."""
    
    def test_successful_result(self):
        """Test successful orchestrator result."""
        result = OrchestratorResult(
            success=True,
            session_id="session-123",
            orchestrator_name="TestOrch",
            final_state="COMPLETED",
            execution_time_seconds=1.5,
            outputs={"result": "success"},
            errors=[]
        )
        
        assert result.success is True
        assert result.final_state == "COMPLETED"
        assert result.outputs["result"] == "success"
        assert len(result.errors) == 0
    
    def test_failed_result(self):
        """Test failed orchestrator result."""
        result = OrchestratorResult(
            success=False,
            session_id="session-123",
            orchestrator_name="TestOrch",
            final_state="FAILED",
            execution_time_seconds=0.5,
            outputs={},
            errors=["DoR validation failed", "Missing API key"]
        )
        
        assert result.success is False
        assert result.final_state == "FAILED"
        assert len(result.errors) == 2


class TestStateTransitions:
    """Test state transitions during execution."""
    
    def test_state_progression_successful(self, basic_fsm, fresh_session_manager, fresh_container):
        """Test state progresses through all phases on success."""
        orchestrator = MockOrchestrator(basic_fsm, fresh_session_manager, fresh_container)
        
        result = orchestrator.execute(
            tenant_id="tenant-1",
            project_id="proj-1",
            user_id="user-1",
            inputs={"feature": "authentication"}
        )
        
        # Check FSM state progression
        assert basic_fsm.current_state == "COMPLETED"
        
        # Check history
        states = [entry.state for entry in basic_fsm.history]
        assert "INITIALIZED" in states
        assert "VALIDATING_DOR" in states
        assert "EXECUTING" in states
        assert "VALIDATING_DOD" in states
        assert "COMPLETED" in states
    
    def test_state_progression_dor_failure(self, basic_fsm, fresh_session_manager, fresh_container):
        """Test state stops at DoR validation on failure."""
        orchestrator = MockOrchestrator(basic_fsm, fresh_session_manager, fresh_container)
        orchestrator.dor_should_pass = False
        
        result = orchestrator.execute(
            tenant_id="tenant-1",
            project_id="proj-1",
            user_id="user-1",
            inputs={"feature": "authentication"}
        )
        
        assert basic_fsm.current_state == "FAILED"
        
        # Should not reach EXECUTING
        states = [entry.state for entry in basic_fsm.history]
        assert "VALIDATING_DOR" in states
        assert "EXECUTING" not in states


class TestDependencyInjection:
    """Test dependency injection with BaseOrchestrator."""
    
    def test_container_injection(self, basic_fsm, fresh_session_manager, fresh_container):
        """Test orchestrator receives DI container."""
        orchestrator = MockOrchestrator(basic_fsm, fresh_session_manager, fresh_container)
        
        assert orchestrator.container is fresh_container
    
    def test_session_manager_injection(self, basic_fsm, fresh_session_manager, fresh_container):
        """Test orchestrator receives session manager."""
        orchestrator = MockOrchestrator(basic_fsm, fresh_session_manager, fresh_container)
        
        assert orchestrator.session_manager is fresh_session_manager
    
    def test_fsm_injection(self, basic_fsm, fresh_session_manager, fresh_container):
        """Test orchestrator receives FSM."""
        orchestrator = MockOrchestrator(basic_fsm, fresh_session_manager, fresh_container)
        
        assert orchestrator.fsm is basic_fsm


class TestErrorHandling:
    """Test error handling in BaseOrchestrator."""
    
    def test_dor_exception_handling(self, basic_fsm, fresh_session_manager, fresh_container):
        """Test DoR validation exception is caught."""
        class FailingDorOrchestrator(MockOrchestrator):
            def validate_dor(self, context):
                raise ValueError("DoR crashed")
        
        orchestrator = FailingDorOrchestrator(basic_fsm, fresh_session_manager, fresh_container)
        
        result = orchestrator.execute(
            tenant_id="tenant-1",
            project_id="proj-1",
            user_id="user-1",
            inputs={}
        )
        
        assert result.success is False
        assert any("DoR crashed" in err for err in result.errors)
    
    def test_dod_exception_handling(self, basic_fsm, fresh_session_manager, fresh_container):
        """Test DoD validation exception is caught."""
        class FailingDodOrchestrator(MockOrchestrator):
            def validate_dod(self, context):
                raise ValueError("DoD crashed")
        
        orchestrator = FailingDodOrchestrator(basic_fsm, fresh_session_manager, fresh_container)
        
        result = orchestrator.execute(
            tenant_id="tenant-1",
            project_id="proj-1",
            user_id="user-1",
            inputs={}
        )
        
        assert result.success is False
        assert any("DoD crashed" in err for err in result.errors)


class TestMultiTenant:
    """Test multi-tenant functionality."""
    
    def test_different_tenants_isolated(self, basic_fsm, fresh_session_manager, fresh_container):
        """Test different tenants have isolated sessions."""
        orchestrator = MockOrchestrator(basic_fsm, fresh_session_manager, fresh_container)
        
        result1 = orchestrator.execute(
            tenant_id="tenant-1",
            project_id="proj-1",
            user_id="user-1",
            inputs={}
        )
        
        # Reset FSM for second execution
        orchestrator.fsm = create_basic_orchestrator_fsm("MockOrchestrator")
        
        result2 = orchestrator.execute(
            tenant_id="tenant-2",
            project_id="proj-2",
            user_id="user-2",
            inputs={}
        )
        
        session1 = fresh_session_manager.get_session(result1.session_id)
        session2 = fresh_session_manager.get_session(result2.session_id)
        
        assert session1.tenant_id == "tenant-1"
        assert session2.tenant_id == "tenant-2"
        assert session1.session_id != session2.session_id
