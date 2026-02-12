"""LENS Dashboard Cache Manager.

Manages cache entries for generated dashboards, including:
- Output path resolution
- Cache entry creation and retrieval
- Expiration handling
- Cleanup operations

Authority: CORE-008 (TDD), CORE-011 (Type hints), CORE-012 (Docstrings)
Phase: 14 - LENS Dashboard Implementation
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional, Any
import json
import hashlib


@dataclass
class CacheEntry:
    """Represents a cached dashboard entry.
    
    Attributes:
        repo_path: Path to the repository
        output_path: Path where dashboard is stored
        created_at: When the cache entry was created
        expires_at: When the cache entry expires
        is_cortex: Whether this is the CORTEX repository
    """
    repo_path: str
    output_path: str
    created_at: datetime
    expires_at: datetime
    is_cortex: bool = False
    
    def is_expired(self) -> bool:
        """Check if this cache entry has expired.
        
        Returns:
            True if current time is past expires_at
        """
        return datetime.now() > self.expires_at
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize cache entry to dictionary.
        
        Returns:
            Dictionary representation of cache entry
        """
        return {
            "repo_path": self.repo_path,
            "output_path": self.output_path,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
            "is_cortex": self.is_cortex,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CacheEntry":
        """Deserialize cache entry from dictionary.
        
        Args:
            data: Dictionary with cache entry data
            
        Returns:
            CacheEntry instance
        """
        return cls(
            repo_path=data["repo_path"],
            output_path=data["output_path"],
            created_at=datetime.fromisoformat(data["created_at"]),
            expires_at=datetime.fromisoformat(data["expires_at"]),
            is_cortex=data.get("is_cortex", False),
        )


class CacheManager:
    """Manages dashboard cache entries.
    
    Handles output path resolution, cache entry lifecycle,
    and cleanup of expired entries.
    
    Attributes:
        cache_base: Base directory for cache storage
        cache_hours: Hours before cache entries expire
    """
    
    _instance: Optional["CacheManager"] = None
    
    def __init__(
        self,
        cache_base: Optional[Path] = None,
        cache_hours: int = 24,
    ) -> None:
        """Initialize cache manager.
        
        Args:
            cache_base: Base directory for cache (default: ~/.cortex/lens-cache)
            cache_hours: Hours before entries expire (default: 24)
        """
        if cache_base is None:
            cache_base = Path.home() / ".cortex" / "lens-cache"
        
        self.cache_base = Path(cache_base)
        self.cache_hours = cache_hours
        self._entries: Dict[str, CacheEntry] = {}
        self._cache_file = self.cache_base / "cache_index.json"
        
        # Ensure cache directory exists
        self.cache_base.mkdir(parents=True, exist_ok=True)
        
        # Load existing cache entries
        self._load_cache()
    
    def _load_cache(self) -> None:
        """Load cache entries from disk."""
        if self._cache_file.exists():
            try:
                with open(self._cache_file, "r") as f:
                    data = json.load(f)
                    for key, entry_data in data.items():
                        self._entries[key] = CacheEntry.from_dict(entry_data)
            except (json.JSONDecodeError, KeyError):
                self._entries = {}
    
    def _save_cache(self) -> None:
        """Save cache entries to disk."""
        data = {key: entry.to_dict() for key, entry in self._entries.items()}
        with open(self._cache_file, "w") as f:
            json.dump(data, f, indent=2)
    
    def _get_cache_key(self, repo_path: Path) -> str:
        """Generate cache key for repository.
        
        Args:
            repo_path: Path to repository
            
        Returns:
            Hash-based cache key
        """
        return hashlib.sha256(str(repo_path.resolve()).encode()).hexdigest()[:16]
    
    def get_output_path(
        self,
        repo_path: Path,
        is_cortex: bool = False,
        is_remote: bool = False,
        owner: Optional[str] = None,
        repo_name: Optional[str] = None,
    ) -> Path:
        """Get output path for dashboard.
        
        Args:
            repo_path: Path to repository
            is_cortex: Whether this is the CORTEX repository
            is_remote: Whether this is a remote repository
            owner: Repository owner (required for remote)
            repo_name: Repository name (required for remote)
            
        Returns:
            Path where dashboard should be stored
            
        Raises:
            ValueError: If is_remote=True but owner/repo_name not provided
        """
        if is_remote:
            if not owner or not repo_name:
                raise ValueError("owner and repo_name required for remote repositories")
            # Remote repos go to cache with owner/repo structure
            return self.cache_base / "remote" / owner / repo_name / "lens-dashboard"
        elif is_cortex:
            # CORTEX uses reports folder
            return repo_path / "reports" / "lens-dashboard"
        else:
            # External repos use .cortex folder
            return repo_path / ".cortex" / "lens-dashboard"
    
    def register_cache(
        self,
        repo_path: Path,
        output_path: Path,
        is_cortex: bool = False,
    ) -> CacheEntry:
        """Register a cache entry (alias for create_entry).
        
        Args:
            repo_path: Path to repository
            output_path: Path where dashboard is stored
            is_cortex: Whether this is the CORTEX repository
            
        Returns:
            CacheEntry instance
        """
        return self.create_entry(repo_path, output_path, is_cortex)
    
    def get_cached(self, repo_path: Path) -> Optional[CacheEntry]:
        """Get cached entry for repository (alias for get_entry).
        
        Args:
            repo_path: Path to repository
            
        Returns:
            CacheEntry if exists and not expired, None otherwise
        """
        return self.get_entry(repo_path)
    
    def invalidate(self, repo_path: Path) -> bool:
        """Invalidate/remove a cache entry.
        
        Args:
            repo_path: Path to repository
            
        Returns:
            True if entry was removed, False if not found
        """
        cache_key = self._get_cache_key(repo_path)
        if cache_key in self._entries:
            del self._entries[cache_key]
            self._save_cache()
            return True
        return False
    
    def get_entry(self, repo_path: Path) -> Optional[CacheEntry]:
        """Get cache entry for repository.
        
        Args:
            repo_path: Path to repository
            
        Returns:
            CacheEntry if exists and not expired, None otherwise
        """
        cache_key = self._get_cache_key(repo_path)
        entry = self._entries.get(cache_key)
        
        if entry and not entry.is_expired():
            return entry
        
        return None
    
    def create_entry(
        self,
        repo_path: Path,
        output_path: Path,
        is_cortex: bool = False,
    ) -> CacheEntry:
        """Create a new cache entry.
        
        Args:
            repo_path: Path to repository
            output_path: Path where dashboard is stored
            is_cortex: Whether this is the CORTEX repository
            
        Returns:
            New CacheEntry instance
        """
        now = datetime.now()
        entry = CacheEntry(
            repo_path=str(repo_path),
            output_path=str(output_path),
            created_at=now,
            expires_at=now + timedelta(hours=self.cache_hours),
            is_cortex=is_cortex,
        )
        
        cache_key = self._get_cache_key(repo_path)
        self._entries[cache_key] = entry
        self._save_cache()
        
        return entry
    
    def cleanup_expired(self) -> int:
        """Remove expired cache entries.
        
        Returns:
            Number of entries removed
        """
        expired_keys = [
            key for key, entry in self._entries.items()
            if entry.is_expired()
        ]
        
        for key in expired_keys:
            del self._entries[key]
        
        if expired_keys:
            self._save_cache()
        
        return len(expired_keys)
    
    def cleanup_older_than(self, days: int) -> int:
        """Remove entries older than specified days.
        
        Args:
            days: Remove entries older than this many days
            
        Returns:
            Number of entries removed
        """
        cutoff = datetime.now() - timedelta(days=days)
        old_keys = [
            key for key, entry in self._entries.items()
            if entry.created_at < cutoff
        ]
        
        for key in old_keys:
            del self._entries[key]
        
        if old_keys:
            self._save_cache()
        
        return len(old_keys)
    
    def list_cached(self) -> list:
        """List all cached entries.
        
        Returns:
            List of CacheEntry instances
        """
        return list(self._entries.values())
    
    def ensure_gitignore(self, output_path: Path) -> None:
        """Ensure .gitignore excludes the dashboard output folder.
        
        Creates or updates .gitignore in the parent repo to exclude 
        the lens-dashboard output folder.
        
        Args:
            output_path: Path where dashboard is stored
        """
        output_path = Path(output_path)
        
        # Find the repo root (parent of .cortex or reports folder)
        # Walk up to find the actual repo
        repo_path = output_path.parent
        while repo_path.name in [".cortex", "reports", "lens-dashboard"]:
            repo_path = repo_path.parent
        
        gitignore_path = repo_path / ".gitignore"
        
        # Calculate relative path from repo to output
        try:
            rel_path = output_path.relative_to(repo_path)
            gitignore_entry = f"{rel_path}/"
        except ValueError:
            # If not relative, use the folder name
            gitignore_entry = f"{output_path.name}/"
        
        # Content to add
        gitignore_content = f"\n# CORTEX LENS Dashboard generated files\n{gitignore_entry}\n"
        
        if gitignore_path.exists():
            # Append if not already present
            existing = gitignore_path.read_text()
            if gitignore_entry not in existing and "CORTEX LENS" not in existing:
                with open(gitignore_path, "a") as f:
                    f.write(gitignore_content)
        else:
            # Create the gitignore
            gitignore_path.write_text(gitignore_content.lstrip())
    
    @classmethod
    def instance(cls) -> "CacheManager":
        """Get singleton instance.
        
        Returns:
            CacheManager singleton
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    @classmethod
    def reset_instance(cls) -> None:
        """Reset singleton instance (for testing)."""
        cls._instance = None


def get_cache_manager() -> CacheManager:
    """Get the CacheManager singleton instance.
    
    Returns:
        CacheManager singleton
    """
    return CacheManager.instance()
