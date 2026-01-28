"""
AC-REM-001-04: Health Check Framework Tests

Verifies that health checks are operational and detect failures.

Updated: 2026-01-28 - Fixed imports to match actual implementation (CORE-030)
"""

import pytest
from unittest.mock import MagicMock, patch

from cortex.common.health_check import (
    DatabaseHealthCheck,
    HealthChecker,
    CompositeHealthCheck,
)


class TestDatabaseHealthCheck:
    """Test database health check."""
    
    def test_database_health_check_callable(self):
        """Database health check should be callable."""
        mock_path = "/tmp/test.db"
        checker = DatabaseHealthCheck(mock_path)
        
        assert hasattr(checker, 'validate')
        assert callable(checker.validate)
    
    def test_database_health_check_returns_status(self):
        """Database health check should return status dict."""
        with patch('cortex.common.health_check.sqlite3.connect') as mock_connect:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_cursor.fetchone.return_value = (1,)
            mock_conn.cursor.return_value = mock_cursor
            mock_connect.return_value = mock_conn
            
            checker = DatabaseHealthCheck("/tmp/test.db")
            status = checker.get_status()
            
            assert isinstance(status, dict)
            assert status["component"] == "database"
    
    def test_database_health_check_error_handling(self):
        """Database health check should handle connection errors."""
        with patch('cortex.common.health_check.sqlite3.connect') as mock_connect:
            mock_connect.side_effect = Exception("Connection failed")
            
            checker = DatabaseHealthCheck("/tmp/test.db")
            result = checker.is_healthy()
            
            assert result is False
            assert checker.last_error is not None


class TestCompositeHealthCheck:
    """Test composite health check."""
    
    def test_composite_health_check_empty(self):
        """Composite with no checkers should be healthy."""
        composite = CompositeHealthCheck([])
        assert composite.is_healthy() is True
    
    def test_composite_health_check_all_healthy(self):
        """Composite should be healthy when all checks pass."""
        mock_checker1 = MagicMock(spec=HealthChecker)
        mock_checker1.is_healthy.return_value = True
        mock_checker1.get_status.return_value = {"component": "test1", "healthy": True}
        
        mock_checker2 = MagicMock(spec=HealthChecker)
        mock_checker2.is_healthy.return_value = True
        mock_checker2.get_status.return_value = {"component": "test2", "healthy": True}
        
        composite = CompositeHealthCheck([mock_checker1, mock_checker2])
        
        assert composite.is_healthy() is True
    
    def test_composite_health_check_one_unhealthy(self):
        """Composite should be unhealthy when any check fails."""
        mock_checker1 = MagicMock(spec=HealthChecker)
        mock_checker1.is_healthy.return_value = True
        
        mock_checker2 = MagicMock(spec=HealthChecker)
        mock_checker2.is_healthy.return_value = False
        
        composite = CompositeHealthCheck([mock_checker1, mock_checker2])
        
        assert composite.is_healthy() is False
    
    def test_composite_get_summary(self):
        """Composite should return summary of all checks."""
        mock_checker = MagicMock(spec=HealthChecker)
        mock_checker.is_healthy.return_value = True
        mock_checker.get_status.return_value = {"component": "test", "healthy": True}
        
        composite = CompositeHealthCheck([mock_checker])
        summary = composite.get_summary()
        
        assert summary["overall_healthy"] is True
        assert summary["healthy_count"] == 1
        assert summary["total_count"] == 1
        assert len(summary["components"]) == 1


class TestHealthCheckerBase:
    """Test HealthChecker base class behavior."""
    
    def test_health_checker_caches_result(self):
        """HealthChecker should cache the last result."""
        
        class TestChecker(HealthChecker):
            def __init__(self):
                super().__init__("test")
                self.call_count = 0
            
            def validate(self):
                self.call_count += 1
                return True
        
        checker = TestChecker()
        checker.is_healthy()
        
        assert checker._last_check_result is True
        assert checker.call_count == 1
    
    def test_health_checker_records_error(self):
        """HealthChecker should record errors."""
        
        class FailingChecker(HealthChecker):
            def __init__(self):
                super().__init__("failing")
            
            def validate(self):
                raise ValueError("Test error")
        
        checker = FailingChecker()
        result = checker.is_healthy()
        
        assert result is False
        assert "Test error" in checker.last_error
