"""COMPAT shim — cortex.core.database → cortex.infrastructure.database.

Phase 58-B: Canonical implementation lives in cortex/infrastructure/database.py.
"""
# noqa: F401
from cortex.infrastructure.database import DatabaseConfig, DatabaseManager, get_database_manager

__all__ = ["DatabaseConfig", "DatabaseManager", "get_database_manager"]
