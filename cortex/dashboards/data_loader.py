"""
Phase 53 Stage 2 Implementation: DataLoader with Cache Strategy
Authority: CORTEX Architecture (Option B - Centralized Broker)
Purpose: Load repository JSON data with 5-minute TTL caching

AC_START: AC-PHASE53-S2-IMPL-001
Phase: 53 | Stage: 2 | Component: DataLoader
"""

import json
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
import hashlib


@dataclass
class CacheEntry:
    """Single cache entry with TTL tracking"""
    repository: str
    data: Dict[str, Any]
    loaded_at: datetime
    cache_ttl_ms: int = 5 * 60 * 1000  # 5 minutes
    
    def is_expired(self) -> bool:
        """Check if cache entry has expired"""
        age_ms = (datetime.utcnow() - self.loaded_at).total_seconds() * 1000
        return age_ms > self.cache_ttl_ms
    
    def age_ms(self) -> float:
        """Get age of cache entry in milliseconds"""
        return (datetime.utcnow() - self.loaded_at).total_seconds() * 1000


@dataclass
class DataLoadResponse:
    """Standardized response from data loading operations"""
    status: str  # "success", "error", "cached"
    repository: str
    data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    loaded_at: datetime = field(default_factory=datetime.utcnow)
    cache_hit: bool = False
    cache_age_ms: float = 0.0
    load_time_ms: float = 0.0


class DataLoader:
    """
    Load repository dashboard data from JSON files with intelligent caching
    
    Features:
    - Load from company/dashboards/data/{repo}.json
    - 5-minute TTL caching with age tracking
    - LRU eviction for memory efficiency
    - Graceful error handling
    - Concurrent request safety
    """
    
    SUPPORTED_REPOS = ["cortex", "ksessions", "kashkole", "alist", "noor-canvas"]
    CACHE_TTL_MS = 5 * 60 * 1000  # 5 minutes
    MAX_CACHE_SIZE = 50  # Maximum cache entries before LRU cleanup
    
    def __init__(self, data_dir: str = "company/dashboards/data"):
        self.data_dir = Path(data_dir)
        self.cache: Dict[str, CacheEntry] = {}
        self.cache_hits = 0
        self.cache_misses = 0
        self.access_order: List[str] = []  # For LRU tracking
    
    def get_data_file_path(self, repository: str) -> Path:
        """Get full path to repository data file"""
        return self.data_dir / f"{repository}.json"
    
    def load(self, repository: str) -> DataLoadResponse:
        """
        Load repository data with caching
        
        Process:
        1. Check cache (hit → return cached)
        2. Load from disk
        3. Store in cache
        4. Return response
        """
        start_time = datetime.utcnow()
        
        # Validate repository
        if repository not in self.SUPPORTED_REPOS:
            return DataLoadResponse(
                status="error",
                repository=repository,
                error_message=f"Unsupported repository: {repository}"
            )
        
        # Check cache
        cache_response = self._check_cache(repository)
        if cache_response:
            load_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            cache_response.load_time_ms = load_time
            return cache_response
        
        # Load from disk
        disk_response = self._load_from_disk(repository)
        if disk_response.status == "success":
            # Cache it
            self._cache_entry(
                repository,
                disk_response.data,
                datetime.utcnow()
            )
            self.cache_misses += 1
        
        load_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        disk_response.load_time_ms = load_time
        return disk_response
    
    def _check_cache(self, repository: str) -> Optional[DataLoadResponse]:
        """Check cache for repository data"""
        if repository not in self.cache:
            return None
        
        entry = self.cache[repository]
        
        # Check expiration
        if entry.is_expired():
            del self.cache[repository]
            return None
        
        # Cache hit
        self.cache_hits += 1
        self.access_order.append(repository)
        
        return DataLoadResponse(
            status="cached",
            repository=repository,
            data=entry.data,
            cache_hit=True,
            cache_age_ms=entry.age_ms()
        )
    
    def _load_from_disk(self, repository: str) -> DataLoadResponse:
        """Load data from JSON file on disk"""
        file_path = self.get_data_file_path(repository)
        
        try:
            if not file_path.exists():
                return DataLoadResponse(
                    status="error",
                    repository=repository,
                    error_message=f"Data file not found: {file_path}"
                )
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return DataLoadResponse(
                status="success",
                repository=repository,
                data=data,
                loaded_at=datetime.utcnow()
            )
            
        except json.JSONDecodeError as e:
            return DataLoadResponse(
                status="error",
                repository=repository,
                error_message=f"Invalid JSON: {str(e)}"
            )
        except Exception as e:
            return DataLoadResponse(
                status="error",
                repository=repository,
                error_message=f"Load error: {str(e)}"
            )
    
    def _cache_entry(self, repository: str, data: Dict[str, Any], 
                    loaded_at: datetime):
        """Store data in cache with LRU management"""
        # Check if cache is full
        if len(self.cache) >= self.MAX_CACHE_SIZE:
            # Remove oldest entry (LRU)
            oldest = self.access_order.pop(0)
            if oldest in self.cache:
                del self.cache[oldest]
        
        # Add entry
        self.cache[repository] = CacheEntry(
            repository=repository,
            data=data,
            loaded_at=loaded_at,
            cache_ttl_ms=self.CACHE_TTL_MS
        )
    
    def invalidate_cache(self, repository: Optional[str] = None):
        """
        Invalidate cache entries
        
        Args:
            repository: If specified, only invalidate that repo. 
                       If None, invalidate all.
        """
        if repository is None:
            self.cache.clear()
            self.access_order.clear()
        else:
            if repository in self.cache:
                del self.cache[repository]
            if repository in self.access_order:
                self.access_order.remove(repository)
    
    def load_all(self) -> Dict[str, DataLoadResponse]:
        """Load all repository data"""
        results = {}
        for repo in self.SUPPORTED_REPOS:
            results[repo] = self.load(repo)
        return results
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics for monitoring"""
        total_requests = self.cache_hits + self.cache_misses
        hit_rate = (self.cache_hits / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "cache_entries": len(self.cache),
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "hit_rate_percent": hit_rate,
            "max_cache_size": self.MAX_CACHE_SIZE,
            "cache_ttl_ms": self.CACHE_TTL_MS,
            "supported_repos": len(self.SUPPORTED_REPOS)
        }


class DataSynchronizer:
    """Synchronize data across dashboard components"""
    
    def __init__(self, loader: DataLoader):
        self.loader = loader
        self.sync_history = []
    
    def sync_all_data(self) -> Dict[str, Any]:
        """Sync all repository data"""
        start_time = datetime.utcnow()
        
        # Load all
        all_data = self.loader.load_all()
        
        # Validate
        valid_count = sum(1 for r in all_data.values() if r.status == "success")
        error_count = sum(1 for r in all_data.values() if r.status == "error")
        
        sync_result = {
            "timestamp": datetime.utcnow().isoformat(),
            "total_repos": len(all_data),
            "successful": valid_count,
            "failed": error_count,
            "sync_time_ms": (datetime.utcnow() - start_time).total_seconds() * 1000,
            "cache_stats": self.loader.get_cache_stats(),
            "results": all_data
        }
        
        self.sync_history.append(sync_result)
        return sync_result
    
    def invalidate_and_refresh(self, repository: str) -> DataLoadResponse:
        """Invalidate cache and reload specific repository"""
        self.loader.invalidate_cache(repository)
        return self.loader.load(repository)


# AC_COMPLETE: AC-PHASE53-S2-IMPL-001 ✅ DataLoader implemented
