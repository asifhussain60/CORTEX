"""
PatternStore unit tests

Covers create, duplicate handling, get (with access increment), update,
pin/unpin via update, delete, and list with filters.
"""

import sqlite3
import pytest

from src.tier2.knowledge_graph.database import ConnectionManager, DatabaseSchema
from src.tier2.knowledge_graph.patterns.pattern_store import PatternStore


@pytest.fixture
def store(tmp_path):
    """Create a PatternStore with temp database."""
    db_path = tmp_path / "kg_test.db"
    db = ConnectionManager(db_path=db_path)
    DatabaseSchema.initialize(db_path=db_path)
    return PatternStore(db)


def test_store_and_get_pattern(store: PatternStore):
    pid = "pat-001"
    stored = store.store_pattern(
        pattern_id=pid,
        title="TDD Workflow",
        content="Write tests first",
        pattern_type="workflow",
        confidence=0.95,
        scope="cortex",
        namespaces=["CORTEX-core"],
    )
    assert stored["pattern_id"] == pid
    got = store.get_pattern(pid)
    assert got is not None
    assert got["pattern_id"] == pid
    # access_count incremented by get
    assert got["access_count"] == 1


def test_duplicate_pattern_id_raises(store: PatternStore):
    pid = "dup-001"
    store.store_pattern(
        pattern_id=pid,
        title="A",
        content="B",
        pattern_type="workflow",
        confidence=1.0,
        scope="cortex",
    )
    with pytest.raises(sqlite3.IntegrityError):
        store.store_pattern(
            pattern_id=pid,
            title="C",
            content="D",
            pattern_type="workflow",
            confidence=0.9,
            scope="cortex",
        )


def test_update_pattern_confidence(store: PatternStore):
    pid = "pat-002"
    store.store_pattern(
        pattern_id=pid,
        title="Rule",
        content="Always do X",
        pattern_type="principle",
        confidence=0.7,
        scope="cortex",
    )
    updated = store.update_pattern(pid, {"confidence": 0.8})
    assert updated is True
    got = store.get_pattern(pid)
    assert pytest.approx(got["confidence"], rel=1e-6) == 0.8


def test_list_patterns_with_filters(store: PatternStore):
    # insert three patterns
    store.store_pattern("p1", "A", "a", "workflow", 0.9, scope="cortex")
    store.store_pattern("p2", "B", "b", "solution", 0.6, scope="cortex")
    store.store_pattern("p3", "C", "c", "workflow", 0.4, scope="application")
    results = store.list_patterns(pattern_type="workflow", scope="cortex", min_confidence=0.5)
    ids = [r["pattern_id"] for r in results]
    assert "p1" in ids
    assert "p3" not in ids  # wrong scope
    assert "p2" not in ids  # wrong type


def test_delete_pattern(store: PatternStore):
    pid = "pat-del"
    store.store_pattern(pid, "A", "a", "workflow", 1.0, scope="cortex")
    deleted = store.delete_pattern(pid)
    assert deleted is True
    assert store.get_pattern(pid) is None
"""
Tests for Pattern Store Module

Tests pattern CRUD operations following TDD methodology.
"""

import pytest
import tempfile
from pathlib import Path
import json

from src.tier2.knowledge_graph.database.connection import ConnectionManager
from src.tier2.knowledge_graph.database.schema import DatabaseSchema
from src.tier2.knowledge_graph.patterns.pattern_store import PatternStore


@pytest.fixture
def temp_db():
    """Create temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = Path(f.name)
    
    # Initialize database with schema
    DatabaseSchema.initialize(db_path)
    db = ConnectionManager(db_path)
    
    yield db
    
    # Cleanup
    db.close()
    db_path.unlink(missing_ok=True)


@pytest.fixture
def pattern_store(temp_db):
    """Create PatternStore instance."""
    return PatternStore(temp_db)


class TestPatternStoreInitialization:
    """Test PatternStore initialization."""
    
    def test_pattern_store_requires_db(self, temp_db):
        """PatternStore requires database connection."""
        store = PatternStore(temp_db)
        assert store.db is not None
    
    def test_pattern_store_has_db_reference(self, pattern_store):
        """PatternStore maintains reference to database."""
        assert pattern_store.db is not None


class TestPatternStorage:
    """Test pattern creation and storage."""
    
    def test_store_pattern_with_minimal_data(self, pattern_store):
        """Can store pattern with minimal required fields."""
        pattern = pattern_store.store_pattern(
            pattern_id="test-pattern-1",
            title="Test Pattern",
            content="Test content",
            pattern_type="workflow"
        )
        
        assert pattern["pattern_id"] == "test-pattern-1"
        assert pattern["title"] == "Test Pattern"
        assert pattern["content"] == "Test content"
        assert pattern["pattern_type"] == "workflow"
        assert pattern["confidence"] == 1.0  # Default
        assert pattern["scope"] == "cortex"  # Default
        assert pattern["namespaces"] == ["CORTEX-core"]  # Default
    
    def test_store_pattern_with_all_fields(self, pattern_store):
        """Can store pattern with all optional fields."""
        metadata = {"author": "test", "version": "1.0"}
        
        pattern = pattern_store.store_pattern(
            pattern_id="test-pattern-2",
            title="Full Pattern",
            content="Complete pattern",
            pattern_type="principle",
            confidence=0.95,
            source="test-source",
            metadata=metadata,
            is_pinned=True,
            scope="application",
            namespaces=["KSESSIONS", "NOOR"]
        )
        
        assert pattern["confidence"] == 0.95
        assert pattern["source"] == "test-source"
        assert pattern["metadata"] == metadata
        assert pattern["is_pinned"] is True
        assert pattern["scope"] == "application"
        assert pattern["namespaces"] == ["KSESSIONS", "NOOR"]
    
    def test_store_pattern_validates_confidence_range(self, pattern_store):
        """Validates confidence is between 0.0 and 1.0."""
        with pytest.raises(ValueError, match="Confidence must be between"):
            pattern_store.store_pattern(
                pattern_id="bad-confidence",
                title="Bad",
                content="Bad",
                pattern_type="workflow",
                confidence=1.5  # Invalid
            )
    
    def test_store_pattern_validates_scope(self, pattern_store):
        """Validates scope is 'generic' or 'application'."""
        with pytest.raises(ValueError, match="Scope must be"):
            pattern_store.store_pattern(
                pattern_id="bad-scope",
                title="Bad",
                content="Bad",
                pattern_type="workflow",
                scope="invalid"  # Invalid
            )
    
    def test_store_pattern_sets_timestamps(self, pattern_store):
        """Pattern gets created_at and last_accessed timestamps."""
        pattern = pattern_store.store_pattern(
            pattern_id="test-timestamps",
            title="Timestamps",
            content="Test",
            pattern_type="workflow"
        )
        
        assert "created_at" in pattern
        assert "last_accessed" in pattern
        assert pattern["created_at"] == pattern["last_accessed"]  # Same on creation
    
    def test_store_pattern_initializes_access_count(self, pattern_store):
        """Pattern starts with access_count of 0."""
        pattern = pattern_store.store_pattern(
            pattern_id="test-access-count",
            title="Access Count",
            content="Test",
            pattern_type="workflow"
        )
        
        assert pattern["access_count"] == 0


class TestPatternRetrieval:
    """Test pattern retrieval operations."""
    
    def test_get_pattern_returns_stored_pattern(self, pattern_store):
        """Can retrieve pattern after storage."""
        # Store pattern
        pattern_store.store_pattern(
            pattern_id="retrieve-test",
            title="Retrieve Test",
            content="Content",
            pattern_type="workflow"
        )
        
        # Retrieve pattern
        retrieved = pattern_store.get_pattern("retrieve-test")
        
        assert retrieved is not None
        assert retrieved["pattern_id"] == "retrieve-test"
        assert retrieved["title"] == "Retrieve Test"
    
    def test_get_pattern_returns_none_if_not_found(self, pattern_store):
        """Returns None for non-existent pattern."""
        result = pattern_store.get_pattern("does-not-exist")
        assert result is None
    
    def test_get_pattern_updates_access_timestamp(self, pattern_store):
        """Accessing pattern updates last_accessed timestamp."""
        # Store pattern
        stored = pattern_store.store_pattern(
            pattern_id="timestamp-test",
            title="Timestamp Test",
            content="Content",
            pattern_type="workflow"
        )
        
        original_timestamp = stored["last_accessed"]
        
        # Small delay to ensure timestamp changes
        import time
        time.sleep(0.01)
        
        # Retrieve pattern
        retrieved = pattern_store.get_pattern("timestamp-test")
        
        assert retrieved["last_accessed"] > original_timestamp
    
    def test_get_pattern_increments_access_count(self, pattern_store):
        """Accessing pattern increments access_count."""
        # Store pattern
        pattern_store.store_pattern(
            pattern_id="access-count-test",
            title="Access Count Test",
            content="Content",
            pattern_type="workflow"
        )
        
        # Access multiple times
        first = pattern_store.get_pattern("access-count-test")
        assert first["access_count"] == 1
        
        second = pattern_store.get_pattern("access-count-test")
        assert second["access_count"] == 2
        
        third = pattern_store.get_pattern("access-count-test")
        assert third["access_count"] == 3


class TestPatternUpdates:
    """Test pattern update operations."""
    
    def test_update_pattern_changes_title(self, pattern_store):
        """Can update pattern title."""
        # Store pattern
        pattern_store.store_pattern(
            pattern_id="update-title",
            title="Old Title",
            content="Content",
            pattern_type="workflow"
        )
        
        # Update title
        updated = pattern_store.update_pattern(
            "update-title",
            {"title": "New Title"}
        )
        
        assert updated is True
        
        # Verify update
        pattern = pattern_store.get_pattern("update-title")
        assert pattern["title"] == "New Title"
    
    def test_update_pattern_changes_confidence(self, pattern_store):
        """Can update pattern confidence."""
        pattern_store.store_pattern(
            pattern_id="update-confidence",
            title="Confidence Test",
            content="Content",
            pattern_type="workflow",
            confidence=1.0
        )
        
        updated = pattern_store.update_pattern(
            "update-confidence",
            {"confidence": 0.75}
        )
        
        assert updated is True
        
        pattern = pattern_store.get_pattern("update-confidence")
        assert pattern["confidence"] == 0.75
    
    def test_update_pattern_changes_metadata(self, pattern_store):
        """Can update pattern metadata."""
        pattern_store.store_pattern(
            pattern_id="update-metadata",
            title="Metadata Test",
            content="Content",
            pattern_type="workflow",
            metadata={"version": "1.0"}
        )
        
        new_metadata = {"version": "2.0", "updated": True}
        updated = pattern_store.update_pattern(
            "update-metadata",
            {"metadata": new_metadata}
        )
        
        assert updated is True
        
        pattern = pattern_store.get_pattern("update-metadata")
        assert pattern["metadata"] == new_metadata
    
    def test_update_pattern_protects_pattern_id(self, pattern_store):
        """Cannot update pattern_id (protected field)."""
        pattern_store.store_pattern(
            pattern_id="protected-test",
            title="Protected",
            content="Content",
            pattern_type="workflow"
        )
        
        # Try to update pattern_id (should be ignored)
        pattern_store.update_pattern(
            "protected-test",
            {"pattern_id": "new-id"}
        )
        
        # Verify pattern_id unchanged
        pattern = pattern_store.get_pattern("protected-test")
        assert pattern["pattern_id"] == "protected-test"
    
    def test_update_pattern_returns_false_if_not_found(self, pattern_store):
        """Returns False when updating non-existent pattern."""
        updated = pattern_store.update_pattern(
            "does-not-exist",
            {"title": "New Title"}
        )
        
        assert updated is False
    
    def test_update_pattern_returns_false_if_no_updates(self, pattern_store):
        """Returns False when no valid updates provided."""
        pattern_store.store_pattern(
            pattern_id="no-updates",
            title="Test",
            content="Content",
            pattern_type="workflow"
        )
        
        updated = pattern_store.update_pattern("no-updates", {})
        assert updated is False


class TestPatternDeletion:
    """Test pattern deletion operations."""
    
    def test_delete_pattern_removes_pattern(self, pattern_store):
        """Can delete pattern."""
        # Store pattern
        pattern_store.store_pattern(
            pattern_id="delete-test",
            title="Delete Test",
            content="Content",
            pattern_type="workflow"
        )
        
        # Delete pattern
        deleted = pattern_store.delete_pattern("delete-test")
        assert deleted is True
        
        # Verify deletion
        pattern = pattern_store.get_pattern("delete-test")
        assert pattern is None
    
    def test_delete_pattern_returns_false_if_not_found(self, pattern_store):
        """Returns False when deleting non-existent pattern."""
        deleted = pattern_store.delete_pattern("does-not-exist")
        assert deleted is False


class TestPatternListing:
    """Test pattern listing and filtering operations."""
    
    def test_list_patterns_returns_all_patterns(self, pattern_store):
        """Can list all patterns."""
        # Store multiple patterns
        pattern_store.store_pattern("p1", "P1", "Content", "workflow")
        pattern_store.store_pattern("p2", "P2", "Content", "principle")
        pattern_store.store_pattern("p3", "P3", "Content", "solution")
        
        patterns = pattern_store.list_patterns()
        
        assert len(patterns) == 3
        pattern_ids = [p["pattern_id"] for p in patterns]
        assert "p1" in pattern_ids
        assert "p2" in pattern_ids
        assert "p3" in pattern_ids
    
    def test_list_patterns_filters_by_type(self, pattern_store):
        """Can filter patterns by type."""
        pattern_store.store_pattern("w1", "W1", "Content", "workflow")
        pattern_store.store_pattern("w2", "W2", "Content", "workflow")
        pattern_store.store_pattern("p1", "P1", "Content", "principle")
        
        workflows = pattern_store.list_patterns(pattern_type="workflow")
        
        assert len(workflows) == 2
        assert all(p["pattern_type"] == "workflow" for p in workflows)
    
    def test_list_patterns_filters_by_scope(self, pattern_store):
        """Can filter patterns by scope."""
        pattern_store.store_pattern("g1", "G1", "Content", "workflow", scope="cortex")
        pattern_store.store_pattern("a1", "A1", "Content", "workflow", scope="application")
        
        cortex_patterns = pattern_store.list_patterns(scope="cortex")
        
        assert len(cortex_patterns) == 1
        assert cortex_patterns[0]["scope"] == "cortex"
    
    def test_list_patterns_filters_by_confidence(self, pattern_store):
        """Can filter patterns by minimum confidence."""
        pattern_store.store_pattern("high", "High", "Content", "workflow", confidence=0.9)
        pattern_store.store_pattern("low", "Low", "Content", "workflow", confidence=0.5)
        
        high_conf = pattern_store.list_patterns(min_confidence=0.8)
        
        assert len(high_conf) == 1
        assert high_conf[0]["pattern_id"] == "high"
    
    def test_list_patterns_respects_limit(self, pattern_store):
        """Can limit number of results."""
        # Store 5 patterns
        for i in range(5):
            pattern_store.store_pattern(f"p{i}", f"P{i}", "Content", "workflow")
        
        limited = pattern_store.list_patterns(limit=3)
        
        assert len(limited) == 3
    
    def test_list_patterns_orders_by_confidence_and_access(self, pattern_store):
        """Patterns ordered by confidence DESC, then last_accessed DESC."""
        import time
        
        # Store patterns with different confidence
        pattern_store.store_pattern("low", "Low", "Content", "workflow", confidence=0.5)
        time.sleep(0.01)
        pattern_store.store_pattern("high", "High", "Content", "workflow", confidence=0.9)
        
        patterns = pattern_store.list_patterns()
        
        # High confidence should be first
        assert patterns[0]["pattern_id"] == "high"
        assert patterns[1]["pattern_id"] == "low"


class TestPatternPerformance:
    """Test pattern operation performance."""
    
    def test_pattern_storage_is_fast(self, pattern_store):
        """Pattern storage completes in <20ms."""
        import time
        
        start = time.perf_counter()
        pattern_store.store_pattern(
            "perf-store",
            "Performance Test",
            "Content",
            "workflow"
        )
        duration_ms = (time.perf_counter() - start) * 1000
        
        assert duration_ms < 20
    
    def test_pattern_retrieval_is_fast(self, pattern_store):
        """Pattern retrieval completes in <10ms."""
        import time
        
        # Store pattern first
        pattern_store.store_pattern(
            "perf-retrieve",
            "Performance Test",
            "Content",
            "workflow"
        )
        
        start = time.perf_counter()
        pattern_store.get_pattern("perf-retrieve")
        duration_ms = (time.perf_counter() - start) * 1000
        
        assert duration_ms < 10
