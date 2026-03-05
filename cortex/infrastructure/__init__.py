"""
CORTEX Infrastructure Module

Production-grade infrastructure components:
- enhanced_audit_logger.py: Hash-chain audit logging
- file_locker.py: Cross-platform file locking
- sqlite_manager.py: SQLite connection management
- env_initializer.py: Canonical fast-init for .cortex-runtime/ + all 7 SQLite DBs (Phase 109)
"""

# Phase 109: Expose env_initializer public API at package level
from cortex.infrastructure.env_initializer import (
    DB_REGISTRY,
    RUNTIME_DIRS,
    EnvironmentInitializer,
    initialize_runtime_environment,
    verify_runtime_environment,
)

__all__ = [
    "DB_REGISTRY",
    "RUNTIME_DIRS",
    "EnvironmentInitializer",
    "initialize_runtime_environment",
    "verify_runtime_environment",
]
