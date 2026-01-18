"""
AC-CONF-002-01: Confidence-Based Approval Gate Logic - Unit & Integration Tests.

Requirements:
- Implement confidence-based approval matrix
- Support auto-approval for high-confidence operations
- Require review for uncertain operations
- Route decisions to appropriate teams
"""

import pytest
from datetime import datetime
from typing import Dict, List
from dataclasses import dataclass
from enum import Enum


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
        """Get statistics on all decisions."""
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
        
        Returns: Updated approval result
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


# ============================================================================
# Unit Tests
# ============================================================================

class TestApprovalMatrixValidation:
    """Test approval matrix validation."""
    
    def test_valid_matrix(self):
        """Valid matrix configuration."""
        matrix = ApprovalMatrix(
            high_confidence_threshold=0.9,
            review_threshold=0.7,
            auto_approval_teams=["general", "ci"],
            review_routing={"deploy": ["architecture"]}
        )
        assert matrix.validate() is True
    
    def test_invalid_threshold_range(self):
        """Invalid threshold (outside 0-1 range)."""
        matrix = ApprovalMatrix(
            high_confidence_threshold=1.5,
            review_threshold=0.7,
            auto_approval_teams=[],
            review_routing={}
        )
        assert matrix.validate() is False
    
    def test_reversed_thresholds(self):
        """High threshold less than review threshold."""
        matrix = ApprovalMatrix(
            high_confidence_threshold=0.5,
            review_threshold=0.8,
            auto_approval_teams=[],
            review_routing={}
        )
        assert matrix.validate() is False


class TestGateInitialization:
    """Test gate initialization."""
    
    def test_gate_creation_valid(self):
        """Create gate with valid matrix."""
        matrix = ApprovalMatrix(
            high_confidence_threshold=0.9,
            review_threshold=0.7,
            auto_approval_teams=["general"],
            review_routing={"deploy": ["architecture"]}
        )
        gate = ConfidenceBasedGateLady(matrix)
        assert gate.matrix == matrix
        assert len(gate.decision_log) == 0
    
    def test_gate_creation_invalid(self):
        """Gate creation with invalid matrix raises error."""
        matrix = ApprovalMatrix(
            high_confidence_threshold=0.5,
            review_threshold=0.8,
            auto_approval_teams=[],
            review_routing={}
        )
        with pytest.raises(ValueError):
            ConfidenceBasedGateLady(matrix)


class TestAutoApprovalDecision:
    """Test auto-approval decisions."""
    
    @pytest.fixture
    def gate(self):
        """Create gate instance."""
        matrix = ApprovalMatrix(
            high_confidence_threshold=0.85,
            review_threshold=0.65,
            auto_approval_teams=["general"],
            review_routing={"deploy": ["architecture"]}
        )
        return ConfidenceBasedGateLady(matrix)
    
    def test_high_confidence_auto_approve(self, gate):
        """High confidence triggers auto-approval."""
        context = OperationContext(
            operation_id="op-001",
            operation_type="deploy",
            complexity_level="simple",
            requestor_id="user-001",
            requestor_team="general",
            affected_services=["api"],
            estimated_impact="low"
        )
        request = ApprovalRequest(
            operation_context=context,
            confidence_score=0.95,
            lens_confidence=0.90,
            risk_score=0.05,
            timestamp=datetime.now()
        )
        
        result = gate.evaluate(request)
        assert result.decision == ApprovalDecision.AUTO_APPROVED
        assert result.confidence >= 0.85
    
    def test_perfect_confidence_auto_approve(self, gate):
        """Perfect confidence (1.0) triggers auto-approval."""
        context = OperationContext(
            operation_id="op-002",
            operation_type="deploy",
            complexity_level="trivial",
            requestor_id="user-002",
            requestor_team="general",
            affected_services=["internal"],
            estimated_impact="low"
        )
        request = ApprovalRequest(
            operation_context=context,
            confidence_score=1.0,
            lens_confidence=1.0,
            risk_score=0.0,
            timestamp=datetime.now()
        )
        
        result = gate.evaluate(request)
        assert result.decision == ApprovalDecision.AUTO_APPROVED
        assert abs(result.confidence - 1.0) < 0.001  # floating point tolerance


class TestReviewRequiredDecision:
    """Test review-required decisions."""
    
    @pytest.fixture
    def gate(self):
        """Create gate instance."""
        matrix = ApprovalMatrix(
            high_confidence_threshold=0.85,
            review_threshold=0.65,
            auto_approval_teams=["general"],
            review_routing={"deploy": ["architecture"], "security": ["security"]}
        )
        return ConfidenceBasedGateLady(matrix)
    
    def test_medium_confidence_review_required(self, gate):
        """Medium confidence requires review."""
        context = OperationContext(
            operation_id="op-003",
            operation_type="deploy",
            complexity_level="moderate",
            requestor_id="user-003",
            requestor_team="general",
            affected_services=["api", "database"],
            estimated_impact="medium"
        )
        request = ApprovalRequest(
            operation_context=context,
            confidence_score=0.75,
            lens_confidence=0.80,
            risk_score=0.20,
            timestamp=datetime.now()
        )
        
        result = gate.evaluate(request)
        assert result.decision == ApprovalDecision.REVIEW_REQUIRED
        assert result.assigned_team == ReviewRoutingTeam.ARCHITECTURE
        assert result.estimated_review_time is not None
    
    def test_review_routing_by_operation_type(self, gate):
        """Review routes to correct team based on operation type."""
        # Test security routing
        context = OperationContext(
            operation_id="op-004",
            operation_type="security",
            complexity_level="complex",
            requestor_id="user-004",
            requestor_team="general",
            affected_services=["auth", "api"],
            estimated_impact="high"
        )
        request = ApprovalRequest(
            operation_context=context,
            confidence_score=0.75,
            lens_confidence=0.78,
            risk_score=0.25,
            timestamp=datetime.now()
        )
        
        result = gate.evaluate(request)
        assert result.decision == ApprovalDecision.REVIEW_REQUIRED
        assert result.assigned_team == ReviewRoutingTeam.SECURITY


class TestRejectionDecision:
    """Test rejection decisions."""
    
    @pytest.fixture
    def gate(self):
        """Create gate instance."""
        matrix = ApprovalMatrix(
            high_confidence_threshold=0.85,
            review_threshold=0.65,
            auto_approval_teams=["general"],
            review_routing={}
        )
        return ConfidenceBasedGateLady(matrix)
    
    def test_low_confidence_rejection(self, gate):
        """Low confidence triggers rejection."""
        context = OperationContext(
            operation_id="op-005",
            operation_type="deploy",
            complexity_level="critical",
            requestor_id="user-005",
            requestor_team="general",
            affected_services=["core", "database", "cache"],
            estimated_impact="critical"
        )
        request = ApprovalRequest(
            operation_context=context,
            confidence_score=0.50,
            lens_confidence=0.45,
            risk_score=0.75,
            timestamp=datetime.now()
        )
        
        result = gate.evaluate(request)
        assert result.decision == ApprovalDecision.REJECTED
        assert result.assigned_team is None


class TestEffectiveConfidenceCalculation:
    """Test effective confidence calculation."""
    
    @pytest.fixture
    def gate(self):
        """Create gate instance."""
        matrix = ApprovalMatrix(
            high_confidence_threshold=0.85,
            review_threshold=0.65,
            auto_approval_teams=[],
            review_routing={}
        )
        return ConfidenceBasedGateLady(matrix)
    
    def test_confidence_weighting(self, gate):
        """Effective confidence uses correct weights."""
        context = OperationContext(
            operation_id="op-006",
            operation_type="deploy",
            complexity_level="moderate",
            requestor_id="user-006",
            requestor_team="general",
            affected_services=["api"],
            estimated_impact="medium"
        )
        
        # Test: 0.8 * 0.6 + 0.7 * 0.3 + 0.7 * 0.1 = 0.76
        request = ApprovalRequest(
            operation_context=context,
            confidence_score=0.8,
            lens_confidence=0.7,
            risk_score=0.3,  # inverse = 0.7
            timestamp=datetime.now()
        )
        
        result = gate.evaluate(request)
        assert abs(result.confidence - 0.76) < 0.01


class TestDecisionStatistics:
    """Test decision statistics tracking."""
    
    @pytest.fixture
    def gate_with_decisions(self):
        """Create gate with multiple decisions."""
        matrix = ApprovalMatrix(
            high_confidence_threshold=0.85,
            review_threshold=0.65,
            auto_approval_teams=["general"],
            review_routing={"deploy": ["architecture"]}
        )
        gate = ConfidenceBasedGateLady(matrix)
        
        # Add some decisions
        for i, (conf_score, lens_conf, risk) in enumerate([
            (0.95, 0.90, 0.05),  # auto-approve
            (0.75, 0.80, 0.20),  # review
            (0.50, 0.45, 0.75),  # reject
        ]):
            context = OperationContext(
                operation_id=f"op-{i:03d}",
                operation_type="deploy",
                complexity_level="simple",
                requestor_id=f"user-{i:03d}",
                requestor_team="general",
                affected_services=["api"],
                estimated_impact="low"
            )
            request = ApprovalRequest(
                operation_context=context,
                confidence_score=conf_score,
                lens_confidence=lens_conf,
                risk_score=risk,
                timestamp=datetime.now()
            )
            gate.evaluate(request)
        
        return gate
    
    def test_statistics_counts(self, gate_with_decisions):
        """Statistics report correct decision counts."""
        stats = gate_with_decisions.get_decision_statistics()
        assert stats['total_decisions'] == 3
        assert stats['auto_approved'] == 1
        assert stats['review_required'] == 1
        assert stats['rejected'] == 1


class TestReviewApproval:
    """Test review approval workflow."""
    
    @pytest.fixture
    def gate_with_review(self):
        """Create gate with review-required decision."""
        matrix = ApprovalMatrix(
            high_confidence_threshold=0.85,
            review_threshold=0.65,
            auto_approval_teams=["general"],
            review_routing={"deploy": ["architecture"]}
        )
        gate = ConfidenceBasedGateLady(matrix)
        
        context = OperationContext(
            operation_id="op-100",
            operation_type="deploy",
            complexity_level="moderate",
            requestor_id="user-100",
            requestor_team="general",
            affected_services=["api", "database"],
            estimated_impact="medium"
        )
        request = ApprovalRequest(
            operation_context=context,
            confidence_score=0.75,
            lens_confidence=0.80,
            risk_score=0.20,
            timestamp=datetime.now()
        )
        
        result = gate.evaluate(request)
        gate.current_review_id = result.request_id
        return gate
    
    def test_review_approval(self, gate_with_review):
        """Reviewer can approve decision."""
        gate = gate_with_review
        updated = gate.approve_review(
            gate.current_review_id,
            approved=True,
            reviewer_id="reviewer-001"
        )
        
        assert updated['decision'] == "auto_approved"
        assert updated['reviewer_id'] == "reviewer-001"
    
    def test_review_rejection(self, gate_with_review):
        """Reviewer can reject decision."""
        gate = gate_with_review
        updated = gate.approve_review(
            gate.current_review_id,
            approved=False,
            reviewer_id="reviewer-002"
        )
        
        assert updated['decision'] == "rejected"
        assert updated['reviewer_id'] == "reviewer-002"


# ============================================================================
# Integration Tests
# ============================================================================

class TestEndToEndApprovalFlow:
    """Test complete approval workflow."""
    
    def test_full_auto_approval_workflow(self):
        """Complete workflow for auto-approved operation."""
        matrix = ApprovalMatrix(
            high_confidence_threshold=0.85,
            review_threshold=0.65,
            auto_approval_teams=["general"],
            review_routing={"deploy": ["architecture"]}
        )
        gate = ConfidenceBasedGateLady(matrix)
        
        # Create operation context
        context = OperationContext(
            operation_id="op-workflow-1",
            operation_type="deploy",
            complexity_level="simple",
            requestor_id="user-001",
            requestor_team="general",
            affected_services=["api"],
            estimated_impact="low"
        )
        
        # Create approval request
        request = ApprovalRequest(
            operation_context=context,
            confidence_score=0.95,
            lens_confidence=0.92,
            risk_score=0.03,
            timestamp=datetime.now()
        )
        
        # Evaluate
        result = gate.evaluate(request)
        
        # Verify decision
        assert result.decision == ApprovalDecision.AUTO_APPROVED
        assert result.confidence >= 0.85
        assert result.assigned_team is None
        
        # Verify logging
        stats = gate.get_decision_statistics()
        assert stats['total_decisions'] == 1
        assert stats['auto_approved'] == 1
    
    def test_full_review_workflow(self):
        """Complete workflow for review-required operation."""
        matrix = ApprovalMatrix(
            high_confidence_threshold=0.85,
            review_threshold=0.65,
            auto_approval_teams=["general"],
            review_routing={"deploy": ["architecture"]}
        )
        gate = ConfidenceBasedGateLady(matrix)
        
        # Create operation context
        context = OperationContext(
            operation_id="op-workflow-2",
            operation_type="deploy",
            complexity_level="complex",
            requestor_id="user-002",
            requestor_team="general",
            affected_services=["api", "database", "cache"],
            estimated_impact="high"
        )
        
        # Create approval request
        request = ApprovalRequest(
            operation_context=context,
            confidence_score=0.72,
            lens_confidence=0.75,
            risk_score=0.30,
            timestamp=datetime.now()
        )
        
        # Evaluate - should require review
        result = gate.evaluate(request)
        assert result.decision == ApprovalDecision.REVIEW_REQUIRED
        assert result.assigned_team == ReviewRoutingTeam.ARCHITECTURE
        
        # Simulate reviewer approval
        approved = gate.approve_review(
            result.request_id,
            approved=True,
            reviewer_id="reviewer-001"
        )
        assert approved['decision'] == "auto_approved"


class TestComplexApprovalScenario:
    """Test complex approval scenarios."""
    
    def test_multiple_operations_queue(self):
        """Multiple operations are processed and queued correctly."""
        matrix = ApprovalMatrix(
            high_confidence_threshold=0.85,
            review_threshold=0.65,
            auto_approval_teams=["general"],
            review_routing={
                "deploy": ["architecture"],
                "security": ["security"],
                "scale": ["performance"]
            }
        )
        gate = ConfidenceBasedGateLady(matrix)
        
        operations = [
            ("op-1", "deploy", 0.95, 0.90, 0.05),      # auto-approve
            ("op-2", "security", 0.75, 0.78, 0.25),    # review
            ("op-3", "scale", 0.50, 0.45, 0.75),       # reject
            ("op-4", "deploy", 0.80, 0.82, 0.18),      # review
        ]
        
        for op_id, op_type, conf, lens, risk in operations:
            context = OperationContext(
                operation_id=op_id,
                operation_type=op_type,
                complexity_level="moderate",
                requestor_id="user-001",
                requestor_team="general",
                affected_services=["api"],
                estimated_impact="medium"
            )
            request = ApprovalRequest(
                operation_context=context,
                confidence_score=conf,
                lens_confidence=lens,
                risk_score=risk,
                timestamp=datetime.now()
            )
            gate.evaluate(request)
        
        # Verify statistics
        stats = gate.get_decision_statistics()
        assert stats['total_decisions'] == 4
        assert stats['auto_approved'] == 1
        assert stats['review_required'] == 2
        assert stats['rejected'] == 1
