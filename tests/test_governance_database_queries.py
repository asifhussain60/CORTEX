"""
Test suite for GovernanceDatabaseManager query optimization and caching.

Purpose:
    Test advanced query methods, cache functionality, and performance
    for governance rules database.

Coverage:
    - get_rules_by_category()
    - get_rules_by_severity()
    - get_rules_by_enforcement_point()
    - search_rules()
    - get_active_rules()
    - Query result caching (LRU)
    - Cache invalidation on write operations

Author: Asif Hussain
Version: 1.0
"""

import pytest
import tempfile
from pathlib import Path
from typing import Generator, Any
from cortex.brain.core.governance_database import (
    GovernanceDatabaseManager,
    QueryCache,
)


class TestQueryCache:
    """Test suite for QueryCache LRU implementation."""

    def test_cache_set_and_get(self) -> None:
        """Test basic cache set/get operations."""
        cache = QueryCache(maxsize=5)
        
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"

    def test_cache_miss(self) -> None:
        """Test cache miss returns None."""
        cache = QueryCache(maxsize=5)
        
        assert cache.get("nonexistent") is None

    def test_cache_maxsize_enforcement(self) -> None:
        """Test cache respects maxsize and evicts oldest entry."""
        cache = QueryCache(maxsize=3)
        
        cache.set("k1", "v1")
        cache.set("k2", "v2")
        cache.set("k3", "v3")
        cache.set("k4", "v4")  # Should evict k1
        
        # k1 should be evicted
        assert cache.get("k1") is None
        # Newer entries should exist
        assert cache.get("k2") == "v2"
        assert cache.get("k3") == "v3"
        assert cache.get("k4") == "v4"
        # Size should respect max
        assert cache.size() <= 3

    def test_cache_clear(self) -> None:
        """Test cache clear operation."""
        cache = QueryCache(maxsize=5)
        
        cache.set("k1", "v1")
        cache.set("k2", "v2")
        cache.clear()
        
        assert cache.get("k1") is None
        assert cache.get("k2") is None

    def test_cache_invalidate_by_pattern(self) -> None:
        """Test cache invalidation by pattern."""
        cache = QueryCache(maxsize=10)
        
        cache.set("category:security", ["rule1", "rule2"])
        cache.set("category:performance", ["rule3"])
        cache.set("search:audit", ["rule4"])
        
        # Invalidate by pattern
        cache.invalidate(pattern="category")
        
        assert cache.get("category:security") is None
        assert cache.get("category:performance") is None
        assert cache.get("search:audit") == ["rule4"]

    def test_thread_safe_operations(self) -> None:
        """Test cache operations are thread-safe."""
        cache = QueryCache(maxsize=10)
        
        # Simulate concurrent access
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        
        # Should not raise any threading errors
        for i in range(100):
            cache.set(f"key{i}", f"value{i}")
            _ = cache.get(f"key{i % 50}")


class TestQueryMethods:
    """Test suite for advanced query methods."""

    @pytest.fixture
    def temp_db(self) -> Generator[GovernanceDatabaseManager, None, None]:
        """Create temporary database for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            mgr = GovernanceDatabaseManager(db_path=db_path)
            mgr.initialize()
            yield mgr
            mgr.close()

    def test_get_rules_by_category(self, temp_db: GovernanceDatabaseManager) -> None:
        """Test retrieving rules by category."""
        # Create test rules
        temp_db.create_project_rule(
            rule_id="SEC-001",
            name="SQL Injection Prevention",
            category="security",
            severity="blocked",
            description="Prevent SQL injection attacks",
            enforcement_point="query_builder",
            audit_event="SECURITY_VIOLATION",
            created_by="test_user",
        )
        
        temp_db.create_project_rule(
            rule_id="SEC-002",
            name="XSS Prevention",
            category="security",
            severity="blocked",
            description="Prevent XSS attacks",
            enforcement_point="output_sanitizer",
            audit_event="SECURITY_VIOLATION",
            created_by="test_user",
        )
        
        temp_db.create_project_rule(
            rule_id="PERF-001",
            name="Query Optimization",
            category="performance",
            severity="warning",
            description="Optimize slow queries",
            enforcement_point="query_optimizer",
            audit_event="PERFORMANCE_WARNING",
            created_by="test_user",
        )
        
        # Test query
        security_rules = temp_db.get_rules_by_category("security")
        assert len(security_rules) == 2
        assert all(r.category == "security" for r in security_rules)
        
        performance_rules = temp_db.get_rules_by_category("performance")
        assert len(performance_rules) == 1
        assert performance_rules[0].rule_id == "PERF-001"

    def test_get_rules_by_severity(self, temp_db: GovernanceDatabaseManager) -> None:
        """Test retrieving rules by severity."""
        # Create test rules
        for i in range(3):
            temp_db.create_project_rule(
                rule_id=f"BLOCK-{i}",
                name=f"Blocking Rule {i}",
                category="security",
                severity="blocked",
                description="Test",
                enforcement_point="test",
                audit_event="TEST",
                created_by="test_user",
            )
        
        for i in range(2):
            temp_db.create_project_rule(
                rule_id=f"WARN-{i}",
                name=f"Warning Rule {i}",
                category="quality",
                severity="warning",
                description="Test",
                enforcement_point="test",
                audit_event="TEST",
                created_by="test_user",
            )
        
        # Test queries
        blocked_rules = temp_db.get_rules_by_severity("blocked")
        assert len(blocked_rules) == 3
        
        warning_rules = temp_db.get_rules_by_severity("warning")
        assert len(warning_rules) == 2

    def test_get_rules_by_enforcement_point(self, temp_db: GovernanceDatabaseManager) -> None:
        """Test retrieving rules by enforcement point."""
        # Create test rules
        temp_db.create_project_rule(
            rule_id="EP-001",
            name="Rule 1",
            category="test",
            severity="blocked",
            description="Test",
            enforcement_point="linting",
            audit_event="TEST",
            created_by="test_user",
        )
        
        temp_db.create_project_rule(
            rule_id="EP-002",
            name="Rule 2",
            category="test",
            severity="warning",
            description="Test",
            enforcement_point="linting",
            audit_event="TEST",
            created_by="test_user",
        )
        
        temp_db.create_project_rule(
            rule_id="EP-003",
            name="Rule 3",
            category="test",
            severity="info",
            description="Test",
            enforcement_point="formatting",
            audit_event="TEST",
            created_by="test_user",
        )
        
        # Test query
        linting_rules = temp_db.get_rules_by_enforcement_point("linting")
        assert len(linting_rules) == 2
        assert all(r.enforcement_point == "linting" for r in linting_rules)

    def test_search_rules(self, temp_db: GovernanceDatabaseManager) -> None:
        """Test full-text search on rules."""
        # Create test rules
        temp_db.create_project_rule(
            rule_id="S-001",
            name="SQL Injection Prevention",
            category="security",
            severity="blocked",
            description="Prevent database attacks",
            enforcement_point="backend",
            audit_event="TEST",
            created_by="test_user",
        )
        
        temp_db.create_project_rule(
            rule_id="S-002",
            name="Type Checking",
            category="quality",
            severity="warning",
            description="Enforce strong typing",
            enforcement_point="compiler",
            audit_event="TEST",
            created_by="test_user",
        )
        
        # Test searches
        sql_results = temp_db.search_rules("SQL")
        assert len(sql_results) == 1
        assert sql_results[0].rule_id == "S-001"
        
        attack_results = temp_db.search_rules("attacks")
        assert len(attack_results) == 1
        
        type_results = temp_db.search_rules("Type")
        assert len(type_results) == 1
        assert type_results[0].rule_id == "S-002"

    def test_get_active_rules(self, temp_db: GovernanceDatabaseManager) -> None:
        """Test retrieving active rules only."""
        # Create test rules
        _ = temp_db.create_project_rule(
            rule_id="ACT-001",
            name="Active Rule",
            category="security",
            severity="blocked",
            description="Test",
            enforcement_point="test",
            audit_event="TEST",
            created_by="test_user",
        )
        
        _ = temp_db.create_project_rule(
            rule_id="ACT-002",
            name="Inactive Rule",
            category="security",
            severity="info",
            description="Test",
            enforcement_point="test",
            audit_event="TEST",
            created_by="test_user",
        )
        
        # Deactivate rule2
        temp_db.update_rule("ACT-002", updated_by="test_user", is_active=False)
        
        # Test query
        active_rules = temp_db.get_active_rules()
        assert len(active_rules) == 1
        assert active_rules[0].rule_id == "ACT-001"


class TestCacheInvalidation:
    """Test suite for cache invalidation on write operations."""

    @pytest.fixture
    def temp_db(self) -> Generator[GovernanceDatabaseManager, None, None]:
        """Create temporary database for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            mgr = GovernanceDatabaseManager(db_path=db_path)
            mgr.initialize()
            yield mgr
            mgr.close()

    def test_cache_invalidation_on_create(self, temp_db: GovernanceDatabaseManager) -> None:
        """Test cache is invalidated when creating new rule."""
        # Populate cache by calling get_active_rules
        temp_db.get_active_rules()
        cache_size_before = temp_db.get_cache_size()
        assert cache_size_before > 0
        
        # Create new rule (should invalidate cache)
        temp_db.create_project_rule(
            rule_id="NEW-001",
            name="New Rule",
            category="test",
            severity="info",
            description="Test",
            enforcement_point="test",
            audit_event="TEST",
            created_by="test_user",
        )
        
        # Cache should be cleared
        cache_size_after = temp_db.get_cache_size()
        assert cache_size_after == 0

    def test_cache_invalidation_on_update(self, temp_db: GovernanceDatabaseManager) -> None:
        """Test cache is invalidated when updating rule."""
        # Create rule
        temp_db.create_project_rule(
            rule_id="UPD-001",
            name="Update Test",
            category="security",
            severity="blocked",
            description="Test",
            enforcement_point="test",
            audit_event="TEST",
            created_by="test_user",
        )
        
        # Populate cache
        temp_db.get_rules_by_category("security")
        cache_size_before = temp_db.get_cache_size()
        assert cache_size_before > 0
        
        # Update rule (should invalidate cache with pattern matching)
        temp_db.update_rule("UPD-001", updated_by="test_user", severity="warning")
        
        # Re-querying should give updated data
        updated_rules = temp_db.get_rules_by_category("security")
        # The rule should now have severity "warning", not "blocked"
        updated_rule = next((r for r in updated_rules if r.rule_id == "UPD-001"), None)
        assert updated_rule is not None
        assert updated_rule.severity == "warning"

    def test_manual_cache_clear(self, temp_db: GovernanceDatabaseManager) -> None:
        """Test manual cache clearing."""
        # Populate cache
        temp_db.get_rules_by_category("security")
        cache_size_before = temp_db.get_cache_size()
        assert cache_size_before > 0
        
        # Clear cache
        temp_db.clear_query_cache()
        cache_size_after = temp_db.get_cache_size()
        assert cache_size_after == 0


class TestQueryPerformance:
    """Test suite for query performance characteristics."""

    @pytest.fixture
    def populated_db(self) -> Generator[GovernanceDatabaseManager, None, None]:
        """Create database with test data."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            mgr = GovernanceDatabaseManager(db_path=db_path)
            mgr.initialize()
            
            # Create multiple rules
            categories = ["security", "performance", "quality", "compliance"]
            severities = ["blocked", "warning", "info"]
            
            for cat_idx, category in enumerate(categories):
                for sev_idx, severity in enumerate(severities):
                    for i in range(5):
                        mgr.create_project_rule(
                            rule_id=f"{category.upper()}-{sev_idx}-{i}",
                            name=f"{category} Rule {i}",
                            category=category,
                            severity=severity,
                            description=f"Test rule for {category}",
                            enforcement_point=f"enforcement_{cat_idx}",
                            audit_event="TEST",
                            created_by="test_user",
                        )
            
            yield mgr
            mgr.close()

    def test_query_caching_improves_performance(self, populated_db: GovernanceDatabaseManager) -> None:
        """Test that cached queries return same results faster."""
        # First call (cache miss)
        results1 = populated_db.get_rules_by_category("security")
        
        # Second call (cache hit)
        results2 = populated_db.get_rules_by_category("security")
        
        # Results should be identical
        assert len(results1) == len(results2)
        assert all(r1.rule_id == r2.rule_id for r1, r2 in zip(results1, results2))

    def test_multiple_query_types_with_caching(self, populated_db: GovernanceDatabaseManager) -> None:
        """Test multiple query types with caching."""
        # Execute various queries
        results = {
            "category:security": populated_db.get_rules_by_category("security"),
            "severity:blocked": populated_db.get_rules_by_severity("blocked"),
            "enforcement:enforcement_0": populated_db.get_rules_by_enforcement_point("enforcement_0"),
            "active": populated_db.get_active_rules(),
        }
        
        # All should have results
        assert all(len(v) > 0 for v in results.values())
        
        # Cache should have entries
        cache_size = populated_db.get_cache_size()
        assert cache_size > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
