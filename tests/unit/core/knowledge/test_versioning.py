"""Tests for versioning service."""
import pytest
from datetime import datetime
from src.core.knowledge.versioning import VersioningService, KnowledgeVersion

@pytest.fixture
def versioning_service():
    backends = {"backend_a": {}, "backend_b": {}}
    return VersioningService(backends)

def test_create_version(versioning_service):
    """Test version creation."""
    data = {"key": "value"}
    version_id = versioning_service.create_version("backend_a", data, "user1", "Initial")
    assert version_id is not None
    assert version_id.startswith("v_")

def test_get_version_history(versioning_service):
    """Test getting version history."""
    versioning_service.create_version("backend_a", {"v": 1})
    versioning_service.create_version("backend_a", {"v": 2})
    history = versioning_service.get_version_history("backend_a")
    assert len(history) == 2

def test_get_current_version(versioning_service):
    """Test getting current version."""
    v1 = versioning_service.create_version("backend_a", {"v": 1})
    v2 = versioning_service.create_version("backend_a", {"v": 2})
    current = versioning_service.get_current_version("backend_a")
    assert current.version_id == v2

def test_rollback_to_version(versioning_service):
    """Test rollback functionality."""
    v1 = versioning_service.create_version("backend_a", {"v": 1})
    v2 = versioning_service.create_version("backend_a", {"v": 2})
    success = versioning_service.rollback_to_version("backend_a", v1)
    assert success
    current = versioning_service.get_current_version("backend_a")
    assert current.version_id == v1

def test_rollback_invalid_version(versioning_service):
    """Test rollback with invalid version."""
    success = versioning_service.rollback_to_version("backend_a", "invalid_version")
    assert not success

def test_version_metadata(versioning_service):
    """Test version metadata."""
    data = {"info": "test"}
    v_id = versioning_service.create_version("backend_a", data, "user1", "Test version")
    history = versioning_service.get_version_history("backend_a")
    version = history[0]
    assert version.author == "user1"
    assert version.comment == "Test version"
    assert version.data == data

def test_multiple_backends(versioning_service):
    """Test versioning across multiple backends."""
    versioning_service.create_version("backend_a", {"data": "a"})
    versioning_service.create_version("backend_b", {"data": "b"})
    hist_a = versioning_service.get_version_history("backend_a")
    hist_b = versioning_service.get_version_history("backend_b")
    assert len(hist_a) == 1
    assert len(hist_b) == 1

def test_version_timestamp(versioning_service):
    """Test version timestamp."""
    before = datetime.now()
    versioning_service.create_version("backend_a", {})
    after = datetime.now()
    version = versioning_service.get_current_version("backend_a")
    assert before <= version.timestamp <= after

def test_version_sequence(versioning_service):
    """Test sequential versioning."""
    for i in range(5):
        versioning_service.create_version("backend_a", {"count": i})
    history = versioning_service.get_version_history("backend_a")
    assert len(history) == 5
    assert history[0].data["count"] == 0
    assert history[4].data["count"] == 4

def test_audit_trail(versioning_service):
    """Test version audit trail."""
    versioning_service.create_version("backend_a", {"v": 1}, "admin", "Initial setup")
    versioning_service.create_version("backend_a", {"v": 2}, "user1", "User update")
    versioning_service.create_version("backend_a", {"v": 3}, "admin", "Admin revert")
    history = versioning_service.get_version_history("backend_a")
    assert history[0].author == "admin"
    assert history[1].author == "user1"
    assert history[2].author == "admin"

def test_empty_history(versioning_service):
    """Test empty version history."""
    history = versioning_service.get_version_history("backend_a")
    assert len(history) == 0

def test_current_version_empty_backend(versioning_service):
    """Test current version on empty backend."""
    current = versioning_service.get_current_version("backend_a")
    assert current is None

def test_rollback_integration(versioning_service):
    """Test rollback integration."""
    v1 = versioning_service.create_version("backend_a", {"status": "v1"})
    v2 = versioning_service.create_version("backend_a", {"status": "v2"})
    v3 = versioning_service.create_version("backend_a", {"status": "v3"})
    versioning_service.rollback_to_version("backend_a", v2)
    current = versioning_service.get_current_version("backend_a")
    assert current.data["status"] == "v2"

def test_version_persistence(versioning_service):
    """Test version persistence."""
    v1 = versioning_service.create_version("backend_a", {"data": "original"})
    history = versioning_service.get_version_history("backend_a")
    assert len(history) == 1
    v2 = versioning_service.create_version("backend_a", {"data": "updated"})
    history = versioning_service.get_version_history("backend_a")
    assert len(history) == 2
    first_version = history[0]
    assert first_version.data["data"] == "original"
