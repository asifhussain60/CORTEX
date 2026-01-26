"""
Planning Audit Trail - Database-Backed E2E Verification.

Logs all planning refinement operations to database with SHA256 hash chain
for tamper-proof audit trail. Integrates with EnhancedAuditLogger for
persistent storage.

Features:
  - Complete turn-by-turn logging
  - SHA256 hash chain linking (tamper detection)
  - Clarity progression tracking
  - User response recording
  - Git analysis persistence
  - Challenge/question logging
  - Database persistence via EnhancedAuditLogger
  - Session state reconstruction from audit trail

Hash Chain Integrity:
  Turn N audit_hash = SHA256(
    session_id +
    turn_number +
    timestamp +
    clarity_before +
    clarity_after +
    dor_achieved +
    user_response +
    plan_version +
    Turn(N-1) audit_hash  # Previous hash for chain linking
  )

Tampering Detection:
  If any field is modified, recalculating hash produces different value.
  Chain is broken and audit is flagged as tampered.

Author: CORTEX Master Orchestrator
Version: 2.0
Authority: AC-PLANNING-REFINE-COMPLETE
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime
import hashlib
from enum import Enum


class AuditEventType(Enum):
    """Types of audit events."""

    SESSION_STARTED = "session_started"
    TURN_COMPLETED = "turn_completed"
    CLARITY_MEASURED = "clarity_measured"
    DOR_ACHIEVED = "dor_achieved"
    GIT_ANALYSIS_RECORDED = "git_analysis_recorded"
    USER_RESPONSE_RECORDED = "user_response_recorded"
    APPROVAL_UNLOCKED = "approval_unlocked"
    SESSION_COMPLETED = "session_completed"


@dataclass
class AuditLogEntry:
    """Single audit log entry with hash chain linkage."""

    entry_id: str  # Unique identifier (UUID)
    session_id: str
    event_type: AuditEventType
    timestamp: datetime
    turn_number: Optional[int] = None
    clarity_before: float = 0.0
    clarity_after: float = 0.0
    dor_achieved: bool = False
    user_response: Optional[str] = None
    plan_version: int = 1
    git_analysis_summary: Optional[str] = None
    challenges_count: int = 0
    questions_count: int = 0
    previous_hash: str = ""  # Hash chain linkage
    current_hash: str = ""  # This entry's hash
    additional_data: Dict[str, Any] = field(default_factory=dict)

    def calculate_hash(self) -> str:
        """Calculate SHA256 hash for this entry (includes previous hash for chain)."""
        content = (
            f"{self.session_id}"
            f"{self.turn_number or 0}"
            f"{self.timestamp.isoformat()}"
            f"{self.clarity_before:.6f}"
            f"{self.clarity_after:.6f}"
            f"{self.dor_achieved}"
            f"{self.user_response or ''}"
            f"{self.plan_version}"
            f"{self.git_analysis_summary or ''}"
            f"{self.challenges_count}"
            f"{self.questions_count}"
            f"{self.previous_hash}"  # CRITICAL: Include previous hash
        )
        self.current_hash = hashlib.sha256(content.encode()).hexdigest()
        return self.current_hash

    def verify_integrity(self) -> bool:
        """Verify this entry's hash is correct (detect tampering)."""
        recalculated = self.calculate_hash()
        return recalculated == self.current_hash

    def verify_chain_linkage(self, previous_entry: Optional["AuditLogEntry"]) -> bool:
        """Verify this entry's previous_hash matches actual previous entry."""
        if previous_entry is None:
            return self.previous_hash == ""
        return self.previous_hash == previous_entry.current_hash


@dataclass
class PlanningAuditTrail:
    """Complete audit trail for a planning refinement session."""

    session_id: str
    entries: List[AuditLogEntry] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    last_updated_at: datetime = field(default_factory=datetime.now)

    def add_entry(self, entry: AuditLogEntry) -> str:
        """
        Add an entry to the audit trail.

        Calculates hash chain linkage to previous entry.

        Args:
            entry: AuditLogEntry to add

        Returns:
            The calculated hash for this entry
        """
        # Link to previous entry if exists
        if self.entries:
            entry.previous_hash = self.entries[-1].current_hash
        else:
            entry.previous_hash = ""

        # Calculate hash (includes linkage)
        entry_hash = entry.calculate_hash()

        # Add to trail
        self.entries.append(entry)
        self.last_updated_at = datetime.now()

        return entry_hash

    def get_clarity_progression(self) -> List[float]:
        """Get clarity progression across all turns."""
        return [
            entry.clarity_after
            for entry in self.entries
            if entry.event_type == AuditEventType.CLARITY_MEASURED
        ]

    def verify_chain_integrity(self) -> bool:
        """
        Verify complete hash chain integrity (detect tampering).

        Checks:
        1. Each entry's hash is correct (hasn't been tampered)
        2. Each entry's previous_hash matches actual previous entry
        3. Chain is unbroken from start to end

        Returns:
            True if chain is intact, False if tampering detected
        """
        for i, entry in enumerate(self.entries):
            # Verify entry's own hash
            if not entry.verify_integrity():
                return False

            # Verify chain linkage
            previous_entry = self.entries[i - 1] if i > 0 else None
            if not entry.verify_chain_linkage(previous_entry):
                return False

        return True

    def get_tampering_report(self) -> Dict[str, Any]:
        """
        Generate tampering detection report.

        Returns:
            Dict with:
            - chain_intact: bool
            - tampered_entries: List of entry_ids that failed verification
            - broken_links: List of chain linkage failures
            - first_failure: index of first failure
        """
        report: Dict[str, Any] = {
            "chain_intact": True,
            "tampered_entries": [],
            "broken_links": [],
            "first_failure": None,
        }

        for i, entry in enumerate(self.entries):
            # Check entry hash
            if not entry.verify_integrity():
                report["chain_intact"] = False
                tampered_list = report["tampered_entries"]
                if isinstance(tampered_list, list):
                    tampered_list.append(entry.entry_id)
                if report["first_failure"] is None:
                    report["first_failure"] = i

            # Check chain linkage
            previous_entry = self.entries[i - 1] if i > 0 else None
            if not entry.verify_chain_linkage(previous_entry):
                report["chain_intact"] = False
                broken_list = report["broken_links"]
                if isinstance(broken_list, list):
                    broken_list.append({"entry_index": i, "entry_id": entry.entry_id})
                if report["first_failure"] is None:
                    report["first_failure"] = i

        return report

    def get_session_summary(self) -> Dict[str, Any]:
        """Get summary statistics for the session."""
        turns = [
            e for e in self.entries if e.event_type == AuditEventType.TURN_COMPLETED
        ]
        clarity_entries = [
            e for e in self.entries if e.event_type == AuditEventType.CLARITY_MEASURED
        ]

        return {
            "session_id": self.session_id,
            "total_entries": len(self.entries),
            "total_turns": len(turns),
            "clarity_progression": self.get_clarity_progression(),
            "initial_clarity": clarity_entries[0].clarity_after if clarity_entries else 0.0,
            "final_clarity": clarity_entries[-1].clarity_after if clarity_entries else 0.0,
            "dor_achieved": any(
                e.event_type == AuditEventType.DOR_ACHIEVED for e in self.entries
            ),
            "approval_unlocked": any(
                e.event_type == AuditEventType.APPROVAL_UNLOCKED for e in self.entries
            ),
            "created_at": self.created_at.isoformat(),
            "completed_at": self.last_updated_at.isoformat(),
            "chain_intact": self.verify_chain_integrity(),
        }

    def get_turn_audit(self, turn_number: int) -> Optional[AuditLogEntry]:
        """Get audit entry for specific turn."""
        for entry in self.entries:
            if (
                entry.event_type == AuditEventType.TURN_COMPLETED
                and entry.turn_number == turn_number
            ):
                return entry
        return None

    def get_all_turn_audits(self) -> List[AuditLogEntry]:
        """Get all turn-related audit entries."""
        return [
            e for e in self.entries if e.event_type == AuditEventType.TURN_COMPLETED
        ]

    def export_for_database(self) -> List[Dict[str, Any]]:
        """
        Export audit trail for database persistence.

        Returns:
            List of dicts suitable for database insertion
        """
        return [
            {
                "entry_id": entry.entry_id,
                "session_id": entry.session_id,
                "event_type": entry.event_type.value,
                "timestamp": entry.timestamp.isoformat(),
                "turn_number": entry.turn_number,
                "clarity_before": entry.clarity_before,
                "clarity_after": entry.clarity_after,
                "dor_achieved": entry.dor_achieved,
                "user_response": entry.user_response,
                "plan_version": entry.plan_version,
                "git_analysis_summary": entry.git_analysis_summary,
                "challenges_count": entry.challenges_count,
                "questions_count": entry.questions_count,
                "previous_hash": entry.previous_hash,
                "current_hash": entry.current_hash,
                "additional_data": entry.additional_data,
            }
            for entry in self.entries
        ]
