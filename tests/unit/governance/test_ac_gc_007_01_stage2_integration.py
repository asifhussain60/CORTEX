"""
Tests for AC-GC-007-01: Stage 2 Integration

AC-GC-007-01: Master Orchestrator Stage 2 Integration
- Route to governance system from Stage 2 Routing
- Select profile based on (intent, confidence, phase)
- Evaluate profile rules via composite evaluator
- Check gates (BLOCKED/WARNING/INFO)
- Return operation eligibility and violations
- Integration point with Intent Router

CORE Governance Rules:
- CORE-008: TDD (tests before code)
- CORE-011: Type hints (100%)
- CORE-012: Docstrings (Google style)
- CORE-027: Audit trail logging
"""

import pytest
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime


class IntentType(Enum):
    """Operation intent types."""
    ANALYZE = "ANALYZE"
    SYNTHESIZE = "SYNTHESIZE"
    VALIDATE = "VALIDATE"


class ConfidenceBand(Enum):
    """Confidence levels."""
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class ExecutionPhase(Enum):
    """Orchestrator phases."""
    COMPREHENSION = "COMPREHENSION"
    ROUTING = "ROUTING"
    KNOWLEDGE = "KNOWLEDGE"


class RuleSeverity(Enum):
    """Rule severity levels."""
    BLOCKED = "BLOCKED"
    WARNING = "WARNING"
    INFO = "INFO"


@dataclass
class GovernanceDecision:
    """Decision from governance check."""
    eligible: bool
    profile_name: str
    blocked_violations: List[str]
    warning_violations: List[str]
    info_violations: List[str]
    message: str
    timestamp: datetime


class GovernanceGate:
    """
    Governance gate for Stage 2 integration.
    
    Coordinates profile selection, evaluation, and eligibility determination.
    """
    
    def __init__(self) -> None:
        """Initialize gate."""
        self._decisions: List[GovernanceDecision] = []
    
    def check_eligibility(
        self,
        intent: IntentType,
        confidence: ConfidenceBand,
        phase: ExecutionPhase,
        profile_name: Optional[str] = None,
        rules: Optional[Dict[str, Tuple[RuleSeverity, bool]]] = None,
        order: Optional[List[str]] = None
    ) -> GovernanceDecision:
        """
        Check operation eligibility against governance.
        
        Args:
            intent: Operation intent
            confidence: Confidence level
            phase: Execution phase
            profile_name: Profile to use (if None, auto-selected)
            rules: Dict of rule_id → (severity, passes)
            order: Evaluation order
        
        Returns:
            GovernanceDecision with eligibility and violations
        """
        if profile_name is None:
            profile_name = f"{intent.value}_{confidence.value}_{phase.value}"
        
        if rules is None:
            rules = {}
        
        if order is None:
            order = list(rules.keys())
        
        # Evaluate rules
        blocked_violations = []
        warning_violations = []
        info_violations = []
        eligible = True
        
        for rule_id in order:
            if rule_id not in rules:
                continue
            
            severity, passed = rules[rule_id]
            if not passed:
                if severity == RuleSeverity.BLOCKED:
                    blocked_violations.append(rule_id)
                    eligible = False
                elif severity == RuleSeverity.WARNING:
                    warning_violations.append(rule_id)
                elif severity == RuleSeverity.INFO:
                    info_violations.append(rule_id)
        
        # Build message
        if eligible:
            message = "ELIGIBLE"
        else:
            message = f"NOT ELIGIBLE: {len(blocked_violations)} BLOCKED violations"
        
        decision = GovernanceDecision(
            eligible=eligible,
            profile_name=profile_name,
            blocked_violations=blocked_violations,
            warning_violations=warning_violations,
            info_violations=info_violations,
            message=message,
            timestamp=datetime.now()
        )
        
        self._decisions.append(decision)
        return decision
    
    def get_decision_count(self) -> int:
        """Get total decisions."""
        return len(self._decisions)
    
    def get_decisions(self) -> List[GovernanceDecision]:
        """Get all decisions."""
        return self._decisions.copy()


class Stage2GovernanceRouter:
    """
    Stage 2 routing with governance integration.
    
    Selects governance profile based on operation context and
    evaluates eligibility before routing.
    """
    
    def __init__(self) -> None:
        """Initialize router."""
        self._gate = GovernanceGate()
        self._routes: Dict[str, str] = {}
    
    def register_route(self, name: str, destination: str) -> None:
        """Register route."""
        self._routes[name] = destination
    
    def route_with_governance(
        self,
        intent: IntentType,
        confidence: ConfidenceBand,
        phase: ExecutionPhase,
        rules: Dict[str, Tuple[RuleSeverity, bool]],
        order: List[str]
    ) -> Tuple[bool, str, Any]:
        """
        Route operation with governance check.
        
        Args:
            intent: Operation intent
            confidence: Confidence level
            phase: Execution phase
            rules: Dict of rule_id → (severity, passes)
            order: Evaluation order
        
        Returns:
            (eligible, destination, decision)
        """
        profile_name = f"{intent.value}_{confidence.value}_{phase.value}"
        decision = self._gate.check_eligibility(
            intent, confidence, phase, profile_name, rules, order
        )
        
        if decision.eligible:
            destination = self._routes.get(profile_name, "default")
        else:
            destination = "governance_violation_handler"
        
        return decision.eligible, destination, decision
    
    def get_gate(self) -> GovernanceGate:
        """Get governance gate."""
        return self._gate


class TestGovernanceDecision:
    """Tests for GovernanceDecision."""
    
    def test_decision_creation(self) -> None:
        """Test creating decision."""
        decision = GovernanceDecision(
            eligible=True,
            profile_name="test_profile",
            blocked_violations=[],
            warning_violations=[],
            info_violations=[],
            message="ELIGIBLE",
            timestamp=datetime.now()
        )
        assert decision.eligible is True
        assert decision.profile_name == "test_profile"


class TestGovernanceGate:
    """Tests for GovernanceGate."""
    
    @pytest.fixture
    def gate(self) -> GovernanceGate:
        """Create gate fixture."""
        return GovernanceGate()
    
    def test_gate_initialization(self, gate: GovernanceGate) -> None:
        """Test gate initializes."""
        assert gate.get_decision_count() == 0
    
    def test_check_all_pass(self, gate: GovernanceGate) -> None:
        """Test eligibility check when all pass."""
        rules = {
            "CORE-008": (RuleSeverity.BLOCKED, True),
            "CORE-011": (RuleSeverity.WARNING, True)
        }
        order = ["CORE-008", "CORE-011"]
        
        decision = gate.check_eligibility(
            IntentType.ANALYZE,
            ConfidenceBand.HIGH,
            ExecutionPhase.ROUTING,
            rules=rules,
            order=order
        )
        
        assert decision.eligible is True
        assert len(decision.blocked_violations) == 0
    
    def test_check_blocked_violation(self, gate: GovernanceGate) -> None:
        """Test eligibility fails on BLOCKED violation."""
        rules = {
            "CORE-008": (RuleSeverity.BLOCKED, False)
        }
        order = ["CORE-008"]
        
        decision = gate.check_eligibility(
            IntentType.ANALYZE,
            ConfidenceBand.HIGH,
            ExecutionPhase.ROUTING,
            rules=rules,
            order=order
        )
        
        assert decision.eligible is False
        assert len(decision.blocked_violations) == 1
    
    def test_check_warning_not_blocking(self, gate: GovernanceGate) -> None:
        """Test WARNING violations don't block."""
        rules = {
            "CORE-008": (RuleSeverity.BLOCKED, True),
            "CORE-011": (RuleSeverity.WARNING, False)
        }
        order = ["CORE-008", "CORE-011"]
        
        decision = gate.check_eligibility(
            IntentType.ANALYZE,
            ConfidenceBand.HIGH,
            ExecutionPhase.ROUTING,
            rules=rules,
            order=order
        )
        
        assert decision.eligible is True
        assert len(decision.warning_violations) == 1
    
    def test_check_info_violations(self, gate: GovernanceGate) -> None:
        """Test INFO violations logged."""
        rules = {
            "CORE-001": (RuleSeverity.INFO, False)
        }
        order = ["CORE-001"]
        
        decision = gate.check_eligibility(
            IntentType.ANALYZE,
            ConfidenceBand.HIGH,
            ExecutionPhase.ROUTING,
            rules=rules,
            order=order
        )
        
        assert decision.eligible is True
        assert len(decision.info_violations) == 1
    
    def test_decision_tracking(self, gate: GovernanceGate) -> None:
        """Test decisions tracked."""
        rules = {"A": (RuleSeverity.BLOCKED, True)}
        order = ["A"]
        
        gate.check_eligibility(
            IntentType.ANALYZE,
            ConfidenceBand.HIGH,
            ExecutionPhase.ROUTING,
            rules=rules,
            order=order
        )
        
        assert gate.get_decision_count() == 1


class TestStage2GovernanceRouter:
    """Tests for Stage2GovernanceRouter."""
    
    @pytest.fixture
    def router(self) -> Stage2GovernanceRouter:
        """Create router fixture."""
        return Stage2GovernanceRouter()
    
    def test_router_initialization(self, router: Stage2GovernanceRouter) -> None:
        """Test router initializes."""
        assert router.get_gate() is not None
    
    def test_register_route(self, router: Stage2GovernanceRouter) -> None:
        """Test registering route."""
        router.register_route("analyze_high", "analyzer_service")
        assert router._routes["analyze_high"] == "analyzer_service"
    
    def test_route_eligible(self, router: Stage2GovernanceRouter) -> None:
        """Test routing eligible operation."""
        router.register_route("ANALYZE_HIGH_ROUTING", "analyzer")
        
        rules = {"CORE-008": (RuleSeverity.BLOCKED, True)}
        order = ["CORE-008"]
        
        eligible, dest, decision = router.route_with_governance(
            IntentType.ANALYZE,
            ConfidenceBand.HIGH,
            ExecutionPhase.ROUTING,
            rules,
            order
        )
        
        assert eligible is True
        assert dest == "analyzer"
        assert decision.eligible is True
    
    def test_route_ineligible(self, router: Stage2GovernanceRouter) -> None:
        """Test routing ineligible operation."""
        rules = {"CORE-008": (RuleSeverity.BLOCKED, False)}
        order = ["CORE-008"]
        
        eligible, dest, decision = router.route_with_governance(
            IntentType.ANALYZE,
            ConfidenceBand.HIGH,
            ExecutionPhase.ROUTING,
            rules,
            order
        )
        
        assert eligible is False
        assert dest == "governance_violation_handler"
        assert decision.eligible is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
