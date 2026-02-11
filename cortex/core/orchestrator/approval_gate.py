"""Approval Gate

STUB IMPLEMENTATION - To be completed in Phase E.

Author: CORTEX Framework
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class AlternativeRecommendation:
    """Alternative recommendation for approval."""
    alternative_id: str
    description: str
    rationale: str
    complexity_score: Optional[float] = None


@dataclass
class ApprovalDecision:
    """Approval decision."""
    approved: bool
    reason: str
    approver: str = ""
    requires_confirmation: bool = False
    escalated: bool = False
    confirmation_request: Optional['ConfirmationRequest'] = None
    alternatives: List[AlternativeRecommendation] = field(default_factory=list)


@dataclass
class ApprovalGateLogic:
    """Approval gate logic."""
    gate_id: str
    conditions: list = field(default_factory=list)
    decision_history: Dict[str, ApprovalDecision] = field(default_factory=dict)

    def evaluate(self) -> bool:
        """Evaluate approval gate."""
        return True

    def evaluate_approval(self, assessment: Any, operation_id: str, alternatives: Optional[List] = None) -> ApprovalDecision:
        """Evaluate approval based on complexity assessment.

        Args:
            assessment: Complexity assessment object with complexity_level
            operation_id: Operation ID for tracking
            alternatives: Optional list of alternative recommendations

        Returns:
            ApprovalDecision with approval status and requirements
        """
        alternatives = alternatives or []
        complexity_level = getattr(assessment, 'complexity_level', 'unknown')

        # Convert alternative dict list to AlternativeRecommendation objects
        alt_recommendations = []
        for alt in alternatives:
            if isinstance(alt, dict):
                alt_recommendations.append(AlternativeRecommendation(
                    alternative_id=alt.get('name', ''),
                    description=alt.get('description', ''),
                    rationale=f"Lower complexity score: {alt.get('complexity_score', 'N/A')}",
                    complexity_score=alt.get('complexity_score')
                ))
            else:
                alt_recommendations.append(alt)

        if complexity_level == 'trivial':
            decision = ApprovalDecision(
                approved=True,
                reason="Auto-approved: trivial operation",
                requires_confirmation=False,
                escalated=False
            )
        elif complexity_level == 'simple':
            decision = ApprovalDecision(
                approved=True,
                reason="Auto-approved: simple operation",
                requires_confirmation=False,
                escalated=False
            )
        elif complexity_level == 'moderate':
            decision = ApprovalDecision(
                approved=False,
                reason="Confirmation required: moderate complexity",
                requires_confirmation=True,
                escalated=False,
                confirmation_request=ConfirmationRequest(
                    request_id=f"confirm-{operation_id}",
                    message=f"Operation {operation_id} requires confirmation due to moderate complexity",
                    operation_id=operation_id,
                    complexity_level=complexity_level
                )
            )
        elif complexity_level in ('complex', 'critical'):
            # Use provided alternatives or create default ones
            if alt_recommendations:
                # Select top 3 by lowest complexity_score
                alt_recommendations.sort(key=lambda x: float(x.rationale.split(': ')[1]) if ': ' in x.rationale else float('inf'))
                alt_recommendations = alt_recommendations[:3]
            else:
                alt_recommendations = [
                    AlternativeRecommendation(
                        alternative_id=f"alt-{i+1}",
                        description=f"Alternative approach {i+1}",
                        rationale="Review alternative implementation"
                    )
                    for i in range(3)
                ]
            decision = ApprovalDecision(
                approved=False,
                reason="Escalation required: high complexity operation",
                requires_confirmation=True,
                escalated=True,
                confirmation_request=ConfirmationRequest(
                    request_id=f"escalate-{operation_id}",
                    message=f"Operation {operation_id} escalated for executive approval",
                    operation_id=operation_id,
                    complexity_level=complexity_level,
                    suggested_action="Review escalation details and select approach"
                ),
                alternatives=alt_recommendations
            )
        else:
            decision = ApprovalDecision(
                approved=True,
                reason="Default approval for unclassified operation",
                requires_confirmation=False,
                escalated=False
            )

        # Store in history
        self.decision_history[operation_id] = decision
        return decision

    def check_threshold_crossing(self, prev_complexity: float, curr_complexity: float) -> Dict[str, Any]:
        """Check if complexity crosses a threshold boundary.

        Args:
            prev_complexity: Previous complexity score (0-1)
            curr_complexity: Current complexity score (0-1)

        Returns:
            Dictionary with crossing information
        """
        def get_level(score):
            if score <= 0.2:
                return 'TRIVIAL'
            elif score <= 0.35:
                return 'SIMPLE'
            elif score < 0.65:
                return 'MODERATE'
            elif score < 0.85:
                return 'COMPLEX'
            else:
                return 'CRITICAL'

        from_level = get_level(prev_complexity)
        to_level = get_level(curr_complexity)
        crossed = from_level != to_level

        return {
            'crossed_boundary': crossed,
            'from_level': from_level,
            'to_level': to_level,
            'prev_complexity': prev_complexity,
            'curr_complexity': curr_complexity
        }

    def ensure_consistency(self, decision: ApprovalDecision) -> bool:
        """Ensure approval decision is consistent with complexity level.

        Args:
            decision: Approval decision to validate

        Returns:
            True if decision is consistent, False otherwise
        """
        # A decision is consistent if it follows expected patterns
        # - Trivial/Simple: should be approved and not require confirmation
        # - Moderate: should require confirmation
        # - Complex/Critical: should be escalated and require confirmation

        if "trivial" in decision.reason.lower() or "simple" in decision.reason.lower():
            return decision.approved and not decision.requires_confirmation
        elif "moderate" in decision.reason.lower():
            return decision.requires_confirmation
        elif "escalat" in decision.reason.lower() or "complex" in decision.reason.lower():
            return decision.escalated and decision.requires_confirmation

        return True  # Default to consistent for unclassified

    def handle_missing_signals(self, assessment: Any) -> ApprovalDecision:
        """Handle approval when confidence in signals is low.

        Args:
            assessment: Assessment with low confidence signals

        Returns:
            Conservative ApprovalDecision requiring confirmation
        """
        # When confidence is low, default to conservative approach
        decision = ApprovalDecision(
            approved=False,
            reason="Confirmation required: low confidence in complexity assessment",
            requires_confirmation=True,
            escalated=False,
            confirmation_request=ConfirmationRequest(
                request_id="confirm-low-confidence",
                message="Operation assessment has low confidence - manual confirmation recommended"
            )
        )
        return decision

    def get_confirmation_request(self, decision: ApprovalDecision, description: str, operation_id: Optional[str] = None, complexity_level: Optional[str] = None) -> Optional['ConfirmationRequest']:
        """Get confirmation request if needed.

        Args:
            decision: Approval decision
            description: Operation description for context
            operation_id: Operation ID (optional, for enrichment)
            complexity_level: Complexity level (optional, for enrichment)

        Returns:
            ConfirmationRequest if confirmation needed, None otherwise
        """
        if not decision.requires_confirmation:
            return None

        if decision.confirmation_request:
            # Enrich the existing confirmation request if provided
            if operation_id:
                decision.confirmation_request.operation_id = operation_id
            if complexity_level:
                decision.confirmation_request.complexity_level = complexity_level
            return decision.confirmation_request

        # Create a generic confirmation request
        return ConfirmationRequest(
            request_id="generic-confirmation",
            message=f"Please confirm: {description}",
            options=["approve", "reject", "escalate"],
            operation_id=operation_id,
            complexity_level=complexity_level
        )

    def get_decision_history(self, limit: Optional[int] = None) -> Dict[str, ApprovalDecision]:
        """Get decision history.

        Args:
            limit: Maximum number of decisions to return (most recent first)

        Returns:
            Dictionary of operation_id -> ApprovalDecision
        """
        history = self.decision_history

        if limit:
            # Return the most recent 'limit' items
            items = list(history.items())
            return dict(items[-limit:])

        return history

    def get_approval_statistics(self) -> Dict[str, Any]:
        """Get approval statistics from decision history.

        Returns:
            Dictionary with approval statistics
        """
        if not self.decision_history:
            return {
                'total_decisions': 0,
                'approved_count': 0,
                'rejected_count': 0,
                'escalated_count': 0,
                'approval_rate': 0.0,
                'escalation_rate': 0.0,
                'by_complexity_level': {}
            }

        total = len(self.decision_history)
        approved = sum(1 for d in self.decision_history.values() if d.approved)
        rejected = total - approved
        escalated = sum(1 for d in self.decision_history.values() if d.escalated)

        # Count by complexity level from confirmation requests
        by_complexity = {}
        for decision in self.decision_history.values():
            if decision.confirmation_request and decision.confirmation_request.complexity_level:
                level = decision.confirmation_request.complexity_level
                if level not in by_complexity:
                    by_complexity[level] = {'count': 0, 'approved': 0}
                by_complexity[level]['count'] += 1
                if decision.approved:
                    by_complexity[level]['approved'] += 1

        return {
            'total_decisions': total,
            'approved_count': approved,
            'rejected_count': rejected,
            'escalated_count': escalated,
            'approval_rate': approved / total if total > 0 else 0.0,
            'escalation_rate': escalated / total if total > 0 else 0.0,
            'by_complexity_level': by_complexity
        }


@dataclass
class ConfirmationRequest:
    """Confirmation request for approval."""
    request_id: str
    message: str
    options: List[str] = field(default_factory=lambda: ["approve", "reject"])
    operation_id: Optional[str] = None
    complexity_level: Optional[str] = None
    suggested_action: Optional[str] = None


__all__ = ["AlternativeRecommendation", "ApprovalDecision", "ApprovalGateLogic", "ConfirmationRequest"]
