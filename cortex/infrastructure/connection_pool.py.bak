"""
Connection Pool with Health Checks (BRT-010)

Provides a thread-safe connection pool with passive health monitoring.
Manages connection lifecycle, detects stale connections, and tracks metrics.

Key Features:
- Thread-safe acquire/release with configurable timeout
- Passive health checks to detect and remove stale connections
- Comprehensive status reporting and monitoring
- Compatible with LifecycleManager (BRT-008) and RateLimiter (BRT-009)
- Simple, focused implementation (no adaptive recovery - see BRT-011)

CORE-CRIT-STATE-001: Thread-safe operations with RLock protecting shared state
"""

import logging
import threading
import time
from dataclasses import dataclass, field
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class InvalidConfigError(Exception):
    """Raised when pool configuration is invalid."""

    pass


class PoolExhaustedError(Exception):
    """Raised when no connections available and timeout exceeded."""

    pass


@dataclass
class Connection:
    """
    Represents a managed connection in the pool.
    
    Attributes:
        connection_id: Unique identifier for this connection
        pool: Reference to parent pool
        is_valid: Whether this connection is still valid
        created_at: Timestamp when connection was created
        last_used: Timestamp when connection was last used
    """

    connection_id: str
    """Unique identifier for this connection."""

    pool: "ConnectionPool"
    """Reference to parent pool."""

    is_valid: bool = True
    """Whether this connection is still valid."""

    created_at: float = field(default_factory=time.time)
    """Timestamp when connection was created."""

    last_used: float = field(default_factory=time.time)
    """Timestamp when connection was last used."""

    def __hash__(self) -> int:
        """Make connection hashable for set/dict operations."""
        return hash(self.connection_id)


class ConnectionPool:
    """
    Thread-safe connection pool with health monitoring.

    Manages a pool of connections with configurable capacity, timeout,
    and periodic health checks to detect stale connections.

    Usage:
        pool = ConnectionPool(capacity=10)
        conn = pool.acquire_connection()
        try:
            # use connection
            pass
        finally:
            pool.release_connection(conn)

    Args:
        capacity: Maximum number of connections in pool
        timeout: Max wait time in seconds for acquiring connection
        health_check_interval: Seconds between health check runs
    """

    def __init__(
        self,
        capacity: int,
        timeout: float = 30.0,
        health_check_interval: float = 60.0,
    ) -> None:
        """
        Initialize connection pool.

        Args:
            capacity: Must be > 0
            timeout: Must be > 0
            health_check_interval: Must be > 0

        Raises:
            InvalidConfigError: If any parameter is invalid
        """
        if capacity <= 0:
            raise InvalidConfigError("capacity must be > 0")
        if timeout <= 0:
            raise InvalidConfigError("timeout must be > 0")
        if health_check_interval <= 0:
            raise InvalidConfigError("health_check_interval must be > 0")

        self.capacity = capacity
        self.timeout = timeout
        self.health_check_interval = health_check_interval

        self._available_connections: list[Connection] = []
        self._all_connections: set[Connection] = set()
        self._lock = threading.RLock()
        self._not_empty = threading.Condition(self._lock)

        self._failed_checks = 0
        self._last_health_check = 0.0
        self._connection_counter = 0

        # Initialize pool with connections
        self._initialize_pool()

        logger.info(
            f"ConnectionPool initialized: capacity={capacity}, "
            f"timeout={timeout}s, health_check_interval={health_check_interval}s"
        )

    def _initialize_pool(self) -> None:
        """Initialize pool with available connections."""
        for _ in range(self.capacity):
            conn = self._create_connection()
            self._available_connections.append(conn)
            self._all_connections.add(conn)

    def _create_connection(self) -> Connection:
        """Create a new connection for the pool."""
        self._connection_counter += 1
        conn_id = f"conn-{self._connection_counter}"
        return Connection(connection_id=conn_id, pool=self)

    def acquire_connection(self) -> Connection:
        """
        Acquire a connection from the pool.

        Waits up to self.timeout seconds for a connection to become available.
        Only returns valid (non-stale) connections.

        Returns:
            Available Connection from the pool

        Raises:
            PoolExhaustedError: If no connection available within timeout
        """
        with self._not_empty:
            deadline = time.time() + self.timeout

            while True:
                # Try to get a valid connection
                valid_conns = [c for c in self._available_connections if c.is_valid]

                if valid_conns:
                    conn = valid_conns[0]
                    self._available_connections.remove(conn)
                    conn.last_used = time.time()
                    return conn

                # No valid connections, calculate wait time
                wait_time = deadline - time.time()
                if wait_time <= 0:
                    raise PoolExhaustedError(
                        f"No connections available after {self.timeout}s timeout "
                        f"(capacity={self.capacity})"
                    )

                # Wait for connection to be released
                self._not_empty.wait(timeout=min(wait_time, 0.1))

    def release_connection(self, conn: Connection) -> None:
        """
        Return a connection to the pool.

        Makes the connection available for reuse. If the connection is from
        a different pool or invalid, raises an error.

        Args:
            conn: Connection to return to pool

        Raises:
            ValueError: If connection is not from this pool
        """
        with self._lock:
            if conn not in self._all_connections:
                raise ValueError(
                    f"Connection {conn.connection_id} not from this pool"
                )

            # Only return valid connections to available pool
            if conn.is_valid:
                self._available_connections.append(conn)
                self._not_empty.notify()
            else:
                # Invalid connection, mark for removal (will be cleaned on health check)
                logger.debug(f"Not returning invalid connection {conn.connection_id}")

    def run_health_check(self) -> None:
        """
        Execute health check on all connections.

        Detects stale connections and removes them from the pool.
        Tracks health check failures for monitoring.

        This is a passive health check - it validates connections
        already in the pool. For active recovery, see BRT-011.
        """
        with self._lock:
            # Check available connections for staleness
            stale_conns = []

            for conn in self._available_connections:
                # Mark very old connections as stale (> 1 hour)
                age = time.time() - conn.created_at
                if age > 3600:
                    conn.is_valid = False
                    stale_conns.append(conn)

            # Remove stale connections from available pool
            for conn in stale_conns:
                if conn in self._available_connections:
                    self._available_connections.remove(conn)
                    self._failed_checks += 1
                    logger.debug(f"Removed stale connection {conn.connection_id}")

            self._last_health_check = time.time()

    def get_status(self) -> Dict[str, Any]:
        """
        Get current pool status and metrics.

        Returns:
            Dictionary with pool metrics:
            - capacity: Pool maximum size
            - available_connections: Currently available connections
            - total_connections: Total connections in pool
            - failed_checks: Cumulative failed health checks
            - last_health_check: Timestamp of last check (or 0.0)
        """
        with self._lock:
            return {
                "capacity": self.capacity,
                "available_connections": len(
                    [c for c in self._available_connections if c.is_valid]
                ),
                "total_connections": len(self._all_connections),
                "failed_checks": self._failed_checks,
                "last_health_check": self._last_health_check,
            }


# Module-level singleton instance
_connection_pool: Optional[ConnectionPool] = None
_pool_lock = threading.Lock()


def get_connection_pool(
    capacity: int = 10,
    timeout: float = 30.0,
    health_check_interval: float = 60.0,
) -> ConnectionPool:
    """
    Get or create thread-safe singleton connection pool.

    First call creates the pool with specified parameters.
    Subsequent calls return the existing instance (parameters ignored).

    Args:
        capacity: Initial pool capacity (default: 10)
        timeout: Acquire timeout in seconds (default: 30)
        health_check_interval: Health check interval in seconds (default: 60)

    Returns:
        The singleton ConnectionPool instance
    """
    global _connection_pool

    if _connection_pool is None:
        with _pool_lock:
            if _connection_pool is None:
                _connection_pool = ConnectionPool(
                    capacity=capacity,
                    timeout=timeout,
                    health_check_interval=health_check_interval,
                )

    return _connection_pool
