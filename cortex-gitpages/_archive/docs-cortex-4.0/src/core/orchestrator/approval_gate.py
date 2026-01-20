"""Approval Gate Logic - Confidence-based approval matrix for operations."""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

from src.core.orchestrator.complexity_assessment import (
    ComplexityAssessment,
    ComplexityLevel,
    ComplexityAssessmentEngine,
)

@dataclass
class ConfirmationRequest:
    """Request for user confirmation before executing operation."""
    operation_id: str
    complexity_level: str
    complexity_score: float
    context: str
    reason: str
    suggested_action: str
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class AlternativeRecommendation:
    """Alternative approach recommendation."""
    name: str
    description: str
    complexity_score: float
    reason: str
    benefit: str

@dataclass
class ApprovalDecision:
    """Decision from approval gate."""
    operation_id: str
    approved: bool
    reason: str
    complexity_level: str
    complexity_score: float
    requires_confirmation: bool
    escalated: bool
    alternatives: List[AlternativeRecommendation] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)

class ApprovalGateLogic:
    """Implements confidence-based approval matrix."""
    
    # Approval thresholds
    THRESHOLDS = {
        'trivial': 0.15,          # Auto-approve (<=)
        'simple': 0.35,           # Auto-approve (<=)
        'moderate': 0.60,         # Confirmation needed (<=)
        'complex': 0.85,          # Escalation with alternatives (<=)
        'critical': float('inf'), # Executive summary + escalation (>)
    }
    
    def __init__(self):
        """Initialize approval gate logic."""
        self.decision_history: List[ApprovalDecision] = []
        self.enforcement_mode = 'STRICT'  # No overrides
    
    def evaluate_approval(
        self,
        assessment: ComplexityAssessment,
        operation_id: str,
        context: Optional[Dict[str, Any]] = None,
        alternatives: Optional[List[Dict[str, Any]]] = None,
    ) -> ApprovalDecision:
        """
        Evaluate whether operation should be auto-approved or escalated.
        
        Args:
            assessment: ComplexityAssessment from assessment engine
            operation_id: Unique operation identifier
            context: Additional context (e.g., user intent, changed files)
            alternatives: List of alternative approaches
        
        Returns:
            ApprovalDecision with approval status and reasoning
        """
        score = assessment.complexity_score
        level = assessment.complexity_level
        
        # Determine approval action
        if score <= self.THRESHOLDS['trivial']:
            # TRIVIAL: Auto-approve, no interaction
            decision = ApprovalDecision(
                operation_id=operation_id,
                approved=True,
                reason="Trivial operation - auto-approved",
                complexity_level=level,
                complexity_score=score,
                requires_confirmation=False,
                escalated=False,
                alternatives=[],
            )
        
        elif score <= self.THRESHOLDS['simple']:
            # SIMPLE: Auto-approve with summary
            decision = ApprovalDecision(
                operation_id=operation_id,
                approved=True,
                reason="Simple operation - auto-approved with summary confirmation",
                complexity_level=level,
                complexity_score=score,
                requires_confirmation=True,  # Show summary
                escalated=False,
                alternatives=[],
            )
        
        elif score <= self.THRESHOLDS['moderate']:
            # MODERATE: Request confirmation
            decision = ApprovalDecision(
                operation_id=operation_id,
                approved=False,
                reason="Moderate complexity - user confirmation requested",
                complexity_level=level,
                complexity_score=score,
                requires_confirmation=True,
                escalated=False,
                alternatives=[],
            )
        
        elif score <= self.THRESHOLDS['complex']:
            # COMPLEX: Escalation with alternatives
            alt_recommendations = self._generate_alternatives(alternatives) if alternatives else []
            decision = ApprovalDecision(
                operation_id=operation_id,
                approved=False,
                reason="Complex operation - escalation with alternatives",
                complexity_level=level,
                complexity_score=score,
                requires_confirmation=True,
                escalated=True,
                alternatives=alt_recommendations,
            )
        
        else:
            # CRITICAL: Executive summary + escalation
            alt_recommendations = self._generate_alternatives(alternatives, top_k=3) if alternatives else []
            decision = ApprovalDecision(
                operation_id=operation_id,
                approved=False,
                reason="Critical complexity - executive summary escalation",
                complexity_level=level,
                complexity_score=score,
                requires_confirmation=True,
                escalated=True,
                alternatives=alt_recommendations,
            )
        
        # Record decision in history
        self.decision_history.append(decision)
        
        return decision
    
    @staticmethod
    def _generate_alternatives(
        alternatives: Optional[List[Dict[str, Any]]],
        top_k: int = 3
    ) -> List[AlternativeRecommendation]:
        """Generate alternative recommendations from input."""
        if not alternatives:
            return []
        
        recommendations = []
        for alt in alternatives[:top_k]:
            recommendation = AlternativeRecommendation(
                name=alt.get('name', 'Alternative'),
                description=alt.get('description', ''),
                complexity_score=alt.get('complexity_score', 0.5),
                reason=alt.get('reason', 'Consider this approach'),
                benefit=alt.get('benefit', 'May reduce complexity'),
            )
            recommendations.append(recommendation)
        
        return recommendations
    
    def get_confirmation_request(
        self,
        decision: ApprovalDecision,
        context: str,
    ) -> Optional[ConfirmationRequest]:
        """
        Generate confirmation request if needed.
        
        Returns:
            ConfirmationRequest if decision requires confirmation, None otherwise
        """
        if not decision.requires_confirmation:
            return None
        
        # Determine suggested action based on complexity
        if decision.complexity_score <= self.THRESHOLDS['simple']:
            suggested_action = "Review summary and proceed"
        elif decision.complexity_score <= self.THRESHOLDS['moderate']:
            suggested_action = "Review impact and confirm"
        else:
            suggested_action = "Review escalation details and select approach"
        
        return ConfirmationRequest(
            operation_id=decision.operation_id,
            complexity_level=decision.complexity_level,
            complexity_score=decision.complexity_score,
            context=context,
            reason=decision.reason,
            suggested_action=suggested_action,
        )
    
    def check_threshold_crossing(
        self,
        previous_score: float,
        current_score: float,
    ) -> Dict[str, Any]:
        """
        Detect threshold boundary crossing.
        
        Args:
            previous_score: Previous complexity score
            current_score: Current complexity score
        
        Returns:
            Dict with crossing information
        """
        previous_level = self._get_level_for_score(previous_score)
        current_level = self._get_level_for_score(current_score)
        
        crossed = previous_level != current_level
        
        return {
            'crossed_boundary': crossed,
            'from_level': previous_level,
            'to_level': current_level,
            'score_change': current_score - previous_score,
            'approval_change': self._is_approved(current_score) != self._is_approved(previous_score),
        }
    
    def _get_level_for_score(self, score: float) -> str:
        """Get complexity level for a score."""
        if score <= 0.15:
            return ComplexityLevel.TRIVIAL.value
        elif score <= 0.35:
            return ComplexityLevel.SIMPLE.value
        elif score <= 0.60:
            return ComplexityLevel.MODERATE.value
        elif score <= 0.85:
            return ComplexityLevel.COMPLEX.value
        else:
            return ComplexityLevel.CRITICAL.value
    
    def _is_approved(self, score: float) -> bool:
        """Check if score auto-approves operation."""
        return score <= self.THRESHOLDS['simple']
    
    def ensure_consistency(
        self,
        decision: ApprovalDecision,
    ) -> bool:
        """
        Ensure approval decision is consistent.
        
        Validates:
        - TRIVIAL/SIMPLE with score <= threshold: must be auto-approved
        - MODERATE-CRITICAL with score > simple threshold: must require confirmation
        - Escalation only for COMPLEX/CRITICAL
        """
        score = decision.complexity_score
        level = decision.complexity_level
        
        # Check consistency
        if score <= 0.35:  # TRIVIAL or SIMPLE
            return decision.approved is True
        elif score <= 0.60:  # MODERATE
            return decision.requires_confirmation is True and decision.escalated is False
        else:  # COMPLEX or CRITICAL
            return decision.requires_confirmation is True and decision.escalated is True
    
    def handle_missing_signals(
        self,
        partial_assessment: ComplexityAssessment,
    ) -> ApprovalDecision:
        """
        Handle case where some signals are missing.
        
        Fallback strategy: Default to requiring confirmation if uncertain.
        """
        # Lower confidence = require confirmation as fallback
        if partial_assessment.confidence < 0.7:
            # Conservative: escalate to confirmation
            return ApprovalDecision(
                operation_id="unknown",
                approved=False,
                reason="Missing signals - insufficient confidence for auto-approval",
                complexity_level=partial_assessment.complexity_level,
                complexity_score=partial_assessment.complexity_score,
                requires_confirmation=True,
                escalated=False,
            )
        
        # Otherwise, use normal evaluation
        return ApprovalDecision(
            operation_id="unknown",
            approved=partial_assessment.complexity_score <= 0.35,
            reason="Evaluated with available signals",
            complexity_level=partial_assessment.complexity_level,
            complexity_score=partial_assessment.complexity_score,
            requires_confirmation=partial_assessment.complexity_score > 0.15,
            escalated=partial_assessment.complexity_score > 0.60,
        )
    
    def get_decision_history(self, limit: int = 10) -> List[ApprovalDecision]:
        """Get recent decisions."""
        return self.decision_history[-limit:]
    
    def get_approval_statistics(self) -> Dict[str, Any]:
        """Get statistics on approval decisions."""
        if not self.decision_history:
            return {
                'total_decisions': 0,
                'approved': 0,
                'rejected': 0,
                'escalated': 0,
                'approval_rate': 0.0,
            }
        
        total = len(self.decision_history)
        approved = sum(1 for d in self.decision_history if d.approved)
        escalated = sum(1 for d in self.decision_history if d.escalated)
        
        # Group by complexity level
        level_counts = {}
        for decision in self.decision_history:
            level = decision.complexity_level
            level_counts[level] = level_counts.get(level, 0) + 1
        
        return {
            'total_decisions': total,
            'approved': approved,
            'rejected': total - approved,
            'escalated': escalated,
            'approval_rate': approved / total if total > 0 else 0.0,
            'by_complexity_level': level_counts,
        }
