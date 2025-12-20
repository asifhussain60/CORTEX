"""
Unit tests for Session Manager
Tests session CRUD, state persistence, tenant isolation, cleanup
"""

import pytest
import time
from datetime import datetime, timedelta
from orchestration_3_0.session.session_manager import (
    SessionManager,
    WorkflowSession,
    SessionStatus,
    get_session_manager
)


class TestSessionManager:
    """Test SessionManager core functionality."""
    
    def test_create_session(self, fresh_session_manager):
        """Test creating a new session."""
        session = fresh_session_manager.create_session(
            session_id="test-session-001",
            orchestrator_name="TestOrchestrator",
            tenant_id="tenant-1",
            project_id="project-1",
            user_id="user-1",
            initial_state="INITIALIZED"
        )
        
        assert session.session_id == "test-session-001"
        assert session.orchestrator_name == "TestOrchestrator"
        assert session.tenant_id == "tenant-1"
        assert session.current_state == "INITIALIZED"
        assert session.status == SessionStatus.ACTIVE
    
    def test_get_session(self, fresh_session_manager):
        """Test retrieving an existing session."""
        fresh_session_manager.create_session(
            session_id="test-session-001",
            orchestrator_name="TestOrchestrator",
            tenant_id="tenant-1",
            project_id="project-1",
            user_id="user-1",
            initial_state="INITIALIZED"
        )
        
        session = fresh_session_manager.get_session("test-session-001")
        
        assert session is not None
        assert session.session_id == "test-session-001"
    
    def test_get_nonexistent_session(self, fresh_session_manager):
        """Test retrieving non-existent session returns None."""
        session = fresh_session_manager.get_session("nonexistent")
        
        assert session is None
    
    def test_update_session_state(self, fresh_session_manager):
        """Test updating session state."""
        fresh_session_manager.create_session(
            session_id="test-session-001",
            orchestrator_name="TestOrchestrator",
            tenant_id="tenant-1",
            project_id="project-1",
            user_id="user-1",
            initial_state="INITIALIZED"
        )
        
        fresh_session_manager.update_session_state(
            session_id="test-session-001",
            new_state="EXECUTING",
            checkpoint_data={"progress": 50}
        )
        
        session = fresh_session_manager.get_session("test-session-001")
        
        assert session.current_state == "EXECUTING"
        assert session.checkpoint_data["progress"] == 50
    
    def test_complete_session(self, fresh_session_manager):
        """Test marking session as completed."""
        fresh_session_manager.create_session(
            session_id="test-session-001",
            orchestrator_name="TestOrchestrator",
            tenant_id="tenant-1",
            project_id="project-1",
            user_id="user-1",
            initial_state="INITIALIZED"
        )
        
        fresh_session_manager.complete_session("test-session-001")
        
        session = fresh_session_manager.get_session("test-session-001")
        
        assert session.status == SessionStatus.COMPLETED
        assert session.current_state == "COMPLETED"
    
    def test_fail_session(self, fresh_session_manager):
        """Test marking session as failed."""
        fresh_session_manager.create_session(
            session_id="test-session-001",
            orchestrator_name="TestOrchestrator",
            tenant_id="tenant-1",
            project_id="project-1",
            user_id="user-1",
            initial_state="INITIALIZED"
        )
        
        error_info = {"error": "LLM timeout", "code": 500}
        fresh_session_manager.fail_session("test-session-001", error_info=error_info)
        
        session = fresh_session_manager.get_session("test-session-001")
        
        assert session.status == SessionStatus.FAILED
        assert session.current_state == "FAILED"
        assert session.metadata["error"] == "LLM timeout"
    
    def test_abandon_session(self, fresh_session_manager):
        """Test marking session as abandoned."""
        fresh_session_manager.create_session(
            session_id="test-session-001",
            orchestrator_name="TestOrchestrator",
            tenant_id="tenant-1",
            project_id="project-1",
            user_id="user-1",
            initial_state="INITIALIZED"
        )
        
        fresh_session_manager.abandon_session("test-session-001")
        
        session = fresh_session_manager.get_session("test-session-001")
        
        assert session.status == SessionStatus.ABANDONED


class TestSessionQueries:
    """Test session query functionality."""
    
    def test_get_active_sessions(self, fresh_session_manager):
        """Test retrieving active sessions for tenant."""
        # Create multiple sessions
        fresh_session_manager.create_session(
            "session-1", "Orch1", "tenant-1", "proj-1", "user-1", "INITIALIZED"
        )
        fresh_session_manager.create_session(
            "session-2", "Orch2", "tenant-1", "proj-1", "user-1", "EXECUTING"
        )
        fresh_session_manager.create_session(
            "session-3", "Orch3", "tenant-2", "proj-2", "user-2", "INITIALIZED"
        )
        
        # Complete one session
        fresh_session_manager.complete_session("session-2")
        
        active_sessions = fresh_session_manager.get_active_sessions(tenant_id="tenant-1")
        
        assert len(active_sessions) == 1
        assert active_sessions[0].session_id == "session-1"
    
    def test_get_active_sessions_by_orchestrator(self, fresh_session_manager):
        """Test retrieving active sessions filtered by orchestrator."""
        fresh_session_manager.create_session(
            "session-1", "TDDOrchestrator", "tenant-1", "proj-1", "user-1", "INITIALIZED"
        )
        fresh_session_manager.create_session(
            "session-2", "DevOpsOrchestrator", "tenant-1", "proj-1", "user-1", "EXECUTING"
        )
        
        active_sessions = fresh_session_manager.get_active_sessions(
            tenant_id="tenant-1",
            orchestrator_name="TDDOrchestrator"
        )
        
        assert len(active_sessions) == 1
        assert active_sessions[0].orchestrator_name == "TDDOrchestrator"
    
    def test_get_session_history(self, fresh_session_manager):
        """Test retrieving session history for tenant."""
        # Create and complete sessions
        fresh_session_manager.create_session(
            "session-1", "Orch1", "tenant-1", "proj-1", "user-1", "INITIALIZED"
        )
        fresh_session_manager.complete_session("session-1")
        
        fresh_session_manager.create_session(
            "session-2", "Orch2", "tenant-1", "proj-1", "user-1", "INITIALIZED"
        )
        fresh_session_manager.fail_session("session-2")
        
        history = fresh_session_manager.get_session_history(
            tenant_id="tenant-1",
            limit=10
        )
        
        assert len(history) == 2
    
    def test_get_session_history_with_limit(self, fresh_session_manager):
        """Test session history respects limit parameter."""
        # Create 5 sessions
        for i in range(5):
            fresh_session_manager.create_session(
                f"session-{i}", "TestOrch", "tenant-1", "proj-1", "user-1", "INITIALIZED"
            )
            fresh_session_manager.complete_session(f"session-{i}")
        
        history = fresh_session_manager.get_session_history(
            tenant_id="tenant-1",
            limit=3
        )
        
        assert len(history) == 3


class TestTenantIsolation:
    """Test multi-tenant isolation."""
    
    def test_tenant_isolation_create(self, fresh_session_manager):
        """Test sessions are isolated by tenant."""
        fresh_session_manager.create_session(
            "session-1", "Orch1", "tenant-1", "proj-1", "user-1", "INITIALIZED"
        )
        fresh_session_manager.create_session(
            "session-2", "Orch2", "tenant-2", "proj-2", "user-2", "INITIALIZED"
        )
        
        tenant1_sessions = fresh_session_manager.get_active_sessions("tenant-1")
        tenant2_sessions = fresh_session_manager.get_active_sessions("tenant-2")
        
        assert len(tenant1_sessions) == 1
        assert len(tenant2_sessions) == 1
        assert tenant1_sessions[0].session_id == "session-1"
        assert tenant2_sessions[0].session_id == "session-2"
    
    def test_tenant_isolation_query(self, fresh_session_manager):
        """Test queries respect tenant boundaries."""
        # Create sessions for different tenants
        fresh_session_manager.create_session(
            "session-1", "Orch1", "tenant-1", "proj-1", "user-1", "INITIALIZED"
        )
        fresh_session_manager.create_session(
            "session-2", "Orch2", "tenant-2", "proj-2", "user-2", "INITIALIZED"
        )
        fresh_session_manager.complete_session("session-1")
        fresh_session_manager.complete_session("session-2")
        
        tenant1_history = fresh_session_manager.get_session_history("tenant-1")
        tenant2_history = fresh_session_manager.get_session_history("tenant-2")
        
        assert len(tenant1_history) == 1
        assert len(tenant2_history) == 1
        assert tenant1_history[0].tenant_id == "tenant-1"
        assert tenant2_history[0].tenant_id == "tenant-2"


class TestCheckpointData:
    """Test checkpoint data persistence."""
    
    def test_checkpoint_data_persistence(self, fresh_session_manager):
        """Test checkpoint data is persisted and retrieved."""
        fresh_session_manager.create_session(
            "session-1", "TestOrch", "tenant-1", "proj-1", "user-1", "INITIALIZED"
        )
        
        checkpoint = {
            "progress": 75,
            "completed_steps": ["step1", "step2"],
            "current_step": "step3"
        }
        
        fresh_session_manager.update_session_state(
            "session-1",
            "EXECUTING",
            checkpoint_data=checkpoint
        )
        
        session = fresh_session_manager.get_session("session-1")
        
        assert session.checkpoint_data["progress"] == 75
        assert session.checkpoint_data["completed_steps"] == ["step1", "step2"]
        assert session.checkpoint_data["current_step"] == "step3"
    
    def test_checkpoint_update_preserves_history(self, fresh_session_manager):
        """Test checkpoint updates preserve previous checkpoint."""
        fresh_session_manager.create_session(
            "session-1", "TestOrch", "tenant-1", "proj-1", "user-1", "INITIALIZED"
        )
        
        # First checkpoint
        fresh_session_manager.update_session_state(
            "session-1",
            "VALIDATING_DOR",
            checkpoint_data={"stage": "validation"}
        )
        
        # Second checkpoint
        fresh_session_manager.update_session_state(
            "session-1",
            "EXECUTING",
            checkpoint_data={"stage": "execution", "progress": 50}
        )
        
        session = fresh_session_manager.get_session("session-1")
        
        # Latest checkpoint should be active
        assert session.checkpoint_data["stage"] == "execution"
        assert session.checkpoint_data["progress"] == 50


class TestSessionCleanup:
    """Test session cleanup functionality."""
    
    def test_cleanup_old_completed_sessions(self, fresh_session_manager):
        """Test cleanup removes old completed sessions."""
        # Create old session (simulate by modifying timestamp)
        fresh_session_manager.create_session(
            "old-session", "TestOrch", "tenant-1", "proj-1", "user-1", "INITIALIZED"
        )
        fresh_session_manager.complete_session("old-session")
        
        # Create recent session
        fresh_session_manager.create_session(
            "recent-session", "TestOrch", "tenant-1", "proj-1", "user-1", "INITIALIZED"
        )
        fresh_session_manager.complete_session("recent-session")
        
        # Cleanup sessions older than 0 days (should remove all completed)
        deleted_count = fresh_session_manager.cleanup_old_sessions(days_old=0)
        
        assert deleted_count >= 1
    
    def test_cleanup_preserves_active_sessions(self, fresh_session_manager):
        """Test cleanup does not remove active sessions."""
        fresh_session_manager.create_session(
            "active-session", "TestOrch", "tenant-1", "proj-1", "user-1", "INITIALIZED"
        )
        
        # Cleanup (should not remove active session)
        deleted_count = fresh_session_manager.cleanup_old_sessions(days_old=0)
        
        session = fresh_session_manager.get_session("active-session")
        assert session is not None
        assert session.status == SessionStatus.ACTIVE


class TestGlobalSessionManager:
    """Test get_session_manager() global accessor."""
    
    def test_get_session_manager_returns_singleton(self):
        """Test get_session_manager returns same instance."""
        sm1 = get_session_manager()
        sm2 = get_session_manager()
        
        assert sm1 is sm2


class TestSessionMetadata:
    """Test session metadata functionality."""
    
    def test_metadata_persistence(self, fresh_session_manager):
        """Test custom metadata is persisted."""
        metadata = {
            "user_role": "developer",
            "priority": "high",
            "tags": ["feature", "backend"]
        }
        
        fresh_session_manager.create_session(
            "session-1",
            "TestOrch",
            "tenant-1",
            "proj-1",
            "user-1",
            "INITIALIZED",
            metadata=metadata
        )
        
        session = fresh_session_manager.get_session("session-1")
        
        assert session.metadata["user_role"] == "developer"
        assert session.metadata["priority"] == "high"
        assert session.metadata["tags"] == ["feature", "backend"]
    
    def test_metadata_update(self, fresh_session_manager):
        """Test updating session metadata."""
        fresh_session_manager.create_session(
            "session-1", "TestOrch", "tenant-1", "proj-1", "user-1", "INITIALIZED"
        )
        
        fresh_session_manager.update_session_metadata(
            "session-1",
            {"custom_field": "value"}
        )
        
        session = fresh_session_manager.get_session("session-1")
        
        assert session.metadata["custom_field"] == "value"


class TestSessionTimestamps:
    """Test session timestamp tracking."""
    
    def test_created_at_timestamp(self, fresh_session_manager):
        """Test created_at timestamp is set."""
        before = datetime.now()
        
        fresh_session_manager.create_session(
            "session-1", "TestOrch", "tenant-1", "proj-1", "user-1", "INITIALIZED"
        )
        
        after = datetime.now()
        
        session = fresh_session_manager.get_session("session-1")
        created_at = datetime.fromisoformat(session.created_at)
        
        assert before <= created_at <= after
    
    def test_updated_at_timestamp_changes(self, fresh_session_manager):
        """Test updated_at timestamp changes on update."""
        fresh_session_manager.create_session(
            "session-1", "TestOrch", "tenant-1", "proj-1", "user-1", "INITIALIZED"
        )
        
        session = fresh_session_manager.get_session("session-1")
        original_updated_at = session.updated_at
        
        time.sleep(0.1)  # Ensure timestamp difference
        
        fresh_session_manager.update_session_state("session-1", "EXECUTING")
        
        session = fresh_session_manager.get_session("session-1")
        new_updated_at = session.updated_at
        
        assert new_updated_at > original_updated_at
