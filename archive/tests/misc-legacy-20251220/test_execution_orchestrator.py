"""
Unit tests for ExecutionOrchestrator (CORTEX 4.0)

Tests execution orchestrator functionality including phase execution,
sub-orchestrator routing, and error handling.
"""

import pytest
import logging
from src.orchestration_4_0.orchestrators.execution import ExecutionOrchestrator
from src.orchestration_4_0.base.phase_manager import PhaseStatus
from src.orchestration_4_0.base.error_handler import ErrorSeverity


@pytest.fixture
def simple_plan():
    """Simple execution plan with 2 phases"""
    return {
        "name": "simple_test",
        "phases": [
            {"name": "setup", "description": "Setup phase", "required": True},
            {"name": "execute", "description": "Execute phase", "required": True}
        ]
    }


@pytest.fixture
def complex_plan():
    """Complex execution plan with multiple phase types"""
    return {
        "name": "complex_test",
        "phases": [
            {
                "name": "prepare",
                "description": "Preparation phase",
                "required": True
            },
            {
                "name": "inline_code",
                "description": "Execute inline code",
                "code": "print('Hello World')",
                "required": True
            },
            {
                "name": "sub_orchestrator",
                "description": "Run sub-orchestrator",
                "orchestrator": "tdd",
                "required": True
            },
            {
                "name": "custom_handler",
                "description": "Custom handler",
                "handler": "custom_function",
                "required": False
            }
        ]
    }


@pytest.fixture
def orchestrator():
    """Create ExecutionOrchestrator instance"""
    logger = logging.getLogger("test")
    return ExecutionOrchestrator(logger=logger, config={"max_retries": 2})


class TestOrchestratorInitialization:
    """Test orchestrator initialization"""
    
    def test_init_default(self):
        """Test default initialization"""
        orch = ExecutionOrchestrator()
        
        assert orch.name == "execution"
        assert orch.logger is not None
        assert orch.phase_manager is not None
        assert orch.error_handler is not None
        assert orch.is_running is False
        assert orch.is_complete is False
    
    def test_init_with_config(self):
        """Test initialization with config"""
        config = {"max_retries": 5, "custom": "value"}
        orch = ExecutionOrchestrator(config=config)
        
        assert orch.config == config
        assert orch.error_handler.max_retries == 5


class TestSetupPhase:
    """Test orchestrator setup"""
    
    def test_setup_with_plan(self, orchestrator, simple_plan):
        """Test setup with valid plan"""
        context = {"plan": simple_plan}
        orchestrator._setup(context)
        
        assert orchestrator.execution_plan == simple_plan
        assert orchestrator.workspace is None
    
    def test_setup_with_workspace(self, orchestrator, simple_plan):
        """Test setup with workspace path"""
        context = {
            "plan": simple_plan,
            "workspace": "/path/to/workspace"
        }
        orchestrator._setup(context)
        
        assert orchestrator.workspace == "/path/to/workspace"
    
    def test_setup_with_validators(self, orchestrator, simple_plan):
        """Test setup with phase validators"""
        def validate():
            return True
        
        context = {
            "plan": simple_plan,
            "validators": {"setup_validator": validate}
        }
        orchestrator._setup(context)
        
        assert "setup_validator" in orchestrator.phase_validators
    
    def test_setup_without_plan_fails(self, orchestrator):
        """Test that setup fails without plan"""
        context = {}
        
        with pytest.raises(ValueError, match="must contain 'plan'"):
            orchestrator._setup(context)


class TestPhaseRegistration:
    """Test phase registration from execution plan"""
    
    def test_register_phases_simple(self, orchestrator, simple_plan):
        """Test registering phases from simple plan"""
        orchestrator._setup({"plan": simple_plan})
        orchestrator._register_phases()
        
        assert len(orchestrator.phase_manager.phases) == 2
        assert orchestrator.phase_manager.phases[0].name == "setup"
        assert orchestrator.phase_manager.phases[1].name == "execute"
    
    def test_register_phases_with_properties(self, orchestrator):
        """Test phase registration with all properties"""
        plan = {
            "name": "test",
            "phases": [
                {
                    "name": "optional",
                    "description": "Optional phase",
                    "required": False
                }
            ]
        }
        
        orchestrator._setup({"plan": plan})
        orchestrator._register_phases()
        
        phase = orchestrator.phase_manager.phases[0]
        assert phase.name == "optional"
        assert phase.description == "Optional phase"
        assert phase.required is False
    
    def test_register_phases_empty_plan_fails(self, orchestrator):
        """Test that empty phase list fails"""
        plan = {"name": "test", "phases": []}
        orchestrator._setup({"plan": plan})
        
        with pytest.raises(ValueError, match="at least one phase"):
            orchestrator._register_phases()
    
    def test_register_phases_invalid_phase_fails(self, orchestrator):
        """Test that phase without name fails"""
        plan = {
            "name": "test",
            "phases": [{"description": "Missing name"}]
        }
        orchestrator._setup({"plan": plan})
        
        with pytest.raises(ValueError, match="must contain 'name'"):
            orchestrator._register_phases()


class TestPhaseExecution:
    """Test phase execution"""
    
    def test_execute_simple_phase(self, orchestrator, simple_plan):
        """Test executing a simple phase"""
        orchestrator._setup({"plan": simple_plan})
        orchestrator._register_phases()
        
        result = orchestrator._execute_phase("setup", {})
        
        assert result is not None
        assert result["status"] == "completed"
    
    def test_execute_inline_code_phase(self, orchestrator):
        """Test executing phase with inline code"""
        plan = {
            "name": "test",
            "phases": [
                {
                    "name": "code_phase",
                    "code": "x = 1 + 1"
                }
            ]
        }
        
        orchestrator._setup({"plan": plan})
        orchestrator._register_phases()
        
        result = orchestrator._execute_phase("code_phase", {})
        
        assert result["status"] == "completed"
        assert "Inline code executed" in result["message"]
    
    def test_execute_sub_orchestrator_phase(self, orchestrator):
        """Test executing phase with sub-orchestrator"""
        plan = {
            "name": "test",
            "phases": [
                {
                    "name": "sub_orch_phase",
                    "orchestrator": "tdd"
                }
            ]
        }
        
        orchestrator._setup({"plan": plan})
        orchestrator._register_phases()
        
        result = orchestrator._execute_phase("sub_orch_phase", {})
        
        # Should skip since sub-orchestrator not implemented
        assert result["status"] == "skipped"
    
    def test_execute_custom_handler_phase(self, orchestrator):
        """Test executing phase with custom handler"""
        plan = {
            "name": "test",
            "phases": [
                {
                    "name": "handler_phase",
                    "handler": "custom_func"
                }
            ]
        }
        
        orchestrator._setup({"plan": plan})
        orchestrator._register_phases()
        
        result = orchestrator._execute_phase("handler_phase", {})
        
        assert result["status"] == "completed"
        assert "custom_func" in result["message"]


class TestFullWorkflow:
    """Test full orchestrator execution workflow"""
    
    def test_execute_simple_workflow(self, orchestrator, simple_plan):
        """Test executing complete simple workflow"""
        context = {"plan": simple_plan}
        
        result = orchestrator.execute(context)
        
        assert result is not None
        assert orchestrator.is_running is False
        assert result["orchestrator"] == "execution"
        assert result["progress"]["completed"] == 2
        assert result["progress"]["total_phases"] == 2
        assert result["is_complete"] is True
    
    def test_execute_complex_workflow(self, orchestrator, complex_plan):
        """Test executing complex workflow"""
        context = {"plan": complex_plan}
        
        result = orchestrator.execute(context)
        
        assert result["progress"]["total_phases"] == 4
        # Most phases should complete (sub-orchestrator might skip)
        assert result["progress"]["completed"] >= 3
    
    def test_execute_prevents_concurrent_runs(self, orchestrator, simple_plan):
        """Test that concurrent execution is prevented"""
        orchestrator.is_running = True
        
        with pytest.raises(RuntimeError, match="already running"):
            orchestrator.execute({"plan": simple_plan})
    
    def test_execute_records_timing(self, orchestrator, simple_plan):
        """Test that execution timing is recorded"""
        result = orchestrator.execute({"plan": simple_plan})
        
        assert orchestrator.started_at is not None
        assert orchestrator.completed_at is not None
        assert result["duration_seconds"] > 0


class TestSubOrchestratorManagement:
    """Test sub-orchestrator registration and management"""
    
    def test_register_sub_orchestrator(self, orchestrator):
        """Test registering a sub-orchestrator"""
        class MockSubOrchestrator:
            def execute(self, context):
                return {"status": "success"}
        
        sub_orch = MockSubOrchestrator()
        orchestrator.register_sub_orchestrator("mock", sub_orch)
        
        assert "mock" in orchestrator.sub_orchestrators
        assert orchestrator.sub_orchestrators["mock"] == sub_orch
    
    def test_register_validator(self, orchestrator):
        """Test registering a phase validator"""
        def validator():
            return True
        
        orchestrator.register_validator("test_validator", validator)
        
        assert "test_validator" in orchestrator.phase_validators
        assert orchestrator.phase_validators["test_validator"]() is True


class TestErrorHandling:
    """Test error handling in orchestrator"""
    
    def test_execution_with_phase_failure(self, orchestrator):
        """Test handling phase failure"""
        plan = {
            "name": "test",
            "phases": [
                {"name": "will_fail", "description": "This will fail"}
            ]
        }
        
        # Mock phase execution to fail
        original_execute = orchestrator._execute_phase
        
        def failing_execute(phase_name, context):
            if phase_name == "will_fail":
                raise ValueError("Simulated failure")
            return original_execute(phase_name, context)
        
        orchestrator._execute_phase = failing_execute
        
        # Should handle error and continue
        with pytest.raises(ValueError):
            orchestrator.execute({"plan": plan})
        
        # Error should be recorded
        assert len(orchestrator.error_handler.errors) > 0


class TestTeardown:
    """Test orchestrator teardown"""
    
    def test_teardown_cleanup(self, orchestrator, simple_plan):
        """Test that teardown cleans up resources"""
        # Register mock sub-orchestrator with cleanup
        class MockSubOrchestrator:
            def __init__(self):
                self.cleaned_up = False
            
            def cleanup(self):
                self.cleaned_up = True
        
        sub_orch = MockSubOrchestrator()
        orchestrator.register_sub_orchestrator("mock", sub_orch)
        
        # Execute and teardown
        orchestrator.execute({"plan": simple_plan})
        
        # Sub-orchestrator should be cleaned up
        assert sub_orch.cleaned_up is True
        assert len(orchestrator.sub_orchestrators) == 0


class TestGetStatus:
    """Test status retrieval"""
    
    def test_get_status_before_execution(self, orchestrator):
        """Test status before execution"""
        status = orchestrator.get_status()
        
        assert status["name"] == "execution"
        assert status["is_running"] is False
        assert status["is_complete"] is False
        assert status["started_at"] is None
    
    def test_get_status_during_execution(self, orchestrator, simple_plan):
        """Test status during execution"""
        # This would require async execution to properly test
        # For now, just test the status structure
        orchestrator.is_running = True
        orchestrator.started_at = orchestrator.phase_manager.phases[0].started_at if orchestrator.phase_manager.phases else None
        
        status = orchestrator.get_status()
        
        assert status["is_running"] is True
    
    def test_get_status_after_execution(self, orchestrator, simple_plan):
        """Test status after execution"""
        orchestrator.execute({"plan": simple_plan})
        
        status = orchestrator.get_status()
        
        assert status["is_running"] is False
        assert status["is_complete"] is True
        assert status["started_at"] is not None
