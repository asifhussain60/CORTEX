"""
Governance Decorator Tests - TDD for AR-003

Tests for:
- AC-AR-003-01: @governance_enforced decorator validates all rules
- AC-AR-003-02: @audit_logged decorator records to governance.db
- AC-AR-003-03: Decorators composable (@governance_enforced + @audit_logged)

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from src.core.decorators.governance_decorator import (
    governance_enforced,
    audit_logged,
    governance_with_audit,
)
from src.core.governance_enforcer import GovernanceEnforcer
from src.infrastructure.database import DatabaseManager, DatabaseConfig
from src.core.result import Ok, Err


@pytest.mark.ac("AR-003-01")
class TestGovernanceDecorator:
    """Test @governance_enforced decorator."""
    
    def test_governance_decorator_basic(self):
        """AC-AR-003-01: @governance_enforced decorator returns Result."""
        @governance_enforced(ac_id="AC-DECORATOR-001", phase="PHASE-01")
        def test_function():
            return "success"
        
        # Call decorated function - should return Result
        result = test_function()
        
        # Should return a Result object
        assert hasattr(result, 'is_ok')
        assert hasattr(result, 'is_err')
        
    def test_governance_decorator(self, temp_dir):
        """AC-AR-003-01: @governance_enforced decorator validates all rules."""
        db_path = temp_dir / "governance.db"
        db_config = DatabaseConfig(db_path=db_path)
        db = DatabaseManager(db_config)
        db.initialize()
        
        # Insert an AC-ID to test against
        db.insert_ac(
            ac_id="AC-DECORATOR-001",
            phase="PHASE-01",
            title="Test AC"
        )
        
        @governance_enforced(ac_id="AC-DECORATOR-001", phase="PHASE-01", db=db)
        def test_function():
            return "success"
        
        # Call decorated function
        result = test_function()
        
        # Should execute successfully
        assert result.is_ok()
        assert result.unwrap() == "success"
        
        db.close()
    
    def test_governance_decorator_blocks_invalid_ac_id(self, temp_dir):
        """Decorator should reject operations with invalid AC-IDs."""
        db_path = temp_dir / "governance.db"
        db_config = DatabaseConfig(db_path=db_path)
        db = DatabaseManager(db_config)
        db.initialize()
        
        @governance_enforced(ac_id="AC-INVALID-999", phase="PHASE-01", db=db)
        def test_function():
            return "success"
        
        result = test_function()
        
        # Should fail with governance violation
        assert result.is_err()
        
        db.close()
    
    def test_governance_decorator_exception_handling(self, temp_dir):
        """Decorator should catch function exceptions."""
        db_path = temp_dir / "governance.db"
        db_config = DatabaseConfig(db_path=db_path)
        db = DatabaseManager(db_config)
        db.initialize()
        
        db.insert_ac(
            ac_id="AC-DECORATOR-002",
            phase="PHASE-01",
            title="Test AC"
        )
        
        @governance_enforced(ac_id="AC-DECORATOR-002", phase="PHASE-01", db=db)
        def failing_function():
            raise ValueError("Test error")
        
        result = failing_function()
        
        # Should return error result
        assert result.is_err()
        assert "Test error" in str(result)
        
        db.close()


@pytest.mark.ac("AR-003-02")
class TestAuditDecorator:
    """Test @audit_logged decorator."""
    
    def test_audit_decorator(self, temp_dir):
        """AC-AR-003-02: @audit_logged decorator should record to governance.db."""
        db_path = temp_dir / "governance.db"
        db_config = DatabaseConfig(db_path=db_path)
        db = DatabaseManager(db_config)
        db.initialize()
        
        @audit_logged(
            ac_id="AC-AUDIT-001",
            operation="AC_EXECUTE",
            db=db,
        )
        def test_function():
            return "executed"
        
        result = test_function()
        
        # Function should execute
        assert result.is_ok()
        assert result.unwrap() == "executed"
        
        # Verify audit log entries
        query_result = db.query_audit_by_ac_id("AC-AUDIT-001")
        assert query_result.is_ok()
        
        entries = query_result.unwrap()
        assert len(entries) >= 2  # START and COMPLETE
        
        db.close()
    
    def test_audit_decorator_logs_failure(self, temp_dir):
        """Decorator should log failures to audit trail."""
        db_path = temp_dir / "governance.db"
        db_config = DatabaseConfig(db_path=db_path)
        db = DatabaseManager(db_config)
        db.initialize()
        
        @audit_logged(
            ac_id="AC-FAIL-001",
            operation="AC_EXECUTE",
            db=db,
        )
        def failing_function():
            raise RuntimeError("Test failure")
        
        result = failing_function()
        
        # Should return error
        assert result.is_err()
        
        # Verify failure was logged
        query_result = db.query_audit_by_ac_id("AC-FAIL-001")
        assert query_result.is_ok()
        
        entries = query_result.unwrap()
        assert len(entries) >= 1  # At least the start
        
        db.close()
    
    def test_audit_decorator_without_db(self, temp_dir):
        """Decorator should work without database (graceful fallback)."""
        @audit_logged(
            ac_id="AC-NOODB-001",
            operation="AC_EXECUTE",
        )
        def test_function():
            return "success"
        
        result = test_function()
        
        # Should still execute
        assert result.is_ok()
        assert result.unwrap() == "success"


@pytest.mark.ac("AR-003-03")
class TestDecoratorComposition:
    """Test composable decorators."""
    
    def test_decorator_composition(self, temp_dir):
        """AC-AR-003-03: Decorators should be composable."""
        db_path = temp_dir / "governance.db"
        db_config = DatabaseConfig(db_path=db_path)
        db = DatabaseManager(db_config)
        db.initialize()
        
        # Insert AC-ID
        db.insert_ac(
            ac_id="AC-COMPOSED-001",
            phase="PHASE-01",
            title="Test AC"
        )
        
        # Use composite decorator
        @governance_with_audit(
            ac_id="AC-COMPOSED-001",
            operation="AC_EXECUTE",
            phase="PHASE-01",
            db=db,
        )
        def test_function():
            return "composed"
        
        result = test_function()
        
        # Should execute
        assert result.is_ok()
        inner = result.unwrap()
        # Check if it's wrapped or not
        if hasattr(inner, 'unwrap'):
            assert inner.unwrap() == "composed"
        else:
            assert inner == "composed"
        
        # Verify both governance and audit
        query_result = db.query_audit_by_ac_id("AC-COMPOSED-001")
        assert query_result.is_ok()
        
        db.close()
    
    def test_stacked_decorators(self, temp_dir):
        """Decorators should stack properly."""
        db_path = temp_dir / "governance.db"
        db_config = DatabaseConfig(db_path=db_path)
        db = DatabaseManager(db_config)
        db.initialize()
        
        db.insert_ac(
            ac_id="AC-STACK-001",
            phase="PHASE-01",
            title="Test AC"
        )
        
        # Stack decorators manually
        @audit_logged(ac_id="AC-STACK-001", db=db)
        @governance_enforced(ac_id="AC-STACK-001", phase="PHASE-01", db=db)
        def test_function():
            return "stacked"
        
        result = test_function()
        
        # Should work - but unwrap twice because decorators are stacked
        assert result.is_ok()
        inner = result.unwrap()
        # Inner result might be another Ok() from the first decorator
        if hasattr(inner, 'unwrap'):
            assert inner.unwrap() == "stacked"
        else:
            assert inner == "stacked"
        
        db.close()


class TestDecoratorWithReturnValues:
    """Test decorators preserve function return values."""
    
    def test_decorator_preserves_return_type(self, temp_dir):
        """Decorator should preserve function return values."""
        db_path = temp_dir / "governance.db"
        db_config = DatabaseConfig(db_path=db_path)
        db = DatabaseManager(db_config)
        db.initialize()
        
        db.insert_ac(
            ac_id="AC-RET-001",
            phase="PHASE-01",
            title="Test AC"
        )
        
        @governance_enforced(ac_id="AC-RET-001", db=db)
        def return_dict():
            return {"key": "value"}
        
        result = return_dict()
        
        assert result.is_ok()
        assert result.unwrap() == {"key": "value"}
        
        db.close()
    
    def test_decorator_preserves_return_list(self, temp_dir):
        """Decorator should preserve list returns."""
        db_path = temp_dir / "governance.db"
        db_config = DatabaseConfig(db_path=db_path)
        db = DatabaseManager(db_config)
        db.initialize()
        
        db.insert_ac(
            ac_id="AC-RET-002",
            phase="PHASE-01",
            title="Test AC"
        )
        
        @governance_enforced(ac_id="AC-RET-002", db=db)
        def return_list():
            return [1, 2, 3]
        
        result = return_list()
        
        assert result.is_ok()
        assert result.unwrap() == [1, 2, 3]
        
        db.close()
    
    def test_decorator_preserves_none_return(self, temp_dir):
        """Decorator should handle None returns."""
        db_path = temp_dir / "governance.db"
        db_config = DatabaseConfig(db_path=db_path)
        db = DatabaseManager(db_config)
        db.initialize()
        
        db.insert_ac(
            ac_id="AC-RET-003",
            phase="PHASE-01",
            title="Test AC"
        )
        
        @governance_enforced(ac_id="AC-RET-003", db=db)
        def return_none():
            return None
        
        result = return_none()
        
        assert result.is_ok()
        assert result.unwrap() is None
        
        db.close()


class TestDecoratorMetadata:
    """Test decorator preserves function metadata."""
    
    def test_decorator_preserves_docstring(self):
        """@wraps should preserve function docstring."""
        @governance_enforced(ac_id="AC-DOC-001")
        def documented_function():
            """This is a test function."""
            return "test"
        
        # Check that docstring is preserved
        assert documented_function.__doc__ == "This is a test function."
    
    def test_decorator_preserves_name(self):
        """@wraps should preserve function name."""
        @governance_enforced(ac_id="AC-NAME-001")
        def named_function():
            return "test"
        
        assert named_function.__name__ == "named_function"


class TestDecoratorAuditTrail:
    """Test audit trail created by decorators."""
    
    def test_audit_trail_completeness(self, temp_dir):
        """Audit trail should capture all required information."""
        db_path = temp_dir / "governance.db"
        db_config = DatabaseConfig(db_path=db_path)
        db = DatabaseManager(db_config)
        db.initialize()
        
        @audit_logged(
            ac_id="AC-TRAIL-001",
            operation="AC_EXECUTE",
            db=db,
        )
        def test_function():
            return "executed"
        
        test_function()
        
        # Query audit trail
        result = db.query_audit_by_ac_id("AC-TRAIL-001")
        assert result.is_ok()
        
        entries = result.unwrap()
        assert len(entries) >= 2
        
        # Verify entries have required fields
        for entry in entries:
            assert "ac_id" in entry
            assert "operation" in entry
            assert "timestamp" in entry
            assert "component" in entry
        
        db.close()
