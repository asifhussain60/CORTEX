"""
AC Completion Audit Requirement Validator

Enforces minimum audit entry requirements before AC-ID completion.
AC-IDs must have at least 3 audit log entries (START, EXECUTE, COMPLETE)
before they can be marked as completed.

Design: Single-responsibility validator for AC audit requirements.
Focuses on audit trail validation, not mutation enforcement.
"""

import sqlite3
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Tuple

from cortex.infrastructure.enhanced_audit_logger import AuditEntry

# =============================================================================
# DATA STRUCTURES
# =============================================================================

class AuditOperationType(Enum):
    """Audit operation types for AC lifecycle."""
    AC_START = "AC_START"
    AC_EXECUTE = "AC_EXECUTE"
    AC_COMPLETE = "AC_COMPLETE"
    AC_VERIFY = "AC_VERIFY"
    AC_REVERT = "AC_REVERT"


class AuditValidationResult(Enum):
    """Result of audit validation."""
    SUFFICIENT = "sufficient_entries"
    INSUFFICIENT = "insufficient_entries"
    MISSING_START = "missing_start_operation"
    MISSING_EXECUTE = "missing_execute_operation"
    MISSING_COMPLETE = "missing_complete_operation"
    SEQUENCING_ERROR = "operation_sequencing_error"
    DATABASE_ERROR = "database_error"
    NOT_FOUND = "ac_id_not_found"


@dataclass
class ACCompletionStatus:
    """AC-ID completion audit status."""
    ac_id: str
    total_entries: int
    required_entries: int
    is_valid: bool
    result_code: str  # AuditValidationResult value
    reason: str

    # Operation presence
    has_start: bool = False
    has_execute: bool = False
    has_complete: bool = False

    # Sequencing
    is_sequenced: bool = False
    sequence_order: List[str] = None  # Order of operations

    # Timeline
    start_time: str = None
    execute_time: str = None
    complete_time: str = None
    total_duration_minutes: float = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "ac_id": self.ac_id,
            "total_entries": self.total_entries,
            "required_entries": self.required_entries,
            "is_valid": self.is_valid,
            "result_code": self.result_code,
            "reason": self.reason,
            "has_start": self.has_start,
            "has_execute": self.has_execute,
            "has_complete": self.has_complete,
            "is_sequenced": self.is_sequenced,
            "sequence_order": self.sequence_order or [],
            "start_time": self.start_time,
            "execute_time": self.execute_time,
            "complete_time": self.complete_time,
            "total_duration_minutes": self.total_duration_minutes
        }


# =============================================================================
# AUDIT OPERATIONS TRACKER
# =============================================================================

class AuditOperationsTracker:
    """Tracks AC-ID audit operations."""

    def __init__(self, db_path: str):
        """
        Initialize tracker with database connection.

        Args:
            db_path: Path to governance.db
        """
        self.db_path = db_path

    def get_ac_entries(self, ac_id: str) -> Tuple[List[AuditEntry], str]:
        """
        Get all audit entries for AC-ID.

        Args:
            ac_id: Acceptance criteria identifier

        Returns:
            Tuple of (entries_list, error_message)
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT id, timestamp, ac_id, operation, actor, details
                FROM audit_log
                WHERE ac_id = ?
                ORDER BY timestamp ASC
                """,
                (ac_id,)
            )

            rows = cursor.fetchall()
            conn.close()

            entries = []
            for row in rows:
                try:
                    import json
                    details = json.loads(row[5]) if row[5] else {}
                except (ValueError, TypeError):
                    details = {}

                entry = AuditEntry(
                    id=row[0],
                    timestamp=row[1],
                    ac_id=row[2],
                    operation=row[3],
                    actor=row[4],
                    details=details
                )
                entries.append(entry)

            return entries, None

        except Exception as e:
            return [], str(e)

    def get_operation_counts(self, ac_id: str) -> Dict[str, int]:
        """
        Get count of each operation type for AC-ID.

        Args:
            ac_id: Acceptance criteria identifier

        Returns:
            Dictionary of operation_type → count
        """
        entries, error = self.get_ac_entries(ac_id)

        if error:
            return {}

        counts = {
            "AC_START": 0,
            "AC_EXECUTE": 0,
            "AC_COMPLETE": 0,
            "AC_VERIFY": 0,
            "AC_REVERT": 0
        }

        for entry in entries:
            if entry.operation in counts:
                counts[entry.operation] += 1

        return counts


# =============================================================================
# AC COMPLETION AUDIT VALIDATOR
# =============================================================================

class ACCompletionAuditValidator:
    """Validates AC-ID completion against audit requirements."""

    # Required operations for completion
    REQUIRED_OPERATIONS = [
        AuditOperationType.AC_START.value,
        AuditOperationType.AC_EXECUTE.value,
        AuditOperationType.AC_COMPLETE.value
    ]

    def __init__(self, db_path: str):
        """
        Initialize validator with database connection.

        Args:
            db_path: Path to governance.db
        """
        self.db_path = db_path
        self.tracker = AuditOperationsTracker(db_path)

    def validate_ac_completion(self, ac_id: str, minimum_entries: int = 3) -> ACCompletionStatus:
        """
        Validate if AC-ID can be marked as completed.

        Args:
            ac_id: Acceptance criteria identifier
            minimum_entries: Minimum required audit entries (default 3)

        Returns:
            ACCompletionStatus with detailed validation result
        """
        # Fetch audit entries
        entries, error = self.tracker.get_ac_entries(ac_id)

        if error:
            return ACCompletionStatus(
                ac_id=ac_id,
                total_entries=0,
                required_entries=minimum_entries,
                is_valid=False,
                result_code=AuditValidationResult.DATABASE_ERROR.value,
                reason=f"Database error: {error}"
            )

        if not entries:
            return ACCompletionStatus(
                ac_id=ac_id,
                total_entries=0,
                required_entries=minimum_entries,
                is_valid=False,
                result_code=AuditValidationResult.NOT_FOUND.value,
                reason=f"No audit entries found for AC {ac_id}"
            )

        # Check entry count
        total_entries = len(entries)
        if total_entries < minimum_entries:
            return ACCompletionStatus(
                ac_id=ac_id,
                total_entries=total_entries,
                required_entries=minimum_entries,
                is_valid=False,
                result_code=AuditValidationResult.INSUFFICIENT.value,
                reason=f"AC {ac_id} has {total_entries} entries (minimum: {minimum_entries})"
            )

        # Check for required operations
        operations = {entry.operation for entry in entries}

        if AuditOperationType.AC_START.value not in operations:
            return ACCompletionStatus(
                ac_id=ac_id,
                total_entries=total_entries,
                required_entries=minimum_entries,
                is_valid=False,
                result_code=AuditValidationResult.MISSING_START.value,
                reason=f"AC {ac_id} missing AC_START operation",
                has_start=False,
                has_execute=AuditOperationType.AC_EXECUTE.value in operations,
                has_complete=AuditOperationType.AC_COMPLETE.value in operations
            )

        if AuditOperationType.AC_EXECUTE.value not in operations:
            return ACCompletionStatus(
                ac_id=ac_id,
                total_entries=total_entries,
                required_entries=minimum_entries,
                is_valid=False,
                result_code=AuditValidationResult.MISSING_EXECUTE.value,
                reason=f"AC {ac_id} missing AC_EXECUTE operation",
                has_start=True,
                has_execute=False,
                has_complete=AuditOperationType.AC_COMPLETE.value in operations
            )

        if AuditOperationType.AC_COMPLETE.value not in operations:
            return ACCompletionStatus(
                ac_id=ac_id,
                total_entries=total_entries,
                required_entries=minimum_entries,
                is_valid=False,
                result_code=AuditValidationResult.MISSING_COMPLETE.value,
                reason=f"AC {ac_id} missing AC_COMPLETE operation",
                has_start=True,
                has_execute=True,
                has_complete=False
            )

        # Verify sequencing (START before EXECUTE before COMPLETE)
        is_sequenced, sequence = self._verify_operation_sequencing(entries)

        if not is_sequenced:
            return ACCompletionStatus(
                ac_id=ac_id,
                total_entries=total_entries,
                required_entries=minimum_entries,
                is_valid=False,
                result_code=AuditValidationResult.SEQUENCING_ERROR.value,
                reason=f"AC {ac_id} operations out of sequence: {' → '.join(sequence)}",
                has_start=True,
                has_execute=True,
                has_complete=True,
                is_sequenced=False,
                sequence_order=sequence
            )

        # Calculate timeline
        start_time, execute_time, complete_time, duration = self._calculate_timeline(entries)

        # All validations passed
        return ACCompletionStatus(
            ac_id=ac_id,
            total_entries=total_entries,
            required_entries=minimum_entries,
            is_valid=True,
            result_code=AuditValidationResult.SUFFICIENT.value,
            reason=f"AC {ac_id} ready for completion ({total_entries} entries, properly sequenced)",
            has_start=True,
            has_execute=True,
            has_complete=True,
            is_sequenced=True,
            sequence_order=sequence,
            start_time=start_time,
            execute_time=execute_time,
            complete_time=complete_time,
            total_duration_minutes=duration
        )

    def _verify_operation_sequencing(self, entries: List[AuditEntry]) -> Tuple[bool, List[str]]:
        """
        Verify operations are in correct sequence: START → EXECUTE → COMPLETE.

        Args:
            entries: List of audit entries (sorted by timestamp)

        Returns:
            Tuple of (is_sequenced, operation_sequence)
        """
        sequence = []
        start_idx = None
        execute_idx = None
        complete_idx = None

        for i, entry in enumerate(entries):
            if entry.operation == AuditOperationType.AC_START.value and start_idx is None:
                start_idx = i
                sequence.append(entry.operation)
            elif entry.operation == AuditOperationType.AC_EXECUTE.value and execute_idx is None:
                execute_idx = i
                sequence.append(entry.operation)
            elif entry.operation == AuditOperationType.AC_COMPLETE.value and complete_idx is None:
                complete_idx = i
                sequence.append(entry.operation)

        # Check if operations are in correct order
        is_correct_order = True
        if start_idx is not None and execute_idx is not None:
            is_correct_order = is_correct_order and (start_idx < execute_idx)
        if execute_idx is not None and complete_idx is not None:
            is_correct_order = is_correct_order and (execute_idx < complete_idx)

        return is_correct_order, sequence

    def _calculate_timeline(self, entries: List[AuditEntry]) -> Tuple[str, str, str, float]:
        """
        Calculate operation timeline from audit entries.

        Args:
            entries: List of audit entries

        Returns:
            Tuple of (start_time, execute_time, complete_time, duration_minutes)
        """
        start_time = None
        execute_time = None
        complete_time = None

        for entry in entries:
            if entry.operation == AuditOperationType.AC_START.value and start_time is None:
                start_time = entry.timestamp
            elif entry.operation == AuditOperationType.AC_EXECUTE.value and execute_time is None:
                execute_time = entry.timestamp
            elif entry.operation == AuditOperationType.AC_COMPLETE.value and complete_time is None:
                complete_time = entry.timestamp

        # Calculate duration
        duration = None
        if start_time and complete_time:
            try:
                from datetime import datetime
                start = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                complete = datetime.fromisoformat(complete_time.replace('Z', '+00:00'))
                duration = (complete - start).total_seconds() / 60.0
            except (ValueError, TypeError):
                pass

        return start_time, execute_time, complete_time, duration

    def get_completion_readiness(self, ac_id: str) -> Dict[str, Any]:
        """
        Get comprehensive AC completion readiness report.

        Args:
            ac_id: Acceptance criteria identifier

        Returns:
            Dictionary with completion readiness details
        """
        status = self.validate_ac_completion(ac_id)

        return {
            "ac_id": ac_id,
            "ready_for_completion": status.is_valid,
            "validation_result": status.result_code,
            "reason": status.reason,
            "status_dict": status.to_dict(),
            "entries_count": status.total_entries,
            "required_count": status.required_entries,
            "operations": {
                "start": status.has_start,
                "execute": status.has_execute,
                "complete": status.has_complete
            },
            "sequencing": {
                "is_correct": status.is_sequenced,
                "sequence": status.sequence_order or []
            },
            "timeline": {
                "start": status.start_time,
                "execute": status.execute_time,
                "complete": status.complete_time,
                "duration_minutes": status.total_duration_minutes
            }
        }


# =============================================================================
# AUDIT REQUIREMENT ENFORCEMENT
# =============================================================================

class AuditRequiredValidator:
    """
    Enforces audit requirements for AC completion.

    Single-responsibility: Validate AC completion prerequisites.
    Does NOT perform mutations - only validation.
    """

    def __init__(self, db_path: str):
        """
        Initialize validator with database connection.

        Args:
            db_path: Path to governance.db
        """
        self.db_path = db_path
        self.completion_validator = ACCompletionAuditValidator(db_path)

    def can_mark_ac_complete(self, ac_id: str) -> Tuple[bool, str]:
        """
        Check if AC-ID can be marked as complete.

        Args:
            ac_id: Acceptance criteria identifier

        Returns:
            Tuple of (allowed, reason)
        """
        status = self.completion_validator.validate_ac_completion(ac_id)

        if status.is_valid:
            return True, f"AC {ac_id} is ready for completion"
        else:
            return False, status.reason

    def get_completion_blockers(self, ac_id: str) -> List[str]:
        """
        Get list of issues preventing AC completion.

        Args:
            ac_id: Acceptance criteria identifier

        Returns:
            List of blocker reasons
        """
        status = self.completion_validator.validate_ac_completion(ac_id)

        blockers = []

        if status.total_entries == 0:
            blockers.append("No audit entries found")
        elif status.total_entries < status.required_entries:
            blockers.append(f"Only {status.total_entries} of {status.required_entries} entries present")

        if not status.has_start:
            blockers.append("Missing AC_START operation")
        if not status.has_execute:
            blockers.append("Missing AC_EXECUTE operation")
        if not status.has_complete:
            blockers.append("Missing AC_COMPLETE operation")

        if not status.is_sequenced:
            blockers.append(f"Operations out of sequence: {' → '.join(status.sequence_order or [])}")

        return blockers

    def get_ac_audit_summary(self, ac_id: str) -> Dict[str, Any]:
        """
        Get comprehensive AC audit summary.

        Args:
            ac_id: Acceptance criteria identifier

        Returns:
            Dictionary with complete audit information
        """
        return self.completion_validator.get_completion_readiness(ac_id)
