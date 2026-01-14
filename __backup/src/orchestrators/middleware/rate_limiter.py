"""
Rate Limiter Middleware - CORTEX 6.0

Implements rate limiting with multiple algorithms:
- Token bucket (smooth rate limiting with burst)
- Sliding window (precise time-based limiting)

Author: CORTEX Autonomous Executor
Feature: feat05-resilience Phase 1
Correlation ID: FEAT05-P1-T1.2
"""

import time
import threading
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Optional, List
from contextlib import contextmanager
from collections import deque

from src.orchestrators.audit_logger import EnterpriseAuditLogger, AuditLevel, AuditCategory


class RateLimitAlgorithm(Enum):
    """Rate limiting algorithms."""
    TOKEN_BUCKET = "token_bucket"
    SLIDING_WINDOW = "sliding_window"


@dataclass
class RateLimit:
    """Rate limit configuration."""
    requests_per_second: float
    burst_size: Optional[int] = None
    algorithm: RateLimitAlgorithm = RateLimitAlgorithm.TOKEN_BUCKET
    
    def __post_init__(self):
        """Set defaults after initialization."""
        if self.burst_size is None:
            self.burst_size = int(self.requests_per_second)
            
    def validate(self):
        """Validate rate limit configuration."""
        if self.requests_per_second <= 0:
            raise ValueError("requests_per_second must be positive")
        if self.burst_size <= 0:
            raise ValueError("burst_size must be positive")


class RateLimitExceeded(Exception):
    """Exception raised when rate limit is exceeded."""
    
    def __init__(
        self,
        message: str,
        operation: str,
        limit_per_second: float,
        retry_after_seconds: float
    ):
        super().__init__(message)
        self.operation = operation
        self.limit_per_second = limit_per_second
        self.retry_after_seconds = retry_after_seconds
        
    def get_details(self) -> Dict:
        """Get error details as dictionary."""
        return {
            "operation": self.operation,
            "limit_per_second": self.limit_per_second,
            "retry_after_seconds": self.retry_after_seconds
        }


class TokenBucket:
    """Token bucket rate limiter implementation."""
    
    def __init__(self, rate: float, burst_size: int):
        """
        Initialize token bucket.
        
        Args:
            rate: Tokens per second
            burst_size: Maximum bucket capacity
        """
        self.rate = rate
        self.burst_size = burst_size
        self.tokens = float(burst_size)
        self.last_update = time.time()
        self._lock = threading.Lock()
        
    def consume(self, tokens: int = 1) -> bool:
        """
        Try to consume tokens.
        
        Args:
            tokens: Number of tokens to consume
            
        Returns:
            True if tokens were available, False otherwise
        """
        with self._lock:
            now = time.time()
            elapsed = now - self.last_update
            
            # Refill tokens based on elapsed time
            self.tokens = min(
                self.burst_size,
                self.tokens + (elapsed * self.rate)
            )
            self.last_update = now
            
            # Try to consume
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False
            
    def get_tokens_available(self) -> float:
        """Get current number of available tokens."""
        with self._lock:
            now = time.time()
            elapsed = now - self.last_update
            return min(
                self.burst_size,
                self.tokens + (elapsed * self.rate)
            )
            
    def reset(self):
        """Reset bucket to full capacity."""
        with self._lock:
            self.tokens = float(self.burst_size)
            self.last_update = time.time()


class SlidingWindow:
    """Sliding window rate limiter implementation."""
    
    def __init__(self, rate: float):
        """
        Initialize sliding window.
        
        Args:
            rate: Requests per second
        """
        self.rate = rate
        self.window_size = 1.0  # 1 second window
        self.requests: deque = deque()
        self._lock = threading.Lock()
        
    def check(self) -> bool:
        """
        Check if request is allowed.
        
        Returns:
            True if request is allowed, False otherwise
        """
        with self._lock:
            now = time.time()
            window_start = now - self.window_size
            
            # Remove expired requests
            while self.requests and self.requests[0] < window_start:
                self.requests.popleft()
                
            # Check if we're within rate
            if len(self.requests) < self.rate:
                self.requests.append(now)
                return True
            return False
            
    def get_request_count(self) -> int:
        """Get number of requests in current window."""
        with self._lock:
            now = time.time()
            window_start = now - self.window_size
            
            # Remove expired
            while self.requests and self.requests[0] < window_start:
                self.requests.popleft()
                
            return len(self.requests)
            
    def reset(self):
        """Reset window."""
        with self._lock:
            self.requests.clear()


class RateLimiter:
    """
    Middleware for enforcing rate limits on orchestrator operations.
    
    Features:
    - Token bucket algorithm (smooth limiting with burst)
    - Sliding window algorithm (precise time-based limiting)
    - Per-operation rate limits
    - Thread-safe operation
    - Audit logging integration
    
    Usage:
        limiter = RateLimiter()
        limiter.set_rate_limit("api_call", RateLimit(requests_per_second=10, burst_size=20))
        
        if limiter.check_rate_limit("api_call"):
            # Make API call
            pass
        else:
            # Rate limited, wait
            pass
    """
    
    def __init__(self, audit_logger: Optional[EnterpriseAuditLogger] = None):
        """Initialize rate limiter."""
        self.audit_logger = audit_logger or EnterpriseAuditLogger()
        self._limits: Dict[str, RateLimit] = {}
        self._buckets: Dict[str, TokenBucket] = {}
        self._windows: Dict[str, SlidingWindow] = {}
        self._request_counts: Dict[str, int] = {}
        self._lock = threading.RLock()
        
        self.audit_logger.log(
            level=AuditLevel.INFO,
            category=AuditCategory.MIDDLEWARE,
            component="rate_limiter",
            operation="initialize",
            message="Rate limiter initialized",
            correlation_id="FEAT05-P1-T1.2",
            context={"status": "initialized"}
        )
        
    def set_rate_limit(self, operation: str, limit: RateLimit):
        """
        Set rate limit for an operation.
        
        Args:
            operation: Operation name
            limit: Rate limit configuration
        """
        limit.validate()
        
        with self._lock:
            self._limits[operation] = limit
            self._request_counts[operation] = 0
            
            # Initialize appropriate algorithm
            if limit.algorithm == RateLimitAlgorithm.TOKEN_BUCKET:
                self._buckets[operation] = TokenBucket(
                    rate=limit.requests_per_second,
                    burst_size=limit.burst_size
                )
            else:  # SLIDING_WINDOW
                self._windows[operation] = SlidingWindow(
                    rate=limit.requests_per_second
                )
                
            self.audit_logger.log(
                level=AuditLevel.INFO,
                category=AuditCategory.MIDDLEWARE,
                component="rate_limiter",
                operation="set_rate_limit",
                message=f"Rate limit set for {operation}",
                correlation_id="FEAT05-P1-T1.2",
                context={
                    "operation": operation,
                    "requests_per_second": limit.requests_per_second,
                    "burst_size": limit.burst_size,
                    "algorithm": limit.algorithm.value
                }
            )
            
    def check_rate_limit(self, operation: str) -> bool:
        """
        Check if operation is within rate limit.
        
        Args:
            operation: Operation name
            
        Returns:
            True if operation is allowed, False if rate limited
        """
        with self._lock:
            # No limit set - allow
            if operation not in self._limits:
                return True
                
            limit = self._limits[operation]
            allowed = False
            
            if limit.algorithm == RateLimitAlgorithm.TOKEN_BUCKET:
                bucket = self._buckets[operation]
                allowed = bucket.consume(1)
            else:  # SLIDING_WINDOW
                window = self._windows[operation]
                allowed = window.check()
                
            if allowed:
                self._request_counts[operation] += 1
            else:
                self.audit_logger.log(
                    level=AuditLevel.WARNING,
                    category=AuditCategory.MIDDLEWARE,
                    component="rate_limiter",
                    operation="rate_limit_exceeded",
                    message=f"Rate limit exceeded for {operation}",
                    correlation_id="FEAT05-P1-T1.2",
                    context={
                        "operation": operation,
                        "limit_per_second": limit.requests_per_second
                    }
                )
                
            return allowed
            
    @contextmanager
    def limit_rate(self, operation: str):
        """
        Context manager for rate limiting.
        
        Args:
            operation: Operation name
            
        Raises:
            RateLimitExceeded: If rate limit is exceeded
        """
        if not self.check_rate_limit(operation):
            limit = self._limits.get(operation)
            retry_after = 1.0 / limit.requests_per_second if limit else 1.0
            
            raise RateLimitExceeded(
                message=f"Rate limit exceeded for operation: {operation}",
                operation=operation,
                limit_per_second=limit.requests_per_second if limit else 0,
                retry_after_seconds=retry_after
            )
            
        yield
        
    def get_rate_stats(self, operation: str) -> Dict:
        """
        Get rate limit statistics for an operation.
        
        Args:
            operation: Operation name
            
        Returns:
            Dictionary with rate limit stats
        """
        with self._lock:
            if operation not in self._limits:
                return {
                    "limit_per_second": 0,
                    "requests_made": 0,
                    "tokens_available": 0
                }
                
            limit = self._limits[operation]
            stats = {
                "limit_per_second": limit.requests_per_second,
                "burst_size": limit.burst_size,
                "algorithm": limit.algorithm.value,
                "requests_made": self._request_counts.get(operation, 0)
            }
            
            if limit.algorithm == RateLimitAlgorithm.TOKEN_BUCKET:
                bucket = self._buckets[operation]
                stats["tokens_available"] = bucket.get_tokens_available()
            else:  # SLIDING_WINDOW
                window = self._windows[operation]
                stats["requests_in_window"] = window.get_request_count()
                
            return stats
            
    def reset_rate_limit(self, operation: str):
        """
        Reset rate limit for an operation.
        
        Args:
            operation: Operation name
        """
        with self._lock:
            if operation in self._request_counts:
                self._request_counts[operation] = 0
                
            if operation in self._buckets:
                self._buckets[operation].reset()
                
            if operation in self._windows:
                self._windows[operation].reset()
                
            self.audit_logger.log(
                level=AuditLevel.INFO,
                category=AuditCategory.MIDDLEWARE,
                component="rate_limiter",
                operation="reset_rate_limit",
                message=f"Rate limit reset for {operation}",
                correlation_id="FEAT05-P1-T1.2",
                context={"operation": operation}
            )
