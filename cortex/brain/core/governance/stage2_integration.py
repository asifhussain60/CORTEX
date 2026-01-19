"""
Implementation of AC-GC-007-01: Master Orchestrator Stage 2 Integration

Integrates governance system into Master Orchestrator Stage 2 (Routing):
- Profile selection: Based on (intent_type, confidence_band, phase)
- Eligibility check: Evaluate profile rules via composite evaluator
- Gate enforcement: BLOCKED/WARNING/INFO severity handling
- Decision routing: Route to handler or governance_violation_handler
- Decision logging: Audit trail of all governance decisions

Integration points:
- Stage 1 Comprehension output: intent, confidence, phase
- Stage 2 Routing input: operation context
- Stage 2 Routing output: eligibility, destination handler
- Intent Router: Profile selection matrix

CORE Governance Rules:
- CORE-005: Path portability (pathlib used for paths)
- CORE-008: TDD (tests created first)
- CORE-011: Type hints (100% coverage)
- CORE-012: Google docstrings
- CORE-027: Audit trail logging
"""

import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
from datetime import datetime


logger = logging.getLogger(__name__)


class IntentType(Enum):
    """
    Master Orchestrator operation intent types.
    
    ANALYZE: Information extraction and comprehension
    SYNTHESIZE: Generate or combine outputs
    VALIDATE: Check correctness and compliance
    TRANSFORM: Convert between representations
    AUDIT: Create records for compliance trail
    """
    ANALYZE = "ANALYZE"
    SYNTHESIZE = "SYNTHESIZE"
    VALIDATE = "VALIDATE"
    TRANSFORM = "TRANSFORM"
    AUDIT = "AUDIT"


class ConfidenceBand(Enum):
    """
    Confidence level bands.
    
    HIGH: ≥0.8 (high confidence in operation outcome)
    MEDIUM: 0.5-0.8 (moderate confidence)
    LOW: <0.5 (low confidence)
    """
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class ExecutionPhase(Enum):
    """
    Master Orchestrator execution phases.
    
    COMPREHENSION: Understand input and context (Stage 1)
    ROUTING: Route to appropriate handler (Stage 2)
    KNOWLEDGE: Gather supporting information (Stage 3)
    APPROVAL: Final validation and approval (Stage 4)
    """
    COMPREHENSION = "COMPREHENSION"
    ROUTING = "ROUTING"
    KNOWLEDGE = "KNOWLEDGE"
    APPROVAL = "APPROVAL"


class RuleSeverity(Enum):
    """
    Rule severity levels for gate enforcement.
    
    BLOCKED: Fail-fast enforcement (violation blocks operation)
    WARNING: Continue but log violations
    INFO: Audit trail only
    """
    BLOCKED = "BLOCKED"
    WARNING = "WARNING"
    INFO = "INFO"


@dataclass
class GovernanceDecision:
    """
    Decision from governance eligibility check.
    
    Attributes:
        eligible: Whether operation is eligible to proceed
        profile_name: Governance profile used for evaluation
        blocked_violations: Rules that blocked operation
        warning_violations: Rules with warnings (non-blocking)
        info_violations: Rules with info entries (audit-only)
        message: Human-readable decision message
        timestamp: When decision was made
    """
    eligible: bool
    profile_name: str
    blocked_violations: List[str]
    warning_violations: List[str]
    info_violations: List[str]
    message: str
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert decision to dictionary.
        
        Returns:
            Dictionary representation
        """
        return {
            "eligible": self.eligible,
            "profile_name": self.profile_name,
            "blocked_violations": self.blocked_violations,
            "warning_violations": self.warning_violations,
            "info_violations": self.info_violations,
            "message": self.message,
            "timestamp": self.timestamp.isoformat()
        }


class GovernanceGate:
    """
    Governance gate for Stage 2 Routing integration.
    
    Coordinates:
    - Profile selection from matrix based on operation context
    - Rule evaluation via composite evaluator
    - Severity-based gate enforcement
    - Decision logging and audit trail
    
    Input: (intent, confidence, phase, rules, order)
    Output: GovernanceDecision with eligibility and violations
    """
    
    def __init__(self) -> None:
        """Initialize governance gate."""
        self._decisions: List[GovernanceDecision] = []
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def check_eligibility(
        self,
        intent: IntentType,
        confidence: ConfidenceBand,
        phase: ExecutionPhase,
        profile_name: Optional[str] = None,
        rules: Optional[Dict[str, Tuple[RuleSeverity, bool]]] = None,
        order: Optional[List[str]] = None,
        audit: bool = True
    ) -> GovernanceDecision:
        """
        Check operation eligibility against governance rules.
        
        Evaluates rules in given order, segregating violations by severity.
        BLOCKED violations make operation ineligible. WARNING violations
        logged but allowed. INFO violations audit-only.
        
        Args:
            intent: Operation intent type
            confidence: Confidence band
            phase: Execution phase
            profile_name: Profile name (auto-generated if None)
            rules: Dict rule_id → (severity, passes)
            order: Topological evaluation order
            audit: Whether to log to audit trail
        
        Returns:
            GovernanceDecision with eligibility and violations
        """
        # Generate profile name if not provided
        if profile_name is None:
            profile_name = f"{intent.value}_{confidence.value}_{phase.value}"
        
        # Initialize empty data if not provided
        if rules is None:
            rules = {}
        if order is None:
            order = list(rules.keys())
        
        # Evaluate rules in order
        blocked_violations: List[str] = []
        warning_violations: List[str] = []
        info_violations: List[str] = []
        eligible = True
        
        for rule_id in order:
            if rule_id not in rules:
                if audit:
                    self._logger.debug(f"Rule not found in evaluation: {rule_id}")
                continue
            
            severity, passed = rules[rule_id]
            
            # Aggregate violations by severity
            if not passed:
                if severity == RuleSeverity.BLOCKED:
                    blocked_violations.append(rule_id)
                    eligible = False
                    if audit:
                        self._logger.error(
                            f"BLOCKED violation: {rule_id}",
                            extra={"rule": rule_id, "profile": profile_name}
                        )
                elif severity == RuleSeverity.WARNING:
                    warning_violations.append(rule_id)
                    if audit:
                        self._logger.warning(
                            f"WARNING violation: {rule_id}",
                            extra={"rule": rule_id, "profile": profile_name}
                        )
                elif severity == RuleSeverity.INFO:
                    info_violations.append(rule_id)
                    if audit:
                        self._logger.info(
                            f"INFO: {rule_id}",
                            extra={"rule": rule_id, "profile": profile_name}
                        )
        
        # Build decision message
        if eligible:
            message = "ELIGIBLE"
        else:
            message = f"NOT ELIGIBLE: {len(blocked_violations)} BLOCKED violation(s)"
        
        # Create decision
        decision = GovernanceDecision(
            eligible=eligible,
            profile_name=profile_name,
            blocked_violations=blocked_violations,
            warning_violations=warning_violations,
            info_violations=info_violations,
            message=message,
            timestamp=datetime.now()
        )
        
        # Track decision
        self._decisions.append(decision)
        
        if audit:
            self._logger.info(
                f"Governance decision: {profile_name}",
                extra={
                    "intent": intent.value,
                    "confidence": confidence.value,
                    "phase": phase.value,
                    "eligible": eligible,
                    "blocked_count": len(blocked_violations),
                    "warning_count": len(warning_violations),
                    "info_count": len(info_violations)
                }
            )
        
        return decision
    
    def get_decision_count(self) -> int:
        """
        Get total decisions made.
        
        Returns:
            Count of decisions
        """
        return len(self._decisions)
    
    def get_decisions(self) -> List[GovernanceDecision]:
        """
        Get all decisions.
        
        Returns:
            Copied list of all decisions
        """
        return self._decisions.copy()
    
    def get_decisions_for_profile(self, profile_name: str) -> List[GovernanceDecision]:
        """
        Get decisions for specific profile.
        
        Args:
            profile_name: Profile name
        
        Returns:
            List of decisions for this profile
        """
        return [
            d for d in self._decisions
            if d.profile_name == profile_name
        ]
    
    def clear_decisions(self) -> None:
        """Clear decision history."""
        self._decisions.clear()
        self._logger.info("Decision history cleared")


class Stage2GovernanceRouter:
    """
    Stage 2 Routing with governance integration.
    
    Coordinates with Intent Router to:
    1. Select governance profile based on operation context
    2. Check eligibility via governance gate
    3. Route to appropriate handler or violation handler
    4. Maintain audit trail of all routing decisions
    
    Integration with Master Orchestrator:
    - Input: (intent, confidence, phase) from Stage 1 Comprehension
    - Output: (eligible, destination, decision) to Stage 3 Knowledge
    - Fallback: Ineligible operations routed to governance_violation_handler
    """
    
    def __init__(self) -> None:
        """Initialize router."""
        self._gate = GovernanceGate()
        self._routes: Dict[str, str] = {}
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def register_route(
        self,
        profile_or_context: str,
        destination: str,
        audit: bool = True
    ) -> None:
        """
        Register routing destination for profile/context.
        
        Args:
            profile_or_context: Profile name or (intent_confidence_phase)
            destination: Handler destination
            audit: Whether to log registration
        """
        self._routes[profile_or_context] = destination
        if audit:
            self._logger.info(
                f"Route registered: {profile_or_context} → {destination}",
                extra={"profile": profile_or_context, "destination": destination}
            )
    
    def route_with_governance(
        self,
        intent: IntentType,
        confidence: ConfidenceBand,
        phase: ExecutionPhase,
        rules: Dict[str, Tuple[RuleSeverity, bool]],
        order: List[str],
        audit: bool = True
    ) -> Tuple[bool, str, GovernanceDecision]:
        """
        Route operation with governance eligibility check.
        
        Determines routing destination based on eligibility:
        - Eligible: Route to registered destination for (intent, confidence, phase)
        - Ineligible: Route to governance_violation_handler
        
        Args:
            intent: Operation intent type
            confidence: Confidence band
            phase: Execution phase
            rules: Dict rule_id → (severity, passes)
            order: Topological evaluation order
            audit: Whether to log decisions
        
        Returns:
            (eligible, destination, decision) tuple
        """
        profile_name = f"{intent.value}_{confidence.value}_{phase.value}"
        
        # Check eligibility
        decision = self._gate.check_eligibility(
            intent, confidence, phase,
            profile_name=profile_name,
            rules=rules,
            order=order,
            audit=audit
        )
        
        # Determine destination
        if decision.eligible:
            destination = self._routes.get(profile_name, "default_handler")
            if audit:
                self._logger.info(
                    f"Routing eligible operation: {profile_name} → {destination}",
                    extra={"profile": profile_name, "destination": destination}
                )
        else:
            destination = "governance_violation_handler"
            if audit:
                self._logger.warning(
                    f"Routing ineligible operation: {profile_name} → {destination}",
                    extra={
                        "profile": profile_name,
                        "blocked_violations": decision.blocked_violations
                    }
                )
        
        return decision.eligible, destination, decision
    
    def get_gate(self) -> GovernanceGate:
        """
        Get governance gate.
        
        Returns:
            GovernanceGate instance
        """
        return self._gate
    
    def get_routing_table(self) -> Dict[str, str]:
        """
        Get routing table.
        
        Returns:
            Copy of routing table
        """
        return self._routes.copy()
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get router statistics.
        
        Returns:
            Dictionary with routing and decision stats
        """
        total_decisions = self._gate.get_decision_count()
        decisions = self._gate.get_decisions()
        
        eligible_count = sum(1 for d in decisions if d.eligible)
        ineligible_count = total_decisions - eligible_count
        
        return {
            "total_decisions": total_decisions,
            "eligible_operations": eligible_count,
            "ineligible_operations": ineligible_count,
            "registered_routes": len(self._routes)
        }
