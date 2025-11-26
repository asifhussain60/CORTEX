"""
Unified Validation Cache for CORTEX Entry Points

Provides SQLite-backed caching with file hash tracking for automatic invalidation.
Shared by: align, deploy, optimize, cleanup, and future entry points.

Features:
- File hash tracking (SHA256) for automatic cache invalidation
- Cross-operation result sharing (e.g., align → deploy)
- TTL support for time-based expiration
- SQLite persistence (survives process restarts)
- Incremental validation (only revalidate changed files)

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
Version: 1.0.0
Date: November 26, 2025
"""

from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, asdict
from datetime import datetime
import hashlib
import json
import sqlite3
import logging

logger = logging.getLogger(__name__)

# Default cache database location
DEFAULT_CACHE_DB = Path(__file__).parent.parent.parent / "cortex-brain" / "cache" / "validation_cache.db"


@dataclass
class CacheEntry:
    """Single cache entry with file hash tracking."""
    operation: str  # 'align', 'deploy', 'optimize', 'cleanup'
    key: str  # Unique identifier (e.g., 'feature:auth_orchestrator', 'test_suite:all')
    result: Any  # Cached result (dict, list, or simple value)
    file_hashes: Dict[str, str]  # {file_path: sha256_hash}
    timestamp: datetime
    ttl_seconds: int  # Time-to-live (0 = infinite)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'operation': self.operation,
            'key': self.key,
            'result': self.result,
            'file_hashes': self.file_hashes,
            'timestamp': self.timestamp.isoformat(),
            'ttl_seconds': self.ttl_seconds
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CacheEntry':
        """Create CacheEntry from dictionary."""
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)


class ValidationCache:
    """
    Unified cache for all validation operations.
    
    Features:
    - File hash tracking (SHA256) for automatic invalidation
    - Cross-operation result sharing (align → deploy)
    - TTL support (time-based expiration)
    - SQLite persistence (survives process restart)
    - Incremental validation (only changed files)
    
    Usage:
        from src.caching import get_cache
        
        cache = get_cache()
        
        # Try cache first
        result = cache.get('align', 'orchestrators', [Path('src/operations')])
        if result is None:
            # Cache miss - run expensive operation
            result = discover_orchestrators()
            cache.set('align', 'orchestrators', result, [Path('src/operations')])
        
        # Share results with deploy
        cache.share_result('align', 'deploy', 'orchestrators')
    """
    
    def __init__(self, cache_db_path: Path):
        """
        Initialize ValidationCache.
        
        Args:
            cache_db_path: Path to SQLite database file
        """
        self.cache_db = Path(cache_db_path) if isinstance(cache_db_path, str) else cache_db_path
        self._init_database()
        self._stats = {
            'hits': 0,
            'misses': 0,
            'invalidations': 0,
            'sets': 0
        }
        logger.info(f"ValidationCache initialized: {cache_db_path}")
    
    def _init_database(self):
        """Create cache database schema if not exists."""
        self.cache_db.parent.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(str(self.cache_db))
        try:
            # Main cache entries table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS cache_entries (
                    operation TEXT NOT NULL,
                    key TEXT NOT NULL,
                    result_json TEXT NOT NULL,
                    file_hashes_json TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    ttl_seconds INTEGER NOT NULL,
                    PRIMARY KEY (operation, key)
                )
            ''')
            
            # Index for timestamp-based queries
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_timestamp 
                ON cache_entries(timestamp)
            ''')
            
            # Index for operation-based queries
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_operation 
                ON cache_entries(operation)
            ''')
            
            # Cache statistics table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS cache_stats (
                    operation TEXT NOT NULL,
                    hits INTEGER DEFAULT 0,
                    misses INTEGER DEFAULT 0,
                    invalidations INTEGER DEFAULT 0,
                    last_updated TEXT NOT NULL,
                    PRIMARY KEY (operation)
                )
            ''')
            
            conn.commit()
            logger.debug("Cache database schema initialized")
        finally:
            conn.close()
    
    def get(self, operation: str, key: str, files: Optional[List[Path]] = None) -> Optional[Any]:
        """
        Get cached result if files haven't changed.
        
        Args:
            operation: Operation name ('align', 'deploy', 'optimize', 'cleanup')
            key: Cache key (e.g., 'integration_scores', 'test_coverage:auth')
            files: List of files to check for changes (None = no file tracking)
        
        Returns:
            Cached result if valid, None if cache miss or invalidated
        """
        if files is None:
            files = []
        else:
            # Convert to Path objects if strings
            files = [Path(f) if isinstance(f, str) else f for f in files]
        conn = sqlite3.connect(str(self.cache_db))
        try:
            cursor = conn.execute(
                'SELECT result_json, file_hashes_json, timestamp, ttl_seconds FROM cache_entries WHERE operation = ? AND key = ?',
                (operation, key)
            )
            row = cursor.fetchone()
            
            if not row:
                self._stats['misses'] += 1
                self._update_stats(conn, operation, misses=1)
                logger.debug(f"Cache MISS: {operation}:{key}")
                return None
            
            result_json, file_hashes_json, timestamp_str, ttl_seconds = row
            
            # Check TTL
            timestamp = datetime.fromisoformat(timestamp_str)
            if ttl_seconds > 0:
                age_seconds = (datetime.now() - timestamp).total_seconds()
                if age_seconds > ttl_seconds:
                    self._stats['misses'] += 1
                    self._update_stats(conn, operation, misses=1)
                    logger.debug(f"Cache EXPIRED: {operation}:{key} (age: {age_seconds}s, TTL: {ttl_seconds}s)")
                    return None
            
            # Check file hashes
            cached_hashes = json.loads(file_hashes_json)
            current_hashes = self._calculate_file_hashes(files)
            
            if cached_hashes != current_hashes:
                self._stats['misses'] += 1
                self._stats['invalidations'] += 1
                self._update_stats(conn, operation, misses=1, invalidations=1)
                logger.debug(f"Cache INVALIDATED: {operation}:{key} (file hashes changed)")
                return None
            
            # Cache hit
            self._stats['hits'] += 1
            self._update_stats(conn, operation, hits=1)
            result = json.loads(result_json)
            logger.debug(f"Cache HIT: {operation}:{key}")
            return result
            
        finally:
            conn.close()
    
    def set(self, operation: str, key: str, result: Any, files: Optional[List[Path]] = None, ttl_seconds: int = 0):
        """
        Store result in cache with file hash tracking.
        
        Args:
            operation: Operation name ('align', 'deploy', etc.)
            key: Cache key (unique identifier)
            result: Result to cache (must be JSON-serializable)
            files: Files to track for invalidation (None = no file tracking)
            ttl_seconds: Time-to-live in seconds (0 = infinite)
        """
        if files is None:
            files = []
        else:
            # Convert to Path objects if strings
            files = [Path(f) if isinstance(f, str) else f for f in files]
        file_hashes = self._calculate_file_hashes(files)
        
        conn = sqlite3.connect(str(self.cache_db))
        try:
            conn.execute('''
                INSERT OR REPLACE INTO cache_entries (operation, key, result_json, file_hashes_json, timestamp, ttl_seconds)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                operation,
                key,
                json.dumps(result),
                json.dumps(file_hashes),
                datetime.now().isoformat(),
                ttl_seconds
            ))
            conn.commit()
            
            self._stats['sets'] += 1
            logger.debug(f"Cache SET: {operation}:{key} (tracked {len(files)} files, TTL: {ttl_seconds}s)")
            
        finally:
            conn.close()
    
    def invalidate(self, operation: Optional[str] = None, key: Optional[str] = None):
        """
        Invalidate cache entries.
        
        Args:
            operation: If provided, invalidate only this operation (e.g., 'align')
            key: If provided with operation, invalidate specific key only
        
        Examples:
            cache.invalidate()  # Clear all cache
            cache.invalidate('align')  # Clear all align cache
            cache.invalidate('align', 'orchestrators')  # Clear specific entry
        """
        conn = sqlite3.connect(str(self.cache_db))
        try:
            if operation and key:
                cursor = conn.execute('DELETE FROM cache_entries WHERE operation = ? AND key = ?', (operation, key))
                deleted = cursor.rowcount
                if deleted > 0:
                    self._update_stats(conn, operation, invalidations=1)
                logger.info(f"Cache invalidated: {operation}:{key} ({deleted} entries)")
            elif operation:
                cursor = conn.execute('DELETE FROM cache_entries WHERE operation = ?', (operation,))
                deleted = cursor.rowcount
                if deleted > 0:
                    self._update_stats(conn, operation, invalidations=deleted)
                logger.info(f"Cache invalidated: {operation} ({deleted} entries)")
            else:
                cursor = conn.execute('DELETE FROM cache_entries')
                deleted = cursor.rowcount
                logger.info(f"Cache cleared: all entries ({deleted} total)")
            
            conn.commit()
            self._stats['invalidations'] += deleted
            
        finally:
            conn.close()
    
    def share_result(self, source_operation: str, target_operation: str, key: str):
        """
        Share cached result between operations.
        
        Example: Share integration scores from 'align' to 'deploy'
        
        Args:
            source_operation: Operation that produced result (e.g., 'align')
            target_operation: Operation that needs result (e.g., 'deploy')
            key: Cache key to share
        """
        conn = sqlite3.connect(str(self.cache_db))
        try:
            # Copy cache entry from source to target
            cursor = conn.execute('''
                INSERT OR REPLACE INTO cache_entries (operation, key, result_json, file_hashes_json, timestamp, ttl_seconds)
                SELECT ?, key, result_json, file_hashes_json, timestamp, ttl_seconds
                FROM cache_entries
                WHERE operation = ? AND key = ?
            ''', (target_operation, source_operation, key))
            
            if cursor.rowcount > 0:
                conn.commit()
                logger.info(f"Cache shared: {source_operation}:{key} → {target_operation}:{key}")
            else:
                logger.warning(f"Cache share failed: {source_operation}:{key} not found")
            
        finally:
            conn.close()
    
    def get_stats(self, operation: Optional[str] = None) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Args:
            operation: If provided, get stats for specific operation only
        
        Returns:
            Dictionary with hits, misses, hit_rate, total_entries
        """
        conn = sqlite3.connect(str(self.cache_db))
        try:
            if operation:
                cursor = conn.execute(
                    'SELECT hits, misses, invalidations FROM cache_stats WHERE operation = ?',
                    (operation,)
                )
                row = cursor.fetchone()
                if row:
                    hits, misses, invalidations = row
                else:
                    hits = misses = invalidations = 0
                
                # Count entries
                cursor = conn.execute(
                    'SELECT COUNT(*) FROM cache_entries WHERE operation = ?',
                    (operation,)
                )
                total_entries = cursor.fetchone()[0]
            else:
                # Aggregate stats
                cursor = conn.execute(
                    'SELECT SUM(hits), SUM(misses), SUM(invalidations) FROM cache_stats'
                )
                row = cursor.fetchone()
                hits = row[0] or 0
                misses = row[1] or 0
                invalidations = row[2] or 0
                
                # Count all entries
                cursor = conn.execute('SELECT COUNT(*) FROM cache_entries')
                total_entries = cursor.fetchone()[0]
            
            total_requests = hits + misses
            hit_rate = (hits / total_requests) if total_requests > 0 else 0.0
            
            return {
                'hits': hits,
                'misses': misses,
                'invalidations': invalidations,
                'total_requests': total_requests,
                'hit_rate': hit_rate,
                'total_entries': total_entries,
                'operation': operation or 'all'
            }
            
        finally:
            conn.close()
    
    def get_all_keys(self, operation: Optional[str] = None) -> List[str]:
        """
        Get all cached keys (excludes expired entries).
        
        Args:
            operation: If provided, get keys for specific operation only
        
        Returns:
            List of cache keys (strings) that are not expired
        """ 
        conn = sqlite3.connect(str(self.cache_db))
        try:
            if operation:
                cursor = conn.execute(
                    'SELECT key, timestamp, ttl_seconds FROM cache_entries WHERE operation = ? ORDER BY key',
                    (operation,)
                )
            else:
                cursor = conn.execute(
                    'SELECT key, timestamp, ttl_seconds FROM cache_entries ORDER BY key'
                )
            
            keys = []
            now = datetime.now()
            for row in cursor.fetchall():
                key, timestamp_str, ttl_seconds = row
                # Check if expired
                if ttl_seconds > 0:
                    timestamp = datetime.fromisoformat(timestamp_str)
                    age_seconds = (now - timestamp).total_seconds()
                    if age_seconds > ttl_seconds:
                        continue  # Skip expired
                keys.append(key)
            
            return keys
            
        finally:
            conn.close()
    
    def _calculate_file_hashes(self, files: List[Path]) -> Dict[str, str]:
        """
        Calculate SHA256 hashes for file list.
        
        Args:
            files: List of file paths to hash
        
        Returns:
            Dictionary mapping file path to SHA256 hash
        """
        hashes = {}
        for file_path in files:
            if file_path.exists() and file_path.is_file():
                try:
                    with open(file_path, 'rb') as f:
                        file_hash = hashlib.sha256(f.read()).hexdigest()
                        hashes[str(file_path)] = file_hash
                except Exception as e:
                    logger.warning(f"Failed to hash {file_path}: {e}")
            elif file_path.exists() and file_path.is_dir():
                # For directories, hash all Python files recursively
                for py_file in file_path.rglob('*.py'):
                    try:
                        with open(py_file, 'rb') as f:
                            file_hash = hashlib.sha256(f.read()).hexdigest()
                            hashes[str(py_file)] = file_hash
                    except Exception as e:
                        logger.warning(f"Failed to hash {py_file}: {e}")
        
        return hashes
    
    def _update_stats(self, conn: sqlite3.Connection, operation: str, 
                      hits: int = 0, misses: int = 0, invalidations: int = 0):
        """Update cache statistics in database."""
        conn.execute('''
            INSERT INTO cache_stats (operation, hits, misses, invalidations, last_updated)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(operation) DO UPDATE SET
                hits = hits + ?,
                misses = misses + ?,
                invalidations = invalidations + ?,
                last_updated = ?
        ''', (
            operation, hits, misses, invalidations, datetime.now().isoformat(),
            hits, misses, invalidations, datetime.now().isoformat()
        ))
        conn.commit()


# Global cache instance
_cache: Optional[ValidationCache] = None
_cache_db_path: Optional[Path] = None


def get_cache(cache_db_path: Optional[Path] = None) -> ValidationCache:
    """
    Get global ValidationCache instance.
    
    Args:
        cache_db_path: Optional custom cache database path.
                      If None, uses default: cortex-brain/tier1/validation_cache.db
    
    Returns:
        Global ValidationCache instance
    """
    global _cache, _cache_db_path
    
    if cache_db_path is not None:
        # Custom path provided - reinitialize
        _cache_db_path = cache_db_path
        _cache = None
    
    if _cache is None:
        if _cache_db_path is None:
            # Default path
            _cache_db_path = DEFAULT_CACHE_DB
        
        # Ensure Path object
        if isinstance(_cache_db_path, str):
            _cache_db_path = Path(_cache_db_path)
        
        _cache = ValidationCache(_cache_db_path)
        logger.info(f"Global ValidationCache initialized: {_cache_db_path}")
    
    return _cache


def clear_global_cache():
    """Clear the global cache instance (mainly for testing)."""
    global _cache, _cache_db_path
    _cache = None
    _cache_db_path = None
