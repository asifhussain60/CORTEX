"""
CORTEX Caching Module

Unified validation cache for all CORTEX entry points.
Provides file hash tracking, cross-operation result sharing, and automatic invalidation.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

from .validation_cache import ValidationCache, CacheEntry, get_cache, clear_global_cache

__all__ = ['ValidationCache', 'CacheEntry', 'get_cache', 'clear_global_cache']
