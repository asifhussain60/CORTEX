"""
AC-REM-001-04: Health Check Framework Tests

Verifies that health checks are operational and detect failures.
"""

import pytest
from unittest.mock import MagicMock, patch
import logging

from cortex.infrastructure.health_check import (
    DatabaseHealthCheck,
    AuditLoggerHealthCheck,
    ConnectionPoolHealthCheck,
    HealthCheckManager,
    HealthStatus
)


class TestDatabaseHealthCheck:
    """Test database health check."""
    
    def test_database_health_check_callable(self):
        """Database health check should be callable."""
        mock_path = MagicMock()
        checker = DatabaseHealthCheck(mock_path)
        
        assert hasattr(checker, 'check')
        assert callable(checker.check)
    
    def test_database_health_check_returns_status(self):
        """Database health check should return HealthStatus."""
        with patch('cortex.infrastructure.health_check.sqlite3.connect') as mock_connect:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_cursor.fetchone.return_value = (1,)
            mock_conn.cursor.return_value = mock_cursor
            mock_connect.return_value.__enter__.return_value = mock_conn
            
            mock_path = MagicMock()
            checker = DatabaseHealthCheck(mock_path)
            status = checker.check()
            
            assert isinstance(status, HealthStatus)
            assert status.component == "database"


class TestAuditLoggerHealthCheck:
    """Test audit logger health check."""
    
    def test_audit_logger_health_check_callable(self):
        """Audit logger health check should be callable."""
        mock_path = MagicMock()
        checker = AuditLoggerHealthCheck(mock_path)
        
        assert hasattr(checker, 'check')
        assert callable(checker.check)
    
    def test_audit_logger_health_check_error_handling(self):
        """Audit logger health check should handle errors."""
        with patch('builtins.open', side_effect=IOError("Test error")):
            mock_path = MagicMock()
            checker = AuditLoggerHealthCheck(mock_path)
            status = checker.check()
            
            assert isinstance(status, HealthStatus)
            assert status.component == "audit_logger"
            assert not status.healthy


class TestConnectionPoolHealthCheck:
    """Test connection pool health check."""
    
    def test_connection_pool_health_check_callable(self):
        """Connection pool health check should be callable."""
        mock_pool = MagicMock()
        checker = ConnectionPoolHealthCheck(mock_pool)
        
        assert hasattr(checker, 'check')
        assert callable(checker.check)
    
    def test_connection_pool_health_check_returns_status(self):
        """Connection pool health check should return HealthStatus."""
        mock_pool = MagicMock()
        mock_pool._available = MagicMock()
        mock_pool._available.qsize = MagicMock(return_value=5)
        mock_pool._all_connections = {1: "conn1", 2: "conn2"}
        
        checker = ConnectionPoolHealthCheck(mock_pool)
        status = checker.check()
        
        assert isinstance(status, HealthStatus)
        assert status.component == "connection_pool"


class TestHealthCheckManager:
    """Test health check manager."""
    
    def test_health_check_manager_register(self):
        """Health check manager should register checks."""
        manager = HealthCheckManager()
        
        mock_checker = MagicMock()
        manager.register_check("test", mock_checker)
        
        assert "test" in manager.checks
    
    def test_health_check_manager_run_all(self):
        """Health check manager should run all checks."""
        manager = HealthCheckManager()
        
        # Mock checker returns healthy status
        mock_checker = MagicMock()
        mock_status = HealthStatus(
            component="test",
            healthy=True,
            message="OK",
            latency_ms=1.0,
            timestamp=0
        )
        mock_checker.check.return_value = mock_status
        
        manager.register_check("test", mock_checker)
        
        healthy, results = manager.check_all()
        
        assert len(results) == 1
        assert results[0].component == "test"
        assert results[0].healthy
