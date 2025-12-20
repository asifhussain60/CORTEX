"""
Unit tests for ErrorHandler (CORTEX 4.0)

Tests error handling, recovery strategies, and retry logic.
"""

import pytest
from src.orchestration_4_0.base.error_handler import (
    ErrorHandler,
    OrchestratorError,
    ErrorSeverity,
    RecoveryStrategy
)


class TestErrorHandling:
    """Test basic error handling functionality"""
    
    def test_handle_simple_error(self):
        """Test handling a simple error"""
        handler = ErrorHandler("test_orchestrator")
        
        error = handler.handle_error(
            phase="setup",
            exception=ValueError("Test error")
        )
        
        assert error.phase == "setup"
        assert error.severity == ErrorSeverity.ERROR
        assert error.message == "Test error"
        assert error.exception is not None
        assert error.traceback is not None
        assert len(handler.errors) == 1
    
    def test_handle_error_with_severity(self):
        """Test handling error with specific severity"""
        handler = ErrorHandler("test_orchestrator")
        
        error = handler.handle_error(
            phase="critical_phase",
            exception=RuntimeError("Critical failure"),
            severity=ErrorSeverity.CRITICAL
        )
        
        assert error.severity == ErrorSeverity.CRITICAL
    
    def test_handle_error_with_context(self):
        """Test handling error with context data"""
        handler = ErrorHandler("test_orchestrator")
        
        context = {"attempt": 2, "user": "test"}
        error = handler.handle_error(
            phase="retry_phase",
            exception=ConnectionError("Connection failed"),
            context=context
        )
        
        assert error.context == context
    
    def test_handle_error_with_recovery_strategy(self):
        """Test handling error with explicit recovery strategy"""
        handler = ErrorHandler("test_orchestrator")
        
        error = handler.handle_error(
            phase="skippable",
            exception=FileNotFoundError("File not found"),
            recovery_strategy=RecoveryStrategy.SKIP
        )
        
        assert error.recovery_strategy == RecoveryStrategy.SKIP


class TestRecoveryStrategies:
    """Test automatic recovery strategy determination"""
    
    def test_critical_error_fails_fast(self):
        """Test that critical errors always fail fast"""
        handler = ErrorHandler("test_orchestrator")
        
        error = handler.handle_error(
            phase="critical",
            exception=RuntimeError("Critical error"),
            severity=ErrorSeverity.CRITICAL
        )
        
        assert error.recovery_strategy == RecoveryStrategy.FAIL_FAST
    
    def test_connection_error_retries(self):
        """Test that connection errors retry by default"""
        handler = ErrorHandler("test_orchestrator")
        
        error = handler.handle_error(
            phase="network",
            exception=ConnectionError("Connection failed")
        )
        
        assert error.recovery_strategy == RecoveryStrategy.RETRY
    
    def test_timeout_error_retries(self):
        """Test that timeout errors retry by default"""
        handler = ErrorHandler("test_orchestrator")
        
        error = handler.handle_error(
            phase="slow_operation",
            exception=TimeoutError("Operation timed out")
        )
        
        assert error.recovery_strategy == RecoveryStrategy.RETRY
    
    def test_file_not_found_skips(self):
        """Test that file not found errors can be skipped"""
        handler = ErrorHandler("test_orchestrator")
        
        error = handler.handle_error(
            phase="file_operation",
            exception=FileNotFoundError("File not found")
        )
        
        assert error.recovery_strategy == RecoveryStrategy.SKIP
    
    def test_permission_error_requires_user(self):
        """Test that permission errors require user intervention"""
        handler = ErrorHandler("test_orchestrator")
        
        error = handler.handle_error(
            phase="restricted",
            exception=PermissionError("Permission denied")
        )
        
        assert error.recovery_strategy == RecoveryStrategy.USER_INTERVENTION
    
    def test_value_error_fails_fast(self):
        """Test that value errors fail fast"""
        handler = ErrorHandler("test_orchestrator")
        
        error = handler.handle_error(
            phase="validation",
            exception=ValueError("Invalid value")
        )
        
        assert error.recovery_strategy == RecoveryStrategy.FAIL_FAST
    
    def test_warning_continues(self):
        """Test that warnings continue by default"""
        handler = ErrorHandler("test_orchestrator")
        
        error = handler.handle_error(
            phase="optional",
            exception=RuntimeError("Minor issue"),
            severity=ErrorSeverity.WARNING
        )
        
        assert error.recovery_strategy == RecoveryStrategy.CONTINUE


class TestRetryLogic:
    """Test retry counting and limits"""
    
    def test_can_retry_initial(self):
        """Test that phase can be retried initially"""
        handler = ErrorHandler("test_orchestrator", max_retries=3)
        
        assert handler.can_retry("phase1") is True
    
    def test_record_retry(self):
        """Test recording retry attempts"""
        handler = ErrorHandler("test_orchestrator", max_retries=3)
        
        count = handler.record_retry("phase1")
        assert count == 1
        assert handler.retry_counts["phase1"] == 1
    
    def test_max_retries_reached(self):
        """Test that max retries limit is enforced"""
        handler = ErrorHandler("test_orchestrator", max_retries=3)
        
        handler.record_retry("phase1")
        handler.record_retry("phase1")
        handler.record_retry("phase1")
        
        assert handler.can_retry("phase1") is False
    
    def test_reset_retries(self):
        """Test resetting retry counter"""
        handler = ErrorHandler("test_orchestrator", max_retries=3)
        
        handler.record_retry("phase1")
        handler.record_retry("phase1")
        handler.reset_retries("phase1")
        
        assert handler.can_retry("phase1") is True
        assert "phase1" not in handler.retry_counts
    
    def test_retry_separate_phases(self):
        """Test that retry counts are per-phase"""
        handler = ErrorHandler("test_orchestrator", max_retries=2)
        
        handler.record_retry("phase1")
        handler.record_retry("phase1")
        handler.record_retry("phase2")
        
        assert handler.can_retry("phase1") is False
        assert handler.can_retry("phase2") is True


class TestErrorSummary:
    """Test error summary and statistics"""
    
    def test_get_error_summary_empty(self):
        """Test error summary with no errors"""
        handler = ErrorHandler("test_orchestrator")
        
        summary = handler.get_error_summary()
        
        assert summary["total_errors"] == 0
        assert summary["by_severity"] == {}
        assert summary["by_phase"] == {}
        assert summary["critical_errors"] == []
    
    def test_get_error_summary_single_error(self):
        """Test error summary with one error"""
        handler = ErrorHandler("test_orchestrator")
        
        handler.handle_error(
            phase="setup",
            exception=ValueError("Test error"),
            severity=ErrorSeverity.ERROR
        )
        
        summary = handler.get_error_summary()
        
        assert summary["total_errors"] == 1
        assert summary["by_severity"]["error"] == 1
        assert summary["by_phase"]["setup"] == 1
    
    def test_get_error_summary_multiple_errors(self):
        """Test error summary with multiple errors"""
        handler = ErrorHandler("test_orchestrator")
        
        handler.handle_error("phase1", ValueError("Error 1"), ErrorSeverity.ERROR)
        handler.handle_error("phase1", RuntimeError("Error 2"), ErrorSeverity.WARNING)
        handler.handle_error("phase2", ConnectionError("Error 3"), ErrorSeverity.ERROR)
        
        summary = handler.get_error_summary()
        
        assert summary["total_errors"] == 3
        assert summary["by_severity"]["error"] == 2
        assert summary["by_severity"]["warning"] == 1
        assert summary["by_phase"]["phase1"] == 2
        assert summary["by_phase"]["phase2"] == 1
    
    def test_get_error_summary_critical_tracking(self):
        """Test that critical errors are tracked separately"""
        handler = ErrorHandler("test_orchestrator")
        
        handler.handle_error(
            phase="critical_phase",
            exception=RuntimeError("Critical failure"),
            severity=ErrorSeverity.CRITICAL
        )
        
        summary = handler.get_error_summary()
        
        assert len(summary["critical_errors"]) == 1
        critical = summary["critical_errors"][0]
        assert critical["phase"] == "critical_phase"
        assert critical["message"] == "Critical failure"
    
    def test_has_critical_errors(self):
        """Test checking for critical errors"""
        handler = ErrorHandler("test_orchestrator")
        
        assert handler.has_critical_errors() is False
        
        handler.handle_error("phase1", ValueError("Error"), ErrorSeverity.ERROR)
        assert handler.has_critical_errors() is False
        
        handler.handle_error("phase2", RuntimeError("Critical"), ErrorSeverity.CRITICAL)
        assert handler.has_critical_errors() is True


class TestErrorCleanup:
    """Test error history cleanup"""
    
    def test_clear_errors(self):
        """Test clearing error history"""
        handler = ErrorHandler("test_orchestrator")
        
        handler.handle_error("phase1", ValueError("Error 1"))
        handler.handle_error("phase2", ValueError("Error 2"))
        handler.record_retry("phase1")
        
        assert len(handler.errors) == 2
        assert len(handler.retry_counts) == 1
        
        handler.clear_errors()
        
        assert len(handler.errors) == 0
        assert len(handler.retry_counts) == 0


class TestOrchestratorError:
    """Test OrchestratorError dataclass"""
    
    def test_orchestrator_error_creation(self):
        """Test creating OrchestratorError"""
        exception = ValueError("Test error")
        
        error = OrchestratorError(
            phase="test_phase",
            severity=ErrorSeverity.ERROR,
            message="Test message",
            exception=exception,
            recovery_strategy=RecoveryStrategy.RETRY
        )
        
        assert error.phase == "test_phase"
        assert error.severity == ErrorSeverity.ERROR
        assert error.message == "Test message"
        assert error.exception == exception
        assert error.recovery_strategy == RecoveryStrategy.RETRY
        assert error.timestamp is not None
    
    def test_orchestrator_error_auto_traceback(self):
        """Test that traceback is auto-captured from exception"""
        try:
            raise ValueError("Test error")
        except ValueError as e:
            error = OrchestratorError(
                phase="test",
                severity=ErrorSeverity.ERROR,
                message=str(e),
                exception=e
            )
        
        assert error.traceback is not None
        assert "ValueError: Test error" in error.traceback
