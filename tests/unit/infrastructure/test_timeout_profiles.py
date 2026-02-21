"""
Tests for Issue #2: Environment-Specific Timeout Profiles

Validates timeout configuration for different environments.
"""

import pytest
import os
from cortex.core.config.timeout_profiles import (
    TimeoutProfile,
    get_environment,
    get_profile,
    get_timeout,
    get_timeout_seconds,
    get_thread_join_timeout,
    get_http_timeout,
    get_db_timeout,
    get_llm_timeout,
    get_fallback_timeout,
    PROFILES,
)


class TestTimeoutProfile:
    """Test TimeoutProfile dataclass."""
    
    def test_profile_to_dict(self):
        """Profile should export to dictionary."""
        profile = PROFILES["production"]
        data = profile.to_dict()
        
        assert isinstance(data, dict)
        assert "thread_join_ms" in data
        assert "http_request_ms" in data
        assert data["thread_join_ms"] == 500
    
    def test_profile_attributes(self):
        """Profile should have all timeout attributes."""
        profile = PROFILES["development"]
        
        assert hasattr(profile, "thread_join_ms")
        assert hasattr(profile, "http_request_ms")
        assert hasattr(profile, "db_query_ms")
        assert hasattr(profile, "llm_inference_ms")
        assert hasattr(profile, "cache_operation_ms")
        assert hasattr(profile, "fallback_timeout_ms")
        assert hasattr(profile, "circuit_breaker_threshold_ms")


class TestEnvironmentDetection:
    """Test environment detection."""
    
    def test_default_environment(self):
        """Default environment should be development."""
        # Ensure env var is not set
        if "CORTEX_ENV" in os.environ:
            del os.environ["CORTEX_ENV"]
        
        env = get_environment()
        assert env in ["development", "test", "production"]
    
    def test_environment_from_env_var(self):
        """Environment should be read from CORTEX_ENV."""
        os.environ["CORTEX_ENV"] = "test"
        env = get_environment()
        assert env == "test"
        
        os.environ["CORTEX_ENV"] = "production"
        env = get_environment()
        assert env == "production"
        
        # Cleanup
        if "CORTEX_ENV" in os.environ:
            del os.environ["CORTEX_ENV"]
    
    def test_invalid_environment_raises(self):
        """Invalid environment should raise ValueError."""
        os.environ["CORTEX_ENV"] = "invalid_env"
        
        with pytest.raises(ValueError, match="Unknown environment"):
            get_environment()
        
        # Cleanup
        if "CORTEX_ENV" in os.environ:
            del os.environ["CORTEX_ENV"]


class TestProfileRetrieval:
    """Test getting timeout profiles."""
    
    def test_get_all_profiles(self):
        """All profiles should be retrievable."""
        for env in ["development", "test", "production"]:
            profile = get_profile(env)  # type: ignore
            assert profile.name == env
    
    def test_dev_profile_generous(self):
        """Dev profile should have generous timeouts."""
        dev = get_profile("development")  # type: ignore
        
        assert dev.thread_join_ms > 1000  # >= 5000
        assert dev.http_request_ms > 10000  # >= 30000
    
    def test_test_profile_moderate(self):
        """Test profile should have moderate timeouts."""
        test = get_profile("test")  # type: ignore
        
        assert 500 < test.thread_join_ms < 5000
        assert 2000 < test.http_request_ms < 10000
    
    def test_prod_profile_conservative(self):
        """Prod profile should have conservative timeouts."""
        prod = get_profile("production")  # type: ignore
        
        assert prod.thread_join_ms < 1000  # <= 500
        assert prod.http_request_ms < 5000  # <= 3000
    
    def test_dev_more_generous_than_prod(self):
        """Dev timeouts should be more generous than prod."""
        dev = get_profile("development")  # type: ignore
        prod = get_profile("production")  # type: ignore
        
        assert dev.thread_join_ms > prod.thread_join_ms
        assert dev.http_request_ms > prod.http_request_ms
        assert dev.llm_inference_ms > prod.llm_inference_ms
    
    def test_test_between_dev_and_prod(self):
        """Test timeouts should be between dev and prod."""
        dev = get_profile("development")  # type: ignore
        test = get_profile("test")  # type: ignore
        prod = get_profile("production")  # type: ignore
        
        assert dev.thread_join_ms >= test.thread_join_ms >= prod.thread_join_ms
        assert dev.http_request_ms >= test.http_request_ms >= prod.http_request_ms


class TestTimeoutRetrieval:
    """Test getting specific timeout values."""
    
    def test_get_timeout_by_name(self):
        """Should be able to get timeout by parameter name."""
        timeout = get_timeout("thread_join_ms", "development")
        assert timeout == PROFILES["development"].thread_join_ms
    
    def test_get_timeout_invalid_key_raises(self):
        """Invalid timeout key should raise AttributeError."""
        with pytest.raises(AttributeError, match="Unknown timeout key"):
            get_timeout("invalid_key", "development")
    
    def test_get_timeout_in_seconds(self):
        """Timeout in seconds should convert correctly."""
        ms = get_timeout("thread_join_ms", "development")
        sec = get_timeout_seconds("thread_join_ms", "development")
        
        assert sec == ms / 1000.0
    
    def test_convenience_functions(self):
        """Convenience functions should work."""
        # Set environment
        os.environ["CORTEX_ENV"] = "test"
        
        # All should return floats (seconds)
        thread_timeout = get_thread_join_timeout()
        assert isinstance(thread_timeout, float)
        assert thread_timeout > 0
        
        http_timeout = get_http_timeout()
        assert isinstance(http_timeout, float)
        assert http_timeout > 0
        
        db_timeout = get_db_timeout()
        assert isinstance(db_timeout, float)
        assert db_timeout > 0
        
        llm_timeout = get_llm_timeout()
        assert isinstance(llm_timeout, float)
        assert llm_timeout > 0
        
        fallback_timeout = get_fallback_timeout()
        assert isinstance(fallback_timeout, float)
        assert fallback_timeout > 0
        
        # Cleanup
        if "CORTEX_ENV" in os.environ:
            del os.environ["CORTEX_ENV"]


class TestEnvironmentConsistency:
    """Test consistency across environments."""
    
    def test_all_profiles_have_same_keys(self):
        """All profiles should have same timeout keys."""
        keys_list = [set(p.to_dict().keys()) for p in PROFILES.values()]
        
        # All should be equal
        first_keys = keys_list[0]
        for keys in keys_list[1:]:
            assert keys == first_keys
    
    def test_all_timeouts_positive(self):
        """All timeout values should be positive."""
        for env_name, profile in PROFILES.items():
            for key, value in profile.to_dict().items():
                assert value > 0, f"{env_name}.{key} is not positive"
    
    def test_profile_completeness(self):
        """All profiles should have 7 timeout values."""
        expected_count = 7
        
        for env_name, profile in PROFILES.items():
            timeout_dict = profile.to_dict()
            assert len(timeout_dict) == expected_count, \
                f"{env_name} has {len(timeout_dict)} timeouts, expected {expected_count}"


class TestTimeoutApplications:
    """Test how timeouts are used in real scenarios."""
    
    def test_dev_allows_debugging(self):
        """Dev environment should allow long-running operations."""
        dev = get_profile("development")  # type: ignore
        
        # Should have generous limits for debugging
        assert dev.thread_join_ms >= 5000
        assert dev.llm_inference_ms >= 60000
    
    def test_prod_prevents_cascades(self):
        """Prod environment should fail fast to prevent cascades."""
        prod = get_profile("production")  # type: ignore
        
        # Should have tight limits
        assert prod.thread_join_ms <= 500
        assert prod.db_query_ms <= 500
        assert prod.fallback_timeout_ms <= 2000
    
    def test_test_balances_speed_and_reliability(self):
        """Test environment should balance test speed and accuracy."""
        test = get_profile("test")  # type: ignore
        dev = get_profile("development")  # type: ignore
        
        # Should be faster than dev for quick test runs
        assert test.thread_join_ms < dev.thread_join_ms


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
