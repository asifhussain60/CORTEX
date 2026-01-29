"""Cache Manager for LENS Dashboard.

Manages dashboard output locations and caching for:
- Local repositories (.cortex/lens-dashboard/)
- CORTEX self-analysis (reports/lens-dashboard/)
- Remote repository cache (~/.cortex/cache/<owner>/<repo>/)

This module integrates with the MCP infrastructure for consistent
file management across the CORTEX system.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List
import json
import shutil


@dataclass
class CacheEntry:
    """Represents a cached dashboard entry.
    
    Attributes:
        repo_path: Path to the analyzed repository
        output_path: Path to the generated dashboard
        created_at: Timestamp of cache creation
        expires_at: Timestamp when cache expires
        is_cortex: Whether this is CORTEX self-analysis
    """
    repo_path: str
    output_path: str
    created_at: datetime
    expires_at: datetime
    is_cortex: bool
    
    def is_expired(self) -> bool:
        """Check if this cache entry has expired."""
        return datetime.now() > self.expires_at
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "repo_path": self.repo_path,
            "output_path": self.output_path,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
            "is_cortex": self.is_cortex,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "CacheEntry":
        """Create CacheEntry from dictionary."""
        return cls(
            repo_path=data["repo_path"],
            output_path=data["output_path"],
            created_at=datetime.fromisoformat(data["created_at"]),
            expires_at=datetime.fromisoformat(data["expires_at"]),
            is_cortex=data["is_cortex"],
        )


class CacheManager:
    """Manages dashboard caching and output locations.
    
    This class provides a unified interface for managing dashboard
    outputs across different contexts (local, CORTEX, remote).
    
    Example:
        >>> manager = CacheManager()
        >>> output_path = manager.get_output_path(Path("/my/repo"))
        >>> manager.register_cache(Path("/my/repo"), output_path)
    """
    
    DEFAULT_CACHE_HOURS = 24
    CACHE_INDEX_FILE = "cache_index.json"
    
    def __init__(
        self,
        cache_base: Optional[Path] = None,
        cache_hours: int = DEFAULT_CACHE_HOURS,
    ) -> None:
        """Initialize CacheManager.
        
        Args:
            cache_base: Base directory for cache storage.
                        Defaults to ~/.cortex/cache/
            cache_hours: Hours before cache expires. Defaults to 24.
        """
        self.cache_base = cache_base or Path.home() / ".cortex" / "cache"
        self.cache_hours = cache_hours
        self._entries: List[CacheEntry] = []
        self._load_index()
    
    def _load_index(self) -> None:
        """Load cache index from disk."""
        index_path = self.cache_base / self.CACHE_INDEX_FILE
        if index_path.exists():
            try:
                with open(index_path) as f:
                    data = json.load(f)
                self._entries = [CacheEntry.from_dict(e) for e in data.get("entries", [])]
            except (json.JSONDecodeError, KeyError):
                self._entries = []
    
    def _save_index(self) -> None:
        """Save cache index to disk."""
        self.cache_base.mkdir(parents=True, exist_ok=True)
        index_path = self.cache_base / self.CACHE_INDEX_FILE
        with open(index_path, "w") as f:
            json.dump(
                {"entries": [e.to_dict() for e in self._entries]},
                f,
                indent=2,
            )
    
    def get_output_path(
        self,
        repo_path: Path,
        is_cortex: bool = False,
        is_remote: bool = False,
        owner: Optional[str] = None,
        repo_name: Optional[str] = None,
    ) -> Path:
        """Get the output path for a repository dashboard.
        
        Args:
            repo_path: Path to the repository
            is_cortex: Whether this is CORTEX self-analysis
            is_remote: Whether this is a remote repository
            owner: Repository owner (for remote repos)
            repo_name: Repository name (for remote repos)
            
        Returns:
            Path where dashboard should be generated
        """
        if is_cortex:
            # CORTEX self-analysis goes to reports/
            return repo_path / "reports" / "lens-dashboard"
        elif is_remote:
            # Remote repos go to ~/.cortex/cache/<owner>/<repo>/
            if not owner or not repo_name:
                raise ValueError("owner and repo_name required for remote repos")
            return self.cache_base / owner / repo_name / "lens-dashboard"
        else:
            # Local repos go to .cortex/lens-dashboard/
            return repo_path / ".cortex" / "lens-dashboard"
    
    def register_cache(
        self,
        repo_path: Path,
        output_path: Path,
        is_cortex: bool = False,
    ) -> CacheEntry:
        """Register a new cache entry.
        
        Args:
            repo_path: Path to the analyzed repository
            output_path: Path to the generated dashboard
            is_cortex: Whether this is CORTEX self-analysis
            
        Returns:
            The created CacheEntry
        """
        now = datetime.now()
        entry = CacheEntry(
            repo_path=str(repo_path),
            output_path=str(output_path),
            created_at=now,
            expires_at=now + timedelta(hours=self.cache_hours),
            is_cortex=is_cortex,
        )
        
        # Remove existing entry for same repo
        self._entries = [e for e in self._entries if e.repo_path != str(repo_path)]
        self._entries.append(entry)
        self._save_index()
        
        return entry
    
    def get_cached(self, repo_path: Path) -> Optional[CacheEntry]:
        """Get cached entry for a repository if valid.
        
        Args:
            repo_path: Path to the repository
            
        Returns:
            CacheEntry if found and not expired, None otherwise
        """
        for entry in self._entries:
            if entry.repo_path == str(repo_path):
                if not entry.is_expired():
                    return entry
                # Remove expired entry
                self._entries.remove(entry)
                self._save_index()
                return None
        return None
    
    def invalidate(self, repo_path: Path) -> bool:
        """Invalidate cache for a repository.
        
        Args:
            repo_path: Path to the repository
            
        Returns:
            True if entry was found and removed
        """
        for entry in self._entries:
            if entry.repo_path == str(repo_path):
                self._entries.remove(entry)
                self._save_index()
                return True
        return False
    
    def cleanup_expired(self) -> int:
        """Remove all expired cache entries.
        
        Returns:
            Number of entries removed
        """
        original_count = len(self._entries)
        self._entries = [e for e in self._entries if not e.is_expired()]
        removed = original_count - len(self._entries)
        if removed > 0:
            self._save_index()
        return removed
    
    def cleanup_old_dashboards(self, max_age_days: int = 30) -> int:
        """Remove dashboard files older than max_age_days.
        
        Args:
            max_age_days: Maximum age in days before removal
            
        Returns:
            Number of dashboards removed
        """
        removed = 0
        cutoff = datetime.now() - timedelta(days=max_age_days)
        
        for entry in list(self._entries):
            if entry.created_at < cutoff:
                output_path = Path(entry.output_path)
                if output_path.exists():
                    shutil.rmtree(output_path)
                    removed += 1
                self._entries.remove(entry)
        
        if removed > 0:
            self._save_index()
        
        return removed
    
    def list_cached(self) -> List[CacheEntry]:
        """List all cached entries (including expired).
        
        Returns:
            List of all cache entries
        """
        return list(self._entries)
    
    def ensure_gitignore(self, output_path: Path) -> None:
        """Ensure .gitignore entry exists for output path.
        
        For local repositories, adds lens-dashboard/ to .gitignore
        if not already present.
        
        Args:
            output_path: Path to the dashboard output directory
        """
        # Only add gitignore for local repos (those with .cortex/)
        if ".cortex" not in str(output_path):
            return
            
        repo_root = output_path.parent.parent  # .cortex/lens-dashboard/ -> repo root
        gitignore_path = repo_root / ".gitignore"
        
        entry = ".cortex/lens-dashboard/"
        
        if gitignore_path.exists():
            content = gitignore_path.read_text()
            if entry not in content:
                with open(gitignore_path, "a") as f:
                    f.write(f"\n# LENS Dashboard output\n{entry}\n")
        else:
            with open(gitignore_path, "w") as f:
                f.write(f"# LENS Dashboard output\n{entry}\n")


def get_cache_manager() -> CacheManager:
    """Get a singleton CacheManager instance.
    
    Returns:
        Global CacheManager instance
    """
    global _cache_manager
    if "_cache_manager" not in globals():
        _cache_manager = CacheManager()
    return _cache_manager
