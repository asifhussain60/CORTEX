"""Tests for LENS Dashboard Cache Manager.

Tests the CacheManager class for:
- Cache entry creation and retrieval
- Expiration handling
- Cleanup operations
- Output path resolution
"""

import json
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch

import pytest

# Import will work at runtime when package is installed
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "cortex-lens"))

from backend.cache_manager import CacheManager, CacheEntry, get_cache_manager


class TestCacheEntry:
    """Tests for CacheEntry dataclass."""
    
    def test_create_cache_entry(self) -> None:
        """Test creating a cache entry."""
        now = datetime.now()
        entry = CacheEntry(
            repo_path="/path/to/repo",
            output_path="/path/to/output",
            created_at=now,
            expires_at=now + timedelta(hours=24),
            is_cortex=False,
        )
        
        assert entry.repo_path == "/path/to/repo"
        assert entry.output_path == "/path/to/output"
        assert entry.is_cortex is False
    
    def test_is_expired_false(self) -> None:
        """Test that fresh entry is not expired."""
        now = datetime.now()
        entry = CacheEntry(
            repo_path="/repo",
            output_path="/output",
            created_at=now,
            expires_at=now + timedelta(hours=24),
            is_cortex=False,
        )
        
        assert entry.is_expired() is False
    
    def test_is_expired_true(self) -> None:
        """Test that old entry is expired."""
        past = datetime.now() - timedelta(hours=48)
        entry = CacheEntry(
            repo_path="/repo",
            output_path="/output",
            created_at=past,
            expires_at=past + timedelta(hours=24),
            is_cortex=False,
        )
        
        assert entry.is_expired() is True
    
    def test_to_dict(self) -> None:
        """Test serialization to dict."""
        now = datetime.now()
        entry = CacheEntry(
            repo_path="/repo",
            output_path="/output",
            created_at=now,
            expires_at=now + timedelta(hours=24),
            is_cortex=True,
        )
        
        d = entry.to_dict()
        
        assert d["repo_path"] == "/repo"
        assert d["output_path"] == "/output"
        assert d["is_cortex"] is True
        assert "created_at" in d
        assert "expires_at" in d
    
    def test_from_dict(self) -> None:
        """Test deserialization from dict."""
        now = datetime.now()
        data = {
            "repo_path": "/repo",
            "output_path": "/output",
            "created_at": now.isoformat(),
            "expires_at": (now + timedelta(hours=24)).isoformat(),
            "is_cortex": False,
        }
        
        entry = CacheEntry.from_dict(data)
        
        assert entry.repo_path == "/repo"
        assert entry.is_cortex is False


class TestCacheManager:
    """Tests for CacheManager class."""
    
    @pytest.fixture
    def temp_cache_dir(self, tmp_path: Path) -> Path:
        """Create a temporary cache directory."""
        cache_dir = tmp_path / "cache"
        cache_dir.mkdir()
        return cache_dir
    
    @pytest.fixture
    def cache_manager(self, temp_cache_dir: Path) -> CacheManager:
        """Create a CacheManager with temp directory."""
        return CacheManager(cache_base=temp_cache_dir)
    
    def test_initialization(self, cache_manager: CacheManager) -> None:
        """Test CacheManager initialization."""
        assert cache_manager.cache_hours == 24
        assert len(cache_manager._entries) == 0
    
    def test_get_output_path_external(
        self,
        cache_manager: CacheManager,
        tmp_path: Path,
    ) -> None:
        """Test output path for external repository."""
        repo_path = tmp_path / "my-project"
        
        output_path = cache_manager.get_output_path(repo_path)
        
        assert output_path == repo_path / ".cortex" / "lens-dashboard"
    
    def test_get_output_path_cortex(
        self,
        cache_manager: CacheManager,
        tmp_path: Path,
    ) -> None:
        """Test output path for CORTEX repository."""
        repo_path = tmp_path / "cortex"
        
        output_path = cache_manager.get_output_path(repo_path, is_cortex=True)
        
        assert output_path == repo_path / "reports" / "lens-dashboard"
    
    def test_get_output_path_remote(
        self,
        cache_manager: CacheManager,
        tmp_path: Path,
    ) -> None:
        """Test output path for remote repository."""
        repo_path = tmp_path / "remote-repo"
        
        output_path = cache_manager.get_output_path(
            repo_path,
            is_remote=True,
            owner="user",
            repo_name="project",
        )
        
        assert "user" in str(output_path)
        assert "project" in str(output_path)
        assert "lens-dashboard" in str(output_path)
    
    def test_get_output_path_remote_missing_params(
        self,
        cache_manager: CacheManager,
        tmp_path: Path,
    ) -> None:
        """Test that remote without owner/repo raises error."""
        repo_path = tmp_path / "remote-repo"
        
        with pytest.raises(ValueError, match="owner and repo_name required"):
            cache_manager.get_output_path(repo_path, is_remote=True)
    
    def test_register_cache(
        self,
        cache_manager: CacheManager,
        tmp_path: Path,
    ) -> None:
        """Test registering a cache entry."""
        repo_path = tmp_path / "repo"
        output_path = tmp_path / "output"
        
        entry = cache_manager.register_cache(repo_path, output_path)
        
        assert entry.repo_path == str(repo_path)
        assert entry.output_path == str(output_path)
        assert not entry.is_expired()
        assert len(cache_manager._entries) == 1
    
    def test_register_cache_replaces_existing(
        self,
        cache_manager: CacheManager,
        tmp_path: Path,
    ) -> None:
        """Test that registering same repo replaces existing entry."""
        repo_path = tmp_path / "repo"
        output_path1 = tmp_path / "output1"
        output_path2 = tmp_path / "output2"
        
        cache_manager.register_cache(repo_path, output_path1)
        cache_manager.register_cache(repo_path, output_path2)
        
        assert len(cache_manager._entries) == 1
        assert cache_manager._entries[0].output_path == str(output_path2)
    
    def test_get_cached_returns_valid_entry(
        self,
        cache_manager: CacheManager,
        tmp_path: Path,
    ) -> None:
        """Test getting a valid cached entry."""
        repo_path = tmp_path / "repo"
        output_path = tmp_path / "output"
        
        cache_manager.register_cache(repo_path, output_path)
        
        entry = cache_manager.get_cached(repo_path)
        
        assert entry is not None
        assert entry.repo_path == str(repo_path)
    
    def test_get_cached_returns_none_for_missing(
        self,
        cache_manager: CacheManager,
        tmp_path: Path,
    ) -> None:
        """Test getting cache for unregistered repo."""
        repo_path = tmp_path / "nonexistent"
        
        entry = cache_manager.get_cached(repo_path)
        
        assert entry is None
    
    def test_invalidate_removes_entry(
        self,
        cache_manager: CacheManager,
        tmp_path: Path,
    ) -> None:
        """Test invalidating a cache entry."""
        repo_path = tmp_path / "repo"
        output_path = tmp_path / "output"
        
        cache_manager.register_cache(repo_path, output_path)
        assert len(cache_manager._entries) == 1
        
        success = cache_manager.invalidate(repo_path)
        
        assert success is True
        assert len(cache_manager._entries) == 0
    
    def test_invalidate_nonexistent_returns_false(
        self,
        cache_manager: CacheManager,
        tmp_path: Path,
    ) -> None:
        """Test invalidating nonexistent entry."""
        repo_path = tmp_path / "nonexistent"
        
        success = cache_manager.invalidate(repo_path)
        
        assert success is False
    
    def test_cleanup_expired(
        self,
        cache_manager: CacheManager,
    ) -> None:
        """Test cleaning up expired entries."""
        # Manually add an expired entry
        past = datetime.now() - timedelta(hours=48)
        entry = CacheEntry(
            repo_path="/old/repo",
            output_path="/old/output",
            created_at=past,
            expires_at=past + timedelta(hours=24),
            is_cortex=False,
        )
        cache_manager._entries.append(entry)
        
        removed = cache_manager.cleanup_expired()
        
        assert removed == 1
        assert len(cache_manager._entries) == 0
    
    def test_list_cached(
        self,
        cache_manager: CacheManager,
        tmp_path: Path,
    ) -> None:
        """Test listing all cached entries."""
        repo_path1 = tmp_path / "repo1"
        repo_path2 = tmp_path / "repo2"
        
        cache_manager.register_cache(repo_path1, tmp_path / "out1")
        cache_manager.register_cache(repo_path2, tmp_path / "out2")
        
        entries = cache_manager.list_cached()
        
        assert len(entries) == 2
    
    def test_persistence_across_instances(
        self,
        temp_cache_dir: Path,
        tmp_path: Path,
    ) -> None:
        """Test that cache persists across manager instances."""
        manager1 = CacheManager(cache_base=temp_cache_dir)
        repo_path = tmp_path / "repo"
        manager1.register_cache(repo_path, tmp_path / "output")
        
        # Create new manager instance
        manager2 = CacheManager(cache_base=temp_cache_dir)
        
        entry = manager2.get_cached(repo_path)
        assert entry is not None
    
    def test_ensure_gitignore_creates_file(
        self,
        cache_manager: CacheManager,
        tmp_path: Path,
    ) -> None:
        """Test that gitignore is created for local repos."""
        repo_path = tmp_path / "repo"
        repo_path.mkdir()
        output_path = repo_path / ".cortex" / "lens-dashboard"
        output_path.mkdir(parents=True)
        
        cache_manager.ensure_gitignore(output_path)
        
        gitignore = repo_path / ".gitignore"
        assert gitignore.exists()
        content = gitignore.read_text()
        assert ".cortex/lens-dashboard/" in content
    
    def test_ensure_gitignore_appends_if_exists(
        self,
        cache_manager: CacheManager,
        tmp_path: Path,
    ) -> None:
        """Test that gitignore is appended if it exists."""
        repo_path = tmp_path / "repo"
        repo_path.mkdir()
        
        # Create existing gitignore
        gitignore = repo_path / ".gitignore"
        gitignore.write_text("*.pyc\n")
        
        output_path = repo_path / ".cortex" / "lens-dashboard"
        output_path.mkdir(parents=True)
        
        cache_manager.ensure_gitignore(output_path)
        
        content = gitignore.read_text()
        assert "*.pyc" in content
        assert ".cortex/lens-dashboard/" in content


class TestGetCacheManager:
    """Tests for singleton cache manager."""
    
    def test_returns_same_instance(self) -> None:
        """Test that get_cache_manager returns singleton."""
        # Clear any existing singleton
        if "_cache_manager" in globals():
            del globals()["_cache_manager"]
        
        manager1 = get_cache_manager()
        manager2 = get_cache_manager()
        
        assert manager1 is manager2
