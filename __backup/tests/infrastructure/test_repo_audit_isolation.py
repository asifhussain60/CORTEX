"""
Tests for AC-AUDIT-006: Per-Repo Isolation

Validates repository isolation, metadata management, and cross-repo prevention.
"""

import pytest
import sqlite3
import tempfile
import hashlib
from pathlib import Path
from datetime import datetime

from src.infrastructure.repo_audit_isolation import (
    RepositoryIdentity,
    RepositoryAuditIsolation,
)


@pytest.fixture
def temp_audit_dir():
    """Create temporary audit directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def isolation_system(temp_audit_dir):
    """Create isolation system with temp directory."""
    return RepositoryAuditIsolation(audit_base_path=temp_audit_dir)


@pytest.fixture
def repo_identity_alpha():
    """Create identity for first repository."""
    return RepositoryIdentity(
        repo_id="repo_alpha_001",
        repo_name="alpha-repo",
        repo_path="/home/user/projects/alpha"
    )


@pytest.fixture
def repo_identity_beta():
    """Create identity for second repository."""
    return RepositoryIdentity(
        repo_id="repo_beta_001",
        repo_name="beta-repo",
        repo_path="/home/user/projects/beta"
    )


class TestRepositoryIdentity:
    """Tests for RepositoryIdentity dataclass."""
    
    def test_valid_identity(self, repo_identity_alpha):
        """Test creating valid repository identity."""
        repo_identity_alpha.validate()  # Should not raise
        assert repo_identity_alpha.repo_id == "repo_alpha_001"
        assert repo_identity_alpha.repo_name == "alpha-repo"
    
    def test_invalid_repo_id(self):
        """Test rejection of invalid repo_id."""
        with pytest.raises(ValueError, match="repo_id"):
            RepositoryIdentity(
                repo_id="",
                repo_name="test",
                repo_path="/path"
            ).validate()
    
    def test_invalid_repo_name(self):
        """Test rejection of invalid repo_name."""
        with pytest.raises(ValueError, match="repo_name"):
            RepositoryIdentity(
                repo_id="repo_001",
                repo_name="",
                repo_path="/path"
            ).validate()
    
    def test_invalid_repo_path(self):
        """Test rejection of invalid repo_path."""
        with pytest.raises(ValueError, match="repo_path"):
            RepositoryIdentity(
                repo_id="repo_001",
                repo_name="test",
                repo_path=""
            ).validate()


class TestRepoIDGeneration:
    """Tests for repository ID generation."""
    
    def test_generate_repo_id_from_path(self):
        """Test generating repo ID from filesystem path."""
        repo_path = "/home/user/projects/myrepo"
        repo_id = RepositoryAuditIsolation.generate_repo_id(repo_path)
        
        assert len(repo_id) == 16
        assert isinstance(repo_id, str)
        
        # Same path should generate same ID
        repo_id2 = RepositoryAuditIsolation.generate_repo_id(repo_path)
        assert repo_id == repo_id2
        
        # Different paths should generate different IDs
        repo_id3 = RepositoryAuditIsolation.generate_repo_id("/home/user/projects/other")
        assert repo_id != repo_id3
    
    def test_generate_repo_id_from_url(self):
        """Test generating repo ID from URL."""
        repo_url = "https://github.com/user/myrepo"
        repo_id = RepositoryAuditIsolation.generate_repo_id_from_url(repo_url)
        
        assert len(repo_id) == 16
        assert isinstance(repo_id, str)
        
        # Same URL should generate same ID
        repo_id2 = RepositoryAuditIsolation.generate_repo_id_from_url(repo_url)
        assert repo_id == repo_id2
        
        # Different URLs should generate different IDs
        repo_id3 = RepositoryAuditIsolation.generate_repo_id_from_url("https://github.com/user/other")
        assert repo_id != repo_id3


class TestRepositoryIsolation:
    """Tests for database isolation."""
    
    def test_get_repo_db_path(self, isolation_system, repo_identity_alpha):
        """Test getting isolated database path for repo."""
        db_path = isolation_system.get_repo_db_path(repo_identity_alpha)
        
        assert db_path.endswith("audit_repo_alpha_001.db")
        assert "audit_repo_alpha_001.db" in db_path
    
    def test_initialize_repo_db(self, isolation_system, repo_identity_alpha):
        """Test initializing isolated database."""
        db_path = isolation_system.initialize_repo_db(repo_identity_alpha)
        
        assert Path(db_path).exists()
        
        # Verify schema exists
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='audit_events'"
        )
        assert cursor.fetchone() is not None
        
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='repo_metadata'"
        )
        assert cursor.fetchone() is not None
        
        conn.close()
    
    def test_multiple_repo_isolation(self, isolation_system, repo_identity_alpha, repo_identity_beta):
        """Test that multiple repos have separate databases."""
        db_alpha = isolation_system.initialize_repo_db(repo_identity_alpha)
        db_beta = isolation_system.initialize_repo_db(repo_identity_beta)
        
        assert db_alpha != db_beta
        assert Path(db_alpha).exists()
        assert Path(db_beta).exists()
    
    def test_get_repo_metadata(self, isolation_system, repo_identity_alpha):
        """Test retrieving repository metadata."""
        db_path = isolation_system.initialize_repo_db(repo_identity_alpha)
        
        metadata = isolation_system.get_repo_metadata(db_path)
        
        assert metadata is not None
        assert metadata["repo_id"] == "repo_alpha_001"
        assert metadata["repo_name"] == "alpha-repo"
        assert metadata["repo_path"] == "/home/user/projects/alpha"
        assert metadata["db_version"] == "1.0"
    
    def test_list_isolated_databases(self, isolation_system, repo_identity_alpha, repo_identity_beta):
        """Test listing all isolated databases."""
        isolation_system.initialize_repo_db(repo_identity_alpha)
        isolation_system.initialize_repo_db(repo_identity_beta)
        
        databases = isolation_system.list_isolated_databases()
        
        assert len(databases) == 2
        
        db_names = [db["db_file"] for db in databases]
        assert "audit_repo_alpha_001.db" in db_names
        assert "audit_repo_beta_001.db" in db_names


class TestEventLogging:
    """Tests for logging events to isolated repositories."""
    
    def test_log_event_to_repo(self, isolation_system, repo_identity_alpha):
        """Test logging event to repository database."""
        db_path = isolation_system.initialize_repo_db(repo_identity_alpha)
        
        success = isolation_system.log_event_to_repo(
            repo_identity_alpha,
            timestamp=datetime.utcnow().isoformat(),
            level="INFO",
            category="TEST",
            message="Test event",
            actor="test_user",
            ac_id="AC-TEST-001"
        )
        
        assert success is True
        
        # Verify event was logged
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) as count FROM audit_events")
        count = cursor.fetchone()["count"]
        
        conn.close()
        
        assert count == 1
    
    def test_log_multiple_events(self, isolation_system, repo_identity_alpha):
        """Test logging multiple events."""
        isolation_system.initialize_repo_db(repo_identity_alpha)
        
        for i in range(5):
            isolation_system.log_event_to_repo(
                repo_identity_alpha,
                timestamp=datetime.utcnow().isoformat(),
                level="INFO",
                category="TEST",
                message=f"Event {i}",
                ac_id=f"AC-TEST-{i:03d}"
            )
        
        db_path = isolation_system.get_repo_db_path(repo_identity_alpha)
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) as count FROM audit_events")
        count = cursor.fetchone()["count"]
        
        conn.close()
        
        assert count == 5
    
    def test_event_repo_id_isolation(self, isolation_system, repo_identity_alpha, repo_identity_beta):
        """Test that events are tagged with correct repo_id."""
        isolation_system.initialize_repo_db(repo_identity_alpha)
        isolation_system.initialize_repo_db(repo_identity_beta)
        
        isolation_system.log_event_to_repo(
            repo_identity_alpha,
            timestamp=datetime.utcnow().isoformat(),
            level="INFO",
            category="TEST",
            message="Alpha event"
        )
        
        isolation_system.log_event_to_repo(
            repo_identity_beta,
            timestamp=datetime.utcnow().isoformat(),
            level="INFO",
            category="TEST",
            message="Beta event"
        )
        
        # Verify alpha database only has alpha events
        alpha_db = isolation_system.get_repo_db_path(repo_identity_alpha)
        conn = sqlite3.connect(alpha_db)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT repo_id, message FROM audit_events")
        for row in cursor.fetchall():
            assert row["repo_id"] == "repo_alpha_001"
            assert row["message"] == "Alpha event"
        
        conn.close()


class TestIsolationVerification:
    """Tests for verifying isolation integrity."""
    
    def test_verify_isolation_valid(self, isolation_system, repo_identity_alpha):
        """Test verification of valid isolated database."""
        db_path = isolation_system.initialize_repo_db(repo_identity_alpha)
        
        result = isolation_system.verify_isolation(db_path)
        
        assert result["isolated"] is True
        assert "All events properly isolated" in result["details"]
    
    def test_verify_isolation_nonexistent_db(self, temp_audit_dir):
        """Test verification of non-existent database."""
        isolation_system = RepositoryAuditIsolation(audit_base_path=temp_audit_dir)
        nonexistent_db = str(Path(temp_audit_dir) / "nonexistent.db")
        
        result = isolation_system.verify_isolation(nonexistent_db)
        
        assert result["isolated"] is True  # Doesn't exist yet, so okay


class TestQueryingRepoEvents:
    """Tests for querying events from isolated repositories."""
    
    def test_query_repo_events_empty(self, isolation_system, repo_identity_alpha):
        """Test querying events from empty database."""
        isolation_system.initialize_repo_db(repo_identity_alpha)
        db_path = isolation_system.get_repo_db_path(repo_identity_alpha)
        
        events = isolation_system.query_repo_events(db_path)
        
        assert events == []
    
    def test_query_repo_events_all(self, isolation_system, repo_identity_alpha):
        """Test querying all events."""
        isolation_system.initialize_repo_db(repo_identity_alpha)
        
        # Log some events
        for i in range(3):
            isolation_system.log_event_to_repo(
                repo_identity_alpha,
                timestamp=datetime.utcnow().isoformat(),
                level="INFO",
                category="TEST",
                message=f"Event {i}"
            )
        
        db_path = isolation_system.get_repo_db_path(repo_identity_alpha)
        events = isolation_system.query_repo_events(db_path)
        
        assert len(events) == 3
    
    def test_query_repo_events_by_level(self, isolation_system, repo_identity_alpha):
        """Test querying events filtered by level."""
        isolation_system.initialize_repo_db(repo_identity_alpha)
        
        isolation_system.log_event_to_repo(
            repo_identity_alpha,
            timestamp=datetime.utcnow().isoformat(),
            level="ERROR",
            category="TEST",
            message="Error"
        )
        
        isolation_system.log_event_to_repo(
            repo_identity_alpha,
            timestamp=datetime.utcnow().isoformat(),
            level="INFO",
            category="TEST",
            message="Info"
        )
        
        db_path = isolation_system.get_repo_db_path(repo_identity_alpha)
        error_events = isolation_system.query_repo_events(db_path, level="ERROR")
        
        assert len(error_events) == 1
        assert error_events[0]["level"] == "ERROR"
    
    def test_query_repo_events_by_ac_id(self, isolation_system, repo_identity_alpha):
        """Test querying events filtered by AC-ID."""
        isolation_system.initialize_repo_db(repo_identity_alpha)
        
        isolation_system.log_event_to_repo(
            repo_identity_alpha,
            timestamp=datetime.utcnow().isoformat(),
            level="INFO",
            category="TEST",
            message="Event 1",
            ac_id="AC-AUDIT-001"
        )
        
        isolation_system.log_event_to_repo(
            repo_identity_alpha,
            timestamp=datetime.utcnow().isoformat(),
            level="INFO",
            category="TEST",
            message="Event 2",
            ac_id="AC-AUDIT-002"
        )
        
        db_path = isolation_system.get_repo_db_path(repo_identity_alpha)
        audit_001_events = isolation_system.query_repo_events(db_path, ac_id="AC-AUDIT-001")
        
        assert len(audit_001_events) == 1
        assert audit_001_events[0]["ac_id"] == "AC-AUDIT-001"
