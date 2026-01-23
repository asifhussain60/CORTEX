"""
Tiered Logger - Tiered Logging Architecture (AR-004)

Implements tiered logging with configurable levels:
- AUDIT: Always logged to governance.db (highest priority)
- CRITICAL: Error/blocking conditions
- WARNING: Potential issues
- INFO: General information
- DEBUG: Detailed debugging information

Features:
- Logs written to governance.db with hash chain
- Configurable log levels per tier
- Structured JSON format for all logs
- Thread-safe singleton access

Author: Asif Hussain
"""

import json
import logging
import threading
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional

from cortex.brain.core.result import Result, Ok, Err
from cortex.infrastructure.database import DatabaseManager


class LogLevel(Enum):
    """Log level enumeration."""
    AUDIT = "AUDIT"
    CRITICAL = "CRITICAL"
    WARNING = "WARNING"
    INFO = "INFO"
    DEBUG = "DEBUG"


class LogTier(Enum):
    """Logging tier enumeration."""
    TIER0 = 0
    TIER1 = 1
    TIER2 = 2


@dataclass
class LogEntry:
    """Structured log entry."""
    timestamp: str
    level: str
    tier: int
    component: str
    message: str
    ac_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(asdict(self), default=str)


class TieredLogger:
    """
    Tiered logging system for CORTEX.
    
    Thread-safe singleton that manages:
    - Tiered log level configuration
    - Structured JSON logging
    - Database persistence for AUDIT level
    - Python logging integration
    """
    
    _instance: Optional['TieredLogger'] = None
    _lock = threading.Lock()
    
    def __init__(self, db: Optional[DatabaseManager] = None):
        """
        Initialize tiered logger.
        
        Args:
            db: DatabaseManager instance (uses global if None)
        """
        self._db = db
        self._logger = logging.getLogger(__name__)
        self._log_levels: Dict[int, LogLevel] = {
            0: LogLevel.AUDIT,      # Tier 0: always audit everything
            1: LogLevel.INFO,       # Tier 1: info and above
            2: LogLevel.WARNING,    # Tier 2: warnings and above
        }
        self._initialized = False
    
    @classmethod
    def instance(cls, db: Optional[DatabaseManager] = None) -> 'TieredLogger':
        """Get singleton instance."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls(db)
        return cls._instance
    
    @classmethod
    def reset_instance(cls) -> None:
        """Reset singleton instance (for testing)."""
        with cls._lock:
            cls._instance = None
    
    def initialize(self, db: DatabaseManager) -> Result[None]:
        """
        Initialize logger with database manager.
        
        Args:
            db: DatabaseManager instance
        
        Returns:
            Result containing None if successful, error otherwise
        """
        self._db = db
        self._initialized = True
        self._logger.info("Tiered logger initialized")
        return Ok(None)
    
    def set_log_level(self, tier: int, level: LogLevel) -> Result[None]:
        """
        Set log level for a tier.
        
        Args:
            tier: Governance tier (0, 1, or 2)
            level: LogLevel to set
        
        Returns:
            Result containing None if successful, error otherwise
        """
        if tier not in (0, 1, 2):
            return Err(f"Invalid tier: {tier}. Must be 0, 1, or 2")
        
        self._log_levels[tier] = level
        return Ok(None)
    
    def get_log_level(self, tier: int) -> Result[LogLevel]:
        """
        Get log level for a tier.
        
        Args:
            tier: Governance tier
        
        Returns:
            Result containing LogLevel
        """
        if tier not in (0, 1, 2):
            return Err(f"Invalid tier: {tier}")
        
        return Ok(self._log_levels.get(tier, LogLevel.INFO))
    
    def should_log(self, tier: int, level: LogLevel) -> Result[bool]:
        """
        Determine if a message should be logged.
        
        Args:
            tier: Governance tier
            level: Message log level
        
        Returns:
            Result containing boolean
        """
        tier_level_result = self.get_log_level(tier)
        if tier_level_result.is_err():
            return tier_level_result
        
        tier_level = tier_level_result.unwrap()
        
        # Define level hierarchy
        level_order = {
            LogLevel.DEBUG: 0,
            LogLevel.INFO: 1,
            LogLevel.WARNING: 2,
            LogLevel.CRITICAL: 3,
            LogLevel.AUDIT: 4,
        }
        
        return Ok(level_order.get(level, 0) >= level_order.get(tier_level, 0))
    
    def log_to_audit(
        self,
        component: str,
        message: str,
        tier: int = 0,
        ac_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> Result[None]:
        """
        Log to AUDIT level (database).
        
        Args:
            component: Component name
            message: Log message
            tier: Governance tier
            ac_id: Associated AC-ID if any
            context: Additional context data
        
        Returns:
            Result containing None if successful, error otherwise
        """
        if not self._initialized or self._db is None:
            return Err("Logger not initialized with database")
        
        # Create log entry
        entry = LogEntry(
            timestamp=datetime.now(timezone.utc).isoformat(),
            level=LogLevel.AUDIT.value,
            tier=tier,
            component=component,
            message=message,
            ac_id=ac_id,
            context=context or {},
        )
        
        # Insert to audit log in database
        result = self._db.insert_audit(
            operation="LOG",
            component=component,
            level=LogLevel.AUDIT.value,
            message=message,
            ac_id=ac_id,
            metadata=context or {},
        )
        
        if result.is_err():
            return result
        
        # Also log to Python logging
        self._logger.info(f"[AUDIT] {component}: {message}")
        
        return Ok(None)
    
    def log(
        self,
        level: LogLevel,
        component: str,
        message: str,
        tier: int = 1,
        ac_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> Result[None]:
        """
        Log a message at specified level.
        
        Args:
            level: Log level
            component: Component name
            message: Log message
            tier: Governance tier
            ac_id: Associated AC-ID if any
            context: Additional context data
        
        Returns:
            Result containing None if successful, error otherwise
        """
        # Check if should log
        should_log_result = self.should_log(tier, level)
        if should_log_result.is_err():
            return should_log_result
        
        if not should_log_result.unwrap():
            return Ok(None)  # Don't log, but return success
        
        # Create structured entry
        entry = LogEntry(
            timestamp=datetime.now(timezone.utc).isoformat(),
            level=level.value,
            tier=tier,
            component=component,
            message=message,
            ac_id=ac_id,
            context=context or {},
        )
        
        # If AUDIT level, also write to database
        if level == LogLevel.AUDIT and self._initialized and self._db:
            db_result = self._db.insert_audit(
                operation="LOG",
                component=component,
                level=level.value,
                message=message,
                ac_id=ac_id,
                metadata=context or {},
            )
            if db_result.is_err():
                return db_result
        
        # Log to Python logging
        log_method = {
            LogLevel.DEBUG: self._logger.debug,
            LogLevel.INFO: self._logger.info,
            LogLevel.WARNING: self._logger.warning,
            LogLevel.CRITICAL: self._logger.critical,
            LogLevel.AUDIT: self._logger.info,
        }.get(level, self._logger.info)
        
        log_method(f"[{level.value}] {component}: {message}")
        
        return Ok(None)
    
    def __repr__(self) -> str:
        """String representation."""
        return f"TieredLogger(initialized={self._initialized}, db={'attached' if self._db else 'none'})"
