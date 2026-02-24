"""
ISSUE #2: Environment-Specific Timeout Profiles

Provides different timeout values for DEV, TEST, and PROD environments.
"""

import logging
import os
from dataclasses import dataclass
from typing import Dict, Literal, Optional

logger = logging.getLogger(__name__)

EnvironmentType = Literal["development", "test", "production"]


@dataclass
class TimeoutProfile:
    """Timeout configuration for an environment."""

    name: str
    thread_join_ms: int
    http_request_ms: int
    db_query_ms: int
    llm_inference_ms: int
    cache_operation_ms: int
    fallback_timeout_ms: int
    circuit_breaker_threshold_ms: int

    def to_dict(self) -> Dict[str, int]:
        """Export profile as dictionary."""
        return {
            "thread_join_ms": self.thread_join_ms,
            "http_request_ms": self.http_request_ms,
            "db_query_ms": self.db_query_ms,
            "llm_inference_ms": self.llm_inference_ms,
            "cache_operation_ms": self.cache_operation_ms,
            "fallback_timeout_ms": self.fallback_timeout_ms,
            "circuit_breaker_threshold_ms": self.circuit_breaker_threshold_ms,
        }


# Define timeout profiles for each environment
PROFILES: Dict[EnvironmentType, TimeoutProfile] = {
    "development": TimeoutProfile(
        name="development",
        thread_join_ms=5000,              # Generous for debugging
        http_request_ms=30000,            # 30sec for slow networks
        db_query_ms=10000,                # 10sec for big queries in dev
        llm_inference_ms=60000,           # 1 min for LLM experiments
        cache_operation_ms=5000,          # 5sec for cache
        fallback_timeout_ms=15000,        # 15sec for fallbacks
        circuit_breaker_threshold_ms=50,  # Fast trip for testing
    ),
    "test": TimeoutProfile(
        name="test",
        thread_join_ms=1000,              # 1sec for unit tests
        http_request_ms=5000,             # 5sec for integration
        db_query_ms=2000,                 # 2sec for test database
        llm_inference_ms=10000,           # 10sec for test LLM mocks
        cache_operation_ms=1000,          # 1sec for cache
        fallback_timeout_ms=3000,         # 3sec for fallbacks
        circuit_breaker_threshold_ms=30,  # Fast trip for testing
    ),
    "production": TimeoutProfile(
        name="production",
        thread_join_ms=500,               # Very conservative
        http_request_ms=3000,             # 3sec hard limit
        db_query_ms=500,                  # 500ms for queries
        llm_inference_ms=5000,            # 5sec for inference
        cache_operation_ms=500,           # 500ms for cache ops
        fallback_timeout_ms=2000,         # Fail fast to prevent cascades
        circuit_breaker_threshold_ms=100, # Conservative threshold
    ),
}


def get_environment() -> EnvironmentType:
    """
    Get current environment from CORTEX_ENV variable.

    Returns:
        Environment type ("development", "test", or "production")

    Raises:
        ValueError: If CORTEX_ENV is set to unknown value
    """
    env = os.getenv("CORTEX_ENV", "development").lower()

    if env not in PROFILES:
        raise ValueError(
            f"Unknown environment: {env}. "
            f"Must be one of: {list(PROFILES.keys())}"
        )

    return env  # type: ignore


def get_profile(env: Optional[EnvironmentType] = None) -> TimeoutProfile:
    """
    Get timeout profile for specified environment.

    Args:
        env: Environment type. If None, uses current CORTEX_ENV

    Returns:
        TimeoutProfile for the environment
    """
    if env is None:
        env = get_environment()

    if env not in PROFILES:
        raise ValueError(f"Unknown environment: {env}")

    profile = PROFILES[env]
    logger.debug(f"Loaded timeout profile for {env}: {profile.name}")
    return profile


def get_timeout(key: str, env: Optional[EnvironmentType] = None) -> int:
    """
    Get specific timeout value for current environment.

    Args:
        key: Timeout parameter name (e.g., "thread_join_ms")
        env: Environment type. If None, uses current CORTEX_ENV

    Returns:
        Timeout value in milliseconds

    Raises:
        AttributeError: If key is not a valid timeout parameter
    """
    profile = get_profile(env)

    if not hasattr(profile, key):
        valid_keys = list(profile.to_dict().keys())
        raise AttributeError(
            f"Unknown timeout key: {key}. Valid keys: {valid_keys}"
        )

    return getattr(profile, key)


def get_timeout_seconds(key: str, env: Optional[EnvironmentType] = None) -> float:
    """
    Get timeout value in seconds (for use with Python timeouts).

    Args:
        key: Timeout parameter name
        env: Environment type. If None, uses current CORTEX_ENV

    Returns:
        Timeout value in seconds
    """
    ms = get_timeout(key, env)
    return ms / 1000.0


# Export commonly used timeouts as convenience functions
def get_thread_join_timeout() -> float:
    """Get thread.join() timeout in seconds."""
    return get_timeout_seconds("thread_join_ms")


def get_http_timeout() -> float:
    """Get HTTP request timeout in seconds."""
    return get_timeout_seconds("http_request_ms")


def get_db_timeout() -> float:
    """Get database query timeout in seconds."""
    return get_timeout_seconds("db_query_ms")


def get_llm_timeout() -> float:
    """Get LLM inference timeout in seconds."""
    return get_timeout_seconds("llm_inference_ms")


def get_fallback_timeout() -> float:
    """Get fallback chain timeout in seconds."""
    return get_timeout_seconds("fallback_timeout_ms")


if __name__ == "__main__":
    # Example: Show all profiles
    for env_name in ["development", "test", "production"]:
        profile = get_profile(env_name)  # type: ignore
        print(f"\n{env_name.upper()} Profile:")
        for key, value in profile.to_dict().items():
            print(f"  {key}: {value}ms")
