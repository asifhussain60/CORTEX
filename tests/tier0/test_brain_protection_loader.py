"""
Tests for Brain Protection Rules Loader with Caching

Validates caching behavior, performance improvements, and cache invalidation.

Test Categories:
1. Cache Behavior - Hit/miss scenarios, invalidation
2. Performance - Load time improvements
3. File Modification - Timestamp-based invalidation
4. Integration - BrainProtector integration

Expected Performance:
- First load: ~550ms (cold cache)
- Subsequent loads: <5ms (warm cache)
- 99%+ improvement for repeated loads

Date: November 17, 2025
"""

import pytest
import time
import os
from pathlib import Path
from unittest.mock import patch, mock_open
import tempfile
import yaml

from src.tier0.brain_protection_loader import (
    load_brain_protection_rules,
    get_cache_stats,
    clear_cache,
    reset_cache_stats,
    is_cached,
    get_cache_age_seconds,
    patch_brain_protector,
    unpatch_brain_protector
)


@pytest.fixture
def reset_cache():
    """Reset cache before each test."""
    clear_cache()
    reset_cache_stats()
    yield
    clear_cache()
    reset_cache_stats()


@pytest.fixture
def temp_rules_file():
    """Create temporary rules file for testing."""
    rules_data = {
        'critical_paths': ['test/path/'],
        'tier0_instincts': ['TEST_RULE'],
        'protection_layers': [
            {
                'layer_id': 'test_layer',
                'name': 'Test Layer',
                'rules': []
            }
        ]
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(rules_data, f)
        temp_path = Path(f.name)
    
    yield temp_path
    
    # Cleanup
    if temp_path.exists():
        temp_path.unlink()


class TestCacheBehavior:
    """Test cache hit/miss scenarios and invalidation."""
    
    def test_first_load_is_cache_miss(self, reset_cache, temp_rules_file):
        """First load should be a cache miss (load from disk)."""
        # Load rules
        rules = load_brain_protection_rules(rules_path=temp_rules_file)
        
        # Verify loaded
        assert rules is not None
        assert 'critical_paths' in rules
        
        # Check stats
        stats = get_cache_stats()
        assert stats['cached'] is True
        assert stats['misses'] == 1
        assert stats['hits'] == 0
        assert stats['hit_rate'] == 0.0
    
    def test_second_load_is_cache_hit(self, reset_cache, temp_rules_file):
        """Second load (file unchanged) should be a cache hit."""
        # First load
        rules1 = load_brain_protection_rules(rules_path=temp_rules_file)
        
        # Second load (file unchanged)
        rules2 = load_brain_protection_rules(rules_path=temp_rules_file)
        
        # Should be identical objects (cached)
        assert rules1 is rules2
        
        # Check stats
        stats = get_cache_stats()
        assert stats['hits'] == 1
        assert stats['misses'] == 1
        assert stats['hit_rate'] == 50.0
    
    def test_cache_invalidation_on_file_modification(self, reset_cache, temp_rules_file):
        """Cache should invalidate when file is modified."""
        # First load
        rules1 = load_brain_protection_rules(rules_path=temp_rules_file)
        
        # Modify file (update mtime)
        time.sleep(0.01)  # Ensure mtime changes
        temp_rules_file.touch()
        
        # Second load (file changed)
        rules2 = load_brain_protection_rules(rules_path=temp_rules_file)
        
        # Should reload (new object)
        # Note: Content is same, but should be new object due to reload
        
        # Check stats
        stats = get_cache_stats()
        assert stats['misses'] == 2  # Both loads were misses
        assert stats['hits'] == 0
    
    def test_force_reload_bypasses_cache(self, reset_cache, temp_rules_file):
        """force_reload=True should bypass cache even if file unchanged."""
        # First load
        rules1 = load_brain_protection_rules(rules_path=temp_rules_file)
        
        # Second load with force_reload
        rules2 = load_brain_protection_rules(rules_path=temp_rules_file, force_reload=True)
        
        # Check stats
        stats = get_cache_stats()
        assert stats['misses'] == 2  # Both should be misses
        assert stats['hits'] == 0
    
    def test_clear_cache_removes_cached_data(self, reset_cache, temp_rules_file):
        """clear_cache() should remove cached rules."""
        # Load and cache
        load_brain_protection_rules(rules_path=temp_rules_file)
        assert is_cached() is True
        
        # Clear cache
        clear_cache()
        assert is_cached() is False
        
        # Next load should be cache miss
        load_brain_protection_rules(rules_path=temp_rules_file)
        stats = get_cache_stats()
        assert stats['misses'] == 2


class TestPerformance:
    """Test performance improvements from caching."""
    
    def test_warm_cache_is_faster_than_cold_cache(self, reset_cache, temp_rules_file):
        """Warm cache should be significantly faster than cold cache."""
        # Cold cache (first load)
        start_cold = time.perf_counter()
        load_brain_protection_rules(rules_path=temp_rules_file)
        cold_time = time.perf_counter() - start_cold
        
        # Warm cache (second load)
        start_warm = time.perf_counter()
        load_brain_protection_rules(rules_path=temp_rules_file)
        warm_time = time.perf_counter() - start_warm
        
        # Warm should be faster (at least 2x for small test files)
        # (In production: 550ms -> 1-2ms = 275-550x faster)
        # (For small test file: ~2-10x faster due to minimal YAML parsing overhead)
        assert warm_time < cold_time / 2, f"Warm cache not faster: cold={cold_time:.4f}s, warm={warm_time:.4f}s"
        
        # Warm cache should be under 1ms for small files
        assert warm_time < 0.001, f"Warm cache too slow: {warm_time*1000:.2f}ms"
    
    def test_cache_hit_under_5ms(self, reset_cache, temp_rules_file):
        """Cache hits should be under 5ms (performance target)."""
        # Prime cache
        load_brain_protection_rules(rules_path=temp_rules_file)
        
        # Measure cache hit
        start = time.perf_counter()
        load_brain_protection_rules(rules_path=temp_rules_file)
        elapsed_ms = (time.perf_counter() - start) * 1000
        
        # Should be very fast (<5ms for timestamp check)
        assert elapsed_ms < 5.0, f"Cache hit too slow: {elapsed_ms:.2f}ms"


class TestCacheStats:
    """Test cache statistics functionality."""
    
    def test_cache_stats_structure(self, reset_cache, temp_rules_file):
        """get_cache_stats() should return expected structure."""
        load_brain_protection_rules(rules_path=temp_rules_file)
        
        stats = get_cache_stats()
        
        # Verify structure
        assert 'cached' in stats
        assert 'hits' in stats
        assert 'misses' in stats
        assert 'total_calls' in stats
        assert 'hit_rate' in stats
        assert 'last_mtime' in stats
        
        # Verify types
        assert isinstance(stats['cached'], bool)
        assert isinstance(stats['hits'], int)
        assert isinstance(stats['misses'], int)
        assert isinstance(stats['total_calls'], int)
        assert isinstance(stats['hit_rate'], float)
    
    def test_hit_rate_calculation(self, reset_cache, temp_rules_file):
        """Hit rate should be calculated correctly."""
        # 1 miss
        load_brain_protection_rules(rules_path=temp_rules_file)
        
        # 9 hits
        for _ in range(9):
            load_brain_protection_rules(rules_path=temp_rules_file)
        
        stats = get_cache_stats()
        assert stats['hits'] == 9
        assert stats['misses'] == 1
        assert stats['total_calls'] == 10
        assert stats['hit_rate'] == 90.0
    
    def test_reset_stats_clears_counters(self, reset_cache, temp_rules_file):
        """reset_cache_stats() should clear hit/miss counters."""
        # Generate some stats
        load_brain_protection_rules(rules_path=temp_rules_file)
        load_brain_protection_rules(rules_path=temp_rules_file)
        
        # Reset stats
        reset_cache_stats()
        
        stats = get_cache_stats()
        assert stats['hits'] == 0
        assert stats['misses'] == 0
        assert stats['total_calls'] == 0
        # Cache should still be populated
        assert stats['cached'] is True


class TestFileOperations:
    """Test file system operations and error handling."""
    
    def test_file_not_found_raises_error(self, reset_cache):
        """Loading non-existent file should raise FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            load_brain_protection_rules(rules_path=Path("nonexistent.yaml"))
    
    def test_default_path_resolution(self, reset_cache):
        """Default rules_path should resolve to cortex-brain/brain-protection-rules.yaml."""
        # This test requires actual file to exist
        project_root = Path(__file__).parent.parent.parent
        default_path = project_root / "cortex-brain" / "brain-protection-rules.yaml"
        
        if default_path.exists():
            rules = load_brain_protection_rules()
            assert rules is not None
            assert 'protection_layers' in rules
    
    def test_cache_age_tracking(self, reset_cache, temp_rules_file):
        """get_cache_age_seconds() should track cache age."""
        # Before loading
        assert get_cache_age_seconds() is None
        
        # Load rules
        load_brain_protection_rules(rules_path=temp_rules_file)
        
        # Check age (should be close to 0)
        age = get_cache_age_seconds()
        assert age is not None
        assert age < 1.0  # Less than 1 second old


class TestBrainProtectorIntegration:
    """Test integration with BrainProtector class."""
    
    def test_patch_brain_protector_enables_caching(self, reset_cache):
        """patch_brain_protector() should enable caching for BrainProtector instances."""
        from src.tier0.brain_protector import BrainProtector
        
        # Patch
        patch_brain_protector()
        
        try:
            # Create instances
            protector1 = BrainProtector()
            
            # Check cache stats (should have loaded once)
            stats = get_cache_stats()
            initial_misses = stats['misses']
            
            # Create second instance (should use cache)
            protector2 = BrainProtector()
            
            stats = get_cache_stats()
            assert stats['hits'] >= 1  # Second instance used cache
            
        finally:
            unpatch_brain_protector()
    
    def test_unpatch_restores_original_behavior(self, reset_cache):
        """unpatch_brain_protector() should restore original loading."""
        from src.tier0.brain_protector import BrainProtector
        
        # Patch
        patch_brain_protector()
        
        # Verify patched
        assert hasattr(BrainProtector, '_original_load_rules')
        
        # Unpatch
        unpatch_brain_protector()
        
        # Verify restored
        assert not hasattr(BrainProtector, '_original_load_rules')


class TestRealWorldScenarios:
    """Test realistic usage patterns."""
    
    def test_repeated_loads_high_cache_hit_rate(self, reset_cache, temp_rules_file):
        """Realistic scenario: 100 loads should have >95% hit rate."""
        # Simulate 100 rule loads (e.g., 100 user requests)
        for _ in range(100):
            load_brain_protection_rules(rules_path=temp_rules_file)
        
        stats = get_cache_stats()
        assert stats['total_calls'] == 100
        assert stats['misses'] == 1  # Only first load
        assert stats['hits'] == 99
        assert stats['hit_rate'] == 99.0
    
    def test_performance_improvement_over_session(self, reset_cache, temp_rules_file):
        """Calculate total time saved over a session with caching."""
        # Measure first load (cold cache)
        start = time.perf_counter()
        load_brain_protection_rules(rules_path=temp_rules_file)
        cold_time = time.perf_counter() - start
        
        # Measure average warm cache time (10 loads)
        warm_times = []
        for _ in range(10):
            start = time.perf_counter()
            load_brain_protection_rules(rules_path=temp_rules_file)
            warm_times.append(time.perf_counter() - start)
        
        avg_warm_time = sum(warm_times) / len(warm_times)
        
        # Calculate savings for 100-operation session
        # Without cache: 100 * cold_time
        # With cache: 1 * cold_time + 99 * warm_time
        without_cache = 100 * cold_time
        with_cache = cold_time + (99 * avg_warm_time)
        
        time_saved = without_cache - with_cache
        improvement_pct = (time_saved / without_cache) * 100
        
        # Should save significant time
        assert improvement_pct > 50.0, f"Only {improvement_pct:.1f}% improvement"


# Performance benchmark (skip in regular test runs)
@pytest.mark.benchmark
@pytest.mark.skip(reason="Benchmark test - run manually with 'pytest -m benchmark'")
def test_benchmark_cache_performance(reset_cache, temp_rules_file):
    """Benchmark cache performance with real brain-protection-rules.yaml."""
    project_root = Path(__file__).parent.parent.parent
    real_rules_path = project_root / "cortex-brain" / "brain-protection-rules.yaml"
    
    if not real_rules_path.exists():
        pytest.skip("Real brain-protection-rules.yaml not found")
    
    print("\n" + "="*60)
    print("CACHE PERFORMANCE BENCHMARK")
    print("="*60)
    
    # Cold cache
    clear_cache()
    start = time.perf_counter()
    load_brain_protection_rules(rules_path=real_rules_path)
    cold_time = time.perf_counter() - start
    
    print(f"\nCold Cache (First Load):")
    print(f"  Time: {cold_time*1000:.2f}ms")
    
    # Warm cache (10 runs)
    warm_times = []
    for i in range(10):
        start = time.perf_counter()
        load_brain_protection_rules(rules_path=real_rules_path)
        warm_times.append(time.perf_counter() - start)
    
    avg_warm = sum(warm_times) / len(warm_times)
    min_warm = min(warm_times)
    max_warm = max(warm_times)
    
    print(f"\nWarm Cache (10 Loads):")
    print(f"  Average: {avg_warm*1000:.2f}ms")
    print(f"  Min: {min_warm*1000:.2f}ms")
    print(f"  Max: {max_warm*1000:.2f}ms")
    
    # Calculate improvement
    improvement = ((cold_time - avg_warm) / cold_time) * 100
    speedup = cold_time / avg_warm
    
    print(f"\nImprovement:")
    print(f"  Reduction: {improvement:.1f}%")
    print(f"  Speedup: {speedup:.1f}x faster")
    
    # Session savings
    without_cache_100 = 100 * cold_time
    with_cache_100 = cold_time + (99 * avg_warm)
    saved_100 = without_cache_100 - with_cache_100
    
    print(f"\n100-Operation Session:")
    print(f"  Without cache: {without_cache_100*1000:.0f}ms ({without_cache_100:.2f}s)")
    print(f"  With cache: {with_cache_100*1000:.0f}ms ({with_cache_100:.2f}s)")
    print(f"  Time saved: {saved_100*1000:.0f}ms ({saved_100:.2f}s)")
    print(f"  Improvement: {(saved_100/without_cache_100)*100:.1f}%")
    
    # Cache stats
    stats = get_cache_stats()
    print(f"\nCache Statistics:")
    print(f"  Hits: {stats['hits']}")
    print(f"  Misses: {stats['misses']}")
    print(f"  Hit Rate: {stats['hit_rate']:.1f}%")
    
    print("="*60)
    
    # Assertions
    assert improvement > 90.0, f"Expected >90% improvement, got {improvement:.1f}%"
    assert avg_warm < 0.005, f"Expected <5ms average, got {avg_warm*1000:.2f}ms"
