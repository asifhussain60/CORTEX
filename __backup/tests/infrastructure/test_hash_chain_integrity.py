"""
Tests for AC-AUDIT-007: Hash Chain Integrity

Validates cryptographic hash chain, tamper detection, and chain verification.
"""

import pytest
import sqlite3
import tempfile
import hashlib
from pathlib import Path
from datetime import datetime

from src.infrastructure.hash_chain_integrity import (
    HashChainIntegrity,
    HashChainEvent,
)


@pytest.fixture
def temp_chain_db():
    """Create temporary hash chain database."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    
    yield db_path
    
    # Cleanup
    Path(db_path).unlink(missing_ok=True)


@pytest.fixture
def chain_system(temp_chain_db):
    """Create hash chain system with test database."""
    return HashChainIntegrity(db_path=temp_chain_db)


class TestEventHashing:
    """Tests for event hash computation."""
    
    def test_compute_event_hash(self):
        """Test computing hash of event content."""
        hash1 = HashChainIntegrity.compute_event_hash(
            "2026-01-10T12:00:00",
            "INFO",
            "TEST",
            "Test message"
        )
        
        assert len(hash1) == 64  # SHA256 hex is 64 chars
        assert isinstance(hash1, str)
    
    def test_compute_event_hash_deterministic(self):
        """Test that same content produces same hash."""
        hash1 = HashChainIntegrity.compute_event_hash(
            "2026-01-10T12:00:00",
            "INFO",
            "TEST",
            "Test message"
        )
        
        hash2 = HashChainIntegrity.compute_event_hash(
            "2026-01-10T12:00:00",
            "INFO",
            "TEST",
            "Test message"
        )
        
        assert hash1 == hash2
    
    def test_compute_event_hash_sensitive_to_changes(self):
        """Test that hash changes with any content change."""
        hash1 = HashChainIntegrity.compute_event_hash(
            "2026-01-10T12:00:00",
            "INFO",
            "TEST",
            "Test message"
        )
        
        # Change message
        hash2 = HashChainIntegrity.compute_event_hash(
            "2026-01-10T12:00:00",
            "INFO",
            "TEST",
            "Different message"
        )
        
        assert hash1 != hash2
    
    def test_compute_event_hash_with_actor_and_resource(self, chain_system):
        """Test computing hash with actor and resource."""
        hash1 = chain_system.compute_event_hash(
            "2026-01-10T12:00:00",
            "ERROR",
            "SECURITY",
            "Unauthorized access",
            actor="user123",
            resource="/api/admin"
        )
        
        assert len(hash1) == 64
    
    def test_compute_chain_hash(self, chain_system):
        """Test computing chain hash that links events."""
        event_hash = "a" * 64
        prev_hash = "b" * 64
        
        chain_hash = chain_system.compute_chain_hash(event_hash, prev_hash)
        
        assert len(chain_hash) == 64
        assert isinstance(chain_hash, str)
    
    def test_compute_chain_hash_deterministic(self, chain_system):
        """Test chain hash is deterministic."""
        event_hash = "a" * 64
        prev_hash = "b" * 64
        
        chain_hash1 = chain_system.compute_chain_hash(event_hash, prev_hash)
        chain_hash2 = chain_system.compute_chain_hash(event_hash, prev_hash)
        
        assert chain_hash1 == chain_hash2


class TestChainDatabase:
    """Tests for hash chain database operations."""
    
    def test_initialize_chain_db(self, chain_system):
        """Test database initialization."""
        db_path = chain_system.initialize_chain_db()
        
        assert Path(db_path).exists()
        
        # Verify schema
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='hash_chain'"
        )
        assert cursor.fetchone() is not None
        
        conn.close()
    
    def test_append_to_chain_single_event(self, chain_system):
        """Test appending first event to chain."""
        result = chain_system.append_to_chain(
            "2026-01-10T12:00:00",
            "INFO",
            "TEST",
            "First event"
        )
        
        assert result["status"] == "appended"
        assert result["event_id"] == 1
        assert len(result["event_hash"]) == 64
        assert result["prev_event_hash"] == "0" * 64  # Genesis
    
    def test_append_to_chain_multiple_events(self, chain_system):
        """Test appending multiple events creates links."""
        # Append first event
        result1 = chain_system.append_to_chain(
            "2026-01-10T12:00:00",
            "INFO",
            "TEST",
            "Event 1"
        )
        
        # Append second event
        result2 = chain_system.append_to_chain(
            "2026-01-10T12:01:00",
            "INFO",
            "TEST",
            "Event 2"
        )
        
        # Verify chain link
        assert result2["prev_event_hash"] == result1["event_hash"]
        assert result2["event_id"] == 2
    
    def test_append_to_chain_with_metadata(self, chain_system):
        """Test appending event with actor and resource."""
        result = chain_system.append_to_chain(
            "2026-01-10T12:00:00",
            "ERROR",
            "SECURITY",
            "Authorization failed",
            actor="user123",
            resource="/api/admin"
        )
        
        assert result["status"] == "appended"
        assert result["event_id"] is not None


class TestChainVerification:
    """Tests for chain integrity verification."""
    
    def test_verify_chain_integrity_empty(self, chain_system):
        """Test verifying empty chain."""
        is_valid, results = chain_system.verify_chain_integrity()
        
        assert is_valid is True
        assert results["message"] == "Chain is empty"
    
    def test_verify_chain_integrity_single_event(self, chain_system):
        """Test verifying single event in chain."""
        chain_system.append_to_chain(
            "2026-01-10T12:00:00",
            "INFO",
            "TEST",
            "Single event"
        )
        
        is_valid, results = chain_system.verify_chain_integrity()
        
        assert is_valid is True
        assert results["events_verified"] == 1
        assert results["chain_valid"] is True
    
    def test_verify_chain_integrity_multiple_events(self, chain_system):
        """Test verifying chain with multiple events."""
        for i in range(5):
            chain_system.append_to_chain(
                f"2026-01-10T12:{i:02d}:00",
                "INFO",
                "TEST",
                f"Event {i}"
            )
        
        is_valid, results = chain_system.verify_chain_integrity()
        
        assert is_valid is True
        assert results["events_verified"] == 5
    
    def test_verify_detects_tampered_event_hash(self, chain_system, temp_chain_db):
        """Test that verification detects tampered event hash."""
        # Append events
        chain_system.append_to_chain(
            "2026-01-10T12:00:00",
            "INFO",
            "TEST",
            "Event 1"
        )
        
        chain_system.append_to_chain(
            "2026-01-10T12:01:00",
            "INFO",
            "TEST",
            "Event 2"
        )
        
        # Tamper with event hash in database
        conn = sqlite3.connect(temp_chain_db)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE hash_chain SET event_hash = ?
            WHERE event_id = 2
        """, ("x" * 64,))
        
        conn.commit()
        conn.close()
        
        # Verify detects tampering
        is_valid, results = chain_system.verify_chain_integrity()
        
        assert is_valid is False
        assert "hash mismatch" in results["message"].lower()
    
    def test_verify_detects_broken_chain_link(self, chain_system, temp_chain_db):
        """Test that verification detects broken chain links."""
        # Append events
        chain_system.append_to_chain(
            "2026-01-10T12:00:00",
            "INFO",
            "TEST",
            "Event 1"
        )
        
        chain_system.append_to_chain(
            "2026-01-10T12:01:00",
            "INFO",
            "TEST",
            "Event 2"
        )
        
        # Break chain link
        conn = sqlite3.connect(temp_chain_db)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE hash_chain SET prev_event_hash = ?
            WHERE event_id = 2
        """, ("y" * 64,))
        
        conn.commit()
        conn.close()
        
        # Verify detects broken link
        is_valid, results = chain_system.verify_chain_integrity()
        
        assert is_valid is False
        assert "chain link broken" in results["message"].lower()


class TestChainStatistics:
    """Tests for chain statistics."""
    
    def test_get_chain_stats_empty(self, chain_system):
        """Test stats for uninitialized chain."""
        stats = chain_system.get_chain_stats()
        
        assert stats["total_events"] == 0 or stats["status"] == "not_initialized"
    
    def test_get_chain_stats_with_events(self, chain_system):
        """Test stats with events in chain."""
        for i in range(3):
            chain_system.append_to_chain(
                f"2026-01-10T12:{i:02d}:00",
                "INFO",
                "TEST",
                f"Event {i}"
            )
        
        stats = chain_system.get_chain_stats()
        
        assert stats["total_events"] == 3
        assert stats["first_event"] is not None
        assert stats["last_event"] is not None


class TestChainTracing:
    """Tests for tracing event ancestry."""
    
    def test_get_event_chain_single_event(self, chain_system):
        """Test getting chain for single event."""
        chain_system.append_to_chain(
            "2026-01-10T12:00:00",
            "INFO",
            "TEST",
            "Single event"
        )
        
        chain = chain_system.get_event_chain(1)
        
        assert len(chain) == 1
        assert chain[0]["event_id"] == 1
    
    def test_get_event_chain_multiple_events(self, chain_system):
        """Test getting full chain ancestry."""
        for i in range(5):
            chain_system.append_to_chain(
                f"2026-01-10T12:{i:02d}:00",
                "INFO",
                "TEST",
                f"Event {i}"
            )
        
        # Get chain for event 5
        chain = chain_system.get_event_chain(5)
        
        # Should have all 5 events from genesis to event 5
        assert len(chain) == 5
        assert chain[0]["event_id"] == 1
        assert chain[4]["event_id"] == 5
    
    def test_get_event_chain_nonexistent(self, chain_system):
        """Test getting chain for non-existent event."""
        chain_system.append_to_chain(
            "2026-01-10T12:00:00",
            "INFO",
            "TEST",
            "Event"
        )
        
        chain = chain_system.get_event_chain(999)
        
        assert chain == []


class TestHashChainEvent:
    """Tests for HashChainEvent dataclass."""
    
    def test_create_hash_chain_event(self):
        """Test creating hash chain event."""
        event = HashChainEvent(
            event_id=1,
            timestamp="2026-01-10T12:00:00",
            level="INFO",
            category="TEST",
            message="Test",
            event_hash="a" * 64,
            prev_event_hash="0" * 64
        )
        
        assert event.event_id == 1
        assert event.chain_valid is True
    
    def test_hash_chain_event_invalid_chain(self):
        """Test event with broken chain."""
        event = HashChainEvent(
            event_id=2,
            timestamp="2026-01-10T12:01:00",
            level="INFO",
            category="TEST",
            message="Test",
            event_hash="a" * 64,
            prev_event_hash="b" * 64,
            chain_valid=False
        )
        
        assert event.chain_valid is False
