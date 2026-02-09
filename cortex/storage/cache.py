"""Caching decorator for storage providers."""

import hashlib
import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from cortex.storage.provider import IKnowledgeProvider
from cortex.storage.config import StorageConfig


class CachedKnowledgeProvider(IKnowledgeProvider):
    """
    Decorator that adds L1/L2 caching to any IKnowledgeProvider.
    
    L1 Cache: In-memory with TTL (fast, volatile)
    L2 Cache: Filesystem persistence (slower, persistent)
    
    AC-PHASE50-S5-001: Wraps any IKnowledgeProvider with L1/L2 cache
    AC-PHASE50-S5-002: L1 cache (in-memory) with TTL from StorageConfig.cache_ttl_seconds
    AC-PHASE50-S5-003: L2 cache (filesystem) for persistence across restarts
    AC-PHASE50-S5-004: Cache hits measured in observability metrics
    AC-PHASE50-S5-005: Supports cache bypass via bypass_cache flag
    """

    def __init__(self, provider: IKnowledgeProvider, config: StorageConfig) -> None:
        """
        Initialize CachedKnowledgeProvider.
        
        Args:
            provider: Underlying IKnowledgeProvider to wrap
            config: StorageConfig with cache_enabled, cache_ttl_seconds
        """
        self.provider = provider
        self.config = config
        
        # AC-PHASE50-S5-002: Initialize L1 cache (in-memory)
        self.l1_cache: Dict[str, tuple[str, float]] = {}  # key -> (value, timestamp)
        self.l1_cache_max_size = 500  # Max entries
        self.cache_ttl_seconds = config.cache_ttl_seconds or 3600
        
        # AC-PHASE50-S5-003: Initialize L2 cache (filesystem)
        self.l2_cache_enabled = config.cache_enabled if config.cache_enabled is not None else True
        self.l2_cache_dir = Path.home() / ".cortex" / "cache" / "storage"
        
        if self.l2_cache_enabled:
            self.l2_cache_dir.mkdir(parents=True, exist_ok=True)
            self._load_l2_cache()
        
        # AC-PHASE50-S5-004: Initialize metrics
        self.metrics = {
            "hits": 0,
            "misses": 0,
            "writes": 0,
            "deletes": 0
        }

    def _get_cache_key(self, path: str, method: str) -> str:
        """
        Generate cache key from path and method.
        
        Args:
            path: File path
            method: Method name (read, list, exists)
            
        Returns:
            Cache key
        """
        cache_input = f"{method}:{path}"
        return hashlib.md5(cache_input.encode()).hexdigest()

    def _is_cache_valid(self, timestamp: float) -> bool:
        """
        Check if cached entry is still valid.
        
        Args:
            timestamp: Cache entry timestamp
            
        Returns:
            True if entry is within TTL
        """
        age = time.time() - timestamp
        return age < self.cache_ttl_seconds

    def _evict_old_entries(self) -> None:
        """
        Remove expired entries from L1 cache.
        
        AC-PHASE50-S5-002: Respect TTL for cached entries
        """
        current_time = time.time()
        expired_keys = [
            key for key, (_, timestamp) in self.l1_cache.items()
            if current_time - timestamp >= self.cache_ttl_seconds
        ]
        for key in expired_keys:
            del self.l1_cache[key]

    def _evict_lru_entry(self) -> None:
        """
        Remove least recently used entry if cache is full.
        
        AC-PHASE50-S5-004: Prevent memory bloat
        """
        if len(self.l1_cache) >= self.l1_cache_max_size:
            # Find least recent (oldest timestamp)
            lru_key = min(
                self.l1_cache.keys(),
                key=lambda k: self.l1_cache[k][1]
            )
            del self.l1_cache[lru_key]

    def _load_l2_cache(self) -> None:
        """
        Load L2 cache from filesystem.
        
        AC-PHASE50-S5-003: Load persisted cache on startup
        """
        if not self.l2_cache_dir.exists():
            return
        
        for cache_file in self.l2_cache_dir.glob("*"):
            try:
                if cache_file.is_file() and cache_file.suffix == ".cache":
                    with open(cache_file, "r") as f:
                        data = json.load(f)
                        # Only load if not expired
                        if self._is_cache_valid(data.get("timestamp", 0)):
                            key = cache_file.stem
                            value = data.get("value", "")
                            timestamp = data.get("timestamp", time.time())
                            self.l1_cache[key] = (value, timestamp)
            except Exception:
                # Silently skip corrupted cache files
                pass

    def _save_to_l2_cache(self, key: str, value: str) -> None:
        """
        Save entry to L2 filesystem cache.
        
        AC-PHASE50-S5-003: Persist cache to disk
        
        Args:
            key: Cache key
            value: Cache value
        """
        if not self.l2_cache_enabled:
            return
        
        try:
            cache_file = self.l2_cache_dir / f"{key}.cache"
            data = {
                "value": value,
                "timestamp": time.time()
            }
            with open(cache_file, "w") as f:
                json.dump(data, f)
        except Exception:
            # Silently fail if L2 cache write fails
            pass

    def read(self, path: str, bypass_cache: bool = False) -> str:
        """
        Read with caching.
        
        AC-PHASE50-S5-001: Cache read results
        AC-PHASE50-S5-005: Support bypass_cache parameter
        
        Args:
            path: File path
            bypass_cache: Skip cache and fetch from provider
            
        Returns:
            File content
        """
        if not bypass_cache and self.config.cache_enabled:
            # AC-PHASE50-S5-002: Check L1 cache
            cache_key = self._get_cache_key(path, "read")
            
            if cache_key in self.l1_cache:
                value, timestamp = self.l1_cache[cache_key]
                if self._is_cache_valid(timestamp):
                    self.metrics["hits"] += 1
                    return value
                else:
                    del self.l1_cache[cache_key]
            
            self.metrics["misses"] += 1
        
        # Fetch from provider
        content = self.provider.read(path)
        
        # Store in L1 and L2 cache
        if self.config.cache_enabled and not bypass_cache:
            cache_key = self._get_cache_key(path, "read")
            self._evict_lru_entry()
            self.l1_cache[cache_key] = (content, time.time())
            self._save_to_l2_cache(cache_key, content)
        
        return content

    def write(self, path: str, content: str) -> None:
        """
        Write and invalidate cache.
        
        AC-PHASE50-S5-001: Invalidate cache on write
        
        Args:
            path: File path
            content: Content to write
        """
        # Pass through to provider
        self.provider.write(path, content)
        
        # AC-PHASE50-S5-001: Invalidate related cache entries
        cache_key_read = self._get_cache_key(path, "read")
        cache_key_exists = self._get_cache_key(path, "exists")
        cache_key_list = self._get_cache_key(path.rsplit("/", 1)[0] if "/" in path else "", "list")
        
        for key in [cache_key_read, cache_key_exists, cache_key_list]:
            if key in self.l1_cache:
                del self.l1_cache[key]
            
            cache_file = self.l2_cache_dir / f"{key}.cache"
            if cache_file.exists():
                cache_file.unlink()
        
        self.metrics["writes"] += 1

    def list(self, path: str) -> List[str]:
        """
        List with caching.
        
        AC-PHASE50-S5-001: Cache list results
        
        Args:
            path: Directory path
            
        Returns:
            List of file paths
        """
        if self.config.cache_enabled:
            cache_key = self._get_cache_key(path, "list")
            
            if cache_key in self.l1_cache:
                value, timestamp = self.l1_cache[cache_key]
                if self._is_cache_valid(timestamp):
                    self.metrics["hits"] += 1
                    # Deserialize list
                    return json.loads(value)
            
            self.metrics["misses"] += 1
        
        # Fetch from provider
        entries = self.provider.list(path)
        
        # Store in cache
        if self.config.cache_enabled:
            cache_key = self._get_cache_key(path, "list")
            self._evict_lru_entry()
            self.l1_cache[cache_key] = (json.dumps(entries), time.time())
            self._save_to_l2_cache(cache_key, json.dumps(entries))
        
        return entries

    def exists(self, path: str) -> bool:
        """
        Check existence with caching.
        
        AC-PHASE50-S5-001: Cache exists results
        
        Args:
            path: File path
            
        Returns:
            True if path exists
        """
        if self.config.cache_enabled:
            cache_key = self._get_cache_key(path, "exists")
            
            if cache_key in self.l1_cache:
                value, timestamp = self.l1_cache[cache_key]
                if self._is_cache_valid(timestamp):
                    self.metrics["hits"] += 1
                    return value == "true"
            
            self.metrics["misses"] += 1
        
        # Fetch from provider
        exists = self.provider.exists(path)
        
        # Store in cache
        if self.config.cache_enabled:
            cache_key = self._get_cache_key(path, "exists")
            self._evict_lru_entry()
            self.l1_cache[cache_key] = ("true" if exists else "false", time.time())
            self._save_to_l2_cache(cache_key, "true" if exists else "false")
        
        return exists

    def delete(self, path: str) -> None:
        """
        Delete and invalidate cache.
        
        AC-PHASE50-S5-001: Invalidate cache on delete
        
        Args:
            path: File path
        """
        # Pass through to provider
        self.provider.delete(path)
        
        # AC-PHASE50-S5-001: Invalidate related cache entries
        cache_key_read = self._get_cache_key(path, "read")
        cache_key_exists = self._get_cache_key(path, "exists")
        cache_key_list = self._get_cache_key(path.rsplit("/", 1)[0] if "/" in path else "", "list")
        
        for key in [cache_key_read, cache_key_exists, cache_key_list]:
            if key in self.l1_cache:
                del self.l1_cache[key]
            
            cache_file = self.l2_cache_dir / f"{key}.cache"
            if cache_file.exists():
                cache_file.unlink()
        
        self.metrics["deletes"] += 1
