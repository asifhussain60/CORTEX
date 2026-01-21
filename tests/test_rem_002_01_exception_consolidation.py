"""
Tests for REMEDIATION-002 Phase A: Exception Handler Consolidation.

AC-REM-002-01: Consolidate exception handlers with decorator patterns.
Tests the decorator-based exception handling system.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sqlite3
import logging
from typing import Optional


class TestExceptionDecorators(unittest.TestCase):
    """Tests for exception handler decorators."""
    
    def test_handle_database_error_decorator_catches_sqlite_error(self) -> None:
        """Decorator should catch and handle sqlite3 errors."""
        from cortex.common.exceptions import handle_database_error
        
        @handle_database_error
        def failing_db_operation() -> str:
            raise sqlite3.Error("Connection failed")
        
        # Should not raise, returns None or handles gracefully
        result = failing_db_operation()
        self.assertIsNone(result)
    
    def test_handle_database_error_decorator_logs_error(self) -> None:
        """Decorator should log the database error."""
        from cortex.common.exceptions import handle_database_error
        
        @handle_database_error
        def failing_operation() -> str:
            raise sqlite3.OperationalError("Database locked")
        
        with patch('cortex.common.exceptions.logging') as mock_logging:
            failing_operation()
            mock_logging.log.assert_called()
    
    def test_handle_database_error_decorator_returns_fallback(self) -> None:
        """Decorator with fallback should return fallback value on error."""
        from cortex.common.exceptions import handle_database_error
        
        @handle_database_error(fallback="default_value")
        def failing_operation() -> str:
            raise sqlite3.Error("Connection error")
        
        result = failing_operation()
        self.assertEqual(result, "default_value")
    
    def test_handle_database_error_decorator_reraises_when_configured(self) -> None:
        """Decorator should reraise when reraise=True."""
        from cortex.common.exceptions import handle_database_error, DatabaseOperationError
        
        @handle_database_error(reraise=True)
        def failing_operation() -> str:
            raise sqlite3.Error("Connection error")
        
        with self.assertRaises(DatabaseOperationError):
            failing_operation()
    
    def test_handle_database_error_decorator_success_path(self) -> None:
        """Decorator should not interfere with successful operations."""
        from cortex.common.exceptions import handle_database_error
        
        @handle_database_error
        def successful_operation() -> str:
            return "success"
        
        result = successful_operation()
        self.assertEqual(result, "success")
    
    def test_handle_validation_error_decorator_catches_value_error(self) -> None:
        """Validation decorator should catch ValueError."""
        from cortex.common.exceptions import handle_validation_error
        
        @handle_validation_error
        def validate_input(value: str) -> bool:
            if not value:
                raise ValueError("Empty value")
            return True
        
        result = validate_input("")
        self.assertFalse(result)
    
    def test_handle_validation_error_decorator_catches_type_error(self) -> None:
        """Validation decorator should catch TypeError."""
        from cortex.common.exceptions import handle_validation_error
        
        @handle_validation_error
        def validate_type(value: str) -> bool:
            if not isinstance(value, str):
                raise TypeError("Expected string")
            return True
        
        result = validate_type(123)  # type: ignore
        self.assertFalse(result)
    
    def test_handle_io_error_decorator_catches_file_errors(self) -> None:
        """IO decorator should catch file-related errors."""
        from cortex.common.exceptions import handle_io_error
        
        @handle_io_error
        def read_file(path: str) -> Optional[str]:
            raise FileNotFoundError(f"File not found: {path}")
        
        result = read_file("/nonexistent/path")
        self.assertIsNone(result)
    
    def test_handle_io_error_decorator_with_fallback(self) -> None:
        """IO decorator should return fallback on error."""
        from cortex.common.exceptions import handle_io_error
        
        @handle_io_error(fallback={})
        def load_config(path: str) -> dict:
            raise PermissionError("Access denied")
        
        result = load_config("/etc/secret")
        self.assertEqual(result, {})


class TestExceptionChaining(unittest.TestCase):
    """Tests for exception chaining and context preservation."""
    
    def test_database_operation_error_preserves_original(self) -> None:
        """DatabaseOperationError should chain original exception."""
        from cortex.common.exceptions import DatabaseOperationError
        
        original = sqlite3.Error("Original error")
        wrapped = DatabaseOperationError("Database operation failed", original)
        
        self.assertIs(wrapped.__cause__, original)
        self.assertIn("Original error", str(wrapped))
    
    def test_database_operation_error_includes_operation_name(self) -> None:
        """DatabaseOperationError should include operation context."""
        from cortex.common.exceptions import DatabaseOperationError
        
        error = DatabaseOperationError(
            "Insert failed",
            operation="insert_record",
            table="audit_log"
        )
        
        self.assertEqual(error.operation, "insert_record")
        self.assertEqual(error.table, "audit_log")
        self.assertIn("insert_record", str(error))


class TestDecoratorComposition(unittest.TestCase):
    """Tests for composing multiple decorators."""
    
    def test_multiple_decorators_in_order(self) -> None:
        """Multiple decorators should apply in correct order."""
        from cortex.common.exceptions import (
            handle_database_error,
            handle_validation_error
        )
        
        @handle_database_error
        @handle_validation_error
        def complex_operation(value: str) -> str:
            if not value:
                raise ValueError("Empty")
            return value.upper()
        
        # Empty value - validation error handled
        result = complex_operation("")
        self.assertFalse(result)
        
        # Valid value - success
        result = complex_operation("test")
        self.assertEqual(result, "TEST")


class TestLoggingIntegration(unittest.TestCase):
    """Tests for logging integration with decorators."""
    
    def test_decorator_logs_exception_details(self) -> None:
        """Decorator should log exception type and message."""
        from cortex.common.exceptions import handle_database_error
        
        @handle_database_error
        def db_operation() -> None:
            raise sqlite3.IntegrityError("UNIQUE constraint failed")
        
        with patch('cortex.common.exceptions.logging') as mock_logging:
            db_operation()
            # Verify logging was called with error details
            mock_logging.log.assert_called()


class TestRetryDecorator(unittest.TestCase):
    """Tests for retry decorator functionality."""
    
    def test_retry_decorator_retries_on_failure(self) -> None:
        """Retry decorator should retry specified number of times."""
        from cortex.common.exceptions import retry_on_error
        
        call_count = 0
        
        @retry_on_error(max_retries=3, delay_seconds=0.01)
        def flaky_operation() -> str:
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ConnectionError("Temporary failure")
            return "success"
        
        result = flaky_operation()
        self.assertEqual(result, "success")
        self.assertEqual(call_count, 3)
    
    def test_retry_decorator_gives_up_after_max_retries(self) -> None:
        """Retry decorator should give up after max retries."""
        from cortex.common.exceptions import retry_on_error, RetryExhaustedError
        
        @retry_on_error(max_retries=2, delay_seconds=0.01)
        def always_fails() -> str:
            raise ConnectionError("Permanent failure")
        
        with self.assertRaises(RetryExhaustedError):
            always_fails()
    
    def test_retry_decorator_only_retries_specified_exceptions(self) -> None:
        """Retry decorator should only retry specified exception types."""
        from cortex.common.exceptions import retry_on_error
        
        @retry_on_error(max_retries=3, retry_on=(ConnectionError,), delay_seconds=0.01)
        def wrong_exception() -> str:
            raise ValueError("Not retryable")
        
        with self.assertRaises(ValueError):
            wrong_exception()


if __name__ == "__main__":
    unittest.main()
