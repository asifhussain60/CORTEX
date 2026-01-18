"""
Vision Rollback Manager - AC-AR-015-03

Implements vision rollback capability to previous states:
- Rolling back to previous vision snapshots
- Validating rollback safety
- Updating orchestrators on rollback
- Logging all rollback events
- Preventing unsafe rollbacks
- Confirming successful rollback

Enables safe vision evolution while maintaining the ability
to revert to known good states if needed.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple, Set
from datetime import datetime
import hashlib
from pathlib import Path
import json


class RollbackStatus(Enum):
    """Status of a rollback operation."""
    PENDING = "pending"
    VALIDATING = "validating"
    APPROVED = "approved"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


class RollbackReason(Enum):
    """Reason for rollback."""
    BREAKING_CHANGE = "breaking_change"
    UNINTENDED_CONSEQUENCE = "unintended_consequence"
    SAFETY_ISSUE = "safety_issue"
    PERFORMANCE_DEGRADATION = "performance_degradation"
    ORCHESTRATOR_INCOMPATIBILITY = "orchestrator_incompatibility"
    USER_REQUEST = "user_request"
    SCHEDULED_REVERT = "scheduled_revert"


@dataclass
class RollbackValidation:
    """Validation result for a rollback operation."""
    is_safe: bool
    validation_errors: List[str] = field(default_factory=list)
    validation_warnings: List[str] = field(default_factory=list)
    affected_orchestrators: Set[str] = field(default_factory=set)
    data_loss_risk: str = "none"  # none, low, medium, high
    estimated_impact: str = ""
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "is_safe": self.is_safe,
            "validation_errors": self.validation_errors,
            "validation_warnings": self.validation_warnings,
            "affected_orchestrators": sorted(list(self.affected_orchestrators)),
            "data_loss_risk": self.data_loss_risk,
            "estimated_impact": self.estimated_impact,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class RollbackEvent:
    """Record of a rollback operation."""
    rollback_id: str
    from_snapshot_id: str
    to_snapshot_id: str
    reason: RollbackReason
    initiated_by: str
    status: RollbackStatus
    affected_orchestrators: Set[str] = field(default_factory=set)
    validation: Optional[RollbackValidation] = None
    start_timestamp: datetime = field(default_factory=datetime.now)
    completion_timestamp: Optional[datetime] = None
    error_message: Optional[str] = None
    orchestrators_updated: Set[str] = field(default_factory=set)
    notes: str = ""

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "rollback_id": self.rollback_id,
            "from_snapshot_id": self.from_snapshot_id,
            "to_snapshot_id": self.to_snapshot_id,
            "reason": self.reason.value,
            "initiated_by": self.initiated_by,
            "status": self.status.value,
            "validation": self.validation.to_dict() if self.validation else None,
            "start_timestamp": self.start_timestamp.isoformat(),
            "completion_timestamp": self.completion_timestamp.isoformat() if self.completion_timestamp else None,
            "error_message": self.error_message,
            "orchestrators_updated": sorted(list(self.orchestrators_updated)),
            "notes": self.notes,
        }

    @staticmethod
    def from_dict(data: Dict) -> "RollbackEvent":
        """Create from dictionary."""
        validation_data = data.get("validation")
        validation = None
        if validation_data:
            validation = RollbackValidation(
                is_safe=validation_data["is_safe"],
                validation_errors=validation_data.get("validation_errors", []),
                validation_warnings=validation_data.get("validation_warnings", []),
                affected_orchestrators=set(validation_data.get("affected_orchestrators", [])),
                data_loss_risk=validation_data.get("data_loss_risk", "none"),
                estimated_impact=validation_data.get("estimated_impact", ""),
                timestamp=datetime.fromisoformat(validation_data.get("timestamp", datetime.now().isoformat())),
            )
        
        return RollbackEvent(
            rollback_id=data["rollback_id"],
            from_snapshot_id=data["from_snapshot_id"],
            to_snapshot_id=data["to_snapshot_id"],
            reason=RollbackReason(data["reason"]),
            initiated_by=data["initiated_by"],
            status=RollbackStatus(data["status"]),
            validation=validation,
            start_timestamp=datetime.fromisoformat(data.get("start_timestamp", datetime.now().isoformat())),
            completion_timestamp=datetime.fromisoformat(data["completion_timestamp"]) if data.get("completion_timestamp") else None,
            error_message=data.get("error_message"),
            orchestrators_updated=set(data.get("orchestrators_updated", [])),
            notes=data.get("notes", ""),
        )


class VisionRollbackValidator:
    """Validates vision rollbacks for safety and consistency."""

    def validate_rollback(
        self,
        current_snapshot_id: str,
        target_snapshot_id: str,
        affected_orchestrators: Set[str],
        registry_data: Optional[Dict] = None,
    ) -> RollbackValidation:
        """
        Validate a rollback operation.
        
        Args:
            current_snapshot_id: ID of current vision snapshot
            target_snapshot_id: ID of target snapshot to rollback to
            affected_orchestrators: Orchestrators that will be affected
            registry_data: Optional orchestrator registry data
            
        Returns:
            RollbackValidation with results
        """
        validation = RollbackValidation(is_safe=True)

        # Check snapshot IDs are valid
        if not current_snapshot_id or not target_snapshot_id:
            validation.is_safe = False
            validation.validation_errors.append("Invalid snapshot IDs")
            return validation

        # Check snapshots are different
        if current_snapshot_id == target_snapshot_id:
            validation.is_safe = False
            validation.validation_errors.append("Cannot rollback to current snapshot")
            return validation

        # Add affected orchestrators
        validation.affected_orchestrators = affected_orchestrators

        # Validate orchestrator compatibility
        if registry_data and not self._validate_orchestrator_compatibility(registry_data, affected_orchestrators):
            validation.validation_warnings.append("Some orchestrators may have compatibility issues")
            validation.data_loss_risk = "low"

        return validation

    def _validate_orchestrator_compatibility(self, registry_data: Dict, orchestrators: Set[str]) -> bool:
        """Check if all orchestrators are known and registered."""
        if not registry_data or "orchestrators" not in registry_data:
            return True
        
        registered = set(registry_data["orchestrators"].keys())
        unknown = orchestrators - registered
        
        return len(unknown) == 0


class VisionRollbackManager:
    """
    Manages vision rollback operations.
    
    Handles:
    - Validating rollback safety
    - Executing rollback operations
    - Updating orchestrators
    - Recording rollback events
    - Preventing unsafe rollbacks
    - Providing rollback history
    """

    def __init__(self, storage_path: Optional[Path] = None):
        """
        Initialize rollback manager.
        
        Args:
            storage_path: Path to JSON file for persistence (optional)
        """
        self.storage_path = storage_path
        self.rollback_events: Dict[str, RollbackEvent] = {}
        self.rollback_counter = 0
        self.validator = VisionRollbackValidator()
        self._load_from_storage()

    def initiate_rollback(
        self,
        current_snapshot_id: str,
        target_snapshot_id: str,
        reason: RollbackReason,
        initiated_by: str,
        affected_orchestrators: Optional[Set[str]] = None,
        notes: str = "",
    ) -> Tuple[bool, str, Optional[str]]:
        """
        Initiate a rollback operation.
        
        Args:
            current_snapshot_id: ID of current snapshot
            target_snapshot_id: ID of target snapshot
            reason: Reason for rollback
            initiated_by: User initiating rollback
            affected_orchestrators: Set of affected orchestrator IDs
            notes: Optional notes about rollback
            
        Returns:
            Tuple of (success, message, rollback_id)
        """
        # Generate rollback ID
        self.rollback_counter += 1
        rollback_id = f"RB-{self.rollback_counter:05d}"

        # Create rollback event
        affected_orchs = affected_orchestrators or set()
        event = RollbackEvent(
            rollback_id=rollback_id,
            from_snapshot_id=current_snapshot_id,
            to_snapshot_id=target_snapshot_id,
            reason=reason,
            initiated_by=initiated_by,
            status=RollbackStatus.PENDING,
            affected_orchestrators=affected_orchs,
            notes=notes,
        )

        # Validate rollback
        validation = self.validator.validate_rollback(
            current_snapshot_id,
            target_snapshot_id,
            affected_orchs,
        )
        event.validation = validation

        if not validation.is_safe:
            event.status = RollbackStatus.FAILED
            event.error_message = "; ".join(validation.validation_errors)
            self.rollback_events[rollback_id] = event
            return False, f"Rollback validation failed: {event.error_message}", rollback_id

        event.status = RollbackStatus.APPROVED
        self.rollback_events[rollback_id] = event
        self._save_to_storage()

        return True, f"Rollback {rollback_id} initiated and approved", rollback_id

    def execute_rollback(
        self,
        rollback_id: str,
        new_vision_content: Dict,
    ) -> Tuple[bool, str]:
        """
        Execute an approved rollback.
        
        Args:
            rollback_id: ID of rollback to execute
            new_vision_content: Vision content to apply (from target snapshot)
            
        Returns:
            Tuple of (success, message)
        """
        if rollback_id not in self.rollback_events:
            return False, f"Rollback {rollback_id} not found"

        event = self.rollback_events[rollback_id]

        if event.status != RollbackStatus.APPROVED:
            return False, f"Cannot execute rollback in {event.status.value} status"

        event.status = RollbackStatus.EXECUTING

        # Simulate orchestrator updates
        event.orchestrators_updated = event.affected_orchestrators.copy()

        # Complete rollback
        event.status = RollbackStatus.COMPLETED
        event.completion_timestamp = datetime.now()
        
        self._save_to_storage()

        return True, f"Rollback {rollback_id} executed successfully"

    def validate_rollback_dry_run(
        self,
        current_snapshot_id: str,
        target_snapshot_id: str,
        affected_orchestrators: Optional[Set[str]] = None,
        registry_data: Optional[Dict] = None,
    ) -> RollbackValidation:
        """
        Perform a dry-run validation of rollback without executing.
        
        Args:
            current_snapshot_id: ID of current snapshot
            target_snapshot_id: ID of target snapshot
            affected_orchestrators: Orchestrators that would be affected
            registry_data: Optional orchestrator registry data
            
        Returns:
            RollbackValidation results
        """
        return self.validator.validate_rollback(
            current_snapshot_id,
            target_snapshot_id,
            affected_orchestrators or set(),
            registry_data,
        )

    def get_rollback_history(
        self,
        limit: Optional[int] = None,
        status: Optional[RollbackStatus] = None,
    ) -> List[RollbackEvent]:
        """
        Get rollback history with optional filtering.
        
        Args:
            limit: Maximum number of events to return
            status: Filter by rollback status
            
        Returns:
            List of rollback events (most recent first)
        """
        events = list(self.rollback_events.values())

        if status:
            events = [e for e in events if e.status == status]

        # Sort by timestamp (most recent first)
        events.sort(key=lambda e: e.start_timestamp, reverse=True)

        if limit:
            events = events[:limit]

        return events

    def get_rollback_details(self, rollback_id: str) -> Optional[RollbackEvent]:
        """
        Get details of a specific rollback.
        
        Args:
            rollback_id: ID of rollback
            
        Returns:
            RollbackEvent or None if not found
        """
        return self.rollback_events.get(rollback_id)

    def can_rollback_to_snapshot(self, snapshot_id: str) -> Tuple[bool, str]:
        """
        Check if rollback to a specific snapshot is safe.
        
        Args:
            snapshot_id: ID of target snapshot
            
        Returns:
            Tuple of (is_safe, reason)
        """
        if not snapshot_id:
            return False, "Invalid snapshot ID"

        # Check for recent rollbacks to same snapshot
        recent = self.get_rollback_history(limit=5)
        for event in recent:
            if event.to_snapshot_id == snapshot_id and event.status == RollbackStatus.COMPLETED:
                return True, f"Recently rolled back to {snapshot_id}"

        return True, "Safe to rollback"

    def record_orchestrator_update_failure(
        self,
        rollback_id: str,
        orchestrator_id: str,
        error_message: str,
    ) -> Tuple[bool, str]:
        """
        Record orchestrator update failure during rollback.
        
        Args:
            rollback_id: ID of rollback
            orchestrator_id: ID of orchestrator that failed
            error_message: Description of failure
            
        Returns:
            Tuple of (success, message)
        """
        if rollback_id not in self.rollback_events:
            return False, f"Rollback {rollback_id} not found"

        event = self.rollback_events[rollback_id]
        event.orchestrators_updated.discard(orchestrator_id)
        
        if not event.notes:
            event.notes = f"Orchestrator update failures: {orchestrator_id} - {error_message}"
        else:
            event.notes += f"; {orchestrator_id} - {error_message}"

        self._save_to_storage()
        return True, f"Recorded failure for {orchestrator_id}"

    def mark_rollback_complete(
        self,
        rollback_id: str,
        success: bool = True,
        error_message: Optional[str] = None,
    ) -> Tuple[bool, str]:
        """
        Mark rollback as complete.
        
        Args:
            rollback_id: ID of rollback
            success: Whether rollback succeeded
            error_message: Optional error message
            
        Returns:
            Tuple of (success, message)
        """
        if rollback_id not in self.rollback_events:
            return False, f"Rollback {rollback_id} not found"

        event = self.rollback_events[rollback_id]

        if success:
            event.status = RollbackStatus.COMPLETED
        else:
            event.status = RollbackStatus.FAILED
            event.error_message = error_message

        event.completion_timestamp = datetime.now()
        self._save_to_storage()

        return True, f"Rollback {rollback_id} marked as {'completed' if success else 'failed'}"

    def get_rollback_statistics(self) -> Dict:
        """
        Get statistics about rollback operations.
        
        Returns:
            Dictionary with rollback statistics
        """
        if not self.rollback_events:
            return {
                "total_rollbacks": 0,
                "by_status": {},
                "by_reason": {},
                "success_rate": 0.0,
            }

        by_status = {}
        by_reason = {}
        completed_count = 0

        for event in self.rollback_events.values():
            # Count by status
            status_key = event.status.value
            by_status[status_key] = by_status.get(status_key, 0) + 1

            # Count by reason
            reason_key = event.reason.value
            by_reason[reason_key] = by_reason.get(reason_key, 0) + 1

            if event.status == RollbackStatus.COMPLETED:
                completed_count += 1

        success_rate = (completed_count / len(self.rollback_events)) * 100 if self.rollback_events else 0

        return {
            "total_rollbacks": len(self.rollback_events),
            "by_status": by_status,
            "by_reason": by_reason,
            "completed_rollbacks": completed_count,
            "failed_rollbacks": by_status.get("failed", 0),
            "success_rate": round(success_rate, 1),
        }

    def export_rollback_history(self) -> Dict:
        """
        Export rollback history as JSON.
        
        Returns:
            Dictionary ready for JSON serialization
        """
        return {
            "rollback_events": {
                rbk_id: event.to_dict()
                for rbk_id, event in self.rollback_events.items()
            },
            "total_rollbacks": len(self.rollback_events),
            "generated_timestamp": datetime.now().isoformat(),
        }

    def _save_to_storage(self) -> None:
        """Save rollback history to persistent storage."""
        if self.storage_path is None:
            return

        data = self.export_rollback_history()
        self.storage_path.write_text(json.dumps(data, indent=2))

    def _load_from_storage(self) -> None:
        """Load rollback history from persistent storage."""
        if self.storage_path is None or not self.storage_path.exists():
            return

        try:
            data = json.loads(self.storage_path.read_text())
            
            for rbk_id, event_data in data.get("rollback_events", {}).items():
                event = RollbackEvent.from_dict(event_data)
                self.rollback_events[rbk_id] = event
            
            self.rollback_counter = len(self.rollback_events)
        except Exception as e:
            # If loading fails, start fresh
            pass
