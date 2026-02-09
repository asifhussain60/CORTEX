"""
Phase 52 S5: Production Integration Tests (20+ tests)
"""

import pytest
import asyncio
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent / "cortex" / "orchestrators" / "pr_review"))

from production_client import (
    RateLimiter, RateLimitStrategy, RateLimitInfo, ErrorType,
    RetryStrategy, ConnectionPool, ProductionGitHubClient, IntegrationMetrics
)


class TestRateLimiter:
    """Test rate limiting"""

    def test_rate_limiter_creation(self):
        """Test creating rate limiter"""
        limiter = RateLimiter()
        assert limiter.strategy == RateLimitStrategy.EXPONENTIAL_BACKOFF
        assert limiter.rate_limit_info is None

    def test_check_limits_no_info(self):
        """Test check limits with no info"""
        limiter = RateLimiter()
        within_limits, wait_time = limiter.check_limits()
        assert within_limits
        assert wait_time is None

    def test_check_limits_within(self):
        """Test check limits when within limits"""
        limiter = RateLimiter()
        info = RateLimitInfo(
            limit=5000,
            remaining=100,
            reset_time=int(datetime.now().timestamp()) + 3600
        )
        limiter.update_limits(info)
        
        within_limits, wait_time = limiter.check_limits()
        assert within_limits
        assert wait_time is None

    def test_check_limits_exceeded(self):
        """Test check limits when exceeded"""
        limiter = RateLimiter()
        info = RateLimitInfo(
            limit=5000,
            remaining=0,
            reset_time=int(datetime.now().timestamp()) + 60
        )
        limiter.update_limits(info)
        
        within_limits, wait_time = limiter.check_limits()
        assert not within_limits
        assert wait_time is not None
        assert wait_time > 0

    def test_exponential_backoff(self):
        """Test exponential backoff calculation"""
        limiter = RateLimiter(RateLimitStrategy.EXPONENTIAL_BACKOFF)
        
        wait_0 = limiter.get_wait_time(0)
        wait_1 = limiter.get_wait_time(1)
        wait_2 = limiter.get_wait_time(2)
        
        assert wait_0 == 1
        assert wait_1 == 2
        assert wait_2 == 4

    def test_linear_backoff(self):
        """Test linear backoff calculation"""
        limiter = RateLimiter(RateLimitStrategy.LINEAR_BACKOFF)
        
        wait_0 = limiter.get_wait_time(0)
        wait_1 = limiter.get_wait_time(1)
        wait_2 = limiter.get_wait_time(2)
        
        assert wait_0 == 0
        assert wait_1 == 10
        assert wait_2 == 20


class TestRetryStrategy:
    """Test retry logic"""

    def test_retry_strategy_creation(self):
        """Test creating retry strategy"""
        strategy = RetryStrategy()
        assert strategy.max_retries == 3
        assert strategy.backoff_factor == 2.0

    def test_should_retry_rate_limit(self):
        """Test retry on rate limit error"""
        strategy = RetryStrategy(max_retries=3)
        assert strategy.should_retry(ErrorType.RATE_LIMIT, 0)
        assert strategy.should_retry(ErrorType.RATE_LIMIT, 1)
        assert not strategy.should_retry(ErrorType.RATE_LIMIT, 3)

    def test_should_retry_auth_error(self):
        """Test no retry on auth error"""
        strategy = RetryStrategy()
        assert not strategy.should_retry(ErrorType.AUTH_ERROR, 0)

    def test_should_retry_invalid_request(self):
        """Test no retry on invalid request"""
        strategy = RetryStrategy()
        assert not strategy.should_retry(ErrorType.INVALID_REQUEST, 0)

    def test_backoff_time_calculation(self):
        """Test backoff time calculation"""
        strategy = RetryStrategy(backoff_factor=2.0)
        
        time_0 = strategy.get_backoff_time(0)
        time_1 = strategy.get_backoff_time(1)
        time_2 = strategy.get_backoff_time(2)
        
        assert time_0 == 0.5
        assert time_1 == 1.0
        assert time_2 == 2.0


class TestConnectionPool:
    """Test connection pooling"""

    def test_connection_pool_creation(self):
        """Test creating connection pool"""
        pool = ConnectionPool(max_connections=5)
        assert pool.max_connections == 5
        assert pool.active_connections == 0

    def test_acquire_connection(self):
        """Test acquiring connection"""
        pool = ConnectionPool(max_connections=2)
        
        conn1 = pool.acquire()
        assert conn1 is not None
        assert pool.active_connections == 1
        
        conn2 = pool.acquire()
        assert conn2 is not None
        assert pool.active_connections == 2
        
        conn3 = pool.acquire()
        assert conn3 is None  # Pool full
        assert pool.active_connections == 2

    def test_release_connection(self):
        """Test releasing connection"""
        pool = ConnectionPool(max_connections=2)
        
        conn = pool.acquire()
        assert pool.active_connections == 1
        
        result = pool.release(conn)
        assert result
        assert pool.active_connections == 0

    def test_pool_stats(self):
        """Test pool statistics"""
        pool = ConnectionPool(max_connections=5)
        pool.acquire()
        pool.acquire()
        
        stats = pool.get_pool_stats()
        assert stats["active_connections"] == 2
        assert stats["available_slots"] == 3
        assert stats["max_connections"] == 5


class TestIntegrationMetrics:
    """Test integration metrics"""

    def test_metrics_creation(self):
        """Test creating metrics"""
        metrics = IntegrationMetrics()
        assert metrics.total_requests == 0
        assert metrics.successful_requests == 0
        assert metrics.failed_requests == 0
        assert isinstance(metrics.error_count_by_type, dict)

    def test_metrics_tracking(self):
        """Test tracking metrics"""
        metrics = IntegrationMetrics()
        metrics.total_requests = 100
        metrics.successful_requests = 95
        metrics.failed_requests = 5
        metrics.error_count_by_type["rate_limit"] = 3
        metrics.error_count_by_type["timeout"] = 2
        
        assert metrics.total_requests == 100
        assert len(metrics.error_count_by_type) == 2


class TestProductionGitHubClient:
    """Test production GitHub client"""

    @pytest.mark.asyncio
    async def test_client_creation(self):
        """Test creating production client"""
        client = ProductionGitHubClient("token123")
        assert client.token == "token123"
        assert client.rate_limiter is not None
        assert client.retry_strategy is not None
        assert client.connection_pool is not None

    @pytest.mark.asyncio
    async def test_fetch_pr_success(self):
        """Test successful PR fetch"""
        client = ProductionGitHubClient("token123")
        result = await client.fetch_pr("owner", "repo", 123)
        
        assert result is not None
        assert client.metrics.total_requests == 1
        assert client.metrics.successful_requests == 1

    @pytest.mark.asyncio
    async def test_connection_pool_usage(self):
        """Test connection pool is used"""
        client = ProductionGitHubClient("token123")
        
        result = await client.fetch_pr("owner", "repo", 123)
        
        stats = client.connection_pool.get_pool_stats()
        assert stats["active_connections"] == 0  # Released after use

    @pytest.mark.asyncio
    async def test_error_classification(self):
        """Test error classification"""
        client = ProductionGitHubClient("token123")
        
        assert client._classify_error("429 Too Many Requests") == ErrorType.RATE_LIMIT.value
        assert client._classify_error("401 Unauthorized") == ErrorType.AUTH_ERROR.value
        assert client._classify_error("500 Server Error") == ErrorType.SERVER_ERROR.value

    def test_get_metrics(self):
        """Test getting metrics"""
        client = ProductionGitHubClient("token123")
        metrics = client.get_metrics()
        
        assert isinstance(metrics, IntegrationMetrics)
        assert metrics.total_requests == 0

    def test_health_status(self):
        """Test health status"""
        client = ProductionGitHubClient("token123")
        client.metrics.total_requests = 100
        client.metrics.successful_requests = 99
        client.metrics.failed_requests = 1
        client.metrics.average_response_time_ms = 150.0
        
        status = client.get_health_status()
        assert "healthy" in status
        assert "error_rate" in status
        assert status["error_rate"] == 0.01


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
