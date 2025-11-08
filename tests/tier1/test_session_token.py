"""
Tests for CORTEX Tier 1: Session Token Manager
Comprehensive test coverage for persistent conversation tracking.
"""

import pytest
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from src.tier1.session_token import (
    SessionTokenManager,
    Session,
    SessionStatus
)


@pytest.fixture
def temp_db(tmp_path):
    """Create a temporary database for testing."""
    db_path = tmp_path / "test_session_tokens.db"
    return db_path


@pytest.fixture
def stm(temp_db):
    """Create a SessionTokenManager instance."""
    return SessionTokenManager(db_path=temp_db)


class TestDatabaseInitialization:
    """Test database creation and schema."""
    
    def test_database_created(self, temp_db):
        """Test that database file is created."""
        stm = SessionTokenManager(db_path=temp_db)
        assert temp_db.exists()
    
    def test_session_tokens_table_exists(self, stm, temp_db):
        """Test that session_tokens table is created."""
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='session_tokens'
        """)
        assert cursor.fetchone() is not None
        conn.close()
    
    def test_indexes_created(self, stm, temp_db):
        """Test that indexes are created."""
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='index'
        """)
        indexes = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        assert "idx_session_tokens_status" in indexes
        assert "idx_session_tokens_conversation" in indexes


class TestSessionCreation:
    """Test session token creation."""
    
    def test_create_session_basic(self, stm):
        """Test creating a basic session."""
        token = stm.create_session("Implementing auth feature")
        
        assert token.startswith("SESSION_")
        assert len(token) > 20  # TOKEN_YYYYMMDD_HHMMSS_hex
    
    def test_create_session_with_conversation(self, stm):
        """Test creating session with conversation ID."""
        token = stm.create_session(
            "Implementing auth",
            conversation_id="conv_12345"
        )
        
        session = stm.get_session(token)
        assert session.conversation_id == "conv_12345"
    
    def test_create_session_with_work_session(self, stm):
        """Test creating session with work session ID."""
        token = stm.create_session(
            "Implementing auth",
            work_session_id="work_20251108_143022"
        )
        
        session = stm.get_session(token)
        assert session.work_session_id == "work_20251108_143022"
    
    def test_create_session_with_metadata(self, stm):
        """Test creating session with metadata."""
        metadata = {"branch": "feature/auth", "user": "test"}
        token = stm.create_session("Implementing auth", metadata=metadata)
        
        session = stm.get_session(token)
        assert session.metadata == metadata
    
    def test_token_uniqueness(self, stm):
        """Test that tokens are unique."""
        token1 = stm.create_session("Task 1")
        token2 = stm.create_session("Task 2")
        
        assert token1 != token2


class TestSessionRetrieval:
    """Test session retrieval operations."""
    
    def test_get_session_by_token(self, stm):
        """Test retrieving session by token."""
        token = stm.create_session("Test task")
        
        session = stm.get_session(token)
        
        assert session is not None
        assert session.token == token
        assert session.description == "Test task"
        assert session.status == SessionStatus.ACTIVE
    
    def test_get_session_nonexistent(self, stm):
        """Test retrieving non-existent session."""
        session = stm.get_session("SESSION_nonexistent")
        assert session is None
    
    def test_get_active_session(self, stm):
        """Test getting the active session."""
        token = stm.create_session("Active task")
        
        session = stm.get_active_session()
        
        assert session is not None
        assert session.token == token
    
    def test_get_active_session_none(self, stm):
        """Test getting active session when none exists."""
        session = stm.get_active_session()
        assert session is None
    
    def test_get_active_session_most_recent(self, stm):
        """Test that most recent active session is returned."""
        token1 = stm.create_session("Task 1")
        import time
        time.sleep(0.01)  # Ensure different timestamps
        token2 = stm.create_session("Task 2")
        
        session = stm.get_active_session()
        
        assert session.token == token2


class TestSessionAssociations:
    """Test associating sessions with conversations and work."""
    
    def test_associate_conversation(self, stm):
        """Test associating a conversation ID."""
        token = stm.create_session("Test task")
        
        stm.associate_conversation(token, "conv_12345")
        
        session = stm.get_session(token)
        assert session.conversation_id == "conv_12345"
    
    def test_associate_work_session(self, stm):
        """Test associating a work session ID."""
        token = stm.create_session("Test task")
        
        stm.associate_work_session(token, "work_20251108_143022")
        
        session = stm.get_session(token)
        assert session.work_session_id == "work_20251108_143022"
    
    def test_association_updates_activity(self, stm):
        """Test that associations update last_activity."""
        token = stm.create_session("Test task")
        
        session1 = stm.get_session(token)
        original_activity = session1.last_activity
        
        import time
        time.sleep(0.01)
        
        stm.associate_conversation(token, "conv_12345")
        
        session2 = stm.get_session(token)
        assert session2.last_activity > original_activity


class TestSessionLifecycle:
    """Test session lifecycle management."""
    
    def test_update_activity(self, stm):
        """Test updating session activity timestamp."""
        token = stm.create_session("Test task")
        
        session1 = stm.get_session(token)
        original_activity = session1.last_activity
        
        import time
        time.sleep(0.01)
        
        stm.update_activity(token)
        
        session2 = stm.get_session(token)
        assert session2.last_activity > original_activity
    
    def test_pause_session(self, stm):
        """Test pausing a session."""
        token = stm.create_session("Test task")
        
        stm.pause_session(token)
        
        session = stm.get_session(token)
        assert session.status == SessionStatus.PAUSED
    
    def test_resume_session(self, stm):
        """Test resuming a paused session."""
        token = stm.create_session("Test task")
        stm.pause_session(token)
        
        stm.resume_session(token)
        
        session = stm.get_session(token)
        assert session.status == SessionStatus.ACTIVE
    
    def test_complete_session(self, stm):
        """Test completing a session."""
        token = stm.create_session("Test task")
        
        stm.complete_session(token)
        
        session = stm.get_session(token)
        assert session.status == SessionStatus.COMPLETED
    
    def test_expire_session(self, stm):
        """Test expiring a session."""
        token = stm.create_session("Test task")
        
        stm.expire_session(token)
        
        session = stm.get_session(token)
        assert session.status == SessionStatus.EXPIRED


class TestSessionClass:
    """Test Session dataclass methods."""
    
    def test_session_to_dict(self, stm):
        """Test converting Session to dictionary."""
        token = stm.create_session("Test task")
        session = stm.get_session(token)
        
        session_dict = session.to_dict()
        
        assert session_dict["token"] == token
        assert session_dict["description"] == "Test task"
        assert session_dict["status"] == "active"
        assert "created_at" in session_dict
        assert "last_activity" in session_dict
    
    def test_is_stale_false(self, stm):
        """Test is_stale returns False for recent session."""
        token = stm.create_session("Test task")
        session = stm.get_session(token)
        
        assert not session.is_stale(hours=24)
    
    def test_is_stale_true(self, stm, temp_db):
        """Test is_stale returns True for old session."""
        # Create old session directly in DB
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        
        old_time = datetime.now() - timedelta(hours=25)
        cursor.execute("""
            INSERT INTO session_tokens 
            (token, description, status, created_at, last_activity, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
        """, ("SESSION_old_123", "Old task", "active", old_time, old_time, "{}"))
        
        conn.commit()
        conn.close()
        
        session = stm.get_session("SESSION_old_123")
        assert session.is_stale(hours=24)
    
    def test_age_hours(self, stm):
        """Test age calculation."""
        token = stm.create_session("Test task")
        session = stm.get_session(token)
        
        age = session.age_hours()
        
        assert age >= 0
        assert age < 0.1  # Should be very small for test


class TestBulkRetrieval:
    """Test bulk session retrieval operations."""
    
    def test_get_all_active_sessions(self, stm):
        """Test getting all active sessions."""
        token1 = stm.create_session("Task 1")
        token2 = stm.create_session("Task 2")
        token3 = stm.create_session("Task 3")
        
        stm.complete_session(token1)
        
        active_sessions = stm.get_all_active_sessions()
        
        assert len(active_sessions) == 2
        active_tokens = [s.token for s in active_sessions]
        assert token2 in active_tokens
        assert token3 in active_tokens
        assert token1 not in active_tokens
    
    def test_get_all_active_sessions_empty(self, stm):
        """Test getting active sessions when none exist."""
        active_sessions = stm.get_all_active_sessions()
        assert len(active_sessions) == 0
    
    def test_get_all_active_sessions_order(self, stm):
        """Test that active sessions are ordered by activity."""
        token1 = stm.create_session("Task 1")
        import time
        time.sleep(0.01)
        token2 = stm.create_session("Task 2")
        
        active_sessions = stm.get_all_active_sessions()
        
        # Most recent first
        assert active_sessions[0].token == token2
        assert active_sessions[1].token == token1


class TestSessionSearch:
    """Test searching for sessions by associations."""
    
    def test_find_by_conversation(self, stm):
        """Test finding session by conversation ID."""
        token = stm.create_session("Test task")
        stm.associate_conversation(token, "conv_12345")
        
        session = stm.find_by_conversation("conv_12345")
        
        assert session is not None
        assert session.token == token
    
    def test_find_by_conversation_not_found(self, stm):
        """Test finding non-existent conversation."""
        session = stm.find_by_conversation("conv_nonexistent")
        assert session is None
    
    def test_find_by_work_session(self, stm):
        """Test finding session by work session ID."""
        token = stm.create_session("Test task")
        stm.associate_work_session(token, "work_20251108_143022")
        
        session = stm.find_by_work_session("work_20251108_143022")
        
        assert session is not None
        assert session.token == token
    
    def test_find_by_work_session_not_found(self, stm):
        """Test finding non-existent work session."""
        session = stm.find_by_work_session("work_nonexistent")
        assert session is None
    
    def test_find_by_conversation_most_recent(self, stm):
        """Test that most recent session is returned for duplicate conversations."""
        token1 = stm.create_session("Task 1")
        stm.associate_conversation(token1, "conv_12345")
        
        import time
        time.sleep(0.01)
        
        token2 = stm.create_session("Task 2")
        stm.associate_conversation(token2, "conv_12345")
        
        session = stm.find_by_conversation("conv_12345")
        
        assert session.token == token2


class TestStaleSessionCleanup:
    """Test automatic cleanup of stale sessions."""
    
    def test_cleanup_stale_sessions(self, stm, temp_db):
        """Test cleaning up stale sessions."""
        # Create old active session
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        
        old_time = datetime.now() - timedelta(hours=25)
        cursor.execute("""
            INSERT INTO session_tokens 
            (token, description, status, created_at, last_activity, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
        """, ("SESSION_old_123", "Old task", "active", old_time, old_time, "{}"))
        
        conn.commit()
        conn.close()
        
        # Create recent session
        stm.create_session("Recent task")
        
        # Cleanup stale sessions
        count = stm.cleanup_stale_sessions(hours=24)
        
        assert count == 1
        
        # Verify old session is expired
        session = stm.get_session("SESSION_old_123")
        assert session.status == SessionStatus.EXPIRED
    
    def test_cleanup_no_stale_sessions(self, stm):
        """Test cleanup when no stale sessions exist."""
        stm.create_session("Recent task")
        
        count = stm.cleanup_stale_sessions(hours=24)
        
        assert count == 0
    
    def test_cleanup_preserves_completed(self, stm, temp_db):
        """Test that completed sessions are not expired."""
        # Create old completed session
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        
        old_time = datetime.now() - timedelta(hours=25)
        cursor.execute("""
            INSERT INTO session_tokens 
            (token, description, status, created_at, last_activity, completed_at, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, ("SESSION_old_completed", "Old task", "completed", old_time, old_time, old_time, "{}"))
        
        conn.commit()
        conn.close()
        
        # Cleanup should not affect completed sessions
        count = stm.cleanup_stale_sessions(hours=24)
        
        assert count == 0
        
        session = stm.get_session("SESSION_old_completed")
        assert session.status == SessionStatus.COMPLETED


class TestStatistics:
    """Test statistics reporting."""
    
    def test_get_statistics_empty(self, stm):
        """Test statistics with no sessions."""
        stats = stm.get_statistics()
        
        assert stats["total_sessions"] == 0
        assert not stats["has_active_session"]
    
    def test_get_statistics_with_sessions(self, stm):
        """Test statistics with various sessions."""
        token1 = stm.create_session("Task 1")
        token2 = stm.create_session("Task 2")
        token3 = stm.create_session("Task 3")
        
        stm.complete_session(token1)
        stm.pause_session(token2)
        
        stats = stm.get_statistics()
        
        assert stats["total_sessions"] == 3
        assert stats["has_active_session"]
        assert "status_counts" in stats
        assert stats["status_counts"]["completed"] == 1
        assert stats["status_counts"]["active"] == 1
        assert stats["status_counts"]["paused"] == 1
    
    def test_get_statistics_average_duration(self, stm):
        """Test average duration calculation."""
        token = stm.create_session("Task 1")
        stm.complete_session(token)
        
        stats = stm.get_statistics()
        
        assert "average_duration_hours" in stats
        assert stats["average_duration_hours"] >= 0


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_operations_on_nonexistent_token(self, stm):
        """Test operations on non-existent token (should not raise)."""
        # These should not raise errors
        stm.associate_conversation("nonexistent", "conv_123")
        stm.update_activity("nonexistent")
        stm.pause_session("nonexistent")
        stm.complete_session("nonexistent")
    
    def test_multiple_pauses_and_resumes(self, stm):
        """Test multiple pause/resume cycles."""
        token = stm.create_session("Task 1")
        
        stm.pause_session(token)
        stm.resume_session(token)
        stm.pause_session(token)
        stm.resume_session(token)
        
        session = stm.get_session(token)
        assert session.status == SessionStatus.ACTIVE
    
    def test_session_with_empty_metadata(self, stm):
        """Test session creation with empty metadata."""
        token = stm.create_session("Task 1", metadata={})
        
        session = stm.get_session(token)
        assert session.metadata == {}
