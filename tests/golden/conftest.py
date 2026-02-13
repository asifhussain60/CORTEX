"""
Golden Path Tests Configuration & Fixtures

Purpose:
    Shared fixtures and configuration for all Golden Path truth tests.
    Initializes audit database, reference repository, and event bus.

Authority:
    - WAVE-10 Track 1 (Golden Path Truth Tests)
    - ENH-089+ phase delivery

AC-ID: AC-WAVE10-T1-CONF-001
"""

import pytest
import sqlite3
import tempfile
from pathlib import Path
from datetime import datetime

from cortex.core.event_bus import EventBus


@pytest.fixture(scope="session")
def audit_db_session():
    """Session-scoped audit database for test session."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    
    # Initialize audit schema
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            operation TEXT NOT NULL,
            rule_id TEXT,
            source TEXT,
            metadata TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()
    
    yield db_path
    
    # Cleanup
    Path(db_path).unlink()


@pytest.fixture
def audit_db(audit_db_session):
    """Function-scoped reference to session audit database."""
    return audit_db_session


@pytest.fixture
def event_bus():
    """Initialize EventBus for test."""
    bus = EventBus()
    yield bus
    # Cleanup: Clear subscriptions
    bus.subscriptions.clear()


@pytest.fixture
def reference_repo_path():
    """Path to reference repository fixture."""
    path = Path(__file__).parent.parent / "fixtures" / "reference_repo"
    if not path.exists():
        pytest.skip("Reference repository fixture not available")
    return path


def audit_log_entry(
    db_path: str,
    operation: str,
    rule_id: str,
    source: str,
    metadata: dict = None
) -> int:
    """
    Helper to insert audit log entry and return entry ID.
    
    Args:
        db_path: Path to audit database
        operation: Operation type (e.g., 'rule_resolution')
        rule_id: ID of rule being audited
        source: Source of the rule (e.g., 'company', 'cortex')
        metadata: Additional metadata as dictionary
    
    Returns:
        ID of inserted audit entry
    """
    import json
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    metadata_json = json.dumps(metadata) if metadata else None
    timestamp = datetime.now().isoformat()
    
    cursor.execute("""
        INSERT INTO audit (timestamp, operation, rule_id, source, metadata)
        VALUES (?, ?, ?, ?, ?)
    """, (timestamp, operation, rule_id, source, metadata_json))
    
    entry_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return entry_id


@pytest.fixture
def audit_log_helper():
    """Provide audit log helper function to tests."""
    return audit_log_entry
