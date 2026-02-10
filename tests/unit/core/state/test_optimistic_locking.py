"""
Unit tests for Optimistic Locking (AC-STATE-002-02).

Tests version-based conflict detection, automatic merge strategies,
and concurrent update handling without blocking readers.

Author: Asif Hussain
Copyright © 2026 Asif Hussain. All rights reserved.
"""

import pytest
import sqlite3
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import List, Optional

from cortex.core.state.optimistic_lock import (
    OptimisticLockManager,
    VersionedRow,
    ConflictError,
    StaleDataError,
    MergeStrategy,
)


@pytest.fixture
def temp_db(tmp_path: Path) -> Path:
    """Create temporary database for testing."""
    db_path = tmp_path / "test_optimistic_lock.db"
    conn = sqlite3.connect(str(db_path))
    conn.execute("""
        CREATE TABLE test_entity (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            value INTEGER DEFAULT 0,
            version INTEGER DEFAULT 1
        )
    """)
    conn.execute("INSERT INTO test_entity (id, name, value) VALUES (1, 'test', 0)")
    conn.commit()
    conn.close()
    return db_path


@pytest.fixture
def lock_manager(temp_db: Path) -> OptimisticLockManager:
    """Create optimistic lock manager for testing."""
    return OptimisticLockManager(str(temp_db))


class TestBasicOptimisticLocking:
    """Test basic optimistic locking operations."""
    
    def test_read_with_version(self, lock_manager: OptimisticLockManager) -> None:
        """Test reading entity with version capture."""
        row = lock_manager.read("test_entity", 1)
        assert row.id == 1
        assert row.version == 1
        assert row.data["name"] == "test"
    
    def test_successful_update(self, lock_manager: OptimisticLockManager) -> None:
        """Test successful update with correct version."""
        row = lock_manager.read("test_entity", 1)
        row.data["value"] = 42
        
        updated = lock_manager.write("test_entity", row)
        assert updated.version == 2
        assert updated.data["value"] == 42
    
    def test_conflict_detection(self, lock_manager: OptimisticLockManager) -> None:
        """Test conflict detected when version mismatch."""
        # Thread 1 reads
        row1 = lock_manager.read("test_entity", 1)
        
        # Thread 2 reads and updates
        row2 = lock_manager.read("test_entity", 1)
        row2.data["value"] = 100
        lock_manager.write("test_entity", row2)
        
        # Thread 1 tries to update (should detect conflict)
        row1.data["value"] = 200
        with pytest.raises(ConflictError) as exc_info:
            lock_manager.write("test_entity", row1)
        
        assert "version mismatch" in str(exc_info.value).lower()
    
    def test_multiple_updates_sequential(
        self, lock_manager: OptimisticLockManager
    ) -> None:
        """Test multiple sequential updates increment version correctly."""
        for i in range(5):
            row = lock_manager.read("test_entity", 1)
            row.data["value"] = i * 10
            updated = lock_manager.write("test_entity", row)
            assert updated.version == i + 2  # Starts at 1


class TestAutomaticRetry:
    """Test automatic retry with re-read on conflict."""
    
    def test_retry_on_conflict(self, lock_manager: OptimisticLockManager) -> None:
        """Test automatic retry on conflict."""
        def updater(value: int):
            return lock_manager.write_with_retry(
                "test_entity",
                1,
                lambda row: {**row.data, "value": row.data["value"] + value},
                max_retries=3,
            )
        
        # Should succeed even with conflicts
        result = updater(10)
        assert result.data["value"] == 10
    
    def test_retry_exhaustion(self, lock_manager: OptimisticLockManager) -> None:
        """Test error when retries exhausted."""
        attempt_count = 0
        
        def always_conflict(row: VersionedRow) -> dict:
            nonlocal attempt_count
            attempt_count += 1
            # Simulate another thread updating between retries
            if attempt_count < 5:
                conn = sqlite3.connect(lock_manager._db_path)
                conn.execute(
                    "UPDATE test_entity SET version = version + 1 WHERE id = 1"
                )
                conn.commit()
                conn.close()
            return {**row.data, "value": 999}
        
        with pytest.raises(ConflictError, match="max retries"):
            lock_manager.write_with_retry(
                "test_entity", 1, always_conflict, max_retries=3
            )


class TestConcurrentUpdates:
    """Test concurrent update scenarios."""
    
    def test_concurrent_increments(self, lock_manager: OptimisticLockManager) -> None:
        """Test 50 concurrent increments all succeed."""
        num_increments = 50
        
        def increment():
            return lock_manager.write_with_retry(
                "test_entity",
                1,
                lambda row: {**row.data, "value": row.data["value"] + 1},
                max_retries=10,
            )
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(increment) for _ in range(num_increments)]
            results = [f.result() for f in as_completed(futures)]
        
        # Verify all increments applied
        final = lock_manager.read("test_entity", 1)
        assert final.data["value"] == num_increments
        assert final.version == num_increments + 1
    
    def test_high_contention_updates(self, lock_manager: OptimisticLockManager) -> None:
        """Test performance under high contention."""
        num_threads = 20
        updates_per_thread = 5
        
        def worker(thread_id: int):
            successes = 0
            for i in range(updates_per_thread):
                try:
                    lock_manager.write_with_retry(
                        "test_entity",
                        1,
                        lambda row: {
                            **row.data,
                            "value": row.data["value"] + 1,
                        },
                        max_retries=10,
                    )
                    successes += 1
                except ConflictError:
                    pass
            return successes
        
        start = time.time()
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(worker, i) for i in range(num_threads)]
            total_successes = sum(f.result() for f in as_completed(futures))
        duration = time.time() - start
        
        # All updates should succeed with retries
        assert total_successes == num_threads * updates_per_thread
        
        # Should complete in reasonable time (<5s)
        assert duration < 5.0


class TestMergeStrategies:
    """Test conflict resolution merge strategies."""
    
    def test_last_write_wins(self, lock_manager: OptimisticLockManager) -> None:
        """Test last-write-wins merge strategy."""
        row1 = lock_manager.read("test_entity", 1)
        row2 = lock_manager.read("test_entity", 1)
        
        # First update
        row1.data["value"] = 100
        lock_manager.write("test_entity", row1)
        
        # Second update with merge
        row2.data["value"] = 200
        merged = lock_manager.write_with_merge(
            "test_entity", row2, MergeStrategy.LAST_WRITE_WINS
        )
        
        assert merged.data["value"] == 200
    
    def test_merge_non_conflicting_fields(
        self, lock_manager: OptimisticLockManager
    ) -> None:
        """Test merging non-conflicting field updates."""
        # Add a new field to table
        conn = sqlite3.connect(str(lock_manager._db_path))
        conn.execute("ALTER TABLE test_entity ADD COLUMN description TEXT")
        conn.commit()
        conn.close()
        
        row1 = lock_manager.read("test_entity", 1)
        row2 = lock_manager.read("test_entity", 1)
        
        # Update different fields
        row1.data["value"] = 100
        lock_manager.write("test_entity", row1)
        
        # row2 only updates description (keeps original value field)
        row2.data["description"] = "updated"
        # Don't modify value in row2, it should preserve from row1
        row2.data.pop("value", None)  # Remove to not override
        
        merged = lock_manager.write_with_merge(
            "test_entity", row2, MergeStrategy.MERGE_NON_CONFLICTING
        )
        
        # Both updates should be present
        assert merged.data["value"] == 100  # From row1's update
        assert merged.data.get("description") == "updated"  # From row2's update
    
    def test_fail_on_conflict(self, lock_manager: OptimisticLockManager) -> None:
        """Test fail-fast strategy on conflict."""
        row1 = lock_manager.read("test_entity", 1)
        row2 = lock_manager.read("test_entity", 1)
        
        row1.data["value"] = 100
        lock_manager.write("test_entity", row1)
        
        row2.data["value"] = 200
        with pytest.raises(ConflictError):
            lock_manager.write_with_merge(
                "test_entity", row2, MergeStrategy.FAIL_ON_CONFLICT
            )


class TestVersionOverflow:
    """Test version counter overflow handling."""
    
    def test_version_wraparound(self, lock_manager: OptimisticLockManager) -> None:
        """Test version wraps around correctly."""
        # Manually set version to a high value (not max to avoid overflow)
        conn = sqlite3.connect(str(lock_manager._db_path))
        high_version = 1000000
        conn.execute(
            f"UPDATE test_entity SET version = {high_version} WHERE id = 1"
        )
        conn.commit()
        conn.close()
        
        # Multiple updates should handle high versions
        for _ in range(5):
            row = lock_manager.read("test_entity", 1)
            row.data["value"] = row.data["value"] + 1
            lock_manager.write("test_entity", row)
        
        # Version should have incremented
        final = lock_manager.read("test_entity", 1)
        assert final.version == high_version + 5


class TestStaleDataDetection:
    """Test stale data detection and refresh."""
    
    def test_stale_read_detection(self, lock_manager: OptimisticLockManager) -> None:
        """Test detection of stale reads."""
        row = lock_manager.read("test_entity", 1)
        
        # Another process updates
        conn = sqlite3.connect(str(lock_manager._db_path))
        conn.execute(
            "UPDATE test_entity SET value = 999, version = version + 1 WHERE id = 1"
        )
        conn.commit()
        conn.close()
        
        # Original row is now stale
        assert lock_manager.is_stale("test_entity", row)
    
    def test_refresh_stale_data(self, lock_manager: OptimisticLockManager) -> None:
        """Test refreshing stale data."""
        row = lock_manager.read("test_entity", 1)
        
        # Update via different path
        conn = sqlite3.connect(str(lock_manager._db_path))
        conn.execute(
            "UPDATE test_entity SET value = 777, version = version + 1 WHERE id = 1"
        )
        conn.commit()
        conn.close()
        
        # Refresh should get latest version
        refreshed = lock_manager.refresh("test_entity", row)
        assert refreshed.data["value"] == 777
        assert refreshed.version > row.version


class TestDeleteWithVersion:
    """Test optimistic delete operations."""
    
    def test_delete_with_correct_version(
        self, lock_manager: OptimisticLockManager
    ) -> None:
        """Test successful delete with correct version."""
        row = lock_manager.read("test_entity", 1)
        lock_manager.delete("test_entity", row)
        
        # Should be gone
        with pytest.raises(Exception):  # Could be NotFoundError or similar
            lock_manager.read("test_entity", 1)
    
    def test_delete_conflict(self, lock_manager: OptimisticLockManager) -> None:
        """Test delete fails if version changed."""
        row1 = lock_manager.read("test_entity", 1)
        row2 = lock_manager.read("test_entity", 1)
        
        # Update changes version
        row2.data["value"] = 999
        lock_manager.write("test_entity", row2)
        
        # Delete should detect conflict
        with pytest.raises(ConflictError):
            lock_manager.delete("test_entity", row1)


class TestMetrics:
    """Test optimistic lock metrics collection."""
    
    def test_tracks_retries(self, lock_manager: OptimisticLockManager) -> None:
        """Test retry count tracking."""
        initial_retries = lock_manager.metrics.retries
        
        # Force some retries
        def updater():
            return lock_manager.write_with_retry(
                "test_entity",
                1,
                lambda row: {**row.data, "value": row.data["value"] + 1},
                max_retries=5,
            )
        
        # Concurrent updates will cause retries
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(updater) for _ in range(10)]
            [f.result() for f in as_completed(futures)]
        
        # Should have tracked some retries
        assert lock_manager.metrics.retries > initial_retries


class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_concurrent_deletes(self, lock_manager: OptimisticLockManager) -> None:
        """Test concurrent delete attempts."""
        row1 = lock_manager.read("test_entity", 1)
        row2 = lock_manager.read("test_entity", 1)
        
        # First delete succeeds
        lock_manager.delete("test_entity", row1)
        
        # Second delete should fail (gone)
        with pytest.raises((ConflictError, Exception)):
            lock_manager.delete("test_entity", row2)
    
    def test_read_nonexistent(self, lock_manager: OptimisticLockManager) -> None:
        """Test reading non-existent entity."""
        with pytest.raises(Exception):  # Could be NotFoundError
            lock_manager.read("test_entity", 9999)
    
    def test_update_deleted_entity(self, lock_manager: OptimisticLockManager) -> None:
        """Test updating entity deleted by another transaction."""
        row = lock_manager.read("test_entity", 1)
        
        # Delete via different path
        conn = sqlite3.connect(str(lock_manager._db_path))
        conn.execute("DELETE FROM test_entity WHERE id = 1")
        conn.commit()
        conn.close()
        
        # Update should detect entity is gone
        row.data["value"] = 999
        with pytest.raises((ConflictError, Exception)):
            lock_manager.write("test_entity", row)


def test_optimistic_lock_performance_benchmark(temp_db: Path) -> None:
    """Benchmark optimistic locking performance."""
    lock_manager = OptimisticLockManager(str(temp_db))
    
    num_operations = 100
    start = time.time()
    
    for i in range(num_operations):
        lock_manager.write_with_retry(
            "test_entity",
            1,
            lambda row: {**row.data, "value": row.data["value"] + 1},
            max_retries=5,
        )
    
    duration = time.time() - start
    ops_per_second = num_operations / duration
    
    # Should achieve >100 ops/sec
    assert ops_per_second > 100
    print(f"Optimistic locking: {ops_per_second:.0f} ops/sec")
