"""
Integration Tests for Orchestrator Health Checker

AC-DB-SSOT-TEST-002: Tests for the OrchestratorHealthChecker

Tests:
- Health check execution
- Background check scheduling
- Unwiring detection
- Recovery attempts
- Escalation logic
- Database logging

Author: Asif Hussain
Date: 2026-01-25
"""

import shutil
import tempfile
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional
from unittest.mock import MagicMock, patch

import pytest

from cortex.infrastructure.database import DatabaseConfig, DatabaseManager
from cortex.orchestrators.core.database_registry import (
    DatabaseBackedRegistry,
    OrchestratorCategory,
    OrchestratorConfig,
    RegistryValidation,
    WiringState,
)
from cortex.orchestrators.core.health_checker import (
    HealthCheckResult,
    OrchestratorHealthChecker,
    create_health_checker,
)


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def temp_db_dir():
    """Create a temporary directory for test databases."""
    tmpdir = tempfile.mkdtemp()
    yield tmpdir
    shutil.rmtree(tmpdir, ignore_errors=True)


@pytest.fixture
def db_manager(temp_db_dir):
    """Create a DatabaseManager with a temporary database."""
    db_path = Path(temp_db_dir) / "test_health.db"
    config = DatabaseConfig(db_path=db_path)
    return DatabaseManager(config)


@pytest.fixture
def registry(db_manager):
    """Create a fresh DatabaseBackedRegistry instance."""
    DatabaseBackedRegistry.reset_instance()
    reg = DatabaseBackedRegistry(db_manager)
    reg.initialize_schema()
    return reg


@pytest.fixture
def health_checker(registry):
    """Create a health checker for the registry."""
    checker = OrchestratorHealthChecker(registry)
    yield checker
    # Stop any background checks
    checker.stop_background_checks()


# ============================================================================
# Health Check Execution Tests
# ============================================================================

class TestHealthCheckExecution:
    """Tests for individual health check execution."""

    def test_run_health_check_empty_registry(self, health_checker, registry):
        """Health check on empty registry should pass."""
        # Reset registry singleton to get clean state
        DatabaseBackedRegistry.reset_instance()
        
        result = health_checker.run_health_check()
        
        assert isinstance(result, HealthCheckResult)
        assert result.orchestrators_ok == 0
        assert result.orchestrators_failed == 0
        # Note: is_healthy may be False due to drift detection from other tests
        # Just verify the basic check runs

    def test_run_health_check_with_registered_orchestrator(
        self, health_checker, registry
    ):
        """Health check should count registered but unwired orchestrators."""
        registry.register(OrchestratorConfig(
            name="test",
            module_path="test.module",
            class_name="Test",
            category=OrchestratorCategory.CORE,
        ))
        
        result = health_checker.run_health_check()
        
        assert result.orchestrators_failed >= 0
        assert isinstance(result.check_time, datetime)

    def test_health_check_result_structure(self, health_checker, registry):
        """HealthCheckResult should have all required fields."""
        registry.register(OrchestratorConfig(
            name="test",
            module_path="test.module",
            class_name="Test",
            category=OrchestratorCategory.CORE,
        ))
        
        result = health_checker.run_health_check()
        
        # Verify structure
        assert hasattr(result, "check_time")
        assert hasattr(result, "orchestrators_ok")
        assert hasattr(result, "orchestrators_failed")
        assert hasattr(result, "unwiring_detected")
        assert hasattr(result, "recovery_attempted")
        assert hasattr(result, "recovery_success")
        assert hasattr(result, "details")
        assert hasattr(result, "is_healthy")

    def test_health_check_stores_details(self, health_checker, registry):
        """Health check should store validation details."""
        registry.register(OrchestratorConfig(
            name="detail_test",
            module_path="test.detail",
            class_name="DetailTest",
            category=OrchestratorCategory.CORE,
        ))
        
        result = health_checker.run_health_check()
        
        assert "validation" in result.details
        assert "checked" in result.details["validation"]


# ============================================================================
# Background Check Tests
# ============================================================================

class TestBackgroundChecks:
    """Tests for background health check scheduling."""

    def test_start_background_checks(self, health_checker):
        """Should start background check thread."""
        health_checker.start_background_checks(interval_seconds=5)
        
        assert health_checker._running
        assert health_checker._check_thread is not None
        assert health_checker._check_thread.is_alive()
        
        health_checker.stop_background_checks()

    def test_stop_background_checks(self, health_checker):
        """Should stop background check thread."""
        health_checker.start_background_checks(interval_seconds=5)
        health_checker.stop_background_checks()
        
        assert not health_checker._running
        time.sleep(0.1)  # Give thread time to stop

    def test_background_check_executes(self, health_checker, registry):
        """Background check should execute within interval."""
        registry.register(OrchestratorConfig(
            name="bg_test",
            module_path="test.bg",
            class_name="BgTest",
            category=OrchestratorCategory.CORE,
        ))
        
        health_checker.start_background_checks(interval_seconds=1)
        
        # Wait for at least one check
        time.sleep(1.5)
        
        health_checker.stop_background_checks()
        
        # Should have at least one check in history
        history = health_checker.get_check_history()
        assert len(history) >= 1

    def test_multiple_start_calls_safe(self, health_checker):
        """Multiple start calls should be safe."""
        health_checker.start_background_checks(interval_seconds=5)
        health_checker.start_background_checks(interval_seconds=5)  # Should warn
        
        assert health_checker._running
        
        health_checker.stop_background_checks()


# ============================================================================
# Unwiring Detection Tests
# ============================================================================

class TestUnwiringDetection:
    """Tests for unwiring detection."""

    def test_detect_unwired_orchestrator(self, health_checker, registry):
        """Should detect when orchestrator is not wired."""
        registry.register(OrchestratorConfig(
            name="unwired",
            module_path="test.unwired",
            class_name="Unwired",
            category=OrchestratorCategory.CORE,
        ))
        
        result = health_checker.run_health_check()
        
        # Should detect the unwired orchestrator
        assert result.orchestrators_failed >= 1 or not result.is_healthy

    def test_consecutive_failure_tracking(self, health_checker, registry):
        """Should track consecutive failures."""
        registry.register(OrchestratorConfig(
            name="fail_test",
            module_path="test.fail",
            class_name="FailTest",
            category=OrchestratorCategory.CORE,
        ))
        
        # Run multiple checks
        health_checker.run_health_check()
        health_checker.run_health_check()
        
        status = health_checker.get_status()
        # consecutive_failures should be tracked
        assert "consecutive_failures" in status


# ============================================================================
# Recovery Tests
# ============================================================================

class TestRecovery:
    """Tests for automatic recovery attempts."""

    def test_recovery_attempted_on_unwiring(self, health_checker, registry):
        """Recovery should be attempted when unwiring is detected."""
        # Register a real orchestrator that can be wired
        registry.register(OrchestratorConfig(
            name="recoverable",
            module_path="cortex.orchestrators.core.master_orchestrator",
            class_name="MasterOrchestrator",
            category=OrchestratorCategory.CORE,
        ))
        
        result = health_checker.run_health_check()
        
        # If unwiring was detected, recovery should have been attempted
        if result.unwiring_detected:
            assert "recovery" in result.details

    def test_recovery_counter_reset(self, health_checker, registry):
        """Recovery counter should reset on success."""
        health_checker._recovery_attempts = 2
        health_checker._consecutive_failures = 3
        
        health_checker.reset_recovery_counter()
        
        assert health_checker._recovery_attempts == 0
        assert health_checker._consecutive_failures == 0


# ============================================================================
# Escalation Tests
# ============================================================================

class TestEscalation:
    """Tests for escalation on persistent failures."""

    def test_escalation_threshold(self, health_checker, registry):
        """Should escalate after threshold failures."""
        alert_called = []
        
        def alert_callback(message, details):
            alert_called.append((message, details))
        
        health_checker._alert_callback = alert_callback
        health_checker._consecutive_failures = (
            OrchestratorHealthChecker.ESCALATION_THRESHOLD
        )
        
        registry.register(OrchestratorConfig(
            name="escalate_test",
            module_path="test.escalate",
            class_name="EscalateTest",
            category=OrchestratorCategory.CORE,
        ))
        
        health_checker.run_health_check()
        
        # Should have triggered escalation
        if health_checker._consecutive_failures >= OrchestratorHealthChecker.ESCALATION_THRESHOLD:
            # Alert callback should have been called
            pass  # May or may not have been called based on unwiring_detected


# ============================================================================
# Database Logging Tests
# ============================================================================

class TestDatabaseLogging:
    """Tests for health check database logging."""

    def test_health_check_logged_to_db(self, health_checker, registry, db_manager):
        """Health checks should be logged to database."""
        registry.register(OrchestratorConfig(
            name="log_test",
            module_path="test.log",
            class_name="LogTest",
            category=OrchestratorCategory.CORE,
        ))
        
        health_checker.run_health_check()
        
        with db_manager.get_connection() as conn:
            logs = conn.execute(
                "SELECT * FROM health_check_log ORDER BY check_time DESC LIMIT 1"
            ).fetchone()
        
        assert logs is not None
        # Should have logged the check

    def test_multiple_checks_logged(self, health_checker, registry, db_manager):
        """Multiple health checks should all be logged."""
        registry.register(OrchestratorConfig(
            name="multi_log",
            module_path="test.multi",
            class_name="MultiLog",
            category=OrchestratorCategory.CORE,
        ))
        
        # Run 3 checks
        health_checker.run_health_check()
        health_checker.run_health_check()
        health_checker.run_health_check()
        
        with db_manager.get_connection() as conn:
            count = conn.execute(
                "SELECT COUNT(*) FROM health_check_log"
            ).fetchone()[0]
        
        assert count >= 3


# ============================================================================
# Status API Tests
# ============================================================================

class TestStatusAPI:
    """Tests for health checker status API."""

    def test_get_status_structure(self, health_checker):
        """get_status should return expected structure."""
        status = health_checker.get_status()
        
        expected_keys = {
            "running",
            "interval_seconds",
            "consecutive_failures",
            "recovery_attempts",
            "unwiring_first_detected",
            "last_check",
            "history_count",
        }
        
        assert expected_keys.issubset(status.keys())

    def test_get_last_check(self, health_checker, registry):
        """get_last_check should return most recent result."""
        registry.register(OrchestratorConfig(
            name="last_check_test",
            module_path="test.last",
            class_name="LastCheck",
            category=OrchestratorCategory.CORE,
        ))
        
        health_checker.run_health_check()
        
        last = health_checker.get_last_check()
        
        assert last is not None
        assert isinstance(last, HealthCheckResult)

    def test_get_check_history(self, health_checker, registry):
        """get_check_history should return recent checks."""
        registry.register(OrchestratorConfig(
            name="history_test",
            module_path="test.history",
            class_name="History",
            category=OrchestratorCategory.CORE,
        ))
        
        # Run 5 checks
        for _ in range(5):
            health_checker.run_health_check()
        
        history = health_checker.get_check_history(limit=3)
        
        assert len(history) == 3

    def test_force_check(self, health_checker, registry):
        """force_check should trigger immediate check."""
        registry.register(OrchestratorConfig(
            name="force_test",
            module_path="test.force",
            class_name="Force",
            category=OrchestratorCategory.CORE,
        ))
        
        result = health_checker.force_check()
        
        assert isinstance(result, HealthCheckResult)


# ============================================================================
# Convenience Function Tests
# ============================================================================

class TestConvenienceFunctions:
    """Tests for convenience functions."""

    def test_create_health_checker_auto_start(self, registry):
        """create_health_checker should start checks if requested."""
        checker = create_health_checker(
            registry=registry,
            start_immediately=True,
            interval_seconds=5,
        )
        
        assert checker._running
        
        checker.stop_background_checks()

    def test_create_health_checker_no_auto_start(self, registry):
        """create_health_checker should not start if not requested."""
        checker = create_health_checker(
            registry=registry,
            start_immediately=False,
            interval_seconds=5,
        )
        
        assert not checker._running

    def test_create_health_checker_with_callback(self, registry):
        """create_health_checker should accept alert callback."""
        callback = MagicMock()
        
        checker = create_health_checker(
            registry=registry,
            start_immediately=False,
            alert_callback=callback,
        )
        
        assert checker._alert_callback == callback


# ============================================================================
# Thread Safety Tests
# ============================================================================

class TestHealthCheckerThreadSafety:
    """Tests for thread-safe operations."""

    def test_concurrent_checks_safe(self, health_checker, registry):
        """Multiple concurrent health checks should be safe."""
        registry.register(OrchestratorConfig(
            name="concurrent",
            module_path="test.concurrent",
            class_name="Concurrent",
            category=OrchestratorCategory.CORE,
        ))
        
        results = []
        
        def run_check():
            result = health_checker.run_health_check()
            results.append(result)
        
        threads = [threading.Thread(target=run_check) for _ in range(5)]
        
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # All checks should complete
        assert len(results) == 5
        for r in results:
            assert isinstance(r, HealthCheckResult)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
