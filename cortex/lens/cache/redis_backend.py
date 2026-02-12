"""Redis distributed cache backend for production."""

import json
import logging
from abc import ABC
from typing import Any, Dict, Optional

from cortex.lens.cache.lens_cache import LENSCache

logger = logging.getLogger(__name__)


class RedisConnectionError(Exception):
    """Raised when Redis connection fails."""
    pass


class RedisBackend(LENSCache):
    """Redis distributed cache backend.

    Suitable for production deployments with multiple processes.
    Features: Distributed cache, TTL support, persistence options.

    Requirements:
    - Redis server running (default: localhost:6379)
    - redis-py package installed

    Note:
        This implementation is designed for distributed systems.
        Falls back gracefully when Redis is unavailable.
    """

    def __init__(self,
                 redis_url: str = "redis://localhost:6379/0",
                 db: int = 0,
                 max_connections: int = 10,
                 socket_connect_timeout: int = 5,
                 socket_keepalive: bool = True):
        """Initialize Redis backend.

        Args:
            redis_url: Redis connection URL (default: localhost:6379)
            db: Database number (default: 0)
            max_connections: Max connection pool size (default: 10)
            socket_connect_timeout: Connection timeout in seconds
            socket_keepalive: Enable TCP keepalive

        Raises:
            ValueError: If redis_url or db invalid
        """
        super().__init__(backend_type="redis")

        if db < 0 or db > 15:
            raise ValueError("db must be between 0 and 15")
        if max_connections <= 0:
            raise ValueError("max_connections must be positive")
        if socket_connect_timeout <= 0:
            raise ValueError("socket_connect_timeout must be positive")

        self.redis_url = redis_url
        self.db = db
        self.max_connections = max_connections
        self.socket_connect_timeout = socket_connect_timeout
        self.socket_keepalive = socket_keepalive

        self._redis_client = None
        self._connection_pool = None
        self._connected = False

        # Try to initialize connection
        self._init_connection()

    def _init_connection(self) -> None:
        """Initialize Redis connection pool.

        Note:
            Lazy connection - connection attempted on first use.
        """
        try:
            import redis

            self._redis_client = redis.from_url(
                self.redis_url,
                db=self.db,
                max_connections=self.max_connections,
                socket_connect_timeout=self.socket_connect_timeout,
                socket_keepalive=self.socket_keepalive,
                decode_responses=True  # Return strings, not bytes
            )

            # Test connection
            self._redis_client.ping()
            self._connected = True

        except ImportError:
            logger.warning("redis-py not installed. Install with: pip install redis")
            self._connected = False
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}. Cache disabled.")
            self._connected = False

    def _serialize(self, value: Any) -> str:
        """Serialize value to JSON string.

        Args:
            value: Value to serialize

        Returns:
            JSON string representation
        """
        try:
            return json.dumps(value, default=str)
        except Exception as e:
            logger.error(f"Serialization error: {e}")
            raise ValueError(f"Cannot serialize value: {e}")

    def _deserialize(self, data: str) -> Any:
        """Deserialize JSON string to Python object.

        Args:
            data: JSON string

        Returns:
            Deserialized Python object
        """
        try:
            return json.loads(data)
        except Exception as e:
            logger.error(f"Deserialization error: {e}")
            raise ValueError(f"Cannot deserialize value: {e}")

    def get(self, key: str) -> Optional[Any]:
        """Retrieve value from Redis cache.

        Args:
            key: Cache key

        Returns:
            Cached value if found and not expired, else None

        Note:
            Redis handles TTL automatically via EX.
            Missing keys return None (not a miss if Redis unavailable).
        """
        self._statistics["get_operations"] += 1

        if not self._connected or self._redis_client is None:
            self._statistics["misses"] += 1
            return None

        try:
            # Redis GET - automatically handles expired keys
            data = self._redis_client.get(key)

            if data is None:
                self._statistics["misses"] += 1
                return None

            # Deserialize and return
            value = self._deserialize(data)
            self._statistics["hits"] += 1
            return value

        except Exception as e:
            logger.warning(f"Redis GET error for key {key}: {e}")
            self._statistics["misses"] += 1
            return None

    def set(self, key: str, value: Any, ttl: int = 300) -> None:
        """Store value in Redis cache with TTL.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (default: 300)

        Raises:
            ValueError: If ttl invalid

        Note:
            Uses Redis EX (expire in seconds) for TTL.
            Gracefully continues if Redis unavailable.
        """
        if ttl <= 0:
            raise ValueError("ttl must be positive")

        self._statistics["set_operations"] += 1

        if not self._connected or self._redis_client is None:
            return  # Silently skip if Redis unavailable

        try:
            # Serialize value
            data = self._serialize(value)

            # Set with TTL (EX = expire in seconds)
            self._redis_client.set(key, data, ex=ttl)

        except Exception as e:
            logger.warning(f"Redis SET error for key {key}: {e}")

    def invalidate(self, pattern: str = "*") -> None:
        """Invalidate cache entries matching pattern.

        Args:
            pattern: Glob pattern (e.g., "analyze_*", "*" for all)

        Note:
            Uses Redis KEYS command for pattern matching.
            Then uses DEL for removal.
        """
        if not self._connected or self._redis_client is None:
            return  # Silently skip if Redis unavailable

        try:
            if pattern == "*":
                # Flush all keys in current DB
                self._redis_client.flushdb()
                return

            # Find keys matching pattern
            keys = self._redis_client.keys(pattern)

            if keys:
                # Delete matching keys
                self._redis_client.delete(*keys)
                self._statistics["evictions"] += len(keys)

        except Exception as e:
            logger.warning(f"Redis INVALIDATE error for pattern {pattern}: {e}")

    def health_check(self) -> Dict[str, Any]:
        """Check Redis connection health.

        Returns:
            Dictionary with:
            - connected: Boolean (True if connected)
            - latency_ms: Ping latency in milliseconds
            - error: Error message if disconnected
        """
        if not self._connected or self._redis_client is None:
            return {
                "connected": False,
                "latency_ms": None,
                "error": "Not initialized"
            }

        try:
            # Measure ping latency
            import time
            start = time.time()
            self._redis_client.ping()
            latency_ms = (time.time() - start) * 1000

            return {
                "connected": True,
                "latency_ms": round(latency_ms, 2),
                "error": None
            }

        except Exception as e:
            return {
                "connected": False,
                "latency_ms": None,
                "error": str(e)
            }

    def get_info(self) -> Dict[str, Any]:
        """Get Redis server information.

        Returns:
            Dictionary with Redis info (memory, keys, operations, etc.)
            Empty dict if Redis unavailable
        """
        if not self._connected or self._redis_client is None:
            return {}

        try:
            info = self._redis_client.info()

            return {
                "used_memory_mb": round(info.get("used_memory", 0) / (1024 * 1024), 2),
                "total_keys": self._redis_client.dbsize(),
                "connected_clients": info.get("connected_clients", 0),
                "commands_processed": info.get("total_commands_processed", 0),
                "uptime_seconds": info.get("uptime_in_seconds", 0)
            }

        except Exception as e:
            logger.warning(f"Redis INFO error: {e}")
            return {}

    def reconnect(self) -> bool:
        """Attempt to reconnect to Redis.

        Returns:
            True if successful, False otherwise
        """
        self._init_connection()
        return self._connected


__all__ = ["RedisBackend", "RedisConnectionError"]
