"""
Connection Pool with Lifecycle Management.

AC-INFRA-001-01: Implements production-grade connection pooling with:
- Configurable min/max connections
- Health checks before reuse
- Automatic cleanup of idle connections
- Context manager support
- Comprehensive metrics

CORE-CRIT-STATE-001: Thread-safe operations with RLock protecting shared state
"""

import logging
import sqlite3
import threading
import time
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional, Any
from queue import Queue, Empty


class PoolExhaustedError(Exception):
    """Raised when connection pool is exhausted and timeout expires."""
    pass


class ConnectionHealthCheckFailedError(Exception):
    """Raised when connection health check fails."""
    pass


@dataclass
class ConnectionPoolConfig:
    """Configuration for connection pool."""
    
    min_connections: int = 2
    max_connections: int = 20
    connection_timeout_seconds: float = 30.0
    idle_timeout_seconds: float = 300.0  # 5 minutes
    health_check_enabled: bool = True
    
    def __post_init__(self) -> None:
        """Validate configuration parameters."""
        if self.min_connections <= 0:
            raise ValueError("min_connections must be positive")
        if self.max_connections < self.min_connections:
            raise ValueError("max_connections must be >= min_connections")
        if self.connection_timeout_seconds <= 0:
            raise ValueError("connection_timeout_seconds must be positive")
        if self.idle_timeout_seconds <= 0:
            raise ValueError("idle_timeout_seconds must be positive")


@dataclass
class _ConnectionWrapper:
    """Wrapper for tracking connection metadata."""
    
    connection: sqlite3.Connection
    last_used: float
    in_use: bool = False


class ConnectionPool:
    """
    Production-grade connection pool with lifecycle management.
    
    Features:
    - Min/max connection limits
    - Health checks before reuse
    - Automatic idle connection cleanup
    - Context manager support
    - Thread-safe operations
    - Comprehensive metrics
    
    Example:
        >>> config = ConnectionPoolConfig(min_connections=2, max_connections=10)
        >>> pool = ConnectionPool(Path("db.sqlite"), config)
        >>> with pool.connection() as conn:
        ...     cursor = conn.cursor()
        ...     cursor.execute("SELECT 1")
        >>> pool.shutdown()
    """
    
    def __init__(
        self,
        database_path: Path,
        config: Optional[ConnectionPoolConfig] = None,
    ) -> None:
        """
        Initialize connection pool.
        
        Args:
            database_path: Path to SQLite database file
            config: Pool configuration (uses defaults if None)
        """
        self.database_path = database_path
        self.config = config or ConnectionPoolConfig()
        
        self._lock = threading.RLock()
        self._available: Queue[_ConnectionWrapper] = Queue()
        self._all_connections: Dict[int, _ConnectionWrapper] = {}
        self._shutdown_flag = False
        
        # Metrics tracking
        self._wait_times: list[float] = []
        self._total_acquires = 0
        
        # Initialize minimum connections
        self._initialize_pool()
    
    def _initialize_pool(self) -> None:
        """Create minimum connections during initialization."""
        with self._lock:
            for _ in range(self.config.min_connections):
                wrapper = self._create_connection()
                self._all_connections[id(wrapper.connection)] = wrapper
                self._available.put(wrapper)
    
    def _create_connection(self) -> _ConnectionWrapper:
        """
        Create a new database connection.
        
        Returns:
            Wrapped connection with metadata
        """
        conn = sqlite3.connect(
            str(self.database_path),
            timeout=self.config.connection_timeout_seconds,
            check_same_thread=False,
        )
        # Enable WAL mode for better concurrency
        conn.execute("PRAGMA journal_mode=WAL")
        
        return _ConnectionWrapper(
            connection=conn,
            last_used=time.time(),
            in_use=False,
        )
    
    def _health_check(self, conn: sqlite3.Connection) -> bool:
        """
        Check if connection is healthy.
        
        Args:
            conn: Connection to check
            
        Returns:
            True if healthy, False otherwise
        """
        if not self.config.health_check_enabled:
            return True
        
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            return True
        except (sqlite3.Error, AttributeError):
            return False
    
    def acquire(self, timeout: Optional[float] = None) -> sqlite3.Connection:
        """
        Acquire a connection from the pool.
        
        Args:
            timeout: Maximum time to wait for connection (uses config default if None)
            
        Returns:
            Database connection
            
        Raises:
            PoolExhaustedError: If pool exhausted and timeout expires
            RuntimeError: If pool is shutdown
        """
        if self._shutdown_flag:
            raise RuntimeError("Connection pool is shutdown")
        
        timeout = timeout if timeout is not None else self.config.connection_timeout_seconds
        start_time = time.time()
        
        with self._lock:
            self._total_acquires += 1
        
        while True:
            wait_time = time.time() - start_time
            remaining_timeout = timeout - wait_time
            
            if remaining_timeout <= 0:
                raise PoolExhaustedError(
                    f"Connection pool exhausted after {timeout}s timeout"
                )
            
            try:
                # Try to get available connection
                wrapper = self._available.get(timeout=min(remaining_timeout, 0.1))
                
                # Validate health
                if self._health_check(wrapper.connection):
                    with self._lock:
                        wrapper.in_use = True
                        wrapper.last_used = time.time()
                        self._wait_times.append(wait_time)
                        if len(self._wait_times) > 1000:
                            self._wait_times = self._wait_times[-1000:]
                    return wrapper.connection
                else:
                    # Connection unhealthy, try to replace it
                    self._close_connection(wrapper)
                    with self._lock:
                        if len(self._all_connections) < self.config.max_connections:
                            new_wrapper = self._create_connection()
                            self._all_connections[id(new_wrapper.connection)] = new_wrapper
                            self._available.put(new_wrapper)
                    
            except Empty:
                # No available connections, try to create new one
                with self._lock:
                    if len(self._all_connections) < self.config.max_connections:
                        wrapper = self._create_connection()
                        self._all_connections[id(wrapper.connection)] = wrapper
                        wrapper.in_use = True
                        wrapper.last_used = time.time()
                        return wrapper.connection
                
                # Pool at max capacity, continue waiting
                continue
    
    def release(self, conn: sqlite3.Connection) -> None:
        """
        Release a connection back to the pool.
        
        Args:
            conn: Connection to release
            
        Raises:
            ConnectionHealthCheckFailedError: If connection fails health check
        """
        if self._shutdown_flag:
            self._close_connection_by_ref(conn)
            return
        
        conn_id = id(conn)
        
        with self._lock:
            wrapper = self._all_connections.get(conn_id)
            if wrapper is None:
                return  # Connection not from this pool
            
            # Health check before returning to pool
            if not self._health_check(conn):
                self._close_connection(wrapper)
                raise ConnectionHealthCheckFailedError(
                    "Connection failed health check on release"
                )
            
            wrapper.in_use = False
            wrapper.last_used = time.time()
            self._available.put(wrapper)
    
    def _cleanup_idle_connections(self) -> None:
        """Clean up connections idle longer than timeout."""
        if self._shutdown_flag:
            return
        
        current_time = time.time()
        idle_timeout = self.config.idle_timeout_seconds
        
        with self._lock:
            # Don't cleanup if at minimum
            if len(self._all_connections) <= self.config.min_connections:
                return
            
            # Find idle connections to cleanup
            to_cleanup = []
            temp_available = []
            
            while not self._available.empty():
                try:
                    wrapper = self._available.get_nowait()
                    # CORE-CRIT-STATE-001: Check idle status while holding lock
                    # to prevent race condition between check and cleanup
                    if (current_time - wrapper.last_used > idle_timeout and
                        len(self._all_connections) > self.config.min_connections and
                        not wrapper.in_use):  # Additional safety check
                        to_cleanup.append(wrapper)
                    else:
                        temp_available.append(wrapper)
                except Empty:
                    break
            
            # Return non-cleaned connections to queue
            for wrapper in temp_available:
                self._available.put(wrapper)
            
            # Close idle connections - lock held throughout ensures
            # no concurrent access to _all_connections dict
            for wrapper in to_cleanup:
                self._close_connection(wrapper)
    
    def _close_connection(self, wrapper: _ConnectionWrapper) -> None:
        """Close a connection and remove from pool."""
        try:
            wrapper.connection.close()
        except sqlite3.Error as e:
            logging.warning(f"Error closing connection: {e}")
        except Exception as e:
            logging.error(f"Unexpected error closing connection: {e}")
        
        conn_id = id(wrapper.connection)
        if conn_id in self._all_connections:
            del self._all_connections[conn_id]
    
    def _close_connection_by_ref(self, conn: sqlite3.Connection) -> None:
        """Close a connection by reference."""
        conn_id = id(conn)
        wrapper = self._all_connections.get(conn_id)
        if wrapper:
            self._close_connection(wrapper)
    
    @contextmanager
    def connection(self, timeout: Optional[float] = None):
        """
        Context manager for acquiring and releasing connections.
        
        Args:
            timeout: Maximum time to wait for connection
            
        Yields:
            Database connection
            
        Example:
            >>> with pool.connection() as conn:
            ...     cursor = conn.cursor()
            ...     cursor.execute("SELECT 1")
        """
        conn = self.acquire(timeout=timeout)
        try:
            yield conn
        finally:
            try:
                self.release(conn)
            except ConnectionHealthCheckFailedError:
                pass  # Already handled in release
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get pool metrics.
        
        Returns:
            Dictionary with metrics:
            - total: Total connections
            - active: Connections in use
            - idle: Connections available
            - avg_wait_time_ms: Average wait time in milliseconds
        """
        with self._lock:
            active = sum(1 for w in self._all_connections.values() if w.in_use)
            total = len(self._all_connections)
            idle = total - active
            
            avg_wait_time_ms = 0.0
            if self._wait_times:
                avg_wait_time_ms = (sum(self._wait_times) / len(self._wait_times)) * 1000
            
            return {
                "total": total,
                "active": active,
                "idle": idle,
                "avg_wait_time_ms": avg_wait_time_ms,
                "total_acquires": self._total_acquires,
            }
    
    def shutdown(self, timeout: float = 5.0) -> None:
        """
        Shutdown the connection pool.
        
        Closes all connections and prevents new acquisitions.
        
        Args:
            timeout: Maximum time to wait for shutdown
        """
        with self._lock:
            self._shutdown_flag = True
            
            # Close all connections
            for wrapper in list(self._all_connections.values()):
                try:
                    wrapper.connection.close()
                except sqlite3.Error as e:
                    logging.warning(f"Error closing connection during cleanup: {e}")
                except Exception as e:
                    logging.error(f"Unexpected error closing connection during cleanup: {e}")
            
            self._all_connections.clear()
            
            # Clear queue
            while not self._available.empty():
                try:
                    self._available.get_nowait()
                except Empty:
                    break
