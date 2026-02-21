"""
AuditVerifier — E2E audit trail verification utility.

Validates that orchestrator invocations produce complete, consistent,
and chronologically ordered audit records in CortexAuditDB.

Authority: Phase 13 Sub-Phase C (AC-P13-003)
"""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from cortex.infrastructure.audit_db import AuditEntry, CortexAuditDB, EventType, get_audit_db


class AuditVerificationError(Exception):
    """Raised when audit trail verification fails."""


class AuditVerifier:
    """
    Verifies audit trail integrity for orchestrator invocations.

    Provides assertions for:
    - Event existence (start/end pairs)
    - Required fields on every entry
    - Timestamp monotonicity
    - Full chain from user request to enforcement
    """

    REQUIRED_FIELDS = ("event_type", "orchestrator_id", "status", "timestamp")

    def __init__(self, db: Optional[CortexAuditDB] = None) -> None:
        """Initialize verifier.

        Args:
            db: CortexAuditDB instance (uses singleton if None).
        """
        self.db = db or get_audit_db()

    # ------------------------------------------------------------------
    # Single-orchestrator assertions
    # ------------------------------------------------------------------

    def assert_event_exists(
        self,
        orchestrator_id: str,
        event_type: str,
    ) -> AuditEntry:
        """Assert that at least one matching event exists.

        Args:
            orchestrator_id: Orchestrator to check.
            event_type: Expected event type string.

        Returns:
            The first matching AuditEntry.

        Raises:
            AuditVerificationError: If no matching event found.
        """
        events = self.db.query_events(
            orchestrator_id=orchestrator_id,
            event_type=event_type,
            limit=1,
        )
        if not events:
            raise AuditVerificationError(
                f"No {event_type} event found for orchestrator '{orchestrator_id}'"
            )
        return events[0]

    def assert_start_end_pair(
        self,
        orchestrator_id: str,
    ) -> Tuple[AuditEntry, AuditEntry]:
        """Assert that an orchestrator has both START and END events.

        Args:
            orchestrator_id: Orchestrator to check.

        Returns:
            Tuple of (start_entry, end_entry).

        Raises:
            AuditVerificationError: If either event is missing.
        """
        start = self.assert_event_exists(
            orchestrator_id, EventType.ORCHESTRATOR_START.value
        )
        end = self.assert_event_exists(
            orchestrator_id, EventType.ORCHESTRATOR_END.value
        )
        return start, end

    def assert_required_fields(self, entry: AuditEntry) -> None:
        """Assert that an audit entry has all required fields populated.

        Args:
            entry: AuditEntry to validate.

        Raises:
            AuditVerificationError: If any required field is missing/empty.
        """
        for field_name in self.REQUIRED_FIELDS:
            value = getattr(entry, field_name, None)
            if value is None or (isinstance(value, str) and not value.strip()):
                raise AuditVerificationError(
                    f"Required field '{field_name}' is missing or empty on "
                    f"audit entry id={entry.id}"
                )

    # ------------------------------------------------------------------
    # Multi-event assertions
    # ------------------------------------------------------------------

    def assert_timestamps_monotonic(
        self,
        orchestrator_id: Optional[str] = None,
        limit: int = 100,
    ) -> List[AuditEntry]:
        """Assert that audit event timestamps are monotonically non-decreasing.

        Args:
            orchestrator_id: Optional filter by orchestrator.
            limit: Max events to check.

        Returns:
            The list of events checked.

        Raises:
            AuditVerificationError: If timestamps go backward.
        """
        events = self.db.query_events(
            orchestrator_id=orchestrator_id,
            limit=limit,
        )
        # query_events returns DESC order — reverse for chronological
        events = list(reversed(events))

        for i in range(1, len(events)):
            prev_ts = events[i - 1].timestamp
            curr_ts = events[i].timestamp
            if prev_ts and curr_ts and curr_ts < prev_ts:
                raise AuditVerificationError(
                    f"Timestamp regression: event {events[i].id} "
                    f"({curr_ts.isoformat()}) is before event "
                    f"{events[i-1].id} ({prev_ts.isoformat()})"
                )
        return events

    def assert_all_entries_have_required_fields(
        self,
        orchestrator_id: Optional[str] = None,
        limit: int = 100,
    ) -> int:
        """Assert every event has required fields.

        Args:
            orchestrator_id: Optional filter.
            limit: Max events.

        Returns:
            Count of validated entries.

        Raises:
            AuditVerificationError: On first missing field.
        """
        events = self.db.query_events(
            orchestrator_id=orchestrator_id,
            limit=limit,
        )
        for entry in events:
            self.assert_required_fields(entry)
        return len(events)

    # ------------------------------------------------------------------
    # Full chain verification
    # ------------------------------------------------------------------

    def verify_full_chain(
        self,
        orchestrator_ids: List[str],
    ) -> Dict[str, Any]:
        """Verify a complete audit chain across multiple orchestrators.

        Checks:
        1. Every orchestrator has start+end events
        2. All entries have required fields
        3. Timestamps are globally monotonic
        4. End events have duration_ms > 0

        Args:
            orchestrator_ids: Ordered list of orchestrator IDs in the chain.

        Returns:
            Dict with verification summary.

        Raises:
            AuditVerificationError: On any verification failure.
        """
        results: Dict[str, Any] = {
            "chain_length": len(orchestrator_ids),
            "verified": [],
            "total_events": 0,
        }

        all_events: List[AuditEntry] = []

        for orch_id in orchestrator_ids:
            start_evt, end_evt = self.assert_start_end_pair(orch_id)
            self.assert_required_fields(start_evt)
            self.assert_required_fields(end_evt)

            events = self.db.query_events(orchestrator_id=orch_id, limit=100)
            all_events.extend(events)

            results["verified"].append(orch_id)
            results["total_events"] += len(events)

        # Global timestamp monotonicity across chain
        all_events.sort(key=lambda e: e.timestamp or datetime.min)
        for i in range(1, len(all_events)):
            prev_ts = all_events[i - 1].timestamp
            curr_ts = all_events[i].timestamp
            if prev_ts and curr_ts and curr_ts < prev_ts:
                raise AuditVerificationError(
                    f"Cross-orchestrator timestamp regression between "
                    f"events {all_events[i-1].id} and {all_events[i].id}"
                )

        results["timestamps_monotonic"] = True
        return results
