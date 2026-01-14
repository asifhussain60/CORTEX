"""
Tests for Rate Limiter middleware.

This module provides comprehensive tests for rate limiting including:
- Token bucket algorithm
- Sliding window rate limiting
- Per-operation rate limits
- Burst handling

Author: CORTEX
Feature: feat05-resilience Phase 1
Correlation ID: FEAT05-P1-T1.2
"""

import pytest
import time
import threading
from datetime import datetime, timedelta

from src.orchestrators.middleware.rate_limiter import (
    RateLimiter,
    RateLimit,
    RateLimitExceeded,
    RateLimitAlgorithm
)


class TestRateLimit:
    """Tests for RateLimit configuration."""
    
    def test_create_rate_limit(self):
        """Test creating a rate limit configuration."""
        limit = RateLimit(
            requests_per_second=10,
            burst_size=20,
            algorithm=RateLimitAlgorithm.TOKEN_BUCKET
        )
        
        assert limit.requests_per_second == 10
        assert limit.burst_size == 20
        assert limit.algorithm == RateLimitAlgorithm.TOKEN_BUCKET
        
    def test_default_rate_limit(self):
        """Test default rate limit values."""
        limit = RateLimit(requests_per_second=5)
        
        assert limit.requests_per_second == 5
        assert limit.burst_size == 5  # Default to same as rate
        assert limit.algorithm == RateLimitAlgorithm.TOKEN_BUCKET
        
    def test_validate_rate_limit(self):
        """Test rate limit validation."""
        # Valid limit
        limit = RateLimit(requests_per_second=10)
        limit.validate()
        
        # Invalid rate
        with pytest.raises(ValueError, match="requests_per_second must be positive"):
            RateLimit(requests_per_second=0).validate()
            
        # Invalid burst
        with pytest.raises(ValueError, match="burst_size must be positive"):
            RateLimit(requests_per_second=10, burst_size=0).validate()


class TestTokenBucketAlgorithm:
    """Tests for token bucket rate limiting."""
    
    @pytest.fixture
    def limiter(self):
        """Create rate limiter with token bucket."""
        return RateLimiter()
        
    def test_allow_requests_within_rate(self, limiter):
        """Test allowing requests within rate limit."""
        limiter.set_rate_limit("test_op", RateLimit(requests_per_second=10))
        
        # Should allow multiple requests
        for _ in range(5):
            result = limiter.check_rate_limit("test_op")
            assert result is True
            
    def test_block_requests_exceeding_rate(self, limiter):
        """Test blocking requests that exceed rate limit."""
        limiter.set_rate_limit("test_op", RateLimit(requests_per_second=2, burst_size=2))
        
        # Allow burst
        assert limiter.check_rate_limit("test_op") is True
        assert limiter.check_rate_limit("test_op") is True
        
        # Exceed rate - should block
        assert limiter.check_rate_limit("test_op") is False
        
    def test_token_refill_over_time(self, limiter):
        """Test that tokens refill over time."""
        limiter.set_rate_limit("test_op", RateLimit(requests_per_second=10, burst_size=5))
        
        # Use all tokens
        for _ in range(5):
            limiter.check_rate_limit("test_op")
            
        # Should block immediately
        assert limiter.check_rate_limit("test_op") is False
        
        # Wait for token refill (100ms = 1 token at 10/sec rate)
        time.sleep(0.15)
        
        # Should allow again
        assert limiter.check_rate_limit("test_op") is True
        
    def test_burst_handling(self, limiter):
        """Test burst size allows temporary spike."""
        limiter.set_rate_limit("test_op", RateLimit(requests_per_second=1, burst_size=5))
        
        # Should allow burst
        for _ in range(5):
            assert limiter.check_rate_limit("test_op") is True
            
        # Exceed burst
        assert limiter.check_rate_limit("test_op") is False


class TestSlidingWindowAlgorithm:
    """Tests for sliding window rate limiting."""
    
    @pytest.fixture
    def limiter(self):
        """Create rate limiter with sliding window."""
        return RateLimiter()
        
    def test_sliding_window_enforcement(self, limiter):
        """Test sliding window tracks requests over time."""
        limiter.set_rate_limit(
            "test_op",
            RateLimit(
                requests_per_second=5,
                algorithm=RateLimitAlgorithm.SLIDING_WINDOW
            )
        )
        
        # Make 5 requests
        for _ in range(5):
            assert limiter.check_rate_limit("test_op") is True
            
        # Exceed limit
        assert limiter.check_rate_limit("test_op") is False
        
    def test_sliding_window_expiry(self, limiter):
        """Test that old requests expire from window."""
        limiter.set_rate_limit(
            "test_op",
            RateLimit(
                requests_per_second=2,
                algorithm=RateLimitAlgorithm.SLIDING_WINDOW
            )
        )
        
        # Make 2 requests
        limiter.check_rate_limit("test_op")
        limiter.check_rate_limit("test_op")
        
        # Should be at limit
        assert limiter.check_rate_limit("test_op") is False
        
        # Wait for window to slide (1.1 seconds to ensure full window expired)
        time.sleep(1.1)
        
        # Should allow new requests after window expired
        assert limiter.check_rate_limit("test_op") is True


class TestRateLimiter:
    """Tests for RateLimiter middleware."""
    
    @pytest.fixture
    def limiter(self):
        """Create rate limiter for testing."""
        return RateLimiter()
        
    def test_initialization(self, limiter):
        """Test limiter initialization."""
        assert limiter is not None
        
    def test_set_rate_limit(self, limiter):
        """Test setting a rate limit."""
        limit = RateLimit(requests_per_second=100)
        limiter.set_rate_limit("api_call", limit)
        
        stats = limiter.get_rate_stats("api_call")
        assert stats['limit_per_second'] == 100
        
    def test_multiple_operations(self, limiter):
        """Test different rate limits for different operations."""
        limiter.set_rate_limit("fast_op", RateLimit(requests_per_second=100))
        limiter.set_rate_limit("slow_op", RateLimit(requests_per_second=1))
        
        # Fast op should allow many
        for _ in range(10):
            assert limiter.check_rate_limit("fast_op") is True
            
        # Slow op should limit
        assert limiter.check_rate_limit("slow_op") is True
        assert limiter.check_rate_limit("slow_op") is False
        
    def test_rate_limit_context_manager(self, limiter):
        """Test context manager for rate limiting."""
        limiter.set_rate_limit("test_op", RateLimit(requests_per_second=5))
        
        # Should succeed within limit
        with limiter.limit_rate("test_op"):
            pass
            
    def test_rate_limit_context_manager_exceeds(self, limiter):
        """Test context manager raises when limit exceeded."""
        limiter.set_rate_limit("test_op", RateLimit(requests_per_second=1, burst_size=1))
        
        # Use up the token
        with limiter.limit_rate("test_op"):
            pass
            
        # Should raise on second immediate attempt
        with pytest.raises(RateLimitExceeded):
            with limiter.limit_rate("test_op"):
                pass
                
    def test_get_rate_stats(self, limiter):
        """Test getting rate limit statistics."""
        limiter.set_rate_limit("test_op", RateLimit(requests_per_second=10, burst_size=20))
        
        # Make some requests
        for _ in range(3):
            limiter.check_rate_limit("test_op")
            
        stats = limiter.get_rate_stats("test_op")
        
        assert "limit_per_second" in stats
        assert "requests_made" in stats
        assert "tokens_available" in stats
        assert stats['limit_per_second'] == 10
        assert stats['requests_made'] == 3
        
    def test_reset_rate_limit(self, limiter):
        """Test resetting rate limit."""
        limiter.set_rate_limit("test_op", RateLimit(requests_per_second=1, burst_size=1))
        
        # Use up token
        limiter.check_rate_limit("test_op")
        assert limiter.check_rate_limit("test_op") is False
        
        # Reset
        limiter.reset_rate_limit("test_op")
        
        # Should work again
        assert limiter.check_rate_limit("test_op") is True
        
    def test_no_rate_limit_set(self, limiter):
        """Test behavior when no rate limit is set."""
        # Should allow unlimited
        result = limiter.check_rate_limit("unlimited_op")
        assert result is True


class TestConcurrentRateLimiting:
    """Tests for concurrent access to rate limiter."""
    
    def test_concurrent_requests(self):
        """Test rate limiting with concurrent requests."""
        limiter = RateLimiter()
        limiter.set_rate_limit("test_op", RateLimit(requests_per_second=50, burst_size=50))
        
        results = []
        
        def worker(worker_id: int):
            result = limiter.check_rate_limit("test_op")
            results.append((worker_id, result))
            
        threads = [threading.Thread(target=worker, args=(i,)) for i in range(40)]
        
        for t in threads:
            t.start()
            
        for t in threads:
            t.join()
            
        # Should allow all within burst size
        allowed = sum(1 for _, result in results if result)
        assert allowed == 40
        
    def test_concurrent_rate_limit_enforcement(self):
        """Test that rate limits are enforced under concurrent load."""
        limiter = RateLimiter()
        limiter.set_rate_limit("test_op", RateLimit(requests_per_second=10, burst_size=10))
        
        results = []
        
        def worker(worker_id: int):
            result = limiter.check_rate_limit("test_op")
            results.append(result)
            
        threads = [threading.Thread(target=worker, args=(i,)) for i in range(20)]
        
        for t in threads:
            t.start()
            
        for t in threads:
            t.join()
            
        # Should allow only up to burst size
        allowed = sum(1 for result in results if result)
        assert allowed <= 10


class TestRateLimitExceededError:
    """Tests for RateLimitExceeded exception."""
    
    def test_error_creation(self):
        """Test error creation with details."""
        error = RateLimitExceeded(
            message="Rate limit exceeded",
            operation="test_op",
            limit_per_second=10,
            retry_after_seconds=0.5
        )
        
        assert str(error) == "Rate limit exceeded"
        assert error.operation == "test_op"
        assert error.limit_per_second == 10
        assert error.retry_after_seconds == 0.5
        
    def test_error_details(self):
        """Test error details dictionary."""
        error = RateLimitExceeded(
            message="Too many requests",
            operation="api_call",
            limit_per_second=100,
            retry_after_seconds=0.01
        )
        
        details = error.get_details()
        
        assert details["operation"] == "api_call"
        assert details["limit_per_second"] == 100
        assert details["retry_after_seconds"] == 0.01


class TestIntegration:
    """Integration tests for rate limiter."""
    
    def test_real_world_api_limiting(self):
        """Test realistic API rate limiting scenario."""
        limiter = RateLimiter()
        
        # Simulate API with 10 req/sec, burst of 20
        limiter.set_rate_limit(
            "external_api",
            RateLimit(requests_per_second=10, burst_size=20)
        )
        
        successful = 0
        failed = 0
        
        # Try 30 requests rapidly
        for _ in range(30):
            if limiter.check_rate_limit("external_api"):
                successful += 1
            else:
                failed += 1
                
        # Should allow burst, then start blocking
        assert successful == 20
        assert failed == 10
        
    def test_gradual_recovery(self):
        """Test that rate limit gradually recovers."""
        limiter = RateLimiter()
        limiter.set_rate_limit("test_op", RateLimit(requests_per_second=10, burst_size=5))
        
        # Exhaust burst
        for _ in range(5):
            limiter.check_rate_limit("test_op")
            
        # Should block
        assert limiter.check_rate_limit("test_op") is False
        
        # Wait for partial recovery
        time.sleep(0.2)  # 2 tokens at 10/sec
        
        # Should allow 2 more
        assert limiter.check_rate_limit("test_op") is True
        assert limiter.check_rate_limit("test_op") is True
        assert limiter.check_rate_limit("test_op") is False
        
    def test_mixed_operations_independent_limits(self):
        """Test that different operations have independent limits."""
        limiter = RateLimiter()
        
        limiter.set_rate_limit("op_a", RateLimit(requests_per_second=1, burst_size=1))
        limiter.set_rate_limit("op_b", RateLimit(requests_per_second=100, burst_size=100))
        
        # Exhaust op_a
        limiter.check_rate_limit("op_a")
        
        # op_a should block
        assert limiter.check_rate_limit("op_a") is False
        
        # op_b should still work
        assert limiter.check_rate_limit("op_b") is True
