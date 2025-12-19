"""
Tests for Base Orchestrator Framework

Validates:
- BaseOrchestrator initialization and lifecycle
- PhaseManager phase execution and transitions
- OrchestratorErrorHandler error handling and recovery
"""

import pytest
from datetime import datetime
from src.orchestrators.base import (
    BaseOrchestrator,
    OrchestratorResult,
    OrchestratorStatus,
    ValidationResult,
    ErrorResult,
    PhaseManager,
    PhaseResult,
    PhaseStatus,
    RecoveryStrategy,
    OrchestratorErrorHandler,
    OrchestratorError,
    PhaseError,
    ConfigurationError,
    ErrorSeverity,
    ErrorCategory
)


# ============================================================================
# Test Orchestrator Implementation
# ============================================================================

class TestOrchestrator(BaseOrchestrator):
    """Test orchestrator implementation."""
    
    def execute(self) -> OrchestratorResult:
        """Simple execute implementation."""
        return OrchestratorResult(
            status=OrchestratorStatus.COMPLETED,
            success=True,
            message="Test orchestrator completed"
        )


class FailingOrchestrator(BaseOrchestrator):
    """Orchestrator that fails."""
    
    def execute(self) -> OrchestratorResult:
        """Raise an exception."""
        raise ValueError("Test failure")


# ============================================================================
# BaseOrchestrator Tests
# ============================================================================

class TestBaseOrchestrator:
    """Tests for BaseOrchestrator class."""
    
    def test_initialization(self):
        """Test orchestrator initialization."""
        config = {
            "name": "TestOrch",
            "version": "1.0.0",
            "log_level": "DEBUG"
        }
        
        orch = TestOrchestrator(config)
        
        assert orch.name == "TestOrch"
        assert orch.version == "1.0.0"
        assert orch.status == OrchestratorStatus.NOT_STARTED
        assert orch.brain is not None  # Brain interface integrated ✅
        assert orch.template_manager is None  # Placeholder - will be implemented in Phase 1 item #4
    
    def test_execute_success(self):
        """Test successful orchestrator execution."""
        config = {"name": "TestOrch", "version": "1.0.0"}
        orch = TestOrchestrator(config)
        
        result = orch.run()
        
        assert result.success is True
        assert result.status == OrchestratorStatus.COMPLETED
        assert result.execution_time_seconds > 0
        assert orch.status == OrchestratorStatus.COMPLETED
    
    def test_execute_failure(self):
        """Test orchestrator execution with failure."""
        config = {"name": "FailOrch", "version": "1.0.0"}
        orch = FailingOrchestrator(config)
        
        result = orch.run()
        
        assert result.success is False
        assert result.status == OrchestratorStatus.FAILED
        assert "Test failure" in result.message
        assert len(result.errors) > 0
        assert orch.status == OrchestratorStatus.FAILED
    
    def test_validation_success(self):
        """Test input validation success."""
        config = {"name": "TestOrch", "version": "1.0.0"}
        orch = TestOrchestrator(config)
        
        result = orch.validate_input({})
        
        assert result.valid is True
        assert len(result.errors) == 0
    
    def test_validation_missing_fields(self):
        """Test validation with missing required fields."""
        config = {}  # Missing name and version
        orch = TestOrchestrator(config)
        
        result = orch.validate_input({})
        
        assert result.valid is False
        assert len(result.errors) == 2  # Missing name and version
    
    def test_error_handling(self):
        """Test error handling."""
        config = {"name": "TestOrch", "version": "1.0.0"}
        orch = TestOrchestrator(config)
        
        error = ValueError("Test error")
        result = orch.handle_error(error)
        
        assert result.handled is True
        assert result.error_type == "ValueError"
        assert "Test error" in result.error_message
        assert len(orch.errors) == 1
    
    def test_execution_time_tracking(self):
        """Test execution time tracking."""
        config = {"name": "TestOrch", "version": "1.0.0"}
        orch = TestOrchestrator(config)
        
        assert orch.get_execution_time() == 0.0
        
        orch.run()
        
        assert orch.get_execution_time() > 0.0


# ============================================================================
# PhaseManager Tests
# ============================================================================

class TestPhaseManager:
    """Tests for PhaseManager class."""
    
    def test_initialization(self):
        """Test phase manager initialization."""
        manager = PhaseManager()
        
        assert len(manager.phases) == 0
        assert manager.current_phase is None
        assert len(manager.phase_history) == 0
    
    def test_register_phase(self):
        """Test phase registration."""
        manager = PhaseManager()
        
        def test_phase():
            return PhaseResult(
                phase_name="test",
                status=PhaseStatus.COMPLETED,
                success=True,
                message="Test phase"
            )
        
        manager.register_phase("test", test_phase, required=True)
        
        assert "test" in manager.phases
        assert manager.phases["test"].required is True
    
    def test_execute_phase_success(self):
        """Test successful phase execution."""
        manager = PhaseManager()
        
        def test_phase():
            result = PhaseResult(
                phase_name="test",
                status=PhaseStatus.RUNNING,
                success=False,
                message="Running"
            )
            result.complete(success=True, message="Completed")
            return result
        
        manager.register_phase("test", test_phase)
        result = manager.execute_phase("test")
        
        assert result.success is True
        assert result.status == PhaseStatus.COMPLETED
        assert len(manager.phase_history) == 1
        assert manager.current_phase == "test"
    
    def test_execute_phase_with_dependencies(self):
        """Test phase execution with dependencies."""
        manager = PhaseManager()
        
        def phase1():
            result = PhaseResult("phase1", PhaseStatus.RUNNING, True, "Phase 1")
            result.complete(success=True)
            return result
        
        def phase2():
            result = PhaseResult("phase2", PhaseStatus.RUNNING, True, "Phase 2")
            result.complete(success=True)
            return result
        
        manager.register_phase("phase1", phase1)
        manager.register_phase("phase2", phase2, dependencies=["phase1"])
        
        # Try to execute phase2 without phase1 - should fail
        result = manager.execute_phase("phase2")
        assert result.success is False
        assert "Dependency" in result.message
        
        # Execute phase1 then phase2 - should succeed
        manager.execute_phase("phase1")
        result = manager.execute_phase("phase2")
        assert result.success is True
    
    def test_execute_all_phases(self):
        """Test executing all phases in order."""
        manager = PhaseManager()
        
        def phase1():
            result = PhaseResult("phase1", PhaseStatus.RUNNING, True, "Phase 1")
            result.complete(success=True)
            return result
        
        def phase2():
            result = PhaseResult("phase2", PhaseStatus.RUNNING, True, "Phase 2")
            result.complete(success=True)
            return result
        
        manager.register_phase("phase1", phase1)
        manager.register_phase("phase2", phase2)
        
        results = manager.execute_all()
        
        assert len(results) == 2
        assert all(r.success for r in results)
    
    def test_phase_retry(self):
        """Test phase retry logic."""
        manager = PhaseManager()
        
        attempts = []
        
        def failing_phase():
            attempts.append(1)
            result = PhaseResult("failing", PhaseStatus.RUNNING, True, "Failing")
            result.complete(success=False, message="Failed")
            return result
        
        manager.register_phase("failing", failing_phase, max_retries=2)
        result = manager.execute_phase("failing")
        
        assert result.success is False
        assert len(attempts) == 3  # Initial + 2 retries
    
    def test_get_phase_status(self):
        """Test getting phase status."""
        manager = PhaseManager()
        
        def test_phase():
            result = PhaseResult("test", PhaseStatus.RUNNING, True, "Test")
            result.complete(success=True)
            return result
        
        manager.register_phase("test", test_phase)
        
        assert manager.get_phase_status("test") is None
        
        manager.execute_phase("test")
        
        assert manager.get_phase_status("test") == PhaseStatus.COMPLETED
    
    def test_reset(self):
        """Test phase manager reset."""
        manager = PhaseManager()
        
        def test_phase():
            result = PhaseResult("test", PhaseStatus.RUNNING, True, "Test")
            result.complete(success=True)
            return result
        
        manager.register_phase("test", test_phase)
        manager.execute_phase("test")
        
        assert len(manager.phase_history) == 1
        assert manager.current_phase == "test"
        
        manager.reset()
        
        assert len(manager.phase_history) == 0
        assert manager.current_phase is None


# ============================================================================
# OrchestratorErrorHandler Tests
# ============================================================================

class TestOrchestratorErrorHandler:
    """Tests for OrchestratorErrorHandler class."""
    
    def test_initialization(self):
        """Test error handler initialization."""
        handler = OrchestratorErrorHandler("TestOrch")
        
        assert handler.orchestrator_name == "TestOrch"
        assert handler.max_retries == 3
        assert len(handler.errors) == 0
    
    def test_handle_exception(self):
        """Test exception handling."""
        handler = OrchestratorErrorHandler("TestOrch")
        
        exc = ValueError("Test error")
        error = handler.handle_exception(exc, phase_name="test_phase")
        
        assert error.error_type == "ValueError"
        assert "Test error" in error.error_message
        assert error.context.phase_name == "test_phase"
        assert len(handler.errors) == 1
    
    def test_error_severity_classification(self):
        """Test error severity classification."""
        handler = OrchestratorErrorHandler("TestOrch")
        
        # Configuration error - HIGH
        config_error = ConfigurationError("Missing config")
        error1 = handler.handle_exception(config_error)
        assert error1.severity == ErrorSeverity.HIGH
        
        # Phase error - MEDIUM
        phase_error = PhaseError("test_phase", "Failed")
        error2 = handler.handle_exception(phase_error)
        assert error2.severity == ErrorSeverity.MEDIUM
    
    def test_should_retry(self):
        """Test retry determination."""
        handler = OrchestratorErrorHandler("TestOrch", max_retries=2)
        
        exc = RuntimeError("Temporary error")
        error = handler.handle_exception(exc)
        
        # Should retry on first attempt
        assert handler.should_retry(error) is True
        
        # Increment retry count
        error.retry_count = 2
        assert handler.should_retry(error) is False
        
        # Critical errors should not retry
        critical_error = handler.handle_exception(SystemError("Critical"))
        assert handler.should_retry(critical_error) is False
    
    def test_recovery_strategy(self):
        """Test recovery strategy determination."""
        handler = OrchestratorErrorHandler("TestOrch")
        
        # Recoverable error - retry
        exc1 = RuntimeError("Temporary error")
        error1 = handler.handle_exception(exc1)
        assert handler.get_recovery_strategy(error1) == "retry"
        
        # Configuration error - manual
        exc2 = ConfigurationError("Missing config")
        error2 = handler.handle_exception(exc2)
        assert handler.get_recovery_strategy(error2) == "manual"
        
        # Critical error - abort
        exc3 = SystemError("Critical")
        error3 = handler.handle_exception(exc3)
        assert handler.get_recovery_strategy(error3) == "abort"
    
    def test_has_critical_errors(self):
        """Test critical error detection."""
        handler = OrchestratorErrorHandler("TestOrch")
        
        assert handler.has_critical_errors() is False
        
        handler.handle_exception(RuntimeError("Normal error"))
        assert handler.has_critical_errors() is False
        
        handler.handle_exception(SystemError("Critical error"))
        assert handler.has_critical_errors() is True
    
    def test_get_error_summary(self):
        """Test error summary generation."""
        handler = OrchestratorErrorHandler("TestOrch")
        
        handler.handle_exception(ValueError("Error 1"))
        handler.handle_exception(RuntimeError("Error 2"))
        handler.handle_exception(ConfigurationError("Error 3"))
        
        summary = handler.get_error_summary()
        
        assert summary["total_errors"] == 3
        assert summary["critical_errors"] is True  # ConfigurationError is HIGH
        assert len(summary["errors"]) == 3
    
    def test_clear_errors(self):
        """Test clearing error history."""
        handler = OrchestratorErrorHandler("TestOrch")
        
        handler.handle_exception(ValueError("Error"))
        assert len(handler.errors) == 1
        
        handler.clear_errors()
        assert len(handler.errors) == 0


# ============================================================================
# Integration Tests
# ============================================================================

class TestOrchestratorIntegration:
    """Integration tests for orchestrator framework."""
    
    def test_orchestrator_with_phases(self):
        """Test orchestrator using phase manager."""
        
        class PhaseOrchestrator(BaseOrchestrator):
            def execute(self) -> OrchestratorResult:
                manager = PhaseManager()
                
                def phase1():
                    result = PhaseResult("phase1", PhaseStatus.RUNNING, True, "Phase 1")
                    result.complete(success=True)
                    return result
                
                def phase2():
                    result = PhaseResult("phase2", PhaseStatus.RUNNING, True, "Phase 2")
                    result.complete(success=True)
                    return result
                
                manager.register_phase("phase1", phase1)
                manager.register_phase("phase2", phase2)
                
                results = manager.execute_all()
                
                return OrchestratorResult(
                    status=OrchestratorStatus.COMPLETED,
                    success=all(r.success for r in results),
                    message=f"Completed {len(results)} phases"
                )
        
        config = {"name": "PhaseOrch", "version": "1.0.0"}
        orch = PhaseOrchestrator(config)
        result = orch.run()
        
        assert result.success is True
        assert "2 phases" in result.message
    
    def test_orchestrator_with_error_handler(self):
        """Test orchestrator using error handler."""
        
        class ErrorHandlingOrchestrator(BaseOrchestrator):
            def __init__(self, config):
                super().__init__(config)
                self.error_handler = OrchestratorErrorHandler(self.name)
            
            def execute(self) -> OrchestratorResult:
                try:
                    raise ValueError("Intentional error")
                except Exception as e:
                    error = self.error_handler.handle_exception(e)
                    
                    return OrchestratorResult(
                        status=OrchestratorStatus.FAILED,
                        success=False,
                        message="Handled error",
                        errors=[error.error_message]
                    )
        
        config = {"name": "ErrorOrch", "version": "1.0.0"}
        orch = ErrorHandlingOrchestrator(config)
        result = orch.run()
        
        assert result.success is False
        assert len(result.errors) > 0
        assert len(orch.error_handler.errors) == 1
