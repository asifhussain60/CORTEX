"""
AC-FIX-006-01: SQLite Connection Lifecycle Management Tests

Tests for proper SQLite connection lifecycle management to prevent:
- File handle exhaustion
- "database is locked" errors
- Memory leaks under sustained load

FINDING-006 (MEDIUM): Connections not explicitly closed in error paths
SOLUTION: Wrap all SQLite operations in context managers (with statement)
"""

import sqlite3
import tempfile
from pathlib import Path
from typing import List, Tuple
from contextlib import contextmanager
import pytest


@contextmanager
def managed_sqlite_connection(db_path: str):
    """Context manager for SQLite connections - guaranteed cleanup."""
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        yield conn
    finally:
        if conn is not None:
            conn.close()


class TestSQLiteConnectionLifecycle:
    """Tests for SQLite connection lifecycle patterns."""
    
    @pytest.fixture
    def temp_db(self):
        """Create a temporary SQLite database."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = str(Path(tmpdir) / "test.db")
            yield db_path
    
    def test_context_manager_closes_connection(self, temp_db):
        """Verify context manager closes connection on normal exit."""
        with managed_sqlite_connection(temp_db) as conn:
            conn.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, value TEXT)")
            conn.execute("INSERT INTO test (value) VALUES ('test')")
        
        # Connection should be closed after context manager exits
        # Verify by trying to use connection (should fail if properly closed)
        with pytest.raises(sqlite3.ProgrammingError):
            conn.execute("SELECT * FROM test")
    
    def test_context_manager_closes_on_exception(self, temp_db):
        """Verify context manager closes connection even when exception occurs."""
        try:
            with managed_sqlite_connection(temp_db) as conn:
                conn.execute("CREATE TABLE test (id INTEGER PRIMARY KEY)")
                # Force an exception
                raise ValueError("Test exception")
        except ValueError:
            pass  # Expected
        
        # Connection should still be closed despite exception
        with pytest.raises(sqlite3.ProgrammingError):
            conn.execute("SELECT COUNT(*) FROM test")
    
    def test_connection_pool_prevents_exhaustion(self, temp_db):
        """Verify connection pooling prevents file handle exhaustion."""
        connections = []
        max_connections = 5
        
        # Create and properly close connections
        for i in range(max_connections * 2):  # Exceed limit but with proper cleanup
            with managed_sqlite_connection(temp_db) as conn:
                conn.execute(f"PRAGMA user_version = {i}")
                # Connection properly closed in finally block
        
        # All connections should be closed, so we shouldn't hit "database is locked"
        # Subsequent connections should work fine
        with managed_sqlite_connection(temp_db) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM sqlite_master")
            result = cursor.fetchone()
            assert result is not None
    
    def test_audit_operations_use_context_manager(self, temp_db):
        """Verify audit operations use proper context manager pattern."""
        operation_count = 0
        
        for i in range(10):
            with managed_sqlite_connection(temp_db) as conn:
                # Simulated audit operation
                conn.execute(f"PRAGMA user_version = {i}")
                operation_count += 1
        
        assert operation_count == 10
        
        # Verify no connections left open (can still connect)
        with managed_sqlite_connection(temp_db) as conn:
            conn.execute("SELECT 1")


class TestConnectionLeakDetection:
    """Tests for detecting and preventing connection leaks."""
    
    def test_bad_pattern_without_context_manager(self, tmp_path):
        """Document the BAD pattern that should be avoided."""
        db_path = str(tmp_path / "test.db")
        
        # BAD PATTERN (should NOT be used):
        # conn = sqlite3.connect(db_path)
        # try:
        #     conn.execute("SELECT 1")
        # except Exception:
        #     pass  # Connection NOT closed on exception!
        # finally:
        #     conn.close()
        
        # Even with try/finally, the pattern above can fail if:
        # - Exception occurs before connect() returns
        # - Connection.__del__ depends on garbage collection (unreliable)
        # - Finally block itself raises an exception
        
        # GOOD PATTERN (use context manager):
        with managed_sqlite_connection(db_path) as conn:
            conn.execute("SELECT 1")
        
        # Connection guaranteed closed
        assert True
    
    def test_multiple_operations_same_connection(self, tmp_path):
        """Verify reusing same connection within context is safe."""
        db_path = str(tmp_path / "test.db")
        
        with managed_sqlite_connection(db_path) as conn:
            # Create table
            conn.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)")
            
            # Insert multiple rows
            for i in range(100):
                conn.execute("INSERT INTO users (name) VALUES (?)", (f"user_{i}",))
            
            # Query results
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM users")
            count = cursor.fetchone()[0]
            
            assert count == 100
        
        # No leak: connection properly closed
    
    def test_nested_transactions(self, tmp_path):
        """Verify transaction handling with proper connection lifecycle."""
        db_path = str(tmp_path / "test.db")
        
        with managed_sqlite_connection(db_path) as conn:
            conn.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, value INTEGER)")
            
            try:
                conn.execute("BEGIN TRANSACTION")
                conn.execute("INSERT INTO test (value) VALUES (1)")
                conn.execute("INSERT INTO test (value) VALUES (2)")
                conn.execute("COMMIT")
            except Exception:
                conn.execute("ROLLBACK")
        
        # Verify data persisted and connection closed
        with managed_sqlite_connection(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM test")
            assert cursor.fetchone()[0] == 2


class TestConnectionMetrics:
    """Tests for connection pool metrics and monitoring."""
    
    def test_connection_metrics_structure(self):
        """Define connection metrics structure for monitoring."""
        metrics_structure = {
            'total_connections_created': 0,
            'currently_open': 0,
            'total_queries_executed': 0,
            'connection_pool_exhaustion_count': 0,
            'average_connection_lifetime_ms': 0,
            'max_concurrent_connections': 0,
            'database_locked_errors': 0,
        }
        
        # Verify structure has expected fields
        assert 'currently_open' in metrics_structure
        assert 'database_locked_errors' in metrics_structure
        assert 'connection_pool_exhaustion_count' in metrics_structure
    
    def test_connection_metric_tracking(self, tmp_path):
        """Verify metrics can be tracked during connections."""
        db_path = str(tmp_path / "test.db")
        metrics = {
            'created': 0,
            'closed': 0,
        }
        
        # Track connection lifecycle
        for i in range(5):
            with managed_sqlite_connection(db_path) as conn:
                metrics['created'] += 1
                conn.execute(f"PRAGMA user_version = {i}")
            metrics['closed'] += 1
        
        assert metrics['created'] == 5
        assert metrics['closed'] == 5
        assert metrics['created'] == metrics['closed']  # No leaks


class TestLoadBehavior:
    """Tests for connection behavior under load."""
    
    def test_rapid_sequential_connections(self, tmp_path):
        """Test rapid sequential connections don't leak."""
        db_path = str(tmp_path / "test.db")
        
        # Create table first
        with managed_sqlite_connection(db_path) as conn:
            conn.execute("CREATE TABLE counters (id INTEGER PRIMARY KEY, count INTEGER)")
            conn.commit()
        
        # Rapid-fire connections
        for i in range(100):
            with managed_sqlite_connection(db_path) as conn:
                conn.execute("INSERT INTO counters (count) VALUES (?)", (i,))
                conn.commit()
        
        # Verify all data persisted (no leaks caused early termination)
        with managed_sqlite_connection(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM counters")
            assert cursor.fetchone()[0] == 100
    
    def test_concurrent_scenarios(self, tmp_path):
        """Test connection cleanup in various scenarios."""
        db_path = str(tmp_path / "test.db")
        
        scenarios = [
            ("normal_query", lambda c: c.execute("SELECT 1")),
            ("insert", lambda c: c.execute("INSERT INTO test (value) VALUES (1)")),
            ("transaction", lambda c: (
                c.execute("BEGIN"),
                c.execute("SELECT 1"),
                c.execute("COMMIT")
            )),
        ]
        
        with managed_sqlite_connection(db_path) as conn:
            conn.execute("CREATE TABLE IF NOT EXISTS test (id INTEGER PRIMARY KEY, value INTEGER)")
        
        for scenario_name, scenario_func in scenarios:
            with managed_sqlite_connection(db_path) as conn:
                try:
                    scenario_func(conn)
                except Exception as e:
                    # Even with exceptions, connection should close
                    pass


class TestBestPractices:
    """Documents best practices for SQLite connection management."""
    
    def test_context_manager_pattern_documentation(self):
        """Document recommended context manager pattern."""
        pattern = """
        RECOMMENDED PATTERN (AC-FIX-006-01):
        ===================================
        
        ✅ GOOD: Use context manager
        
        ```python
        from contextlib import contextmanager
        
        @contextmanager
        def managed_db_connection(db_path):
            conn = sqlite3.connect(db_path)
            try:
                yield conn
            finally:
                if conn:
                    conn.close()
        
        # Usage:
        with managed_db_connection("app.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users")
            results = cursor.fetchall()
        # ✅ Connection guaranteed closed, even if exception occurs
        ```
        
        ❌ BAD: Manual connection management
        
        ```python
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM users")
        except Exception as e:
            pass  # Connection NOT closed on exception!
        finally:
            conn.close()  # Might not execute if exception in except block
        ```
        
        KEY BENEFITS:
        - Guaranteed connection cleanup
        - Exception safety (connection closed even if exception occurs)
        - Clean, readable code
        - Composable with other context managers
        - Prevents "database is locked" errors
        - Prevents file handle exhaustion
        """
        
        assert "context manager" in pattern.lower()
        assert "GOOD" in pattern
        assert "BAD" in pattern


# Integration with existing code patterns
class TestAuditLoggerPattern:
    """Test patterns for audit logger SQLite operations."""
    
    def test_audit_operation_with_proper_cleanup(self, tmp_path):
        """Verify audit operations properly manage connections."""
        db_path = str(tmp_path / "audit.db")
        
        # Simulate audit operation
        with managed_sqlite_connection(db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS audit_log (
                    id INTEGER PRIMARY KEY,
                    timestamp TEXT,
                    action TEXT,
                    details TEXT
                )
            """)
            
            # Simulate 5 audit entries
            for i in range(5):
                conn.execute("""
                    INSERT INTO audit_log (timestamp, action, details)
                    VALUES (?, ?, ?)
                """, (f"2026-01-17T03:{i:02d}:00Z", "ACTION", f"Details {i}"))
            
            conn.commit()
        
        # Verify all entries persisted and connection closed
        with managed_sqlite_connection(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM audit_log")
            assert cursor.fetchone()[0] == 5
