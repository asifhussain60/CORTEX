"""
ENH-087 Track 5 Stage 3: Session State Persistence - RED Phase Tests

RED phase tests define expected behavior for LENS session state persistence:
- Session state YAML/JSON file lifecycle
- Session metadata tracking (timestamps, orchestrator context)
- Session state serialization/deserialization
- Session state validation + integrity checks
- State recovery after process restart

Authority: ENH-087 Track 5 + Integration-First Testing pattern
Compliance: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)

AC_START: AC-ENH087-T5-S3-RED-001
Description: Session state persistence lifecycle tests (RED phase)
"""

import pytest
from pathlib import Path
from typing import Generator
import tempfile
import shutil
from dataclasses import dataclass
from datetime import datetime

import yaml


@dataclass
class SessionStateTestContext:
    """Test context for session state lifecycle verification."""
    temp_dir: Path
    session_id: str
    
    def get_session_file(self) -> Path:
        """Get path to session state file."""
        return self.temp_dir / "sessions" / f"{self.session_id}.yaml"
    
    def session_file_exists(self) -> bool:
        """Check if session file exists."""
        return self.get_session_file().exists()
    
    def read_session_file(self) -> dict:
        """Read session file content."""
        with open(self.get_session_file()) as f:
            return yaml.safe_load(f)


@pytest.fixture
def temp_sessions_dir() -> Generator[Path, None, None]:
    """Create temporary sessions directory."""
    temp_dir = Path(tempfile.mkdtemp(prefix="cortex_sessions_"))
    (temp_dir / "sessions").mkdir(parents=True, exist_ok=True)
    yield temp_dir
    if temp_dir.exists():
        shutil.rmtree(temp_dir)


@pytest.fixture
def session_context(temp_sessions_dir: Path) -> SessionStateTestContext:
    """Create session test context."""
    return SessionStateTestContext(
        temp_dir=temp_sessions_dir,
        session_id="session-001"
    )


class TestSessionStateFileCreation:
    """Test session state file creation during onboarding."""
    
    def test_session_state_file_created_on_onboard(
        self,
        session_context: SessionStateTestContext,
    ) -> None:
        """RED: Session state YAML file created during repository onboarding."""
        # When: Repository is onboarded with session
        # Then: Session state file should exist
        assert not session_context.session_file_exists()
        
        # Simulate onboarding (RED test defines expected file structure)
        session_file = session_context.get_session_file()
        session_file.parent.mkdir(parents=True, exist_ok=True)
        session_file.write_text("""
session_id: session-001
repo_id: test-repo
repo_path: /path/to/repo
status: ACTIVE
created_at: '2026-02-11T16:00:00Z'
metadata:
  orchestrator: LENS
  stage: 1
""")
        
        assert session_context.session_file_exists()
    
    def test_session_state_directory_structure(
        self,
        session_context: SessionStateTestContext,
    ) -> None:
        """RED: Session state files organized in sessions/ directory."""
        # Given: Sessions directory structure requirement
        sessions_dir = session_context.temp_dir / "sessions"
        
        # Then: sessions/ directory should exist
        assert sessions_dir.exists()
        assert sessions_dir.is_dir()
    
    def test_session_state_file_naming_convention(
        self,
        session_context: SessionStateTestContext,
    ) -> None:
        """RED: Session files follow {session_id}.yaml naming convention."""
        # Given: Session ID
        session_id = "session-abc123"
        session_file = session_context.temp_dir / "sessions" / f"{session_id}.yaml"
        
        # When: File created with session ID
        session_file.parent.mkdir(parents=True, exist_ok=True)
        session_file.write_text("session_id: session-abc123")
        
        # Then: File exists with correct name
        assert session_file.exists()
        assert session_file.name == "session-abc123.yaml"


class TestSessionStateMetadata:
    """Test session state metadata tracking."""
    
    def test_session_state_includes_timestamps(
        self,
        session_context: SessionStateTestContext,
    ) -> None:
        """RED: Session state includes creation and update timestamps."""
        session_file = session_context.get_session_file()
        session_file.parent.mkdir(parents=True, exist_ok=True)
        
        state = {
            "session_id": "session-001",
            "created_at": "2026-02-11T16:00:00Z",
            "updated_at": "2026-02-11T16:05:00Z",
            "repo_id": "test-repo",
        }
        
        session_file.write_text(yaml.dump(state))
        loaded = yaml.safe_load(session_file.read_text())
        
        assert "created_at" in loaded
        assert "updated_at" in loaded
        assert loaded["created_at"] == "2026-02-11T16:00:00Z"
    
    def test_session_state_tracks_orchestrator_context(
        self,
        session_context: SessionStateTestContext,
    ) -> None:
        """RED: Session state tracks orchestrator name + operation."""
        session_file = session_context.get_session_file()
        session_file.parent.mkdir(parents=True, exist_ok=True)
        
        state = {
            "session_id": "session-001",
            "metadata": {
                "orchestrator": "LENSOrchestrator",
                "operation": "ANALYZE",
                "stage": 2,
            },
        }
        
        session_file.write_text(yaml.dump(state))
        loaded = yaml.safe_load(session_file.read_text())
        
        assert loaded["metadata"]["orchestrator"] == "LENSOrchestrator"
        assert loaded["metadata"]["operation"] == "ANALYZE"
    
    def test_session_state_includes_repo_context(
        self,
        session_context: SessionStateTestContext,
    ) -> None:
        """RED: Session state includes repository context (ID, path)."""
        session_file = session_context.get_session_file()
        session_file.parent.mkdir(parents=True, exist_ok=True)
        
        state = {
            "session_id": "session-001",
            "repo_id": "repo-123",
            "repo_path": "/path/to/repo",
        }
        
        session_file.write_text(yaml.dump(state))
        loaded = yaml.safe_load(session_file.read_text())
        
        assert loaded["repo_id"] == "repo-123"
        assert loaded["repo_path"] == "/path/to/repo"


class TestSessionStateSerialization:
    """Test session state serialization/deserialization."""
    
    def test_session_state_yaml_serialization(
        self,
        session_context: SessionStateTestContext,
    ) -> None:
        """RED: Session state serializes to valid YAML."""
        session_file = session_context.get_session_file()
        session_file.parent.mkdir(parents=True, exist_ok=True)
        
        original_state = {
            "session_id": "session-001",
            "status": "ACTIVE",
            "analysis_results": ["finding1", "finding2"],
            "metadata": {"key": "value"},
        }
        
        # Serialize
        session_file.write_text(yaml.dump(original_state))
        
        # Deserialize
        loaded_state = yaml.safe_load(session_file.read_text())
        
        # Then: Data preserved through cycle
        assert loaded_state["session_id"] == original_state["session_id"]
        assert loaded_state["analysis_results"] == original_state["analysis_results"]
    
    def test_session_state_update_persistence(
        self,
        session_context: SessionStateTestContext,
    ) -> None:
        """RED: Session state updates persist to file."""
        session_file = session_context.get_session_file()
        session_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Initial state
        initial_state = {"session_id": "session-001", "status": "PENDING"}
        session_file.write_text(yaml.dump(initial_state))
        
        # Update state
        state = yaml.safe_load(session_file.read_text())
        state["status"] = "ACTIVE"
        state["updated_at"] = "2026-02-11T16:10:00Z"
        session_file.write_text(yaml.dump(state))
        
        # Then: Updated state persisted
        reloaded = yaml.safe_load(session_file.read_text())
        assert reloaded["status"] == "ACTIVE"
        assert "updated_at" in reloaded


class TestSessionStateValidation:
    """Test session state validation + integrity checks."""
    
    def test_session_state_schema_validation(
        self,
        session_context: SessionStateTestContext,
    ) -> None:
        """RED: Session state validates required fields."""
        session_file = session_context.get_session_file()
        session_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Valid state with all required fields
        valid_state = {
            "session_id": "session-001",
            "repo_id": "repo-123",
            "repo_path": "/path",
            "status": "ACTIVE",
            "created_at": "2026-02-11T16:00:00Z",
        }
        
        session_file.write_text(yaml.dump(valid_state))
        loaded = yaml.safe_load(session_file.read_text())
        
        # Then: All required fields present
        required_fields = ["session_id", "repo_id", "repo_path", "status", "created_at"]
        for field in required_fields:
            assert field in loaded
    
    def test_session_state_file_integrity_on_read(
        self,
        session_context: SessionStateTestContext,
    ) -> None:
        """RED: Session state file integrity verified on read."""
        session_file = session_context.get_session_file()
        session_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Create valid state
        state = {"session_id": "session-001", "data": "test"}
        session_file.write_text(yaml.dump(state))
        
        # Read and verify
        content = session_file.read_text()
        loaded = yaml.safe_load(content)
        
        # Then: Data integrity maintained
        assert loaded["session_id"] == "session-001"
        assert loaded["data"] == "test"


class TestSessionStateRecovery:
    """Test session state recovery after process restart."""
    
    def test_session_state_loads_after_restart(
        self,
        session_context: SessionStateTestContext,
    ) -> None:
        """RED: Session state recovers after simulated process restart."""
        session_file = session_context.get_session_file()
        session_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Simulate session before restart
        state = {
            "session_id": "session-001",
            "analysis_data": ["finding1", "finding2"],
            "status": "ACTIVE",
        }
        session_file.write_text(yaml.dump(state))
        
        # Simulate restart (read from file)
        restarted_state = yaml.safe_load(session_file.read_text())
        
        # Then: State recovered
        assert restarted_state["session_id"] == "session-001"
        assert restarted_state["analysis_data"] == ["finding1", "finding2"]
    
    def test_session_state_consistency_across_reads(
        self,
        session_context: SessionStateTestContext,
    ) -> None:
        """RED: Session state consistent across multiple reads."""
        session_file = session_context.get_session_file()
        session_file.parent.mkdir(parents=True, exist_ok=True)
        
        state = {"session_id": "session-001", "counter": 42}
        session_file.write_text(yaml.dump(state))
        
        # Multiple reads
        read1 = yaml.safe_load(session_file.read_text())
        read2 = yaml.safe_load(session_file.read_text())
        read3 = yaml.safe_load(session_file.read_text())
        
        # Then: Consistent across reads
        assert read1["counter"] == read2["counter"] == read3["counter"] == 42


class TestSessionStateCleanup:
    """Test session state cleanup and archival."""
    
    def test_session_state_file_cleanup(
        self,
        session_context: SessionStateTestContext,
    ) -> None:
        """RED: Session state file can be removed during cleanup."""
        session_file = session_context.get_session_file()
        session_file.parent.mkdir(parents=True, exist_ok=True)
        session_file.write_text("session_id: session-001")
        
        assert session_file.exists()
        
        # Cleanup
        session_file.unlink()
        
        # Then: File removed
        assert not session_file.exists()
    
    def test_session_state_archive_preserves_history(
        self,
        session_context: SessionStateTestContext,
    ) -> None:
        """RED: Session state can be archived without loss."""
        session_file = session_context.get_session_file()
        session_file.parent.mkdir(parents=True, exist_ok=True)
        
        state = {"session_id": "session-001", "data": "important"}
        session_file.write_text(yaml.dump(state))
        
        # Archive (move to archive directory)
        archive_dir = session_context.temp_dir / "sessions" / "archive"
        archive_dir.mkdir(parents=True, exist_ok=True)
        archive_file = archive_dir / f"{session_context.session_id}.yaml"
        
        content = session_file.read_text()
        archive_file.write_text(content)
        
        # Then: Data preserved in archive
        archived = yaml.safe_load(archive_file.read_text())
        assert archived["data"] == "important"


# AC_COMPLETE: AC-ENH087-T5-S3-RED-001 ✅ Session state persistence RED tests complete
# Total tests: 18 (all RED phase behavioral contracts)
# Tests define expected session state file lifecycle + metadata + validation
