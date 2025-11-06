"""
Tests for Pattern Cleanup System.

Validates:
- Automatic confidence decay
- Pattern consolidation
- Stale pattern removal
- Scope protection (generic patterns never touched)
- CORTEX-core namespace protection
"""

import pytest
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
import tempfile
import shutil
import json

from CORTEX.src.tier2.knowledge_graph import KnowledgeGraph, PatternType
from CORTEX.src.tier2.pattern_cleanup import PatternCleanup, CleanupStats


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    temp_dir = tempfile.mkdtemp()
    db_path = Path(temp_dir) / "test_kg.db"
    yield db_path
    shutil.rmtree(temp_dir)


@pytest.fixture
def kg(temp_db):
    """Create a KnowledgeGraph instance."""
    return KnowledgeGraph(db_path=temp_db)


@pytest.fixture
def cleanup(kg):
    """Create a PatternCleanup instance."""
    return PatternCleanup(kg)


class TestPatternDecay:
    """Test automatic confidence decay."""
    
    def test_decay_old_application_patterns(self, kg, cleanup):
        """Application patterns should decay after 30 days."""
        # Add old application pattern
        old_date = (datetime.now() - timedelta(days=45)).isoformat()
        kg.add_pattern(
            pattern_id="app_old_1",
            title="Old Application Pattern",
            content="Test content",
            pattern_type=PatternType.WORKFLOW,
            confidence=1.0,
            scope="application",
            namespaces=["KSESSIONS"]
        )
        
        # Manually set old access time
        conn = sqlite3.connect(kg.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE patterns SET last_accessed = ? WHERE pattern_id = ?
        """, (old_date, "app_old_1"))
        conn.commit()
        conn.close()
        
        # Apply decay
        stats = cleanup.apply_automatic_decay()
        
        # Should have decayed
        assert stats.decayed_count >= 1
        
        # Check new confidence
        pattern = kg.get_pattern("app_old_1")
        assert pattern is not None
        assert pattern.confidence < 1.0
    
    def test_never_decay_generic_patterns(self, kg, cleanup):
        """Generic patterns should NEVER decay."""
        # Add old generic pattern
        old_date = (datetime.now() - timedelta(days=90)).isoformat()
        kg.add_pattern(
            pattern_id="gen_old_1",
            title="Old Generic Pattern",
            content="CORTEX core intelligence",
            pattern_type=PatternType.PRINCIPLE,
            confidence=1.0,
            scope="generic",
            namespaces=["CORTEX-core"]
        )
        
        # Manually set very old access time
        conn = sqlite3.connect(kg.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE patterns SET last_accessed = ? WHERE pattern_id = ?
        """, (old_date, "gen_old_1"))
        conn.commit()
        conn.close()
        
        # Apply decay with protection
        stats = cleanup.apply_automatic_decay(protect_generic=True)
        
        # Generic pattern should be unchanged
        pattern = kg.get_pattern("gen_old_1")
        assert pattern is not None
        assert pattern.confidence == 1.0  # No decay
    
    def test_never_decay_cortex_core_namespace(self, kg, cleanup):
        """Patterns in CORTEX-core namespace should NEVER decay."""
        # Add old pattern with CORTEX-core namespace
        old_date = (datetime.now() - timedelta(days=120)).isoformat()
        kg.add_pattern(
            pattern_id="core_old_1",
            title="Core Pattern",
            content="Essential CORTEX logic",
            pattern_type=PatternType.PRINCIPLE,
            confidence=1.0,
            scope="application",  # Even if scope is application
            namespaces=["CORTEX-core", "KSESSIONS"]  # CORTEX-core protects it
        )
        
        # Set very old access time
        conn = sqlite3.connect(kg.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE patterns SET last_accessed = ? WHERE pattern_id = ?
        """, (old_date, "core_old_1"))
        conn.commit()
        conn.close()
        
        # Apply decay
        stats = cleanup.apply_automatic_decay()
        
        # Should not decay (CORTEX-core protection)
        pattern = kg.get_pattern("core_old_1")
        assert pattern is not None
        assert pattern.confidence == 1.0
    
    def test_delete_below_minimum_confidence(self, kg, cleanup):
        """Patterns below minimum confidence should be deleted."""
        # Add low confidence pattern
        kg.add_pattern(
            pattern_id="low_conf_1",
            title="Low Confidence Pattern",
            content="Weak pattern",
            pattern_type=PatternType.WORKFLOW,
            confidence=0.25,  # Below 0.3 threshold
            scope="application",
            namespaces=["KSESSIONS"]
        )
        
        # Apply decay (should delete immediately)
        stats = cleanup.apply_automatic_decay()
        
        # Should be deleted
        assert stats.deleted_count >= 1
        pattern = kg.get_pattern("low_conf_1")
        assert pattern is None
    
    def test_pinned_patterns_protected(self, kg, cleanup):
        """Pinned patterns should never decay."""
        # Add old pattern
        old_date = (datetime.now() - timedelta(days=90)).isoformat()
        kg.add_pattern(
            pattern_id="pinned_1",
            title="Pinned Pattern",
            content="Important pattern",
            pattern_type=PatternType.WORKFLOW,
            confidence=1.0,
            scope="application",
            namespaces=["KSESSIONS"]
        )
        
        # Pin it
        kg.pin_pattern("pinned_1")
        
        # Set old access time
        conn = sqlite3.connect(kg.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE patterns SET last_accessed = ? WHERE pattern_id = ?
        """, (old_date, "pinned_1"))
        conn.commit()
        conn.close()
        
        # Apply decay
        stats = cleanup.apply_automatic_decay()
        
        # Should not decay (pinned)
        pattern = kg.get_pattern("pinned_1")
        assert pattern is not None
        assert pattern.confidence == 1.0


class TestPatternConsolidation:
    """Test pattern consolidation (merge similar patterns)."""
    
    def test_consolidate_similar_patterns(self, kg, cleanup):
        """Similar patterns should be merged."""
        # Add two very similar patterns
        kg.add_pattern(
            pattern_id="similar_1",
            title="Button Workflow",
            content="Add a button test first TDD RED GREEN REFACTOR",
            pattern_type=PatternType.WORKFLOW,
            confidence=0.9,
            scope="application",
            namespaces=["KSESSIONS"]
        )
        
        kg.add_pattern(
            pattern_id="similar_2",
            title="Button Workflow",
            content="Add a button test first TDD RED GREEN REFACTOR",
            pattern_type=PatternType.WORKFLOW,
            confidence=0.85,
            scope="application",
            namespaces=["KSESSIONS"]
        )
        
        # Test similarity calculation
        sim = cleanup._calculate_similarity(
            "Button Workflow",
            "Add a button test first TDD RED GREEN REFACTOR",
            "Button Workflow",
            "Add a button test first TDD RED GREEN REFACTOR"
        )
        print(f"Similarity: {sim}")
        
        # Consolidate
        stats = cleanup.consolidate_similar_patterns(namespace="KSESSIONS")
        
        # Should consolidate at least one
        assert stats.consolidated_count >= 1
        
        # One pattern should remain
        patterns = kg.get_patterns_by_namespace("KSESSIONS")
        assert len(patterns) == 1
    
    def test_never_consolidate_generic(self, kg, cleanup):
        """Generic patterns should NEVER be consolidated."""
        # Add two similar generic patterns
        kg.add_pattern(
            pattern_id="gen_similar_1",
            title="TDD Workflow",
            content="Test-driven development RED GREEN REFACTOR",
            pattern_type=PatternType.PRINCIPLE,
            confidence=1.0,
            scope="generic",
            namespaces=["CORTEX-core"]
        )
        
        kg.add_pattern(
            pattern_id="gen_similar_2",
            title="TDD Process",
            content="Test-driven development RED GREEN REFACTOR cycle",
            pattern_type=PatternType.PRINCIPLE,
            confidence=1.0,
            scope="generic",
            namespaces=["CORTEX-core"]
        )
        
        # Try to consolidate
        stats = cleanup.consolidate_similar_patterns()
        
        # Should NOT consolidate any (generic protection)
        assert stats.consolidated_count == 0
        
        # Both should still exist
        assert kg.get_pattern("gen_similar_1") is not None
        assert kg.get_pattern("gen_similar_2") is not None
    
    def test_dry_run_consolidation(self, kg, cleanup):
        """Dry run should report without making changes."""
        # Add similar patterns
        kg.add_pattern(
            pattern_id="dry_1",
            title="Export Workflow",
            content="PDF export feature workflow pattern",
            pattern_type=PatternType.WORKFLOW,
            confidence=0.9,
            scope="application",
            namespaces=["KSESSIONS"]
        )
        
        kg.add_pattern(
            pattern_id="dry_2",
            title="Export Pattern",
            content="PDF export feature workflow pattern design",
            pattern_type=PatternType.WORKFLOW,
            confidence=0.85,
            scope="application",
            namespaces=["KSESSIONS"]
        )
        
        # Dry run
        stats = cleanup.consolidate_similar_patterns(namespace="KSESSIONS", dry_run=True)
        
        # Should report consolidation
        assert stats.consolidated_count >= 1
        
        # But patterns should still exist (no actual changes)
        assert kg.get_pattern("dry_1") is not None
        assert kg.get_pattern("dry_2") is not None


class TestStalePatternRemoval:
    """Test removal of stale patterns."""
    
    def test_remove_stale_patterns(self, kg, cleanup):
        """Old unused patterns should be removed."""
        # Add stale pattern (90+ days old, low confidence)
        old_date = (datetime.now() - timedelta(days=100)).isoformat()
        kg.add_pattern(
            pattern_id="stale_1",
            title="Stale Pattern",
            content="Old unused pattern",
            pattern_type=PatternType.WORKFLOW,
            confidence=0.25,
            scope="application",
            namespaces=["KSESSIONS"]
        )
        
        # Set old access time
        conn = sqlite3.connect(kg.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE patterns SET last_accessed = ? WHERE pattern_id = ?
        """, (old_date, "stale_1"))
        conn.commit()
        conn.close()
        
        # Remove stale
        stats = cleanup.remove_stale_patterns(stale_days=90)
        
        # Should delete
        assert stats.deleted_count >= 1
        assert kg.get_pattern("stale_1") is None
    
    def test_keep_high_confidence_stale(self, kg, cleanup):
        """Stale patterns with high confidence should be kept."""
        # Add old pattern with high confidence
        old_date = (datetime.now() - timedelta(days=100)).isoformat()
        kg.add_pattern(
            pattern_id="stale_high_1",
            title="Old But Strong",
            content="Old pattern with high confidence",
            pattern_type=PatternType.WORKFLOW,
            confidence=0.95,  # High confidence
            scope="application",
            namespaces=["KSESSIONS"]
        )
        
        # Set old access time
        conn = sqlite3.connect(kg.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE patterns SET last_accessed = ? WHERE pattern_id = ?
        """, (old_date, "stale_high_1"))
        conn.commit()
        conn.close()
        
        # Try to remove stale
        stats = cleanup.remove_stale_patterns(stale_days=90)
        
        # Should NOT delete (high confidence protection)
        pattern = kg.get_pattern("stale_high_1")
        assert pattern is not None


class TestCleanupRecommendations:
    """Test cleanup recommendation system."""
    
    def test_get_recommendations(self, kg, cleanup):
        """Should provide cleanup recommendations."""
        # Add various patterns
        kg.add_pattern(
            pattern_id="rec_1",
            title="Pattern 1",
            content="Test",
            pattern_type=PatternType.WORKFLOW,
            confidence=1.0,
            scope="generic",
            namespaces=["CORTEX-core"]
        )
        
        old_date = (datetime.now() - timedelta(days=45)).isoformat()
        kg.add_pattern(
            pattern_id="rec_2",
            title="Pattern 2",
            content="Test",
            pattern_type=PatternType.WORKFLOW,
            confidence=0.5,
            scope="application",
            namespaces=["KSESSIONS"]
        )
        
        conn = sqlite3.connect(kg.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE patterns SET last_accessed = ? WHERE pattern_id = ?
        """, (old_date, "rec_2"))
        conn.commit()
        conn.close()
        
        # Get recommendations
        recs = cleanup.get_cleanup_recommendations()
        
        # Should have counts
        assert 'total_patterns' in recs
        assert 'generic_patterns' in recs
        assert 'application_patterns' in recs
        assert 'decay_candidates' in recs
        assert recs['total_patterns'] == 2
        assert recs['generic_patterns'] == 1
        assert recs['application_patterns'] == 1
        assert recs['decay_candidates'] >= 1


class TestDatabaseOptimization:
    """Test database optimization."""
    
    def test_optimize_database(self, kg, cleanup):
        """Database optimization should succeed."""
        # Add some patterns
        for i in range(10):
            kg.add_pattern(
                pattern_id=f"opt_{i}",
                title=f"Pattern {i}",
                content=f"Content {i}",
                pattern_type=PatternType.WORKFLOW,
                confidence=0.9,
                scope="application",
                namespaces=["KSESSIONS"]
            )
        
        # Delete half
        for i in range(5):
            kg.delete_pattern(f"opt_{i}")
        
        # Optimize
        result = cleanup.optimize_database()
        
        # Should succeed
        assert result is True
