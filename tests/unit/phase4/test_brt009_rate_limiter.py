"""
Comprehensive tests for RateLimiter (BRT-009 Implementation)

Tests the actual rate_limiter.py implementation with:
- TokenBucket algorithm (capacity, refill rate, consumption)
- RateLimiter multi-scope support (global, per-user, per-endpoint)
- Thread-safe concurrent access
- Error handling and edge cases
- Backoff and wait-until-allowed strategies
"""

import pytest
import threading
import time
from cortex.infrastructure.rate_limiter import (
    TokenBucket,
    RateLimiter,
    RateLimitScope,
    RateLimitConfig,
    get_rate_limiter,
)


class TestTokenBucketBasics:
    """Tests for TokenBucket basic functionality."""

    def test_token_bucket_creation(self) -> None:
        """Verify token bucket initializes with correct values."""
        bucket = TokenBucket(capacity=100, refill_rate=10.0)

        assert bucket.capacity == 100
        assert bucket.refill_rate == 10.0
        assert bucket.tokens == 100.0  # Start with full bucket

    def test_token_bucket_invalid_capacity_raises(self) -> None:
        """Verify invalid capacity raises ValueError."""
        with pytest.raises(ValueError, match="capacity must be > 0"):
            TokenBucket(capacity=0, refill_rate=10.0)

        with pytest.raises(ValueError, match="capacity must be > 0"):
            TokenBucket(capacity=-5, refill_rate=10.0)

    def test_token_bucket_invalid_refill_rate_raises(self) -> None:
        """Verify invalid refill rate raises ValueError."""
        with pytest.raises(ValueError, match="refill_rate must be > 0"):
            TokenBucket(capacity=100, refill_rate=0)

        with pytest.raises(ValueError, match="refill_rate must be > 0"):
            TokenBucket(capacity=100, refill_rate=-1.0)

    def test_token_bucket_consume_success(self) -> None:
        """Verify successful token consumption."""
        bucket = TokenBucket(capacity=10, refill_rate=1.0)

        assert bucket.try_consume(1) is True
        assert bucket.tokens == 9.0

    def test_token_bucket_consume_multiple_tokens(self) -> None:
        """Verify consuming multiple tokens at once."""
        bucket = TokenBucket(capacity=20, refill_rate=1.0)

        assert bucket.try_consume(5) is True
        assert bucket.tokens == 15.0

    def test_token_bucket_consume_exceeds_available(self) -> None:
        """Verify consumption fails when insufficient tokens."""
        bucket = TokenBucket(capacity=10, refill_rate=1.0)

        # Consume all tokens
        assert bucket.try_consume(10) is True

        # Try to consume more
        assert bucket.try_consume(1) is False
        assert abs(bucket.tokens - 0.0) < 0.001  # Allow small timing variance

    def test_token_bucket_refill(self) -> None:
        """Verify tokens refill over time."""
        bucket = TokenBucket(capacity=10, refill_rate=10.0)

        # Consume all tokens
        assert bucket.try_consume(10) is True
        assert bucket.tokens == 0.0

        # Wait for refill
        time.sleep(0.15)  # Should refill ~1.5 tokens

        # Should have some tokens now
        available = bucket.get_available_tokens()
        assert available >= 1.0

    def test_token_bucket_refill_caps_at_capacity(self) -> None:
        """Verify tokens don't exceed capacity."""
        bucket = TokenBucket(capacity=10, refill_rate=100.0)

        # Wait for potential overfill
        time.sleep(1.0)

        available = bucket.get_available_tokens()
        assert available <= 10.0
        assert available == 10.0  # Should be exactly at capacity

    def test_token_bucket_thread_safe(self) -> None:
        """Verify token bucket thread-safe under concurrent access."""
        bucket = TokenBucket(capacity=1000, refill_rate=100.0)
        consumed_count = 0
        consumed_lock = threading.Lock()

        def consume_tokens() -> None:
            nonlocal consumed_count
            for _ in range(10):
                if bucket.try_consume(1):
                    with consumed_lock:
                        consumed_count += 1

        threads = [threading.Thread(target=consume_tokens) for _ in range(20)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Should have consumed some tokens (exact count may vary due to timing)
        assert consumed_count > 0
        assert consumed_count <= 1000


class TestTokenBucketMonitoring:
    """Tests for TokenBucket monitoring features."""

    def test_get_available_tokens(self) -> None:
        """Verify get_available_tokens returns correct count."""
        bucket = TokenBucket(capacity=100, refill_rate=10.0)

        # Immediately should have full capacity
        assert abs(bucket.get_available_tokens() - 100.0) < 0.001

        # After consuming
        bucket.try_consume(30)
        available = bucket.get_available_tokens()
        assert 69.9 < available < 70.1  # Allow for timing variance

    def test_get_time_until_token_when_available(self) -> None:
        """Verify get_time_until_token returns 0 when tokens available."""
        bucket = TokenBucket(capacity=100, refill_rate=10.0)

        wait_time = bucket.get_time_until_token(1)
        assert wait_time == 0.0

    def test_get_time_until_token_when_unavailable(self) -> None:
        """Verify get_time_until_token returns estimated wait."""
        bucket = TokenBucket(capacity=1, refill_rate=1.0)

        # Consume the one token
        bucket.try_consume(1)

        # Get estimated wait time for 1 token
        wait_time = bucket.get_time_until_token(1)
        assert 0.9 < wait_time < 1.2  # Allow small tolerance for timing


class TestRateLimiterGlobal:
    """Tests for RateLimiter with GLOBAL scope."""

    def test_rate_limiter_global_creation(self) -> None:
        """Verify global rate limiter initializes correctly."""
        limiter = RateLimiter(
            capacity=100,
            refill_rate=10.0,
            scope=RateLimitScope.GLOBAL,
        )

        assert limiter.capacity == 100
        assert limiter.refill_rate == 10.0
        assert limiter.scope == RateLimitScope.GLOBAL

    def test_rate_limiter_global_enforces_limit(self) -> None:
        """Verify global rate limiter enforces capacity."""
        limiter = RateLimiter(capacity=3, refill_rate=1.0, scope=RateLimitScope.GLOBAL)

        # Consume up to capacity
        assert limiter.is_allowed() is True
        assert limiter.is_allowed() is True
        assert limiter.is_allowed() is True

        # Exceed capacity
        assert limiter.is_allowed() is False


class TestRateLimiterPerUser:
    """Tests for RateLimiter with PER_USER scope."""

    def test_rate_limiter_per_user_creation(self) -> None:
        """Verify per-user rate limiter initializes correctly."""
        limiter = RateLimiter(
            capacity=50,
            refill_rate=5.0,
            scope=RateLimitScope.PER_USER,
        )

        assert limiter.scope == RateLimitScope.PER_USER

    def test_rate_limiter_per_user_independent_buckets(self) -> None:
        """Verify each user has independent bucket."""
        limiter = RateLimiter(capacity=2, refill_rate=1.0, scope=RateLimitScope.PER_USER)

        # User 1 consumes limit
        assert limiter.is_allowed(user_id="user_1") is True
        assert limiter.is_allowed(user_id="user_1") is True
        assert limiter.is_allowed(user_id="user_1") is False

        # User 2 still has tokens
        assert limiter.is_allowed(user_id="user_2") is True
        assert limiter.is_allowed(user_id="user_2") is True
        assert limiter.is_allowed(user_id="user_2") is False

    def test_rate_limiter_per_user_missing_user_id_raises(self) -> None:
        """Verify missing user_id raises error for per-user scope."""
        limiter = RateLimiter(capacity=100, refill_rate=10.0, scope=RateLimitScope.PER_USER)

        with pytest.raises(ValueError, match="user_id required"):
            limiter.is_allowed()  # Missing user_id


class TestRateLimiterPerEndpoint:
    """Tests for RateLimiter with PER_ENDPOINT scope."""

    def test_rate_limiter_per_endpoint_independent_limits(self) -> None:
        """Verify each endpoint has independent rate limit."""
        limiter = RateLimiter(
            capacity=2,
            refill_rate=1.0,
            scope=RateLimitScope.PER_ENDPOINT,
        )

        # Endpoint /api/users
        assert limiter.is_allowed(endpoint="/api/users") is True
        assert limiter.is_allowed(endpoint="/api/users") is True
        assert limiter.is_allowed(endpoint="/api/users") is False

        # Endpoint /api/data still has limit
        assert limiter.is_allowed(endpoint="/api/data") is True
        assert limiter.is_allowed(endpoint="/api/data") is True


class TestRateLimiterBackoff:
    """Tests for RateLimiter backoff strategies."""

    def test_consume_with_backoff_immediate_success(self) -> None:
        """Verify consume_with_backoff succeeds immediately when available."""
        limiter = RateLimiter(capacity=100, refill_rate=10.0)

        result = limiter.consume_with_backoff()
        assert result is True

    def test_consume_with_backoff_waits_for_token(self) -> None:
        """Verify consume_with_backoff waits for token refill."""
        limiter = RateLimiter(capacity=1, refill_rate=10.0)

        # Consume the token
        assert limiter.consume_with_backoff() is True

        # Try again with backoff (should wait for refill)
        start_time = time.time()
        result = limiter.consume_with_backoff()
        elapsed = time.time() - start_time

        assert result is True
        assert elapsed >= 0.09  # Should have waited at least ~100ms for refill

    def test_consume_with_backoff_timeout(self) -> None:
        """Verify consume_with_backoff times out."""
        limiter = RateLimiter(
            capacity=1,
            refill_rate=0.1,  # Very slow refill
            timeout=0.1,  # Short timeout
        )

        # Consume the token
        assert limiter.consume_with_backoff() is True

        # Try again with backoff (should timeout)
        result = limiter.consume_with_backoff()
        assert result is False

    def test_get_time_until_allowed_per_user(self) -> None:
        """Verify get_time_until_allowed works for per-user."""
        limiter = RateLimiter(capacity=1, refill_rate=1.0, scope=RateLimitScope.PER_USER)

        # Consume user's token
        limiter.is_allowed(user_id="user_1")

        # Get wait time
        wait_time = limiter.get_time_until_allowed(user_id="user_1")
        assert 0.9 < wait_time < 1.2


class TestRateLimiterStatus:
    """Tests for RateLimiter status reporting."""

    def test_get_status_global(self) -> None:
        """Verify status reporting for global limiter."""
        limiter = RateLimiter(capacity=100, refill_rate=10.0)

        status = limiter.get_status()  # type: ignore

        assert status["scope"] == "global"  # type: ignore
        assert status["capacity"] == 100  # type: ignore
        assert status["refill_rate"] == 10.0  # type: ignore

    def test_get_status_per_user_with_users(self) -> None:
        """Verify status reporting includes user count."""
        limiter = RateLimiter(
            capacity=100, refill_rate=10.0, scope=RateLimitScope.PER_USER
        )

        # Add some users
        limiter.is_allowed(user_id="user_1")
        limiter.is_allowed(user_id="user_2")

        status = limiter.get_status()  # type: ignore

        assert status["scope"] == "per_user"  # type: ignore
        assert status["active_users"] == 2  # type: ignore


class TestRateLimiterSingleton:
    """Tests for RateLimiter singleton pattern."""

    def test_get_rate_limiter_creates_instance(self) -> None:
        """Verify get_rate_limiter creates instance."""
        limiter = get_rate_limiter(capacity=100, refill_rate=10.0)

        assert limiter is not None
        assert isinstance(limiter, RateLimiter)

    def test_get_rate_limiter_returns_same_instance(self) -> None:
        """Verify get_rate_limiter returns same instance."""
        limiter1 = get_rate_limiter()
        limiter2 = get_rate_limiter()

        assert limiter1 is limiter2


class TestRateLimitConfig:
    """Tests for RateLimitConfig dataclass."""

    def test_rate_limit_config_creation(self) -> None:
        """Verify RateLimitConfig initializes correctly."""
        config = RateLimitConfig(
            capacity=100,
            refill_rate=10.0,
            scope=RateLimitScope.PER_USER,
            timeout=60.0,
        )

        assert config.capacity == 100
        assert config.refill_rate == 10.0
        assert config.scope == RateLimitScope.PER_USER
        assert config.timeout == 60.0

    def test_rate_limit_config_defaults(self) -> None:
        """Verify RateLimitConfig uses correct defaults."""
        config = RateLimitConfig(capacity=100, refill_rate=10.0)

        assert config.scope == RateLimitScope.GLOBAL
        assert config.timeout == 30.0


class TestRateLimiterIntegration:
    """Integration tests for RateLimiter."""

    def test_multi_user_concurrent_requests(self) -> None:
        """Verify multiple users can make concurrent requests."""
        limiter = RateLimiter(
            capacity=100,
            refill_rate=100.0,
            scope=RateLimitScope.PER_USER,
        )
        results: list[tuple[str, bool]] = []
        results_lock = threading.Lock()

        def make_requests(user_id: str) -> None:
            for _ in range(50):
                if limiter.is_allowed(user_id=user_id):
                    with results_lock:
                        results.append((user_id, True))
                else:
                    with results_lock:
                        results.append((user_id, False))

        threads = [
            threading.Thread(target=make_requests, args=(f"user_{i}",))
            for i in range(5)
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # All users should have some allowed requests
        assert len(results) == 250  # 5 users * 50 requests
        assert any(r[1] for r in results)  # At least some allowed

    def test_rate_limiter_with_refill_during_load(self) -> None:
        """Verify rate limiter refills tokens during load."""
        limiter = RateLimiter(capacity=10, refill_rate=100.0)

        # Exhaust capacity
        for _ in range(10):
            assert limiter.is_allowed() is True

        assert limiter.is_allowed() is False

        # Wait for refill
        time.sleep(0.15)

        # Should have more tokens
        assert limiter.is_allowed() is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
