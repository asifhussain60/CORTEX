"""
Base Test Class for Negative (Forbidden Action) Tests

Provides helpers for testing that orchestrators properly BLOCK forbidden actions.

Authority: AC-GOLDEN-FRAMEWORK-001
"""
from typing import Callable, Type

import pytest

from tests.orchestrators.base_orchestrator_test import BaseOrchestratorTest


class BaseNegativeTest(BaseOrchestratorTest):
    """Base class for negative (forbidden action) tests."""
    
    def assert_blocked(
        self,
        action: Callable,
        expected_error: Type[Exception],
        expected_message_contains: str
    ) -> None:
        """
        Assert that an action is blocked with appropriate error.
        
        Args:
            action: Callable that should be blocked
            expected_error: Expected exception type
            expected_message_contains: Expected substring in error message
            
        Raises:
            AssertionError: If action not blocked correctly
        """
        with pytest.raises(expected_error) as exc_info:
            action()
        
        assert expected_message_contains in str(exc_info.value), \
            f"Expected '{expected_message_contains}' in error message"
    
    def assert_violation_logged(
        self,
        db_path,
        violation_type: str
    ) -> None:
        """
        Assert that governance violation was logged.
        
        Args:
            db_path: Path to audit database
            violation_type: Type of violation (e.g., "TDD_BYPASS")
            
        Raises:
            AssertionError: If violation not logged
        """
        import sqlite3
        
        conn = sqlite3.connect(db_path)
        cursor = conn.execute(
            "SELECT details FROM audit_log WHERE operation = ? AND status = 'BLOCKED'",
            (violation_type,)
        )
        result = cursor.fetchone()
        conn.close()
        
        assert result is not None, f"Violation {violation_type} not logged"
