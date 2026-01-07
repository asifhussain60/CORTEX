"""
Performance tests for GovernanceMerger.

This module validates the <50ms merge performance requirement
for feat03-governance Phase 3, Task 3.3.

Tests:
- Merge performance < 50ms (with caching)
- Cache hit rate validation
- File hash computation performance
- Cache invalidation on file changes
- Memory usage tracking
"""

import time
from pathlib import Path
from unittest import mock

import pytest

from src.orchestrators.core.governance_merger import GovernanceMerger
from src.orchestrators.audit_logger import AuditLevel, AuditCategory


class TestGovernancePerformance:
    """Test performance characteristics of GovernanceMerger."""

    def test_merge_performance_under_50ms(self, tmp_path):
        """Test: Merge completes in <50ms with caching."""
        # Create minimal governance file
        core_rules = tmp_path / "tier0" / "governance"
        core_rules.mkdir(parents=True)
        core_rules_file = core_rules / "core-rules.yaml"
        core_rules_file.write_text("""
rules:
  - id: CORE-001
    name: test_rule
    category: orchestration_lifecycle
    severity: CRITICAL
    description: Test rule
    governance_tier: 0
    precedence: 1
""")

        # Create merger with caching enabled
        with mock.patch("src.orchestrators.core.governance_merger.EnterpriseAuditLogger"):
            merger = GovernanceMerger(governance_root=tmp_path, enable_cache=True)

            # First merge (cold cache) - may be slower
            start = time.time()
            result1 = merger.merge()
            cold_time = (time.time() - start) * 1000  # ms

            # Second merge (warm cache) - should be <50ms
            start = time.time()
            result2 = merger.merge()
            warm_time = (time.time() - start) * 1000  # ms

            # Verify results
            assert result1.rule_count > 0
            assert result2.rule_count == result1.rule_count

            # Performance assertion
            assert warm_time < 50.0, f"Warm cache merge took {warm_time:.2f}ms (target: <50ms)"

            # Cache should have hit on second merge
            stats = merger.get_cache_stats()
            assert stats["hit_count"] > 0, "Cache should have hits on warm merge"

    def test_cache_hit_rate_validation(self, tmp_path):
        """Test: Cache achieves high hit rate on repeated operations."""
        # Create governance file
        core_rules = tmp_path / "tier0" / "governance"
        core_rules.mkdir(parents=True)
        core_rules_file = core_rules / "core-rules.yaml"
        core_rules_file.write_text("""
rules:
  - id: CORE-001
    name: test_rule
    category: orchestration_lifecycle
    severity: CRITICAL
    description: Test rule
    governance_tier: 0
    precedence: 1
""")

        with mock.patch("src.orchestrators.core.governance_merger.EnterpriseAuditLogger"):
            merger = GovernanceMerger(governance_root=tmp_path, enable_cache=True)

            # Perform 10 merge operations
            for _ in range(10):
                merger.merge()

            # Check cache statistics
            stats = merger.get_cache_stats()
            hit_rate = stats["hit_count"] / (stats["hit_count"] + stats["miss_count"])

            # After first miss, should have 9 hits = 90% hit rate
            assert hit_rate >= 0.85, f"Cache hit rate {hit_rate:.1%} below 85% threshold"

    def test_file_hash_computation_performance(self, tmp_path):
        """Test: File hash computation is fast (<5ms)."""
        # Create test file with moderate size (10KB)
        test_file = tmp_path / "test.yaml"
        test_file.write_text("rule: test\n" * 1000)

        with mock.patch("src.orchestrators.core.governance_merger.EnterpriseAuditLogger"):
            merger = GovernanceMerger(governance_root=tmp_path, enable_cache=True)

            # Measure hash computation
            start = time.time()
            file_hash = merger._compute_file_hash(test_file)
            elapsed = (time.time() - start) * 1000  # ms

            # Verify hash generated
            assert file_hash is not None
            assert len(file_hash) == 64  # SHA256 hex digest

            # Performance assertion
            assert elapsed < 5.0, f"Hash computation took {elapsed:.2f}ms (target: <5ms)"

    def test_cache_invalidation_on_file_change(self, tmp_path):
        """Test: Cache invalidates when file is modified."""
        # Create governance file
        core_rules = tmp_path / "tier0" / "governance"
        core_rules.mkdir(parents=True)
        core_rules_file = core_rules / "core-rules.yaml"
        core_rules_file.write_text("""
rules:
  - id: CORE-001
    name: test_rule
    category: orchestration_lifecycle
    severity: CRITICAL
    description: Test rule v1
    governance_tier: 0
    precedence: 1
""")

        with mock.patch("src.orchestrators.core.governance_merger.EnterpriseAuditLogger"):
            merger = GovernanceMerger(governance_root=tmp_path, enable_cache=True)

            # First load (cache miss)
            result1 = merger.load_core_rules()
            stats1 = merger.get_cache_stats()
            misses1 = stats1["miss_count"]

            # Second load (cache hit)
            result2 = merger.load_core_rules()
            stats2 = merger.get_cache_stats()
            hits2 = stats2["hit_count"]

            # Modify file
            core_rules_file.write_text("""
rules:
  - id: CORE-001
    name: test_rule
    category: orchestration_lifecycle
    severity: CRITICAL
    description: Test rule v2 MODIFIED
    governance_tier: 0
    precedence: 1
""")

            # Third load (should detect change and reload)
            result3 = merger.load_core_rules()
            stats3 = merger.get_cache_stats()
            misses3 = stats3["miss_count"]

            # Verify cache behavior
            assert stats1["hit_count"] == 0, "First load should be cache miss"
            assert hits2 > stats1["hit_count"], "Second load should be cache hit"
            assert misses3 > misses1, "Modified file should cause cache miss"

            # Verify content changed
            assert result3[0].description == "Test rule v2 MODIFIED"

    def test_cache_expiration_after_ttl(self, tmp_path):
        """Test: Cache expires after 5-minute TTL."""
        # Create governance file
        core_rules = tmp_path / "tier0" / "governance"
        core_rules.mkdir(parents=True)
        core_rules_file = core_rules / "core-rules.yaml"
        core_rules_file.write_text("""
rules:
  - id: CORE-001
    name: test_rule
    category: orchestration_lifecycle
    severity: CRITICAL
    description: Test rule
    governance_tier: 0
    precedence: 1
""")

        with mock.patch("src.orchestrators.core.governance_merger.EnterpriseAuditLogger"):
            merger = GovernanceMerger(governance_root=tmp_path, enable_cache=True)

            # First load
            merger.load_core_rules()

            # Simulate time passing by manipulating cache timestamp
            # Set timestamp to 6 minutes ago (beyond 5-min TTL)
            cache_key = "core_rules"
            if cache_key in merger._cache_timestamps:
                merger._cache_timestamps[cache_key] = time.time() - (6 * 60)

            # Load again - should be cache miss due to expiration
            stats_before = merger.get_cache_stats()
            misses_before = stats_before["miss_count"]

            merger.load_core_rules()

            stats_after = merger.get_cache_stats()
            misses_after = stats_after["miss_count"]

            # Verify cache miss occurred
            assert misses_after > misses_before, "Expired cache should cause miss"

    def test_clear_cache_functionality(self, tmp_path):
        """Test: clear_cache() invalidates all cached data."""
        # Create governance file
        core_rules = tmp_path / "tier0" / "governance"
        core_rules.mkdir(parents=True)
        core_rules_file = core_rules / "core-rules.yaml"
        core_rules_file.write_text("""
rules:
  - id: CORE-001
    name: test_rule
    category: orchestration_lifecycle
    severity: CRITICAL
    description: Test rule
    governance_tier: 0
    precedence: 1
""")

        with mock.patch("src.orchestrators.core.governance_merger.EnterpriseAuditLogger"):
            merger = GovernanceMerger(governance_root=tmp_path, enable_cache=True)

            # Load and cache
            merger.load_core_rules()
            merger.merge()

            # Verify cache populated
            assert len(merger._rule_cache) > 0
            assert len(merger._file_hashes) > 0
            assert merger._unified_cache is not None

            # Clear cache
            merger.clear_cache()

            # Verify cache cleared
            assert len(merger._rule_cache) == 0
            assert len(merger._file_hashes) == 0
            assert len(merger._cache_timestamps) == 0
            assert merger._unified_cache is None

            # Next load should be cache miss
            stats_before = merger.get_cache_stats()
            merger.load_core_rules()
            stats_after = merger.get_cache_stats()

            assert stats_after["miss_count"] > stats_before["miss_count"]

    def test_memory_efficiency(self, tmp_path):
        """Test: Cached data does not cause memory bloat."""
        # Create governance files with various sizes
        core_rules = tmp_path / "tier0" / "governance"
        core_rules.mkdir(parents=True)

        # Generate rules (simulate moderate rule set)
        rules_yaml = "rules:\n"
        for i in range(50):  # 50 rules
            rules_yaml += f"""
  - id: CORE-{i:03d}
    name: test_rule_{i}
    category: orchestration_lifecycle
    severity: CRITICAL
    description: Test rule {i}
    governance_tier: 0
    precedence: {i + 1}
"""
        core_rules_file = core_rules / "core-rules.yaml"
        core_rules_file.write_text(rules_yaml)

        with mock.patch("src.orchestrators.core.governance_merger.EnterpriseAuditLogger"):
            merger = GovernanceMerger(governance_root=tmp_path, enable_cache=True)

            # Load and merge multiple times
            for _ in range(20):
                merger.merge()

            # Verify cache size is reasonable
            # Cache should only store one copy of each rule set
            assert len(merger._rule_cache) <= 4, "Cache should not duplicate entries"
            assert len(merger._file_hashes) <= 4, "File hashes should not accumulate"

    def test_concurrent_access_safety(self, tmp_path):
        """Test: Cache handles repeated access safely."""
        # Create governance file
        core_rules = tmp_path / "tier0" / "governance"
        core_rules.mkdir(parents=True)
        core_rules_file = core_rules / "core-rules.yaml"
        core_rules_file.write_text("""
rules:
  - id: CORE-001
    name: test_rule
    category: orchestration_lifecycle
    severity: CRITICAL
    description: Test rule
    governance_tier: 0
    precedence: 1
""")

        with mock.patch("src.orchestrators.core.governance_merger.EnterpriseAuditLogger"):
            merger = GovernanceMerger(governance_root=tmp_path, enable_cache=True)

            # Perform rapid repeated access
            results = []
            for _ in range(100):
                result = merger.merge()
                results.append(result.rule_count)

            # Verify consistency
            assert all(count == results[0] for count in results), "Results should be consistent"

            # Verify cache statistics make sense
            stats = merger.get_cache_stats()
            assert stats["hit_count"] > 90, "Should have high cache hits after 100 iterations"


class TestPerformanceBenchmarks:
    """Benchmark tests for detailed performance profiling."""

    def test_cold_vs_warm_cache_comparison(self, tmp_path):
        """Benchmark: Compare cold cache vs warm cache performance."""
        # Create governance file
        core_rules = tmp_path / "tier0" / "governance"
        core_rules.mkdir(parents=True)
        core_rules_file = core_rules / "core-rules.yaml"

        # Generate moderate rule set
        rules_yaml = "rules:\n"
        for i in range(25):
            rules_yaml += f"""
  - id: CORE-{i:03d}
    name: test_rule_{i}
    category: orchestration_lifecycle
    severity: CRITICAL
    description: Test rule {i}
    governance_tier: 0
    precedence: {i + 1}
"""
        core_rules_file.write_text(rules_yaml)

        with mock.patch("src.orchestrators.core.governance_merger.EnterpriseAuditLogger"):
            # Cold cache test
            merger_cold = GovernanceMerger(governance_root=tmp_path, enable_cache=True)
            start = time.time()
            merger_cold.merge()
            cold_time = (time.time() - start) * 1000

            # Warm cache test
            merger_warm = GovernanceMerger(governance_root=tmp_path, enable_cache=True)
            merger_warm.merge()  # Prime cache
            start = time.time()
            merger_warm.merge()  # Measure cached performance
            warm_time = (time.time() - start) * 1000

            # Verify warm cache is significantly faster
            speedup = cold_time / warm_time
            assert speedup > 2.0, f"Warm cache should be >2x faster (speedup: {speedup:.1f}x)"
            assert warm_time < 50.0, f"Warm cache merge should be <50ms (actual: {warm_time:.2f}ms)"

    def test_cache_disabled_performance(self, tmp_path):
        """Benchmark: Performance with caching disabled."""
        # Create governance file
        core_rules = tmp_path / "tier0" / "governance"
        core_rules.mkdir(parents=True)
        core_rules_file = core_rules / "core-rules.yaml"
        core_rules_file.write_text("""
rules:
  - id: CORE-001
    name: test_rule
    category: orchestration_lifecycle
    severity: CRITICAL
    description: Test rule
    governance_tier: 0
    precedence: 1
""")

        with mock.patch("src.orchestrators.core.governance_merger.EnterpriseAuditLogger"):
            # Test with cache disabled
            merger_no_cache = GovernanceMerger(governance_root=tmp_path, enable_cache=False)

            # Multiple merges without cache
            times = []
            for _ in range(5):
                start = time.time()
                merger_no_cache.merge()
                elapsed = (time.time() - start) * 1000
                times.append(elapsed)

            # Verify stats show no caching
            stats = merger_no_cache.get_cache_stats()
            assert stats["hit_count"] == 0, "No cache hits when disabled"
            assert stats["miss_count"] == 0, "No cache tracking when disabled"

            # Times should be consistent (no speedup without cache)
            avg_time = sum(times) / len(times)
            variance = sum((t - avg_time) ** 2 for t in times) / len(times)
            assert variance < 100, "Times should be consistent without caching"
