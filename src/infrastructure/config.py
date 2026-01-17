"""
Infrastructure Configuration Module

Centralized configuration for infrastructure components including:
- Timeout settings for thread operations
- Database connection parameters
- Telemetry configuration

AC-FIX-BRITTLENESS-004: Timeout Configuration

Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional
import os


@dataclass
class TimeoutConfig:
    """
    Timeout configuration for infrastructure operations.
    
    All blocking operations should use these timeouts to prevent
    indefinite hangs.
    """
    # Thread operations
    thread_join: float = 5.0  # Timeout for thread.join() calls
    thread_start: float = 10.0  # Timeout waiting for thread start
    
    # Database operations  
    database: float = 30.0  # SQLite connection timeout
    query: float = 10.0  # Individual query timeout
    
    # Queue operations
    queue_get: float = 5.0  # Queue.get() timeout
    queue_put: float = 5.0  # Queue.put() timeout
    
    # Network operations (future)
    http_connect: float = 10.0  # HTTP connection timeout
    http_read: float = 30.0  # HTTP read timeout
    
    # Graceful shutdown
    shutdown_grace: float = 5.0  # Grace period for shutdown
    
    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary."""
        return {
            'thread_join': self.thread_join,
            'thread_start': self.thread_start,
            'database': self.database,
            'query': self.query,
            'queue_get': self.queue_get,
            'queue_put': self.queue_put,
            'http_connect': self.http_connect,
            'http_read': self.http_read,
            'shutdown_grace': self.shutdown_grace,
        }


# Global timeout configuration instance
_timeout_config: Optional[TimeoutConfig] = None


def get_timeout_config() -> Dict[str, float]:
    """
    Get timeout configuration.
    
    Returns a dictionary of timeout values for various operations.
    Values can be overridden via environment variables:
    - CORTEX_TIMEOUT_THREAD_JOIN
    - CORTEX_TIMEOUT_DATABASE
    - CORTEX_TIMEOUT_QUEUE_GET
    etc.
    
    Returns:
        Dictionary of timeout name to value in seconds
    """
    global _timeout_config
    
    if _timeout_config is None:
        _timeout_config = TimeoutConfig(
            thread_join=float(os.environ.get('CORTEX_TIMEOUT_THREAD_JOIN', 5.0)),
            database=float(os.environ.get('CORTEX_TIMEOUT_DATABASE', 30.0)),
            queue_get=float(os.environ.get('CORTEX_TIMEOUT_QUEUE_GET', 5.0)),
        )
    
    return _timeout_config.to_dict()


def set_timeout_config(config: TimeoutConfig) -> None:
    """
    Set custom timeout configuration.
    
    Args:
        config: TimeoutConfig instance
    """
    global _timeout_config
    _timeout_config = config


def reset_timeout_config() -> None:
    """Reset timeout configuration to defaults."""
    global _timeout_config
    _timeout_config = None


# Convenience functions for common timeouts
def get_thread_join_timeout() -> float:
    """Get thread join timeout."""
    return get_timeout_config()['thread_join']


def get_database_timeout() -> float:
    """Get database connection timeout."""
    return get_timeout_config()['database']


def get_queue_timeout() -> float:
    """Get queue operation timeout."""
    return get_timeout_config()['queue_get']
