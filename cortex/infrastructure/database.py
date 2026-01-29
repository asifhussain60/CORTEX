"""
Database Manager Stub - DEPRECATED (Scheduled for Phase 8 Deletion)

⚠️ DEPRECATION WARNING:

This module is scheduled for complete deletion in Phase 8 (CORE-035 consolidation).
It serves as a backward-compatibility bridge for legacy code while the system
migrates to EnhancedAuditLogger for audit trails and file-based locking.

MIGRATION PATH:
  Old Code:                          New Code:
  ───────────────────────────────────────────────────────────────
  from cortex.infrastructure.database import DatabaseManager
  db = DatabaseManager()             from cortex.infrastructure.enhanced_audit_logger import EnhancedAuditLogger
  db.insert_audit(...)               logger = EnhancedAuditLogger.instance()
                                     logger.log_operation_start(...)

  db.query_audit_trail()             logger.query_by_ac_id(ac_id)
  db.execute(query)                  logger.log_operation_complete(...)

AFFECTED FILES (43 total - Phase 8 epic):
  • Core orchestrators (2): master_orchestrator.py, intent_router.py
  • Governance infrastructure (3): governance_enforcer.py, governance_database.py, state_machine.py
  • Observability/audit (3): enhanced_audit_logger.py, audit_logger.py, audit_trail.py
  • Infrastructure & tools (35): CI/CD gates, MCP tools, cache, logging, etc.

CURRENT STATUS:
  ✅ Phase 1 COMPLETE: 856 lines of dead code removed (3 files)
  ✅ Phase 2 COMPLETE: Deprecation marked, Phase 8 epic documented
  📋 Phase 8 PLANNED: Full refactoring (8-12 hours of focused work)

REFERENCE:
  See: _workspaces/docker-plan/migration-phases-plan.yaml
  See: _workspaces/docker-plan/DATABASE-CLEANUP-STRATEGY.md
  See: _workspaces/docker-plan/DATABASE-CLEANUP-QUICKREF.md
  See: _workspaces/docker-plan/PHASE-2-DEPRECATION-NOTICE.md (this file)
"""

from dataclasses import dataclass
from typing import Optional, Any, Dict
from pathlib import Path
import logging

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
    ⚠️ DEPRECATED - Stub DatabaseManager for backward compatibility.
    
    SCHEDULED FOR DELETION: Phase 8 (CORE-035 consolidation)
    
    This class is a no-op bridge that allows legacy code to continue working
    without modification. New code should use EnhancedAuditLogger directly.
    
    Architecture:
    - YAML configuration files (cortex/wiring/specifications/wiring.yaml)
    - Ephemeral container state
    - Persistent volumes for logs/metrics only
    - EnhancedAuditLogger for all audit operations
    
    Migration: See module docstring for migration examples.
    Timeline: Phase 8 (2-4 weeks out) - comprehensive 8-12 hour refactor
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
        logger.debug("DatabaseManager stub initialized (Docker-first: no SQLite)")
    
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
