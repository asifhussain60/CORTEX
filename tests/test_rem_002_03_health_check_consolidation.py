"""
Tests for REMEDIATION-002 Phase B: Health Check Consolidation.

AC-REM-002-03: Consolidate health check logic with unified HealthChecker base class.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from typing import Optional


class TestHealthCheckerBase(unittest.TestCase):
    """Tests for HealthChecker base class."""
    
    def test_health_checker_initialization(self) -> None:
        """HealthChecker should initialize with component name."""
        from cortex.common.health_check import HealthChecker
        
        class TestChecker(HealthChecker):
            def validate(self) -> bool:
                return True
        
        checker = TestChecker(component_name="database")
        self.assertEqual(checker.component_name, "database")
    
    def test_health_checker_validate_abstract(self) -> None:
        """HealthChecker.validate should be overridable."""
        from cortex.common.health_check import HealthChecker
        
        class CustomChecker(HealthChecker):
            def validate(self) -> bool:
                return True
        
        checker = CustomChecker(component_name="custom")
        self.assertTrue(checker.validate())
    
    def test_health_checker_is_healthy_returns_result(self) -> None:
        """is_healthy should return validation result."""
        from cortex.common.health_check import HealthChecker
        
        class HealthyChecker(HealthChecker):
            def validate(self) -> bool:
                return True
        
        class UnhealthyChecker(HealthChecker):
            def validate(self) -> bool:
                return False
        
        self.assertTrue(HealthyChecker("healthy").is_healthy())
        self.assertFalse(UnhealthyChecker("unhealthy").is_healthy())
    
    def test_health_checker_get_status_dict(self) -> None:
        """get_status should return dict with component info."""
        from cortex.common.health_check import HealthChecker
        
        class CustomChecker(HealthChecker):
            def validate(self) -> bool:
                return True
        
        checker = CustomChecker("my_component")
        status = checker.get_status()
        
        self.assertIn("component", status)
        self.assertIn("healthy", status)
        self.assertEqual(status["component"], "my_component")
        self.assertTrue(status["healthy"])
    
    def test_health_checker_error_message_on_failure(self) -> None:
        """HealthChecker should capture error message on failure."""
        from cortex.common.health_check import HealthChecker
        
        class FailingChecker(HealthChecker):
            def validate(self) -> bool:
                self.last_error = "Connection refused"
                return False
        
        checker = FailingChecker("failing")
        checker.validate()
        status = checker.get_status()
        
        self.assertIn("error", status)


class TestDatabaseHealthCheck(unittest.TestCase):
    """Tests for DatabaseHealthCheck implementation."""
    
    def test_database_health_check_success(self) -> None:
        """DatabaseHealthCheck should return True for valid database."""
        from cortex.common.health_check import DatabaseHealthCheck
        
        checker = DatabaseHealthCheck(":memory:")
        self.assertTrue(checker.validate())
    
    def test_database_health_check_failure(self) -> None:
        """DatabaseHealthCheck should return False for invalid path."""
        from cortex.common.health_check import DatabaseHealthCheck
        
        checker = DatabaseHealthCheck("/nonexistent/path/db.sqlite")
        self.assertFalse(checker.validate())
    
    def test_database_health_check_status(self) -> None:
        """DatabaseHealthCheck status should include database info."""
        from cortex.common.health_check import DatabaseHealthCheck
        
        checker = DatabaseHealthCheck(":memory:")
        status = checker.get_status()
        
        self.assertEqual(status["component"], "database")


class TestCompositeHealthCheck(unittest.TestCase):
    """Tests for CompositeHealthCheck with multiple checkers."""
    
    def test_composite_all_healthy(self) -> None:
        """CompositeHealthCheck should pass when all checks pass."""
        from cortex.common.health_check import (
            HealthChecker, CompositeHealthCheck
        )
        
        class PassingChecker(HealthChecker):
            def validate(self) -> bool:
                return True
        
        composite = CompositeHealthCheck([
            PassingChecker("check1"),
            PassingChecker("check2"),
        ])
        
        self.assertTrue(composite.is_healthy())
    
    def test_composite_one_failing(self) -> None:
        """CompositeHealthCheck should fail when any check fails."""
        from cortex.common.health_check import (
            HealthChecker, CompositeHealthCheck
        )
        
        class PassingChecker(HealthChecker):
            def validate(self) -> bool:
                return True
        
        class FailingChecker(HealthChecker):
            def validate(self) -> bool:
                return False
        
        composite = CompositeHealthCheck([
            PassingChecker("passing"),
            FailingChecker("failing"),
        ])
        
        self.assertFalse(composite.is_healthy())
    
    def test_composite_get_all_statuses(self) -> None:
        """CompositeHealthCheck should return all component statuses."""
        from cortex.common.health_check import (
            HealthChecker, CompositeHealthCheck
        )
        
        class PassingChecker(HealthChecker):
            def validate(self) -> bool:
                return True
        
        composite = CompositeHealthCheck([
            PassingChecker("comp1"),
            PassingChecker("comp2"),
        ])
        
        statuses = composite.get_all_statuses()
        self.assertEqual(len(statuses), 2)


class TestHealthCheckDecorator(unittest.TestCase):
    """Tests for @health_check decorator."""
    
    def test_health_check_decorator_wraps_function(self) -> None:
        """health_check decorator should wrap function as health check."""
        from cortex.common.health_check import health_check
        
        @health_check("my_service")
        def check_service() -> bool:
            return True
        
        self.assertTrue(check_service())
    
    def test_health_check_decorator_catches_exceptions(self) -> None:
        """health_check decorator should catch exceptions and return False."""
        from cortex.common.health_check import health_check
        
        @health_check("failing_service")
        def check_failing() -> bool:
            raise ConnectionError("Service unavailable")
        
        result = check_failing()
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
