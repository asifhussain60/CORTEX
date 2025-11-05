"""
CORTEX Tier 2: Knowledge Graph Tests
Unit tests for long-term memory with FTS5 search.
"""

import pytest
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
import tempfile
import shutil
from CORTEX.src.tier2.knowledge_graph import (
    KnowledgeGraph,
    Pattern,
    PatternType,
    RelationshipType
)


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    temp_dir = tempfile.mkdtemp()
    db_path = Path(temp_dir) / "test_knowledge_graph.db"
    yield db_path
    # Cleanup
    shutil.rmtree(temp_dir)


@pytest.fixture
def knowledge_graph(temp_db):
    """Create a KnowledgeGraph instance for testing."""
    kg = KnowledgeGraph(db_path=temp_db)
    yield kg
    # Ensure all connections are closed before cleanup
    kg.close()


class TestDatabaseInitialization:
    """Test database creation and schema setup."""
    
    def test_creates_database_file(self, temp_db):
        """Test that database file is created."""
        kg = KnowledgeGraph(db_path=temp_db)
        assert temp_db.exists()
        kg.close()
    
    def test_creates_all_tables(self, knowledge_graph):
        """Test that all required tables are created."""
        conn = sqlite3.connect(knowledge_graph.db_path)
        cursor = conn.cursor()
        
        # Get all table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = {row[0] for row in cursor.fetchall()}
        
        expected_tables = {
            'patterns',
            'pattern_relationships',
            'pattern_tags',
            'pattern_fts'  # FTS5 virtual table
        }
        
        assert expected_tables.issubset(tables)
        conn.close()
    
    def test_creates_fts5_virtual_table(self, knowledge_graph):
        """Test that FTS5 virtual table is created correctly."""
        conn = sqlite3.connect(knowledge_graph.db_path)
        cursor = conn.cursor()
        
        # Check FTS5 table exists and is virtual
        cursor.execute("""
            SELECT type, name FROM sqlite_master 
            WHERE name='pattern_fts'
        """)
        result = cursor.fetchone()
        
        assert result is not None
        assert result[0] == 'table'  # Virtual tables show as 'table'
        conn.close()


class TestPatternManagement:
    """Test pattern CRUD operations."""
    
    def test_adds_pattern(self, knowledge_graph):
        """Test adding a new pattern."""
        pattern = knowledge_graph.add_pattern(
            pattern_id="test_pattern_001",
            title="Test Pattern",
            content="This is a test pattern for unit testing",
            pattern_type=PatternType.WORKFLOW,
            confidence=1.0,
            tags=["testing", "unit-test"],
            source="test"
        )
        
        assert pattern is not None
        assert pattern.pattern_id == "test_pattern_001"
        assert pattern.title == "Test Pattern"
        assert pattern.pattern_type == PatternType.WORKFLOW
        assert pattern.confidence == 1.0
    
    def test_gets_pattern_by_id(self, knowledge_graph):
        """Test retrieving pattern by ID."""
        # Add pattern
        knowledge_graph.add_pattern(
            pattern_id="test_pattern_002",
            title="Another Pattern",
            content="Content here",
            pattern_type=PatternType.PRINCIPLE
        )
        
        # Retrieve it
        pattern = knowledge_graph.get_pattern("test_pattern_002")
        
        assert pattern is not None
        assert pattern.pattern_id == "test_pattern_002"
        assert pattern.pattern_type == PatternType.PRINCIPLE
    
    def test_updates_pattern(self, knowledge_graph):
        """Test updating pattern properties."""
        knowledge_graph.add_pattern(
            pattern_id="update_pattern",
            title="Original Title",
            content="Original content",
            pattern_type=PatternType.SOLUTION
        )
        
        knowledge_graph.update_pattern(
            pattern_id="update_pattern",
            title="Updated Title",
            content="Updated content",
            confidence=0.8
        )
        
        pattern = knowledge_graph.get_pattern("update_pattern")
        assert pattern.title == "Updated Title"
        assert pattern.content == "Updated content"
        assert pattern.confidence == 0.8
    
    def test_deletes_pattern(self, knowledge_graph):
        """Test deleting a pattern."""
        knowledge_graph.add_pattern(
            pattern_id="delete_me",
            title="To Delete",
            content="This will be deleted",
            pattern_type=PatternType.ANTI_PATTERN
        )
        
        knowledge_graph.delete_pattern("delete_me")
        
        pattern = knowledge_graph.get_pattern("delete_me")
        assert pattern is None
    
    def test_lists_patterns_by_type(self, knowledge_graph):
        """Test retrieving patterns filtered by type."""
        # Add patterns of different types
        knowledge_graph.add_pattern(
            pattern_id="workflow_1",
            title="Workflow 1",
            content="Content",
            pattern_type=PatternType.WORKFLOW
        )
        
        knowledge_graph.add_pattern(
            pattern_id="workflow_2",
            title="Workflow 2",
            content="Content",
            pattern_type=PatternType.WORKFLOW
        )
        
        knowledge_graph.add_pattern(
            pattern_id="principle_1",
            title="Principle 1",
            content="Content",
            pattern_type=PatternType.PRINCIPLE
        )
        
        # Get workflows
        workflows = knowledge_graph.get_patterns_by_type(PatternType.WORKFLOW)
        
        assert len(workflows) == 2
        assert all(p.pattern_type == PatternType.WORKFLOW for p in workflows)
    
    def test_updates_access_timestamp(self, knowledge_graph):
        """Test that accessing a pattern updates timestamp and count."""
        knowledge_graph.add_pattern(
            pattern_id="access_test",
            title="Access Test",
            content="Content",
            pattern_type=PatternType.CONTEXT
        )
        
        # Get pattern (should update access)
        pattern1 = knowledge_graph.get_pattern("access_test")
        initial_count = pattern1.access_count
        
        # Access again
        pattern2 = knowledge_graph.get_pattern("access_test")
        
        assert pattern2.access_count == initial_count + 1


class TestFTS5Search:
    """Test FTS5 full-text search operations."""
    
    def test_simple_keyword_search(self, knowledge_graph):
        """Test basic keyword search using FTS5."""
        # Add patterns
        knowledge_graph.add_pattern(
            pattern_id="search_1",
            title="TDD Development",
            content="Test-Driven Development is a workflow where tests are written first",
            pattern_type=PatternType.WORKFLOW
        )
        
        knowledge_graph.add_pattern(
            pattern_id="search_2",
            title="Database Setup",
            content="Configure SQLite database with proper indexes",
            pattern_type=PatternType.SOLUTION
        )
        
        # Search for "test"
        results = knowledge_graph.search_patterns("test")
        
        assert len(results) >= 1
        assert any(r.pattern_id == "search_1" for r in results)
    
    def test_phrase_search(self, knowledge_graph):
        """Test phrase search (exact match)."""
        knowledge_graph.add_pattern(
            pattern_id="phrase_1",
            title="Pattern",
            content="Test-Driven Development is a methodology",
            pattern_type=PatternType.WORKFLOW
        )
        
        knowledge_graph.add_pattern(
            pattern_id="phrase_2",
            title="Pattern",
            content="Development test driven approach",
            pattern_type=PatternType.WORKFLOW
        )
        
        # Phrase search should find exact phrase
        results = knowledge_graph.search_patterns('"Test-Driven Development"')
        
        assert len(results) >= 1
        assert results[0].pattern_id == "phrase_1"
    
    def test_boolean_search(self, knowledge_graph):
        """Test boolean search (AND, OR, NOT)."""
        knowledge_graph.add_pattern(
            pattern_id="bool_1",
            title="TDD Pattern",
            content="Testing and refactoring workflow",
            pattern_type=PatternType.WORKFLOW
        )
        
        knowledge_graph.add_pattern(
            pattern_id="bool_2",
            title="Manual Testing",
            content="Manual testing without automation",
            pattern_type=PatternType.ANTI_PATTERN
        )
        
        # AND search
        results = knowledge_graph.search_patterns("testing AND refactoring")
        assert len(results) >= 1
        assert results[0].pattern_id == "bool_1"
        
        # NOT search
        results = knowledge_graph.search_patterns("testing NOT manual")
        assert all(r.pattern_id != "bool_2" for r in results)
    
    def test_prefix_search(self, knowledge_graph):
        """Test prefix matching."""
        knowledge_graph.add_pattern(
            pattern_id="prefix_1",
            title="Refactoring Pattern",
            content="Refactor code to improve quality",
            pattern_type=PatternType.WORKFLOW
        )
        
        # Prefix search
        results = knowledge_graph.search_patterns("refactor*")
        
        assert len(results) >= 1
        assert results[0].pattern_id == "prefix_1"
    
    def test_search_ranking_by_relevance(self, knowledge_graph):
        """Test that results are ranked by relevance."""
        knowledge_graph.add_pattern(
            pattern_id="rank_1",
            title="Testing Testing Testing",
            content="Testing is mentioned three times: testing, testing, testing",
            pattern_type=PatternType.WORKFLOW
        )
        
        knowledge_graph.add_pattern(
            pattern_id="rank_2",
            title="Other Topic",
            content="This mentions testing once",
            pattern_type=PatternType.WORKFLOW
        )
        
        results = knowledge_graph.search_patterns("testing")
        
        # rank_1 should come first (more occurrences)
        assert len(results) >= 2
        assert results[0].pattern_id == "rank_1"


class TestPatternRelationships:
    """Test pattern relationship and graph operations."""
    
    def test_links_two_patterns(self, knowledge_graph):
        """Test creating a relationship between patterns."""
        # Add patterns
        knowledge_graph.add_pattern(
            pattern_id="rel_1",
            title="TDD",
            content="Test-Driven Development",
            pattern_type=PatternType.WORKFLOW
        )
        
        knowledge_graph.add_pattern(
            pattern_id="rel_2",
            title="Refactoring",
            content="Code improvement",
            pattern_type=PatternType.WORKFLOW
        )
        
        # Link them
        knowledge_graph.link_patterns(
            from_pattern="rel_1",
            to_pattern="rel_2",
            relationship_type=RelationshipType.EXTENDS,
            strength=0.9
        )
        
        # Verify relationship exists
        related = knowledge_graph.get_related_patterns("rel_1")
        assert len(related) >= 1
        assert any(p.pattern_id == "rel_2" for p in related)
    
    def test_gets_related_patterns(self, knowledge_graph):
        """Test retrieving patterns related to a given pattern."""
        # Create pattern graph
        knowledge_graph.add_pattern("graph_1", "P1", "Content", PatternType.WORKFLOW)
        knowledge_graph.add_pattern("graph_2", "P2", "Content", PatternType.WORKFLOW)
        knowledge_graph.add_pattern("graph_3", "P3", "Content", PatternType.WORKFLOW)
        
        knowledge_graph.link_patterns("graph_1", "graph_2", RelationshipType.RELATED_TO)
        knowledge_graph.link_patterns("graph_1", "graph_3", RelationshipType.RELATED_TO)
        
        # Get related patterns
        related = knowledge_graph.get_related_patterns("graph_1")
        
        assert len(related) == 2
        pattern_ids = {p.pattern_id for p in related}
        assert pattern_ids == {"graph_2", "graph_3"}
    
    def test_traverses_graph_multi_level(self, knowledge_graph):
        """Test graph traversal with max depth."""
        # Create multi-level graph: A -> B -> C
        knowledge_graph.add_pattern("traverse_a", "A", "Content", PatternType.WORKFLOW)
        knowledge_graph.add_pattern("traverse_b", "B", "Content", PatternType.WORKFLOW)
        knowledge_graph.add_pattern("traverse_c", "C", "Content", PatternType.WORKFLOW)
        
        knowledge_graph.link_patterns("traverse_a", "traverse_b", RelationshipType.EXTENDS)
        knowledge_graph.link_patterns("traverse_b", "traverse_c", RelationshipType.EXTENDS)
        
        # Traverse with depth 1 (should get only B)
        related_1 = knowledge_graph.get_related_patterns("traverse_a", max_depth=1)
        assert len(related_1) == 1
        assert related_1[0].pattern_id == "traverse_b"
        
        # Traverse with depth 2 (should get B and C)
        related_2 = knowledge_graph.get_related_patterns("traverse_a", max_depth=2)
        assert len(related_2) == 2
        pattern_ids = {p.pattern_id for p in related_2}
        assert pattern_ids == {"traverse_b", "traverse_c"}
    
    def test_detects_circular_relationships(self, knowledge_graph):
        """Test that circular relationships are handled properly."""
        # Create circular graph: A -> B -> C -> A
        knowledge_graph.add_pattern("circ_a", "A", "Content", PatternType.WORKFLOW)
        knowledge_graph.add_pattern("circ_b", "B", "Content", PatternType.WORKFLOW)
        knowledge_graph.add_pattern("circ_c", "C", "Content", PatternType.WORKFLOW)
        
        knowledge_graph.link_patterns("circ_a", "circ_b", RelationshipType.RELATED_TO)
        knowledge_graph.link_patterns("circ_b", "circ_c", RelationshipType.RELATED_TO)
        knowledge_graph.link_patterns("circ_c", "circ_a", RelationshipType.RELATED_TO)
        
        # Traverse should not infinite loop
        related = knowledge_graph.get_related_patterns("circ_a", max_depth=5)
        
        # Should get all 3 patterns but no duplicates
        assert len(related) == 2  # Excludes starting pattern
        pattern_ids = {p.pattern_id for p in related}
        assert pattern_ids == {"circ_b", "circ_c"}


class TestConfidenceDecay:
    """Test confidence decay logic."""
    
    def test_applies_decay_based_on_age(self, knowledge_graph):
        """Test that patterns decay based on last access time."""
        # Add old pattern (simulate 70 days old)
        old_date = (datetime.now() - timedelta(days=70)).isoformat()
        now = datetime.now().isoformat()
        
        conn = sqlite3.connect(knowledge_graph.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO patterns (pattern_id, title, content, pattern_type, confidence, created_at, last_accessed)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, ("old_pattern", "Old", "Content", PatternType.WORKFLOW.value, 1.0, now, old_date))
        conn.commit()
        conn.close()
        
        # Apply decay
        result = knowledge_graph.apply_confidence_decay()
        
        # Pattern should have decayed
        pattern = knowledge_graph.get_pattern("old_pattern")
        assert pattern.confidence < 1.0
        assert result['decayed_count'] >= 1
    
    def test_deletes_low_confidence_patterns(self, knowledge_graph):
        """Test that patterns below confidence threshold are deleted."""
        # Add pattern with low confidence that's old enough to be eligible
        old_date = (datetime.now() - timedelta(days=70)).isoformat()
        now = datetime.now().isoformat()
        
        conn = sqlite3.connect(knowledge_graph.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO patterns (pattern_id, title, content, pattern_type, confidence, created_at, last_accessed)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, ("low_conf", "Low Confidence", "Content", PatternType.SOLUTION.value, 0.25, now, old_date))
        conn.commit()
        conn.close()
        
        # Apply decay (should delete low confidence)
        result = knowledge_graph.apply_confidence_decay()
        
        # Pattern should be deleted
        pattern = knowledge_graph.get_pattern("low_conf")
        assert pattern is None
        assert result['deleted_count'] >= 1
    
    def test_protects_pinned_patterns(self, knowledge_graph):
        """Test that pinned patterns are protected from decay."""
        # Add pinned pattern (simulate 150 days old)
        old_date = (datetime.now() - timedelta(days=150)).isoformat()
        
        knowledge_graph.add_pattern(
            pattern_id="pinned",
            title="Pinned Pattern",
            content="This is pinned",
            pattern_type=PatternType.PRINCIPLE,
            confidence=1.0
        )
        
        # Mark as pinned
        knowledge_graph.pin_pattern("pinned")
        
        # Manually set old access date
        conn = sqlite3.connect(knowledge_graph.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE patterns SET last_accessed = ? WHERE pattern_id = ?
        """, (old_date, "pinned"))
        conn.commit()
        conn.close()
        
        # Apply decay
        knowledge_graph.apply_confidence_decay()
        
        # Pinned pattern should NOT decay
        pattern = knowledge_graph.get_pattern("pinned")
        assert pattern.confidence == 1.0
    
    def test_tracks_decay_history(self, knowledge_graph):
        """Test that decay events are logged."""
        # Add old pattern
        old_date = (datetime.now() - timedelta(days=95)).isoformat()
        now = datetime.now().isoformat()
        
        conn = sqlite3.connect(knowledge_graph.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO patterns (pattern_id, title, content, pattern_type, confidence, created_at, last_accessed)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, ("decay_track", "Track", "Content", PatternType.WORKFLOW.value, 1.0, now, old_date))
        conn.commit()
        conn.close()
        
        # Apply decay
        knowledge_graph.apply_confidence_decay()
        
        # Check decay log
        log = knowledge_graph.get_decay_log()
        
        assert len(log) >= 1
        assert any(entry['pattern_id'] == 'decay_track' for entry in log)


class TestTagManagement:
    """Test pattern tagging operations."""
    
    def test_adds_tags_to_pattern(self, knowledge_graph):
        """Test adding tags to a pattern."""
        knowledge_graph.add_pattern(
            pattern_id="tagged",
            title="Tagged Pattern",
            content="Content",
            pattern_type=PatternType.WORKFLOW,
            tags=["tag1", "tag2", "tag3"]
        )
        
        # Verify tags were added
        pattern = knowledge_graph.get_pattern("tagged")
        tags = knowledge_graph.get_pattern_tags("tagged")
        
        assert len(tags) == 3
        assert set(tags) == {"tag1", "tag2", "tag3"}
    
    def test_finds_patterns_by_tag(self, knowledge_graph):
        """Test finding patterns with a specific tag."""
        knowledge_graph.add_pattern(
            pattern_id="tag_search_1",
            title="Pattern 1",
            content="Content",
            pattern_type=PatternType.WORKFLOW,
            tags=["testing", "quality"]
        )
        
        knowledge_graph.add_pattern(
            pattern_id="tag_search_2",
            title="Pattern 2",
            content="Content",
            pattern_type=PatternType.SOLUTION,
            tags=["testing", "automation"]
        )
        
        knowledge_graph.add_pattern(
            pattern_id="tag_search_3",
            title="Pattern 3",
            content="Content",
            pattern_type=PatternType.PRINCIPLE,
            tags=["design", "solid"]
        )
        
        # Find patterns tagged with "testing"
        results = knowledge_graph.find_patterns_by_tag("testing")
        
        assert len(results) == 2
        pattern_ids = {p.pattern_id for p in results}
        assert pattern_ids == {"tag_search_1", "tag_search_2"}
    
    def test_gets_tag_cloud(self, knowledge_graph):
        """Test getting tag frequency (tag cloud)."""
        # Add patterns with various tags
        knowledge_graph.add_pattern("tc1", "P1", "C", PatternType.WORKFLOW, tags=["testing", "quality"])
        knowledge_graph.add_pattern("tc2", "P2", "C", PatternType.WORKFLOW, tags=["testing", "automation"])
        knowledge_graph.add_pattern("tc3", "P3", "C", PatternType.WORKFLOW, tags=["testing", "tdd"])
        knowledge_graph.add_pattern("tc4", "P4", "C", PatternType.WORKFLOW, tags=["design", "solid"])
        
        # Get tag cloud
        tag_cloud = knowledge_graph.get_tag_cloud()
        
        # "testing" should appear 3 times
        testing_count = next(
            (t['count'] for t in tag_cloud if t['tag'] == 'testing'),
            0
        )
        
        assert testing_count == 3
        assert len(tag_cloud) >= 5  # At least 5 unique tags
