"""
Rate Limiting with Token Bucket Algorithm

Implements request rate limiting to prevent resource exhaustion through
the token bucket algorithm. Supports per-user rate limiting, per-endpoint
rate limiting, and adaptive backoff.

AC-BRT-009: Rate Limiting with Token Bucket Algorithm
- Implement token bucket algorithm (capacity + refill rate)
- Per-user rate limiting (independent buckets per user ID)
- Per-endpoint rate limiting (different limits for different endpoints)
- Support for adaptive backoff (wait for token refill)
- Thread-safe concurrent access
- Configuration via cortex/config/cortex-config.yaml (default: 100 req/sec)

This module provides flexible rate limiting that can be applied at
different levels: global, per-user, or per-endpoint.
"""

import threading
import time
from typing import Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class RateLimitScope(Enum):
    """Scope for rate limiting rules."""
    
    GLOBAL = "global"  # Apply to all requests
    PER_USER = "per_user"  # Apply per user ID
    PER_ENDPOINT = "per_endpoint"  # Apply per endpoint
    PER_USER_ENDPOINT = "per_user_endpoint"  # Apply per user + endpoint combo


@dataclass
class RateLimitConfig:
    """Configuration for rate limiting.
    
    Attributes:
        capacity: Maximum tokens available (burst capacity)
        refill_rate: Tokens added per second
        scope: Scope of rate limiting (global, per_user, etc.)
        timeout: Maximum time to wait for token refill (seconds)
    """
    
    capacity: int  # tokens
    refill_rate: float  # tokens/second
    scope: RateLimitScope = RateLimitScope.GLOBAL
    timeout: float = 30.0  # seconds


class TokenBucket:
    """Token bucket for rate limiting.
    
    Implements the token bucket algorithm for rate limiting:
    - Tokens are added at a constant refill rate
    - Consumers must "spend" tokens to make requests
    - Token count is capped at capacity
    - Thread-safe for concurrent access
    
    Example:
        ```python
        # Allow 10 requests per second, burst capacity 50
        bucket = TokenBucket(capacity=50, refill_rate=10.0)
        
        if bucket.try_consume(1):
            # Process request
        else:
            # Rate limit exceeded
            raise RateLimitExceeded()
        ```
    
    Thread Safety:
        All operations are thread-safe using RLock. Multiple threads can
        attempt to consume tokens concurrently without data corruption.
    """
    
    def __init__(self, capacity: int, refill_rate: float) -> None:
        """Initialize token bucket.
        
        Args:
            capacity: Maximum tokens in bucket
            refill_rate: Tokens added per second
        
        Raises:
            ValueError: If capacity or refill_rate <= 0
        """
        if capacity <= 0:
            raise ValueError(f"capacity must be > 0, got {capacity}")
        if refill_rate <= 0:
            raise ValueError(f"refill_rate must be > 0, got {refill_rate}")
        
        self.capacity = capacity
        self.refill_rate = refill_rate  # tokens per second
        self.tokens = float(capacity)  # Start with full bucket
        self.last_refill = time.time()
        self._lock = threading.RLock()
    
    def try_consume(self, tokens: int = 1) -> bool:
        """Try to consume tokens from the bucket.
        
        Refills tokens based on elapsed time since last refill, then
        attempts to consume the requested number of tokens.
        
        Args:
            tokens: Number of tokens to consume (default 1)
        
        Returns:
            True if tokens were successfully consumed, False if insufficient
        
        Thread Safety:
            Thread-safe. Uses lock to protect token count updates.
        
        Example:
            ```python
            if bucket.try_consume(1):
                print("Request allowed")
            else:
                print("Rate limit exceeded")
            ```
        """
        with self._lock:
            # Refill tokens based on elapsed time
            now = time.time()
            elapsed = now - self.last_refill
            self.tokens = min(
                float(self.capacity),
                self.tokens + elapsed * self.refill_rate,
            )
            self.last_refill = now
            
            # Try to consume tokens
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False
    
    def get_available_tokens(self) -> float:
        """Get current number of available tokens (for monitoring).
        
        Refills tokens based on elapsed time before returning count.
        
        Returns:
            Number of tokens currently available
        """
        with self._lock:
            now = time.time()
            elapsed = now - self.last_refill
            available = min(
                float(self.capacity),
                self.tokens + elapsed * self.refill_rate,
            )
            return available
    
    def get_time_until_token(self, tokens: int = 1) -> float:
        """Get time until requested tokens are available.
        
        Useful for clients implementing backoff strategies.
        
        Args:
            tokens: Number of tokens needed
        
        Returns:
            Time in seconds until tokens available (0 if already available)
        """
        with self._lock:
            now = time.time()
            elapsed = now - self.last_refill
            available = self.tokens + elapsed * self.refill_rate
            
            if available >= tokens:
                return 0.0
            
            # Calculate time needed to refill
            tokens_needed = tokens - available
            time_needed = tokens_needed / self.refill_rate
            return time_needed


class RateLimiter:
    """Rate limiter with multi-level support (global, per-user, per-endpoint).
    
    Provides flexible rate limiting:
    - Global rate limiting across all requests
    - Per-user rate limiting with independent buckets per user
    - Per-endpoint rate limiting with different limits per endpoint
    - Combined per-user-endpoint rate limiting
    
    Example:
        ```python
        # Per-user rate limiting: 100 requests/sec per user
        limiter = RateLimiter(
            capacity=100,
            refill_rate=100.0,
            scope=RateLimitScope.PER_USER
        )
        
        # Check if user_123 is allowed
        if limiter.is_allowed("user_123"):
            print("Request allowed")
        else:
            print("Rate limit exceeded for user_123")
        ```
    
    Thread Safety:
        All operations are thread-safe using RLock. Multiple threads can
        check rate limits concurrently.
    """
    
    def __init__(
        self,
        capacity: int,
        refill_rate: float,
        scope: RateLimitScope = RateLimitScope.GLOBAL,
        timeout: float = 30.0,
    ) -> None:
        """Initialize rate limiter.
        
        Args:
            capacity: Maximum tokens (burst capacity)
            refill_rate: Tokens added per second
            scope: Scope of rate limiting (global, per_user, per_endpoint, etc.)
            timeout: Max wait time for backoff (seconds)
        
        Raises:
            ValueError: If capacity or refill_rate <= 0
        """
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.scope = scope
        self.timeout = timeout
        
        # Create appropriate bucket storage based on scope
        self._global_bucket: Optional[TokenBucket] = None
        self._user_buckets: Dict[str, TokenBucket] = {}
        self._endpoint_buckets: Dict[str, TokenBucket] = {}
        self._user_endpoint_buckets: Dict[Tuple[str, str], TokenBucket] = {}
        
        self._lock = threading.RLock()
        
        # Initialize global bucket if needed
        if scope == RateLimitScope.GLOBAL:
            self._global_bucket = TokenBucket(capacity, refill_rate)
    
    def is_allowed(
        self,
        user_id: Optional[str] = None,
        endpoint: Optional[str] = None,
    ) -> bool:
        """Check if request is allowed under rate limit.
        
        Args:
            user_id: User identifier (required for per-user scope)
            endpoint: Endpoint identifier (required for per-endpoint scope)
        
        Returns:
            True if request is allowed, False if rate limited
        
        Raises:
            ValueError: If required identifier missing for scope
        
        Example:
            ```python
            # Per-user rate limiting
            if limiter.is_allowed(user_id="user_123"):
                process_request()
            else:
                return 429  # Too Many Requests
            ```
        """
        if self.scope == RateLimitScope.GLOBAL:
            if self._global_bucket is None:
                self._global_bucket = TokenBucket(self.capacity, self.refill_rate)
            return self._global_bucket.try_consume(1)
        
        elif self.scope == RateLimitScope.PER_USER:
            if user_id is None:
                raise ValueError("user_id required for PER_USER scope")
            return self._get_user_bucket(user_id).try_consume(1)
        
        elif self.scope == RateLimitScope.PER_ENDPOINT:
            if endpoint is None:
                raise ValueError("endpoint required for PER_ENDPOINT scope")
            return self._get_endpoint_bucket(endpoint).try_consume(1)
        
        elif self.scope == RateLimitScope.PER_USER_ENDPOINT:
            if user_id is None or endpoint is None:
                raise ValueError("user_id and endpoint required for PER_USER_ENDPOINT scope")
            return self._get_user_endpoint_bucket(user_id, endpoint).try_consume(1)
        
        return False
    
    def consume_with_backoff(
        self,
        user_id: Optional[str] = None,
        endpoint: Optional[str] = None,
    ) -> bool:
        """Try to consume token, waiting for refill if necessary.
        
        Implements adaptive backoff: waits up to self.timeout seconds for
        tokens to refill before giving up.
        
        Args:
            user_id: User identifier (required for per-user scope)
            endpoint: Endpoint identifier (required for per-endpoint scope)
        
        Returns:
            True if request eventually allowed, False if timeout
        
        Example:
            ```python
            if limiter.consume_with_backoff(user_id="user_123"):
                process_request()  # After potentially waiting
            else:
                return 429  # Hard rate limit
            ```
        """
        start_time = time.time()
        
        while time.time() - start_time < self.timeout:
            if self.is_allowed(user_id, endpoint):
                return True
            
            # Sleep briefly before retrying
            time.sleep(0.01)
        
        return False
    
    def get_time_until_allowed(
        self,
        user_id: Optional[str] = None,
        endpoint: Optional[str] = None,
    ) -> float:
        """Get time until request will be allowed.
        
        Useful for client-side backoff strategies.
        
        Args:
            user_id: User identifier (required for per-user scope)
            endpoint: Endpoint identifier (required for per-endpoint scope)
        
        Returns:
            Time in seconds until request allowed (0 if already allowed)
        """
        if self.scope == RateLimitScope.GLOBAL:
            if self._global_bucket is None:
                return 0.0
            return self._global_bucket.get_time_until_token(1)
        
        elif self.scope == RateLimitScope.PER_USER:
            if user_id is None:
                return 0.0
            return self._get_user_bucket(user_id).get_time_until_token(1)
        
        elif self.scope == RateLimitScope.PER_ENDPOINT:
            if endpoint is None:
                return 0.0
            return self._get_endpoint_bucket(endpoint).get_time_until_token(1)
        
        elif self.scope == RateLimitScope.PER_USER_ENDPOINT:
            if user_id is None or endpoint is None:
                return 0.0
            return self._get_user_endpoint_bucket(user_id, endpoint).get_time_until_token(1)
        
        return 0.0
    
    def _get_user_bucket(self, user_id: str) -> TokenBucket:
        """Get or create token bucket for user.
        
        Thread-safe creation of per-user buckets.
        """
        with self._lock:
            if user_id not in self._user_buckets:
                self._user_buckets[user_id] = TokenBucket(
                    self.capacity, self.refill_rate
                )
            return self._user_buckets[user_id]
    
    def _get_endpoint_bucket(self, endpoint: str) -> TokenBucket:
        """Get or create token bucket for endpoint.
        
        Thread-safe creation of per-endpoint buckets.
        """
        with self._lock:
            if endpoint not in self._endpoint_buckets:
                self._endpoint_buckets[endpoint] = TokenBucket(
                    self.capacity, self.refill_rate
                )
            return self._endpoint_buckets[endpoint]
    
    def _get_user_endpoint_bucket(
        self, user_id: str, endpoint: str
    ) -> TokenBucket:
        """Get or create token bucket for user+endpoint combo.
        
        Thread-safe creation of per-user-endpoint buckets.
        """
        key = (user_id, endpoint)
        with self._lock:
            if key not in self._user_endpoint_buckets:
                self._user_endpoint_buckets[key] = TokenBucket(
                    self.capacity, self.refill_rate
                )
            return self._user_endpoint_buckets[key]
    
    def get_status(self) -> Dict[str, any]:  # type: ignore
        """Get rate limiter status for monitoring.
        
        Returns monitoring information about the rate limiter state.
        
        Returns:
            Dictionary with:
            - scope: Current rate limiting scope
            - capacity: Burst capacity
            - refill_rate: Tokens per second
            - active_users: Number of active user buckets (if per-user)
            - active_endpoints: Number of active endpoint buckets (if per-endpoint)
        """
        with self._lock:
            status = {
                "scope": self.scope.value,
                "capacity": self.capacity,
                "refill_rate": self.refill_rate,
                "timeout": self.timeout,
            }
            
            if self.scope == RateLimitScope.PER_USER:
                status["active_users"] = len(self._user_buckets)
            elif self.scope == RateLimitScope.PER_ENDPOINT:
                status["active_endpoints"] = len(self._endpoint_buckets)
            elif self.scope == RateLimitScope.PER_USER_ENDPOINT:
                status["active_combinations"] = len(self._user_endpoint_buckets)
            
            return status


# Singleton instance for application-wide use
_rate_limiter: Optional[RateLimiter] = None
_limiter_lock = threading.RLock()


def get_rate_limiter(
    capacity: int = 100,
    refill_rate: float = 100.0,
    scope: RateLimitScope = RateLimitScope.GLOBAL,
) -> RateLimiter:
    """Get or create global rate limiter instance.
    
    Returns:
        Global RateLimiter instance (created on first call)
    
    Args:
        capacity: Initial capacity if creating new instance
        refill_rate: Initial refill rate if creating new instance
        scope: Initial scope if creating new instance
    
    Thread Safety:
        Thread-safe singleton pattern using double-checked locking
    
    Example:
        ```python
        limiter = get_rate_limiter(capacity=100, refill_rate=100.0)
        if limiter.is_allowed(user_id="user_123"):
            process_request()
        ```
    """
    global _rate_limiter
    
    if _rate_limiter is None:
        with _limiter_lock:
            if _rate_limiter is None:
                _rate_limiter = RateLimiter(capacity, refill_rate, scope)
    
    return _rate_limiter
