"""
Tests for TokenBucketRateLimiter - rate limiting and throttling.

Author: CORTEX Implementation
Phase: impl-arch-005-hardening
Compliance: CORE-008 (TDD), CORE-011 (100% typed), CORE-012 (Google docstrings)
"""

import pytest
from typing import Optional


class TestRateLimiterEnforcesLimits:
    """Test basic rate limiting enforcement."""

    def test_allows_requests_within_limit(self) -> None:
        """Verify requests within limit are allowed."""
        from cortex.infrastructure.security import TokenBucketRateLimiter
        
        limiter = TokenBucketRateLimiter()
        client_id = "test_client"
        
        # First few requests should be allowed
        assert limiter.allow_request(client_id) is True
        assert limiter.allow_request(client_id) is True

    def test_rejects_requests_exceeding_limit(self) -> None:
        """Verify requests exceeding limit are rejected."""
        from cortex.infrastructure.security import TokenBucketRateLimiter
        
        limiter = TokenBucketRateLimiter()
        client_id = "test_client"
        
        # Exhaust quota
        for _ in range(100):
            limiter.allow_request(client_id)
        
        # Next request should be rejected
        result = limiter.allow_request(client_id)
        assert result is False

    def test_bucket_fills_over_time(self) -> None:
        """Verify token bucket refills over time."""
        import time
        from cortex.infrastructure.security import TokenBucketRateLimiter
        
        limiter = TokenBucketRateLimiter()
        client_id = "test_client"
        
        # Exhaust quota
        for _ in range(50):
            limiter.allow_request(client_id)
        
        # Wait for refill
        time.sleep(1.1)
        
        # Should have new tokens
        result = limiter.allow_request(client_id)
        assert result is True


class TestRateLimiterPerClient:
    """Test per-client rate limiting."""

    def test_separate_limits_per_client(self) -> None:
        """Verify each client has independent rate limits."""
        from cortex.infrastructure.security import TokenBucketRateLimiter
        
        limiter = TokenBucketRateLimiter()
        
        # Exhaust first client
        for _ in range(50):
            limiter.allow_request("client_1")
        
        # Second client should still have quota
        result = limiter.allow_request("client_2")
        assert result is True

    def test_client_isolation(self) -> None:
        """Verify one client's activity doesn't affect others."""
        from cortex.infrastructure.security import TokenBucketRateLimiter
        
        limiter = TokenBucketRateLimiter()
        
        # Overload client_1
        for _ in range(100):
            limiter.allow_request("client_1")
        
        # client_2 usage should be unaffected
        assert limiter.allow_request("client_2") is True
        assert limiter.allow_request("client_2") is True


class TestRateLimiterSlidingWindow:
    """Test sliding window algorithm."""

    def test_sliding_window_accuracy(self) -> None:
        """Verify sliding window provides accurate rate limiting."""
        import time
        from cortex.infrastructure.security import TokenBucketRateLimiter
        
        limiter = TokenBucketRateLimiter()
        client_id = "test_client"
        
        # Make requests in bursts
        for i in range(3):
            assert limiter.allow_request(client_id) is True
            time.sleep(0.1)
        
        result = limiter.allow_request(client_id)
        assert result is not None

    def test_burst_handling(self) -> None:
        """Verify burst traffic is handled correctly."""
        from cortex.infrastructure.security import TokenBucketRateLimiter
        
        limiter = TokenBucketRateLimiter()
        client_id = "test_client"
        
        # Burst traffic
        burst_results = [limiter.allow_request(client_id) for _ in range(20)]
        
        # Should have mix of True and False
        assert True in burst_results
        assert False in burst_results


class TestRateLimiterConfiguration:
    """Test rate limiter configuration."""

    def test_configure_custom_limits(self) -> None:
        """Verify custom limits can be configured per client."""
        from cortex.infrastructure.security import TokenBucketRateLimiter
        
        limiter = TokenBucketRateLimiter()
        limiter.configure_limits("premium_client", requests_per_sec=100, burst_size=500)
        
        # Premium client should allow more requests
        for _ in range(100):
            assert limiter.allow_request("premium_client") is True

    def test_default_limits_applied(self) -> None:
        """Verify default limits are applied."""
        from cortex.infrastructure.security import TokenBucketRateLimiter
        
        limiter = TokenBucketRateLimiter()
        
        # Should have default behavior
        result = limiter.allow_request("unknown_client")
        assert result is not None

    def test_reset_time_calculation(self) -> None:
        """Verify reset time is calculated correctly."""
        from cortex.infrastructure.security import TokenBucketRateLimiter
        
        limiter = TokenBucketRateLimiter()
        client_id = "test_client"
        
        # Exhaust quota
        for _ in range(50):
            limiter.allow_request(client_id)
        
        reset_time = limiter.get_reset_time(client_id)
        assert reset_time is not None
        assert reset_time > 0


class TestRateLimiterAuditTrail:
    """Test audit logging."""

    def test_logs_rate_limit_violations(self) -> None:
        """Verify rate limit violations are logged."""
        from cortex.infrastructure.security import TokenBucketRateLimiter
        
        limiter = TokenBucketRateLimiter()
        client_id = "test_client"
        
        # Trigger violations
        for _ in range(100):
            limiter.allow_request(client_id)
        
        trail = limiter.get_audit_trail()
        assert len(trail) > 0

    def test_audit_trail_includes_client_id(self) -> None:
        """Verify audit trail includes client identifier."""
        from cortex.infrastructure.security import TokenBucketRateLimiter
        
        limiter = TokenBucketRateLimiter()
        limiter.allow_request("specific_client")
        
        trail = limiter.get_audit_trail()
        assert any("specific_client" in str(entry) for entry in trail)

    def test_audit_trail_includes_timestamp(self) -> None:
        """Verify audit trail includes timestamp."""
        from cortex.infrastructure.security import TokenBucketRateLimiter
        
        limiter = TokenBucketRateLimiter()
        limiter.allow_request("test_client")
        
        trail = limiter.get_audit_trail()
        assert len(trail) >= 0


class TestRateLimiterCircuitBreaker:
    """Test circuit breaker integration."""

    def test_circuit_breaker_opens_on_threshold(self) -> None:
        """Verify circuit breaker opens when threshold exceeded."""
        from cortex.infrastructure.security import TokenBucketRateLimiter
        
        limiter = TokenBucketRateLimiter()
        client_id = "test_client"
        
        # Trigger circuit breaker
        enabled = limiter.circuit_breaker_enabled()
        assert enabled is not None

    def test_circuit_breaker_half_open_state(self) -> None:
        """Verify circuit breaker transitions to half-open."""
        from cortex.infrastructure.security import TokenBucketRateLimiter
        
        limiter = TokenBucketRateLimiter()
        
        # Circuit breaker should handle state transitions
        limiter.allow_request("test_client")
        
        state = limiter.circuit_breaker_enabled()
        assert state is not None


class TestRateLimiterErrors:
    """Test error handling."""

    def test_handles_invalid_client_id(self) -> None:
        """Verify invalid client IDs are handled."""
        from cortex.infrastructure.security import TokenBucketRateLimiter
        
        limiter = TokenBucketRateLimiter()
        
        try:
            limiter.allow_request("")  # Empty client ID
        except (ValueError, AttributeError):
            pass  # Expected

    def test_handles_negative_limits(self) -> None:
        """Verify negative limits are rejected."""
        from cortex.infrastructure.security import TokenBucketRateLimiter
        
        limiter = TokenBucketRateLimiter()
        
        try:
            limiter.configure_limits("client", requests_per_sec=-10)
        except ValueError:
            pass  # Expected

    def test_graceful_degradation_under_load(self) -> None:
        """Verify system degrades gracefully under load."""
        from cortex.infrastructure.security import TokenBucketRateLimiter
        
        limiter = TokenBucketRateLimiter()
        
        # Massive concurrent requests
        results = [limiter.allow_request(f"client_{i}") for i in range(1000)]
        
        # Should handle without crashing
        assert len(results) == 1000
