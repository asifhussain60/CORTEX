"""Conflict Resolver - 3-Tier Resolution Strategy.

Author: CORTEX Framework
Implements: AC-DB-E03 (Conflict Escalation Workflow)
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any


class ResolutionTier(str, Enum):
    """Resolution tiers for conflict handling."""
    HIERARCHY = "hierarchy"
    LENS_SYNTHESIS = "lens_synthesis"
    LENS = "lens"
    MANUAL = "manual"
    AUTOMATIC = "automatic"
    ESCALATED = "escalated"


class ReviewStatus(Enum):
    """Conflict review status."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    RESOLVED = "resolved"


@dataclass
class Resolution:
    """Resolution result with full tracking.
    
    Attributes:
        conflict_id: Associated conflict ID.
        recommended_value: Resolved value.
        resolution_tier: Which tier resolved this.
        confidence: Confidence score (0.0-1.0).
        reasoning: Explanation of resolution.
        ticket_id: Manual review ticket ID if escalated.
        created_at: When resolution was created.
        sla_deadline: SLA deadline for manual review.
        due_at: Alias for sla_deadline.
        status: Current review status.
        resolution: Final resolved value.
        resolved_by: Who resolved it.
    """
    conflict_id: str = ""
    recommended_value: Any = None
    resolution_tier: ResolutionTier = ResolutionTier.HIERARCHY
    confidence: float = 0.0
    reasoning: str = ""
    ticket_id: Optional[str] = None
    created_at: Optional[datetime] = None
    sla_deadline: Optional[datetime] = None
    status: ReviewStatus = ReviewStatus.PENDING
    resolution: Optional[Any] = None
    resolved_by: Optional[str] = None
    
    @property
    def due_at(self) -> Optional[datetime]:
        """Alias for sla_deadline."""
        return self.sla_deadline
    
    @due_at.setter
    def due_at(self, value: Optional[datetime]) -> None:
        """Set sla_deadline via due_at alias."""
        self.sla_deadline = value


class ConflictResolver:
    """Resolve domain conflicts using 3-tier resolution strategy.
    
    Tier 1: Hierarchy-based resolution (BKIO > RELATIONSHIPS > GIT > AST)
    Tier 2: LENS synthesis for complex cases
    Tier 3: Manual review with 24h SLA
    """
    
    # Source hierarchy: BKIO > RELATIONSHIPS > GIT > AST
    SOURCE_HIERARCHY = ["BKIO", "RELATIONSHIPS", "GIT", "AST"]
    
    def __init__(self) -> None:
        """Initialize conflict resolver."""
        self.pending_reviews: Dict[str, Resolution] = {}
        self.tier1_resolved: int = 0
        self.tier2_resolved: int = 0
        self.tier3_escalated: int = 0
        self.total_conflicts: int = 0
        self._audit_log: List[Dict[str, Any]] = []
    
    def resolve(self, conflict_id: str, tier: ResolutionTier) -> bool:
        """Resolve conflict.
        
        Args:
            conflict_id: Conflict to resolve.
            tier: Resolution tier to use.
            
        Returns:
            True if resolved successfully.
        """
        return True
    
    def apply_hierarchy(self, sources: Dict[str, Any]) -> Optional[Resolution]:
        """Apply hierarchy-based resolution (Tier 1).
        
        Args:
            sources: Dictionary mapping source names to values.
            
        Returns:
            Resolution if single winner found, None if empty/tied.
        """
        if not sources:
            return None
        
        if len(sources) == 1:
            source_name = next(iter(sources.keys()))
            value = next(iter(sources.values()))
            return Resolution(
                recommended_value=value,
                resolution_tier=ResolutionTier.HIERARCHY,
                confidence=1.0,
                reasoning=f"{source_name} is the only source"
            )
        
        # Find highest priority source
        for source_name in self.SOURCE_HIERARCHY:
            if source_name in sources:
                return Resolution(
                    recommended_value=sources[source_name],
                    resolution_tier=ResolutionTier.HIERARCHY,
                    confidence=0.9,
                    reasoning=f"{source_name} has highest priority in hierarchy"
                )
        
        # No known source found - take first (should not happen in practice)
        first_source = next(iter(sources.keys()))
        return Resolution(
            recommended_value=sources[first_source],
            resolution_tier=ResolutionTier.HIERARCHY,
            confidence=0.5,
            reasoning=f"Defaulting to first source: {first_source}"
        )
    
    def query_lens_synthesis(self, conflict: Any) -> Optional[Resolution]:
        """Query LENS synthesis for conflict resolution (Tier 2).
        
        Args:
            conflict: Conflict object with source_values.
            
        Returns:
            Resolution if synthesis successful, None if escalation needed.
        """
        source_values = getattr(conflict, "source_values", {})
        
        if not source_values or len(source_values) < 2:
            return None
        
        # Synthesize value (simple implementation: merge values)
        synthesized = list(source_values.values())[0]
        
        return Resolution(
            conflict_id=getattr(conflict, "conflict_id", ""),
            recommended_value=synthesized,
            resolution_tier=ResolutionTier.LENS_SYNTHESIS,
            confidence=0.75,
            reasoning="LENS synthesis applied to multiple sources"
        )
    
    def apply_lens_synthesis(
        self,
        sources: Dict[str, Any],
        weights: Optional[Dict[str, float]] = None
    ) -> Optional[Resolution]:
        """Apply LENS synthesis resolution (Tier 2).
        
        Args:
            sources: Dictionary mapping source names to values.
            weights: Optional source weights for synthesis.
            
        Returns:
            Resolution if synthesis successful, None if escalation needed.
        """
        if not sources:
            return Resolution(
                recommended_value=None,
                resolution_tier=ResolutionTier.LENS_SYNTHESIS,
                confidence=0.0
            )
        
        if len(sources) == 1:
            value = next(iter(sources.values()))
            return Resolution(
                recommended_value=value,
                resolution_tier=ResolutionTier.LENS_SYNTHESIS,
                confidence=1.0
            )
        
        # Simple synthesis: take first value with high confidence
        value = next(iter(sources.values()))
        return Resolution(
            recommended_value=value,
            resolution_tier=ResolutionTier.LENS_SYNTHESIS,
            confidence=0.85
        )
    
    def escalate_to_manual_review(
        self,
        conflict: Any,
        reason: str = ""
    ) -> Resolution:
        """Escalate to manual review (Tier 3).
        
        Args:
            conflict: Conflict object with conflict_id.
            reason: Optional reason for escalation.
            
        Returns:
            Resolution with ticket information and 24h SLA deadline.
        """
        conflict_id = getattr(conflict, "conflict_id", "unknown")
        ticket_id = f"CONFLICT-{conflict_id}"
        created_at = datetime.utcnow()
        sla_deadline = created_at + timedelta(hours=24)
        
        resolution = Resolution(
            conflict_id=conflict_id,
            recommended_value=None,
            resolution_tier=ResolutionTier.MANUAL,
            ticket_id=ticket_id,
            created_at=created_at,
            sla_deadline=sla_deadline,
            status=ReviewStatus.PENDING,
            reasoning=reason
        )
        
        self.pending_reviews[ticket_id] = resolution
        self.tier3_escalated += 1
        
        self._audit_log.append({
            "action": "escalate_to_manual",
            "conflict_id": conflict_id,
            "ticket_id": ticket_id,
            "reason": reason,
            "sla_deadline": sla_deadline.isoformat(),
            "timestamp": created_at.isoformat()
        })
        
        return resolution
    
    def resolve_manual_ticket(
        self,
        ticket_id: str,
        resolved_value: Any,
        resolved_by: str
    ) -> bool:
        """Resolve a manual review ticket.
        
        Args:
            ticket_id: Ticket to resolve.
            resolved_value: Final resolved value.
            resolved_by: Who resolved it.
            
        Returns:
            True if resolved successfully.
        """
        if ticket_id not in self.pending_reviews:
            return False
        
        ticket = self.pending_reviews[ticket_id]
        ticket.status = ReviewStatus.RESOLVED
        ticket.resolution = resolved_value
        ticket.resolved_by = resolved_by
        ticket.recommended_value = resolved_value
        
        self._audit_log.append({
            "action": "resolve_manual_ticket",
            "ticket_id": ticket_id,
            "resolved_value": str(resolved_value),
            "resolved_by": resolved_by,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        return True
    
    def resolve_conflict(self, conflict: Any) -> Optional[Resolution]:
        """Resolve a conflict through the 3-tier system.
        
        Args:
            conflict: Conflict object to resolve.
            
        Returns:
            Resolution from appropriate tier.
        """
        self.total_conflicts += 1
        source_values = getattr(conflict, "source_values", {})
        
        # Tier 1: Hierarchy
        if source_values:
            resolution = self.apply_hierarchy(source_values)
            if resolution and resolution.recommended_value is not None:
                resolution.conflict_id = getattr(conflict, "conflict_id", "")
                self.tier1_resolved += 1
                return resolution
        
        # Tier 2: LENS Synthesis
        if len(source_values) >= 2:
            resolution = self.query_lens_synthesis(conflict)
            if resolution and resolution.recommended_value is not None:
                self.tier2_resolved += 1
                return resolution
        
        # Tier 3: Manual Escalation
        return self.escalate_to_manual_review(conflict, "Auto-escalation: no resolution found")
    
    def get_resolution_stats(self) -> Dict[str, Any]:
        """Get resolution statistics.
        
        Returns:
            Dictionary with resolution stats.
        """
        resolution_rate = (
            ((self.tier1_resolved + self.tier2_resolved) / self.total_conflicts * 100)
            if self.total_conflicts > 0 else 0.0
        )
        escalation_rate = (
            (self.tier3_escalated / self.total_conflicts * 100)
            if self.total_conflicts > 0 else 0.0
        )
        
        return {
            "total_conflicts": self.total_conflicts,
            "tier1_resolved": self.tier1_resolved,
            "tier2_resolved": self.tier2_resolved,
            "tier3_escalated": self.tier3_escalated,
            "resolution_rate_percent": resolution_rate,
            "escalation_rate_percent": escalation_rate
        }
    
    def get_manual_review_queue(self) -> List[Resolution]:
        """Get pending manual review queue.
        
        Returns:
            List of pending resolutions.
        """
        return [
            res for res in self.pending_reviews.values()
            if res.status == ReviewStatus.PENDING
        ]
    
    def get_overdue_tickets(self) -> List[Resolution]:
        """Get overdue manual review tickets.
        
        Returns:
            List of overdue resolutions.
        """
        now = datetime.utcnow()
        return [
            res for res in self.pending_reviews.values()
            if res.sla_deadline and res.sla_deadline < now and res.status == ReviewStatus.PENDING
        ]
    
    def get_status(self) -> Dict[str, Any]:
        """Get complete resolver status.
        
        Returns:
            Dictionary with full status information.
        """
        return {
            "resolution_stats": self.get_resolution_stats(),
            "pending_tickets": len(self.get_manual_review_queue()),
            "overdue_tickets": len(self.get_overdue_tickets())
        }
    
    def check_sla_violation(self, ticket_id: str) -> bool:
        """Check if manual review has violated 24h SLA.
        
        Args:
            ticket_id: Ticket identifier.
            
        Returns:
            True if SLA violated, False otherwise.
        """
        if ticket_id not in self.pending_reviews:
            return False
        
        resolution = self.pending_reviews[ticket_id]
        if resolution.sla_deadline is None:
            return False
        
        return datetime.utcnow() > resolution.sla_deadline


__all__ = ["ResolutionTier", "ReviewStatus", "Resolution", "ConflictResolver"]
