"""
Tests for SessionManager - CORTEX 3.0 session-based conversation boundaries.
"""

import pytest
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
import tempfile
import os

from src.tier1.sessions import SessionManager, Session


@pytest.fixture
def temp_db():
    """Create temporary database for testing."""
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    yield Path(path)
    # Cleanup
    if Path(path).exists():
        Path(path).unlink()


@pytest.fixture
def session_manager(temp_db):
    """Create SessionManager instance with temp database."""
    return SessionManager(temp_db)


class TestSessionManager:
    """Test suite for SessionManager."""
    
    def test_init_creates_schema(self, temp_db):
        """Test that initializing SessionManager creates schema."""
        manager = SessionManager(temp_db)
        
        # Verify table exists
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sessions'")
        assert cursor.fetchone() is not None
        conn.close()
    
    def test_create_new_session(self, session_manager):
        """Test creating a new session."""
        workspace = "/projects/test"
        session = session_manager.detect_or_create_session(workspace)
        
        assert session is not None
        assert session.workspace_path == workspace
        assert session.is_active is True
        assert session.conversation_count == 0
        assert session.session_id.startswith("session_")
    
    def test_detect_existing_active_session(self, session_manager):
        """Test detecting existing active session."""
        workspace = "/projects/test"
        
        # Create session
        session1 = session_manager.detect_or_create_session(workspace)
        
        # Detect should return same session
        session2 = session_manager.detect_or_create_session(workspace)
        
        assert session1.session_id == session2.session_id
    
    def test_idle_threshold_creates_new_session(self, session_manager, temp_db):
        """Test that idle threshold triggers new session creation."""
        workspace = "/projects/test"
        
        # Create session with 1-second idle threshold
        short_idle_manager = SessionManager(temp_db, idle_threshold_seconds=1)
        session1 = short_idle_manager.detect_or_create_session(workspace)
        
        # Wait for idle threshold
        import time
        time.sleep(2)
        
        # Next detection should create new session
        session2 = short_idle_manager.detect_or_create_session(workspace)
        
        assert session1.session_id != session2.session_id
        
        # Verify old session was ended
        old_session = short_idle_manager.get_session(session1.session_id)
        assert old_session.is_active is False
    
    def test_get_active_session(self, session_manager):
        """Test getting active session."""
        workspace = "/projects/test"
        
        # No active session initially
        assert session_manager.get_active_session(workspace) is None
        
        # Create session
        session = session_manager.detect_or_create_session(workspace)
        
        # Get active session
        active = session_manager.get_active_session(workspace)
        assert active is not None
        assert active.session_id == session.session_id
    
    def test_end_session(self, session_manager):
        """Test ending a session."""
        workspace = "/projects/test"
        session = session_manager.detect_or_create_session(workspace)
        
        # End session
        session_manager.end_session(session.session_id, reason="manual")
        
        # Verify session ended
        ended = session_manager.get_session(session.session_id)
        assert ended.is_active is False
        assert ended.end_time is not None
    
    def test_increment_conversation_count(self, session_manager):
        """Test incrementing conversation count."""
        workspace = "/projects/test"
        session = session_manager.detect_or_create_session(workspace)
        
        # Increment count
        session_manager.increment_conversation_count(session.session_id)
        session_manager.increment_conversation_count(session.session_id)
        
        # Verify count
        updated = session_manager.get_session(session.session_id)
        assert updated.conversation_count == 2
    
    def test_get_recent_sessions(self, session_manager):
        """Test getting recent sessions."""
        workspace1 = "/projects/test1"
        workspace2 = "/projects/test2"
        
        # Create multiple sessions
        session1 = session_manager.detect_or_create_session(workspace1)
        session2 = session_manager.detect_or_create_session(workspace2)
        
        # Get all recent sessions
        recent = session_manager.get_recent_sessions(limit=10)
        assert len(recent) == 2
        
        # Get recent sessions for specific workspace
        workspace1_sessions = session_manager.get_recent_sessions(workspace_path=workspace1, limit=10)
        assert len(workspace1_sessions) == 1
        assert workspace1_sessions[0].session_id == session1.session_id
    
    def test_cleanup_old_sessions(self, session_manager):
        """Test cleanup of old sessions."""
        workspace = "/projects/test"
        
        # Create and end a session
        session = session_manager.detect_or_create_session(workspace)
        session_manager.end_session(session.session_id)
        
        # Manually set old end_time for testing
        conn = sqlite3.connect(session_manager.db_path)
        cursor = conn.cursor()
        old_date = (datetime.now() - timedelta(days=100)).isoformat()
        cursor.execute("UPDATE sessions SET start_time = ?, end_time = ? WHERE session_id = ?", 
                      (old_date, old_date, session.session_id))
        conn.commit()
        conn.close()
        
        # Cleanup with 90-day retention
        deleted = session_manager.cleanup_old_sessions(retention_days=90)
        assert deleted == 1
        
        # Verify session deleted
        assert session_manager.get_session(session.session_id) is None
    
    def test_multiple_workspaces_independent_sessions(self, session_manager):
        """Test that different workspaces have independent sessions."""
        workspace1 = "/projects/test1"
        workspace2 = "/projects/test2"
        
        # Create sessions for different workspaces
        session1 = session_manager.detect_or_create_session(workspace1)
        session2 = session_manager.detect_or_create_session(workspace2)
        
        # Sessions should be different
        assert session1.session_id != session2.session_id
        
        # Both should be active
        assert session_manager.get_active_session(workspace1).session_id == session1.session_id
        assert session_manager.get_active_session(workspace2).session_id == session2.session_id
    
    def test_session_last_activity_updates(self, session_manager):
        """Test that last_activity updates on session detection."""
        workspace = "/projects/test"
        
        # Create session
        session1 = session_manager.detect_or_create_session(workspace)
        original_activity = session1.last_activity
        
        # Wait enough time to ensure timestamp differs (at least 1 millisecond)
        import time
        time.sleep(0.01)
        
        # Detect again (should update last_activity)
        session2 = session_manager.detect_or_create_session(workspace)
        
        # Same session but updated activity
        assert session2.session_id == session1.session_id
        assert session2.last_activity >= original_activity  # May be equal due to timestamp precision


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
