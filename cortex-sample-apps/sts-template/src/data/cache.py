"""
Cache Module
PERF-03: Memory leak (no cleanup, infinite growth)
SEC-10: Sensitive data cached without encryption
"""
import time

# PERF-03: Global cache with no TTL or size limits (FLAW)
_cache = {}

def cache_set(key, value, ttl=None):
    """
    PERF-03: No TTL implementation (FLAW)
    SEC-10: No encryption for sensitive data (FLAW)
    """
    # SEC-10: Caches sensitive data in plain text (FLAW)
    _cache[key] = {
        'value': value,
        'timestamp': time.time(),
        'ttl': ttl  # Stored but never used (FLAW)
    }

def cache_get(key):
    """
    Get from cache
    PERF-03: Never checks TTL, never expires entries (FLAW)
    """
    if key in _cache:
        # PERF-03: Should check TTL and remove expired entries (FLAW)
        return _cache[key]['value']
    return None

def cache_clear():
    """Clear entire cache"""
    global _cache
    _cache = {}

# PERF-03: No automatic cleanup mechanism (FLAW)
# Cache grows infinitely, causing memory leak
