"""
Tests for PersistentApplicationCache

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
import tempfile
from pathlib import Path
import time

from src.crawlers.persistent_cache import PersistentApplicationCache


@pytest.fixture
def cache_manager():
    """Create a cache manager with temporary directory"""
    with tempfile.TemporaryDirectory() as tmpdir:
        cache = PersistentApplicationCache(
            cache_dir=Path(tmpdir),
            max_cache_size_mb=10,  # Small for testing
            ttl_days=1  # Short TTL for testing
        )
        yield cache


def test_cache_init(cache_manager):
    """Test cache initialization"""
    assert cache_manager.cache_apps_dir.exists()
    assert cache_manager.index_db_path.exists()
    assert cache_manager.max_cache_size_mb == 10
    assert cache_manager.ttl_days == 1


def test_put_and_get(cache_manager):
    """Test basic cache operations"""
    # Store data
    data = {
        'app_name': 'TestApp',
        'entry_points': ['index.cfm', 'app.cfc'],
        'item_count': 2
    }
    
    success = cache_manager.put(
        app_name='TestApp',
        depth='shallow',
        fingerprint='abc123',
        data=data
    )
    
    assert success is True
    
    # Retrieve data
    cached = cache_manager.get(
        app_name='TestApp',
        depth='shallow',
        fingerprint='abc123'
    )
    
    assert cached is not None
    assert cached['app_name'] == 'TestApp'
    assert len(cached['entry_points']) == 2


def test_cache_miss(cache_manager):
    """Test cache miss scenarios"""
    # Non-existent app
    cached = cache_manager.get(
        app_name='NonExistent',
        depth='shallow',
        fingerprint='xyz789'
    )
    assert cached is None
    
    # Wrong fingerprint
    cache_manager.put('TestApp', 'shallow', 'abc123', {'data': 'test'})
    cached = cache_manager.get('TestApp', 'shallow', 'wrong_fingerprint')
    assert cached is None


def test_cache_stats(cache_manager):
    """Test cache statistics"""
    # Add some entries
    for i in range(3):
        cache_manager.put(
            app_name=f'App{i}',
            depth='shallow',
            fingerprint=f'fp{i}',
            data={'test': i}
        )
    
    stats = cache_manager.get_stats()
    
    assert stats['total_entries'] == 3
    assert stats['apps_cached'] == 3
    assert stats['total_size_mb'] > 0


def test_clear_app(cache_manager):
    """Test clearing cache for specific app"""
    # Add multiple apps
    cache_manager.put('App1', 'shallow', 'fp1', {'data': 'test1'})
    cache_manager.put('App2', 'shallow', 'fp2', {'data': 'test2'})
    
    # Clear one app
    success = cache_manager.clear_app('App1')
    assert success is True
    
    # Verify App1 is gone, App2 remains
    assert cache_manager.get('App1', 'shallow', 'fp1') is None
    assert cache_manager.get('App2', 'shallow', 'fp2') is not None


def test_clear_all(cache_manager):
    """Test clearing all cache"""
    # Add entries
    cache_manager.put('App1', 'shallow', 'fp1', {'data': 'test1'})
    cache_manager.put('App2', 'shallow', 'fp2', {'data': 'test2'})
    
    # Clear all
    success = cache_manager.clear_all()
    assert success is True
    
    # Verify all gone
    stats = cache_manager.get_stats()
    assert stats['total_entries'] == 0


def test_hit_count_tracking(cache_manager):
    """Test hit count tracking"""
    # Add entry
    cache_manager.put('TestApp', 'shallow', 'fp1', {'data': 'test'})
    
    # Access multiple times
    for _ in range(5):
        cache_manager.get('TestApp', 'shallow', 'fp1')
    
    stats = cache_manager.get_stats()
    assert stats['max_hits'] == 5


def test_lru_eviction(cache_manager):
    """Test LRU eviction when cache is full"""
    # Fill cache with entries
    # (Note: With max_cache_size_mb=10, we need to create enough data to trigger eviction)
    large_data = {'data': 'x' * 1000000}  # ~1MB
    
    for i in range(15):  # More than max_cache_size_mb
        cache_manager.put(f'App{i}', 'shallow', f'fp{i}', large_data)
    
    stats = cache_manager.get_stats()
    # Should have evicted some entries
    assert stats['total_entries'] < 15


def test_multiple_depths(cache_manager):
    """Test caching different depths for same app"""
    shallow_data = {'depth': 'shallow', 'items': 10}
    deep_data = {'depth': 'deep', 'items': 100}
    
    # Store both depths
    cache_manager.put('TestApp', 'shallow', 'fp1', shallow_data)
    cache_manager.put('TestApp', 'deep', 'fp1', deep_data)
    
    # Retrieve both
    cached_shallow = cache_manager.get('TestApp', 'shallow', 'fp1')
    cached_deep = cache_manager.get('TestApp', 'deep', 'fp1')
    
    assert cached_shallow['depth'] == 'shallow'
    assert cached_deep['depth'] == 'deep'
    assert cached_deep['items'] == 100


def test_cache_file_structure(cache_manager):
    """Test cache file structure creation"""
    cache_manager.put('TestApp', 'shallow', 'fp1', {'test': 'data'})
    
    # Verify directory structure
    app_dir = cache_manager.cache_apps_dir / 'TestApp'
    assert app_dir.exists()
    
    cache_file = app_dir / 'shallow_context.json'
    assert cache_file.exists()


def test_get_total_cache_size(cache_manager):
    """Test cache size calculation"""
    # Add some entries
    cache_manager.put('App1', 'shallow', 'fp1', {'data': 'test' * 1000})
    cache_manager.put('App2', 'shallow', 'fp2', {'data': 'test' * 1000})
    
    size_mb = cache_manager._get_total_cache_size_mb()
    assert size_mb > 0
    assert isinstance(size_mb, float)


def test_access_stats_update(cache_manager):
    """Test that access stats are updated correctly"""
    cache_manager.put('TestApp', 'shallow', 'fp1', {'data': 'test'})
    
    # First access
    time1 = time.time()
    cache_manager.get('TestApp', 'shallow', 'fp1')
    
    # Wait a bit
    time.sleep(0.1)
    
    # Second access
    time2 = time.time()
    cache_manager.get('TestApp', 'shallow', 'fp1')
    
    stats = cache_manager.get_stats()
    assert stats['max_hits'] == 2


def test_most_accessed(cache_manager):
    """Test most accessed tracking"""
    # Create entries with different access patterns
    cache_manager.put('App1', 'shallow', 'fp1', {'data': 'test1'})
    cache_manager.put('App2', 'shallow', 'fp2', {'data': 'test2'})
    cache_manager.put('App3', 'shallow', 'fp3', {'data': 'test3'})
    
    # Access App1 most
    for _ in range(5):
        cache_manager.get('App1', 'shallow', 'fp1')
    
    # Access App2 less
    for _ in range(2):
        cache_manager.get('App2', 'shallow', 'fp2')
    
    stats = cache_manager.get_stats()
    most_accessed = stats['most_accessed']
    
    assert len(most_accessed) > 0
    assert most_accessed[0]['app'] == 'App1'
    assert most_accessed[0]['hits'] == 5


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
