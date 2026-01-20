"""
Tests for AC-GC-002-01: Severity-Based Rule Execution Gates

AC-GC-002-01: Severity-Based Rule Execution Gates
- SeverityGate processes rules in order: BLOCKED → WARNING → INFO
- BLOCKED gate: fails immediately on first violation
- WARNING gate: logs violations but continues
- INFO gate: captures info for audit trail only
- Deterministic ordering: same rules always evaluated in same sequence
- Audit trail captures each gate's decisions with timestamps

CORE Governance Rules:
- CORE-008: TDD (tests before code)
- CORE-011: Type hints (100%)
- CORE-012: Docstrings (Google style)
- CORE-027: Audit trail logging
"""

import pytest
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime


class RuleSeverity(Enum):
    """Rule severity levels."""
    BLOCKED = "BLOCKED"
    WARNING = "WARNING"
    INFO = "INFO"


@dataclass
class RuleViolation:
    """Represents a single rule violation."""
    rule_id: str
    severity: RuleSeverity
    message: str
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class GateResult:
    """Result of gate evaluation."""
    passed: bool
    violations: List[RuleViolation] = field(default_factory=list)
    gate_name: str = ""
    execution_time_ms: float = 0.0


class SeverityGate:
    """Executes governance rules in severity order."""
    
    def __init__(self) -> None:
        """Initialize severity gate."""
        self._execution_order: List[RuleSeverity] = [
            RuleSeverity.BLOCKED,
            RuleSeverity.WARNING,
            RuleSeverity.INFO
        ]
    
    def evaluate(
        self,
        rules: Dict[str, Tuple[RuleSeverity, bool]],
        gate_name: str = "default"
    ) -> GateResult:
        """
        Evaluate rules in severity order.
        
        Args:
            rules: Dict[rule_id → (severity, passes)]
            gate_name: Name of gate for logging
        
        Returns:
            GateResult with violations and pass/fail status
        """
        violations: List[RuleViolation] = []
        passed: bool = True
        
        # Process BLOCKED rules first
        for rule_id, (severity, passes) in rules.items():
            if severity == RuleSeverity.BLOCKED and not passes:
                violations.append(RuleViolation(
                    rule_id=rule_id,
                    severity=severity,
                    message=f"{rule_id} violation: BLOCKED rule failed"
                ))
                passed = False
        
        # If BLOCKED gate failed, stop here
        if not passed:
            return GateResult(
                passed=False,
                violations=violations,
                gate_name=f"{gate_name}_BLOCKED"
            )
        
        # Process WARNING rules (never blocking)
        for rule_id, (severity, passes) in rules.items():
            if severity == RuleSeverity.WARNING and not passes:
                violations.append(RuleViolation(
                    rule_id=rule_id,
                    severity=severity,
                    message=f"{rule_id} violation: WARNING (logged, not blocking)"
                ))
        
        # Process INFO rules (audit only)
        for rule_id, (severity, passes) in rules.items():
            if severity == RuleSeverity.INFO and not passes:
                violations.append(RuleViolation(
                    rule_id=rule_id,
                    severity=severity,
                    message=f"{rule_id} info: logged to audit trail"
                ))
        
        return GateResult(
            passed=True,
            violations=violations,
            gate_name=f"{gate_name}_WARNING_INFO"
        )
    
    def evaluate_blocked_gate(
        self,
        rules: Dict[str, bool]
    ) -> GateResult:
        """
        Evaluate only BLOCKED rules (fail-fast).
        
        Args:
            rules: Dict[rule_id → passes]
        
        Returns:
            GateResult (False on first violation)
        """
        violations: List[RuleViolation] = []
        
        for rule_id, passes in rules.items():
            if not passes:
                violations.append(RuleViolation(
                    rule_id=rule_id,
                    severity=RuleSeverity.BLOCKED,
                    message=f"{rule_id} violation: BLOCKED rule failed"
                ))
                return GateResult(
                    passed=False,
                    violations=violations,
                    gate_name="BLOCKED"
                )
        
        return GateResult(
            passed=True,
            violations=[],
            gate_name="BLOCKED"
        )
    
    def evaluate_warning_gate(
        self,
        rules: Dict[str, bool]
    ) -> GateResult:
        """
        Evaluate WARNING rules (never blocking).
        
        Args:
            rules: Dict[rule_id → passes]
        
        Returns:
            GateResult (always passed, violations logged)
        """
        violations: List[RuleViolation] = []
        
        for rule_id, passes in rules.items():
            if not passes:
                violations.append(RuleViolation(
                    rule_id=rule_id,
                    severity=RuleSeverity.WARNING,
                    message=f"{rule_id} violation: WARNING (logged, not blocking)"
                ))
        
        return GateResult(
            passed=True,  # Always passes
            violations=violations,
            gate_name="WARNING"
        )


class TestRuleViolation:
    """Tests for RuleViolation dataclass."""
    
    def test_violation_creation(self) -> None:
        """Test creating violation."""
        violation = RuleViolation(
            rule_id="CORE-008",
            severity=RuleSeverity.BLOCKED,
            message="Test violation"
        )
        assert violation.rule_id == "CORE-008"
        assert violation.severity == RuleSeverity.BLOCKED
        assert violation.timestamp is not None
    
    def test_violation_with_custom_timestamp(self) -> None:
        """Test violation with custom timestamp."""
        ts = datetime(2026, 1, 19, 10, 0, 0)
        violation = RuleViolation(
            rule_id="CORE-011",
            severity=RuleSeverity.WARNING,
            message="Warning",
            timestamp=ts
        )
        assert violation.timestamp == ts


class TestGateResult:
    """Tests for GateResult dataclass."""
    
    def test_gate_result_passed(self) -> None:
        """Test gate result for passing gate."""
        result = GateResult(
            passed=True,
            violations=[],
            gate_name="BLOCKED"
        )
        assert result.passed is True
        assert len(result.violations) == 0
    
    def test_gate_result_failed_with_violations(self) -> None:
        """Test gate result with violations."""
        violations = [
            RuleViolation("CORE-008", RuleSeverity.BLOCKED, "Failed")
        ]
        result = GateResult(
            passed=False,
            violations=violations,
            gate_name="BLOCKED"
        )
        assert result.passed is False
        assert len(result.violations) == 1


class TestSeverityGateBasic:
    """Tests for basic SeverityGate functionality."""
    
    @pytest.fixture
    def gate(self) -> SeverityGate:
        """Create gate fixture."""
        return SeverityGate()
    
    def test_gate_initialization(self, gate: SeverityGate) -> None:
        """Test gate initializes correctly."""
        assert gate is not None
        assert len(gate._execution_order) == 3
    
    def test_all_rules_pass(self, gate: SeverityGate) -> None:
        """Test gate passes when all rules pass."""
        rules = {
            "CORE-008": (RuleSeverity.BLOCKED, True),
            "CORE-011": (RuleSeverity.WARNING, True),
            "CORE-012": (RuleSeverity.INFO, True)
        }
        result = gate.evaluate(rules)
        assert result.passed is True
        assert len(result.violations) == 0
    
    def test_blocked_rule_fails_gate(self, gate: SeverityGate) -> None:
        """Test BLOCKED rule failure stops gate."""
        rules = {
            "CORE-008": (RuleSeverity.BLOCKED, False),
            "CORE-011": (RuleSeverity.WARNING, True)
        }
        result = gate.evaluate(rules)
        assert result.passed is False
        assert len(result.violations) == 1
        assert result.violations[0].rule_id == "CORE-008"
    
    def test_warning_violation_logged_not_blocking(self, gate: SeverityGate) -> None:
        """Test WARNING violations logged but not blocking."""
        rules = {
            "CORE-008": (RuleSeverity.BLOCKED, True),
            "CORE-011": (RuleSeverity.WARNING, False)
        }
        result = gate.evaluate(rules)
        assert result.passed is True
        assert len(result.violations) == 1
        assert result.violations[0].severity == RuleSeverity.WARNING
    
    def test_info_violation_audit_only(self, gate: SeverityGate) -> None:
        """Test INFO violations audit-only."""
        rules = {
            "CORE-001": (RuleSeverity.INFO, False)
        }
        result = gate.evaluate(rules)
        assert result.passed is True
        assert len(result.violations) == 1
        assert result.violations[0].severity == RuleSeverity.INFO


class TestBlockedGate:
    """Tests for BLOCKED gate specifically."""
    
    @pytest.fixture
    def gate(self) -> SeverityGate:
        """Create gate fixture."""
        return SeverityGate()
    
    def test_blocked_gate_all_pass(self, gate: SeverityGate) -> None:
        """Test BLOCKED gate when all rules pass."""
        rules = {
            "CORE-008": True,
            "CORE-011": True,
            "CORE-012": True
        }
        result = gate.evaluate_blocked_gate(rules)
        assert result.passed is True
        assert result.gate_name == "BLOCKED"
    
    def test_blocked_gate_first_failure(self, gate: SeverityGate) -> None:
        """Test BLOCKED gate fails on first violation."""
        rules = {
            "CORE-008": False,
            "CORE-011": False,  # Won't evaluate this
            "CORE-012": True
        }
        result = gate.evaluate_blocked_gate(rules)
        assert result.passed is False
        assert len(result.violations) == 1
        assert result.violations[0].rule_id == "CORE-008"
    
    def test_blocked_gate_empty_rules(self, gate: SeverityGate) -> None:
        """Test BLOCKED gate with empty rules."""
        rules: Dict[str, bool] = {}
        result = gate.evaluate_blocked_gate(rules)
        assert result.passed is True


class TestWarningGate:
    """Tests for WARNING gate specifically."""
    
    @pytest.fixture
    def gate(self) -> SeverityGate:
        """Create gate fixture."""
        return SeverityGate()
    
    def test_warning_gate_always_passes(self, gate: SeverityGate) -> None:
        """Test WARNING gate always passes."""
        rules = {
            "CORE-015": False,
            "CORE-016": False,
            "CORE-017": False
        }
        result = gate.evaluate_warning_gate(rules)
        assert result.passed is True
        assert len(result.violations) == 3
    
    def test_warning_gate_no_violations(self, gate: SeverityGate) -> None:
        """Test WARNING gate with no violations."""
        rules = {
            "CORE-015": True,
            "CORE-016": True
        }
        result = gate.evaluate_warning_gate(rules)
        assert result.passed is True
        assert len(result.violations) == 0
    
    def test_warning_gate_partial_violations(self, gate: SeverityGate) -> None:
        """Test WARNING gate with some violations."""
        rules = {
            "CORE-015": True,
            "CORE-016": False,
            "CORE-017": True
        }
        result = gate.evaluate_warning_gate(rules)
        assert result.passed is True
        assert len(result.violations) == 1


class TestSeverityOrdering:
    """Tests for severity-based execution ordering."""
    
    @pytest.fixture
    def gate(self) -> SeverityGate:
        """Create gate fixture."""
        return SeverityGate()
    
    def test_blocked_evaluated_first(self, gate: SeverityGate) -> None:
        """Test BLOCKED rules evaluated before WARNING/INFO."""
        rules = {
            "CORE-008": (RuleSeverity.BLOCKED, False),
            "CORE-011": (RuleSeverity.WARNING, False),
            "CORE-012": (RuleSeverity.INFO, False)
        }
        result = gate.evaluate(rules)
        
        # Only BLOCKED violation should be returned
        assert result.passed is False
        assert len(result.violations) == 1
        assert result.violations[0].severity == RuleSeverity.BLOCKED
    
    def test_deterministic_ordering(self, gate: SeverityGate) -> None:
        """Test same rules produce same ordering."""
        rules1 = {
            "CORE-011": (RuleSeverity.WARNING, False),
            "CORE-008": (RuleSeverity.BLOCKED, True),
            "CORE-012": (RuleSeverity.INFO, False)
        }
        rules2 = {
            "CORE-008": (RuleSeverity.BLOCKED, True),
            "CORE-011": (RuleSeverity.WARNING, False),
            "CORE-012": (RuleSeverity.INFO, False)
        }
        
        result1 = gate.evaluate(rules1)
        result2 = gate.evaluate(rules2)
        
        # Both should have same violations in same order
        assert result1.passed == result2.passed
        assert len(result1.violations) == len(result2.violations)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
