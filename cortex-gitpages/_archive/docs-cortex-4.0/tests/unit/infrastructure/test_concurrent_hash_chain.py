"""
Unit tests for Concurrent Hash Chain Integrity (AC-STATE-002-03).

Tests audit log hash chain remains valid under concurrent writes through
atomic append-only operations and integrity verification.

Author: Asif Hussain
Copyright © 2026 Asif Hussain. All rights reserved.
"""

import pytest
import sqlite3
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from cortex.infrastructure.audit_hash_chain import (
    AuditHashChain,
    HashChainBroken,
)


@pytest.fixture
def temp_db(tmp_path: Path) -> Path:
    """Create temporary database for testing."""
    db_path = tmp_path / "test_hash_chain.db"
    conn = sqlite3.connect(str(db_path))
    conn.execute("""
        CREATE TABLE audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            action TEXT NOT NULL,
            data TEXT,
            hash TEXT NOT NULL,
            prev_hash TEXT
        )
    """)
    conn.commit()
    conn.close()
    return db_path


@pytest.fixture
def hash_chain(temp_db: Path) -> AuditHashChain:
    """Create audit hash chain manager."""
    return AuditHashChain(str(temp_db))


class TestBasicHashChain:
    """Test basic hash chain operations."""
    
    def test_append_first_entry(self, hash_chain: AuditHashChain) -> None:
        """Test appending first entry to empty chain."""
        entry_id = hash_chain.append("TEST_ACTION", {"key": "value"})
        assert entry_id > 0
        assert hash_chain.verify_integrity()
    
    def test_append_sequential_entries(self, hash_chain: AuditHashChain) -> None:
        """Test multiple sequential appends."""
        for i in range(10):
            hash_chain.append(f"ACTION_{i}", {"counter": i})
        
        assert hash_chain.verify_integrity()
        assert hash_chain.get_chain_length() == 10
    
    def test_hash_chain_linkage(self, hash_chain: AuditHashChain) -> None:
        """Test each entry links to previous correctly."""
        id1 = hash_chain.append("ACTION_1", {})
        id2 = hash_chain.append("ACTION_2", {})
        
        entry1 = hash_chain.get_entry(id1)
        entry2 = hash_chain.get_entry(id2)
        
        assert entry2["prev_hash"] == entry1["hash"]


class TestConcurrentAppends:
    """Test concurrent hash chain appends."""
    
    def test_100_concurrent_appends(self, hash_chain: AuditHashChain) -> None:
        """Test 100 concurrent appends maintain integrity."""
        num_appends = 100
        
        def append_entry(i: int):
            return hash_chain.append(f"CONCURRENT_{i}", {"index": i})
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(append_entry, i) for i in range(num_appends)]
            results = [f.result() for f in as_completed(futures)]
        
        # All appends succeeded
        assert len(results) == num_appends
        assert len(set(results)) == num_appends  # All unique IDs
        
        # Chain integrity maintained
        assert hash_chain.verify_integrity()
        assert hash_chain.get_chain_length() == num_appends
    
    def test_high_contention_appends(self, hash_chain: AuditHashChain) -> None:
        """Test hash chain under high contention."""
        num_threads = 20
        appends_per_thread = 10
        
        def worker(thread_id: int):
            for i in range(appends_per_thread):
                hash_chain.append(f"THREAD_{thread_id}_ACTION_{i}", {})
        
        threads = [threading.Thread(target=worker, args=(i,)) for i in range(num_threads)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        assert hash_chain.verify_integrity()
        assert hash_chain.get_chain_length() == num_threads * appends_per_thread


class TestIntegrityVerification:
    """Test hash chain integrity verification."""
    
    def test_detects_modified_entry(self, hash_chain: AuditHashChain) -> None:
        """Test detection of modified entry."""
        hash_chain.append("ACTION_1", {})
        entry_id = hash_chain.append("ACTION_2", {})
        hash_chain.append("ACTION_3", {})
        
        # Tamper with entry - modify hash to break chain
        conn = sqlite3.connect(str(hash_chain._db_path))
        conn.execute(f"UPDATE audit_log SET hash = 'tampered_hash' WHERE id = {entry_id}")
        conn.commit()
        conn.close()
        
        # Should detect break
        with pytest.raises(HashChainBroken):
            hash_chain.verify_integrity(raise_on_error=True)
    
    def test_detects_missing_entry(self, hash_chain: AuditHashChain) -> None:
        """Test detection of deleted entry."""
        hash_chain.append("ACTION_1", {})
        entry_id = hash_chain.append("ACTION_2", {})
        hash_chain.append("ACTION_3", {})
        
        # Delete entry
        conn = sqlite3.connect(str(hash_chain._db_path))
        conn.execute(f"DELETE FROM audit_log WHERE id = {entry_id}")
        conn.commit()
        conn.close()
        
        # Should detect break
        assert not hash_chain.verify_integrity()
    
    def test_repair_broken_chain(self, hash_chain: AuditHashChain) -> None:
        """Test automatic chain repair."""
        for i in range(5):
            hash_chain.append(f"ACTION_{i}", {})
        
        # Break chain
        conn = sqlite3.connect(str(hash_chain._db_path))
        conn.execute("UPDATE audit_log SET hash = 'invalid' WHERE id = 3")
        conn.commit()
        conn.close()
        
        # Repair
        repaired = hash_chain.repair_from_break()
        assert repaired > 0
        assert hash_chain.verify_integrity()


class TestThreadSafety:
    """Test thread-safe operations."""
    
    def test_no_race_in_last_hash_retrieval(self, hash_chain: AuditHashChain) -> None:
        """Test thread-safe last hash retrieval."""
        results = []
        barrier = threading.Barrier(10)
        
        def append_and_verify():
            barrier.wait()
            entry_id = hash_chain.append("CONCURRENT", {})
            results.append(entry_id)
        
        threads = [threading.Thread(target=append_and_verify) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # All appends successful, chain valid
        assert len(set(results)) == 10
        assert hash_chain.verify_integrity()
    
    def test_atomic_hash_calculation(self, hash_chain: AuditHashChain) -> None:
        """Test hash calculation is atomic under concurrent load."""
        num_appends = 50
        
        def concurrent_append(i: int):
            hash_chain.append(f"ACTION_{i}", {"index": i})
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            list(executor.map(concurrent_append, range(num_appends)))
        
        # Verify no duplicates or collisions
        conn = sqlite3.connect(str(hash_chain._db_path))
        cursor = conn.execute("SELECT hash, COUNT(*) as cnt FROM audit_log GROUP BY hash HAVING cnt > 1")
        duplicates = cursor.fetchall()
        conn.close()
        
        assert len(duplicates) == 0  # No duplicate hashes


class TestBackgroundVerification:
    """Test background integrity verification."""
    
    def test_continuous_verification(self, hash_chain: AuditHashChain) -> None:
        """Test background verifier runs correctly."""
        # Add entries
        for i in range(20):
            hash_chain.append(f"ACTION_{i}", {})
        
        # Start background verification
        hash_chain.start_background_verification(interval=0.1)
        
        import time
        time.sleep(0.5)  # Let it run
        
        hash_chain.stop_background_verification()
        
        # Should have completed at least one verification
        metrics = hash_chain.get_metrics()
        assert metrics["verifications"] > 0
        assert metrics["breaks_detected"] == 0


class TestMetrics:
    """Test hash chain metrics."""
    
    def test_tracks_appends(self, hash_chain: AuditHashChain) -> None:
        """Test append counter."""
        for i in range(10):
            hash_chain.append(f"ACTION_{i}", {})
        
        metrics = hash_chain.get_metrics()
        assert metrics["total_appends"] == 10
    
    def test_tracks_verifications(self, hash_chain: AuditHashChain) -> None:
        """Test verification counter."""
        hash_chain.append("ACTION", {})
        
        for _ in range(5):
            hash_chain.verify_integrity()
        
        metrics = hash_chain.get_metrics()
        assert metrics["verifications"] >= 5


def test_hash_chain_performance(temp_db: Path) -> None:
    """Benchmark hash chain performance."""
    hash_chain = AuditHashChain(str(temp_db))
    
    import time
    num_entries = 100
    start = time.time()
    
    for i in range(num_entries):
        hash_chain.append(f"PERF_TEST_{i}", {"index": i})
    
    duration = time.time() - start
    appends_per_sec = num_entries / duration
    
    # Should achieve >500 appends/sec
    assert appends_per_sec > 500
    assert hash_chain.verify_integrity()
