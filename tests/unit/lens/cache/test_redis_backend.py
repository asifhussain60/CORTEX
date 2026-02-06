"""Unit tests for Redis cache backend (integration tests).

Note: These tests mock the redis module since it may not be installed.
Full integration testing requires a running Redis server.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import json


# Mock redis module before any imports
sys.modules['redis'] = MagicMock()


def teardown_function():
    """Clean up test modules after each test."""
    modules_to_clean = [
        'cortex.lens.cache.redis_backend',
        'redis'
    ]
    for mod in modules_to_clean:
        if mod in sys.modules:
            del sys.modules[mod]


class TestRedisBackendConfigValidation:
    """Test configuration validation for RedisBackend."""

    def test_init_invalid_db(self):
        """Backend should reject invalid db values."""
        from cortex.lens.cache.redis_backend import RedisBackend
        
        with pytest.raises(ValueError, match="db must be between 0 and 15"):
            RedisBackend(db=-1)
        
        with pytest.raises(ValueError, match="db must be between 0 and 15"):
            RedisBackend(db=16)

    def test_init_invalid_max_connections(self):
        """Backend should reject invalid max_connections."""
        from cortex.lens.cache.redis_backend import RedisBackend
        
        with pytest.raises(ValueError, match="max_connections must be positive"):
            RedisBackend(max_connections=0)

    def test_init_invalid_socket_timeout(self):
        """Backend should reject invalid socket_connect_timeout."""
        from cortex.lens.cache.redis_backend import RedisBackend
        
        with pytest.raises(ValueError, match="socket_connect_timeout must be positive"):
            RedisBackend(socket_connect_timeout=0)


class TestRedisBackendSerialization:
    """Test JSON serialization/deserialization."""

    def test_serialize_dict(self):
        """Should serialize dictionary to JSON."""
        from cortex.lens.cache.redis_backend import RedisBackend
        
        sys.modules['redis'].from_url.return_value.ping.return_value = True
        
        backend = RedisBackend()
        
        value = {"result": "data", "count": 42}
        result = backend._serialize(value)
        
        assert isinstance(result, str)
        assert json.loads(result) == value

    def test_serialize_list(self):
        """Should serialize list to JSON."""
        from cortex.lens.cache.redis_backend import RedisBackend
        
        sys.modules['redis'].from_url.return_value.ping.return_value = True
        
        backend = RedisBackend()
        
        value = [1, 2, 3, "test"]
        result = backend._serialize(value)
        
        assert json.loads(result) == value

    def test_deserialize_dict(self):
        """Should deserialize JSON dict."""
        from cortex.lens.cache.redis_backend import RedisBackend
        
        sys.modules['redis'].from_url.return_value.ping.return_value = True
        
        backend = RedisBackend()
        
        data = '{"result": "data", "count": 42}'
        result = backend._deserialize(data)
        
        assert result == {"result": "data", "count": 42}

    def test_deserialize_invalid_json(self):
        """Should raise ValueError for invalid JSON."""
        from cortex.lens.cache.redis_backend import RedisBackend
        
        sys.modules['redis'].from_url.return_value.ping.return_value = True
        
        backend = RedisBackend()
        
        with pytest.raises(ValueError):
            backend._deserialize("not valid json {")


class TestRedisBackendInterface:
    """Test RedisBackend interface contract."""

    def test_backend_type_is_redis(self):
        """Backend should identify as Redis type."""
        from cortex.lens.cache.redis_backend import RedisBackend
        
        sys.modules['redis'].from_url.return_value.ping.return_value = True
        
        backend = RedisBackend()
        
        assert backend.backend_type == "redis"

    def test_init_stores_configuration(self):
        """Backend should store initialization configuration."""
        from cortex.lens.cache.redis_backend import RedisBackend
        
        sys.modules['redis'].from_url.return_value.ping.return_value = True
        
        backend = RedisBackend(
            redis_url="redis://custom:6380/2",
            db=3,
            max_connections=50
        )
        
        assert backend.redis_url == "redis://custom:6380/2"
        assert backend.db == 3
        assert backend.max_connections == 50

    def test_statistics_initialized(self):
        """Backend should initialize statistics tracking."""
        from cortex.lens.cache.redis_backend import RedisBackend
        
        sys.modules['redis'].from_url.return_value.ping.return_value = True
        
        backend = RedisBackend()
        stats = backend.get_statistics()
        
        assert stats["hits"] == 0
        assert stats["misses"] == 0
        assert stats["evictions"] == 0
        assert "hit_rate_percent" in stats


class TestRedisBackendDisconnectedBehavior:
    """Test Redis backend behavior when disconnected."""

    def test_get_when_disconnected_returns_none(self):
        """Should return None when Redis not available."""
        from cortex.lens.cache.redis_backend import RedisBackend
        
        sys.modules['redis'].from_url.return_value.ping.side_effect = Exception("Connection refused")
        
        backend = RedisBackend()
        
        result = backend.get("any_key")
        
        assert result is None
        assert backend._statistics["misses"] == 1

    def test_set_when_disconnected_is_safe(self):
        """Should not raise exception when Redis not available."""
        from cortex.lens.cache.redis_backend import RedisBackend
        
        sys.modules['redis'].from_url.return_value.ping.side_effect = Exception("Connection refused")
        
        backend = RedisBackend()
        
        # Should not raise
        backend.set("key", "value", ttl=300)
        assert backend._statistics["set_operations"] == 1


class TestRedisBackendMocked:
    """Test Redis backend with mocked Redis module."""

    def test_get_hit_with_mock(self):
        """Should retrieve value from mocked Redis on hit."""
        from cortex.lens.cache.redis_backend import RedisBackend
        
        mock_client = MagicMock()
        sys.modules['redis'].from_url.return_value = mock_client
        mock_client.ping.return_value = True
        
        backend = RedisBackend()
        
        # Setup mock to return serialized value
        test_value = {"result": "test_data"}
        mock_client.get.return_value = json.dumps(test_value)
        
        result = backend.get("test_key")
        
        assert result == test_value
        assert backend._statistics["hits"] == 1

    def test_set_with_mock(self):
        """Should call Redis SET with TTL on mocked backend."""
        from cortex.lens.cache.redis_backend import RedisBackend
        
        mock_client = MagicMock()
        sys.modules['redis'].from_url.return_value = mock_client
        mock_client.ping.return_value = True
        
        backend = RedisBackend()
        
        test_value = {"data": "test"}
        backend.set("key1", test_value, ttl=300)
        
        # Verify SET was called
        assert mock_client.set.called
        call_args = mock_client.set.call_args
        assert call_args[1]["ex"] == 300  # TTL parameter

    def test_set_invalid_ttl(self):
        """Backend should reject invalid TTL values."""
        from cortex.lens.cache.redis_backend import RedisBackend
        
        mock_client = MagicMock()
        sys.modules['redis'].from_url.return_value = mock_client
        mock_client.ping.return_value = True
        
        backend = RedisBackend()
        
        with pytest.raises(ValueError, match="ttl must be positive"):
            backend.set("key", "value", ttl=0)
        
        with pytest.raises(ValueError, match="ttl must be positive"):
            backend.set("key", "value", ttl=-1)

    def test_invalidate_all_with_mock(self):
        """Should flush Redis on invalidate '*' ."""
        from cortex.lens.cache.redis_backend import RedisBackend
        
        mock_client = MagicMock()
        sys.modules['redis'].from_url.return_value = mock_client
        mock_client.ping.return_value = True
        
        backend = RedisBackend()
        
        backend.invalidate("*")
        
        mock_client.flushdb.assert_called_once()

    def test_invalidate_pattern_with_mock(self):
        """Should delete matching keys on pattern invalidate."""
        from cortex.lens.cache.redis_backend import RedisBackend
        
        mock_client = MagicMock()
        sys.modules['redis'].from_url.return_value = mock_client
        mock_client.ping.return_value = True
        mock_client.keys.return_value = ["key1", "key2"]
        
        backend = RedisBackend()
        
        backend.invalidate("pattern_*")
        
        mock_client.keys.assert_called_once_with("pattern_*")
        mock_client.delete.assert_called_once()
        assert backend._statistics["evictions"] == 2


class TestRedisBackendHealthCheck:
    """Test health check methods."""

    def test_health_check_interface_exists(self):
        """Backend should have health_check method."""
        from cortex.lens.cache.redis_backend import RedisBackend
        
        sys.modules['redis'].from_url.return_value.ping.return_value = True
        
        backend = RedisBackend()
        
        assert hasattr(backend, 'health_check')
        assert callable(backend.health_check)

    def test_get_info_interface_exists(self):
        """Backend should have get_info method."""
        from cortex.lens.cache.redis_backend import RedisBackend
        
        sys.modules['redis'].from_url.return_value.ping.return_value = True
        
        backend = RedisBackend()
        
        assert hasattr(backend, 'get_info')
        assert callable(backend.get_info)

    def test_reconnect_interface_exists(self):
        """Backend should have reconnect method."""
        from cortex.lens.cache.redis_backend import RedisBackend
        
        sys.modules['redis'].from_url.return_value.ping.return_value = True
        
        backend = RedisBackend()
        
        assert hasattr(backend, 'reconnect')
        assert callable(backend.reconnect)


__all__ = ["TestRedisBackendConfigValidation", "TestRedisBackendSerialization"]
