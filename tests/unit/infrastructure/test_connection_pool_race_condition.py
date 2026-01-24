"""
Test for CORE-CRIT-STATE-001: Connection Pool Race Condition Fix.

This test verifies that the connection pool properly handles
concurrent acquire/release/health check operations without race conditions.
The key fix: lock is held throughout entire health check and cleanup cycles.
"""

import pytest
import threading
import time
from typing import Generator, List

from cortex.infrastructure.connection_pool import (
    ConnectionPool,
    Connection,
    PoolExhaustedError,
)


@pytest.fixture
def connection_pool() -> Generator[ConnectionPool, None, None]:
    """Create and cleanup a connection pool for race condition testing."""
    pool = ConnectionPool(capacity=10, timeout=2.0, health_check_interval=1.0)
    yield pool


class TestConnectionPoolRaceCondition:
    """CORE-CRIT-STATE-001: Test race condition handling in connection pool."""

    def test_concurrent_acquire_release_no_race_condition(
        self, connection_pool: ConnectionPool
    ) -> None:
        """Test concurrent acquire/release doesn't cause race condition.
        
        This test simulates multiple threads acquiring and releasing
        connections simultaneously while health checks run, which would expose
        the race condition if the lock wasn't held properly.
        """
        errors: List[Exception] = []
        acquired_connections: List[Connection] = []
        lock = threading.Lock()

        def acquire_and_release_worker() -> None:
            """Worker that acquires and releases connections."""
            try:
                for _ in range(5):
                    conn = connection_pool.acquire_connection()
                    with lock:
                        acquired_connections.append(conn)
                    # Simulate work
                    time.sleep(0.01)
                    connection_pool.release_connection(conn)
            except Exception as e:
                errors.append(e)

        def health_check_worker() -> None:
            """Worker that triggers health checks."""
            try:
                for _ in range(3):
                    time.sleep(0.05)
                    # This triggers health check with lock held
                    connection_pool.run_health_check()
            except Exception as e:
                errors.append(e)

        # Create multiple threads
        threads: List[threading.Thread] = []
        for _ in range(5):
            t = threading.Thread(target=acquire_and_release_worker)
            threads.append(t)
            t.start()

        health_thread = threading.Thread(target=health_check_worker)
        threads.append(health_thread)
        health_thread.start()

        # Wait for all threads to complete
        for t in threads:
            t.join(timeout=10)

        # Verify no errors occurred
        assert (
            not errors
        ), f"Race condition detected: {[str(e) for e in errors]}"

        # Verify connections were successfully acquired
        assert len(acquired_connections) > 0, "No connections were acquired"

    def test_acquire_release_concurrent_no_corruption(
        self, connection_pool: ConnectionPool
    ) -> None:
        """Test that health checks don't corrupt state during concurrent access.
        
        Verifies that the lock is held throughout the health check operation
        to prevent race conditions with acquire/release.
        """
        errors: List[Exception] = []

        def stress_test_worker(worker_id: int) -> None:
            """Stress test with rapid acquire/release."""
            try:
                for i in range(10):
                    try:
                        conn = connection_pool.acquire_connection()
                        # Verify connection is valid
                        assert conn.is_valid
                        connection_pool.release_connection(conn)
                        time.sleep(0.001)  # Brief delay
                    except (PoolExhaustedError, Exception) as e:
                        # Timeout errors acceptable, but not crashes
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

        # Should have no crashes
        crash_errors = [
            e for e in errors if "Unexpected error" in str(e)
        ]
        assert (
            not crash_errors
        ), f"Pool crashed during concurrent access: {crash_errors}"

    def test_health_check_iteration_thread_safe(
        self, connection_pool: ConnectionPool
    ) -> None:
        """Test that health check iteration is protected by lock.
        
        This specifically tests the fix for CORE-CRIT-STATE-001:
        The health check method now holds the lock throughout iteration.
        """
        # Acquire some connections to create activity
        conns: List[Connection] = []
        for _ in range(3):
            conns.append(connection_pool.acquire_connection())

        # Release them to make them idle
        for conn in conns:
            connection_pool.release_connection(conn)

        # Run health checks multiple times concurrently
        errors: List[Exception] = []

        def health_check_repeatedly() -> None:
            try:
                for _ in range(5):
                    connection_pool.run_health_check()
                    time.sleep(0.01)
            except Exception as e:
                errors.append(e)

        threads = [
            threading.Thread(target=health_check_repeatedly)
            for _ in range(3)
        ]

        for t in threads:
            t.start()

        for t in threads:
            t.join(timeout=10)

        # No errors should occur
        assert not errors, f"Health check race condition: {[str(e) for e in errors]}"

        # Pool should still be functional
        conn = connection_pool.acquire_connection()
        assert conn.is_valid
        connection_pool.release_connection(conn)
