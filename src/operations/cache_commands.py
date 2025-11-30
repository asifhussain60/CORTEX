"""
Cache Management Commands for CORTEX

Provides CLI commands for managing the ValidationCache:
- cache status: Show cache statistics
- cache clear: Clear all cache entries
- cache invalidate <operation>: Invalidate specific operation cache

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
Version: 1.0.0
Date: November 26, 2025
"""

from pathlib import Path
from typing import Dict, Any
from src.caching import get_cache
import logging

logger = logging.getLogger(__name__)


def cache_status_command(args: Dict[str, Any] = None) -> str:
    """
    Show cache statistics.
    
    Args:
        args: Optional arguments with 'operation' key for operation-specific stats
    
    Returns:
        Formatted status string
    """
    cache = get_cache()
    operation = args.get('operation') if args else None
    
    stats = cache.get_stats(operation)
    
    lines = []
    lines.append("\n🗄️ **CORTEX ValidationCache Status**")
    lines.append("=" * 60)
    
    if operation:
        lines.append(f"\nOperation: **{operation}**")
    else:
        lines.append(f"\nScope: **All Operations**")
    
    lines.append(f"\n📊 Statistics:")
    lines.append(f"   Cache Hits:         {stats['hits']:,}")
    lines.append(f"   Cache Misses:       {stats['misses']:,}")
    lines.append(f"   Invalidations:      {stats['invalidations']:,}")
    lines.append(f"   Total Requests:     {stats['total_requests']:,}")
    lines.append(f"   Hit Rate:           {stats['hit_rate']:.1f}%")
    lines.append(f"   Total Entries:      {stats['total_entries']:,}")
    
    # Show all keys if specific operation
    if operation:
        keys = cache.get_all_keys(operation)
        if keys:
            lines.append(f"\n🔑 Cached Keys ({len(keys)}):")
            for key_info in keys[:10]:  # Show first 10
                age_min = key_info['age_seconds'] / 60
                ttl_display = f"{key_info['ttl_seconds']}s" if key_info['ttl_seconds'] > 0 else "∞"
                lines.append(f"   - {key_info['key']} (age: {age_min:.1f}m, TTL: {ttl_display})")
            
            if len(keys) > 10:
                lines.append(f"   ... and {len(keys) - 10} more")
    else:
        # Show summary by operation
        lines.append(f"\n📦 Entries by Operation:")
        for op in ['align', 'deploy', 'optimize', 'cleanup']:
            op_stats = cache.get_stats(op)
            if op_stats['total_entries'] > 0:
                lines.append(f"   - {op:12s} {op_stats['total_entries']:3d} entries (hit rate: {op_stats['hit_rate']:.1f}%)")
    
    lines.append("")
    return "\n".join(lines)


def cache_clear_command(args: Dict[str, Any] = None) -> str:
    """
    Clear all cache entries.
    
    Args:
        args: Optional arguments (not used)
    
    Returns:
        Confirmation message
    """
    cache = get_cache()
    
    # Get stats before clearing
    stats_before = cache.get_stats()
    entries_before = stats_before['total_entries']
    
    # Clear cache
    cache.invalidate()
    
    logger.info(f"Cache cleared: {entries_before} entries removed")
    
    return f"\n✅ Cache cleared: {entries_before} entries removed\n"


def cache_invalidate_command(args: Dict[str, Any]) -> str:
    """
    Invalidate specific operation cache.
    
    Args:
        args: Dictionary with 'operation' key (e.g., 'align', 'deploy')
    
    Returns:
        Confirmation message
    """
    if not args or 'operation' not in args:
        return "\n❌ Error: Operation name required. Usage: cache invalidate <operation>\n"
    
    operation = args['operation']
    cache = get_cache()
    
    # Get stats before invalidation
    stats_before = cache.get_stats(operation)
    entries_before = stats_before['total_entries']
    
    # Invalidate operation cache
    cache.invalidate(operation)
    
    logger.info(f"Cache invalidated: {operation} ({entries_before} entries removed)")
    
    return f"\n✅ Cache invalidated: {operation} ({entries_before} entries removed)\n"


def register_cache_commands(command_router):
    """
    Register cache management commands with command router.
    
    Args:
        command_router: CommandRouter instance
    """
    # Register commands
    command_router.register_command(
        triggers=['cache status', 'show cache', 'cache stats'],
        handler=cache_status_command,
        description='Show cache statistics and hit rates',
        category='admin'
    )
    
    command_router.register_command(
        triggers=['cache clear', 'clear cache'],
        handler=cache_clear_command,
        description='Clear all validation cache entries',
        category='admin'
    )
    
    command_router.register_command(
        triggers=['cache invalidate'],
        handler=cache_invalidate_command,
        description='Invalidate cache for specific operation (align, deploy, etc.)',
        category='admin',
        requires_args=True
    )
    
    logger.info("Cache management commands registered")
