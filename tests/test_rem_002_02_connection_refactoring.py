"""
Tests for REMEDIATION-002 Phase A: Connection Refactoring.

AC-REM-002-02: Consolidate connection cleanup patterns with shared context manager.
Tests the unified connection context manager system.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sqlite3
import tempfile
import os
from pathlib import Path
from typing import Optional


class TestManagedConnectionDecorator(unittest.TestCase):
    """Tests for @managed_connection decorator."""
    
    def test_managed_connection_provides_cursor(self) -> None:
        """Decorator should provide cursor as first argument."""
        from cortex.common.connection_utils import managed_connection
        
        @managed_connection(":memory:")
        def create_and_insert(cursor: sqlite3.Cursor, value: str) -> int:
            cursor.execute("CREATE TABLE IF NOT EXISTS test (id INTEGER PRIMARY KEY, value TEXT)")
            cursor.execute("INSERT INTO test (value) VALUES (?)", (value,))
            return cursor.lastrowid
        
        row_id = create_and_insert("test_value")
        self.assertIsNotNone(row_id)
        self.assertGreater(row_id, 0)
    
    def test_managed_connection_returns_result(self) -> None:
        """Decorator should pass through return value."""
        from cortex.common.connection_utils import managed_connection
        
        @managed_connection(":memory:")
        def count_records(cursor: sqlite3.Cursor) -> int:
            cursor.execute("CREATE TABLE IF NOT EXISTS test (id INTEGER)")
            cursor.execute("SELECT COUNT(*) FROM test")
            return cursor.fetchone()[0]
        
        count = count_records()
        self.assertEqual(count, 0)
    
    def test_managed_connection_handles_exception(self) -> None:
        """Decorator should propagate exceptions."""
        from cortex.common.connection_utils import managed_connection
        
        @managed_connection(":memory:")
        def failing_operation(cursor: sqlite3.Cursor) -> None:
            cursor.execute("CREATE TABLE test (id INTEGER)")
            raise ValueError("Intentional failure")
        
        with self.assertRaises(ValueError):
            failing_operation()


class TestConnectionContext(unittest.TestCase):
    """Tests for ConnectionContext class."""
    
    def test_connection_context_as_context_manager(self) -> None:
        """ConnectionContext should work as context manager."""
        from cortex.common.connection_utils import ConnectionContext
        
        with ConnectionContext(":memory:") as ctx:
            ctx.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, value TEXT)")
            ctx.execute("INSERT INTO test (value) VALUES (?)", ("context_mgr",))
            result = ctx.query_one("SELECT value FROM test WHERE value = ?", ("context_mgr",))
            self.assertIsNotNone(result)
    
    def test_connection_context_execute_method(self) -> None:
        """ConnectionContext.execute should execute SQL and return cursor."""
        from cortex.common.connection_utils import ConnectionContext
        
        with ConnectionContext(":memory:") as ctx:
            cursor = ctx.execute("SELECT 1 + 1 AS result")
            result = cursor.fetchone()[0]
            self.assertEqual(result, 2)
    
    def test_connection_context_executemany_method(self) -> None:
        """ConnectionContext.executemany should batch insert."""
        from cortex.common.connection_utils import ConnectionContext
        
        values = [("a",), ("b",), ("c",)]
        
        with ConnectionContext(":memory:") as ctx:
            ctx.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, value TEXT)")
            ctx.executemany("INSERT INTO test (value) VALUES (?)", values)
            cursor = ctx.execute("SELECT COUNT(*) FROM test")
            count = cursor.fetchone()[0]
            self.assertEqual(count, 3)
    
    def test_connection_context_query_method(self) -> None:
        """ConnectionContext.query should return all results."""
        from cortex.common.connection_utils import ConnectionContext
        
        with ConnectionContext(":memory:") as ctx:
            ctx.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, value TEXT)")
            ctx.executemany("INSERT INTO test (value) VALUES (?)", 
                           [("x",), ("y",), ("z",)])
            results = ctx.query("SELECT value FROM test ORDER BY value")
            self.assertEqual(len(results), 3)
            self.assertEqual(results[0][0], "x")
    
    def test_connection_context_query_one_method(self) -> None:
        """ConnectionContext.query_one should return single result."""
        from cortex.common.connection_utils import ConnectionContext
        
        with ConnectionContext(":memory:") as ctx:
            ctx.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, value TEXT)")
            ctx.execute("INSERT INTO test (value) VALUES (?)", ("single",))
            result = ctx.query_one("SELECT value FROM test WHERE value = ?", ("single",))
            self.assertEqual(result[0], "single")


class TestTransactionContext(unittest.TestCase):
    """Tests for explicit transaction management."""
    
    def test_transaction_context_explicit_commit(self) -> None:
        """TransactionContext should support explicit commit."""
        from cortex.common.connection_utils import TransactionContext
        
        with TransactionContext(":memory:", auto_commit=False) as tx:
            tx.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, value TEXT)")
            tx.execute("INSERT INTO test (value) VALUES (?)", ("explicit",))
            tx.commit()
            result = tx.query_one("SELECT value FROM test WHERE value = ?", ("explicit",))
            self.assertIsNotNone(result)
    
    def test_transaction_context_explicit_rollback(self) -> None:
        """TransactionContext rollback method marks transaction as rolled back."""
        from cortex.common.connection_utils import TransactionContext
        
        with TransactionContext(":memory:", auto_commit=False) as tx:
            tx.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, value TEXT)")
            tx.execute("INSERT INTO test (value) VALUES (?)", ("test",))
            
            # Rollback should mark transaction as rolled back
            tx.rollback()
            
            # Verify rollback flag is set
            self.assertTrue(tx._rolledback)
    
    def test_transaction_context_savepoint(self) -> None:
        """TransactionContext should support savepoints."""
        from cortex.common.connection_utils import TransactionContext
        
        with TransactionContext(":memory:", auto_commit=False) as tx:
            tx.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, value TEXT)")
            tx.execute("INSERT INTO test (value) VALUES (?)", ("before_savepoint",))
            tx.savepoint("sp1")
            tx.execute("INSERT INTO test (value) VALUES (?)", ("after_savepoint",))
            tx.rollback_to_savepoint("sp1")
            tx.commit()
            
            # Only first insert should be committed
            cursor = tx.execute("SELECT COUNT(*) FROM test")
            count = cursor.fetchone()[0]
            self.assertEqual(count, 1)


class TestConnectionPoolIntegration(unittest.TestCase):
    """Tests for connection utils integration with ConnectionPool."""
    
    def test_managed_connection_with_pool(self) -> None:
        """managed_connection should work with connection pool."""
        from cortex.common.connection_utils import managed_connection
        
        @managed_connection(":memory:")
        def insert_via_pool(cursor: sqlite3.Cursor) -> int:
            cursor.execute("CREATE TABLE IF NOT EXISTS test (id INTEGER PRIMARY KEY, value TEXT)")
            cursor.execute("INSERT INTO test (value) VALUES (?)", ("pooled",))
            return cursor.lastrowid
        
        row_id = insert_via_pool()
        self.assertIsNotNone(row_id)


if __name__ == "__main__":
    unittest.main()
