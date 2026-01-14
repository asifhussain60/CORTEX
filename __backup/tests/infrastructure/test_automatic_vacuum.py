"""
Tests for AC-AUDIT-005: Automatic Vacuum

Validates retention policy enforcement, event deletion, and vacuum statistics.
"""

import pytest
import sqlite3
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

from src.infrastructure.automatic_vacuum import (
    AutomaticVacuum,
    RetentionPolicy,
    create_vacuum_scheduler,
)


@pytest.fixture
def temp_db():
    """Create temporary audit database for testing."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    
    # Initialize schema
    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE audit_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            level TEXT NOT NULL,
            category TEXT,
            message TEXT,
            actor TEXT,
            resource TEXT
        )
    """)
    conn.commit()
    conn.close()
    
    yield db_path
    
    # Cleanup
    Path(db_path).unlink(missing_ok=True)


@pytest.fixture
def vacuum_system(temp_db):
    """Create vacuum system with test database."""
    return AutomaticVacuum(db_path=temp_db, dry_run=False)


def insert_event(db_path: str, timestamp: str, level: str, message: str = "test"):
    """Helper to insert audit event."""
    conn = sqlite3.connect(db_path)
    conn.execute(
        "INSERT INTO audit_events (timestamp, level, message) VALUES (?, ?, ?)",
        (timestamp, level, message)
    )
    conn.commit()
    conn.close()


class TestRetentionPolicy:
    """Tests for RetentionPolicy dataclass."""
    
    def test_valid_retention_policy(self):
        """Test creating valid retention policy."""
        policy = RetentionPolicy("ERROR", 90)
        assert policy.level == "ERROR"
        assert policy.days == 90
    
    def test_invalid_level(self):
        """Test rejection of invalid log level."""
        with pytest.raises(ValueError, match="Invalid log level"):
            RetentionPolicy("INVALID", 30)
    
    def test_invalid_days(self):
        """Test rejection of invalid day count."""
        with pytest.raises(ValueError, match="Retention days must be"):
            RetentionPolicy("ERROR", 0)


class TestAutomaticVacuum:
    """Tests for AutomaticVacuum core functionality."""
    
    def test_init_default_policies(self, temp_db):
        """Test vacuum initializes with default retention policies."""
        vacuum = AutomaticVacuum(db_path=temp_db)
        
        assert vacuum.retention_policies["CRITICAL"] == 90
        assert vacuum.retention_policies["ERROR"] == 90
        assert vacuum.retention_policies["WARNING"] == 60
        assert vacuum.retention_policies["INFO"] == 30
        assert vacuum.retention_policies["DEBUG"] == 7
        assert vacuum.retention_policies["TRACE"] == 1
    
    def test_init_custom_policies(self, temp_db):
        """Test vacuum with custom retention policies."""
        custom = {"ERROR": 180, "WARNING": 45}
        vacuum = AutomaticVacuum(db_path=temp_db, retention_policies=custom)
        
        assert vacuum.retention_policies["ERROR"] == 180
        assert vacuum.retention_policies["WARNING"] == 45
        assert vacuum.retention_policies["DEBUG"] == 7  # Default unchanged
    
    def test_calculate_cutoff_date(self, vacuum_system):
        """Test cutoff date calculation."""
        now = datetime.utcnow()
        
        # ERROR should be 90 days back
        cutoff_error = vacuum_system.calculate_cutoff_date("ERROR")
        expected_error = now - timedelta(days=90)
        
        # Verify within 1 minute precision
        assert abs((cutoff_error - expected_error).total_seconds()) < 60
        
        # TRACE should be 1 day back
        cutoff_trace = vacuum_system.calculate_cutoff_date("TRACE")
        expected_trace = now - timedelta(days=1)
        
        assert abs((cutoff_trace - expected_trace).total_seconds()) < 60
    
    def test_get_events_to_delete_empty(self, vacuum_system):
        """Test getting events when none exist."""
        events = vacuum_system.get_events_to_delete("ERROR")
        assert events == []
    
    def test_get_events_to_delete_old_events(self, temp_db, vacuum_system):
        """Test retrieving old events for deletion."""
        # Insert old and new TRACE events
        old_trace = (datetime.utcnow() - timedelta(days=2)).isoformat()
        new_trace = (datetime.utcnow() - timedelta(hours=12)).isoformat()
        
        insert_event(temp_db, old_trace, "TRACE", "old event")
        insert_event(temp_db, new_trace, "TRACE", "new event")
        
        # Only old event should be in deletion list
        events = vacuum_system.get_events_to_delete("TRACE")
        assert len(events) == 1
        assert events[0]["message"] == "old event"
    
    def test_delete_events_dry_run(self, temp_db, vacuum_system):
        """Test dry-run mode prevents actual deletion."""
        vacuum_system.dry_run = True
        
        old_time = (datetime.utcnow() - timedelta(days=8)).isoformat()
        insert_event(temp_db, old_time, "DEBUG", "to_delete")
        
        deleted, examined = vacuum_system.delete_events("DEBUG")
        
        assert deleted == 1
        assert examined == 1
        
        # Verify event still exists
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM audit_events")
        count = cursor.fetchone()[0]
        conn.close()
        
        assert count == 1  # Not actually deleted in dry run
    
    def test_delete_events_actual(self, temp_db):
        """Test actual deletion of old events."""
        vacuum = AutomaticVacuum(db_path=temp_db, dry_run=False)
        
        old_time = (datetime.utcnow() - timedelta(days=8)).isoformat()
        new_time = datetime.utcnow().isoformat()
        
        insert_event(temp_db, old_time, "DEBUG", "old")
        insert_event(temp_db, new_time, "DEBUG", "new")
        
        deleted, examined = vacuum.delete_events("DEBUG")
        
        assert deleted == 1
        assert examined == 1
        
        # Verify only new event remains
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM audit_events")
        count = cursor.fetchone()[0]
        conn.close()
        
        assert count == 1
    
    def test_delete_events_unknown_level(self, vacuum_system):
        """Test error handling for unknown log level."""
        with pytest.raises(ValueError, match="Unknown log level"):
            vacuum_system.delete_events("INVALID")


class TestVacuumExecution:
    """Tests for complete vacuum execution."""
    
    def test_run_vacuum_multiple_levels(self, temp_db):
        """Test running vacuum across multiple log levels."""
        vacuum = AutomaticVacuum(db_path=temp_db, dry_run=False)
        
        # Insert events at different levels
        old_time = (datetime.utcnow() - timedelta(days=100)).isoformat()
        new_time = datetime.utcnow().isoformat()
        
        # Old CRITICAL (should delete - 90 day policy)
        insert_event(temp_db, old_time, "CRITICAL", "old critical")
        # New CRITICAL (keep)
        insert_event(temp_db, new_time, "CRITICAL", "new critical")
        
        # Old TRACE (should delete - 1 day policy)
        insert_event(temp_db, old_time, "TRACE", "old trace")
        # New INFO (keep - 30 day policy)
        insert_event(temp_db, new_time, "INFO", "new info")
        
        results = vacuum.run_vacuum()
        
        assert "CRITICAL" in results
        assert results["CRITICAL"][0] >= 1  # At least 1 deleted
        assert results["TRACE"][0] >= 1  # At least 1 deleted
        
        # Verify final count (2 events remain: new CRITICAL, new INFO)
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM audit_events")
        final_count = cursor.fetchone()[0]
        conn.close()
        
        assert final_count == 2
    
    def test_get_vacuum_stats(self, temp_db):
        """Test vacuum statistics reporting."""
        vacuum = AutomaticVacuum(db_path=temp_db)
        
        old_time = (datetime.utcnow() - timedelta(days=100)).isoformat()
        insert_event(temp_db, old_time, "ERROR", "old error")
        
        stats = vacuum.get_vacuum_stats()
        
        assert "ERROR" in stats
        assert stats["ERROR"]["events_to_delete"] >= 1
        assert stats["ERROR"]["oldest_event"] is not None
        assert stats["ERROR"]["cutoff_date"] is not None
        assert stats["ERROR"]["retention_days"] == 90
    
    def test_get_vacuum_stats_empty(self, temp_db):
        """Test stats when database is empty."""
        vacuum = AutomaticVacuum(db_path=temp_db)
        stats = vacuum.get_vacuum_stats()
        
        assert "ERROR" in stats
        assert stats["ERROR"]["events_to_delete"] == 0


class TestVacuumScheduler:
    """Tests for vacuum scheduler configuration."""
    
    def test_create_vacuum_scheduler_default(self):
        """Test scheduler creation with defaults."""
        config = create_vacuum_scheduler()
        
        assert config["type"] == "scheduler"
        assert config["interval_hours"] == 24
        assert config["action"] == "automatic_vacuum"
        assert config["enabled"] is True
    
    def test_create_vacuum_scheduler_custom_interval(self):
        """Test scheduler with custom interval."""
        config = create_vacuum_scheduler(interval_hours=12)
        
        assert config["interval_hours"] == 12
        assert config["action"] == "automatic_vacuum"
