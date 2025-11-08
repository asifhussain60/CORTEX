"""
Tests for CORTEX Tier 1: Work State Manager
Comprehensive test coverage matching test_working_memory.py pattern (22/22).
"""

import pytest
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from src.tier1.work_state_manager import (
    WorkStateManager,
    WorkState,
    WorkStatus
)


@pytest.fixture
def temp_db(tmp_path):
    """Create a temporary database for testing."""
    db_path = tmp_path / "test_work_state.db"
    return db_path


@pytest.fixture
def wsm(temp_db):
    """Create a WorkStateManager instance."""
    return WorkStateManager(db_path=temp_db)


class TestDatabaseInitialization:
    """Test database creation and schema."""
    
    def test_database_created(self, temp_db):
        """Test that database file is created."""
        wsm = WorkStateManager(db_path=temp_db)
        assert temp_db.exists()
    
    def test_work_sessions_table_exists(self, wsm, temp_db):
        """Test that work_sessions table is created."""
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='work_sessions'
        """)
        assert cursor.fetchone() is not None
        conn.close()
    
    def test_work_progress_table_exists(self, wsm, temp_db):
        """Test that work_progress table is created."""
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='work_progress'
        """)
        assert cursor.fetchone() is not None
        conn.close()
    
    def test_indexes_created(self, wsm, temp_db):
        """Test that indexes are created."""
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='index'
        """)
        indexes = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        assert "idx_work_sessions_status" in indexes
        assert "idx_work_progress_session" in indexes


class TestTaskLifecycle:
    """Test task creation, update, and completion."""
    
    def test_start_task_basic(self, wsm):
        """Test starting a new task."""
        session_id = wsm.start_task("Implement authentication")
        
        assert session_id.startswith("work_")
        assert wsm.has_incomplete_work()
    
    def test_start_task_with_files(self, wsm):
        """Test starting a task with initial files."""
        files = ["src/auth.py", "tests/test_auth.py"]
        session_id = wsm.start_task("Implement auth", files=files)
        
        state = wsm.get_state(session_id)
        assert state is not None
        assert set(state.files_touched) == set(files)
    
    def test_start_task_with_metadata(self, wsm):
        """Test starting a task with metadata."""
        metadata = {"branch": "feature/auth", "issue": "123"}
        session_id = wsm.start_task("Implement auth", metadata=metadata)
        
        state = wsm.get_state(session_id)
        assert state.metadata == metadata
    
    def test_update_progress(self, wsm):
        """Test updating task progress."""
        session_id = wsm.start_task("Implement auth")
        
        wsm.update_progress("Added login endpoint", files_touched=["src/auth.py"])
        
        state = wsm.get_state(session_id)
        assert "Added login endpoint" in state.progress_notes
        assert "src/auth.py" in state.files_touched
    
    def test_update_progress_multiple_times(self, wsm):
        """Test multiple progress updates."""
        session_id = wsm.start_task("Implement auth")
        
        wsm.update_progress("Added login", files_touched=["src/auth.py"])
        wsm.update_progress("Added tests", files_touched=["tests/test_auth.py"])
        
        state = wsm.get_state(session_id)
        assert len(state.progress_notes) >= 2
        assert len(state.files_touched) == 2
    
    def test_complete_task(self, wsm):
        """Test completing a task."""
        session_id = wsm.start_task("Implement auth")
        
        wsm.complete_task(session_id)
        
        state = wsm.get_state(session_id)
        assert state.status == WorkStatus.COMPLETED
        assert not wsm.has_incomplete_work()
    
    def test_pause_task(self, wsm):
        """Test pausing a task."""
        session_id = wsm.start_task("Implement auth")
        
        wsm.pause_task(session_id)
        
        state = wsm.get_state(session_id)
        assert state.status == WorkStatus.PAUSED
        assert wsm.has_incomplete_work()
    
    def test_abandon_task(self, wsm):
        """Test abandoning a task."""
        session_id = wsm.start_task("Implement auth")
        
        wsm.abandon_task(session_id, reason="Blocked by API issue")
        
        state = wsm.get_state(session_id)
        assert state.status == WorkStatus.ABANDONED


class TestStateRetrieval:
    """Test state retrieval operations."""
    
    def test_get_current_state_with_active_work(self, wsm):
        """Test getting current state when work is active."""
        session_id = wsm.start_task("Implement auth")
        
        state = wsm.get_current_state()
        
        assert state is not None
        assert state.session_id == session_id
        assert state.status == WorkStatus.IN_PROGRESS
    
    def test_get_current_state_no_active_work(self, wsm):
        """Test getting current state with no active work."""
        state = wsm.get_current_state()
        assert state is None
    
    def test_get_state_by_id(self, wsm):
        """Test getting state by specific session ID."""
        session_id = wsm.start_task("Implement auth")
        
        state = wsm.get_state(session_id)
        
        assert state is not None
        assert state.session_id == session_id
    
    def test_get_state_nonexistent(self, wsm):
        """Test getting state for non-existent session."""
        state = wsm.get_state("nonexistent_session")
        assert state is None
    
    def test_has_incomplete_work_true(self, wsm):
        """Test has_incomplete_work returns True with active work."""
        wsm.start_task("Implement auth")
        assert wsm.has_incomplete_work()
    
    def test_has_incomplete_work_false(self, wsm):
        """Test has_incomplete_work returns False with no active work."""
        assert not wsm.has_incomplete_work()
    
    def test_get_incomplete_sessions(self, wsm):
        """Test getting all incomplete sessions."""
        session1 = wsm.start_task("Task 1")
        session2 = wsm.start_task("Task 2")
        wsm.pause_task(session1)
        
        incomplete = wsm.get_incomplete_sessions()
        
        assert len(incomplete) == 2
        session_ids = [s.session_id for s in incomplete]
        assert session1 in session_ids
        assert session2 in session_ids
    
    def test_get_recent_completed(self, wsm):
        """Test getting recent completed sessions."""
        session1 = wsm.start_task("Task 1")
        session2 = wsm.start_task("Task 2")
        
        wsm.complete_task(session1)
        wsm.complete_task(session2)
        
        completed = wsm.get_recent_completed(limit=2)
        
        assert len(completed) == 2
        assert all(s.status == WorkStatus.COMPLETED for s in completed)


class TestWorkStateClass:
    """Test WorkState dataclass methods."""
    
    def test_work_state_to_dict(self, wsm):
        """Test converting WorkState to dictionary."""
        session_id = wsm.start_task("Test task")
        state = wsm.get_state(session_id)
        
        state_dict = state.to_dict()
        
        assert state_dict["session_id"] == session_id
        assert state_dict["status"] == "in_progress"
        assert "started_at" in state_dict
        assert "last_activity" in state_dict
    
    def test_work_state_from_dict(self, wsm):
        """Test creating WorkState from dictionary."""
        session_id = wsm.start_task("Test task")
        state = wsm.get_state(session_id)
        
        state_dict = state.to_dict()
        restored_state = WorkState.from_dict(state_dict)
        
        assert restored_state.session_id == state.session_id
        assert restored_state.task_description == state.task_description
    
    def test_is_stale_false(self, wsm):
        """Test is_stale returns False for recent work."""
        session_id = wsm.start_task("Test task")
        state = wsm.get_state(session_id)
        
        assert not state.is_stale(hours=24)
    
    def test_is_stale_true(self, wsm, temp_db):
        """Test is_stale returns True for old work."""
        # Create a session with old timestamp
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        
        old_time = datetime.now() - timedelta(hours=25)
        cursor.execute("""
            INSERT INTO work_sessions 
            (session_id, task_description, status, started_at, last_activity, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
        """, ("old_session", "Old task", "in_progress", old_time, old_time, "{}"))
        
        conn.commit()
        conn.close()
        
        state = wsm.get_state("old_session")
        assert state.is_stale(hours=24)
    
    def test_duration_minutes(self, wsm):
        """Test duration calculation."""
        session_id = wsm.start_task("Test task")
        
        # Add some delay (simulated by progress update)
        import time
        time.sleep(0.1)
        wsm.update_progress("Progress update")
        
        state = wsm.get_state(session_id)
        duration = state.duration_minutes()
        
        assert duration >= 0
        assert duration < 1  # Should be less than 1 minute for test


class TestStaleSessionCleanup:
    """Test automatic cleanup of stale sessions."""
    
    def test_cleanup_stale_sessions(self, wsm, temp_db):
        """Test cleaning up stale sessions."""
        # Create old session
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        
        old_time = datetime.now() - timedelta(hours=25)
        cursor.execute("""
            INSERT INTO work_sessions 
            (session_id, task_description, status, started_at, last_activity, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
        """, ("old_session", "Old task", "in_progress", old_time, old_time, "{}"))
        
        conn.commit()
        conn.close()
        
        # Create recent session
        wsm.start_task("Recent task")
        
        # Cleanup stale sessions
        count = wsm.cleanup_stale_sessions(hours=24)
        
        assert count == 1
        
        # Verify old session is abandoned
        state = wsm.get_state("old_session")
        assert state.status == WorkStatus.ABANDONED
    
    def test_cleanup_no_stale_sessions(self, wsm):
        """Test cleanup when no stale sessions exist."""
        wsm.start_task("Recent task")
        
        count = wsm.cleanup_stale_sessions(hours=24)
        
        assert count == 0


class TestStatistics:
    """Test statistics reporting."""
    
    def test_get_statistics_empty(self, wsm):
        """Test statistics with no sessions."""
        stats = wsm.get_statistics()
        
        assert stats["total_sessions"] == 0
        assert not stats["has_incomplete_work"]
    
    def test_get_statistics_with_sessions(self, wsm):
        """Test statistics with various sessions."""
        session1 = wsm.start_task("Task 1")
        session2 = wsm.start_task("Task 2")
        session3 = wsm.start_task("Task 3")
        
        wsm.complete_task(session1)
        wsm.pause_task(session2)
        
        stats = wsm.get_statistics()
        
        assert stats["total_sessions"] == 3
        assert stats["has_incomplete_work"]
        assert "status_counts" in stats
        assert stats["status_counts"][WorkStatus.COMPLETED.value] == 1
        assert stats["status_counts"][WorkStatus.IN_PROGRESS.value] == 1
        assert stats["status_counts"][WorkStatus.PAUSED.value] == 1
    
    def test_get_statistics_average_duration(self, wsm):
        """Test average duration calculation."""
        session1 = wsm.start_task("Task 1")
        wsm.complete_task(session1)
        
        stats = wsm.get_statistics()
        
        assert "average_completion_minutes" in stats
        assert stats["average_completion_minutes"] >= 0


class TestFileAggregation:
    """Test file tracking across progress updates."""
    
    def test_files_aggregated_correctly(self, wsm):
        """Test that files are aggregated from multiple updates."""
        session_id = wsm.start_task("Multi-file task")
        
        wsm.update_progress("Edit file 1", files_touched=["src/file1.py"])
        wsm.update_progress("Edit file 2", files_touched=["src/file2.py"])
        wsm.update_progress("Edit file 1 again", files_touched=["src/file1.py"])
        
        state = wsm.get_state(session_id)
        
        # Should have unique files only
        assert set(state.files_touched) == {"src/file1.py", "src/file2.py"}
    
    def test_files_sorted(self, wsm):
        """Test that files are returned sorted."""
        session_id = wsm.start_task("Multi-file task")
        
        wsm.update_progress("Files", files_touched=["z.py", "a.py", "m.py"])
        
        state = wsm.get_state(session_id)
        
        assert state.files_touched == ["a.py", "m.py", "z.py"]


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_update_progress_no_active_session(self, wsm):
        """Test updating progress with no active session."""
        with pytest.raises(ValueError, match="No active work session found"):
            wsm.update_progress("Some progress")
    
    def test_complete_task_no_session(self, wsm):
        """Test completing task with no active session."""
        # Should not raise, just no-op
        wsm.complete_task()
    
    def test_get_incomplete_sessions_exclude_stale(self, wsm, temp_db):
        """Test excluding stale sessions from incomplete list."""
        # Create stale session
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        
        old_time = datetime.now() - timedelta(hours=25)
        cursor.execute("""
            INSERT INTO work_sessions 
            (session_id, task_description, status, started_at, last_activity, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
        """, ("stale_session", "Stale task", "in_progress", old_time, old_time, "{}"))
        
        conn.commit()
        conn.close()
        
        # Create fresh session
        wsm.start_task("Fresh task")
        
        # Get incomplete sessions (exclude stale)
        incomplete = wsm.get_incomplete_sessions(include_stale=False)
        
        assert len(incomplete) == 1
        assert incomplete[0].task_description == "Fresh task"
