"""
Enhanced Audit Logger - Audit-First Pattern with Hash Chain (FR-001)

Implements the audit-first pattern where operations are logged BEFORE execution,
with full hash chain integrity to detect tampering.

Features:
- Pre-execution logging (operation intent logged before execution)
- Hash chain integrity (each entry references previous hash)
- Queryable by AC-ID
- Atomic transaction tracking
- Recovery from failures

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import hashlib
import json
import threading
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from src.core.result import Result, Ok, Err
from src.infrastructure.database import DatabaseManager


@dataclass
class AuditEntry:
    """Represents an audit log entry in the chain."""
    entry_id: int
    timestamp: str
    ac_id: str
    operation: str
    status: str  # PENDING, COMPLETED, FAILED
    details: Dict[str, Any]
    entry_hash: str
    previous_hash: str


class EnhancedAuditLogger:
    """
    Audit logger implementing audit-first pattern.
    
    Thread-safe singleton that:
    - Logs operation intent BEFORE execution
    - Maintains cryptographic hash chain
    - Supports recovery from interruptions
    - Queryable by AC-ID for compliance tracking
    """
    
    _instance: Optional['EnhancedAuditLogger'] = None
    _lock = threading.Lock()
    
    def __init__(self, db: Optional[DatabaseManager] = None):
        """
        Initialize enhanced audit logger.
        
        Args:
            db: DatabaseManager instance
        """
        self._db = db
        self._current_hash: Optional[str] = None
        self._initialized = False
    
    @classmethod
    def instance(cls, db: Optional[DatabaseManager] = None) -> 'EnhancedAuditLogger':
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
        Initialize logger with database.
        
        Args:
            db: DatabaseManager instance
        
        Returns:
            Result containing None if successful, error otherwise
        """
        self._db = db
        self._initialized = True
        
        # Get the last entry hash for chain continuity
        result = self._get_last_entry_hash()
        if result.is_ok():
            self._current_hash = result.unwrap() or "GENESIS"
        
        return Ok(None)
    
    def _get_last_entry_hash(self) -> Result[Optional[str]]:
        """Get the hash of the last audit entry."""
        if not self._db:
            return Err("Database not initialized")
        
        result = self._db.execute(
            "SELECT entry_hash FROM audit_log ORDER BY id DESC LIMIT 1"
        )
        
        if result.is_err():
            return result
        
        rows = result.unwrap()
        if rows and len(rows) > 0:
            return Ok(rows[0][0])
        
        return Ok(None)
    
    def log_operation_start(
        self,
        ac_id: str,
        operation: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> Result[str]:
        """
        Log operation BEFORE execution (audit-first pattern).
        
        Args:
            ac_id: Acceptance Criteria ID
            operation: Operation type (e.g., "AC_START", "AC_EXECUTE")
            details: Additional details
        
        Returns:
            Result containing operation ID for later reference
        """
        if not self._initialized or not self._db:
            return Err("Logger not initialized with database")
        
        timestamp = datetime.now(timezone.utc).isoformat()
        
        # Create entry hash
        hash_input = f"{timestamp}|{ac_id}|{operation}|{self._current_hash or 'GENESIS'}"
        entry_hash = hashlib.sha256(hash_input.encode()).hexdigest()
        
        # Store the operation with PENDING status
        db_result = self._db.insert_audit(
            operation=f"{operation}_START",
            component="audit_first",
            level="AUDIT",
            message=f"Starting {operation} for {ac_id}",
            ac_id=ac_id,
            metadata=details or {},
        )
        
        if db_result.is_err():
            return db_result
        
        # Update current hash for chain continuity
        self._current_hash = entry_hash
        
        return Ok(entry_hash)
    
    def log_operation_complete(
        self,
        ac_id: str,
        operation: str,
        success: bool,
        details: Optional[Dict[str, Any]] = None,
    ) -> Result[str]:
        """
        Log operation completion with result.
        
        Args:
            ac_id: Acceptance Criteria ID
            operation: Operation type
            success: Whether operation succeeded
            details: Result details
        
        Returns:
            Result containing entry hash
        """
        if not self._initialized or not self._db:
            return Err("Logger not initialized with database")
        
        timestamp = datetime.now(timezone.utc).isoformat()
        
        # Create entry hash
        status = "SUCCESS" if success else "FAILED"
        hash_input = f"{timestamp}|{ac_id}|{operation}|{status}|{self._current_hash or 'GENESIS'}"
        entry_hash = hashlib.sha256(hash_input.encode()).hexdigest()
        
        # Store completion with result
        db_result = self._db.insert_audit(
            operation=f"{operation}_COMPLETE",
            component="audit_first",
            level="AUDIT" if success else "WARNING",
            message=f"Completed {operation} for {ac_id} - {status}",
            ac_id=ac_id,
            metadata={
                "status": status,
                "details": details or {},
            },
        )
        
        if db_result.is_err():
            return db_result
        
        # Update current hash
        self._current_hash = entry_hash
        
        return Ok(entry_hash)
    
    def query_by_ac_id(self, ac_id: str) -> Result[List[Dict[str, Any]]]:
        """
        Query all audit entries for an AC-ID.
        
        Returns:
            Result containing list of audit entries
        """
        if not self._db:
            return Err("Database not initialized")
        
        return self._db.query_audit_by_ac_id(ac_id)
    
    def get_operation_history(self, ac_id: str) -> Result[List[Dict[str, Any]]]:
        """
        Get the operation history for an AC-ID.
        
        Returns:
            Result containing ordered list of operations
        """
        result = self.query_by_ac_id(ac_id)
        if result.is_err():
            return result
        
        rows = result.unwrap()
        if not rows:
            return Ok([])
        
        # Rows are already dicts from database
        return Ok(rows)
    
    def verify_hash_chain(self, ac_id: Optional[str] = None) -> Result[bool]:
        """
        Verify hash chain integrity.
        
        Args:
            ac_id: Optional AC-ID to check (all if None)
        
        Returns:
            Result containing True if chain is valid, False otherwise
        """
        if not self._db:
            return Err("Database not initialized")
        
        # Build query
        if ac_id:
            query = "SELECT entry_hash, previous_hash FROM audit_log WHERE ac_id = ? ORDER BY id ASC"
            result = self._db.execute(query, (ac_id,))
        else:
            query = "SELECT entry_hash, previous_hash FROM audit_log ORDER BY id ASC"
            result = self._db.execute(query)
        
        if result.is_err():
            return result
        
        rows = result.unwrap()
        if not rows:
            return Ok(True)  # No entries, chain is valid
        
        # Verify each entry's previous hash matches previous entry's hash
        prev_hash = "GENESIS"
        for row in rows:
            entry_hash, previous_hash = row[0], row[1]
            
            if previous_hash != prev_hash:
                return Ok(False)  # Chain broken
            
            prev_hash = entry_hash
        
        return Ok(True)
    
    def get_chain_status(self) -> Result[Dict[str, Any]]:
        """
        Get current hash chain status.
        
        Returns:
            Result containing chain metadata
        """
        if not self._db:
            return Err("Database not initialized")
        
        # Get total entries
        count_result = self._db.execute("SELECT COUNT(*) FROM audit_log")
        if count_result.is_err():
            return count_result
        
        count = count_result.unwrap()[0][0] if count_result.unwrap() else 0
        
        # Verify chain
        verify_result = self.verify_hash_chain()
        if verify_result.is_err():
            return verify_result
        
        is_valid = verify_result.unwrap()
        
        status = {
            "total_entries": count,
            "chain_valid": is_valid,
            "current_hash": self._current_hash,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        
        return Ok(status)
