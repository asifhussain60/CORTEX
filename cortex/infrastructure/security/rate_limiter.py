"""COMPAT shim — cortex.infrastructure.security.rate_limiter → cortex.infrastructure.rate_limiter.

Phase 58-B: zero-import duplicate. Canonical implementation at cortex/infrastructure/rate_limiter.py.
"""
# noqa: F401
from cortex.infrastructure.rate_limiter import RateLimitScope, RateLimitConfig, TokenBucket, RateLimiter, get_rate_limiter

__all__ = ["RateLimitScope", "RateLimitConfig", "TokenBucket", "RateLimiter", "get_rate_limiter"]
