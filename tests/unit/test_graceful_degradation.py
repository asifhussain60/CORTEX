"""
Tests for Graceful Degradation Handler

AC-NFR-002-01: Graceful degradation on component failure
"""

import pytest
from src.infrastructure.graceful_degradation import (
    GracefulDegradationHandler,
    DegradationLevel,
    FallbackStrategy,
    FallbackResult,
    CacheFallbackStrategy,
    DefaultValueFallbackStrategy,
)


@pytest.fixture
def handler():
    """Create a fresh handler instance."""
    return GracefulDegradationHandler()


@pytest.fixture
def cache_fallback():
    """Create a cache-based fallback."""
    cache = {"key1": "cached_value"}
    return CacheFallbackStrategy(cache, DegradationLevel.DEGRADED)


@pytest.fixture
def default_fallback():
    """Create a default value fallback."""
    return DefaultValueFallbackStrategy("default_result", DegradationLevel.DEGRADED)


class TestGracefulDegradationHandler:
    """Test graceful degradation functionality."""
    
    def test_handler_initializes_with_full_degradation(self, handler):
        """Test handler starts with FULL degradation level."""
        assert handler.get_degradation_level() == DegradationLevel.FULL
        assert not handler.is_degraded()
    
    def test_register_fallback_strategy(self, handler, cache_fallback):
        """Test registering a fallback strategy."""
        handler.register_fallback("test_component", cache_fallback)
        assert "test_component" in handler.fallback_strategies
        assert len(handler.fallback_strategies["test_component"]) == 1
    
    def test_primary_function_succeeds(self, handler, cache_fallback):
        """Test that primary function is called when successful."""
        handler.register_fallback("test_component", cache_fallback)
        
        def primary_fn():
            return "primary_result"
        
        result = handler.execute_with_fallback("test_component", primary_fn)
        assert result.success
        assert result.data == "primary_result"
        assert not result.fallback_used
        assert result.degradation_level == DegradationLevel.FULL
    
    def test_fallback_triggered_on_primary_failure(self, handler, cache_fallback):
        """Test that fallback is triggered when primary fails."""
        handler.register_fallback("test_component", cache_fallback)
        
        def failing_primary():
            raise ValueError("Primary failed")
        
        result = handler.execute_with_fallback("test_component", failing_primary, "key1")
        assert result.success
        assert result.data == "cached_value"
        assert result.fallback_used
        assert result.degradation_level == DegradationLevel.DEGRADED
        assert handler.is_degraded()
    
    def test_multiple_fallback_strategies(self, handler):
        """Test trying multiple fallback strategies."""
        cache = {"key1": "cached"}
        cache_fallback = CacheFallbackStrategy(cache)
        default_fallback = DefaultValueFallbackStrategy("default")
        
        handler.register_fallback("test_component", cache_fallback)
        handler.register_fallback("test_component", default_fallback)
        
        def failing_primary():
            raise ValueError("Primary failed")
        
        # First fallback should succeed
        result = handler.execute_with_fallback("test_component", failing_primary, "key1")
        assert result.success
        assert result.data == "cached"
    
    def test_no_fallback_available(self, handler):
        """Test behavior when no fallback is available."""
        def failing_primary():
            raise ValueError("Primary failed")
        
        result = handler.execute_with_fallback("unknown_component", failing_primary)
        assert not result.success
        assert result.degradation_level == DegradationLevel.UNAVAILABLE
        assert handler.get_degradation_level() == DegradationLevel.UNAVAILABLE
    
    def test_degradation_level_set_to_critical(self, handler):
        """Test setting critical degradation level."""
        critical_fallback = DefaultValueFallbackStrategy(
            "critical_result",
            DegradationLevel.CRITICAL
        )
        handler.register_fallback("test_component", critical_fallback)
        
        def failing_primary():
            raise ValueError("Primary failed")
        
        result = handler.execute_with_fallback("test_component", failing_primary)
        assert result.degradation_level == DegradationLevel.CRITICAL
        assert handler.get_degradation_level() == DegradationLevel.CRITICAL
    
    def test_reset_degradation_state(self, handler, cache_fallback):
        """Test resetting degradation state."""
        handler.register_fallback("test_component", cache_fallback)
        
        def failing_primary():
            raise ValueError("Primary failed")
        
        # Trigger degradation
        result = handler.execute_with_fallback("test_component", failing_primary, "key1")
        assert handler.is_degraded()
        
        # Reset
        handler.reset()
        assert not handler.is_degraded()
        assert handler.get_degradation_level() == DegradationLevel.FULL
    
    def test_failure_count_tracking(self, handler, cache_fallback):
        """Test tracking failure counts."""
        handler.register_fallback("test_component", cache_fallback)
        
        def failing_primary():
            raise ValueError("Primary failed")
        
        # Multiple failures
        for _ in range(3):
            handler.execute_with_fallback("test_component", failing_primary, "key1")
        
        assert handler.failure_count["test_component"] == 3
    
    def test_failure_count_resets_on_success(self, handler):
        """Test that failure count resets on success."""
        def failing_primary():
            raise ValueError("Primary failed")
        
        def successful_primary():
            return "success"
        
        # Trigger failure
        handler.execute_with_fallback("test_component", failing_primary)
        assert handler.failure_count.get("test_component", 0) > 0
        
        # Trigger success
        handler.execute_with_fallback("test_component", successful_primary)
        assert handler.failure_count["test_component"] == 0


class TestCacheFallbackStrategy:
    """Test cache-based fallback strategy."""
    
    def test_cache_hit(self, cache_fallback):
        """Test successful cache hit."""
        result = cache_fallback.execute("key1")
        assert result.success
        assert result.data == "cached_value"
        assert result.fallback_used
    
    def test_cache_miss(self, cache_fallback):
        """Test cache miss."""
        result = cache_fallback.execute("nonexistent")
        assert not result.success
        assert result.error is not None


class TestDefaultValueFallbackStrategy:
    """Test default value fallback strategy."""
    
    def test_default_value_returned(self, default_fallback):
        """Test that default value is returned."""
        result = default_fallback.execute()
        assert result.success
        assert result.data == "default_result"
        assert result.fallback_used
    
    def test_different_default_types(self):
        """Test various default value types."""
        test_cases = [
            ("string", DegradationLevel.DEGRADED),
            (42, DegradationLevel.DEGRADED),
            ({}, DegradationLevel.DEGRADED),
            ([], DegradationLevel.DEGRADED),
        ]
        
        for value, level in test_cases:
            fallback = DefaultValueFallbackStrategy(value, level)
            result = fallback.execute()
            assert result.data == value
            assert result.degradation_level == level


class TestFallbackResult:
    """Test FallbackResult dataclass."""
    
    def test_result_has_timestamp(self):
        """Test that result has timestamp."""
        result = FallbackResult(success=True, data="test")
        assert result.timestamp is not None
    
    def test_result_defaults(self):
        """Test result default values."""
        result = FallbackResult(success=True)
        assert result.data is None
        assert result.error is None
        assert result.degradation_level == DegradationLevel.FULL
        assert not result.fallback_used
