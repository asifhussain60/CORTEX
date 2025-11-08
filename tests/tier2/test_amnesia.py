"""
Tests for Enhanced Amnesia System.

Validates:
- Namespace-scoped deletion
- Generic pattern protection (NEVER deleted)
- CORTEX-core namespace protection (PERMANENT)
- Multi-namespace safety (only delete when all namespaces cleared)
- Safety thresholds and confirmations
"""

import pytest
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
import tempfile
import shutil
import json

from src.tier2.knowledge_graph import KnowledgeGraph, PatternType
from src.tier2.amnesia import EnhancedAmnesia, AmnesiaStats


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
def amnesia(kg):
    """Create an EnhancedAmnesia instance."""
    return EnhancedAmnesia(kg)


class TestNamespaceDeletion:
    """Test namespace-scoped deletion."""
    
    def test_delete_by_namespace(self, kg, amnesia):
        """Should delete patterns in specific namespace."""
        # Add patterns in different namespaces
        kg.add_pattern(
            pattern_id="ks_1",
            title="KSESSIONS Pattern",
            content="Test",
            pattern_type=PatternType.WORKFLOW,
            confidence=0.9,
            scope="application",
            namespaces=["KSESSIONS"]
        )
        
        kg.add_pattern(
            pattern_id="noor_1",
            title="NOOR Pattern",
            content="Test",
            pattern_type=PatternType.WORKFLOW,
            confidence=0.9,
            scope="application",
            namespaces=["NOOR"]
        )
        
        # Delete KSESSIONS namespace
        stats = amnesia.delete_by_namespace("KSESSIONS", require_confirmation=False)
        
        # KSESSIONS should be deleted
        assert stats.patterns_deleted == 1
        assert kg.get_pattern("ks_1") is None
        
        # NOOR should remain
        assert kg.get_pattern("noor_1") is not None
    
    def test_block_cortex_core_deletion(self, kg, amnesia):
        """CORTEX-core namespace deletion should be FORBIDDEN."""
        with pytest.raises(ValueError, match="FORBIDDEN.*CORTEX-core"):
            amnesia.delete_by_namespace("CORTEX-core")
    
    def test_never_delete_generic_patterns(self, kg, amnesia):
        """Generic patterns should NEVER be deleted."""
        # Add generic pattern in namespace
        kg.add_pattern(
            pattern_id="gen_ks_1",
            title="Generic Pattern",
            content="CORTEX core intelligence",
            pattern_type=PatternType.PRINCIPLE,
            confidence=1.0,
            scope="cortex",
            namespaces=["CORTEX-core", "KSESSIONS"]  # Even if KSESSIONS namespace
        )
        
        # Try to delete KSESSIONS
        stats = amnesia.delete_by_namespace("KSESSIONS", require_confirmation=False)
        
        # Generic should be protected
        assert stats.protected_count >= 1
        assert kg.get_pattern("gen_ks_1") is not None
        assert kg.get_pattern("gen_ks_1").confidence == 1.0
    
    def test_multi_namespace_safety(self, kg, amnesia):
        """Multi-namespace patterns only deleted when all namespaces cleared."""
        # Add pattern in multiple namespaces
        kg.add_pattern(
            pattern_id="multi_1",
            title="Multi-namespace Pattern",
            content="Shared pattern",
            pattern_type=PatternType.WORKFLOW,
            confidence=0.9,
            scope="application",
            namespaces=["KSESSIONS", "NOOR"]
        )
        
        # Delete KSESSIONS namespace
        stats = amnesia.delete_by_namespace("KSESSIONS", require_confirmation=False)
        
        # Pattern should remain (still in NOOR)
        pattern = kg.get_pattern("multi_1")
        assert pattern is not None
        assert "NOOR" in pattern.namespaces
        assert "KSESSIONS" not in pattern.namespaces
        
        # Should be counted as protected
        assert stats.protected_count >= 1
        
        # Now delete NOOR (last namespace) - use bypass_safety since it's 100% of patterns
        stats2 = amnesia.delete_by_namespace("NOOR", require_confirmation=False, bypass_safety=True)
        
        # Now it should be deleted
        assert stats2.patterns_deleted >= 1
        assert kg.get_pattern("multi_1") is None
    
    def test_dry_run_namespace_deletion(self, kg, amnesia):
        """Dry run should report without deleting."""
        # Add pattern
        kg.add_pattern(
            pattern_id="dry_ns_1",
            title="Dry Run Pattern",
            content="Test",
            pattern_type=PatternType.WORKFLOW,
            confidence=0.9,
            scope="application",
            namespaces=["KSESSIONS"]
        )
        
        # Dry run deletion - bypass safety for test
        stats = amnesia.delete_by_namespace("KSESSIONS", require_confirmation=False, dry_run=True, bypass_safety=True)
        
        # Should report deletion
        assert stats.patterns_deleted >= 1
        
        # But pattern should still exist
        assert kg.get_pattern("dry_ns_1") is not None


class TestConfidenceDeletion:
    """Test confidence-based deletion."""
    
    def test_delete_by_confidence(self, kg, amnesia):
        """Should delete patterns below confidence threshold."""
        # Add low and high confidence patterns
        kg.add_pattern(
            pattern_id="low_conf_1",
            title="Low Confidence",
            content="Weak pattern",
            pattern_type=PatternType.WORKFLOW,
            confidence=0.25,
            scope="application",
            namespaces=["KSESSIONS"]
        )
        
        kg.add_pattern(
            pattern_id="high_conf_1",
            title="High Confidence",
            content="Strong pattern",
            pattern_type=PatternType.WORKFLOW,
            confidence=0.95,
            scope="application",
            namespaces=["KSESSIONS"]
        )
        
        # Delete low confidence
        stats = amnesia.delete_by_confidence(max_confidence=0.5)
        
        # Low should be deleted
        assert stats.patterns_deleted >= 1
        assert kg.get_pattern("low_conf_1") is None
        
        # High should remain
        assert kg.get_pattern("high_conf_1") is not None
    
    def test_confidence_deletion_protects_generic(self, kg, amnesia):
        """Generic patterns protected even with low confidence."""
        # Add low confidence generic pattern
        kg.add_pattern(
            pattern_id="gen_low_1",
            title="Generic Low Confidence",
            content="Core intelligence",
            pattern_type=PatternType.PRINCIPLE,
            confidence=0.2,  # Very low
            scope="cortex",
            namespaces=["CORTEX-core"]
        )
        
        # Try to delete low confidence
        stats = amnesia.delete_by_confidence(max_confidence=0.5, protect_generic=True)
        
        # Generic should be protected
        assert kg.get_pattern("gen_low_1") is not None


class TestAgeDeletion:
    """Test age-based deletion."""
    
    def test_delete_by_age(self, kg, amnesia):
        """Should delete old unused patterns."""
        # Add old pattern
        old_date = (datetime.now() - timedelta(days=100)).isoformat()
        kg.add_pattern(
            pattern_id="old_1",
            title="Old Pattern",
            content="Ancient wisdom",
            pattern_type=PatternType.WORKFLOW,
            confidence=0.9,
            scope="application",
            namespaces=["KSESSIONS"]
        )
        
        # Set old access time
        conn = sqlite3.connect(kg.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE patterns SET last_accessed = ? WHERE pattern_id = ?
        """, (old_date, "old_1"))
        conn.commit()
        conn.close()
        
        # Delete patterns >90 days old
        stats = amnesia.delete_by_age(days_inactive=90)
        
        # Should be deleted
        assert stats.patterns_deleted >= 1
        assert kg.get_pattern("old_1") is None
    
    def test_age_deletion_protects_generic(self, kg, amnesia):
        """Generic patterns protected regardless of age."""
        # Add very old generic pattern
        ancient_date = (datetime.now() - timedelta(days=365)).isoformat()
        kg.add_pattern(
            pattern_id="gen_ancient_1",
            title="Ancient Generic",
            content="Timeless wisdom",
            pattern_type=PatternType.PRINCIPLE,
            confidence=1.0,
            scope="cortex",
            namespaces=["CORTEX-core"]
        )
        
        # Set very old access time
        conn = sqlite3.connect(kg.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE patterns SET last_accessed = ? WHERE pattern_id = ?
        """, (ancient_date, "gen_ancient_1"))
        conn.commit()
        conn.close()
        
        # Try to delete old patterns
        stats = amnesia.delete_by_age(days_inactive=30, protect_generic=True)
        
        # Generic should remain
        assert kg.get_pattern("gen_ancient_1") is not None


class TestScopeClear:
    """Test clearing entire application scope."""
    
    def test_clear_application_scope(self, kg, amnesia):
        """Should clear all application patterns."""
        # Add generic and application patterns
        kg.add_pattern(
            pattern_id="gen_scope_1",
            title="Generic",
            content="Core",
            pattern_type=PatternType.PRINCIPLE,
            confidence=1.0,
            scope="cortex",
            namespaces=["CORTEX-core"]
        )
        
        kg.add_pattern(
            pattern_id="app_scope_1",
            title="Application",
            content="App specific",
            pattern_type=PatternType.WORKFLOW,
            confidence=0.9,
            scope="application",
            namespaces=["KSESSIONS"]
        )
        
        kg.add_pattern(
            pattern_id="app_scope_2",
            title="Application 2",
            content="App specific",
            pattern_type=PatternType.WORKFLOW,
            confidence=0.85,
            scope="application",
            namespaces=["NOOR"]
        )
        
        # Clear all applications (with confirmation)
        stats = amnesia.clear_application_scope(
            confirmation_code="DELETE_ALL_APPLICATIONS"
        )
        
        # Applications should be deleted
        assert stats.patterns_deleted >= 2
        assert kg.get_pattern("app_scope_1") is None
        assert kg.get_pattern("app_scope_2") is None
        
        # Generic should remain
        assert kg.get_pattern("gen_scope_1") is not None
    
    def test_scope_clear_requires_confirmation(self, kg, amnesia):
        """Scope clear should require confirmation code."""
        with pytest.raises(ValueError, match="SAFETY BLOCK"):
            amnesia.clear_application_scope()  # No confirmation
        
        with pytest.raises(ValueError, match="SAFETY BLOCK"):
            amnesia.clear_application_scope(confirmation_code="WRONG_CODE")
    
    def test_scope_clear_dry_run(self, kg, amnesia):
        """Dry run scope clear should report without deleting."""
        # Add application patterns
        kg.add_pattern(
            pattern_id="dry_scope_1",
            title="Dry Scope",
            content="Test",
            pattern_type=PatternType.WORKFLOW,
            confidence=0.9,
            scope="application",
            namespaces=["KSESSIONS"]
        )
        
        # Dry run
        stats = amnesia.clear_application_scope(dry_run=True)
        
        # Should report deletion
        assert stats.patterns_deleted >= 1
        
        # But pattern should exist
        assert kg.get_pattern("dry_scope_1") is not None


class TestSafetyProtections:
    """Test safety thresholds and protections."""
    
    def test_safety_threshold_prevents_mass_deletion(self, kg, amnesia):
        """Should prevent deleting >50% of patterns."""
        # Add many patterns
        for i in range(100):
            kg.add_pattern(
                pattern_id=f"safety_{i}",
                title=f"Pattern {i}",
                content="Test",
                pattern_type=PatternType.WORKFLOW,
                confidence=0.9,
                scope="application",
                namespaces=["KSESSIONS"]
            )
        
        # Add a few in different namespace
        for i in range(10):
            kg.add_pattern(
                pattern_id=f"safety_noor_{i}",
                title=f"NOOR {i}",
                content="Test",
                pattern_type=PatternType.WORKFLOW,
                confidence=0.9,
                scope="application",
                namespaces=["NOOR"]
            )
        
        # Try to delete KSESSIONS (>50% of patterns) - should fail
        stats = amnesia.delete_by_namespace("KSESSIONS", require_confirmation=False)
        
        # Should have error logged (caught exception)
        assert len(stats.errors) > 0
        assert "SAFETY ABORT" in stats.errors[0]
    
    def test_cortex_core_namespace_always_protected(self, kg, amnesia):
        """CORTEX-core namespace patterns can NEVER be deleted."""
        # Add pattern with CORTEX-core namespace
        kg.add_pattern(
            pattern_id="core_protected_1",
            title="Core Pattern",
            content="Essential intelligence",
            pattern_type=PatternType.PRINCIPLE,
            confidence=0.1,  # Even with low confidence
            scope="application",  # Even if scope is application
            namespaces=["CORTEX-core", "KSESSIONS"]
        )
        
        # Try various deletion methods
        stats1 = amnesia.delete_by_confidence(max_confidence=0.5)
        assert kg.get_pattern("core_protected_1") is not None
        
        stats2 = amnesia.delete_by_namespace("KSESSIONS", require_confirmation=False)
        pattern = kg.get_pattern("core_protected_1")
        assert pattern is not None
        # Should only remove KSESSIONS namespace
        assert "CORTEX-core" in pattern.namespaces


class TestDeletionPreview:
    """Test deletion preview functionality."""
    
    def test_get_deletion_preview(self, kg, amnesia):
        """Should preview deletions without making changes."""
        # Add patterns - need enough to avoid safety threshold
        kg.add_pattern(
            pattern_id="preview_gen_1",
            title="Generic",
            content="Core",
            pattern_type=PatternType.PRINCIPLE,
            confidence=1.0,
            scope="cortex",
            namespaces=["CORTEX-core"]
        )
        
        # Add more application patterns to avoid safety threshold
        for i in range(5):
            kg.add_pattern(
                pattern_id=f"preview_app_{i}",
                title=f"Application {i}",
                content="App",
                pattern_type=PatternType.WORKFLOW,
                confidence=0.5,
                scope="application",
                namespaces=["KSESSIONS"]
            )
        
        # Preview namespace deletion
        preview = amnesia.get_deletion_preview(namespace="KSESSIONS")
        
        # Debug: print preview
        print(f"Preview: {preview}")
        
        # Should show counts
        assert 'total_patterns' in preview
        assert 'would_delete' in preview
        assert 'would_protect' in preview
        assert preview['total_patterns'] == 6
        assert preview['would_delete'] >= 1
        # Generic pattern is NOT in KSESSIONS namespace, so wouldn't be protected by namespace filter
        # The filter only shows patterns IN the namespace, and generic one is in CORTEX-core only
        assert preview['generic_patterns'] >= 1  # Check generic exists separately
    
    def test_preview_with_confidence_filter(self, kg, amnesia):
        """Preview with confidence threshold."""
        # Add patterns
        kg.add_pattern(
            pattern_id="preview_low_1",
            title="Low",
            content="Weak",
            pattern_type=PatternType.WORKFLOW,
            confidence=0.2,
            scope="application",
            namespaces=["KSESSIONS"]
        )
        
        kg.add_pattern(
            pattern_id="preview_high_1",
            title="High",
            content="Strong",
            pattern_type=PatternType.WORKFLOW,
            confidence=0.95,
            scope="application",
            namespaces=["KSESSIONS"]
        )
        
        # Preview low confidence deletion
        preview = amnesia.get_deletion_preview(max_confidence=0.5)
        
        # Should show low confidence candidates
        assert preview['would_delete'] >= 1


class TestDeletionLogging:
    """Test deletion audit trail."""
    
    def test_deletion_log_recorded(self, kg, amnesia):
        """Deletions should be logged."""
        # Add pattern
        kg.add_pattern(
            pattern_id="logged_1",
            title="Logged Pattern",
            content="Test",
            pattern_type=PatternType.WORKFLOW,
            confidence=0.9,
            scope="application",
            namespaces=["KSESSIONS"]
        )
        
        # Delete with logging - bypass safety for test
        stats = amnesia.delete_by_namespace("KSESSIONS", require_confirmation=False, bypass_safety=True)
        
        # Should have deletion log
        assert len(stats.deletion_log) >= 1
        log_entry = stats.deletion_log[0]
        assert 'pattern_id' in log_entry
        assert 'title' in log_entry
        assert 'action' in log_entry
    
    def test_export_deletion_log(self, kg, amnesia, temp_db):
        """Should export deletion log to file."""
        # Add and delete pattern
        kg.add_pattern(
            pattern_id="export_log_1",
            title="Export Log Pattern",
            content="Test",
            pattern_type=PatternType.WORKFLOW,
            confidence=0.2,
            scope="application",
            namespaces=["KSESSIONS"]
        )
        
        amnesia.delete_by_confidence(max_confidence=0.5)
        
        # Export log
        log_path = temp_db.parent / "deletion_log.json"
        result = amnesia.export_deletion_log(log_path)
        
        # Should succeed
        assert result is True
        assert log_path.exists()
        
        # Verify content
        with open(log_path, 'r') as f:
            log_data = json.load(f)
        assert isinstance(log_data, list)

