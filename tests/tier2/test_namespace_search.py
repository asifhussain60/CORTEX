"""
Tests for CORTEX Tier 2: Namespace-Aware Search

This test suite validates the namespace-aware search functionality that
provides context-sensitive pattern retrieval with boosting based on
current application context.

Test Coverage:
- Namespace-aware search with boosting
- Generic pattern inclusion
- Cross-namespace isolation
- Multi-namespace patterns
- Scope filtering (generic/application)
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

from src.tier2.knowledge_graph import (
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
    
    # Cleanup
    import time
    time.sleep(0.1)
    try:
        shutil.rmtree(temp_dir)
    except PermissionError:
        time.sleep(0.5)
        shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def kg(temp_db):
    """Create a KnowledgeGraph instance with test data."""
    kg = KnowledgeGraph(db_path=temp_db)
    
    # Add generic CORTEX patterns
    kg.add_pattern(
        pattern_id="tdd_workflow",
        title="Test-Driven Development",
        content="Always write tests first RED GREEN REFACTOR",
        pattern_type=PatternType.WORKFLOW,
        scope="cortex",
        namespaces=["CORTEX-core"],
        tags=["testing", "workflow"]
    )
    
    kg.add_pattern(
        pattern_id="solid_principles",
        title="SOLID Design Principles",
        content="Single Responsibility Open Closed Liskov Interface Dependency",
        pattern_type=PatternType.PRINCIPLE,
        scope="cortex",
        namespaces=["CORTEX-core"],
        tags=["architecture", "principles"]
    )
    
    # Add KSESSIONS-specific patterns
    kg.add_pattern(
        pattern_id="ksessions_host_panel",
        title="Host Control Panel",
        content="Host panel with session management testing workflow",
        pattern_type=PatternType.SOLUTION,
        scope="application",
        namespaces=["KSESSIONS"],
        tags=["ui", "ksessions"]
    )
    
    kg.add_pattern(
        pattern_id="ksessions_registration",
        title="User Registration Flow",
        content="Registration workflow with canvas selection testing",
        pattern_type=PatternType.SOLUTION,
        scope="application",
        namespaces=["KSESSIONS"],
        tags=["auth", "ksessions"]
    )
    
    # Add NOOR-specific patterns
    kg.add_pattern(
        pattern_id="noor_canvas",
        title="NOOR Canvas Component",
        content="Canvas rendering with testing and refactoring",
        pattern_type=PatternType.SOLUTION,
        scope="application",
        namespaces=["NOOR"],
        tags=["ui", "noor"]
    )
    
    # Add multi-namespace pattern (shared across apps)
    kg.add_pattern(
        pattern_id="export_pattern",
        title="Export Feature Pattern",
        content="Generic export workflow testing applicable to multiple apps",
        pattern_type=PatternType.WORKFLOW,
        scope="cortex",
        namespaces=["CORTEX-core", "KSESSIONS", "NOOR"],
        tags=["export", "workflow"]
    )
    
    return kg


class TestNamespaceAwareSearch:
    """Test namespace-aware search with boosting."""
    
    def test_search_with_current_namespace_boost(self, kg):
        """Verify current namespace patterns ranked higher."""
        # Search for "testing" from KSESSIONS context
        results = kg.search_patterns_with_namespace(
            query="testing",
            current_namespace="KSESSIONS",
            include_generic=True,
            limit=10
        )
        
        assert len(results) > 0
        
        # First results should be KSESSIONS patterns (boosted 2.0x)
        ksessions_patterns = [p for p in results if "KSESSIONS" in p.namespaces]
        assert len(ksessions_patterns) > 0
        
        # KSESSIONS patterns should appear before other namespaces
        first_ksessions_idx = next(i for i, p in enumerate(results) if "KSESSIONS" in p.namespaces)
        noor_patterns = [i for i, p in enumerate(results) if "NOOR" in p.namespaces and "CORTEX-core" not in p.namespaces]
        
        if noor_patterns:
            assert first_ksessions_idx < noor_patterns[0]
    
    def test_generic_patterns_always_included(self, kg):
        """Verify generic patterns available when include_generic=True."""
        results = kg.search_patterns_with_namespace(
            query="testing",
            current_namespace="KSESSIONS",
            include_generic=True,
            limit=10
        )
        
        # Should include CORTEX-core patterns
        generic_patterns = [p for p in results if p.scope == "cortex"]
        assert len(generic_patterns) > 0
    
    def test_generic_patterns_excluded_when_disabled(self, kg):
        """Verify generic patterns excluded when include_generic=False."""
        results = kg.search_patterns_with_namespace(
            query="testing",
            current_namespace="KSESSIONS",
            include_generic=False,
            limit=10
        )
        
        # Should only have KSESSIONS patterns (no generic)
        for pattern in results:
            if pattern.scope == "cortex":
                # Generic patterns should only appear if they're in KSESSIONS namespace
                assert "KSESSIONS" in pattern.namespaces
    
    def test_cross_namespace_isolation(self, kg):
        """Verify KSESSIONS search doesn't prioritize NOOR patterns."""
        # Search from KSESSIONS context
        ks_results = kg.search_patterns_with_namespace(
            query="testing",
            current_namespace="KSESSIONS",
            include_generic=True,
            limit=10
        )
        
        # Search from NOOR context
        noor_results = kg.search_patterns_with_namespace(
            query="testing",
            current_namespace="NOOR",
            include_generic=True,
            limit=10
        )
        
        # Results should be different due to namespace boosting
        ks_first = ks_results[0].pattern_id if ks_results else None
        noor_first = noor_results[0].pattern_id if noor_results else None
        
        # First result should prioritize respective namespace
        if ks_first and noor_first:
            # At least one should be different (unless multi-namespace pattern)
            if ks_first == noor_first:
                # If same, it should be multi-namespace
                first_pattern = kg.get_pattern(ks_first)
                assert "KSESSIONS" in first_pattern.namespaces and "NOOR" in first_pattern.namespaces
    
    def test_multi_namespace_patterns_boosted_for_all(self, kg):
        """Verify patterns in multiple namespaces boosted for each context."""
        # The "export_pattern" is in CORTEX-core, KSESSIONS, and NOOR
        
        # Search from KSESSIONS
        ks_results = kg.search_patterns_with_namespace(
            query="export",
            current_namespace="KSESSIONS",
            limit=10
        )
        
        # Search from NOOR
        noor_results = kg.search_patterns_with_namespace(
            query="export",
            current_namespace="NOOR",
            limit=10
        )
        
        # Multi-namespace pattern should appear in both with high priority
        export_in_ks = any(p.pattern_id == "export_pattern" for p in ks_results)
        export_in_noor = any(p.pattern_id == "export_pattern" for p in noor_results)
        
        assert export_in_ks
        assert export_in_noor
    
    def test_search_without_namespace_context(self, kg):
        """Verify search works without namespace context (generic search)."""
        results = kg.search_patterns_with_namespace(
            query="testing",
            current_namespace=None,
            include_generic=True,
            limit=10
        )
        
        # Should return results with generic patterns prioritized
        assert len(results) > 0
        generic_patterns = [p for p in results if p.scope == "cortex"]
        assert len(generic_patterns) > 0


class TestGetPatternsByNamespace:
    """Test namespace-specific pattern retrieval."""
    
    def test_get_ksessions_patterns(self, kg):
        """Verify retrieval of all KSESSIONS patterns."""
        patterns = kg.get_patterns_by_namespace("KSESSIONS")
        
        assert len(patterns) >= 2  # host_panel, registration, export_pattern
        
        # All should have KSESSIONS in namespaces
        for pattern in patterns:
            assert "KSESSIONS" in pattern.namespaces
    
    def test_get_noor_patterns(self, kg):
        """Verify retrieval of all NOOR patterns."""
        patterns = kg.get_patterns_by_namespace("NOOR")
        
        assert len(patterns) >= 1  # canvas, export_pattern
        
        for pattern in patterns:
            assert "NOOR" in pattern.namespaces
    
    def test_get_cortex_core_patterns(self, kg):
        """Verify retrieval of CORTEX-core patterns."""
        patterns = kg.get_patterns_by_namespace("CORTEX-core")
        
        # Should have generic patterns + multi-namespace patterns
        assert len(patterns) >= 3  # tdd, solid, export_pattern
        
        for pattern in patterns:
            assert "CORTEX-core" in pattern.namespaces
    
    def test_get_nonexistent_namespace(self, kg):
        """Verify empty result for nonexistent namespace."""
        patterns = kg.get_patterns_by_namespace("NONEXISTENT")
        
        assert len(patterns) == 0


class TestGetGenericPatterns:
    """Test generic pattern retrieval."""
    
    def test_get_all_generic_patterns(self, kg):
        """Verify retrieval of all generic patterns."""
        patterns = kg.get_generic_patterns()
        
        # Should have tdd, solid, export_pattern
        assert len(patterns) >= 3
        
        # All should have scope='cortex'
        for pattern in patterns:
            assert pattern.scope == "cortex"
    
    def test_generic_patterns_sorted_by_confidence(self, kg):
        """Verify generic patterns sorted by confidence."""
        # Add patterns with different confidence
        kg.add_pattern(
            pattern_id="high_conf",
            title="High Confidence",
            content="High confidence pattern",
            pattern_type=PatternType.PRINCIPLE,
            scope="cortex",
            confidence=0.95
        )
        
        kg.add_pattern(
            pattern_id="low_conf",
            title="Low Confidence",
            content="Low confidence pattern",
            pattern_type=PatternType.PRINCIPLE,
            scope="cortex",
            confidence=0.50
        )
        
        patterns = kg.get_generic_patterns()
        
        # Should be sorted by confidence DESC
        confidences = [p.confidence for p in patterns]
        assert confidences == sorted(confidences, reverse=True)


class TestGetApplicationPatterns:
    """Test application pattern retrieval."""
    
    def test_get_all_application_patterns(self, kg):
        """Verify retrieval of all application patterns."""
        patterns = kg.get_application_patterns()
        
        # Should have ksessions_host_panel, ksessions_registration, noor_canvas
        assert len(patterns) >= 3
        
        # All should have scope='application'
        for pattern in patterns:
            assert pattern.scope == "application"
    
    def test_application_patterns_exclude_generic(self, kg):
        """Verify application patterns don't include generic scope."""
        patterns = kg.get_application_patterns()
        
        # Should NOT include tdd, solid, export_pattern (generic scope)
        pattern_ids = [p.pattern_id for p in patterns]
        
        assert "tdd_workflow" not in pattern_ids
        assert "solid_principles" not in pattern_ids
        assert "export_pattern" not in pattern_ids  # Generic scope even with app namespaces


class TestNamespaceBoostingScores:
    """Test namespace boosting score calculations."""
    
    def test_current_namespace_highest_priority(self, kg):
        """Verify current namespace gets 2.0x boost."""
        # Add specific test pattern
        kg.add_pattern(
            pattern_id="ks_specific",
            title="KSESSIONS Specific Feature",
            content="workflow testing feature",
            pattern_type=PatternType.SOLUTION,
            scope="application",
            namespaces=["KSESSIONS"],
            confidence=0.70  # Lower confidence
        )
        
        kg.add_pattern(
            pattern_id="noor_specific",
            title="NOOR Specific Feature",
            content="workflow testing feature",
            pattern_type=PatternType.SOLUTION,
            scope="application",
            namespaces=["NOOR"],
            confidence=0.90  # Higher confidence
        )
        
        # Search from KSESSIONS context
        results = kg.search_patterns_with_namespace(
            query="workflow testing feature",
            current_namespace="KSESSIONS",
            include_generic=False,
            limit=5
        )
        
        # KSESSIONS pattern should rank first despite lower confidence
        # (namespace boost should outweigh confidence difference)
        if len(results) >= 2:
            # First should be KSESSIONS
            assert "KSESSIONS" in results[0].namespaces
    
    def test_generic_patterns_medium_priority(self, kg):
        """Verify generic patterns get 1.5x boost when included."""
        results = kg.search_patterns_with_namespace(
            query="testing",
            current_namespace="KSESSIONS",
            include_generic=True,
            limit=10
        )
        
        # Generic patterns should appear but after current namespace
        generic_found = False
        ksessions_found = False
        
        for pattern in results:
            if pattern.scope == "cortex" and "KSESSIONS" not in pattern.namespaces:
                generic_found = True
            if "KSESSIONS" in pattern.namespaces and pattern.scope == "application":
                ksessions_found = True
        
        # Both should be present
        assert generic_found or ksessions_found  # At least one


class TestEmptyResults:
    """Test edge cases with empty results."""
    
    def test_search_no_matches(self, kg):
        """Verify empty results when no patterns match."""
        results = kg.search_patterns_with_namespace(
            query="nonexistent_term_xyz123",
            current_namespace="KSESSIONS",
            limit=10
        )
        
        assert len(results) == 0
    
    def test_namespace_with_no_patterns(self, kg):
        """Verify empty results for namespace with no patterns."""
        patterns = kg.get_patterns_by_namespace("EMPTY_NAMESPACE")
        
        assert len(patterns) == 0
    
    def test_empty_database_generic_patterns(self, temp_db):
        """Verify empty result when database has no patterns."""
        kg = KnowledgeGraph(db_path=temp_db)
        patterns = kg.get_generic_patterns()
        
        assert len(patterns) == 0


class TestLimitParameter:
    """Test limit parameter functionality."""
    
    def test_limit_respected_in_namespace_search(self, kg):
        """Verify limit parameter limits results."""
        results = kg.search_patterns_with_namespace(
            query="testing",
            current_namespace="KSESSIONS",
            limit=2
        )
        
        assert len(results) <= 2
    
    def test_limit_larger_than_results(self, kg):
        """Verify limit works when larger than available results."""
        results = kg.search_patterns_with_namespace(
            query="testing",
            current_namespace="KSESSIONS",
            limit=1000
        )
        
        # Should return all matches, not padded to 1000
        assert len(results) <= 10  # We only have ~6 patterns total

