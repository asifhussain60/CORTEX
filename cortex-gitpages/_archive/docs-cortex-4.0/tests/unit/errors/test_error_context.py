"""Unit tests for structured error context and causality."""

import pytest
from typing import Any, Dict, List, Optional
from unittest.mock import Mock, patch
from datetime import datetime
import uuid

from cortex.core.errors.structured_error import (
    StructuredError,
    ErrorType,
    CausalityChain,
    ErrorContext,
    RecoveryHint,
    sanitize_pii,
)


class TestErrorType:
    """Test error type classification."""
    
    def test_error_types(self) -> None:
        """Test error type enumeration."""
        assert ErrorType.TRANSIENT == "TRANSIENT"
        assert ErrorType.PERMANENT == "PERMANENT"
        assert ErrorType.CONFIGURATION == "CONFIGURATION"
        assert ErrorType.VALIDATION == "VALIDATION"


class TestRecoveryHint:
    """Test recovery hint generation."""
    
    def test_hint_creation(self) -> None:
        """Test creating recovery hint."""
        hint = RecoveryHint(
            action="Retry operation",
            automated=True,
            estimated_duration_seconds=5
        )
        
        assert hint.action == "Retry operation"
        assert hint.automated is True
        assert hint.estimated_duration_seconds == 5
    
    def test_hint_for_transient_error(self) -> None:
        """Test recovery hint for transient error."""
        hint = RecoveryHint.for_error_type(ErrorType.TRANSIENT)
        
        assert hint.automated is True
        assert "retry" in hint.action.lower()
    
    def test_hint_for_configuration_error(self) -> None:
        """Test recovery hint for configuration error."""
        hint = RecoveryHint.for_error_type(ErrorType.CONFIGURATION)
        
        assert hint.automated is False
        assert "configuration" in hint.action.lower()


class TestCausalityChain:
    """Test causality chain tracking."""
    
    def test_single_error_chain(self) -> None:
        """Test chain with single error."""
        chain = CausalityChain()
        chain.add_error("root-error", "Root cause error")
        
        assert len(chain.errors) == 1
        assert chain.root_cause() == "Root cause error"
    
    def test_multi_level_chain(self) -> None:
        """Test chain with multiple causes."""
        chain = CausalityChain()
        chain.add_error("error-1", "Database connection failed")
        chain.add_error("error-2", "Query execution failed", caused_by="error-1")
        chain.add_error("error-3", "Operation failed", caused_by="error-2")
        
        assert len(chain.errors) == 3
        assert chain.root_cause() == "Database connection failed"
    
    def test_circular_causality_detected(self) -> None:
        """Test circular causality is detected and broken."""
        chain = CausalityChain()
        chain.add_error("error-1", "Error 1", caused_by="error-2")
        chain.add_error("error-2", "Error 2", caused_by="error-1")
        
        # Should detect cycle and break it
        assert chain.has_cycle()
    
    def test_contributing_factors(self) -> None:
        """Test tracking contributing factors."""
        chain = CausalityChain()
        chain.add_error(
            "main-error",
            "Operation failed",
            contributing_factors=["high load", "low memory"]
        )
        
        assert len(chain.errors[0].contributing_factors) == 2


class TestErrorContext:
    """Test error context enrichment."""
    
    def test_context_creation(self) -> None:
        """Test creating error context."""
        context = ErrorContext(
            correlation_id="corr-123",
            operation="phase_validation",
            user_id="user-456",
            metadata={"phase_id": "phase-1"}
        )
        
        assert context.correlation_id == "corr-123"
        assert context.operation == "phase_validation"
        assert context.metadata["phase_id"] == "phase-1"
    
    def test_correlation_id_generation(self) -> None:
        """Test correlation ID auto-generated if missing."""
        context = ErrorContext(operation="test")
        
        assert context.correlation_id is not None
        assert len(context.correlation_id) > 0
    
    def test_context_propagation(self) -> None:
        """Test context propagated through call chain."""
        parent_context = ErrorContext(
            correlation_id="corr-123",
            operation="parent_op"
        )
        
        child_context = ErrorContext(
            operation="child_op",
            parent_context=parent_context
        )
        
        # Child inherits correlation ID
        assert child_context.correlation_id == "corr-123"


class TestPIISanitization:
    """Test PII sanitization."""
    
    def test_sanitize_email(self) -> None:
        """Test email addresses sanitized."""
        text = "User email: user@example.com"
        sanitized = sanitize_pii(text)
        
        assert "user@example.com" not in sanitized
        assert "[EMAIL]" in sanitized
    
    def test_sanitize_api_key(self) -> None:
        """Test API keys sanitized."""
        text = "API key: sk-abc123xyz789"
        sanitized = sanitize_pii(text)
        
        assert "sk-abc123xyz789" not in sanitized
        assert "[API_KEY]" in sanitized
    
    def test_sanitize_phone(self) -> None:
        """Test phone numbers sanitized."""
        text = "Phone: 555-123-4567"
        sanitized = sanitize_pii(text)
        
        assert "555-123-4567" not in sanitized
        assert "[PHONE]" in sanitized
    
    def test_sanitize_preserves_structure(self) -> None:
        """Test sanitization preserves message structure."""
        text = "Error: Failed to send email to user@example.com"
        sanitized = sanitize_pii(text)
        
        assert "Error: Failed to send email to [EMAIL]" == sanitized


class TestStructuredError:
    """Test structured error creation."""
    
    def test_error_creation(self) -> None:
        """Test creating structured error."""
        error = StructuredError(
            error_type=ErrorType.TRANSIENT,
            message="Database connection failed",
            code="DB_CONNECTION_ERROR",
            context=ErrorContext(operation="query_execution")
        )
        
        assert error.error_type == ErrorType.TRANSIENT
        assert error.message == "Database connection failed"
        assert error.code == "DB_CONNECTION_ERROR"
    
    def test_error_with_causality(self) -> None:
        """Test error with causality chain."""
        causality = CausalityChain()
        causality.add_error("root", "Root cause")
        
        error = StructuredError(
            error_type=ErrorType.PERMANENT,
            message="Operation failed",
            code="OP_FAILED",
            context=ErrorContext(operation="test"),
            causality=causality
        )
        
        assert error.causality is not None
        assert error.causality.root_cause() == "Root cause"
    
    def test_error_with_recovery_hint(self) -> None:
        """Test error with recovery hint."""
        hint = RecoveryHint(action="Retry after 5 seconds", automated=True)
        
        error = StructuredError(
            error_type=ErrorType.TRANSIENT,
            message="Temporary failure",
            code="TEMP_FAIL",
            context=ErrorContext(operation="test"),
            recovery_hint=hint
        )
        
        assert error.recovery_hint is not None
        assert error.recovery_hint.automated is True
    
    def test_error_serialization(self) -> None:
        """Test error can be serialized."""
        error = StructuredError(
            error_type=ErrorType.VALIDATION,
            message="Invalid input",
            code="VALIDATION_ERROR",
            context=ErrorContext(operation="validate")
        )
        
        data = error.to_dict()
        
        assert data["error_type"] == "VALIDATION"
        assert data["message"] == "Invalid input"
        assert data["code"] == "VALIDATION_ERROR"
        assert "timestamp" in data
    
    def test_error_includes_correlation_id(self) -> None:
        """Test error includes correlation ID."""
        context = ErrorContext(correlation_id="corr-123", operation="test")
        
        error = StructuredError(
            error_type=ErrorType.PERMANENT,
            message="Error",
            code="ERR",
            context=context
        )
        
        assert error.correlation_id() == "corr-123"
    
    def test_pii_sanitized_in_message(self) -> None:
        """Test PII automatically sanitized in error message."""
        error = StructuredError(
            error_type=ErrorType.PERMANENT,
            message="Failed to email user@example.com",
            code="EMAIL_FAILED",
            context=ErrorContext(operation="send_email")
        )
        
        sanitized_msg = error.sanitized_message()
        
        assert "user@example.com" not in sanitized_msg
        assert "[EMAIL]" in sanitized_msg
    
    def test_error_machine_parseable(self) -> None:
        """Test error output is machine-parseable."""
        error = StructuredError(
            error_type=ErrorType.CONFIGURATION,
            message="Missing config key",
            code="CONFIG_MISSING",
            context=ErrorContext(operation="load_config")
        )
        
        data = error.to_dict()
        
        # Should be valid for JSON serialization
        import json
        json_str = json.dumps(data)
        parsed = json.loads(json_str)
        
        assert parsed["error_type"] == "CONFIGURATION"
        assert parsed["code"] == "CONFIG_MISSING"


class TestErrorIntegration:
    """Integration tests for structured errors."""
    
    def test_end_to_end_error_flow(self) -> None:
        """Test complete error creation and handling."""
        # Create causality chain
        causality = CausalityChain()
        causality.add_error("db-error", "Database connection timeout")
        causality.add_error("query-error", "Query failed", caused_by="db-error")
        
        # Create context
        context = ErrorContext(
            correlation_id="corr-test-123",
            operation="data_fetch",
            user_id="user-789",
            metadata={"query": "SELECT * FROM users"}
        )
        
        # Create recovery hint
        hint = RecoveryHint.for_error_type(ErrorType.TRANSIENT)
        
        # Create error
        error = StructuredError(
            error_type=ErrorType.TRANSIENT,
            message="Failed to fetch user data",
            code="DATA_FETCH_FAILED",
            context=context,
            causality=causality,
            recovery_hint=hint
        )
        
        # Serialize
        data = error.to_dict()
        
        # Verify structure
        assert data["correlation_id"] == "corr-test-123"
        assert data["code"] == "DATA_FETCH_FAILED"
        assert data["causality"]["root_cause"] == "Database connection timeout"
        assert data["recovery_hint"]["automated"] is True
    
    def test_error_tracing_through_system(self) -> None:
        """Test error can be traced through distributed system."""
        # Parent operation
        parent_context = ErrorContext(
            correlation_id="trace-123",
            operation="parent_operation"
        )
        
        # Child operation inherits correlation
        child_context = ErrorContext(
            operation="child_operation",
            parent_context=parent_context
        )
        
        # Create error in child
        error = StructuredError(
            error_type=ErrorType.PERMANENT,
            message="Child operation failed",
            code="CHILD_FAILED",
            context=child_context
        )
        
        # Correlation ID maintained
        assert error.correlation_id() == "trace-123"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
