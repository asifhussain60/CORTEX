"""Conflict Escalation Workflow: 3-Tier Resolution (AC-DB-E03).

Ensures all conflicts are handled through a 3-tier resolution workflow:
1. Tier 1: Apply source hierarchy (BKIO > RELATIONSHIPS > AST > GIT > LENS)
2. Tier 2: Query LENS synthesis for tied sources
3. Tier 3: Escalate to manual review for ambiguous cases (24h SLA)

Handles LENS deferral by escalating to manual review rather than leaving
conflicts unhandled.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum

from src.domain_brain.models import Conflict, AuditOperationType


class ResolutionTier(Enum):
    """Resolution tier classification."""

    HIERARCHY = "HIERARCHY"
    LENS_SYNTHESIS = "LENS_SYNTHESIS"
    MANUAL_REVIEW = "MANUAL_REVIEW"


class ReviewStatus(Enum):
    """Status of manual review."""

    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"
    OVERDUE = "OVERDUE"


@dataclass
class ConflictResolution:
    """Resolution for a conflict."""

    conflict_id: str
    resolution_tier: ResolutionTier
    recommended_value: Any = None
    confidence: float = 0.0
    reasoning: str = ""
    resolved_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "conflict_id": self.conflict_id,
            "resolution_tier": self.resolution_tier.value,
            "recommended_value": self.recommended_value,
            "confidence": self.confidence,
            "reasoning": self.reasoning,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
        }


@dataclass
class ManualReviewTicket:
    """Ticket for manual review."""

    ticket_id: str
    conflict_id: str
    domain_id: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    due_at: datetime = field(default_factory=lambda: datetime.utcnow() + timedelta(hours=24))
    status: ReviewStatus = ReviewStatus.PENDING
    source_values: Dict[str, Any] = field(default_factory=dict)
    assigned_to: Optional[str] = None
    resolution: Optional[str] = None
    resolved_at: Optional[datetime] = None

    @property
    def is_overdue(self) -> bool:
        """Check if ticket is overdue."""
        return datetime.utcnow() > self.due_at and self.status != ReviewStatus.RESOLVED

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "ticket_id": self.ticket_id,
            "conflict_id": self.conflict_id,
            "domain_id": self.domain_id,
            "created_at": self.created_at.isoformat(),
            "due_at": self.due_at.isoformat(),
            "status": self.status.value,
            "source_values": self.source_values,
            "assigned_to": self.assigned_to,
            "resolution": self.resolution,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "is_overdue": self.is_overdue,
        }


class ConflictResolver:
    """3-tier conflict resolution workflow."""

    # Source hierarchy: BKIO > RELATIONSHIPS > AST > GIT > LENS
    SOURCE_HIERARCHY = {
        "BKIO": 5,
        "RELATIONSHIPS": 4,
        "AST": 3,
        "GIT": 2,
        "LENS": 1,
    }

    def __init__(self) -> None:
        """Initialize conflict resolver."""
        self.resolutions: Dict[str, ConflictResolution] = {}
        self.manual_review_queue: List[ManualReviewTicket] = []
        self.tier1_resolved = 0
        self.tier2_resolved = 0
        self.tier3_escalated = 0

    def apply_hierarchy(
        self, sources: Dict[str, Any]
    ) -> Optional[ConflictResolution]:
        """Apply source hierarchy to determine winner.

        Args:
            sources: Dictionary of source -> value

        Returns:
            ConflictResolution or None if no clear winner
        """
        if not sources:
            return None

        # Sort by hierarchy priority
        sorted_sources = sorted(
            sources.items(),
            key=lambda x: self.SOURCE_HIERARCHY.get(x[0], 0),
            reverse=True,
        )

        # Get highest priority source
        best_source, value = sorted_sources[0]
        best_priority = self.SOURCE_HIERARCHY.get(best_source, 0)

        # Check if there's a tie
        if len(sorted_sources) > 1:
            second_priority = self.SOURCE_HIERARCHY.get(sorted_sources[1][0], 0)
            if second_priority == best_priority:
                # Tie detected - needs Tier 2 (LENS synthesis)
                return None

        # Clear winner - Tier 1 resolution
        return ConflictResolution(
            conflict_id="",  # Set by caller
            resolution_tier=ResolutionTier.HIERARCHY,
            recommended_value=value,
            confidence=0.9,  # High confidence for hierarchy
            reasoning=f"Hierarchy winner: {best_source} (priority {best_priority})",
        )

    def query_lens_synthesis(
        self, conflict: Conflict
    ) -> Optional[ConflictResolution]:
        """Query LENS for synthesis on tied sources.

        Args:
            conflict: Conflict to resolve

        Returns:
            ConflictResolution or None if LENS defers
        """
        # Simulate LENS synthesis
        # In reality, this would query LENS IR-004
        if not conflict.source_values:
            return None

        # LENS synthesis succeeds if multiple sources exist
        if len(conflict.source_values) < 2:
            return None

        # Simulate LENS synthesis (70% success rate, 30% deferral)
        import random

        if random.random() > 0.7:
            # LENS defers
            return None

        # LENS synthesizes a value
        best_value = list(conflict.source_values.values())[0]

        return ConflictResolution(
            conflict_id=conflict.conflict_id,
            resolution_tier=ResolutionTier.LENS_SYNTHESIS,
            recommended_value=best_value,
            confidence=0.7,  # Medium confidence for LENS
            reasoning="LENS synthesis of conflicting sources",
        )

    def escalate_to_manual_review(
        self, conflict: Conflict, reason: str
    ) -> ManualReviewTicket:
        """Escalate conflict to manual review.

        Args:
            conflict: Conflict to escalate
            reason: Reason for escalation

        Returns:
            ManualReviewTicket
        """
        ticket_id = f"mrg_{conflict.conflict_id}_{len(self.manual_review_queue)}"

        ticket = ManualReviewTicket(
            ticket_id=ticket_id,
            conflict_id=conflict.conflict_id,
            domain_id=conflict.domain_id,
            source_values=conflict.source_values,
        )

        self.manual_review_queue.append(ticket)
        self.tier3_escalated += 1

        return ticket

    def resolve_conflict(
        self, conflict: Conflict
    ) -> Optional[ConflictResolution]:
        """Resolve conflict through 3-tier workflow.

        Args:
            conflict: Conflict to resolve

        Returns:
            ConflictResolution or None if escalated to manual
        """
        if not conflict.source_values:
            return None

        # Tier 1: Try hierarchy
        resolution = self.apply_hierarchy(conflict.source_values)

        if resolution:
            resolution.conflict_id = conflict.conflict_id
            resolution.resolved_at = datetime.utcnow()
            self.resolutions[conflict.conflict_id] = resolution
            self.tier1_resolved += 1
            return resolution

        # Tier 2: Try LENS synthesis
        resolution = self.query_lens_synthesis(conflict)

        if resolution:
            resolution.resolved_at = datetime.utcnow()
            self.resolutions[conflict.conflict_id] = resolution
            self.tier2_resolved += 1
            return resolution

        # Tier 3: Escalate to manual review
        self.escalate_to_manual_review(conflict, "LENS deferral or tie")
        return None

    def get_manual_review_queue(self) -> List[Dict[str, Any]]:
        """Get manual review queue.

        Returns:
            List of pending manual review tickets
        """
        pending = [t for t in self.manual_review_queue if t.status == ReviewStatus.PENDING]
        return [t.to_dict() for t in pending]

    def get_overdue_tickets(self) -> List[Dict[str, Any]]:
        """Get overdue manual review tickets.

        Returns:
            List of overdue tickets
        """
        overdue = [t for t in self.manual_review_queue if t.is_overdue]
        return [t.to_dict() for t in overdue]

    def resolve_manual_ticket(
        self,
        ticket_id: str,
        resolution_value: Any,
        assigned_to: str = "reviewer",
    ) -> bool:
        """Manually resolve a ticket.

        Args:
            ticket_id: Ticket ID
            resolution_value: Resolved value
            assigned_to: Reviewer who resolved it

        Returns:
            True if successful
        """
        for ticket in self.manual_review_queue:
            if ticket.ticket_id == ticket_id:
                ticket.status = ReviewStatus.RESOLVED
                ticket.resolution = str(resolution_value)
                ticket.assigned_to = assigned_to
                ticket.resolved_at = datetime.utcnow()
                return True

        return False

    def get_resolution_stats(self) -> Dict[str, Any]:
        """Get resolution statistics.

        Returns:
            Statistics dictionary
        """
        total_resolved = self.tier1_resolved + self.tier2_resolved
        total_escalated = self.tier3_escalated
        total = total_resolved + total_escalated

        return {
            "tier1_hierarchy_resolved": self.tier1_resolved,
            "tier2_lens_resolved": self.tier2_resolved,
            "tier3_manual_escalated": self.tier3_escalated,
            "total_conflicts": total,
            "resolution_rate_percent": (total_resolved / total * 100) if total > 0 else 0,
            "escalation_rate_percent": (total_escalated / total * 100) if total > 0 else 0,
        }

    def get_status(self) -> Dict[str, Any]:
        """Get overall status.

        Returns:
            Status dictionary
        """
        return {
            "resolution_stats": self.get_resolution_stats(),
            "pending_tickets": len(self.get_manual_review_queue()),
            "overdue_tickets": len(self.get_overdue_tickets()),
            "total_tickets": len(self.manual_review_queue),
        }

    def clear_all(self) -> None:
        """Clear all data (for testing)."""
        self.resolutions.clear()
        self.manual_review_queue.clear()
        self.tier1_resolved = 0
        self.tier2_resolved = 0
        self.tier3_escalated = 0
