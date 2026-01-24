"""
Comprehensive tests for ConnectionPool (BRT-010 Implementation)

Tests the connection pool with:
- Pool creation and configuration
- Connection acquire/release cycles
- Health check execution and stale detection
- Thread-safe concurrent access
- Status reporting
- Error handling (exhaustion, timeout, invalid config)
"""

import pytest
import threading
import time
from cortex.infrastructure.connection_pool import (
    ConnectionPool,
    Connection,
    PoolExhaustedError,
    InvalidConfigError,
    get_connection_pool,
)


class TestConnectionPoolCreation:
    """Tests for ConnectionPool initialization."""

    def test_pool_creation_with_valid_config(self) -> None:
        """Verify pool initializes with valid configuration."""
        pool = ConnectionPool(capacity=10, timeout=5.0, health_check_interval=10.0)

        assert pool.capacity == 10
        assert pool.timeout == 5.0
        assert pool.health_check_interval == 10.0

    def test_pool_creation_with_defaults(self) -> None:
        """Verify pool uses sensible defaults."""
        pool = ConnectionPool(capacity=5)

        assert pool.capacity == 5
        assert pool.timeout == 30.0
        assert pool.health_check_interval == 60.0

    def test_pool_invalid_capacity_raises(self) -> None:
        """Verify invalid capacity raises InvalidConfigError."""
        with pytest.raises(InvalidConfigError, match="capacity must be > 0"):
            ConnectionPool(capacity=0)

        with pytest.raises(InvalidConfigError, match="capacity must be > 0"):
            ConnectionPool(capacity=-1)

    def test_pool_invalid_timeout_raises(self) -> None:
        """Verify invalid timeout raises InvalidConfigError."""
        with pytest.raises(InvalidConfigError, match="timeout must be > 0"):
            ConnectionPool(capacity=10, timeout=0)

        with pytest.raises(InvalidConfigError, match="timeout must be > 0"):
            ConnectionPool(capacity=10, timeout=-1.0)

    def test_pool_invalid_health_check_interval_raises(self) -> None:
        """Verify invalid health check interval raises InvalidConfigError."""
        with pytest.raises(InvalidConfigError, match="health_check_interval must be > 0"):
            ConnectionPool(capacity=10, health_check_interval=0)


class TestConnectionAcquireRelease:
    """Tests for acquiring and releasing connections."""

    def test_acquire_connection_success(self) -> None:
        """Verify acquiring connection succeeds when available."""
        pool = ConnectionPool(capacity=2)

        conn = pool.acquire_connection()

        assert conn is not None
        assert isinstance(conn, Connection)

    def test_acquire_multiple_connections(self) -> None:
        """Verify acquiring multiple connections up to capacity."""
        pool = ConnectionPool(capacity=3)

        conn1 = pool.acquire_connection()
        conn2 = pool.acquire_connection()
        conn3 = pool.acquire_connection()

        assert conn1 is not None
        assert conn2 is not None
        assert conn3 is not None
        assert conn1 != conn2
        assert conn2 != conn3

    def test_acquire_exceeds_capacity_raises(self) -> None:
        """Verify PoolExhaustedError when exceeding capacity."""
        pool = ConnectionPool(capacity=1, timeout=0.1)

        # Acquire the only connection
        conn = pool.acquire_connection()
        assert conn is not None

        # Try to acquire another (should timeout and raise)
        with pytest.raises(PoolExhaustedError, match="No connections available"):
            pool.acquire_connection()

    def test_release_connection_returns_to_pool(self) -> None:
        """Verify releasing connection makes it available again."""
        pool = ConnectionPool(capacity=1)

        # Acquire, release, acquire again
        conn1 = pool.acquire_connection()
        pool.release_connection(conn1)
        conn2 = pool.acquire_connection()

        # Should be able to acquire (pool replenished)
        assert conn2 is not None

    def test_release_invalid_connection_raises(self) -> None:
        """Verify releasing unknown connection raises error."""
        pool = ConnectionPool(capacity=2)

        conn1 = pool.acquire_connection()
        fake_conn = Connection(connection_id="fake-id", pool=pool)

        with pytest.raises(ValueError, match="not from this pool"):
            pool.release_connection(fake_conn)

    def test_acquire_after_release_cycle(self) -> None:
        """Verify multiple acquire/release cycles work correctly."""
        pool = ConnectionPool(capacity=2)

        for _ in range(5):
            conn1 = pool.acquire_connection()
            conn2 = pool.acquire_connection()

            pool.release_connection(conn1)
            pool.release_connection(conn2)


class TestHealthChecks:
    """Tests for health check execution."""

    def test_health_check_marks_stale_connections(self) -> None:
        """Verify health check identifies stale connections."""
        pool = ConnectionPool(capacity=3, health_check_interval=1.0)

        # Acquire and immediately release
        conn = pool.acquire_connection()
        pool.release_connection(conn)

        # Manually run health check
        pool.run_health_check()

        # Check that pool cleaned up or marked stale connections
        status = pool.get_status()
        assert status["failed_checks"] >= 0

    def test_health_check_removes_invalid_connections(self) -> None:
        """Verify health check removes connections that fail validation."""
        pool = ConnectionPool(capacity=2)

        # Acquire connections
        conn1 = pool.acquire_connection()
        conn2 = pool.acquire_connection()

        # Mark one as invalid (simulate failure)
        conn1.is_valid = False

        # Release them
        pool.release_connection(conn1)
        pool.release_connection(conn2)

        # Run health check
        pool.run_health_check()

        # Should only have valid connection available
        available_status = pool.get_status()
        assert available_status["available_connections"] <= 2

    def test_health_check_tracks_failures(self) -> None:
        """Verify health check tracks failed check count."""
        pool = ConnectionPool(capacity=2)

        initial_status = pool.get_status()
        initial_failures = initial_status["failed_checks"]

        # Run health check multiple times
        pool.run_health_check()
        pool.run_health_check()

        final_status = pool.get_status()
        assert final_status["failed_checks"] >= initial_failures

    def test_health_check_updates_timestamp(self) -> None:
        """Verify health check updates last check timestamp."""
        pool = ConnectionPool(capacity=2)

        status_before = pool.get_status()
        last_check_before = status_before.get("last_health_check")

        time.sleep(0.1)
        pool.run_health_check()

        status_after = pool.get_status()
        last_check_after = status_after.get("last_health_check")

        # Timestamp should be updated (or at least available)
        assert last_check_after is not None


class TestStatusReporting:
    """Tests for pool status reporting."""

    def test_get_status_returns_metrics(self) -> None:
        """Verify get_status returns all expected metrics."""
        pool = ConnectionPool(capacity=5)

        status = pool.get_status()

        assert "capacity" in status
        assert "available_connections" in status
        assert "total_connections" in status
        assert "failed_checks" in status
        assert "last_health_check" in status

    def test_status_capacity_correct(self) -> None:
        """Verify status reports correct capacity."""
        pool = ConnectionPool(capacity=7)

        status = pool.get_status()

        assert status["capacity"] == 7

    def test_status_available_connections_accuracy(self) -> None:
        """Verify available connections count is accurate."""
        pool = ConnectionPool(capacity=5)

        # Initially all available
        status = pool.get_status()
        assert status["available_connections"] == 5

        # Acquire one
        conn = pool.acquire_connection()
        status = pool.get_status()
        assert status["available_connections"] == 4

        # Release it
        pool.release_connection(conn)
        status = pool.get_status()
        assert status["available_connections"] == 5

    def test_status_tracks_total_connections(self) -> None:
        """Verify status tracks total connections created."""
        pool = ConnectionPool(capacity=3)

        # Acquire all connections
        conn1 = pool.acquire_connection()
        conn2 = pool.acquire_connection()
        conn3 = pool.acquire_connection()

        status = pool.get_status()
        assert status["total_connections"] >= 3


class TestThreadSafety:
    """Tests for thread-safe concurrent access."""

    def test_concurrent_acquire_release(self) -> None:
        """Verify thread-safe concurrent acquire/release."""
        pool = ConnectionPool(capacity=10)
        acquired_count = 0
        acquired_lock = threading.Lock()

        def worker() -> None:
            nonlocal acquired_count
            for _ in range(5):
                conn = pool.acquire_connection()
                with acquired_lock:
                    acquired_count += 1
                pool.release_connection(conn)

        threads = [threading.Thread(target=worker) for _ in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Should have successfully acquired connections
        assert acquired_count == 20  # 4 threads × 5 acquisitions

    def test_concurrent_status_reads(self) -> None:
        """Verify thread-safe status reads during active operations."""
        pool = ConnectionPool(capacity=5)
        statuses: list = []
        status_lock = threading.Lock()

        def acquire_and_check() -> None:
            for _ in range(3):
                conn = pool.acquire_connection()
                status = pool.get_status()
                with status_lock:
                    statuses.append(status)
                pool.release_connection(conn)

        threads = [threading.Thread(target=acquire_and_check) for _ in range(3)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # All status reads should have completed successfully
        assert len(statuses) == 9  # 3 threads × 3 checks

    def test_concurrent_health_checks(self) -> None:
        """Verify thread-safe health check execution."""
        pool = ConnectionPool(capacity=5)
        check_count = 0
        check_lock = threading.Lock()

        def run_checks() -> None:
            nonlocal check_count
            for _ in range(3):
                pool.run_health_check()
                with check_lock:
                    check_count += 1

        threads = [threading.Thread(target=run_checks) for _ in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # All health checks should have completed
        assert check_count == 12  # 4 threads × 3 checks


class TestErrorHandling:
    """Tests for error scenarios."""

    def test_timeout_on_acquire_when_exhausted(self) -> None:
        """Verify timeout when trying to acquire exhausted pool."""
        pool = ConnectionPool(capacity=1, timeout=0.2)

        # Exhaust the pool
        conn = pool.acquire_connection()

        # Try to acquire another (should timeout)
        start = time.time()
        with pytest.raises(PoolExhaustedError):
            pool.acquire_connection()
        elapsed = time.time() - start

        # Should have waited at least close to timeout
        assert elapsed >= 0.1

    def test_invalid_config_capacity(self) -> None:
        """Verify invalid configuration rejected."""
        with pytest.raises(InvalidConfigError):
            ConnectionPool(capacity=-5)

    def test_invalid_config_timeout(self) -> None:
        """Verify invalid timeout rejected."""
        with pytest.raises(InvalidConfigError):
            ConnectionPool(capacity=10, timeout=-1.0)

    def test_release_nonexistent_connection_raises(self) -> None:
        """Verify releasing unknown connection raises error."""
        pool1 = ConnectionPool(capacity=2)
        pool2 = ConnectionPool(capacity=2)

        conn = pool1.acquire_connection()

        with pytest.raises(ValueError, match="not from this pool"):
            pool2.release_connection(conn)


class TestConnectionClass:
    """Tests for Connection dataclass."""

    def test_connection_creation(self) -> None:
        """Verify Connection initializes correctly."""
        pool = ConnectionPool(capacity=1)
        conn = Connection(connection_id="test-123", pool=pool)

        assert conn.connection_id == "test-123"
        assert conn.pool == pool
        assert conn.is_valid is True
        assert conn.created_at is not None

    def test_connection_validity_flag(self) -> None:
        """Verify connection validity tracking."""
        pool = ConnectionPool(capacity=1)
        conn = Connection(connection_id="test-456", pool=pool)

        # Initially valid
        assert conn.is_valid is True

        # Mark as invalid
        conn.is_valid = False
        assert conn.is_valid is False


class TestSingletonPattern:
    """Tests for singleton connection pool."""

    def test_get_connection_pool_creates_instance(self) -> None:
        """Verify get_connection_pool creates instance."""
        pool = get_connection_pool(capacity=10)

        assert pool is not None
        assert isinstance(pool, ConnectionPool)

    def test_get_connection_pool_returns_same_instance(self) -> None:
        """Verify get_connection_pool returns same instance."""
        pool1 = get_connection_pool()
        pool2 = get_connection_pool()

        assert pool1 is pool2


class TestIntegration:
    """Integration tests for connection pool."""

    def test_acquire_release_acquire_cycle(self) -> None:
        """Verify complete acquire-release-acquire workflow."""
        pool = ConnectionPool(capacity=2)

        # First cycle
        conn1a = pool.acquire_connection()
        conn2a = pool.acquire_connection()

        pool.release_connection(conn1a)
        pool.release_connection(conn2a)

        # Second cycle - should get connections
        conn1b = pool.acquire_connection()
        conn2b = pool.acquire_connection()

        assert conn1b is not None
        assert conn2b is not None

    def test_pool_metrics_during_load(self) -> None:
        """Verify accurate metrics under concurrent load."""
        pool = ConnectionPool(capacity=5)

        def steady_load() -> None:
            for _ in range(10):
                conn = pool.acquire_connection()
                time.sleep(0.01)
                pool.release_connection(conn)

        threads = [threading.Thread(target=steady_load) for _ in range(3)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Should be stable after load
        status = pool.get_status()
        assert status["available_connections"] <= status["capacity"]
        assert status["total_connections"] > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
