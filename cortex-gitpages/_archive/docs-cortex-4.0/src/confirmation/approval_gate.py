"""
Confidence-Based Approval Gate Logic - Production Implementation.

Makes approval decisions based on confidence thresholds and routes review
requests to appropriate teams.
"""

from typing import Dict, List
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime


class ApprovalDecision(Enum):
    """Approval decision types."""
    AUTO_APPROVED = "auto_approved"      # Automatically approved
    REVIEW_REQUIRED = "review_required"  # Requires human review
    REJECTED = "rejected"                # Rejected due to risk


class ReviewRoutingTeam(Enum):
    """Teams that can handle review requests."""
    SECURITY = "security"
    ARCHITECTURE = "architecture"
    PERFORMANCE = "performance"
    COMPLIANCE = "compliance"
    GENERAL = "general"


@dataclass
class ApprovalMatrix:
    """Confidence-based approval matrix for decision routing."""
    
    high_confidence_threshold: float    # > this value = auto-approve (0-1)
    review_threshold: float              # > this value = requires review; < this = reject
    auto_approval_teams: List[str]       # Teams allowed for auto-approval
    review_routing: Dict[str, List[str]]  # Route types to team
    
    def validate(self) -> bool:
        """Validate matrix configuration."""
        if not (0 < self.high_confidence_threshold <= 1):
            return False
        if not (0 < self.review_threshold <= 1):
            return False
        if self.high_confidence_threshold <= self.review_threshold:
            return False
        return True


@dataclass
class OperationContext:
    """Context for an operation requiring approval."""
    
    operation_id: str
    operation_type: str              # "deploy", "scale", "update", etc.
    complexity_level: str            # "trivial", "simple", "moderate", "complex", "critical"
    requestor_id: str
    requestor_team: str
    affected_services: List[str]
    estimated_impact: str            # "low", "medium", "high", "critical"


@dataclass
class ApprovalRequest:
    """Request for approval with confidence metrics."""
    
    operation_context: OperationContext
    confidence_score: float          # 0-1 (from complexity engine)
    lens_confidence: float           # 0-1 (quality of analysis)
    risk_score: float                # 0-1 (estimated risk)
    timestamp: datetime


@dataclass
class ApprovalResult:
    """Result of approval decision."""
    
    request_id: str
    decision: ApprovalDecision
    confidence: float
    reasoning: str
    assigned_team: ReviewRoutingTeam = None
    estimated_review_time: int = None  # in minutes
    timestamp: datetime = None


class ConfidenceBasedGateLady:
    """
    Confidence-Based Approval Gate Logic.
    
    Makes approval decisions based on confidence thresholds and routes
    review requests to appropriate teams.
    """
    
    def __init__(self, approval_matrix: ApprovalMatrix):
        """
        Initialize gate with approval matrix.
        
        Args:
            approval_matrix: Configuration for approval decisions
        
        Raises:
            ValueError: If approval matrix is invalid
        """
        if not approval_matrix.validate():
            raise ValueError("Invalid approval matrix configuration")
        
        self.matrix = approval_matrix
        self.decision_log: List[ApprovalResult] = []
        self.review_queue: List[ApprovalRequest] = []
    
    def evaluate(self, request: ApprovalRequest) -> ApprovalResult:
        """
        Evaluate approval request based on confidence thresholds.
        
        Args:
            request: Approval request with confidence metrics
        
        Returns:
            ApprovalResult with decision and routing
        """
        # Calculate effective confidence
        effective_confidence = self._calculate_effective_confidence(request)
        
        # Make decision based on thresholds
        if effective_confidence >= self.matrix.high_confidence_threshold:
            decision = ApprovalDecision.AUTO_APPROVED
            reasoning = f"High confidence ({effective_confidence:.2%}) - automatic approval"
            assigned_team = None
            estimated_time = None
        
        elif effective_confidence >= self.matrix.review_threshold:
            decision = ApprovalDecision.REVIEW_REQUIRED
            reasoning = f"Medium confidence ({effective_confidence:.2%}) - review required"
            assigned_team = self._route_to_team(request)
            estimated_time = self._estimate_review_time(request)
            self.review_queue.append(request)
        
        else:
            decision = ApprovalDecision.REJECTED
            reasoning = f"Low confidence ({effective_confidence:.2%}) - rejected"
            assigned_team = None
            estimated_time = None
        
        result = ApprovalResult(
            request_id=f"APPREQ-{len(self.decision_log)+1:06d}",
            decision=decision,
            confidence=effective_confidence,
            reasoning=reasoning,
            assigned_team=assigned_team,
            estimated_review_time=estimated_time,
            timestamp=datetime.now()
        )
        
        self.decision_log.append(result)
        return result
    
    def _calculate_effective_confidence(self, request: ApprovalRequest) -> float:
        """
        Calculate effective confidence from multiple signals.
        
        Factors:
        - Confidence score (60%): Direct confidence from complexity engine
        - LENS confidence (30%): Quality of analysis
        - Risk inverse (10%): Lower risk increases confidence
        """
        return (
            (request.confidence_score * 0.6) +
            (request.lens_confidence * 0.3) +
            ((1.0 - request.risk_score) * 0.1)
        )
    
    def _route_to_team(self, request: ApprovalRequest) -> ReviewRoutingTeam:
        """
        Route review request to appropriate team based on operation type.
        """
        routing_map = {
            "deploy": ReviewRoutingTeam.ARCHITECTURE,
            "scale": ReviewRoutingTeam.PERFORMANCE,
            "update": ReviewRoutingTeam.SECURITY,
            "security": ReviewRoutingTeam.SECURITY,
            "compliance": ReviewRoutingTeam.COMPLIANCE,
        }
        
        team_name = routing_map.get(
            request.operation_context.operation_type,
            ReviewRoutingTeam.GENERAL
        )
        
        return team_name
    
    def _estimate_review_time(self, request: ApprovalRequest) -> int:
        """Estimate review time based on complexity."""
        complexity_time = {
            "trivial": 5,
            "simple": 15,
            "moderate": 30,
            "complex": 60,
            "critical": 120,
        }
        return complexity_time.get(
            request.operation_context.complexity_level,
            30
        )
    
    def get_decision_statistics(self) -> Dict:
        """
        Get statistics on all decisions.
        
        Returns: Dictionary with decision counts and metrics
        """
        if not self.decision_log:
            return {}
        
        auto_count = sum(1 for r in self.decision_log if r.decision == ApprovalDecision.AUTO_APPROVED)
        review_count = sum(1 for r in self.decision_log if r.decision == ApprovalDecision.REVIEW_REQUIRED)
        rejected_count = sum(1 for r in self.decision_log if r.decision == ApprovalDecision.REJECTED)
        
        return {
            'total_decisions': len(self.decision_log),
            'auto_approved': auto_count,
            'review_required': review_count,
            'rejected': rejected_count,
            'average_confidence': sum(r.confidence for r in self.decision_log) / len(self.decision_log),
            'review_queue_size': len(self.review_queue),
        }
    
    def approve_review(self, request_id: str, approved: bool, reviewer_id: str) -> Dict:
        """
        Handle review approval/rejection.
        
        Args:
            request_id: ID of review request
            approved: Whether reviewer approved
            reviewer_id: ID of reviewer
        
        Returns: Updated approval result with decision and reviewer info
        
        Raises:
            ValueError: If request_id not found
        """
        for result in self.decision_log:
            if result.request_id == request_id:
                if approved:
                    result.decision = ApprovalDecision.AUTO_APPROVED
                    result.reasoning = f"Approved by reviewer {reviewer_id} after review"
                else:
                    result.decision = ApprovalDecision.REJECTED
                    result.reasoning = f"Rejected by reviewer {reviewer_id} after review"
                return {
                    'request_id': request_id,
                    'decision': result.decision.value,
                    'reviewer_id': reviewer_id,
                    'timestamp': datetime.now()
                }
        
        raise ValueError(f"Request {request_id} not found")
    
    def get_review_queue(self) -> List[ApprovalRequest]:
        """Get current review queue."""
        return self.review_queue.copy()
    
    def clear_history(self) -> None:
        """Clear all decision history."""
        self.decision_log = []
        self.review_queue = []
