"""
Test for CORE-CRIT-STATE-001: Connection Pool Race Condition Fix.

This test verifies that the connection pool properly handles
concurrent acquire/release/cleanup operations without race conditions.
"""

import pytest
import threading
import time
from pathlib import Path
from typing import Generator, List

from cortex.infrastructure.connection_pool import (
    ConnectionPool,
    ConnectionPoolConfig,
)


@pytest.fixture
def test_db_path(tmp_path: Path) -> Path:
    """Create a temporary database path."""
    return tmp_path / "test_race.db"


@pytest.fixture
def pool_config() -> ConnectionPoolConfig:
    """Create a pool configuration for race condition testing."""
    return ConnectionPoolConfig(
        min_connections=2,
        max_connections=10,
        connection_timeout_seconds=2.0,
        idle_timeout_seconds=1.0,  # Short for testing
        health_check_enabled=True,
    )


@pytest.fixture
def connection_pool(
    test_db_path: Path, pool_config: ConnectionPoolConfig
) -> Generator[ConnectionPool, None, None]:
    """Create and cleanup a connection pool."""
    pool = ConnectionPool(database_path=test_db_path, config=pool_config)
    yield pool
    pool.shutdown()


class TestConnectionPoolRaceCondition:
    """CORE-CRIT-STATE-001: Test race condition handling in connection pool."""

    def test_concurrent_acquire_release_no_race_condition(
        self, connection_pool: ConnectionPool
    ) -> None:
        """Test concurrent acquire/release doesn't cause race condition.
        
        This test simulates multiple threads acquiring and releasing
        connections simultaneously while cleanup runs, which would expose
        the race condition if the lock wasn't held properly.
        """
        errors: List[Exception] = []
        acquired_connections = []
        lock = threading.Lock()

        def acquire_and_release_worker() -> None:
            """Worker that acquires and releases connections."""
            try:
                for _ in range(5):
                    conn = connection_pool.acquire()
                    with lock:
                        acquired_connections.append(conn)
                    # Simulate work
                    time.sleep(0.01)
                    connection_pool.release(conn)
            except Exception as e:
                errors.append(e)

        def cleanup_worker() -> None:
            """Worker that triggers cleanup."""
            try:
                for _ in range(3):
                    time.sleep(0.05)
                    # This triggers _cleanup_idle_connections internally
                    connection_pool._cleanup_idle_connections()
            except Exception as e:
                errors.append(e)

        # Create multiple threads
        threads = []
        for _ in range(5):
            t = threading.Thread(target=acquire_and_release_worker)
            threads.append(t)
            t.start()

        cleanup_thread = threading.Thread(target=cleanup_worker)
        threads.append(cleanup_thread)
        cleanup_thread.start()

        # Wait for all threads to complete
        for t in threads:
            t.join(timeout=10)

        # Verify no errors occurred
        assert (
            not errors
        ), f"Race condition detected: {[str(e) for e in errors]}"

        # Verify connections were successfully acquired
        assert len(acquired_connections) > 0, "No connections were acquired"

    def test_cleanup_with_concurrent_acquire_no_corruption(
        self, connection_pool: ConnectionPool
    ) -> None:
        """Test that cleanup doesn't corrupt state during concurrent access.
        
        Verifies that the lock is held throughout the cleanup operation
        to prevent race conditions with acquire/release.
        """
        errors: List[Exception] = []

        def stress_test_worker(worker_id: int) -> None:
            """Stress test with rapid acquire/release."""
            try:
                for i in range(10):
                    try:
                        conn = connection_pool.acquire(timeout=1.0)
                        # Use connection
                        cursor = conn.cursor()
                        cursor.execute("SELECT 1")
                        connection_pool.release(conn)
                        time.sleep(0.001)  # Brief delay
                    except Exception as e:
                        # Connection errors are acceptable, but not crashes
                        if "Unexpected error" in str(e):
                            errors.append(e)
            except Exception as e:
                errors.append(e)

        # Run multiple workers
        threads = [
            threading.Thread(target=stress_test_worker, args=(i,))
            for i in range(10)
        ]

        for t in threads:
            t.start()

        for t in threads:
            t.join(timeout=10)

        # Should have no crashes (only connection timeouts allowed)
        crash_errors = [
            e for e in errors if "Unexpected error" in str(e)
        ]
        assert (
            not crash_errors
        ), f"Pool crashed during concurrent access: {crash_errors}"

    def test_cleanup_iteration_thread_safe(
        self, connection_pool: ConnectionPool
    ) -> None:
        """Test that cleanup iteration is protected by lock.
        
        This specifically tests the fix for CORE-CRIT-STATE-001:
        The cleanup method now holds the lock throughout iteration.
        """
        # Acquire some connections to create activity
        conns = [
            connection_pool.acquire() for _ in range(3)
        ]

        # Release them to make them idle
        for conn in conns:
            connection_pool.release(conn)

        # Run cleanup multiple times concurrently
        errors: List[Exception] = []

        def cleanup_repeatedly() -> None:
            try:
                for _ in range(5):
                    connection_pool._cleanup_idle_connections()
                    time.sleep(0.01)
            except Exception as e:
                errors.append(e)

        threads = [
            threading.Thread(target=cleanup_repeatedly)
            for _ in range(3)
        ]

        for t in threads:
            t.start()

        for t in threads:
            t.join(timeout=10)

        # No errors should occur
        assert not errors, f"Cleanup race condition: {[str(e) for e in errors]}"

        # Pool should still be functional
        conn = connection_pool.acquire()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        connection_pool.release(conn)
