"""
Enhanced Governance Audit Logger - Compliance & Change Tracking

Purpose:
    Comprehensive audit logging for governance rule changes. Tracks all
    modifications to Tier 1 and Tier 2 rules with full attribution,
    timestamps, and reasons for compliance and forensic analysis.

Features:
    - Complete change history (create, update, delete, override, restore)
    - User/actor attribution for all changes
    - Reason logging for compliance audit trails
    - Queryable audit logs filtered by rule_id, actor, action, date range
    - Event categorization (manual, automated, system)
    - Compliance with CORE-034 (Audit logging) and CORE-027 (Audit trail)

Author: Asif Hussain
Version: 1.0
"""

import json
import logging
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from cortex.brain.core.governance_database import AuditAction, GovernanceDatabaseManager
from cortex.models.canonical_enums import AuditEventType

logger = logging.getLogger(__name__)




@dataclass
class AuditEvent:
    """Represents a single audit event."""
    audit_id: str
    event_type: str
    rule_id: str
    actor: str
    timestamp: str
    reason: Optional[str]
    previous_state: Optional[Dict[str, Any]]
    new_state: Optional[Dict[str, Any]]
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict())


class EnhancedGovernanceAuditLogger:
    """
    Enhanced audit logger for governance rule changes.

    Provides comprehensive audit logging for all governance operations
    with full traceability and compliance support.
    """

    _instance: Optional['EnhancedGovernanceAuditLogger'] = None
    _lock = __import__('threading').Lock()

    def __init__(self):
        """Initialize audit logger."""
        self.db_manager = GovernanceDatabaseManager.instance()
        self._logger = logging.getLogger(__name__)

    @classmethod
    def instance(cls) -> 'EnhancedGovernanceAuditLogger':
        """Get singleton instance."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def log_rule_created(
        self,
        rule_id: str,
        rule_name: str,
        actor: str,
        reason: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AuditEvent:
        """
        Log creation of a new governance rule.

        Args:
            rule_id: Rule identifier
            rule_name: Human-readable rule name
            actor: User/system creating the rule
            reason: Optional reason for creation
            metadata: Optional additional metadata

        Returns:
            Created AuditEvent
        """
        event_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()

        event = AuditEvent(
            audit_id=event_id,
            event_type=AuditEventType.RULE_CREATED.value,
            rule_id=rule_id,
            actor=actor,
            timestamp=now,
            reason=reason,
            previous_state=None,
            new_state={"rule_id": rule_id, "name": rule_name},
            metadata=metadata,
        )

        self.db_manager.log_audit_event(
            rule_id=rule_id,
            action=AuditAction.CREATE.value,
            actor=actor,
            new_state=json.dumps({"rule_id": rule_id, "name": rule_name}),
            reason=reason,
        )

        self._logger.info(
            f"✅ Audit: Rule created - {rule_id} by {actor}"
        )

        return event

    def log_rule_updated(
        self,
        rule_id: str,
        previous_state: Dict[str, Any],
        new_state: Dict[str, Any],
        actor: str,
        reason: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AuditEvent:
        """
        Log update to a governance rule.

        Args:
            rule_id: Rule identifier
            previous_state: State before update
            new_state: State after update
            actor: User/system making the update
            reason: Optional reason for update
            metadata: Optional additional metadata

        Returns:
            Created AuditEvent
        """
        event_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()

        event = AuditEvent(
            audit_id=event_id,
            event_type=AuditEventType.RULE_UPDATED.value,
            rule_id=rule_id,
            actor=actor,
            timestamp=now,
            reason=reason,
            previous_state=previous_state,
            new_state=new_state,
            metadata=metadata,
        )

        self.db_manager.log_audit_event(
            rule_id=rule_id,
            action=AuditAction.UPDATE.value,
            actor=actor,
            previous_state=json.dumps(previous_state),
            new_state=json.dumps(new_state),
            reason=reason,
        )

        self._logger.info(
            f"✅ Audit: Rule updated - {rule_id} by {actor}"
        )

        return event

    def log_rule_deleted(
        self,
        rule_id: str,
        previous_state: Dict[str, Any],
        actor: str,
        reason: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AuditEvent:
        """
        Log deletion of a governance rule.

        Args:
            rule_id: Rule identifier
            previous_state: State before deletion
            actor: User/system deleting the rule
            reason: Optional reason for deletion
            metadata: Optional additional metadata

        Returns:
            Created AuditEvent
        """
        event_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()

        event = AuditEvent(
            audit_id=event_id,
            event_type=AuditEventType.RULE_DELETED.value,
            rule_id=rule_id,
            actor=actor,
            timestamp=now,
            reason=reason,
            previous_state=previous_state,
            new_state=None,
            metadata=metadata,
        )

        self.db_manager.log_audit_event(
            rule_id=rule_id,
            action=AuditAction.DELETE.value,
            actor=actor,
            previous_state=json.dumps(previous_state),
            reason=reason,
        )

        self._logger.info(
            f"✅ Audit: Rule deleted - {rule_id} by {actor}"
        )

        return event

    def get_audit_history(
        self,
        rule_id: Optional[str] = None,
        actor: Optional[str] = None,
        event_type: Optional[str] = None,
        limit: int = 100,
    ) -> List[AuditEvent]:
        """
        Query audit log with filtering.

        Args:
            rule_id: Optional filter by rule_id
            actor: Optional filter by actor
            event_type: Optional filter by event type
            limit: Maximum results to return

        Returns:
            List of matching AuditEvent objects
        """
        # Get raw audit logs from database
        db_logs = self.db_manager.get_audit_log(rule_id=rule_id, limit=limit)

        # Convert to AuditEvent objects
        events = []
        for log in db_logs:
            # Parse JSON states
            prev_state = (
                json.loads(log.previous_state)
                if log.previous_state
                else None
            )
            new_state = (
                json.loads(log.new_state)
                if log.new_state
                else None
            )

            event = AuditEvent(
                audit_id=log.audit_id,
                event_type=log.action,
                rule_id=log.rule_id,
                actor=log.actor,
                timestamp=log.timestamp,
                reason=log.reason,
                previous_state=prev_state,
                new_state=new_state,
            )

            # Apply additional filters
            if actor and event.actor != actor:
                continue
            if event_type and event.event_type != event_type:
                continue

            events.append(event)

        return events

    def get_rule_change_summary(self, rule_id: str) -> Dict[str, Any]:
        """
        Get summary of all changes to a rule.

        Args:
            rule_id: Rule identifier

        Returns:
            Dictionary with summary statistics
        """
        history = self.get_audit_history(rule_id=rule_id)

        return {
            "rule_id": rule_id,
            "total_changes": len(history),
            "created_by": history[-1].actor if history else None,
            "created_at": history[-1].timestamp if history else None,
            "last_modified_by": history[0].actor if history else None,
            "last_modified_at": history[0].timestamp if history else None,
            "modification_count": sum(
                1 for e in history
                if e.event_type == AuditEventType.RULE_UPDATED.value
            ),
            "events": [e.to_dict() for e in history],
        }

    def get_compliance_report(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate compliance audit report.

        Args:
            start_date: Optional ISO format start date
            end_date: Optional ISO format end date

        Returns:
            Compliance report with statistics
        """
        history = self.get_audit_history()

        # Filter by date range if provided
        if start_date or end_date:
            filtered_history = []
            for event in history:
                if start_date and event.timestamp < start_date:
                    continue
                if end_date and event.timestamp > end_date:
                    continue
                filtered_history.append(event)
            history = filtered_history

        # Generate statistics
        actions_count = {}
        actors_set = set()
        rules_set = set()

        for event in history:
            actions_count[event.event_type] = (
                actions_count.get(event.event_type, 0) + 1
            )
            actors_set.add(event.actor)
            rules_set.add(event.rule_id)

        return {
            "report_generated_at": datetime.now(timezone.utc).isoformat(),
            "period": {"start": start_date, "end": end_date},
            "statistics": {
                "total_events": len(history),
                "total_rules_affected": len(rules_set),
                "total_actors": len(actors_set),
                "actions_breakdown": actions_count,
            },
            "actors": sorted(list(actors_set)),
            "event_count_by_type": actions_count,
        }
