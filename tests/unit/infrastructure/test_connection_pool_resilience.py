"""
Tests for Connection Pool with Lifecycle Management.

AC-INFRA-001-01: Connection Pool with Lifecycle Management
Tests connection pooling with configurable min/max connections,
timeout handling, health checks, and automatic cleanup.
"""

import pytest
import sqlite3
import threading
import time
from pathlib import Path
from typing import Generator
from unittest.mock import Mock, patch

from cortex.infrastructure.connection_pool import (
    ConnectionPool,
    ConnectionPoolConfig,
    PoolExhaustedError,
    ConnectionHealthCheckFailedError,
)


@pytest.fixture
def test_db_path(tmp_path: Path) -> Path:
    """Create a temporary database path."""
    return tmp_path / "test.db"


@pytest.fixture
def pool_config() -> ConnectionPoolConfig:
    """Create a standard pool configuration for testing."""
    return ConnectionPoolConfig(
        min_connections=2,
        max_connections=5,
        connection_timeout_seconds=1.0,
        idle_timeout_seconds=5.0,
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


class TestConnectionPoolInitialization:
    """Test connection pool initialization and configuration."""

    def test_pool_creates_min_connections_on_init(
        self, test_db_path: Path, pool_config: ConnectionPoolConfig
    ) -> None:
        """Pool should create minimum connections during initialization."""
        pool = ConnectionPool(database_path=test_db_path, config=pool_config)
        try:
            metrics = pool.get_metrics()
            assert metrics["idle"] >= pool_config.min_connections
            assert metrics["total"] >= pool_config.min_connections
        finally:
            pool.shutdown()

    def test_pool_respects_max_connections_limit(
        self, connection_pool: ConnectionPool, pool_config: ConnectionPoolConfig
    ) -> None:
        """Pool should not exceed max connections."""
        connections = []
        for _ in range(pool_config.max_connections):
            connections.append(connection_pool.acquire())
        
        with pytest.raises(PoolExhaustedError):
            connection_pool.acquire(timeout=0.5)
        
        for conn in connections:
            connection_pool.release(conn)

    def test_pool_config_validation(self, test_db_path: Path) -> None:
        """Pool should validate configuration parameters."""
        with pytest.raises(ValueError, match="min_connections must be positive"):
            ConnectionPoolConfig(min_connections=0, max_connections=5)
        
        with pytest.raises(ValueError, match="max_connections must be >= min_connections"):
            ConnectionPoolConfig(min_connections=5, max_connections=2)


class TestConnectionAcquisitionAndRelease:
    """Test connection acquisition and release lifecycle."""

    def test_acquire_returns_valid_connection(
        self, connection_pool: ConnectionPool
    ) -> None:
        """Acquired connection should be usable."""
        conn = connection_pool.acquire()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            assert cursor.fetchone()[0] == 1
        finally:
            connection_pool.release(conn)

    def test_release_returns_connection_to_pool(
        self, connection_pool: ConnectionPool
    ) -> None:
        """Released connection should be reused."""
        initial_total = connection_pool.get_metrics()["total"]
        
        conn1 = connection_pool.acquire()
        connection_pool.release(conn1)
        
        conn2 = connection_pool.acquire()
        connection_pool.release(conn2)
        
        # Pool should not grow if connections are being reused
        final_total = connection_pool.get_metrics()["total"]
        assert final_total == initial_total, "Pool should reuse connections, not create new ones"

    def test_acquire_blocks_when_pool_exhausted(
        self, connection_pool: ConnectionPool, pool_config: ConnectionPoolConfig
    ) -> None:
        """Acquire should block when pool exhausted, unblock on release."""
        # Exhaust the pool
        connections = [
            connection_pool.acquire() for _ in range(pool_config.max_connections)
        ]
        
        acquired = []
        def acquire_delayed():
            acquired.append(connection_pool.acquire(timeout=2.0))
        
        thread = threading.Thread(target=acquire_delayed)
        thread.start()
        
        time.sleep(0.1)  # Let thread block
        connection_pool.release(connections[0])  # Release one
        thread.join(timeout=2.0)
        
        assert len(acquired) == 1, "Should acquire after release"
        connection_pool.release(acquired[0])
        for conn in connections[1:]:
            connection_pool.release(conn)

    def test_acquire_timeout_raises_error(
        self, connection_pool: ConnectionPool, pool_config: ConnectionPoolConfig
    ) -> None:
        """Acquire should raise PoolExhaustedError on timeout."""
        connections = [
            connection_pool.acquire() for _ in range(pool_config.max_connections)
        ]
        
        with pytest.raises(PoolExhaustedError, match="timeout"):
            connection_pool.acquire(timeout=0.1)
        
        for conn in connections:
            connection_pool.release(conn)


class TestConnectionHealthChecks:
    """Test connection health checking functionality."""

    def test_health_check_detects_closed_connection(
        self, connection_pool: ConnectionPool
    ) -> None:
        """Health check should detect closed connections."""
        conn = connection_pool.acquire()
        conn.close()  # Manually close
        
        # Pool should detect closed connection on next acquire
        with pytest.raises(ConnectionHealthCheckFailedError):
            connection_pool.release(conn)

    def test_health_check_validates_before_reuse(
        self, connection_pool: ConnectionPool
    ) -> None:
        """Pool should run health check before reusing connection."""
        conn = connection_pool.acquire()
        connection_pool.release(conn)
        
        # Next acquire should validate health
        conn2 = connection_pool.acquire()
        assert conn2 is not None
        connection_pool.release(conn2)

    def test_failed_health_check_creates_new_connection(
        self, connection_pool: ConnectionPool, pool_config: ConnectionPoolConfig
    ) -> None:
        """Failed health check should trigger new connection creation."""
        initial_total = connection_pool.get_metrics()["total"]
        
        conn = connection_pool.acquire()
        conn.close()  # Break the connection
        
        # Release should raise error for failed health check
        try:
            connection_pool.release(conn)
        except ConnectionHealthCheckFailedError:
            pass  # Expected
        
        # Next acquire should work with a new connection
        conn2 = connection_pool.acquire()
        assert conn2 is not None
        connection_pool.release(conn2)
        
        # Pool may have same or more connections (one was closed, new one created)
        final_total = connection_pool.get_metrics()["total"]
        assert final_total >= initial_total - 1


class TestIdleConnectionCleanup:
    """Test automatic cleanup of idle connections."""

    def test_idle_connections_cleaned_after_timeout(
        self, test_db_path: Path
    ) -> None:
        """Connections idle longer than timeout should be cleaned up."""
        config = ConnectionPoolConfig(
            min_connections=2,
            max_connections=5,
            idle_timeout_seconds=0.5,  # Short timeout for testing
        )
        pool = ConnectionPool(database_path=test_db_path, config=config)
        
        try:
            # Create extra connections
            connections = [pool.acquire() for _ in range(4)]
            for conn in connections:
                pool.release(conn)
            
            initial_metrics = pool.get_metrics()
            
            # Wait for idle cleanup
            time.sleep(1.0)
            pool._cleanup_idle_connections()
            
            final_metrics = pool.get_metrics()
            assert final_metrics["total"] <= initial_metrics["total"]
            assert final_metrics["idle"] <= initial_metrics["idle"]
        finally:
            pool.shutdown()

    def test_min_connections_never_cleaned(
        self, test_db_path: Path
    ) -> None:
        """Pool should maintain minimum connections even when idle."""
        config = ConnectionPoolConfig(
            min_connections=2,
            max_connections=5,
            idle_timeout_seconds=0.1,
        )
        pool = ConnectionPool(database_path=test_db_path, config=config)
        
        try:
            time.sleep(0.5)
            pool._cleanup_idle_connections()
            
            metrics = pool.get_metrics()
            assert metrics["total"] >= config.min_connections
        finally:
            pool.shutdown()


class TestContextManagerSupport:
    """Test connection pool context manager functionality."""

    def test_context_manager_acquires_and_releases(
        self, connection_pool: ConnectionPool
    ) -> None:
        """Context manager should acquire and automatically release."""
        initial_metrics = connection_pool.get_metrics()
        
        with connection_pool.connection() as conn:
            assert conn is not None
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
        
        final_metrics = connection_pool.get_metrics()
        assert final_metrics["active"] == initial_metrics["active"]

    def test_context_manager_releases_on_exception(
        self, connection_pool: ConnectionPool
    ) -> None:
        """Context manager should release connection even on exception."""
        initial_metrics = connection_pool.get_metrics()
        
        try:
            with connection_pool.connection() as conn:
                raise ValueError("Test exception")
        except ValueError:
            pass
        
        final_metrics = connection_pool.get_metrics()
        assert final_metrics["active"] == initial_metrics["active"]

    def test_nested_context_managers(
        self, connection_pool: ConnectionPool
    ) -> None:
        """Multiple nested context managers should work correctly."""
        with connection_pool.connection() as conn1:
            with connection_pool.connection() as conn2:
                assert conn1 is not conn2
                assert conn1 is not None
                assert conn2 is not None


class TestPoolMetrics:
    """Test connection pool metrics reporting."""

    def test_metrics_track_active_connections(
        self, connection_pool: ConnectionPool
    ) -> None:
        """Metrics should accurately track active connections."""
        initial = connection_pool.get_metrics()["active"]
        
        conn1 = connection_pool.acquire()
        assert connection_pool.get_metrics()["active"] == initial + 1
        
        conn2 = connection_pool.acquire()
        assert connection_pool.get_metrics()["active"] == initial + 2
        
        connection_pool.release(conn1)
        assert connection_pool.get_metrics()["active"] == initial + 1
        
        connection_pool.release(conn2)
        assert connection_pool.get_metrics()["active"] == initial

    def test_metrics_track_idle_connections(
        self, connection_pool: ConnectionPool
    ) -> None:
        """Metrics should accurately track idle connections."""
        conn = connection_pool.acquire()
        active_before = connection_pool.get_metrics()["active"]
        
        connection_pool.release(conn)
        idle_after = connection_pool.get_metrics()["idle"]
        
        assert idle_after > 0

    def test_metrics_track_wait_time(
        self, connection_pool: ConnectionPool, pool_config: ConnectionPoolConfig
    ) -> None:
        """Metrics should track connection wait time."""
        # Exhaust pool
        connections = [
            connection_pool.acquire() for _ in range(pool_config.max_connections)
        ]
        
        start = time.time()
        
        def delayed_acquire():
            time.sleep(0.1)
            connection_pool.release(connections[0])
        
        thread = threading.Thread(target=delayed_acquire)
        thread.start()
        
        conn = connection_pool.acquire(timeout=1.0)
        wait_time = time.time() - start
        
        thread.join()
        connection_pool.release(conn)
        for c in connections[1:]:
            connection_pool.release(c)
        
        metrics = connection_pool.get_metrics()
        assert "avg_wait_time_ms" in metrics
        assert metrics["avg_wait_time_ms"] > 0


class TestConcurrentAccess:
    """Test connection pool under concurrent access."""

    def test_concurrent_acquire_release(
        self, connection_pool: ConnectionPool
    ) -> None:
        """Pool should handle concurrent acquire/release correctly."""
        errors = []
        
        def worker():
            try:
                for _ in range(10):
                    conn = connection_pool.acquire()
                    time.sleep(0.01)  # Simulate work
                    connection_pool.release(conn)
            except Exception as e:
                errors.append(e)
        
        threads = [threading.Thread(target=worker) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        assert len(errors) == 0, f"Concurrent access errors: {errors}"

    def test_no_connection_leaks_under_load(
        self, connection_pool: ConnectionPool
    ) -> None:
        """Pool should not leak connections under high concurrent load."""
        initial_metrics = connection_pool.get_metrics()
        
        def worker():
            for _ in range(100):
                with connection_pool.connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT 1")
        
        threads = [threading.Thread(target=worker) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        final_metrics = connection_pool.get_metrics()
        assert final_metrics["active"] == initial_metrics["active"]
        assert final_metrics["total"] <= initial_metrics["total"] + 2  # Allow some growth


class TestShutdownAndCleanup:
    """Test pool shutdown and resource cleanup."""

    def test_shutdown_closes_all_connections(
        self, test_db_path: Path, pool_config: ConnectionPoolConfig
    ) -> None:
        """Shutdown should close all connections."""
        pool = ConnectionPool(database_path=test_db_path, config=pool_config)
        
        # Acquire some connections
        connections = [pool.acquire() for _ in range(3)]
        for conn in connections:
            pool.release(conn)
        
        pool.shutdown()
        
        metrics = pool.get_metrics()
        assert metrics["total"] == 0
        assert metrics["active"] == 0
        assert metrics["idle"] == 0

    def test_shutdown_within_timeout(
        self, test_db_path: Path, pool_config: ConnectionPoolConfig
    ) -> None:
        """Shutdown should complete within timeout."""
        pool = ConnectionPool(database_path=test_db_path, config=pool_config)
        
        start = time.time()
        pool.shutdown(timeout=5.0)
        duration = time.time() - start
        
        assert duration < 5.0

    def test_acquire_after_shutdown_raises_error(
        self, connection_pool: ConnectionPool
    ) -> None:
        """Acquire after shutdown should raise error."""
        connection_pool.shutdown()
        
        with pytest.raises(RuntimeError, match="shutdown"):
            connection_pool.acquire()
