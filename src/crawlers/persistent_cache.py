"""
Persistent Application Cache for CORTEX

SQLite-indexed cache system that survives VS Code restarts.
Implements LRU eviction and 7-day TTL.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import os
import json
import sqlite3
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class PersistentApplicationCache:
    """
    Cache system that survives VS Code restarts.
    
    Storage Structure:
    - cortex-brain/context-cache/applications/{app_name}/
      ├── metadata.json (fingerprint, timestamps)
      ├── shallow_context.json (entry points, structure)
      └── deep_context.json (full file inventory)
    
    - cortex-brain/context-cache/cache_index.db
      (SQLite database for fast cache lookups)
    
    Features:
    - Persistent across VS Code restarts
    - SQLite index for fast lookups
    - 7-day TTL (configurable)
    - LRU eviction when cache size exceeds limit
    - Hit count tracking
    """
    
    def __init__(
        self,
        cache_dir: Path,
        max_cache_size_mb: int = 500,
        ttl_days: int = 7
    ):
        """
        Initialize persistent cache.
        
        Args:
            cache_dir: Base cache directory (cortex-brain)
            max_cache_size_mb: Maximum total cache size in MB
            ttl_days: Time-to-live in days
        """
        self.cache_base_dir = cache_dir / "context-cache"
        self.cache_apps_dir = self.cache_base_dir / "applications"
        self.cache_apps_dir.mkdir(parents=True, exist_ok=True)
        
        self.max_cache_size_mb = max_cache_size_mb
        self.ttl_days = ttl_days
        
        # SQLite index for fast lookups
        self.index_db_path = self.cache_base_dir / "cache_index.db"
        self._init_cache_index()
        
        logger.info(f"Initialized persistent cache: {self.cache_apps_dir}")
    
    def _init_cache_index(self) -> None:
        """Create SQLite index for cache metadata"""
        conn = sqlite3.connect(self.index_db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS cache_index (
                app_name TEXT NOT NULL,
                depth TEXT NOT NULL,
                fingerprint TEXT NOT NULL,
                cache_path TEXT NOT NULL,
                created_at REAL NOT NULL,
                last_accessed REAL NOT NULL,
                size_bytes INTEGER NOT NULL,
                hit_count INTEGER DEFAULT 0,
                PRIMARY KEY (app_name, depth, fingerprint)
            )
        """)
        
        # Index for LRU eviction queries
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_last_accessed 
            ON cache_index(last_accessed)
        """)
        
        # Index for size queries
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_size 
            ON cache_index(size_bytes)
        """)
        
        conn.commit()
        conn.close()
        
        logger.debug("Cache index initialized")
    
    def get(
        self,
        app_name: str,
        depth: str,
        fingerprint: str
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached context.
        
        Args:
            app_name: Application name
            depth: 'shallow' or 'deep'
            fingerprint: Cache fingerprint for validation
        
        Returns:
            Cached context dictionary or None if not found/stale
        """
        try:
            # Check if entry exists in index
            conn = sqlite3.connect(self.index_db_path)
            cursor = conn.execute("""
                SELECT cache_path, created_at, fingerprint
                FROM cache_index
                WHERE app_name = ? AND depth = ?
                ORDER BY created_at DESC
                LIMIT 1
            """, (app_name, depth))
            
            row = cursor.fetchone()
            conn.close()
            
            if not row:
                logger.debug(f"Cache miss: {app_name}/{depth} (not in index)")
                return None
            
            cache_path, created_at, cached_fingerprint = row
            
            # Check if fingerprint matches (cache is still valid)
            if cached_fingerprint != fingerprint:
                logger.debug(f"Cache miss: {app_name}/{depth} (fingerprint mismatch)")
                return None
            
            # Check TTL
            age_days = (datetime.now().timestamp() - created_at) / 86400
            if age_days > self.ttl_days:
                logger.debug(f"Cache expired: {app_name}/{depth} (age: {age_days:.1f} days)")
                self._remove_from_index(app_name, depth, cached_fingerprint)
                return None
            
            # Load cache file
            cache_file = Path(cache_path)
            if not cache_file.exists():
                logger.warning(f"Cache file missing: {cache_path}")
                self._remove_from_index(app_name, depth, cached_fingerprint)
                return None
            
            with open(cache_file, 'r') as f:
                data = json.load(f)
            
            # Update access time and hit count
            self._update_access_stats(app_name, depth, cached_fingerprint)
            
            logger.info(f"Cache hit: {app_name}/{depth}")
            return data
        
        except Exception as e:
            logger.error(f"Cache retrieval failed: {e}", exc_info=True)
            return None
    
    def put(
        self,
        app_name: str,
        depth: str,
        fingerprint: str,
        data: Dict[str, Any]
    ) -> bool:
        """
        Store context in cache.
        
        Args:
            app_name: Application name
            depth: 'shallow' or 'deep'
            fingerprint: Cache fingerprint
            data: Context data to cache
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check total cache size and evict if needed
            self._check_and_evict()
            
            # Create app cache directory
            app_cache_dir = self.cache_apps_dir / app_name
            app_cache_dir.mkdir(parents=True, exist_ok=True)
            
            # Save context file
            cache_file = app_cache_dir / f"{depth}_context.json"
            with open(cache_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            # Get file size
            file_size = cache_file.stat().st_size
            
            # Update index
            conn = sqlite3.connect(self.index_db_path)
            now = datetime.now().timestamp()
            
            conn.execute("""
                INSERT OR REPLACE INTO cache_index
                (app_name, depth, fingerprint, cache_path, created_at, last_accessed, size_bytes, hit_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, 0)
            """, (app_name, depth, fingerprint, str(cache_file), now, now, file_size))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Cached: {app_name}/{depth} ({file_size / 1024:.1f} KB)")
            return True
        
        except Exception as e:
            logger.error(f"Cache storage failed: {e}", exc_info=True)
            return False
    
    def _check_and_evict(self) -> None:
        """Check total cache size and evict LRU entries if needed"""
        try:
            total_size_mb = self._get_total_cache_size_mb()
            
            if total_size_mb > self.max_cache_size_mb:
                logger.info(f"Cache size ({total_size_mb:.1f} MB) exceeds limit ({self.max_cache_size_mb} MB), evicting...")
                self._evict_lru()
        
        except Exception as e:
            logger.error(f"Cache eviction check failed: {e}")
    
    def _get_total_cache_size_mb(self) -> float:
        """Get total cache size in MB"""
        conn = sqlite3.connect(self.index_db_path)
        cursor = conn.execute("SELECT SUM(size_bytes) FROM cache_index")
        total_bytes = cursor.fetchone()[0] or 0
        conn.close()
        
        return total_bytes / (1024 * 1024)
    
    def _evict_lru(self) -> None:
        """Evict least recently used cache entries"""
        try:
            conn = sqlite3.connect(self.index_db_path)
            
            # Get total entries count first
            cursor = conn.execute("SELECT COUNT(*) FROM cache_index")
            total_count = cursor.fetchone()[0]
            evict_count = int(total_count * 0.2)  # Evict oldest 20%
            
            # Get oldest entries to evict
            cursor = conn.execute("""
                SELECT app_name, depth, fingerprint, cache_path
                FROM cache_index
                ORDER BY last_accessed ASC
                LIMIT ?
            """, (evict_count,))
            
            entries_to_evict = cursor.fetchall()
            
            for app_name, depth, fingerprint, cache_path in entries_to_evict:
                # Delete cache file
                try:
                    cache_file = Path(cache_path)
                    if cache_file.exists():
                        cache_file.unlink()
                except Exception as e:
                    logger.warning(f"Failed to delete cache file {cache_path}: {e}")
                
                # Remove from index
                conn.execute("""
                    DELETE FROM cache_index
                    WHERE app_name = ? AND depth = ? AND fingerprint = ?
                """, (app_name, depth, fingerprint))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Evicted {len(entries_to_evict)} LRU cache entries")
        
        except Exception as e:
            logger.error(f"LRU eviction failed: {e}")
    
    def _update_access_stats(
        self,
        app_name: str,
        depth: str,
        fingerprint: str
    ) -> None:
        """Update last accessed time and hit count"""
        try:
            conn = sqlite3.connect(self.index_db_path)
            now = datetime.now().timestamp()
            
            conn.execute("""
                UPDATE cache_index
                SET last_accessed = ?, hit_count = hit_count + 1
                WHERE app_name = ? AND depth = ? AND fingerprint = ?
            """, (now, app_name, depth, fingerprint))
            
            conn.commit()
            conn.close()
        
        except Exception as e:
            logger.error(f"Failed to update access stats: {e}")
    
    def _remove_from_index(
        self,
        app_name: str,
        depth: str,
        fingerprint: str
    ) -> None:
        """Remove entry from index"""
        try:
            conn = sqlite3.connect(self.index_db_path)
            conn.execute("""
                DELETE FROM cache_index
                WHERE app_name = ? AND depth = ? AND fingerprint = ?
            """, (app_name, depth, fingerprint))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Failed to remove from index: {e}")
    
    def clear_app(self, app_name: str) -> bool:
        """
        Clear all cache entries for an application.
        
        Args:
            app_name: Application name
        
        Returns:
            True if successful
        """
        try:
            conn = sqlite3.connect(self.index_db_path)
            
            # Get all cache paths for app
            cursor = conn.execute("""
                SELECT cache_path FROM cache_index
                WHERE app_name = ?
            """, (app_name,))
            
            cache_paths = [row[0] for row in cursor.fetchall()]
            
            # Delete cache files
            for cache_path in cache_paths:
                try:
                    Path(cache_path).unlink()
                except Exception as e:
                    logger.warning(f"Failed to delete {cache_path}: {e}")
            
            # Remove from index
            conn.execute("DELETE FROM cache_index WHERE app_name = ?", (app_name,))
            conn.commit()
            conn.close()
            
            logger.info(f"Cleared cache for {app_name}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to clear app cache: {e}")
            return False
    
    def clear_all(self) -> bool:
        """
        Clear all cache entries.
        
        Returns:
            True if successful
        """
        try:
            # Delete all cache files
            import shutil
            if self.cache_apps_dir.exists():
                shutil.rmtree(self.cache_apps_dir)
                self.cache_apps_dir.mkdir(parents=True, exist_ok=True)
            
            # Clear index
            conn = sqlite3.connect(self.index_db_path)
            conn.execute("DELETE FROM cache_index")
            conn.commit()
            conn.close()
            
            logger.info("Cleared all cache")
            return True
        
        except Exception as e:
            logger.error(f"Failed to clear all cache: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        try:
            conn = sqlite3.connect(self.index_db_path)
            
            # Total entries
            cursor = conn.execute("SELECT COUNT(*) FROM cache_index")
            total_entries = cursor.fetchone()[0]
            
            # Total size
            cursor = conn.execute("SELECT SUM(size_bytes) FROM cache_index")
            total_bytes = cursor.fetchone()[0] or 0
            
            # Applications cached
            cursor = conn.execute("SELECT COUNT(DISTINCT app_name) FROM cache_index")
            apps_cached = cursor.fetchone()[0]
            
            # Hit count stats
            cursor = conn.execute("""
                SELECT AVG(hit_count), MAX(hit_count)
                FROM cache_index
            """)
            avg_hits, max_hits = cursor.fetchone()
            
            # Most accessed
            cursor = conn.execute("""
                SELECT app_name, depth, hit_count
                FROM cache_index
                ORDER BY hit_count DESC
                LIMIT 5
            """)
            most_accessed = cursor.fetchall()
            
            conn.close()
            
            return {
                'total_entries': total_entries,
                'total_size_mb': total_bytes / (1024 * 1024),
                'apps_cached': apps_cached,
                'average_hits': avg_hits or 0,
                'max_hits': max_hits or 0,
                'most_accessed': [
                    {'app': app, 'depth': depth, 'hits': hits}
                    for app, depth, hits in most_accessed
                ]
            }
        
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {}
