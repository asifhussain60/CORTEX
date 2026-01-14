"""
Tests for AC-AUDIT-004: AC-ID Traceability
"""

import pytest
import sqlite3
import tempfile
from pathlib import Path
from datetime import datetime
from src.infrastructure.ac_id_traceability import ACIDTraceability


@pytest.fixture
def test_db():
    """Create temporary test database."""
    with tempfile.NamedTemporaryFile(suffix='.db') as f:
        db_path = Path(f.name)
    
    conn = sqlite3.connect(db_path)
    
    # Create minimal audit_log table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY,
            timestamp TEXT NOT NULL,
            level TEXT,
            category TEXT,
            component TEXT,
            operation TEXT,
            message TEXT,
            ac_id TEXT,
            context TEXT
        )
    """)
    conn.commit()
    
    yield conn
    
    conn.close()
    db_path.unlink(missing_ok=True)


def test_ac_id_traceability_init(test_db):
    """ACIDTraceability initializes with database."""
    tracer = ACIDTraceability(test_db)
    assert tracer.db is test_db


def test_log_with_ac_id(test_db):
    """log_with_ac_id creates audit entry linked to AC-ID."""
    tracer = ACIDTraceability(test_db)
    
    result = tracer.log_with_ac_id(
        ac_id="AC-AUDIT-004",
        level="INFO",
        category="validation",
        message="Testing AC-ID traceability"
    )
    
    assert result is True


def test_query_events_by_ac_id(test_db):
    """query_events_by_ac_id finds events for AC-ID."""
    tracer = ACIDTraceability(test_db)
    
    # Log an event
    tracer.log_with_ac_id(
        ac_id="AC-AUDIT-004",
        level="INFO",
        category="validation",
        message="Test event"
    )
    
    # Query events
    events = tracer.query_events_by_ac_id("AC-AUDIT-004")
    
    assert len(events) > 0
    assert events[0]['ac_id'] == "AC-AUDIT-004"
    assert events[0]['message'] == "Test event"


def test_query_returns_empty_for_unknown_ac(test_db):
    """query_events_by_ac_id returns empty list for unknown AC-ID."""
    tracer = ACIDTraceability(test_db)
    
    events = tracer.query_events_by_ac_id("AC-NONEXISTENT-999")
    
    assert events == []


def test_validate_ac_id_format():
    """validate_ac_id checks format."""
    # Valid formats
    assert ACIDTraceability._validate_ac_id("AC-TEST-001") is True
    assert ACIDTraceability._validate_ac_id("AC-AUDIT-004") is True
    assert ACIDTraceability._validate_ac_id("AC-EVIDENCE-999") is True
    
    # Invalid formats
    assert ACIDTraceability._validate_ac_id("INVALID-001") is False
    assert ACIDTraceability._validate_ac_id("AC-INVALID") is False
    assert ACIDTraceability._validate_ac_id("AC-TEST-ABC") is False
    assert ACIDTraceability._validate_ac_id("") is False
    assert ACIDTraceability._validate_ac_id(None) is False


def test_get_ac_implementation_proof(test_db):
    """get_ac_implementation_proof returns proof summary."""
    tracer = ACIDTraceability(test_db)
    
    # Log multiple events
    tracer.log_with_ac_id("AC-TEST-004", "INFO", "validation", "Started")
    tracer.log_with_ac_id("AC-TEST-004", "INFO", "validation", "Tests run")
    tracer.log_with_ac_id("AC-TEST-004", "INFO", "validation", "Completed")
    
    # Get proof
    proof = tracer.get_ac_implementation_proof("AC-TEST-004")
    
    assert proof['ac_id'] == "AC-TEST-004"
    assert proof['total_events'] == 3
    assert proof['first_event'] is not None
    assert proof['last_event'] is not None


def test_link_event_to_ac(test_db):
    """link_event_to_ac updates existing event."""
    tracer = ACIDTraceability(test_db)
    
    # Create event without AC-ID
    test_db.execute("""
        INSERT INTO audit_log 
        (timestamp, level, category, message)
        VALUES (?, ?, ?, ?)
    """, (datetime.utcnow().isoformat(), "INFO", "test", "Test event"))
    test_db.commit()
    
    # Link to AC-ID
    result = tracer.link_event_to_ac(1, "AC-AUDIT-004")
    
    assert result is True
    
    # Verify link
    cursor = test_db.execute("SELECT ac_id FROM audit_log WHERE id = 1")
    row = cursor.fetchone()
    assert row[0] == "AC-AUDIT-004"
