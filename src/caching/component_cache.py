"""
CORTEX Component Caching System

Caches initialized CORTEX components (tier APIs, agents, orchestrators) to avoid
redundant initialization overhead on repeated CLI invocations.

Based on ValidationCache pattern from Phase 1 optimization with TTL and
intelligent invalidation.

Cached Components:
    - Tier APIs (Tier1API, KnowledgeGraph, ContextIntelligence)
    - Template Loader (parsed YAML templates)
    - Frequently-used agents (IntentRouter, PlanningAgent, etc.)
    - Session Manager
    - Brain Protector

Performance:
    - Cache hit: <5ms (vs ~500-2000ms initialization)
    - Cache miss: Normal init time + 10ms cache overhead
    - TTL: 1 hour (configurable)
    - Hit rate target: 80-90% for repeated commands

Usage:
    from src.caching.component_cache import ComponentCache
    
    cache = ComponentCache()
    
    # Try cache first
    tier1 = cache.get_tier1_api()
    if tier1 is None:
        # Cache miss - initialize
        tier1 = Tier1API(db_path, log_path)
        cache.set_tier1_api(tier1)
    
    # Subsequent calls are instant
    tier1 = cache.get_tier1_api()  # <5ms

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import time
import pickle
import hashlib
import sqlite3
from pathlib import Path
from typing import Optional, Any, Dict, List
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class ComponentCache:
    """
    Cache for initialized CORTEX components.
    
    Stores components in memory with SQLite persistence for cross-session caching.
    Uses TTL (time-to-live) for automatic invalidation.
    
    Features:
    - In-memory cache for instant access
    - SQLite persistence for cross-session reuse
    - TTL-based invalidation (default: 1 hour)
    - Version-aware (invalidates on CORTEX upgrade)
    - Size limits to prevent memory bloat
    
    Example:
        cache = ComponentCache()
        
        # Get or initialize Tier1 API
        tier1 = cache.get_or_create('tier1_api', lambda: Tier1API(...))
        
        # Manual cache management
        cache.invalidate('tier1_api')
        cache.clear_all()
    """
    
    def __init__(
        self,
        cache_path: Optional[Path] = None,
        ttl_seconds: int = 3600,  # 1 hour
        max_memory_mb: int = 100
    ):
        """
        Initialize component cache.
        
        Args:
            cache_path: Path to SQLite cache database
            ttl_seconds: Time-to-live for cached components (default: 1 hour)
            max_memory_mb: Maximum memory usage for cache (default: 100MB)
        """
        if cache_path is None:
            from src.config import config
            cache_path = Path(config.brain_path) / "cache" / "components.db"
        
        self.cache_path = Path(cache_path)
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.ttl_seconds = ttl_seconds
        self.max_memory_mb = max_memory_mb
        
        # In-memory cache (fastest access)
        self._memory_cache: Dict[str, Any] = {}
        self._cache_times: Dict[str, datetime] = {}
        
        # Initialize database
        self._init_db()
        
        # Get CORTEX version for cache invalidation
        self._version = self._get_version()
    
    def _init_db(self):
        """Initialize SQLite database schema."""
        with sqlite3.connect(str(self.cache_path)) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS component_cache (
                    component_key TEXT PRIMARY KEY,
                    component_data BLOB,
                    cached_at TEXT,
                    expires_at TEXT,
                    version TEXT,
                    size_bytes INTEGER
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_expires_at
                ON component_cache(expires_at)
            """)
            
            conn.commit()
    
    def get(self, component_key: str) -> Optional[Any]:
        """
        Get component from cache.
        
        Args:
            component_key: Unique key for component (e.g., 'tier1_api')
        
        Returns:
            Cached component or None if not found/expired
        """
        start_time = time.perf_counter()
        
        # Check memory cache first
        if component_key in self._memory_cache:
            # Check TTL
            if self._is_valid(component_key):
                elapsed = (time.perf_counter() - start_time) * 1000
                logger.debug(f"Cache hit (memory): {component_key} ({elapsed:.2f}ms)")
                return self._memory_cache[component_key]
            else:
                # Expired - remove from memory
                del self._memory_cache[component_key]
                del self._cache_times[component_key]
        
        # Check database cache
        component = self._load_from_db(component_key)
        if component is not None:
            # Load into memory for faster next access
            self._memory_cache[component_key] = component
            self._cache_times[component_key] = datetime.now()
            
            elapsed = (time.perf_counter() - start_time) * 1000
            logger.debug(f"Cache hit (database): {component_key} ({elapsed:.2f}ms)")
            return component
        
        elapsed = (time.perf_counter() - start_time) * 1000
        logger.debug(f"Cache miss: {component_key} ({elapsed:.2f}ms)")
        return None
    
    def set(self, component_key: str, component: Any, persist: bool = True):
        """
        Store component in cache.
        
        Args:
            component_key: Unique key for component
            component: Component to cache
            persist: Whether to persist to database (default: True)
        """
        start_time = time.perf_counter()
        
        # Store in memory
        self._memory_cache[component_key] = component
        self._cache_times[component_key] = datetime.now()
        
        # Persist to database if requested
        if persist:
            self._save_to_db(component_key, component)
        
        elapsed = (time.perf_counter() - start_time) * 1000
        logger.debug(f"Cached: {component_key} ({elapsed:.2f}ms)")
    
    def get_or_create(self, component_key: str, factory: callable) -> Any:
        """
        Get component from cache or create if not found.
        
        Args:
            component_key: Unique key for component
            factory: Function to create component if not cached
        
        Returns:
            Cached or newly created component
        
        Example:
            tier1 = cache.get_or_create(
                'tier1_api',
                lambda: Tier1API(db_path, log_path)
            )
        """
        component = self.get(component_key)
        if component is not None:
            return component
        
        # Cache miss - create component
        start_time = time.perf_counter()
        component = factory()
        elapsed = (time.perf_counter() - start_time) * 1000
        logger.debug(f"Created component: {component_key} ({elapsed:.2f}ms)")
        
        # Cache for next time
        self.set(component_key, component)
        
        return component
    
    def invalidate(self, component_key: str):
        """
        Invalidate cached component.
        
        Args:
            component_key: Component to invalidate
        """
        # Remove from memory
        if component_key in self._memory_cache:
            del self._memory_cache[component_key]
            del self._cache_times[component_key]
        
        # Remove from database
        with sqlite3.connect(str(self.cache_path)) as conn:
            conn.execute(
                "DELETE FROM component_cache WHERE component_key = ?",
                (component_key,)
            )
            conn.commit()
        
        logger.debug(f"Invalidated: {component_key}")
    
    def clear_all(self):
        """Clear all cached components."""
        # Clear memory
        self._memory_cache.clear()
        self._cache_times.clear()
        
        # Clear database
        with sqlite3.connect(str(self.cache_path)) as conn:
            conn.execute("DELETE FROM component_cache")
            conn.commit()
        
        logger.info("Cache cleared")
    
    def clear_expired(self) -> int:
        """
        Remove expired components from cache.
        
        Returns:
            Number of components cleared
        """
        now = datetime.now()
        expired_keys = []
        
        # Check memory cache
        for key, cached_at in self._cache_times.items():
            if now - cached_at > timedelta(seconds=self.ttl_seconds):
                expired_keys.append(key)
        
        # Remove expired from memory
        for key in expired_keys:
            del self._memory_cache[key]
            del self._cache_times[key]
        
        # Remove expired from database
        with sqlite3.connect(str(self.cache_path)) as conn:
            conn.execute(
                "DELETE FROM component_cache WHERE expires_at < ?",
                (now.isoformat(),)
            )
            conn.commit()
        
        if expired_keys:
            logger.info(f"Cleared {len(expired_keys)} expired components")
        
        return len(expired_keys)
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dict with cache stats
        """
        with sqlite3.connect(str(self.cache_path)) as conn:
            cursor = conn.execute("""
                SELECT
                    COUNT(*) as total_components,
                    SUM(size_bytes) as total_size_bytes,
                    COUNT(CASE WHEN expires_at > ? THEN 1 END) as valid_components
                FROM component_cache
            """, (datetime.now().isoformat(),))
            
            row = cursor.fetchone()
            db_components, db_size, valid_components = row
        
        return {
            'memory_components': len(self._memory_cache),
            'database_components': db_components or 0,
            'valid_components': valid_components or 0,
            'database_size_mb': (db_size or 0) / (1024 * 1024),
            'ttl_seconds': self.ttl_seconds,
            'version': self._version
        }
    
    def _is_valid(self, component_key: str) -> bool:
        """Check if cached component is still valid (not expired)."""
        if component_key not in self._cache_times:
            return False
        
        cached_at = self._cache_times[component_key]
        age = (datetime.now() - cached_at).total_seconds()
        
        return age < self.ttl_seconds
    
    def _load_from_db(self, component_key: str) -> Optional[Any]:
        """Load component from database."""
        try:
            with sqlite3.connect(str(self.cache_path)) as conn:
                cursor = conn.execute("""
                    SELECT component_data, expires_at, version
                    FROM component_cache
                    WHERE component_key = ?
                """, (component_key,))
                
                row = cursor.fetchone()
                if row is None:
                    return None
                
                data, expires_at, version = row
                
                # Check expiration
                if datetime.fromisoformat(expires_at) < datetime.now():
                    # Expired - delete
                    conn.execute(
                        "DELETE FROM component_cache WHERE component_key = ?",
                        (component_key,)
                    )
                    conn.commit()
                    return None
                
                # Check version
                if version != self._version:
                    # Version mismatch - invalidate
                    conn.execute(
                        "DELETE FROM component_cache WHERE component_key = ?",
                        (component_key,)
                    )
                    conn.commit()
                    logger.info(f"Invalidated {component_key} due to version change")
                    return None
                
                # Deserialize
                component = pickle.loads(data)
                return component
        
        except Exception as e:
            logger.warning(f"Failed to load {component_key} from cache: {e}")
            return None
    
    def _save_to_db(self, component_key: str, component: Any):
        """Save component to database."""
        try:
            # Serialize
            data = pickle.dumps(component)
            size_bytes = len(data)
            
            # Check size limit
            size_mb = size_bytes / (1024 * 1024)
            if size_mb > self.max_memory_mb:
                logger.warning(f"Component {component_key} too large ({size_mb:.1f}MB), skipping cache")
                return
            
            # Calculate expiration
            cached_at = datetime.now()
            expires_at = cached_at + timedelta(seconds=self.ttl_seconds)
            
            # Save to database
            with sqlite3.connect(str(self.cache_path)) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO component_cache
                    (component_key, component_data, cached_at, expires_at, version, size_bytes)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    component_key,
                    data,
                    cached_at.isoformat(),
                    expires_at.isoformat(),
                    self._version,
                    size_bytes
                ))
                conn.commit()
        
        except Exception as e:
            logger.warning(f"Failed to save {component_key} to cache: {e}")
    
    def _get_version(self) -> str:
        """Get CORTEX version for cache invalidation."""
        try:
            from src.config import config
            version_file = Path(config.root_path) / "VERSION"
            if version_file.exists():
                return version_file.read_text().strip().split('\n')[0]
        except Exception:
            pass
        
        return "3.2.0"  # Default


# Global singleton for easy access
_global_cache: Optional[ComponentCache] = None


def get_component_cache() -> ComponentCache:
    """
    Get global component cache instance.
    
    Returns:
        Global ComponentCache instance
    """
    global _global_cache
    if _global_cache is None:
        _global_cache = ComponentCache()
    return _global_cache
