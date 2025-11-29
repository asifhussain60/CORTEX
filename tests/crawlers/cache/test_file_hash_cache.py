"""
Tests for File Hash Cache

Author: CORTEX Application Health Dashboard
"""

import pytest
import tempfile
import time
from pathlib import Path
from src.crawlers.cache.file_hash_cache import FileHashCache, FileHashEntry


@pytest.fixture
def temp_cache():
    """Create temporary cache database"""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        cache_path = f.name
    
    cache = FileHashCache(cache_db_path=cache_path, ttl_days=1)
    yield cache
    
    # Cleanup - explicitly close and wait
    cache.close()
    time.sleep(0.1)  # Give Windows time to release file handle
    try:
        Path(cache_path).unlink()
    except PermissionError:
        pass  # Ignore cleanup errors on Windows


@pytest.fixture
def temp_file():
    """Create temporary test file"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("test content")
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    Path(temp_path).unlink(missing_ok=True)


class TestFileHashCacheInitialization:
    """Test cache initialization"""
    
    def test_cache_creation(self, temp_cache):
        """Test cache can be created"""
        assert temp_cache is not None
        assert Path(temp_cache.cache_db_path).exists()
    
    def test_default_cache_location(self):
        """Test default cache location"""
        cache = FileHashCache(ttl_days=1)
        assert cache.cache_db_path is not None
        assert '.cortex' in cache.cache_db_path


class TestFileHashCalculation:
    """Test hash calculation"""
    
    def test_calculate_hash(self, temp_cache, temp_file):
        """Test SHA256 hash calculation"""
        hash1 = temp_cache.calculate_hash(temp_file)
        assert hash1 is not None
        assert len(hash1) == 64  # SHA256 hex digest length
    
    def test_consistent_hash(self, temp_cache, temp_file):
        """Test hash is consistent for same content"""
        hash1 = temp_cache.calculate_hash(temp_file)
        hash2 = temp_cache.calculate_hash(temp_file)
        assert hash1 == hash2
    
    def test_different_content_different_hash(self, temp_cache):
        """Test different content produces different hash"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f1:
            f1.write("content1")
            path1 = f1.name
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f2:
            f2.write("content2")
            path2 = f2.name
        
        try:
            hash1 = temp_cache.calculate_hash(path1)
            hash2 = temp_cache.calculate_hash(path2)
            assert hash1 != hash2
        finally:
            Path(path1).unlink(missing_ok=True)
            Path(path2).unlink(missing_ok=True)


class TestCacheOperations:
    """Test cache CRUD operations"""
    
    def test_update_and_get_cache(self, temp_cache, temp_file):
        """Test updating and retrieving cache entry"""
        # Update cache
        temp_cache.update_cache(temp_file, analysis_level="standard")
        
        # Retrieve
        entry = temp_cache.get_cached_hash(temp_file)
        assert entry is not None
        assert entry.file_path == str(Path(temp_file).resolve())
        assert entry.analysis_level == "standard"
    
    def test_get_nonexistent_file(self, temp_cache):
        """Test getting cache for non-existent file"""
        entry = temp_cache.get_cached_hash("nonexistent.txt")
        assert entry is None
    
    def test_cache_miss_for_new_file(self, temp_cache, temp_file):
        """Test cache miss for file not in cache"""
        entry = temp_cache.get_cached_hash(temp_file)
        assert entry is None


class TestCacheInvalidation:
    """Test cache invalidation"""
    
    def test_is_file_changed_new_file(self, temp_cache, temp_file):
        """Test new file is detected as changed"""
        assert temp_cache.is_file_changed(temp_file) is True
    
    def test_is_file_changed_cached_unchanged(self, temp_cache, temp_file):
        """Test cached unchanged file is detected correctly"""
        # Cache the file
        temp_cache.update_cache(temp_file)
        
        # Check immediately - should be unchanged
        assert temp_cache.is_file_changed(temp_file) is False
    
    def test_is_file_changed_after_modification(self, temp_cache, temp_file):
        """Test file change detection after modification"""
        # Cache the file
        temp_cache.update_cache(temp_file)
        
        # Modify file
        time.sleep(0.01)  # Ensure mtime changes
        with open(temp_file, 'a') as f:
            f.write("\nmodified")
        
        # Should detect change
        assert temp_cache.is_file_changed(temp_file) is True
    
    def test_invalidate_file(self, temp_cache, temp_file):
        """Test manual cache invalidation"""
        # Cache the file
        temp_cache.update_cache(temp_file)
        
        # Invalidate
        temp_cache.invalidate_file(temp_file)
        
        # Should be None now
        entry = temp_cache.get_cached_hash(temp_file)
        assert entry is None


class TestCacheTTL:
    """Test cache TTL (time-to-live)"""
    
    def test_expired_cache_entry(self):
        """Test expired cache entries are removed"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            cache_path = f.name
        
        # Create cache with very short TTL
        cache = FileHashCache(cache_db_path=cache_path, ttl_days=0)  # Expires immediately
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("test")
            temp_file = f.name
        
        try:
            # Update cache
            cache.update_cache(temp_file)
            
            # Wait for expiration
            time.sleep(0.1)
            
            # Should return None (expired)
            entry = cache.get_cached_hash(temp_file)
            assert entry is None
        finally:
            cache.close()
            time.sleep(0.1)
            Path(temp_file).unlink(missing_ok=True)
            try:
                Path(cache_path).unlink()
            except PermissionError:
                pass  # Ignore on Windows


class TestCacheStatistics:
    """Test cache statistics"""
    
    def test_get_cache_stats_empty(self, temp_cache):
        """Test stats for empty cache"""
        stats = temp_cache.get_cache_stats()
        assert stats['total_entries'] == 0
        assert stats['total_size_bytes'] == 0
    
    def test_get_cache_stats_with_entries(self, temp_cache, temp_file):
        """Test stats with cache entries"""
        # Add entry
        temp_cache.update_cache(temp_file, analysis_level="standard")
        
        stats = temp_cache.get_cache_stats()
        assert stats['total_entries'] == 1
        assert stats['total_size_bytes'] > 0
        assert 'standard' in stats['by_analysis_level']
    
    def test_clear_cache(self, temp_cache, temp_file):
        """Test clearing all cache entries"""
        # Add entry
        temp_cache.update_cache(temp_file)
        
        # Clear
        temp_cache.clear_cache()
        
        # Check empty
        stats = temp_cache.get_cache_stats()
        assert stats['total_entries'] == 0
