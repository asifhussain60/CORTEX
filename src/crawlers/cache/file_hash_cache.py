"""
File Hash Cache

SHA256-based file content hashing with SQLite storage for fast cache lookups.
Supports incremental updates and automatic invalidation.

Author: CORTEX Application Health Dashboard
"""

import hashlib
import sqlite3
import time
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass
import json


@dataclass
class FileHashEntry:
    """Entry in file hash cache"""
    file_path: str
    content_hash: str
    file_size: int
    modified_time: float
    cached_at: float
    analysis_level: str = "standard"  # overview, standard, deep


class FileHashCache:
    """
    SHA256-based file hash cache with SQLite storage
    
    Features:
    - Content-based hashing (SHA256)
    - Fast O(1) lookup by file path
    - Automatic invalidation on file change
    - TTL-based cache eviction (30 days default)
    - Analysis level tracking (overview/standard/deep)
    """
    
    def __init__(self, cache_db_path: str = None, ttl_days: int = 30):
        """
        Initialize file hash cache
        
        Args:
            cache_db_path: Path to SQLite database. If None, uses temp location
            ttl_days: Time-to-live for cache entries in days
        """
        if cache_db_path is None:
            cache_dir = Path.home() / ".cortex" / "cache"
            cache_dir.mkdir(parents=True, exist_ok=True)
            cache_db_path = str(cache_dir / "file_hash_cache.db")
        
        self.cache_db_path = cache_db_path
        self.ttl_seconds = ttl_days * 24 * 60 * 60
        
        self._init_database()
    
    def close(self):
        """Close any open database connections (for cleanup)"""
        # SQLite connections are closed automatically with context managers
        # This method exists for explicit cleanup if needed
        pass
    
    def _init_database(self):
        """Initialize SQLite database schema"""
        with sqlite3.connect(self.cache_db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS file_hashes (
                    file_path TEXT PRIMARY KEY,
                    content_hash TEXT NOT NULL,
                    file_size INTEGER,
                    modified_time REAL,
                    cached_at REAL,
                    analysis_level TEXT DEFAULT 'standard'
                )
            """)
            
            # Index for fast hash lookups
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_content_hash 
                ON file_hashes(content_hash)
            """)
            
            conn.commit()
    
    def calculate_hash(self, file_path: str, chunk_size: int = 8192) -> str:
        """
        Calculate SHA256 hash of file content
        
        Args:
            file_path: Path to file
            chunk_size: Read chunk size (default 8KB)
            
        Returns:
            SHA256 hex digest
        """
        sha256 = hashlib.sha256()
        
        with open(file_path, 'rb') as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                sha256.update(chunk)
        
        return sha256.hexdigest()
    
    def get_cached_hash(self, file_path: str) -> Optional[FileHashEntry]:
        """
        Get cached hash entry for file
        
        Args:
            file_path: Path to file
            
        Returns:
            FileHashEntry if found and valid, None otherwise
        """
        # Normalize path
        file_path = str(Path(file_path).resolve())
        
        with sqlite3.connect(self.cache_db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM file_hashes WHERE file_path = ?",
                (file_path,)
            )
            row = cursor.fetchone()
            
            if not row:
                return None
            
            # Check TTL
            current_time = time.time()
            if current_time - row['cached_at'] > self.ttl_seconds:
                # Expired - delete entry
                conn.execute("DELETE FROM file_hashes WHERE file_path = ?", (file_path,))
                conn.commit()
                return None
            
            return FileHashEntry(
                file_path=row['file_path'],
                content_hash=row['content_hash'],
                file_size=row['file_size'],
                modified_time=row['modified_time'],
                cached_at=row['cached_at'],
                analysis_level=row['analysis_level']
            )
    
    def is_file_changed(self, file_path: str) -> bool:
        """
        Check if file has changed since last cache
        
        Args:
            file_path: Path to file
            
        Returns:
            True if file changed or not in cache, False if unchanged
        """
        cached_entry = self.get_cached_hash(file_path)
        
        if not cached_entry:
            return True  # Not in cache = changed
        
        # Check file modification time (fast check)
        try:
            current_mtime = Path(file_path).stat().st_mtime
            if abs(current_mtime - cached_entry.modified_time) > 0.001:
                return True
        except FileNotFoundError:
            return True  # File doesn't exist
        
        # Modification time matches - file likely unchanged
        return False
    
    def update_cache(
        self,
        file_path: str,
        content_hash: Optional[str] = None,
        analysis_level: str = "standard"
    ):
        """
        Update cache with new file hash
        
        Args:
            file_path: Path to file
            content_hash: Precalculated hash (if None, will calculate)
            analysis_level: Level of analysis (overview/standard/deep)
        """
        # Normalize path
        file_path_normalized = str(Path(file_path).resolve())
        
        # Calculate hash if not provided
        if content_hash is None:
            content_hash = self.calculate_hash(file_path)
        
        # Get file stats
        file_stat = Path(file_path).stat()
        
        with sqlite3.connect(self.cache_db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO file_hashes 
                (file_path, content_hash, file_size, modified_time, cached_at, analysis_level)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                file_path_normalized,
                content_hash,
                file_stat.st_size,
                file_stat.st_mtime,
                time.time(),
                analysis_level
            ))
            conn.commit()
    
    def invalidate_file(self, file_path: str):
        """
        Remove file from cache (force re-analysis)
        
        Args:
            file_path: Path to file
        """
        file_path_normalized = str(Path(file_path).resolve())
        
        with sqlite3.connect(self.cache_db_path) as conn:
            conn.execute("DELETE FROM file_hashes WHERE file_path = ?", (file_path_normalized,))
            conn.commit()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics
        
        Returns:
            Dictionary with cache stats
        """
        with sqlite3.connect(self.cache_db_path) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM file_hashes")
            total_entries = cursor.fetchone()[0]
            
            cursor = conn.execute("SELECT SUM(file_size) FROM file_hashes")
            total_size = cursor.fetchone()[0] or 0
            
            cursor = conn.execute("""
                SELECT analysis_level, COUNT(*) 
                FROM file_hashes 
                GROUP BY analysis_level
            """)
            by_level = {row[0]: row[1] for row in cursor.fetchall()}
            
            return {
                'total_entries': total_entries,
                'total_size_bytes': total_size,
                'total_size_mb': total_size / (1024 * 1024),
                'by_analysis_level': by_level
            }
    
    def clear_cache(self):
        """Clear all cache entries"""
        with sqlite3.connect(self.cache_db_path) as conn:
            conn.execute("DELETE FROM file_hashes")
            conn.commit()
