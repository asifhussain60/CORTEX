"""
Database Manager (MCP-First Architecture)

This is a minimal shim for backward compatibility. Database management has
been replaced with YAML-backed configuration — CORTEX is delivered via
MCP (stdio transport) or SaaS, with no SQLite/relational database required.

See: cortex-registry/planning/phases/completed/2025/ (migration plan)
"""

import logging
from dataclasses import dataclass
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


@dataclass
class DatabaseConfig:
    """Database configuration settings (stub for backward compatibility)."""
    host: str = "localhost"
    port: int = 5432
    database: str = "cortex"
    user: str = "cortex"
    password: str = ""
    pool_size: int = 5
    max_overflow: int = 10


class DatabaseManager:
    """
    Stub DatabaseManager for backward compatibility.

    In the MCP-first architecture, persistent state is managed via:
    - YAML configuration files (cortex/wiring/specifications/wiring.yaml)
    - .cortex-runtime/ for logs, traces, and metrics only
    """

    _instance: Optional['DatabaseManager'] = None

    def __new__(cls) -> 'DatabaseManager':
        """Singleton pattern for backward compatibility."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        """Initialize stub database manager."""
        if self._initialized:
            return
        self._initialized = True
        self._data: Dict[str, Any] = {}
        logger.debug("DatabaseManager stub initialized (MCP-first: no SQLite)")

    def execute(self, query: str, params: tuple = ()) -> None:
        """Stub execute - logs warning and no-ops."""
        logger.warning(f"DatabaseManager.execute called (stub): {query[:50]}...")

    def fetchone(self, query: str, params: tuple = ()) -> Optional[tuple]:
        """Stub fetchone - returns None."""
        logger.warning(f"DatabaseManager.fetchone called (stub): {query[:50]}...")
        return None

    def fetchall(self, query: str, params: tuple = ()) -> list:
        """Stub fetchall - returns empty list."""
        logger.warning(f"DatabaseManager.fetchall called (stub): {query[:50]}...")
        return []

    def close(self) -> None:
        """Stub close - no-ops."""
        pass


def get_database_manager() -> DatabaseManager:
    """Get singleton database manager instance."""
    return DatabaseManager()
