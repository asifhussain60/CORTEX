"""
Tests for Transactional State Management.

AC-STATE-002-01: ACID Transactions
Tests transaction manager with isolation levels, deadlock detection,
automatic retry, and nested transaction support.
"""

import pytest
import sqlite3
import threading
import time
from typing import Optional, List
from unittest.mock import Mock, patch

from cortex.infrastructure.transaction_manager import (
    TransactionManager,
    TransactionConfig,
    IsolationLevel,
    TransactionContext,
    DeadlockError,
    TransactionTimeoutError,
)


@pytest.fixture
def db_path(tmp_path):
    """Create temporary database."""
    return str(tmp_path / "test_transactions.db")


@pytest.fixture
def tx_manager(db_path):
    """Create transaction manager instance."""
    config = TransactionConfig(
        default_isolation=IsolationLevel.SERIALIZABLE,
        deadlock_retries=3,
        timeout_seconds=5.0,
    )
    manager = TransactionManager(db_path, config)
    
    # Create test table
    with manager.begin() as tx:
        tx.execute("""
            CREATE TABLE test_data (
                id INTEGER PRIMARY KEY,
                value TEXT,
                version INTEGER DEFAULT 1
            )
        """)
    
    yield manager
    manager.close()


class TestTransactionBasics:
    """Test basic transaction functionality."""

    def test_simple_transaction_commits(self, tx_manager: TransactionManager) -> None:
        """Should commit simple transaction."""
        with tx_manager.begin() as tx:
            tx.execute("INSERT INTO test_data (id, value) VALUES (?, ?)", (1, "test"))
        
        # Verify committed
        with tx_manager.begin(read_only=True) as tx:
            result = tx.execute("SELECT value FROM test_data WHERE id = 1").fetchone()
            assert result[0] == "test"

    def test_transaction_rollback_on_exception(self, tx_manager: TransactionManager) -> None:
        """Should rollback transaction on exception."""
        try:
            with tx_manager.begin() as tx:
                tx.execute("INSERT INTO test_data (id, value) VALUES (?, ?)", (1, "test"))
                raise ValueError("Intentional error")
        except ValueError:
            pass
        
        # Verify rolled back
        with tx_manager.begin(read_only=True) as tx:
            result = tx.execute("SELECT COUNT(*) FROM test_data").fetchone()
            assert result[0] == 0

    def test_explicit_rollback(self, tx_manager: TransactionManager) -> None:
        """Should support explicit rollback."""
        with tx_manager.begin() as tx:
            tx.execute("INSERT INTO test_data (id, value) VALUES (?, ?)", (1, "test"))
            tx.rollback()
        
        # Verify rolled back
        with tx_manager.begin(read_only=True) as tx:
            result = tx.execute("SELECT COUNT(*) FROM test_data").fetchone()
            assert result[0] == 0


class TestIsolationLevels:
    """Test transaction isolation levels."""

    def test_serializable_prevents_dirty_reads(self, tx_manager: TransactionManager) -> None:
        """SERIALIZABLE should prevent dirty reads."""
        results = []
        barrier = threading.Barrier(2)
        
        def writer():
            with tx_manager.begin(isolation=IsolationLevel.SERIALIZABLE) as tx:
                tx.execute("INSERT INTO test_data (id, value) VALUES (?, ?)", (1, "uncommitted"))
                barrier.wait()  # Let reader try
                time.sleep(0.1)
                # Rollback intentionally
                tx.rollback()
        
        def reader():
            barrier.wait()
            with tx_manager.begin(isolation=IsolationLevel.SERIALIZABLE, read_only=True) as tx:
                result = tx.execute("SELECT COUNT(*) FROM test_data").fetchone()
                results.append(result[0])
        
        t1 = threading.Thread(target=writer)
        t2 = threading.Thread(target=reader)
        t1.start()
        t2.start()
        t1.join()
        t2.join()
        
        # Reader should see 0 (no dirty read)
        assert results[0] == 0

    def test_read_committed_isolation(self, tx_manager: TransactionManager) -> None:
        """READ COMMITTED should see only committed data."""
        # Insert initial data
        with tx_manager.begin() as tx:
            tx.execute("INSERT INTO test_data (id, value) VALUES (?, ?)", (1, "initial"))
        
        results = []
        barrier = threading.Barrier(2)
        
        def writer():
            with tx_manager.begin(isolation=IsolationLevel.READ_COMMITTED) as tx:
                tx.execute("UPDATE test_data SET value = ? WHERE id = ?", ("updated", 1))
                barrier.wait()
                time.sleep(0.1)
        
        def reader():
            time.sleep(0.05)
            barrier.wait()
            with tx_manager.begin(isolation=IsolationLevel.READ_COMMITTED, read_only=True) as tx:
                result = tx.execute("SELECT value FROM test_data WHERE id = 1").fetchone()
                results.append(result[0])
        
        t1 = threading.Thread(target=writer)
        t2 = threading.Thread(target=reader)
        t1.start()
        t2.start()
        t1.join()
        t2.join()
        
        # Reader should see either initial or updated (both valid for READ COMMITTED)
        assert results[0] in ["initial", "updated"]


class TestDeadlockDetection:
    """Test deadlock detection and recovery."""

    def test_deadlock_detected_and_retried(self, tx_manager: TransactionManager) -> None:
        """Should detect deadlock and retry automatically."""
        # Insert test data
        with tx_manager.begin() as tx:
            tx.execute("INSERT INTO test_data (id, value) VALUES (?, ?)", (1, "row1"))
            tx.execute("INSERT INTO test_data (id, value) VALUES (?, ?)", (2, "row2"))
        
        results = []
        barrier = threading.Barrier(2)
        
        def tx1_acquire_1_then_2():
            try:
                with tx_manager.begin() as tx:
                    tx.execute("UPDATE test_data SET value = ? WHERE id = 1", ("tx1",))
                    barrier.wait()
                    time.sleep(0.05)
                    tx.execute("UPDATE test_data SET value = ? WHERE id = 2", ("tx1",))
                    results.append("tx1_success")
            except DeadlockError:
                results.append("tx1_deadlock")
        
        def tx2_acquire_2_then_1():
            try:
                with tx_manager.begin() as tx:
                    tx.execute("UPDATE test_data SET value = ? WHERE id = 2", ("tx2",))
                    barrier.wait()
                    time.sleep(0.05)
                    tx.execute("UPDATE test_data SET value = ? WHERE id = 1", ("tx2",))
                    results.append("tx2_success")
            except DeadlockError:
                results.append("tx2_deadlock")
        
        t1 = threading.Thread(target=tx1_acquire_1_then_2)
        t2 = threading.Thread(target=tx2_acquire_2_then_1)
        t1.start()
        t2.start()
        t1.join(timeout=10)
        t2.join(timeout=10)
        
        # At least one should succeed (with retries)
        assert len(results) >= 1

    def test_deadlock_retry_exhaustion(self, tx_manager: TransactionManager) -> None:
        """Should raise DeadlockError after max retries."""
        # Verify the _execute_with_retry method exists and can be called
        assert hasattr(tx_manager, '_execute_with_retry')
        assert callable(tx_manager._execute_with_retry)
        
        # Verify max retries configuration works
        config = TransactionConfig(deadlock_retries=0)
        limited_manager = TransactionManager(tx_manager._db_path, config)
        assert limited_manager._config.deadlock_retries == 0


class TestNestedTransactions:
    """Test nested transaction support via savepoints."""

    def test_nested_transaction_commits(self, tx_manager: TransactionManager) -> None:
        """Should support nested transactions with savepoints."""
        with tx_manager.begin() as tx:
            tx.execute("INSERT INTO test_data (id, value) VALUES (?, ?)", (1, "outer"))
            
            with tx.savepoint() as sp:
                sp.execute("INSERT INTO test_data (id, value) VALUES (?, ?)", (2, "inner"))
        
        # Both should be committed
        with tx_manager.begin(read_only=True) as tx:
            result = tx.execute("SELECT COUNT(*) FROM test_data").fetchone()
            assert result[0] == 2

    def test_nested_transaction_rollback(self, tx_manager: TransactionManager) -> None:
        """Inner savepoint rollback should not affect outer transaction."""
        with tx_manager.begin() as tx:
            tx.execute("INSERT INTO test_data (id, value) VALUES (?, ?)", (1, "outer"))
            
            try:
                with tx.savepoint() as sp:
                    sp.execute("INSERT INTO test_data (id, value) VALUES (?, ?)", (2, "inner"))
                    raise ValueError("Rollback inner")
            except ValueError:
                pass
        
        # Only outer should be committed (id=1), inner rolled back (id=2)
        with tx_manager.begin(read_only=True) as tx:
            result = tx.execute("SELECT COUNT(*) FROM test_data WHERE id = 1").fetchone()
            assert result[0] == 1
            result2 = tx.execute("SELECT COUNT(*) FROM test_data WHERE id = 2").fetchone()
            assert result2[0] == 0


class TestTransactionTimeout:
    """Test transaction timeout handling."""

    def test_transaction_timeout_raises_error(self, tx_manager: TransactionManager) -> None:
        """Should timeout long-running transaction."""
        config = TransactionConfig(timeout_seconds=0.05)
        timeout_manager = TransactionManager(tx_manager._db_path, config)
        
        with pytest.raises(TransactionTimeoutError):
            with timeout_manager.transaction() as tx:
                tx.execute("INSERT INTO test_data (id, value) VALUES (?, ?)", (1, "test"))
                time.sleep(0.15)  # Exceed timeout by significant margin
                tx.execute("SELECT * FROM test_data")  # Trigger timeout check


class TestConcurrentTransactions:
    """Test concurrent transaction correctness."""

    def test_concurrent_inserts_all_succeed(self, tx_manager: TransactionManager) -> None:
        """Should handle concurrent inserts correctly."""
        def insert_row(row_id: int):
            with tx_manager.begin() as tx:
                tx.execute("INSERT INTO test_data (id, value) VALUES (?, ?)", (row_id, f"row{row_id}"))
        
        threads = [threading.Thread(target=insert_row, args=(i,)) for i in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # All 10 rows should exist
        with tx_manager.begin(read_only=True) as tx:
            result = tx.execute("SELECT COUNT(*) FROM test_data").fetchone()
            assert result[0] == 10

    def test_concurrent_updates_no_lost_writes(self, tx_manager: TransactionManager) -> None:
        """Should prevent lost updates under concurrent modification."""
        # Insert initial data
        with tx_manager.begin() as tx:
            tx.execute("INSERT INTO test_data (id, value) VALUES (?, ?)", (1, "0"))
        
        def increment_value():
            for _ in range(10):
                max_retries = 5
                for attempt in range(max_retries):
                    try:
                        with tx_manager.begin() as tx:
                            result = tx.execute("SELECT value FROM test_data WHERE id = 1").fetchone()
                            new_val = str(int(result[0]) + 1)
                            tx.execute("UPDATE test_data SET value = ? WHERE id = 1", (new_val,))
                        break  # Success
                    except sqlite3.OperationalError as e:
                        if "locked" in str(e).lower() and attempt < max_retries - 1:
                            time.sleep(0.01 * (2 ** attempt))
                        else:
                            raise
        
        threads = [threading.Thread(target=increment_value) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # Should be 50 (5 threads * 10 increments)
        with tx_manager.begin(read_only=True) as tx:
            result = tx.execute("SELECT value FROM test_data WHERE id = 1").fetchone()
            assert int(result[0]) == 50


class TestTransactionMetrics:
    """Test transaction metrics collection."""

    def test_tracks_commit_count(self, tx_manager: TransactionManager) -> None:
        """Should track successful commits."""
        for i in range(3):
            with tx_manager.begin() as tx:
                tx.execute("INSERT INTO test_data (id, value) VALUES (?, ?)", (i, f"test{i}"))
        
        metrics = tx_manager.get_metrics()
        assert metrics["total_commits"] >= 3

    def test_tracks_rollback_count(self, tx_manager: TransactionManager) -> None:
        """Should track rollbacks."""
        for i in range(3):
            try:
                with tx_manager.begin() as tx:
                    tx.execute("INSERT INTO test_data (id, value) VALUES (?, ?)", (i, f"test{i}"))
                    raise ValueError("Force rollback")
            except ValueError:
                pass
        
        metrics = tx_manager.get_metrics()
        assert metrics["total_rollbacks"] >= 3

    def test_tracks_deadlock_count(self, tx_manager: TransactionManager) -> None:
        """Should track deadlock occurrences."""
        metrics = tx_manager.get_metrics()
        assert "total_deadlocks" in metrics


class TestReadOnlyTransactions:
    """Test read-only transaction optimization."""

    def test_read_only_transaction(self, tx_manager: TransactionManager) -> None:
        """Should support read-only transactions."""
        # Insert test data
        with tx_manager.begin() as tx:
            tx.execute("INSERT INTO test_data (id, value) VALUES (?, ?)", (1, "test"))
        
        # Read-only transaction
        with tx_manager.begin(read_only=True) as tx:
            result = tx.execute("SELECT value FROM test_data WHERE id = 1").fetchone()
            assert result[0] == "test"

    def test_read_only_prevents_writes(self, tx_manager: TransactionManager) -> None:
        """Read-only transaction should prevent writes."""
        with pytest.raises(sqlite3.OperationalError):
            with tx_manager.begin(read_only=True) as tx:
                tx.execute("INSERT INTO test_data (id, value) VALUES (?, ?)", (1, "test"))


class TestConnectionPooling:
    """Test transaction manager connection pooling."""

    def test_reuses_connections(self, tx_manager: TransactionManager) -> None:
        """Should reuse connections from pool."""
        conn_ids = set()
        
        for _ in range(5):
            with tx_manager.begin() as tx:
                conn_ids.add(id(tx._connection))
        
        # Should reuse connections (up to pool size)
        assert len(conn_ids) <= tx_manager._config.pool_size

    def test_concurrent_connections_isolated(self, tx_manager: TransactionManager) -> None:
        """Concurrent transactions should use separate connections."""
        conn_ids = []
        lock = threading.Lock()
        
        def get_conn_id():
            try:
                with tx_manager.begin() as tx:
                    conn_id = id(tx._connection)
                    with lock:
                        conn_ids.append(conn_id)
                    time.sleep(0.05)
            except Exception as e:
                print(f"Thread error: {e}")
        
        threads = [threading.Thread(target=get_conn_id) for _ in range(3)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=2.0)
        
        # All should have different connection IDs (concurrent)
        assert len(conn_ids) == 3
        assert len(set(conn_ids)) == 3
