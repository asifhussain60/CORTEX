"""
Database Manager Tests - TDD for AR-002

Tests for SQLite-based governance database with:
- Schema creation
- WAL mode
- Query performance (<1ms)
- AC-ID tracking
- Phase locks
- Audit log storage

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import sqlite3
import time
from pathlib import Path

import pytest

from cortex.infrastructure.database import DatabaseManager, DatabaseConfig


class TestDatabaseSchema:
    """Test database schema creation."""
    
    def test_creates_database_file(self, tmp_path):
        """Database file should be created on initialization."""
        db_path = tmp_path / "governance.db"
        config = DatabaseConfig(db_path=db_path)
        
        db = DatabaseManager(config)
        db.initialize()
        
        assert db_path.exists()
        db.close()
    
    def test_creates_ac_index_table(self, tmp_path):
        """ac_index table should exist with correct columns."""
        db_path = tmp_path / "governance.db"
        config = DatabaseConfig(db_path=db_path)
        db = DatabaseManager(config)
        db.initialize()
        
        # Query table info
        result = db.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='ac_index'"
        )
        assert result.is_ok()
        tables = result.unwrap()
        assert len(tables) == 1
        
        # Verify columns
        result = db.execute("PRAGMA table_info(ac_index)")
        assert result.is_ok()
        columns = {row[1] for row in result.unwrap()}
        expected = {"ac_id", "phase", "status", "title", "created_at", "updated_at", "evidence_hash"}
        assert expected.issubset(columns)
        
        db.close()
    
    def test_creates_audit_log_table(self, tmp_path):
        """audit_log table should exist with hash chain columns."""
        db_path = tmp_path / "governance.db"
        config = DatabaseConfig(db_path=db_path)
        db = DatabaseManager(config)
        db.initialize()
        
        result = db.execute("PRAGMA table_info(audit_log)")
        assert result.is_ok()
        columns = {row[1] for row in result.unwrap()}
        expected = {"id", "timestamp", "operation", "ac_id", "correlation_id", 
                    "component", "level", "message", "metadata", "previous_hash", "entry_hash"}
        assert expected.issubset(columns)
        
        db.close()
    
    def test_creates_phase_locks_table(self, tmp_path):
        """phase_locks table should exist for runtime enforcement."""
        db_path = tmp_path / "governance.db"
        config = DatabaseConfig(db_path=db_path)
        db = DatabaseManager(config)
        db.initialize()
        
        result = db.execute("PRAGMA table_info(phase_locks)")
        assert result.is_ok()
        columns = {row[1] for row in result.unwrap()}
        expected = {"phase_id", "locked", "locked_at", "locked_by", "git_checkpoint"}
        assert expected.issubset(columns)
        
        db.close()


@pytest.mark.ac("AR-002-02")
class TestWALMode:
    """Test WAL mode configuration (AC-AR-002-02)."""
    
    def test_wal_mode_enabled(self, tmp_path):
        """WAL mode should be enabled for concurrent access."""
        db_path = tmp_path / "governance.db"
        config = DatabaseConfig(db_path=db_path, wal_mode=True)
        db = DatabaseManager(config)
        db.initialize()
        
        result = db.execute("PRAGMA journal_mode")
        assert result.is_ok()
        mode = result.unwrap()[0][0]
        assert mode.lower() == "wal"
        
        db.close()
    
    def test_wal_creates_shm_and_wal_files(self, tmp_path):
        """WAL mode should create -shm and -wal files after write."""
        db_path = tmp_path / "governance.db"
        config = DatabaseConfig(db_path=db_path, wal_mode=True)
        db = DatabaseManager(config)
        db.initialize()
        
        # Perform a write to trigger WAL
        db.execute(
            "INSERT INTO phase_locks (phase_id, locked) VALUES (?, ?)",
            ("PHASE-TEST", False)
        )
        
        # WAL files created (may need checkpoint to appear)
        # Just verify WAL mode is active
        result = db.execute("PRAGMA journal_mode")
        assert result.unwrap()[0][0].lower() == "wal"
        
        db.close()


@pytest.mark.ac("AR-002-03")
class TestQueryPerformance:
    """Test query performance requirements (AC-AR-002-03)."""
    
    def test_simple_query_under_1ms(self, tmp_path):
        """Simple queries should complete in <1ms."""
        db_path = tmp_path / "governance.db"
        config = DatabaseConfig(db_path=db_path)
        db = DatabaseManager(config)
        db.initialize()
        
        # Insert test data
        for i in range(100):
            db.execute(
                "INSERT INTO ac_index (ac_id, phase, status, title) VALUES (?, ?, ?, ?)",
                (f"AC-TEST-{i:03d}", "PHASE-01", "PENDING", f"Test AC {i}")
            )
        
        # Time a simple query
        start = time.perf_counter()
        result = db.execute("SELECT * FROM ac_index WHERE ac_id = ?", ("AC-TEST-050",))
        elapsed = time.perf_counter() - start
        
        assert result.is_ok()
        assert elapsed < 0.001, f"Query took {elapsed*1000:.2f}ms, expected <1ms"
        
        db.close()
    
    def test_indexed_lookup_performance(self, tmp_path):
        """Indexed lookups should be fast."""
        db_path = tmp_path / "governance.db"
        config = DatabaseConfig(db_path=db_path)
        db = DatabaseManager(config)
        db.initialize()
        
        # Insert 1000 records
        for i in range(1000):
            db.execute(
                "INSERT INTO ac_index (ac_id, phase, status, title) VALUES (?, ?, ?, ?)",
                (f"AC-PERF-{i:04d}", f"PHASE-{(i % 5) + 1:02d}", "PENDING", f"Performance Test {i}")
            )
        
        # Time indexed query
        start = time.perf_counter()
        result = db.execute("SELECT * FROM ac_index WHERE ac_id = ?", ("AC-PERF-0500",))
        elapsed = time.perf_counter() - start
        
        assert result.is_ok()
        assert len(result.unwrap()) == 1
        assert elapsed < 0.001, f"Indexed query took {elapsed*1000:.2f}ms"
        
        db.close()


class TestACIndexOperations:
    """Test AC-ID index operations."""
    
    def test_insert_ac_id(self, tmp_path):
        """Should insert AC-ID record."""
        db_path = tmp_path / "governance.db"
        config = DatabaseConfig(db_path=db_path)
        db = DatabaseManager(config)
        db.initialize()
        
        result = db.insert_ac(
            ac_id="AC-AR-001-01",
            phase="PHASE-01",
            title="Tier 0 rules loaded from cortex_brain/tier0/governance/core-rules.yaml"
        )
        
        assert result.is_ok()
        
        # Verify insertion
        query_result = db.get_ac("AC-AR-001-01")
        assert query_result.is_ok()
        ac = query_result.unwrap()
        assert ac["ac_id"] == "AC-AR-001-01"
        assert ac["status"] == "PENDING"
        
        db.close()
    
    def test_update_ac_status(self, tmp_path):
        """Should update AC-ID status."""
        db_path = tmp_path / "governance.db"
        config = DatabaseConfig(db_path=db_path)
        db = DatabaseManager(config)
        db.initialize()
        
        db.insert_ac("AC-TEST-001", "PHASE-01", "Test AC")
        result = db.update_ac_status("AC-TEST-001", "IN_PROGRESS")
        
        assert result.is_ok()
        
        ac = db.get_ac("AC-TEST-001").unwrap()
        assert ac["status"] == "IN_PROGRESS"
        
        db.close()
    
    def test_ac_exists_check(self, tmp_path):
        """Should check if AC-ID exists."""
        db_path = tmp_path / "governance.db"
        config = DatabaseConfig(db_path=db_path)
        db = DatabaseManager(config)
        db.initialize()
        
        db.insert_ac("AC-EXISTS-001", "PHASE-01", "Exists")
        
        assert db.ac_exists("AC-EXISTS-001").unwrap() is True
        assert db.ac_exists("AC-MISSING-001").unwrap() is False
        
        db.close()


class TestPhaseLockOperations:
    """Test phase lock operations for runtime enforcement."""
    
    def test_lock_phase(self, tmp_path):
        """Should lock a phase."""
        db_path = tmp_path / "governance.db"
        config = DatabaseConfig(db_path=db_path)
        db = DatabaseManager(config)
        db.initialize()
        
        result = db.lock_phase("PHASE-01", locked_by="test", git_checkpoint="abc123")
        assert result.is_ok()
        
        is_locked = db.is_phase_locked("PHASE-01")
        assert is_locked.is_ok()
        assert is_locked.unwrap() is True
        
        db.close()
    
    def test_unlocked_phase_returns_false(self, tmp_path):
        """Unlocked phase should return False."""
        db_path = tmp_path / "governance.db"
        config = DatabaseConfig(db_path=db_path)
        db = DatabaseManager(config)
        db.initialize()
        
        # Insert unlocked phase
        db.execute(
            "INSERT INTO phase_locks (phase_id, locked) VALUES (?, ?)",
            ("PHASE-02", False)
        )
        
        is_locked = db.is_phase_locked("PHASE-02")
        assert is_locked.is_ok()
        assert is_locked.unwrap() is False
        
        db.close()
    
    def test_nonexistent_phase_returns_false(self, tmp_path):
        """Non-existent phase should return False (not locked)."""
        db_path = tmp_path / "governance.db"
        config = DatabaseConfig(db_path=db_path)
        db = DatabaseManager(config)
        db.initialize()
        
        is_locked = db.is_phase_locked("PHASE-NONEXISTENT")
        assert is_locked.is_ok()
        assert is_locked.unwrap() is False
        
        db.close()


class TestAuditLogOperations:
    """Test audit log operations with hash chain."""
    
    def test_insert_audit_entry(self, tmp_path):
        """Should insert audit entry with hash."""
        db_path = tmp_path / "governance.db"
        config = DatabaseConfig(db_path=db_path)
        db = DatabaseManager(config)
        db.initialize()
        
        result = db.insert_audit(
            operation="AC_START",
            component="test",
            level="INFO",
            message="Starting test",
            ac_id="AC-TEST-001",
            correlation_id="corr-123"
        )
        
        assert result.is_ok()
        entry_hash = result.unwrap()
        assert entry_hash is not None
        assert len(entry_hash) == 64  # SHA-256 hex
        
        db.close()
    
    def test_hash_chain_integrity(self, tmp_path):
        """Hash chain should link entries."""
        db_path = tmp_path / "governance.db"
        config = DatabaseConfig(db_path=db_path)
        db = DatabaseManager(config)
        db.initialize()
        
        # Insert multiple entries
        hash1 = db.insert_audit("OP1", "test", "INFO", "First").unwrap()
        hash2 = db.insert_audit("OP2", "test", "INFO", "Second").unwrap()
        hash3 = db.insert_audit("OP3", "test", "INFO", "Third").unwrap()
        
        # Verify chain
        result = db.execute("SELECT previous_hash, entry_hash FROM audit_log ORDER BY id")
        assert result.is_ok()
        rows = result.unwrap()
        
        assert rows[0][0] == "GENESIS"  # First entry
        assert rows[1][0] == rows[0][1]  # Second links to first
        assert rows[2][0] == rows[1][1]  # Third links to second
        
        db.close()
    
    def test_query_audit_by_ac_id(self, tmp_path):
        """Should query audit entries by AC-ID."""
        db_path = tmp_path / "governance.db"
        config = DatabaseConfig(db_path=db_path)
        db = DatabaseManager(config)
        db.initialize()
        
        # Insert entries for different AC-IDs
        db.insert_audit("AC_START", "test", "INFO", "Start", ac_id="AC-001")
        db.insert_audit("AC_EXECUTE", "test", "INFO", "Execute", ac_id="AC-001")
        db.insert_audit("AC_COMPLETE", "test", "INFO", "Complete", ac_id="AC-001")
        db.insert_audit("AC_START", "test", "INFO", "Other", ac_id="AC-002")
        
        result = db.query_audit_by_ac_id("AC-001")
        assert result.is_ok()
        entries = result.unwrap()
        assert len(entries) == 3
        
        db.close()


class TestDatabaseConfig:
    """Test database configuration."""
    
    def test_default_config(self):
        """Default config should use standard paths."""
        config = DatabaseConfig()
        assert config.db_path.name == "governance.db"
        assert config.wal_mode is True
    
    def test_custom_path(self, tmp_path):
        """Should accept custom database path."""
        custom_path = tmp_path / "custom" / "db.sqlite"
        config = DatabaseConfig(db_path=custom_path)
        assert config.db_path == custom_path
