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


@pytest.fixture
def live_trace_db() -> Path:
    """
    Provide path to live orchestrator-traces.db for golden tests.
    
    Phase 81-b: GAP-81-07
    Allows golden tests to validate real orchestrator handoffs in production DB.
    Falls back to session tmp DB if live DB doesn't exist (CI safety).
    
    Returns:
        Path to .cortex-runtime/traces/orchestrator-traces.db or tmp DB
    """
    project_root = Path(__file__).parents[2]
    live_db_path = project_root / ".cortex-runtime" / "traces" / "orchestrator-traces.db"
    
    if live_db_path.exists():
        return live_db_path
    
    # Fallback: create tmp DB with minimal schema for CI environments
    with tempfile.NamedTemporaryFile(suffix="-orchestrator-traces.db", delete=False) as f:
        tmp_db_path = Path(f.name)
    
    conn = sqlite3.connect(tmp_db_path)
    cursor = conn.cursor()
    
    # Minimal schema matching production DB
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_sessions (
            session_id TEXT PRIMARY KEY,
            start_time TEXT,
            end_time TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_stage_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            stage_index INTEGER,
            orchestrator_name TEXT,
            status TEXT,
            timestamp TEXT
        )
    """)
    
    conn.commit()
    conn.close()
    
    return tmp_db_path


def assert_handoff_recorded(
    trace_db: Path,
    from_orchestrator: str,
    to_orchestrator: str,
) -> None:
    """
    Assert that orchestrator handoff is recorded in trace DB.
    
    Phase 81-b: GAP-81-07 helper
    
    Args:
        trace_db: Path to orchestrator-traces.db
        from_orchestrator: Source orchestrator name
        to_orchestrator: Target orchestrator name
    
    Raises:
        AssertionError: If handoff not found in trace DB
    """
    if not trace_db.exists():
        pytest.skip(f"Trace DB not found: {trace_db}")
    
    conn = sqlite3.connect(trace_db)
    cursor = conn.cursor()
    
    # Check for sequential invocations in audit_stage_log
    cursor.execute("""
        SELECT orchestrator_name 
        FROM audit_stage_log 
        WHERE session_id = (SELECT MAX(session_id) FROM audit_sessions)
        ORDER BY stage_index
    """)
    
    orchestrator_chain = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    # Verify handoff exists
    try:
        from_idx = orchestrator_chain.index(from_orchestrator)
        to_idx = orchestrator_chain.index(to_orchestrator)
        assert to_idx > from_idx, (
            f"Handoff order incorrect: {from_orchestrator} → {to_orchestrator}. "
            f"Actual chain: {orchestrator_chain}"
        )
    except ValueError as e:
        raise AssertionError(
            f"Handoff {from_orchestrator} → {to_orchestrator} not recorded. "
            f"Chain: {orchestrator_chain}"
        ) from e
