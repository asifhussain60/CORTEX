"""
CORTEX 4.0 Session Manager Tests

Tests for session state persistence, restoration, and locking functionality.

Test Coverage:
- Session creation (with/without config)
- Session update (success/failure)
- Session restoration (success/not found/corrupted)
- Session completion (success/failure)
- Session locking (acquire/release/conflict)
- Active/interrupted session discovery
- Stale session cleanup
- Session persistence (JSON format, exception handling)

Target Coverage: 85%+
"""

import pytest
import json
import time
import platform
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, mock_open
import tempfile
import os

# Windows compatibility check
WINDOWS = platform.system() == "Windows"

from src.orchestrators.planning.session_manager import (
    SessionManager,
    SessionState,
    SessionStatus
)


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def workspace_root(tmp_path):
    """Create temporary workspace root."""
    return tmp_path / "workspace"


@pytest.fixture
def session_dir(tmp_path):
    """Create temporary session directory."""
    return tmp_path / "sessions"


@pytest.fixture
def mock_logger():
    """Create mock logger."""
    return Mock()


@pytest.fixture
def session_manager(workspace_root, session_dir, mock_logger):
    """Create SessionManager instance."""
    workspace_root.mkdir(parents=True, exist_ok=True)
    return SessionManager(
        workspace_root=workspace_root,
        session_dir=session_dir,
        logger_instance=mock_logger
    )


# ============================================================================
# Initialization Tests
# ============================================================================

def test_session_manager_init(workspace_root, session_dir, mock_logger):
    """Test SessionManager initialization."""
    manager = SessionManager(
        workspace_root=workspace_root,
        session_dir=session_dir,
        logger_instance=mock_logger
    )
    
    assert manager.workspace_root == Path(workspace_root)
    assert manager.session_dir == Path(session_dir)
    assert manager.logger == mock_logger
    assert manager.session_dir.exists()
    assert manager._locks == {}


def test_session_manager_init_default_session_dir(workspace_root, mock_logger):
    """Test SessionManager initialization with default session directory."""
    manager = SessionManager(
        workspace_root=workspace_root,
        logger_instance=mock_logger
    )
    
    expected_dir = Path(workspace_root) / ".cortex" / "sessions"
    assert manager.session_dir == expected_dir
    assert manager.session_dir.exists()


# ============================================================================
# Session Creation Tests
# ============================================================================

def test_create_session_basic(session_manager, workspace_root):
    """Test creating a basic session."""
    plan_path = workspace_root / "plans" / "feature.md"
    
    session = session_manager.create_session(
        plan_name="Feature Implementation",
        plan_path=plan_path
    )
    
    assert session is not None
    assert session.session_id.startswith("session-")
    assert session.plan_name == "Feature Implementation"
    assert session.plan_path == plan_path
    assert session.workspace_root == Path(workspace_root)
    assert session.status == SessionStatus.ACTIVE
    assert session.execution_mode == "supervised"
    assert session.auto_checkpoint is True
    
    # Verify persistence
    session_file = session_manager.session_dir / f"{session.session_id}.json"
    assert session_file.exists()


def test_create_session_with_config(session_manager, workspace_root):
    """Test creating session with execution config."""
    plan_path = workspace_root / "plans" / "test.md"
    
    config = {
        "execution_mode": "autonomous",
        "auto_checkpoint": False,
        "metadata": {"priority": "high", "tags": ["urgent"]}
    }
    
    session = session_manager.create_session(
        plan_name="Test Plan",
        plan_path=plan_path,
        execution_config=config
    )
    
    assert session.execution_mode == "autonomous"
    assert session.auto_checkpoint is False
    assert session.metadata == {"priority": "high", "tags": ["urgent"]}


# ============================================================================
# Session Update Tests
# ============================================================================

def test_update_session_success(session_manager, workspace_root):
    """Test successful session update."""
    # Create session
    session = session_manager.create_session(
        plan_name="Test",
        plan_path=workspace_root / "test.md"
    )
    
    # Update session state
    session.current_phase = "DISCOVERY"
    session.progress_percent = 25.0
    session.completed_phases = ["INIT"]
    
    result = session_manager.update_session(session)
    
    assert result is True
    
    # Verify persistence
    restored = session_manager.restore_session(session.session_id)
    assert restored.current_phase == "DISCOVERY"
    assert restored.progress_percent == 25.0
    assert restored.completed_phases == ["INIT"]


def test_update_session_failure(session_manager, workspace_root, mock_logger):
    """Test session update failure (exception during persistence)."""
    session = session_manager.create_session(
        plan_name="Test",
        plan_path=workspace_root / "test.md"
    )
    
    # Mock _persist_session to raise exception
    with patch.object(session_manager, '_persist_session', side_effect=PermissionError("Access denied")):
        result = session_manager.update_session(session)
        
        assert result is False
        mock_logger.error.assert_called()


# ============================================================================
# Session Restoration Tests
# ============================================================================

def test_restore_session_success(session_manager, workspace_root):
    """Test restoring an existing session."""
    # Create session
    original = session_manager.create_session(
        plan_name="Restore Test",
        plan_path=workspace_root / "restore.md"
    )
    
    # Restore session
    restored = session_manager.restore_session(original.session_id)
    
    assert restored is not None
    assert restored.session_id == original.session_id
    assert restored.plan_name == "Restore Test"
    assert restored.status == SessionStatus.ACTIVE


def test_restore_session_not_found(session_manager, mock_logger):
    """Test restoring a non-existent session."""
    result = session_manager.restore_session("nonexistent-session")
    
    assert result is None
    mock_logger.warning.assert_called()
    assert "not found" in mock_logger.warning.call_args[0][0]


def test_restore_session_corrupted_json(session_manager, mock_logger):
    """Test restoring session with corrupted JSON."""
    # Create corrupted session file
    session_id = "session-corrupted"
    session_file = session_manager.session_dir / f"{session_id}.json"
    session_file.write_text("{ invalid json }")
    
    result = session_manager.restore_session(session_id)
    
    assert result is None
    mock_logger.error.assert_called()


def test_restore_session_with_full_state(session_manager, workspace_root):
    """Test restoring session with complete state."""
    # Create session with full state
    session = session_manager.create_session(
        plan_name="Full State Test",
        plan_path=workspace_root / "full.md"
    )
    
    session.current_phase = "IMPLEMENTATION"
    session.completed_phases = ["DISCOVERY", "PLANNING"]
    session.progress_percent = 60.0
    session.execution_time_seconds = 1200.0
    session.checkpoints = ["cp1", "cp2"]
    session.last_checkpoint_id = "cp2"
    session.errors = ["Error 1"]
    session.warnings = ["Warning 1", "Warning 2"]
    
    session_manager.update_session(session)
    
    # Restore and verify
    restored = session_manager.restore_session(session.session_id)
    
    assert restored.current_phase == "IMPLEMENTATION"
    assert restored.completed_phases == ["DISCOVERY", "PLANNING"]
    assert restored.progress_percent == 60.0
    assert restored.execution_time_seconds == 1200.0
    assert restored.checkpoints == ["cp1", "cp2"]
    assert restored.last_checkpoint_id == "cp2"
    assert restored.errors == ["Error 1"]
    assert restored.warnings == ["Warning 1", "Warning 2"]


# ============================================================================
# Session Discovery Tests
# ============================================================================

def test_find_active_sessions(session_manager, workspace_root):
    """Test finding all active sessions."""
    # Create multiple sessions with different statuses
    # Add 1.1 second delays to ensure unique session IDs (timestamp-based with second precision)
    active1 = session_manager.create_session("Active 1", workspace_root / "a1.md")
    time.sleep(1.1)
    
    active2 = session_manager.create_session("Active 2", workspace_root / "a2.md")
    time.sleep(1.1)
    
    # Create paused session
    paused = session_manager.create_session("Paused", workspace_root / "p1.md")
    paused.status = SessionStatus.PAUSED
    session_manager.update_session(paused)
    time.sleep(1.1)
    
    # Create completed session  
    completed = session_manager.create_session("Completed", workspace_root / "c1.md")
    completed.status = SessionStatus.COMPLETED
    session_manager.update_session(completed)
    
    # Find active sessions
    active_sessions = session_manager.find_active_sessions()
    
    # Should find exactly 3 sessions (2 ACTIVE + 1 PAUSED)
    assert len(active_sessions) == 3, f"Expected 3 active/paused sessions, got {len(active_sessions)}"
    session_ids = {s.session_id for s in active_sessions}
    
    # Verify our sessions are present
    assert active1.session_id in session_ids
    assert active2.session_id in session_ids
    assert paused.session_id in session_ids
    assert completed.session_id not in session_ids
    
    # Verify completed session is NOT present
    assert completed.session_id not in session_ids


def test_find_interrupted_sessions(session_manager, workspace_root):
    """Test finding all interrupted sessions."""
    # Create sessions with different statuses
    # Add 1.1 second delays to ensure unique session IDs
    interrupted1 = session_manager.create_session("Int 1", workspace_root / "i1.md")
    interrupted1.status = SessionStatus.INTERRUPTED
    session_manager.update_session(interrupted1)
    time.sleep(1.1)
    
    interrupted2 = session_manager.create_session("Int 2", workspace_root / "i2.md")
    interrupted2.status = SessionStatus.INTERRUPTED
    session_manager.update_session(interrupted2)
    time.sleep(1.1)
    
    active = session_manager.create_session("Active", workspace_root / "a1.md")
    
    # Find interrupted sessions
    interrupted_sessions = session_manager.find_interrupted_sessions()
    
    # Should find exactly 2 interrupted sessions
    assert len(interrupted_sessions) == 2, f"Expected 2 interrupted sessions, got {len(interrupted_sessions)}"
    session_ids = {s.session_id for s in interrupted_sessions}
    assert interrupted1.session_id in session_ids
    assert interrupted2.session_id in session_ids
    assert active.session_id not in session_ids


def test_find_sessions_with_corrupted_file(session_manager, workspace_root, mock_logger):
    """Test finding sessions handles corrupted files gracefully."""
    # Create valid session
    valid = session_manager.create_session("Valid", workspace_root / "v1.md")
    
    # Create corrupted session file
    corrupted_file = session_manager.session_dir / "session-corrupted.json"
    corrupted_file.write_text("{ invalid }")
    
    # Should skip corrupted file and return valid session
    active_sessions = session_manager.find_active_sessions()
    
    assert len(active_sessions) == 1
    assert active_sessions[0].session_id == valid.session_id
    mock_logger.error.assert_called()


# ============================================================================
# Session Completion Tests
# ============================================================================

def test_complete_session_success(session_manager, workspace_root):
    """Test completing session successfully."""
    session = session_manager.create_session("Test", workspace_root / "test.md")
    
    result = session_manager.complete_session(session.session_id, success=True)
    
    assert result is True
    
    # Verify status updated
    restored = session_manager.restore_session(session.session_id)
    assert restored.status == SessionStatus.COMPLETED


def test_complete_session_failure(session_manager, workspace_root):
    """Test marking session as failed."""
    session = session_manager.create_session("Test", workspace_root / "test.md")
    
    result = session_manager.complete_session(session.session_id, success=False)
    
    assert result is True
    
    # Verify status updated
    restored = session_manager.restore_session(session.session_id)
    assert restored.status == SessionStatus.FAILED


def test_complete_session_not_found(session_manager):
    """Test completing non-existent session."""
    result = session_manager.complete_session("nonexistent")
    
    assert result is False


# ============================================================================
# Session Locking Tests
# ============================================================================

def test_lock_session_success(session_manager, workspace_root):
    """Test successfully acquiring session lock."""
    session = session_manager.create_session("Test", workspace_root / "test.md")
    
    result = session_manager.lock_session(session.session_id)
    
    assert result is True
    assert session.session_id in session_manager._locks
    
    # Verify lock file exists
    lock_file = session_manager.session_dir / f"{session.session_id}.lock"
    assert lock_file.exists()
    
    # Cleanup
    session_manager.unlock_session(session.session_id)


def test_lock_session_already_locked(session_manager, workspace_root, mock_logger):
    """Test locking already locked session."""
    if WINDOWS:
        pytest.skip("fcntl not available on Windows - locking uses file-based mechanism")
    
    session = session_manager.create_session("Test", workspace_root / "test.md")
    
    # First lock succeeds
    result1 = session_manager.lock_session(session.session_id)
    assert result1 is True
    
    # Second lock fails (simulate from different process)
    import fcntl
    with patch('fcntl.flock', side_effect=IOError("Resource locked")):
        result2 = session_manager.lock_session(f"{session.session_id}-2")
        assert result2 is False
    
    # Cleanup
    session_manager.unlock_session(session.session_id)


def test_unlock_session_success(session_manager, workspace_root):
    """Test successfully releasing session lock."""
    session = session_manager.create_session("Test", workspace_root / "test.md")
    
    # Lock session
    session_manager.lock_session(session.session_id)
    
    # Unlock session
    result = session_manager.unlock_session(session.session_id)
    
    assert result is True
    assert session.session_id not in session_manager._locks
    
    # Verify lock file removed
    lock_file = session_manager.session_dir / f"{session.session_id}.lock"
    assert not lock_file.exists()


def test_unlock_session_already_unlocked(session_manager, workspace_root):
    """Test unlocking already unlocked session."""
    session = session_manager.create_session("Test", workspace_root / "test.md")
    
    # Unlock without locking first - should succeed
    result = session_manager.unlock_session(session.session_id)
    
    assert result is True


def test_lock_unlock_exception_handling(session_manager, workspace_root, mock_logger):
    """Test lock/unlock exception handling."""
    if WINDOWS:
        pytest.skip("fcntl not available on Windows - locking uses file-based mechanism")
    
    session = session_manager.create_session("Test", workspace_root / "test.md")
    
    # Test lock exception - we need to patch at the right place
    # The lock_session method calls open() and fcntl.flock()
    import fcntl
    with patch('fcntl.flock', side_effect=Exception("Lock error")):
        result = session_manager.lock_session(session.session_id)
        assert result is False
        # Verify error was logged (check that error method was called)
        assert mock_logger.error.called


# ============================================================================
# Session Cleanup Tests
# ============================================================================

def test_cleanup_stale_sessions(session_manager, workspace_root):
    """Test cleaning up stale completed sessions."""
    # Create old completed session
    # Add 1.1 second delay to ensure unique session ID
    old_session = session_manager.create_session("Old", workspace_root / "old.md")
    old_session.status = SessionStatus.COMPLETED
    old_session.updated_at = datetime.now() - timedelta(hours=48)
    session_manager.update_session(old_session)
    
    # Manually update the JSON file with old timestamp to simulate stale session
    session_file = session_manager.session_dir / f"{old_session.session_id}.json"
    data = json.loads(session_file.read_text())
    data["updated_at"] = (datetime.now() - timedelta(hours=48)).isoformat()
    session_file.write_text(json.dumps(data, indent=2))
    time.sleep(1.1)
    
    # Create recent completed session
    recent_session = session_manager.create_session("Recent", workspace_root / "recent.md")
    recent_session.status = SessionStatus.COMPLETED
    session_manager.update_session(recent_session)
    time.sleep(1.1)
    
    # Create active session
    active_session = session_manager.create_session("Active", workspace_root / "active.md")
    
    # Cleanup (max_age_hours=24)
    cleaned = session_manager.cleanup_stale_sessions(max_age_hours=24)
    
    # Should clean exactly the old session
    assert cleaned == 1, f"Expected 1 cleaned session, got {cleaned}"
    
    # Verify old session file removed
    old_file = session_manager.session_dir / f"{old_session.session_id}.json"
    assert not old_file.exists()
    
    # Verify recent and active sessions still exist
    recent_file = session_manager.session_dir / f"{recent_session.session_id}.json"
    assert recent_file.exists()
    
    active_file = session_manager.session_dir / f"{active_session.session_id}.json"
    assert active_file.exists()


def test_cleanup_stale_sessions_no_cleanup(session_manager, workspace_root):
    """Test cleanup when no stale sessions exist."""
    # Create recent session
    session = session_manager.create_session("Recent", workspace_root / "recent.md")
    
    cleaned = session_manager.cleanup_stale_sessions(max_age_hours=24)
    
    assert cleaned == 0


def test_cleanup_handles_corrupted_files(session_manager, workspace_root, mock_logger):
    """Test cleanup handles corrupted session files gracefully."""
    # Create valid session
    valid = session_manager.create_session("Valid", workspace_root / "valid.md")
    
    # Create corrupted session file
    corrupted_file = session_manager.session_dir / "session-corrupted.json"
    corrupted_file.write_text("{ invalid json }")
    
    # Cleanup should skip corrupted file
    cleaned = session_manager.cleanup_stale_sessions()
    
    # Corrupted file still exists (not cleaned due to error)
    assert corrupted_file.exists()
    mock_logger.error.assert_called()


# ============================================================================
# Session Persistence Tests
# ============================================================================

def test_persist_session_json_format(session_manager, workspace_root):
    """Test session persistence JSON format."""
    session = session_manager.create_session(
        plan_name="JSON Test",
        plan_path=workspace_root / "json.md",
        execution_config={"metadata": {"key": "value"}}
    )
    
    # Read persisted JSON
    session_file = session_manager.session_dir / f"{session.session_id}.json"
    data = json.loads(session_file.read_text())
    
    assert data["session_id"] == session.session_id
    assert data["plan_name"] == "JSON Test"
    assert data["status"] == "active"
    assert "created_at" in data
    assert "updated_at" in data
    assert data["execution_mode"] == "supervised"
    assert data["auto_checkpoint"] is True
    assert data["metadata"] == {"key": "value"}


def test_persist_session_datetime_serialization(session_manager, workspace_root):
    """Test datetime serialization in session persistence."""
    session = session_manager.create_session("DateTime Test", workspace_root / "dt.md")
    
    # Verify datetime serialized as ISO format
    session_file = session_manager.session_dir / f"{session.session_id}.json"
    data = json.loads(session_file.read_text())
    
    # Verify ISO format (can be parsed)
    created_at = datetime.fromisoformat(data["created_at"])
    assert isinstance(created_at, datetime)


# ============================================================================
# Domain Model Tests
# ============================================================================

def test_session_state_dataclass():
    """Test SessionState dataclass creation."""
    session = SessionState(
        session_id="test-123",
        plan_name="Test Plan",
        plan_path=Path("/path/to/plan.md"),
        workspace_root=Path("/workspace"),
        status=SessionStatus.ACTIVE,
        current_phase="DISCOVERY",
        completed_phases=["INIT"],
        progress_percent=20.0
    )
    
    assert session.session_id == "test-123"
    assert session.plan_name == "Test Plan"
    assert session.status == SessionStatus.ACTIVE
    assert session.current_phase == "DISCOVERY"
    assert session.completed_phases == ["INIT"]
    assert session.progress_percent == 20.0


def test_session_status_enum():
    """Test SessionStatus enum values."""
    assert SessionStatus.ACTIVE.value == "active"
    assert SessionStatus.PAUSED.value == "paused"
    assert SessionStatus.INTERRUPTED.value == "interrupted"
    assert SessionStatus.COMPLETED.value == "completed"
    assert SessionStatus.FAILED.value == "failed"
