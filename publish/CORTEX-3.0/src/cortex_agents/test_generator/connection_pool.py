"""
SQLite Connection Pool

Connection pooling for concurrent SQLite access with proper locking.

Copyright (c) 2024-2025 Asif Hussain. All rights reserved.
"""

import sqlite3
import threading
from typing import Optional, List, Any, Dict
from dataclasses import dataclass
from datetime import datetime
import time
from contextlib import contextmanager


@dataclass
class ConnectionStats:
    """Statistics for a pooled connection"""
    connection_id: int
    created_at: float
    last_used: float
    query_count: int
    in_use: bool


class PooledConnection:
    """Wrapper for a pooled SQLite connection"""
    
    def __init__(self, connection_id: int, connection: sqlite3.Connection):
        """
        Initialize pooled connection.
        
        Args:
            connection_id: Unique ID for this connection
            connection: SQLite connection instance
        """
        self.connection_id = connection_id
        self.connection = connection
        self.created_at = time.time()
        self.last_used = time.time()
        self.query_count = 0
        self.in_use = False
        self.lock = threading.Lock()
    
    def mark_used(self) -> None:
        """Mark connection as used (update stats)"""
        self.last_used = time.time()
        self.query_count += 1
    
    def get_stats(self) -> ConnectionStats:
        """Get connection statistics"""
        return ConnectionStats(
            connection_id=self.connection_id,
            created_at=self.created_at,
            last_used=self.last_used,
            query_count=self.query_count,
            in_use=self.in_use
        )


class SQLiteConnectionPool:
    """
    Connection pool for SQLite with thread safety.
    
    Phase 2 Milestone 2.3 - Performance Optimization
    Target: Enable concurrent access to pattern store
    
    Note: SQLite has limited concurrency due to file locking,
    but pooling helps manage connections efficiently.
    """
    
    def __init__(
        self,
        db_path: str,
        pool_size: int = 5,
        timeout: float = 30.0
    ):
        """
        Initialize connection pool.
        
        Args:
            db_path: Path to SQLite database
            pool_size: Maximum connections in pool
            timeout: Connection acquisition timeout (seconds)
        """
        self.db_path = db_path
        self.pool_size = pool_size
        self.timeout = timeout
        
        # Connection pool
        self.connections: List[PooledConnection] = []
        self.pool_lock = threading.Lock()
        self.condition = threading.Condition(self.pool_lock)
        
        # Statistics
        self.total_acquisitions = 0
        self.total_releases = 0
        self.wait_timeouts = 0
        self.created_connections = 0
        
        # Initialize pool
        self._initialize_pool()
    
    def _initialize_pool(self) -> None:
        """Create initial connections"""
        with self.pool_lock:
            for i in range(self.pool_size):
                conn = self._create_connection()
                pooled = PooledConnection(i, conn)
                self.connections.append(pooled)
                self.created_connections += 1
    
    def _create_connection(self) -> sqlite3.Connection:
        """Create a new SQLite connection"""
        conn = sqlite3.connect(
            self.db_path,
            check_same_thread=False,  # Allow use across threads
            timeout=self.timeout
        )
        conn.row_factory = sqlite3.Row
        
        # Enable WAL mode for better concurrency
        conn.execute("PRAGMA journal_mode=WAL")
        
        return conn
    
    @contextmanager
    def get_connection(self):
        """
        Get a connection from the pool (context manager).
        
        Usage:
            with pool.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM patterns")
        
        Yields:
            SQLite connection from pool
        """
        pooled_conn = self._acquire()
        
        try:
            yield pooled_conn.connection
        finally:
            self._release(pooled_conn)
    
    def _acquire(self) -> PooledConnection:
        """
        Acquire a connection from the pool.
        
        Returns:
            PooledConnection instance
            
        Raises:
            TimeoutError: If no connection available within timeout
        """
        start_time = time.time()
        
        with self.condition:
            while True:
                # Look for available connection
                for pooled in self.connections:
                    if not pooled.in_use:
                        pooled.in_use = True
                        pooled.mark_used()
                        self.total_acquisitions += 1
                        return pooled
                
                # Check timeout
                elapsed = time.time() - start_time
                if elapsed >= self.timeout:
                    self.wait_timeouts += 1
                    raise TimeoutError(
                        f"Could not acquire connection within {self.timeout}s"
                    )
                
                # Wait for connection to become available
                remaining = self.timeout - elapsed
                self.condition.wait(timeout=remaining)
    
    def _release(self, pooled_conn: PooledConnection) -> None:
        """
        Release a connection back to the pool.
        
        Args:
            pooled_conn: PooledConnection to release
        """
        with self.condition:
            pooled_conn.in_use = False
            self.total_releases += 1
            self.condition.notify()  # Wake up waiting threads
    
    def execute(
        self,
        query: str,
        parameters: tuple = ()
    ) -> List[sqlite3.Row]:
        """
        Execute a query using a pooled connection.
        
        Args:
            query: SQL query
            parameters: Query parameters
            
        Returns:
            List of result rows
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, parameters)
            return cursor.fetchall()
    
    def execute_many(
        self,
        query: str,
        parameters_list: List[tuple]
    ) -> None:
        """
        Execute a query multiple times with different parameters.
        
        Args:
            query: SQL query
            parameters_list: List of parameter tuples
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.executemany(query, parameters_list)
            conn.commit()
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get pool statistics.
        
        Returns:
            Dictionary with pool stats
        """
        with self.pool_lock:
            in_use_count = sum(1 for p in self.connections if p.in_use)
            available_count = len(self.connections) - in_use_count
            
            connection_stats = [
                p.get_stats() for p in self.connections
            ]
        
        return {
            'pool_size': self.pool_size,
            'connections_in_use': in_use_count,
            'connections_available': available_count,
            'total_acquisitions': self.total_acquisitions,
            'total_releases': self.total_releases,
            'wait_timeouts': self.wait_timeouts,
            'created_connections': self.created_connections,
            'connection_details': connection_stats
        }
    
    def close_all(self) -> None:
        """Close all connections in the pool"""
        with self.pool_lock:
            for pooled in self.connections:
                try:
                    pooled.connection.close()
                except Exception:
                    pass  # Ignore errors on close
            
            self.connections.clear()
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close_all()
    
    def __del__(self):
        """Destructor - ensure connections are closed"""
        self.close_all()


# Helper function for creating pools

def create_pattern_store_pool(
    db_path: str,
    pool_size: int = 5
) -> SQLiteConnectionPool:
    """
    Create a connection pool for pattern store.
    
    Args:
        db_path: Path to pattern store database
        pool_size: Maximum connections in pool
        
    Returns:
        SQLiteConnectionPool instance
    """
    return SQLiteConnectionPool(
        db_path=db_path,
        pool_size=pool_size,
        timeout=30.0
    )
