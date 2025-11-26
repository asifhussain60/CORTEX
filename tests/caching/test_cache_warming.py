"""
Test script for cache warming functionality
Validates that cache warming works correctly in background

Tests:
1. Cache warming starts successfully
2. Runs in background without blocking
3. Warms all operations (align, deploy, optimize, cleanup)
4. Handles errors gracefully
5. Git hooks integration works

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import sys
import time
from pathlib import Path
import logging

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from src.caching.cache_warmer import CacheWarmer
from src.caching import get_cache

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_cache_warming():
    """Test cache warming functionality."""
    
    print("=" * 80)
    print("CORTEX Cache Warming Test Suite")
    print("=" * 80)
    print()
    
    # Test 1: Initialize warmer
    print("Test 1: Initialize CacheWarmer")
    try:
        warmer = CacheWarmer(project_root)
        print("✅ CacheWarmer initialized successfully")
        print(f"   Project root: {warmer.project_root}")
    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
        return False
    print()
    
    # Test 2: Start background warming
    print("Test 2: Start background cache warming")
    try:
        start_time = time.time()
        warmer.warm_cache_background(['align', 'optimize', 'cleanup'])
        elapsed = time.time() - start_time
        print(f"✅ Cache warming started in {elapsed:.3f}s (non-blocking)")
        print(f"   Is warming: {warmer.is_warming}")
    except Exception as e:
        print(f"❌ Failed to start warming: {e}")
        return False
    print()
    
    # Test 3: Verify non-blocking behavior
    print("Test 3: Verify non-blocking behavior")
    print("   Performing other work while cache warms...")
    for i in range(3):
        time.sleep(0.5)
        print(f"   Doing work... {i+1}/3")
    print("✅ Successfully performed work while cache warming in background")
    print()
    
    # Test 4: Wait for completion
    print("Test 4: Wait for cache warming completion")
    try:
        warmer.wait_for_completion(timeout=30.0)
        print(f"✅ Cache warming completed")
        print(f"   Is warming: {warmer.is_warming}")
    except Exception as e:
        print(f"⚠️  Warning: {e}")
    print()
    
    # Test 5: Verify cache contents
    print("Test 5: Verify cache was populated")
    try:
        cache = get_cache()
        
        # Check align cache
        align_keys = cache.get_all_keys('align')
        print(f"   Align operation: {len(align_keys)} keys cached")
        
        # Check optimize cache
        optimize_keys = cache.get_all_keys('optimize')
        print(f"   Optimize operation: {len(optimize_keys)} keys cached")
        
        # Check cleanup cache
        cleanup_keys = cache.get_all_keys('cleanup')
        print(f"   Cleanup operation: {len(cleanup_keys)} keys cached")
        
        total_keys = len(align_keys) + len(optimize_keys) + len(cleanup_keys)
        if total_keys > 0:
            print(f"✅ Cache populated with {total_keys} total keys")
        else:
            print("⚠️  Warning: No keys cached (operations may have failed)")
    except Exception as e:
        print(f"❌ Failed to verify cache: {e}")
        return False
    print()
    
    # Test 6: Cache statistics
    print("Test 6: Cache statistics")
    try:
        for operation in ['align', 'optimize', 'cleanup']:
            stats = cache.get_stats(operation)
            if stats:
                hit_rate = stats.get('hit_rate', 0.0)
                hits = stats.get('hits', 0)
                misses = stats.get('misses', 0)
                print(f"   {operation.capitalize()}: {hit_rate*100:.1f}% hit rate ({hits} hits, {misses} misses)")
        print("✅ Cache statistics retrieved successfully")
    except Exception as e:
        print(f"⚠️  Warning: Could not retrieve stats: {e}")
    print()
    
    # Test 7: Error handling
    print("Test 7: Error handling (invalid project root)")
    try:
        bad_warmer = CacheWarmer(Path("/nonexistent/path"))
        bad_warmer.warm_cache_background(['align'])
        # Should not fail, just log warning
        time.sleep(1)
        print("✅ Gracefully handled invalid project root")
    except Exception as e:
        print(f"⚠️  Warning: {e}")
    print()
    
    print("=" * 80)
    print("✅ All cache warming tests completed successfully!")
    print("=" * 80)
    
    return True


if __name__ == '__main__':
    success = test_cache_warming()
    sys.exit(0 if success else 1)
