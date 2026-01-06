"""
Unit Tests for PlanCache
Token Optimization System
"""

import pytest
from pathlib import Path
from src.cache import PlanCache, get_plan_cache


class TestPlanCache:
    """Test suite for PlanCache."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.cache = PlanCache(max_cache_size=10)
        
        # Create test plan file
        self.test_plan_path = Path("test-plan.md")
        self.test_plan_content = """# Test Plan

**Status:** 🟢 ACTIVE

## Phase 1: Discovery
## Phase 2: Implementation  
## Phase 3: Testing

### Deliverables

- D1.1: Requirements document
- D1.2: Architecture design
- D2.1: Code implementation
"""
        self.test_plan_path.write_text(self.test_plan_content)
    
    def teardown_method(self):
        """Cleanup test files."""
        if self.test_plan_path.exists():
            self.test_plan_path.unlink()
    
    def test_cache_initialization(self):
        """Test cache initializes correctly."""
        assert self.cache.max_cache_size == 10
        assert len(self.cache._cache) == 0
    
    def test_get_or_load_caches_plan(self):
        """Test get_or_load loads and caches plan."""
        # First load - should read file
        entry = self.cache.get_or_load("test-plan", self.test_plan_path)
        
        assert entry.plan_id == "test-plan"
        assert entry.content == self.test_plan_content
        assert entry.access_count == 1
        assert "test-plan" in self.cache._cache
    
    def test_get_returns_cached_entry(self):
        """Test get returns cached entry without file read."""
        # Cache plan first
        self.cache.get_or_load("test-plan", self.test_plan_path)
        
        # Get from cache
        entry = self.cache.get("test-plan")
        
        assert entry is not None
        assert entry.plan_id == "test-plan"
        assert entry.access_count == 2  # Incremented
    
    def test_get_returns_none_if_not_cached(self):
        """Test get returns None for uncached plan."""
        entry = self.cache.get("nonexistent-plan")
        assert entry is None
    
    def test_summary_extraction(self):
        """Test summary extraction from plan content."""
        entry = self.cache.get_or_load("test-plan", self.test_plan_path)
        summary = entry.summary
        
        assert summary["title"] == "Test Plan"
        assert len(summary["phases"]) == 3
        assert len(summary["deliverables"]) == 3
        assert "D1.1" in summary["deliverables"]
        assert "D2.1" in summary["deliverables"]
    
    def test_get_summary_lightweight(self):
        """Test get_summary returns summary only."""
        self.cache.get_or_load("test-plan", self.test_plan_path)
        
        summary = self.cache.get_summary("test-plan")
        
        assert summary is not None
        assert "title" in summary
        assert "phases" in summary
        assert "deliverables" in summary
    
    def test_get_content_returns_full_content(self):
        """Test get_content returns full plan content."""
        self.cache.get_or_load("test-plan", self.test_plan_path)
        
        content = self.cache.get_content("test-plan")
        
        assert content == self.test_plan_content
    
    def test_cache_hit_tracking(self):
        """Test cache hit/miss tracking."""
        # First access - miss
        self.cache.get_or_load("test-plan", self.test_plan_path)
        assert self.cache._miss_count == 1
        assert self.cache._hit_count == 0
        
        # Second access - hit
        self.cache.get("test-plan")
        assert self.cache._hit_count == 1
        assert self.cache._miss_count == 1
    
    def test_stats_calculation(self):
        """Test cache statistics calculation."""
        self.cache.get_or_load("test-plan", self.test_plan_path)
        self.cache.get("test-plan")  # Hit
        self.cache.get("test-plan")  # Hit
        
        stats = self.cache.get_stats()
        
        assert stats["cached_plans"] == 1
        assert stats["hit_count"] == 2
        assert stats["miss_count"] == 1
        assert stats["total_requests"] == 3
        assert stats["hit_rate_percent"] == 66.7  # 2/3 = 66.7%
    
    def test_invalidate_removes_plan(self):
        """Test invalidate removes plan from cache."""
        self.cache.get_or_load("test-plan", self.test_plan_path)
        assert "test-plan" in self.cache._cache
        
        result = self.cache.invalidate("test-plan")
        
        assert result is True
        assert "test-plan" not in self.cache._cache
    
    def test_clear_removes_all_plans(self):
        """Test clear removes all cached plans."""
        self.cache.get_or_load("plan1", self.test_plan_path)
        self.cache.get_or_load("plan2", self.test_plan_path)
        
        count = self.cache.clear()
        
        assert count == 2
        assert len(self.cache._cache) == 0
    
    def test_file_change_invalidates_cache(self):
        """Test cache is invalidated when file changes."""
        # Cache original content
        entry1 = self.cache.get_or_load("test-plan", self.test_plan_path)
        original_hash = entry1.file_hash
        
        # Modify file
        self.test_plan_path.write_text(self.test_plan_content + "\n\n## New Phase")
        
        # Load again - should detect change and reload
        entry2 = self.cache.get_or_load("test-plan", self.test_plan_path)
        
        assert entry2.file_hash != original_hash
        assert "## New Phase" in entry2.content
    
    def test_global_cache_instance(self):
        """Test global cache instance."""
        cache1 = get_plan_cache()
        cache2 = get_plan_cache()
        
        # Should return same instance
        assert cache1 is cache2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
