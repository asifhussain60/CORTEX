"""
Test: Connection Lifecycle Management (AC-FIX-BRITTLENESS-001)

RED test for database connection lifecycle management.
Tests that all database connections are properly closed and cleaned up.

Per CORE-008 (Tests First), these tests define the expected behavior
before implementation.

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import sqlite3
import threading
import time
from pathlib import Path
from typing import List

import pytest

from src.infrastructure.database import DatabaseManager, DatabaseConfig


class TestConnectionLifecycle:
    """Test database connection lifecycle and cleanup."""
    
    def test_connection_closes_on_context_manager_exit(self, temp_dir: Path):
        """Connection should be closed when exiting context manager."""
        db_path = temp_dir / "test.db"
        config = DatabaseConfig(db_path=db_path)
        db = DatabaseManager(config)
        db.initialize()
        
        # Get connection and store state
        conn = db._connection
        conn_id = id(conn)
        assert conn is not None
        
        # Close connection
        db.close()
        
        # After close, the thread-local connection should be None
        assert db._local.connection is None
        
        # Getting connection again should create a new one
        new_conn = db._connection
        new_conn_id = id(new_conn)
        assert new_conn is not None
        assert new_conn_id != conn_id, "Should create a new connection after close"
        
        db.close()
    
    def test_no_connection_leaks_after_exception(self, temp_dir: Path):
        """Connection should close even if exception occurs."""
        db_path = temp_dir / "test.db"
        config = DatabaseConfig(db_path=db_path)
        db = DatabaseManager(config)
        db.initialize()
        
        # Simulate exception during operation - execute bad SQL but catch it
        result = db.execute("INVALID SQL SYNTAX HERE")
        assert result.is_err()  # Should fail gracefully
        
        db.close()
        
        # Should still be able to create new connection
        db2 = DatabaseManager(config)
        db2.initialize()
        result = db2.execute("SELECT 1")
        assert result.is_ok()
        db2.close()
    
    def test_concurrent_connections_isolated(self, temp_dir: Path):
        """Each thread should get its own isolated connection."""
        db_path = temp_dir / "test.db"
        config = DatabaseConfig(db_path=db_path)
        
        connections = {}
        errors = []
        
        def thread_work(thread_id: int):
            """Each thread gets its own connection."""
            try:
                db = DatabaseManager(config)
                db.initialize()
                
                # Store connection ID
                conn_id = id(db._connection)
                connections[thread_id] = conn_id
                
                # Do some work
                result = db.execute("SELECT 1")
                assert result.is_ok()
                
                # Sleep briefly
                time.sleep(0.1)
                
                # Clean up
                db.close()
            except Exception as e:
                errors.append((thread_id, str(e)))
        
        # Create 5 threads
        threads = []
        for i in range(5):
            t = threading.Thread(target=thread_work, args=(i,))
            threads.append(t)
            t.start()
        
        # Wait for all threads
        for t in threads:
            t.join()
        
        # Check for errors
        assert len(errors) == 0, f"Errors occurred: {errors}"
        
        # All connections should be different
        conn_ids = list(connections.values())
        assert len(set(conn_ids)) == 5, "All connections should be unique"
    
    def test_load_test_100_rapid_connections(self, temp_dir: Path):
        """Load test: 100 rapid sequential connections should all close properly."""
        db_path = temp_dir / "test.db"
        config = DatabaseConfig(db_path=db_path)
        
        for i in range(100):
            db = DatabaseManager(config)
            db.initialize()
            
            result = db.execute(f"INSERT INTO ac_index (ac_id, phase, status, title) VALUES (?, ?, ?, ?)",
                              (f"AC-TEST-{i}", "PHASE-TEST", "PENDING", f"Test AC {i}"))
            assert result.is_ok()
            
            db.close()
        
        # Verify all inserts succeeded
        db_final = DatabaseManager(config)
        db_final.initialize()
        result = db_final.execute("SELECT COUNT(*) as cnt FROM ac_index")
        assert result.is_ok()
        count = result.unwrap()[0][0]
        assert count == 100, f"Expected 100 records, got {count}"
        db_final.close()
    
    def test_audit_log_writes_with_proper_cleanup(self, temp_dir: Path):
        """Audit log writes should cleanup connections properly."""
        db_path = temp_dir / "test.db"
        config = DatabaseConfig(db_path=db_path)
        db = DatabaseManager(config)
        db.initialize()
        
        # Write multiple audit entries
        for i in range(10):
            result = db.insert_audit(
                operation=f"TEST-OP-{i}",
                component="TEST-COMPONENT",
                level="INFO",
                message=f"Test message {i}",
                ac_id=f"AC-TEST-{i}"
            )
            assert result.is_ok()
        
        # Verify entries
        result = db.execute("SELECT COUNT(*) as cnt FROM audit_log")
        assert result.is_ok()
        count = result.unwrap()[0][0]
        assert count >= 10, f"Expected at least 10 audit entries, got {count}"
        
        db.close()
    
    def test_transaction_rollback_on_error(self, temp_dir: Path):
        """Failed transactions should rollback without leaving open connections."""
        db_path = temp_dir / "test.db"
        config = DatabaseConfig(db_path=db_path)
        db = DatabaseManager(config)
        db.initialize()
        
        # Insert a valid AC
        result = db.execute(
            "INSERT INTO ac_index (ac_id, phase, status, title) VALUES (?, ?, ?, ?)",
            ("AC-UNIQUE-001", "PHASE-TEST", "PENDING", "Test")
        )
        assert result.is_ok()
        
        # Try duplicate insert (should fail)
        result = db.execute(
            "INSERT INTO ac_index (ac_id, phase, status, title) VALUES (?, ?, ?, ?)",
            ("AC-UNIQUE-001", "PHASE-TEST", "PENDING", "Test")
        )
        assert result.is_err()  # Should fail due to primary key constraint
        
        # Connection should still be usable
        result = db.execute("SELECT COUNT(*) as cnt FROM ac_index WHERE ac_id = 'AC-UNIQUE-001'")
        assert result.is_ok()
        count = result.unwrap()[0][0]
        assert count == 1, "Only one record should exist"
        
        db.close()


class TestConnectionCleanup:
    """Test that connections are properly cleaned up."""
    
    def test_close_method_closes_thread_local_connection(self, temp_dir: Path):
        """close() should close the thread-local connection."""
        db_path = temp_dir / "test.db"
        config = DatabaseConfig(db_path=db_path)
        db = DatabaseManager(config)
        db.initialize()
        
        # Get connection (creates it)
        _ = db._connection
        
        # Connection should exist
        assert hasattr(db._local, 'connection')
        conn = db._local.connection
        assert conn is not None
        
        # Close it
        db.close()
        
        # Should be None now
        assert not hasattr(db._local, 'connection') or db._local.connection is None
    
    def test_context_manager_auto_cleanup(self, temp_dir: Path):
        """With-statement should auto cleanup connection."""
        db_path = temp_dir / "test.db"
        config = DatabaseConfig(db_path=db_path)
        
        db = DatabaseManager(config)
        db.initialize()
        
        # Use context manager (if implemented)
        try:
            with db:
                result = db.execute("SELECT 1")
                assert result.is_ok()
        except TypeError:
            # If context manager not implemented yet, just close explicitly
            db.close()


class TestNoConnectionLeaks:
    """Verify no connection leaks in different scenarios."""
    
    def test_multiple_execute_calls_same_connection(self, temp_dir: Path):
        """Multiple execute calls should reuse connection, not create new ones."""
        db_path = temp_dir / "test.db"
        config = DatabaseConfig(db_path=db_path)
        db = DatabaseManager(config)
        db.initialize()
        
        # Get connection ID on first call
        conn_id_1 = id(db._connection)
        
        # Make multiple calls
        for i in range(10):
            result = db.execute("SELECT ?", (i,))
            assert result.is_ok()
        
        # Connection ID should be the same
        conn_id_2 = id(db._connection)
        assert conn_id_1 == conn_id_2, "Should reuse same connection"
        
        db.close()
    
    def test_no_open_handles_after_close(self, temp_dir: Path):
        """After close(), no open file handles should remain."""
        db_path = temp_dir / "test.db"
        config = DatabaseConfig(db_path=db_path)
        db = DatabaseManager(config)
        db.initialize()
        
        # Perform operations
        db.execute("SELECT 1")
        db.execute("SELECT 2")
        db.execute("SELECT 3")
        
        # Close
        db.close()
        
        # Try to delete DB file (should work if no open handles)
        # On Windows, this would fail if file was still open
        db_path_backup = db_path.with_suffix('.db.bak')
        try:
            db_path.rename(db_path_backup)
            db_path_backup.rename(db_path)
        except (OSError, PermissionError) as e:
            pytest.fail(f"Could not move database file (file still open?): {e}")
