"""
Audit Logger Connector - Governance audit trail integration

AC-PHASE-41: Master Orchestrator Decomposition
- Logs all operation milestones
- Maintains audit trail integrity
- CORE-027: Audit trail gating
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional


@dataclass
class AuditLogEntry:
    """Single audit log entry."""
    timestamp: str
    phase: str
    operation_id: str
    event: str
    details: Dict[str, Any]
    actor: Optional[str] = None


class AuditLoggerConnector:
    """
    Manages audit trail logging for CORE-027 compliance.

    Responsibilities:
    - Log AC_START for operation initiation
    - Log AC_COMPLETE for operation completion
    - Maintain audit trail integrity
    - Provide audit statistics
    - CORE-027 compliance tracking

    Example:
        logger = AuditLoggerConnector(audit_logger=audit_system)
        logger.log_operation_start(operation_id="op-123", intent="IMPLEMENT")
        # ... operation execution ...
        logger.log_operation_complete(operation_id="op-123", success=True)
    """

    def __init__(self, audit_logger: Optional[Any] = None) -> None:
        """
        Initialize Audit Logger connector.

        Args:
            audit_logger: Reference to audit logging system
        """
        self.audit_logger = audit_logger
        self.logger = logging.getLogger(__name__)
        self._local_log: Dict[str, AuditLogEntry] = {}

    def log_operation_start(
        self,
        operation_id: str,
        intent: str,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log operation start (AC_START marker).

        CORE-027: Mandatory start marker for all operations.

        Args:
            operation_id: Unique operation identifier
            intent: Operation intent (IMPLEMENT, FIX, etc)
            context: Operation context
        """
        timestamp = datetime.utcnow().isoformat()

        entry = AuditLogEntry(
            timestamp=timestamp,
            phase="AC_START",
            operation_id=operation_id,
            event=f"{intent} operation initiated",
            details=context or {}
        )

        self._local_log[operation_id] = entry

        if self.audit_logger:
            try:
                self.audit_logger.log_entry(
                    operation_id=operation_id,
                    phase="AC_START",
                    intent=intent,
                    context=context,
                    timestamp=timestamp
                )
            except Exception as e:
                self.logger.error(f"Error logging operation start: {str(e)}")

    def log_operation_complete(
        self,
        operation_id: str,
        success: bool,
        result: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None
    ) -> None:
        """
        Log operation completion (AC_COMPLETE marker).

        CORE-027: Mandatory complete marker for all operations.

        Args:
            operation_id: Unique operation identifier
            success: Whether operation succeeded
            result: Operation result data
            error: Error message if failed
        """
        timestamp = datetime.utcnow().isoformat()

        entry = AuditLogEntry(
            timestamp=timestamp,
            phase="AC_COMPLETE",
            operation_id=operation_id,
            event="operation completed",
            details={
                "success": success,
                "result": result,
                "error": error
            }
        )

        if self.audit_logger:
            try:
                self.audit_logger.log_entry(
                    operation_id=operation_id,
                    phase="AC_COMPLETE",
                    success=success,
                    result=result,
                    error=error,
                    timestamp=timestamp
                )
            except Exception as e:
                self.logger.error(f"Error logging operation complete: {str(e)}")

    def log_validation_result(
        self,
        operation_id: str,
        validation_type: str,
        passed: bool,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log validation result during operation.

        Args:
            operation_id: Unique operation identifier
            validation_type: Type of validation (DoR, Governance, etc)
            passed: Whether validation passed
            details: Validation details
        """
        timestamp = datetime.utcnow().isoformat()

        if self.audit_logger:
            try:
                self.audit_logger.log_validation(
                    operation_id=operation_id,
                    validation_type=validation_type,
                    passed=passed,
                    details=details,
                    timestamp=timestamp
                )
            except Exception as e:
                self.logger.error(f"Error logging validation: {str(e)}")

    def log_phase_transition(
        self,
        operation_id: str,
        from_phase: str,
        to_phase: str,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log pipeline stage transition.

        Args:
            operation_id: Unique operation identifier
            from_phase: Previous phase
            to_phase: Next phase
            details: Transition details
        """
        timestamp = datetime.utcnow().isoformat()

        if self.audit_logger:
            try:
                self.audit_logger.log_phase_transition(
                    operation_id=operation_id,
                    from_phase=from_phase,
                    to_phase=to_phase,
                    details=details,
                    timestamp=timestamp
                )
            except Exception as e:
                self.logger.error(f"Error logging phase transition: {str(e)}")

    def get_operation_log(self, operation_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve full audit log for operation.

        Args:
            operation_id: Unique operation identifier

        Returns:
            Full operation audit log or None
        """
        if not self.audit_logger:
            return None

        try:
            return self.audit_logger.get_operation_log(operation_id)
        except Exception as e:
            self.logger.error(f"Error retrieving operation log: {str(e)}")
            return None

    def get_audit_stats(self) -> Dict[str, int]:
        """Get audit logging statistics."""
        return {
            "local_entries": len(self._local_log),
            "completed_operations": sum(
                1 for entry in self._local_log.values()
                if entry.phase == "AC_COMPLETE"
            ),
            "started_operations": sum(
                1 for entry in self._local_log.values()
                if entry.phase == "AC_START"
            )
        }
