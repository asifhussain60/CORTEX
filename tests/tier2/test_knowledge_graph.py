"""
Comprehensive tests for Brain Tier 2: Knowledge Graph

Tests pattern storage/retrieval, FTS5 search, relationship tracking, workflow templates,
pattern decay, and TDD cycle learning.
Target: 90% coverage (from 0.00%)

Test Coverage Areas:
1. Database initialization and schema
2. Pattern storage and retrieval
3. FTS5 full-text search
4. Relationship tracking (co-modification)
5. Workflow template management
6. Pattern confidence boosting
7. Pattern decay mechanism
8. TDD cycle pattern learning
9. File relationship queries
10. Confidence metadata
"""

import pytest
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any
import tempfile
import shutil
import json

from src.tier2.knowledge_graph import KnowledgeGraph


class TestKnowledgeGraphBasics:
    """Test basic initialization and database schema."""
    
    @pytest.fixture
    def temp_db_path(self):
        """Create a temporary database for testing."""
        temp_dir = tempfile.mkdtemp()
        db_path = Path(temp_dir) / "test_knowledge_graph.db"
        yield db_path
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def knowledge_graph(self, temp_db_path):
        """Create a KnowledgeGraph instance for testing."""
        return KnowledgeGraph(db_path=str(temp_db_path))
    
    def test_initialization(self, knowledge_graph):
        """Test KnowledgeGraph initialization."""
        assert knowledge_graph is not None
        assert knowledge_graph.db_path.exists()
    
    def test_database_schema_creation(self, temp_db_path):
        """Test that database schema is created correctly."""
        kg = KnowledgeGraph(db_path=str(temp_db_path))
        
        conn = sqlite3.connect(temp_db_path)
        cursor = conn.cursor()
        
        # Check tables exist
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name IN (
                'patterns', 'relationships', 'workflows', 'patterns_fts'
            )
        """)
        
        tables = {row[0] for row in cursor.fetchall()}
        assert 'patterns' in tables
        assert 'relationships' in tables
        assert 'workflows' in tables
        assert 'patterns_fts' in tables
        
        conn.close()
    
    def test_database_indexes(self, temp_db_path):
        """Test that database indexes are created."""
        kg = KnowledgeGraph(db_path=str(temp_db_path))
        
        conn = sqlite3.connect(temp_db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='index'
        """)
        
        indexes = {row[0] for row in cursor.fetchall()}
        assert 'idx_patterns_confidence' in indexes
        assert 'idx_patterns_last_used' in indexes
        assert 'idx_relationships_files' in indexes
        
        conn.close()


class TestPatternStorage:
    """Test pattern storage and retrieval."""
    
    @pytest.fixture
    def temp_db_path(self):
        """Create a temporary database for testing."""
        temp_dir = tempfile.mkdtemp()
        db_path = Path(temp_dir) / "test_knowledge_graph.db"
        yield db_path
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def knowledge_graph(self, temp_db_path):
        """Create a KnowledgeGraph instance for testing."""
        return KnowledgeGraph(db_path=str(temp_db_path))
    
    def test_store_pattern_basic(self, knowledge_graph):
        """Test storing a basic pattern."""
        pattern_id = knowledge_graph.store_pattern(
            title="Test Pattern",
            pattern_type="workflow",
            confidence=0.8,
            context={"step1": "Initialize", "step2": "Execute"}
        )
        
        assert pattern_id is not None
        assert pattern_id.startswith("pattern_")
        assert "test_pattern" in pattern_id
    
    def test_store_pattern_with_scope(self, knowledge_graph):
        """Test storing pattern with scope."""
        pattern_id = knowledge_graph.store_pattern(
            title="CORTEX Pattern",
            pattern_type="validation",
            confidence=0.9,
            scope="cortex"
        )
        
        assert pattern_id is not None
    
    def test_store_pattern_with_namespaces(self, knowledge_graph):
        """Test storing pattern with namespaces."""
        pattern_id = knowledge_graph.store_pattern(
            title="Namespaced Pattern",
            pattern_type="workflow",
            confidence=0.75,
            namespaces=["auth", "api", "security"]
        )
        
        assert pattern_id is not None
    
    def test_store_multiple_patterns(self, knowledge_graph):
        """Test storing multiple patterns."""
        pattern_ids = []
        
        for i in range(3):
            pattern_id = knowledge_graph.store_pattern(
                title=f"Pattern {i}",
                pattern_type="workflow",
                confidence=0.5 + (i * 0.1)
            )
            pattern_ids.append(pattern_id)
        
        assert len(pattern_ids) == 3
        assert len(set(pattern_ids)) == 3  # All unique


class TestPatternSearch:
    """Test FTS5 full-text search functionality."""
    
    @pytest.fixture
    def temp_db_path(self):
        """Create a temporary database for testing."""
        temp_dir = tempfile.mkdtemp()
        db_path = Path(temp_dir) / "test_knowledge_graph.db"
        yield db_path
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def knowledge_graph(self, temp_db_path):
        """Create a KnowledgeGraph instance with test patterns."""
        kg = KnowledgeGraph(db_path=str(temp_db_path))
        
        # Add test patterns
        kg.store_pattern(
            title="Authentication Flow",
            pattern_type="workflow",
            confidence=0.9,
            context={"login": "JWT", "oauth": "OAuth2"}
        )
        
        kg.store_pattern(
            title="Database Migration",
            pattern_type="workflow",
            confidence=0.85,
            context={"schema": "SQL", "rollback": "enabled"}
        )
        
        kg.store_pattern(
            title="API Testing Strategy",
            pattern_type="validation",
            confidence=0.8,
            context={"unit": "pytest", "integration": "requests"}
        )
        
        return kg
    
    def test_search_patterns_basic(self, knowledge_graph):
        """Test basic pattern search."""
        results = knowledge_graph.search_patterns(
            query="authentication",
            min_confidence=0.7
        )
        
        assert len(results) > 0
        assert any("authentication" in r["title"].lower() for r in results)
    
    def test_search_patterns_by_type(self, knowledge_graph):
        """Test searching patterns by type."""
        results = knowledge_graph.search_patterns(
            query="authentication OR migration",
            pattern_type="workflow",
            min_confidence=0.7
        )
        
        assert len(results) > 0
        assert all(r["pattern_type"] == "workflow" for r in results)
    
    def test_search_patterns_with_confidence_filter(self, knowledge_graph):
        """Test searching with confidence threshold."""
        results = knowledge_graph.search_patterns(
            query="migration OR authentication",
            min_confidence=0.85
        )
        
        assert all(r["confidence"] >= 0.85 for r in results)
    
    def test_search_patterns_with_limit(self, knowledge_graph):
        """Test search result limiting."""
        results = knowledge_graph.search_patterns(
            query="workflow OR validation",
            min_confidence=0.5,
            limit=2
        )
        
        assert len(results) <= 2
    
    def test_search_patterns_with_metadata(self, knowledge_graph):
        """Test search with confidence metadata."""
        results = knowledge_graph.search_patterns(
            query="authentication",
            min_confidence=0.7,
            include_confidence_metadata=True
        )
        
        if results:
            assert "pattern_count" in results[0]
            assert "success_rate" in results[0]
            assert "usage_count" in results[0]
    
    def test_search_patterns_no_results(self, knowledge_graph):
        """Test search with no matching results."""
        results = knowledge_graph.search_patterns(
            query="nonexistent_pattern_xyz",
            min_confidence=0.99
        )
        
        assert len(results) == 0


class TestRelationshipTracking:
    """Test file relationship tracking."""
    
    @pytest.fixture
    def temp_db_path(self):
        """Create a temporary database for testing."""
        temp_dir = tempfile.mkdtemp()
        db_path = Path(temp_dir) / "test_knowledge_graph.db"
        yield db_path
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def knowledge_graph(self, temp_db_path):
        """Create a KnowledgeGraph instance for testing."""
        return KnowledgeGraph(db_path=str(temp_db_path))
    
    def test_track_relationship_basic(self, knowledge_graph):
        """Test tracking a basic file relationship."""
        knowledge_graph.track_relationship(
            file_a="src/auth.py",
            file_b="src/user.py",
            relationship_type="co_modification",
            strength=0.8
        )
        
        # Verify relationship exists
        relationships = knowledge_graph.get_file_relationships("src/auth.py")
        assert len(relationships) > 0
        assert any(r["related_file"] == "src/user.py" for r in relationships)
    
    def test_track_relationship_increment(self, knowledge_graph):
        """Test that tracking same relationship increments count."""
        # Track relationship twice
        knowledge_graph.track_relationship(
            file_a="src/main.py",
            file_b="src/config.py",
            strength=0.7
        )
        
        knowledge_graph.track_relationship(
            file_a="src/main.py",
            file_b="src/config.py",
            strength=0.8
        )
        
        relationships = knowledge_graph.get_file_relationships("src/main.py")
        
        # Should have one relationship with count >= 2
        config_rel = next((r for r in relationships if r["related_file"] == "src/config.py"), None)
        assert config_rel is not None
        assert config_rel["co_modification_count"] >= 2
    
    def test_get_file_relationships_multiple(self, knowledge_graph):
        """Test getting multiple relationships for a file."""
        # Track multiple relationships
        knowledge_graph.track_relationship(
            file_a="src/core.py",
            file_b="src/utils.py",
            strength=0.9
        )
        
        knowledge_graph.track_relationship(
            file_a="src/core.py",
            file_b="src/helpers.py",
            strength=0.85
        )
        
        relationships = knowledge_graph.get_file_relationships("src/core.py", min_strength=0.8)
        
        assert len(relationships) >= 2
    
    def test_get_file_relationships_strength_filter(self, knowledge_graph):
        """Test filtering relationships by strength."""
        knowledge_graph.track_relationship(
            file_a="src/test.py",
            file_b="src/weak.py",
            strength=0.3
        )
        
        knowledge_graph.track_relationship(
            file_a="src/test.py",
            file_b="src/strong.py",
            strength=0.9
        )
        
        relationships = knowledge_graph.get_file_relationships("src/test.py", min_strength=0.7)
        
        # Should only get strong relationship
        assert all(r["strength"] >= 0.7 for r in relationships)
        assert any(r["related_file"] == "src/strong.py" for r in relationships)
    
    def test_get_file_relationships_empty(self, knowledge_graph):
        """Test getting relationships for file with none."""
        relationships = knowledge_graph.get_file_relationships("src/nonexistent.py")
        assert len(relationships) == 0


class TestWorkflowTemplates:
    """Test workflow template storage and retrieval."""
    
    @pytest.fixture
    def temp_db_path(self):
        """Create a temporary database for testing."""
        temp_dir = tempfile.mkdtemp()
        db_path = Path(temp_dir) / "test_knowledge_graph.db"
        yield db_path
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def knowledge_graph(self, temp_db_path):
        """Create a KnowledgeGraph instance for testing."""
        return KnowledgeGraph(db_path=str(temp_db_path))
    
    def test_store_workflow_template(self, knowledge_graph):
        """Test storing a workflow template."""
        phases = [
            {"name": "Planning", "duration": 2},
            {"name": "Implementation", "duration": 8},
            {"name": "Testing", "duration": 4}
        ]
        
        workflow_id = knowledge_graph.store_workflow_template(
            name="Feature Development",
            phases=phases,
            success_rate=0.85,
            avg_duration_hours=14.0
        )
        
        assert workflow_id is not None
        assert workflow_id.startswith("workflow_")
    
    def test_get_workflow_template(self, knowledge_graph):
        """Test retrieving a workflow template."""
        phases = [
            {"name": "RED", "action": "Write failing test"},
            {"name": "GREEN", "action": "Implement minimum code"},
            {"name": "REFACTOR", "action": "Clean up code"}
        ]
        
        knowledge_graph.store_workflow_template(
            name="TDD Cycle",
            phases=phases,
            success_rate=0.95
        )
        
        workflow = knowledge_graph.get_workflow_template("TDD Cycle")
        
        assert workflow is not None
        assert workflow["name"] == "TDD Cycle"
        assert len(workflow["phases"]) == 3
        assert workflow["success_rate"] == 0.95
    
    def test_get_nonexistent_workflow(self, knowledge_graph):
        """Test retrieving a workflow that doesn't exist."""
        workflow = knowledge_graph.get_workflow_template("Nonexistent Workflow")
        assert workflow is None
    
    def test_workflow_template_replace(self, knowledge_graph):
        """Test that storing same workflow name replaces old one."""
        phases_v1 = [{"name": "Phase 1"}]
        phases_v2 = [{"name": "Phase 1"}, {"name": "Phase 2"}]
        
        knowledge_graph.store_workflow_template(
            name="Test Workflow",
            phases=phases_v1,
            success_rate=0.5
        )
        
        knowledge_graph.store_workflow_template(
            name="Test Workflow",
            phases=phases_v2,
            success_rate=0.8
        )
        
        workflow = knowledge_graph.get_workflow_template("Test Workflow")
        
        assert len(workflow["phases"]) == 2
        assert workflow["success_rate"] == 0.8


class TestPatternConfidence:
    """Test pattern confidence boosting and decay."""
    
    @pytest.fixture
    def temp_db_path(self):
        """Create a temporary database for testing."""
        temp_dir = tempfile.mkdtemp()
        db_path = Path(temp_dir) / "test_knowledge_graph.db"
        yield db_path
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def knowledge_graph(self, temp_db_path):
        """Create a KnowledgeGraph instance for testing."""
        return KnowledgeGraph(db_path=str(temp_db_path))
    
    def test_boost_pattern(self, knowledge_graph):
        """Test boosting pattern confidence."""
        pattern_id = knowledge_graph.store_pattern(
            title="Boostable Pattern",
            pattern_type="workflow",
            confidence=0.5
        )
        
        # Boost pattern
        knowledge_graph.boost_pattern(pattern_id, boost_amount=0.1)
        
        # Verify confidence increased
        results = knowledge_graph.search_patterns(
            query="boostable",
            min_confidence=0.55
        )
        
        assert len(results) > 0
        assert results[0]["confidence"] >= 0.6
    
    def test_boost_pattern_cap(self, knowledge_graph):
        """Test that pattern confidence doesn't exceed 1.0."""
        pattern_id = knowledge_graph.store_pattern(
            title="High Confidence Pattern",
            pattern_type="workflow",
            confidence=0.95
        )
        
        # Boost multiple times
        for _ in range(5):
            knowledge_graph.boost_pattern(pattern_id, boost_amount=0.1)
        
        results = knowledge_graph.search_patterns(
            query="high confidence",
            min_confidence=0.5
        )
        
        # Confidence should not exceed 1.0
        assert results[0]["confidence"] <= 1.0
    
    def test_boost_updates_usage_count(self, knowledge_graph):
        """Test that boosting updates usage count."""
        pattern_id = knowledge_graph.store_pattern(
            title="Usage Tracked Pattern",
            pattern_type="workflow",
            confidence=0.7
        )
        
        # Boost pattern twice
        knowledge_graph.boost_pattern(pattern_id)
        knowledge_graph.boost_pattern(pattern_id)
        
        results = knowledge_graph.search_patterns(
            query="usage tracked",
            min_confidence=0.5
        )
        
        assert results[0]["usage_count"] >= 2
    
    def test_apply_decay_basic(self, knowledge_graph):
        """Test pattern decay mechanism."""
        # Store pattern with old last_used date
        pattern_id = knowledge_graph.store_pattern(
            title="Old Pattern",
            pattern_type="workflow",
            confidence=0.8
        )
        
        # Manually update last_used to be old
        with knowledge_graph._get_connection() as conn:
            cursor = conn.cursor()
            old_date = (datetime.now() - timedelta(days=60)).isoformat()
            cursor.execute("""
                UPDATE patterns 
                SET last_used = ?
                WHERE pattern_id = ?
            """, (old_date, pattern_id))
            conn.commit()
        
        # Apply decay
        knowledge_graph.apply_decay(decay_rate=0.1, min_confidence=0.3)
        
        # Verify confidence decreased
        results = knowledge_graph.search_patterns(
            query="old pattern",
            min_confidence=0.3
        )
        
        if results:
            assert results[0]["confidence"] < 0.8
    
    def test_apply_decay_minimum(self, knowledge_graph):
        """Test that decay respects minimum confidence."""
        pattern_id = knowledge_graph.store_pattern(
            title="Min Confidence Pattern",
            pattern_type="workflow",
            confidence=0.35
        )
        
        # Set old date
        with knowledge_graph._get_connection() as conn:
            cursor = conn.cursor()
            old_date = (datetime.now() - timedelta(days=60)).isoformat()
            cursor.execute("""
                UPDATE patterns 
                SET last_used = ?
                WHERE pattern_id = ?
            """, (old_date, pattern_id))
            conn.commit()
        
        # Apply decay
        knowledge_graph.apply_decay(decay_rate=0.1, min_confidence=0.3)
        
        # Verify confidence not below minimum
        results = knowledge_graph.search_patterns(
            query="min confidence",
            min_confidence=0.2
        )
        
        if results:
            assert results[0]["confidence"] >= 0.3


class TestTDDCyclePatterns:
    """Test TDD cycle pattern learning."""
    
    @pytest.fixture
    def temp_db_path(self):
        """Create a temporary database for testing."""
        temp_dir = tempfile.mkdtemp()
        db_path = Path(temp_dir) / "test_knowledge_graph.db"
        yield db_path
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def knowledge_graph(self, temp_db_path):
        """Create a KnowledgeGraph instance for testing."""
        return KnowledgeGraph(db_path=str(temp_db_path))
    
    def test_store_tdd_cycle_pattern(self, knowledge_graph):
        """Test storing TDD cycle as a pattern."""
        pattern_id = knowledge_graph.store_tdd_cycle_pattern(
            feature="User Authentication",
            test_strategy="unit_integration",
            implementation_approach="service_layer",
            refactoring_type="extract_method",
            confidence=0.85
        )
        
        assert pattern_id is not None
        assert pattern_id.startswith("pattern_")
    
    def test_search_tdd_patterns(self, knowledge_graph):
        """Test searching for TDD patterns."""
        knowledge_graph.store_tdd_cycle_pattern(
            feature="Password Reset",
            test_strategy="unit",
            implementation_approach="facade",
            refactoring_type="simplify_conditionals",
            confidence=0.8
        )
        
        results = knowledge_graph.search_patterns(
            query="password reset",
            pattern_type="tdd_cycle",
            min_confidence=0.7
        )
        
        assert len(results) > 0


class TestHelperMethods:
    """Test helper and utility methods."""
    
    @pytest.fixture
    def temp_db_path(self):
        """Create a temporary database for testing."""
        temp_dir = tempfile.mkdtemp()
        db_path = Path(temp_dir) / "test_knowledge_graph.db"
        yield db_path
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def knowledge_graph(self, temp_db_path):
        """Create a KnowledgeGraph instance for testing."""
        return KnowledgeGraph(db_path=str(temp_db_path))
    
    def test_generate_pattern_id(self, knowledge_graph):
        """Test pattern ID generation."""
        pattern_id = knowledge_graph._generate_pattern_id("Test Pattern Name")
        
        assert pattern_id.startswith("pattern_")
        assert "test_pattern_name" in pattern_id
    
    def test_generate_workflow_id(self, knowledge_graph):
        """Test workflow ID generation."""
        workflow_id = knowledge_graph._generate_workflow_id("My Workflow")
        
        assert workflow_id.startswith("workflow_")
        assert "my_workflow" in workflow_id
    
    def test_calculate_success_rate_new_pattern(self, knowledge_graph):
        """Test success rate calculation for new pattern."""
        pattern_id = knowledge_graph.store_pattern(
            title="New Pattern",
            pattern_type="workflow",
            confidence=0.7
        )
        
        success_rate = knowledge_graph._calculate_success_rate(pattern_id)
        
        # New pattern should have success rate equal to confidence
        assert success_rate == 0.7
    
    def test_calculate_success_rate_well_used(self, knowledge_graph):
        """Test success rate calculation for well-used pattern."""
        pattern_id = knowledge_graph.store_pattern(
            title="Popular Pattern",
            pattern_type="workflow",
            confidence=0.8
        )
        
        # Boost pattern multiple times to increase usage count
        for _ in range(12):
            knowledge_graph.boost_pattern(pattern_id, boost_amount=0.0)
        
        success_rate = knowledge_graph._calculate_success_rate(pattern_id)
        
        # Well-used pattern should have boosted success rate
        assert success_rate > 0.8


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
