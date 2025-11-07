"""
Tests for CORTEX Tier 2: Namespace/Scope Boundary System

This test suite validates the knowledge boundary enforcement that ensures
impenetrable separation between CORTEX core intelligence (generic) and
application-specific knowledge (KSESSIONS, NOOR, etc.).

Test Coverage:
- Scope validation (generic vs application)
- Namespace storage and retrieval
- Default values
- Boundary enforcement
- Migration classification
"""

import pytest
import sqlite3
import json
from pathlib import Path
from datetime import datetime
import tempfile
import shutil

from CORTEX.src.tier2.knowledge_graph import (
    KnowledgeGraph,
    Pattern,
    PatternType
)


@pytest.fixture
def temp_db():
    """Create a temporary test database."""
    temp_dir = tempfile.mkdtemp()
    db_path = Path(temp_dir) / "test_knowledge_graph.db"
    
    yield db_path
    
    # Cleanup - wait a bit for connections to close
    import time
    time.sleep(0.1)
    try:
        shutil.rmtree(temp_dir)
    except PermissionError:
        # On Windows, sometimes files are still locked
        # Try again after a short delay
        time.sleep(0.5)
        shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def kg(temp_db):
    """Create a KnowledgeGraph instance with temporary database."""
    return KnowledgeGraph(db_path=temp_db)


class TestScopeValidation:
    """Test scope parameter validation."""
    
    def test_add_pattern_with_generic_scope(self, kg):
        """Verify generic scope patterns are stored correctly."""
        pattern = kg.add_pattern(
            pattern_id="test_workflow",
            title="Test-Driven Development",
            content="Always write tests first",
            pattern_type=PatternType.WORKFLOW,
            scope="generic",
            namespaces=["CORTEX-core"]
        )
        
        assert pattern.scope == "generic"
        assert pattern.namespaces == ["CORTEX-core"]
        
        # Verify in database
        retrieved = kg.get_pattern("test_workflow")
        assert retrieved.scope == "generic"
        assert retrieved.namespaces == ["CORTEX-core"]
    
    def test_add_pattern_with_application_scope(self, kg):
        """Verify application scope patterns are stored correctly."""
        pattern = kg.add_pattern(
            pattern_id="ksessions_feature",
            title="KSESSIONS Host Panel",
            content="Host control panel implementation",
            pattern_type=PatternType.SOLUTION,
            scope="application",
            namespaces=["KSESSIONS"]
        )
        
        assert pattern.scope == "application"
        assert pattern.namespaces == ["KSESSIONS"]
        
        # Verify in database
        retrieved = kg.get_pattern("ksessions_feature")
        assert retrieved.scope == "application"
        assert retrieved.namespaces == ["KSESSIONS"]
    
    def test_invalid_scope_raises_error(self, kg):
        """Verify invalid scope values are rejected."""
        with pytest.raises(ValueError, match="Invalid scope"):
            kg.add_pattern(
                pattern_id="invalid_pattern",
                title="Invalid Scope Test",
                content="This should fail",
                pattern_type=PatternType.WORKFLOW,
                scope="invalid_scope"  # Invalid!
            )
    
    def test_scope_must_be_generic_or_application(self, kg):
        """Verify only 'generic' and 'application' are valid scopes."""
        valid_scopes = ["generic", "application"]
        
        for scope in valid_scopes:
            pattern = kg.add_pattern(
                pattern_id=f"pattern_{scope}",
                title=f"Pattern with {scope} scope",
                content="Test content",
                pattern_type=PatternType.WORKFLOW,
                scope=scope
            )
            assert pattern.scope == scope
        
        # Invalid scopes
        invalid_scopes = ["project", "session", "global", ""]
        for scope in invalid_scopes:
            with pytest.raises(ValueError):
                kg.add_pattern(
                    pattern_id=f"pattern_{scope}",
                    title="Invalid",
                    content="Test",
                    pattern_type=PatternType.WORKFLOW,
                    scope=scope
                )


class TestNamespaceStorage:
    """Test namespace storage and retrieval."""
    
    def test_namespace_stored_as_json_array(self, kg, temp_db):
        """Verify namespaces are stored as JSON array in database."""
        kg.add_pattern(
            pattern_id="multi_ns_pattern",
            title="Multi-Namespace Pattern",
            content="Shared pattern",
            pattern_type=PatternType.PRINCIPLE,
            scope="generic",
            namespaces=["CORTEX-core", "KSESSIONS", "NOOR"]
        )
        
        # Check raw database value
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("SELECT namespaces FROM patterns WHERE pattern_id = ?", ("multi_ns_pattern",))
        row = cursor.fetchone()
        conn.close()
        
        # Should be JSON string
        assert row is not None
        namespaces_json = row[0]
        namespaces = json.loads(namespaces_json)
        
        assert namespaces == ["CORTEX-core", "KSESSIONS", "NOOR"]
    
    def test_single_namespace(self, kg):
        """Verify single namespace stored correctly."""
        pattern = kg.add_pattern(
            pattern_id="single_ns",
            title="Single Namespace",
            content="CORTEX-only pattern",
            pattern_type=PatternType.WORKFLOW,
            scope="generic",
            namespaces=["CORTEX-core"]
        )
        
        assert pattern.namespaces == ["CORTEX-core"]
        assert len(pattern.namespaces) == 1
    
    def test_multiple_namespaces(self, kg):
        """Verify multiple namespaces stored correctly."""
        pattern = kg.add_pattern(
            pattern_id="multi_ns",
            title="Multi-Namespace Pattern",
            content="Shared across apps",
            pattern_type=PatternType.PRINCIPLE,
            scope="generic",
            namespaces=["CORTEX-core", "KSESSIONS", "NOOR", "SPA"]
        )
        
        assert pattern.namespaces == ["CORTEX-core", "KSESSIONS", "NOOR", "SPA"]
        assert len(pattern.namespaces) == 4
    
    def test_namespace_retrieval_preserves_order(self, kg):
        """Verify namespace order is preserved."""
        namespaces = ["Z-App", "A-Core", "M-Middle"]
        
        kg.add_pattern(
            pattern_id="order_test",
            title="Order Test",
            content="Test namespace order",
            pattern_type=PatternType.WORKFLOW,
            scope="generic",
            namespaces=namespaces
        )
        
        retrieved = kg.get_pattern("order_test")
        assert retrieved.namespaces == namespaces


class TestDefaultValues:
    """Test default values for scope and namespaces."""
    
    def test_default_scope_is_generic(self, kg):
        """Verify default scope is 'generic'."""
        pattern = kg.add_pattern(
            pattern_id="default_scope_test",
            title="Default Scope",
            content="No scope specified",
            pattern_type=PatternType.WORKFLOW
            # scope parameter omitted - should default to 'generic'
        )
        
        assert pattern.scope == "generic"
    
    def test_default_namespaces_is_cortex_core(self, kg):
        """Verify default namespaces is ['CORTEX-core']."""
        pattern = kg.add_pattern(
            pattern_id="default_ns_test",
            title="Default Namespace",
            content="No namespace specified",
            pattern_type=PatternType.WORKFLOW,
            scope="generic"
            # namespaces parameter omitted - should default to ['CORTEX-core']
        )
        
        assert pattern.namespaces == ["CORTEX-core"]
    
    def test_both_defaults_together(self, kg):
        """Verify both scope and namespaces default correctly."""
        pattern = kg.add_pattern(
            pattern_id="both_defaults",
            title="Both Defaults",
            content="No scope or namespace specified",
            pattern_type=PatternType.WORKFLOW
            # Both scope and namespaces omitted
        )
        
        assert pattern.scope == "generic"
        assert pattern.namespaces == ["CORTEX-core"]


class TestBoundaryEnforcement:
    """Test boundary enforcement and isolation."""
    
    def test_generic_scope_accepts_cortex_namespace(self, kg):
        """Verify generic scope works with CORTEX-core namespace."""
        pattern = kg.add_pattern(
            pattern_id="generic_cortex",
            title="Generic CORTEX Pattern",
            content="Core intelligence",
            pattern_type=PatternType.PRINCIPLE,
            scope="generic",
            namespaces=["CORTEX-core"]
        )
        
        assert pattern.scope == "generic"
        assert "CORTEX-core" in pattern.namespaces
    
    def test_application_scope_accepts_app_namespace(self, kg):
        """Verify application scope works with app namespaces."""
        pattern = kg.add_pattern(
            pattern_id="app_ksessions",
            title="KSESSIONS Pattern",
            content="Application-specific",
            pattern_type=PatternType.SOLUTION,
            scope="application",
            namespaces=["KSESSIONS"]
        )
        
        assert pattern.scope == "application"
        assert "KSESSIONS" in pattern.namespaces
    
    def test_can_retrieve_by_scope(self, kg):
        """Verify patterns can be filtered by scope."""
        # Add generic patterns
        kg.add_pattern(
            pattern_id="generic_1",
            title="Generic 1",
            content="CORTEX pattern",
            pattern_type=PatternType.WORKFLOW,
            scope="generic"
        )
        
        # Add application pattern
        kg.add_pattern(
            pattern_id="app_1",
            title="App 1",
            content="KSESSIONS pattern",
            pattern_type=PatternType.WORKFLOW,
            scope="application",
            namespaces=["KSESSIONS"]
        )
        
        # Should be able to query by scope
        # (We'll add this method in Phase 2, but verify data is there)
        conn = sqlite3.connect(kg.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM patterns WHERE scope = 'generic'")
        generic_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM patterns WHERE scope = 'application'")
        app_count = cursor.fetchone()[0]
        
        conn.close()
        
        assert generic_count >= 1
        assert app_count >= 1


class TestMigrationClassification:
    """Test that existing patterns can be classified correctly."""
    
    def test_cortex_patterns_classified_as_generic(self, kg):
        """Verify CORTEX patterns get generic scope."""
        # Patterns that should be classified as generic
        cortex_patterns = [
            ("test_first", "Test-First Development", "TDD workflow"),
            ("solid_principle", "SOLID Principles", "Architecture guidance"),
            ("governance_rule", "Governance Rule", "Protection rules"),
        ]
        
        for pattern_id, title, content in cortex_patterns:
            pattern = kg.add_pattern(
                pattern_id=pattern_id,
                title=title,
                content=content,
                pattern_type=PatternType.PRINCIPLE,
                scope="generic",  # Explicitly generic
                namespaces=["CORTEX-core"]
            )
            
            assert pattern.scope == "generic"
            assert "CORTEX-core" in pattern.namespaces
    
    def test_ksessions_patterns_classified_as_application(self, kg):
        """Verify KSESSIONS patterns get application scope."""
        # Patterns that should be classified as application
        ksessions_patterns = [
            ("host_panel", "Host Control Panel", "SPA/NoorCanvas/HostPanel.razor"),
            ("registration_link", "Registration Link", "KSESSIONS registration flow"),
        ]
        
        for pattern_id, title, content in ksessions_patterns:
            pattern = kg.add_pattern(
                pattern_id=pattern_id,
                title=title,
                content=content,
                pattern_type=PatternType.SOLUTION,
                scope="application",
                namespaces=["KSESSIONS"]
            )
            
            assert pattern.scope == "application"
            assert "KSESSIONS" in pattern.namespaces


class TestIndexPerformance:
    """Test that scope and namespace indexes are created."""
    
    def test_scope_index_exists(self, kg, temp_db):
        """Verify idx_scope index exists on patterns.scope."""
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='index' AND name='idx_scope'
        """)
        
        result = cursor.fetchone()
        conn.close()
        
        assert result is not None
        assert result[0] == "idx_scope"
    
    def test_namespace_index_exists(self, kg, temp_db):
        """Verify idx_namespaces index exists on patterns.namespaces."""
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='index' AND name='idx_namespaces'
        """)
        
        result = cursor.fetchone()
        conn.close()
        
        assert result is not None
        assert result[0] == "idx_namespaces"
