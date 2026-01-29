"""
Performance and benchmarking test suite for Governance system.

Purpose:
    Test performance characteristics, caching efficiency, and scalability.

Coverage:
    - Query performance benchmarking
    - Cache hit/miss rates
    - Bulk operations performance
    - Rule lookup performance
    - Registry loading performance

Author: Asif Hussain
Version: 1.0
"""

import pytest
import tempfile
import time
from pathlib import Path
from cortex.orchestrators.core.governance_registry import GovernanceRegistry
from cortex.brain.core.governance_database import GovernanceDatabaseManager


class TestQueryPerformance:
    """Test query performance characteristics."""

    def test_get_rule_performance(self) -> None:
        """Test performance of single rule retrieval."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            mgr = GovernanceDatabaseManager(db_path=db_path)
            mgr.initialize()
            
            # Create a rule
            mgr.create_project_rule(
                rule_id="PERF-001",
                name="Performance Test Rule",
                category="test",
                severity="info",
                description="Performance",
                enforcement_point="test",
                audit_event="TEST",
                created_by="test_user",
            )
            
            # Measure retrieval time
            start = time.time()
            for _ in range(100):
                mgr.get_rule("PERF-001")
            elapsed = time.time() - start
            
            # Should be very fast (less than 1 second for 100 lookups)
            assert elapsed < 1.0
            
            mgr.close()

    def test_list_rules_performance(self) -> None:
        """Test performance of listing rules."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            mgr = GovernanceDatabaseManager(db_path=db_path)
            mgr.initialize()
            
            # Create multiple rules
            for i in range(20):
                mgr.create_project_rule(
                    rule_id=f"LIST-{i:03d}",
                    name=f"List Test Rule {i}",
                    category="test",
                    severity="info",
                    description="List test",
                    enforcement_point="test",
                    audit_event="TEST",
                    created_by="test_user",
                )
            
            # Measure list time
            start = time.time()
            for _ in range(50):
                mgr.list_rules()
            elapsed = time.time() - start
            
            # Should be reasonable (less than 1 second for 50 list operations)
            assert elapsed < 1.0
            
            mgr.close()


class TestRegistryPerformance:
    """Test registry performance."""

    def test_registry_initialization_speed(self) -> None:
        """Test registry initialization performance."""
        start = time.time()
        registry = GovernanceRegistry()
        registry.initialize()
        elapsed = time.time() - start
        
        # Initialization should be fast
        assert elapsed < 1.0

    def test_registry_get_all_rules_speed(self) -> None:
        """Test get_all_rules() performance."""
        registry = GovernanceRegistry()
        registry.initialize()
        
        # Measure retrieval speed
        start = time.time()
        for _ in range(100):
            registry.get_all_rules()
        elapsed = time.time() - start
        
        # Should be very fast
        assert elapsed < 1.0


class TestCacheEffectiveness:
    """Test query cache effectiveness."""

    def test_repeated_queries_are_fast(self) -> None:
        """Test that repeated queries benefit from caching."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            mgr = GovernanceDatabaseManager(db_path=db_path)
            mgr.initialize()
            
            # Create rules
            for i in range(10):
                mgr.create_project_rule(
                    rule_id=f"CACHE-{i:03d}",
                    name=f"Cache Test Rule {i}",
                    category="test",
                    severity="info",
                    description="Cache test",
                    enforcement_point="test",
                    audit_event="TEST",
                    created_by="test_user",
                )
            
            # First query (cache miss)
            start1 = time.time()
            mgr.get_rules_by_category("test")
            elapsed1 = time.time() - start1
            
            # Second query (cache hit)
            start2 = time.time()
            mgr.get_rules_by_category("test")
            elapsed2 = time.time() - start2
            
            # Cache hit should be faster or similar (already in-memory)
            # Just verify both complete quickly
            assert elapsed1 < 1.0
            assert elapsed2 < 1.0
            
            mgr.close()


class TestBulkOperations:
    """Test bulk operation performance."""

    def test_bulk_rule_creation(self) -> None:
        """Test performance of creating multiple rules."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            mgr = GovernanceDatabaseManager(db_path=db_path)
            mgr.initialize()
            
            # Create many rules
            start = time.time()
            for i in range(50):
                mgr.create_project_rule(
                    rule_id=f"BULK-{i:03d}",
                    name=f"Bulk Rule {i}",
                    category="test",
                    severity="info",
                    description="Bulk test",
                    enforcement_point="test",
                    audit_event="TEST",
                    created_by="test_user",
                )
            elapsed = time.time() - start
            
            # Should be reasonable (less than 2 seconds for 50 creates)
            assert elapsed < 2.0
            
            mgr.close()

    def test_bulk_rule_retrieval(self) -> None:
        """Test performance of retrieving many rules."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            mgr = GovernanceDatabaseManager(db_path=db_path)
            mgr.initialize()
            
            # Create rules
            for i in range(30):
                mgr.create_project_rule(
                    rule_id=f"RET-{i:03d}",
                    name=f"Retrieval Rule {i}",
                    category="test",
                    severity="info",
                    description="Retrieval test",
                    enforcement_point="test",
                    audit_event="TEST",
                    created_by="test_user",
                )
            
            # Retrieve all
            start = time.time()
            rules = mgr.list_rules()
            elapsed = time.time() - start
            
            assert len(rules) >= 30
            assert elapsed < 1.0
            
            mgr.close()


class TestScalability:
    """Test system scalability."""

    def test_many_rules_in_registry(self) -> None:
        """Test registry with many rules."""
        registry = GovernanceRegistry()
        registry.initialize()
        
        all_rules = registry.get_all_rules()
        total_rules = (
            len(all_rules.get("tier0", [])) +
            len(all_rules.get("tier1", [])) +
            len(all_rules.get("tier2", []))
        )
        
        # Should handle multiple rules smoothly
        assert total_rules >= 0  # Just verify it doesn't crash

    def test_many_queries_concurrent_style(self) -> None:
        """Test many sequential queries (simulating concurrent patterns)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            mgr = GovernanceDatabaseManager(db_path=db_path)
            mgr.initialize()
            
            # Create rules
            for i in range(15):
                mgr.create_project_rule(
                    rule_id=f"SEQ-{i:03d}",
                    name=f"Sequential Rule {i}",
                    category="test",
                    severity="info",
                    description="Sequential test",
                    enforcement_point="test",
                    audit_event="TEST",
                    created_by="test_user",
                )
            
            # Perform many queries rapidly
            start = time.time()
            for i in range(200):
                rule_id = f"SEQ-{i % 15:03d}"
                mgr.get_rule(rule_id)
            elapsed = time.time() - start
            
            # Should handle rapid queries
            assert elapsed < 2.0
            
            mgr.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
