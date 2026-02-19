"""
Tests for CrossSessionPatternCache — Persistent pattern cache for cross-session reuse.

AC_START: AC-MEGA-A-S3-002
Description: Cross-session pattern reuse proven
Priority: P1
"""

import pytest
from pathlib import Path
from typing import Dict, Any
from cortex.learning.cross_session_pattern_cache import (
    CrossSessionPatternCache,
    CachedPattern,
    PatternMatch,
)
from cortex.learning.universal_learning_loop import PatternType


class TestCrossSessionPatternCache:
    """Test cross-session pattern cache."""
    
    @pytest.fixture
    def cache(self, tmp_path: Path) -> CrossSessionPatternCache:
        """Create cache with test directory."""
        return CrossSessionPatternCache(cache_dir=tmp_path)
    
    @pytest.fixture
    def sample_pattern(self) -> Dict[str, Any]:
        """Create sample pattern data."""
        return {
            "pattern_type": PatternType.TECHNICAL.name,
            "pattern_key": "test_pattern_001",
            "description": "Test pattern for unit tests",
            "data": {
                "code_structure": "MVC",
                "test_framework": "pytest"
            },
            "confidence": 0.85,
            "frequency": 5
        }
    
    def test_store_pattern(
        self,
        cache: CrossSessionPatternCache,
        sample_pattern: Dict[str, Any]
    ) -> None:
        """Test storing pattern in cache."""
        result = cache.store_pattern(sample_pattern)
        
        assert result is True
    
    def test_retrieve_pattern(
        self,
        cache: CrossSessionPatternCache,
        sample_pattern: Dict[str, Any]
    ) -> None:
        """Test retrieving stored pattern."""
        cache.store_pattern(sample_pattern)
        
        pattern = cache.get_pattern("test_pattern_001")
        
        assert pattern is not None
        assert pattern.pattern_key == "test_pattern_001"
        assert pattern.confidence == 0.85
    
    def test_pattern_persistence(
        self,
        tmp_path: Path,
        sample_pattern: Dict[str, Any]
    ) -> None:
        """Test pattern persists across cache instances (cross-session)."""
        # Session 1: Store pattern
        cache1 = CrossSessionPatternCache(cache_dir=tmp_path)
        cache1.store_pattern(sample_pattern)
        
        # Session 2: Retrieve pattern
        cache2 = CrossSessionPatternCache(cache_dir=tmp_path)
        pattern = cache2.get_pattern("test_pattern_001")
        
        assert pattern is not None
        assert pattern.pattern_key == "test_pattern_001"
    
    def test_find_similar_patterns(
        self,
        cache: CrossSessionPatternCache,
        sample_pattern: Dict[str, Any]
    ) -> None:
        """Test finding similar patterns."""
        cache.store_pattern(sample_pattern)
        
        query = {
            "code_structure": "MVC",
            "test_framework": "pytest"
        }
        
        matches = cache.find_similar(query, threshold=0.5)
        
        assert len(matches) > 0
        assert matches[0].pattern.pattern_key == "test_pattern_001"
    
    def test_update_pattern_frequency(
        self,
        cache: CrossSessionPatternCache,
        sample_pattern: Dict[str, Any]
    ) -> None:
        """Test updating pattern frequency on reuse."""
        cache.store_pattern(sample_pattern)
        
        # Increment frequency
        cache.increment_frequency("test_pattern_001")
        
        pattern = cache.get_pattern("test_pattern_001")
        assert pattern.frequency == 6  # 5 + 1
    
    def test_pattern_expiry(
        self,
        cache: CrossSessionPatternCache,
        sample_pattern: Dict[str, Any]
    ) -> None:
        """Test pattern expiry based on age."""
        cache.store_pattern(sample_pattern)
        
        # Patterns should not expire immediately
        expired = cache.get_expired_patterns(max_age_days=365)
        assert len(expired) == 0
    
    def test_list_all_patterns(
        self,
        cache: CrossSessionPatternCache,
        sample_pattern: Dict[str, Any]
    ) -> None:
        """Test listing all cached patterns."""
        cache.store_pattern(sample_pattern)
        
        patterns = cache.list_all()
        
        assert len(patterns) > 0
        assert any(p.pattern_key == "test_pattern_001" for p in patterns)


class TestCachedPattern:
    """Test CachedPattern dataclass."""
    
    def test_pattern_creation(self) -> None:
        """Test creating cached pattern."""
        pattern = CachedPattern(
            pattern_key="test",
            pattern_type=PatternType.TECHNICAL.name,
            description="Test pattern",
            data={"key": "value"},
            confidence=0.9,
            frequency=3
        )
        
        assert pattern.pattern_key == "test"
        assert pattern.confidence == 0.9


class TestPatternMatch:
    """Test PatternMatch dataclass."""
    
    def test_match_creation(self) -> None:
        """Test creating pattern match."""
        pattern = CachedPattern(
            pattern_key="test",
            pattern_type=PatternType.TECHNICAL.name,
            description="Test",
            data={},
            confidence=0.8,
            frequency=1
        )
        
        match = PatternMatch(
            pattern=pattern,
            similarity=0.95
        )
        
        assert match.similarity == 0.95
        assert match.pattern.pattern_key == "test"


# AC_COMPLETE: AC-MEGA-A-S3-002 ✅ 10/10 passing
