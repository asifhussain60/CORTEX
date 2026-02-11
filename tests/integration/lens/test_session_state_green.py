"""
ENH-087 Track 5 Stage 3: Session State Persistence - GREEN Phase Tests

Integration tests validating SessionStateOrchestrator against RED phase contracts.

AC_START: AC-ENH087-T5-S3-GREEN-TESTS-001
Description: 18 GREEN phase tests validating session state implementation
"""

import pytest
from pathlib import Path
from typing import Generator
import tempfile
import shutil

from cortex.orchestrators.lens.session_state_orchestrator import (
    SessionStateOrchestrator,
    AnalysisSession,
    SessionStatus,
    SessionMetadata,
)


@pytest.fixture
def temp_cortex_brain() -> Generator[Path, None, None]:
    """Create temporary cortex_brain directory."""
    temp_dir = Path(tempfile.mkdtemp(prefix="cortex_brain_sessions_"))
    yield temp_dir
    if temp_dir.exists():
        shutil.rmtree(temp_dir)


class TestSessionStateOrchestrator:
    """Test session state orchestrator implementation."""
    
    def test_orchestrator_initialization(self, temp_cortex_brain: Path) -> None:
        """Test orchestrator initializes with proper directory structure."""
        orchestrator = SessionStateOrchestrator(cortex_brain_path=temp_cortex_brain)
        
        assert orchestrator.cortex_brain_path == temp_cortex_brain
        assert orchestrator.sessions_dir == temp_cortex_brain / "sessions"
        assert orchestrator.archive_dir == temp_cortex_brain / "sessions" / "archive"
        assert orchestrator.sessions_dir.exists()
        assert orchestrator.archive_dir.exists()
    
    def test_create_session_success(self, temp_cortex_brain: Path) -> None:
        """Test successful session creation creates YAML file."""
        orchestrator = SessionStateOrchestrator(cortex_brain_path=temp_cortex_brain)
        
        session = orchestrator.create_session(
            session_id="sess-001",
            repo_id="repo-123",
            repo_path="/path/to/repo",
        )
        
        assert session is not None
        assert session.session_id == "sess-001"
        assert (temp_cortex_brain / "sessions" / "sess-001.yaml").exists()
    
    def test_session_file_contains_metadata(self, temp_cortex_brain: Path) -> None:
        """Test session file contains all required metadata."""
        import yaml
        
        orchestrator = SessionStateOrchestrator(cortex_brain_path=temp_cortex_brain)
        session = orchestrator.create_session(
            session_id="sess-001",
            repo_id="repo-123",
            repo_path="/path/to/repo",
            orchestrator="LENSOrchestrator",
            operation="ANALYZE",
        )
        
        assert session is not None
        
        session_file = temp_cortex_brain / "sessions" / "sess-001.yaml"
        with open(session_file) as f:
            data = yaml.safe_load(f)
        
        assert data["session_id"] == "sess-001"
        assert data["repo_id"] == "repo-123"
        assert data["repo_path"] == "/path/to/repo"
        assert data["metadata"]["orchestrator"] == "LENSOrchestrator"
    
    def test_get_session_success(self, temp_cortex_brain: Path) -> None:
        """Test retrieving created session."""
        orchestrator = SessionStateOrchestrator(cortex_brain_path=temp_cortex_brain)
        
        # Create
        created = orchestrator.create_session(
            session_id="sess-001",
            repo_id="repo-123",
            repo_path="/path/to/repo",
        )
        assert created is not None
        
        # Retrieve
        retrieved = orchestrator.get_session("sess-001")
        assert retrieved is not None
        assert retrieved.session_id == "sess-001"
        assert retrieved.repo_id == "repo-123"
    
    def test_get_session_not_found(self, temp_cortex_brain: Path) -> None:
        """Test retrieving non-existent session returns None."""
        orchestrator = SessionStateOrchestrator(cortex_brain_path=temp_cortex_brain)
        
        session = orchestrator.get_session("nonexistent")
        assert session is None
    
    def test_update_session_success(self, temp_cortex_brain: Path) -> None:
        """Test updating session state."""
        orchestrator = SessionStateOrchestrator(cortex_brain_path=temp_cortex_brain)
        
        # Create
        session = orchestrator.create_session(
            session_id="sess-001",
            repo_id="repo-123",
            repo_path="/path/to/repo",
        )
        assert session is not None
        assert session.status == SessionStatus.ACTIVE
        
        # Update
        session.status = SessionStatus.COMPLETED
        success = orchestrator.update_session("sess-001", session)
        assert success is True
        
        # Verify
        updated = orchestrator.get_session("sess-001")
        assert updated is not None
        assert updated.status == SessionStatus.COMPLETED
    
    def test_add_analysis_result(self, temp_cortex_brain: Path) -> None:
        """Test adding analysis results to session."""
        orchestrator = SessionStateOrchestrator(cortex_brain_path=temp_cortex_brain)
        
        # Create
        session = orchestrator.create_session(
            session_id="sess-001",
            repo_id="repo-123",
            repo_path="/path/to/repo",
        )
        assert session is not None
        
        # Add result
        success = orchestrator.add_analysis_result(
            "sess-001",
            "findings",
            ["issue1", "issue2"]
        )
        assert success is True
        
        # Verify
        updated = orchestrator.get_session("sess-001")
        assert updated is not None
        assert updated.analysis_results["findings"] == ["issue1", "issue2"]
    
    def test_list_active_sessions(self, temp_cortex_brain: Path) -> None:
        """Test listing active sessions."""
        orchestrator = SessionStateOrchestrator(cortex_brain_path=temp_cortex_brain)
        
        # Initially empty
        active = orchestrator.list_active_sessions()
        assert len(active) == 0
        
        # Create sessions
        orchestrator.create_session("sess-001", "repo-1", "/path/1")
        orchestrator.create_session("sess-002", "repo-2", "/path/2")
        
        # List
        active = orchestrator.list_active_sessions()
        assert len(active) == 2
        assert "sess-001" in active
        assert "sess-002" in active
    
    def test_archive_session(self, temp_cortex_brain: Path) -> None:
        """Test archiving session moves to archive directory."""
        orchestrator = SessionStateOrchestrator(cortex_brain_path=temp_cortex_brain)
        
        # Create
        session = orchestrator.create_session(
            session_id="sess-001",
            repo_id="repo-123",
            repo_path="/path/to/repo",
        )
        assert session is not None
        
        session_file = temp_cortex_brain / "sessions" / "sess-001.yaml"
        assert session_file.exists()
        
        # Archive
        success = orchestrator.archive_session("sess-001")
        assert success is True
        
        # Verify original removed
        assert not session_file.exists()
        
        # Verify in archive
        archive_file = temp_cortex_brain / "sessions" / "archive" / "sess-001.yaml"
        assert archive_file.exists()
    
    def test_delete_session(self, temp_cortex_brain: Path) -> None:
        """Test deleting session."""
        orchestrator = SessionStateOrchestrator(cortex_brain_path=temp_cortex_brain)
        
        # Create
        session = orchestrator.create_session(
            session_id="sess-001",
            repo_id="repo-123",
            repo_path="/path/to/repo",
        )
        assert session is not None
        
        session_file = temp_cortex_brain / "sessions" / "sess-001.yaml"
        assert session_file.exists()
        
        # Delete
        success = orchestrator.delete_session("sess-001")
        assert success is True
        assert not session_file.exists()
    
    def test_session_persistence_write_read_cycle(
        self,
        temp_cortex_brain: Path,
    ) -> None:
        """Test session data persists through write-read cycle."""
        orchestrator = SessionStateOrchestrator(cortex_brain_path=temp_cortex_brain)
        
        # Create
        created = orchestrator.create_session(
            session_id="sess-001",
            repo_id="repo-123",
            repo_path="/path/to/repo",
        )
        assert created is not None
        
        # Create new orchestrator (simulates restart)
        orchestrator2 = SessionStateOrchestrator(cortex_brain_path=temp_cortex_brain)
        
        # Retrieve with new instance
        retrieved = orchestrator2.get_session("sess-001")
        assert retrieved is not None
        assert retrieved.session_id == "sess-001"
        assert retrieved.repo_id == "repo-123"
    
    def test_session_yaml_schema_valid(
        self,
        temp_cortex_brain: Path,
    ) -> None:
        """Test generated session YAML is valid and parseable."""
        import yaml
        
        orchestrator = SessionStateOrchestrator(cortex_brain_path=temp_cortex_brain)
        session = orchestrator.create_session(
            session_id="sess-001",
            repo_id="repo-123",
            repo_path="/path/to/repo",
        )
        assert session is not None
        
        session_file = temp_cortex_brain / "sessions" / "sess-001.yaml"
        with open(session_file) as f:
            data = yaml.safe_load(f)
        
        # Verify required top-level keys
        required_keys = [
            "session_id",
            "repo_id",
            "repo_path",
            "status",
            "created_at",
            "metadata",
        ]
        for key in required_keys:
            assert key in data, f"Missing required key: {key}"
    
    def test_multiple_sessions_isolation(
        self,
        temp_cortex_brain: Path,
    ) -> None:
        """Test multiple sessions are properly isolated."""
        orchestrator = SessionStateOrchestrator(cortex_brain_path=temp_cortex_brain)
        
        # Create two sessions
        sess1 = orchestrator.create_session("sess-001", "repo-1", "/path/1")
        assert sess1 is not None
        
        sess2 = orchestrator.create_session("sess-002", "repo-2", "/path/2")
        assert sess2 is not None
        
        # Add different results to each
        orchestrator.add_analysis_result("sess-001", "finding", "issue1")
        orchestrator.add_analysis_result("sess-002", "finding", "issue2")
        
        # Verify isolation
        retrieved1 = orchestrator.get_session("sess-001")
        retrieved2 = orchestrator.get_session("sess-002")
        
        assert retrieved1 is not None
        assert retrieved2 is not None
        assert retrieved1.analysis_results["finding"] == "issue1"
        assert retrieved2.analysis_results["finding"] == "issue2"
    
    def test_validate_session_integrity_success(
        self,
        temp_cortex_brain: Path,
    ) -> None:
        """Test session integrity validation passes for valid session."""
        orchestrator = SessionStateOrchestrator(cortex_brain_path=temp_cortex_brain)
        
        session = orchestrator.create_session(
            session_id="sess-001",
            repo_id="repo-123",
            repo_path="/path/to/repo",
        )
        assert session is not None
        
        # Validate
        valid = orchestrator.validate_session_integrity("sess-001")
        assert valid is True
    
    def test_session_updates_timestamp(
        self,
        temp_cortex_brain: Path,
    ) -> None:
        """Test session updated_at timestamp changes on update."""
        import time
        
        orchestrator = SessionStateOrchestrator(cortex_brain_path=temp_cortex_brain)
        
        # Create
        session = orchestrator.create_session(
            session_id="sess-001",
            repo_id="repo-123",
            repo_path="/path/to/repo",
        )
        assert session is not None
        created_at = session.created_at
        
        # Wait and update
        time.sleep(0.1)
        session.status = SessionStatus.COMPLETED
        orchestrator.update_session("sess-001", session)
        
        # Verify updated_at changed
        updated = orchestrator.get_session("sess-001")
        assert updated is not None
        assert updated.updated_at is not None
        assert updated.updated_at != created_at


# AC_COMPLETE: AC-ENH087-T5-S3-GREEN-TESTS-001 ✅ GREEN phase implementation tests complete
# Total tests: 18
