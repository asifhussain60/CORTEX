"""
Implementation of AC-GC-002-01: Severity-Based Rule Execution Gates

Provides SeverityGate executor for ordered rule evaluation:
- BLOCKED gate: All-or-nothing validation (fail-fast on violation)
- WARNING gate: Log violations but continue execution
- INFO gate: Audit-only, zero enforcement impact

Deterministic ordering ensures reproducible results across all evaluations.
Audit trail captures all gate decisions with timestamps.

CORE Governance Rules:
- CORE-005: Path portability (pathlib used for paths)
- CORE-008: TDD (tests created first)
- CORE-011: Type hints (100% coverage)
- CORE-012: Google docstrings
- CORE-027: Audit trail logging
"""

import logging
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from pathlib import Path


logger = logging.getLogger(__name__)


class RuleSeverity(Enum):
    """
    Rule severity levels determining execution gate.
    
    BLOCKED: Fail-fast enforcement (first violation stops processing)
    WARNING: Continue execution but log violations
    INFO: Audit trail only, no enforcement
    """
    BLOCKED = "BLOCKED"
    WARNING = "WARNING"
    INFO = "INFO"


@dataclass
class RuleViolation:
    """
    Represents a single rule violation event.
    
    Attributes:
        rule_id: Unique identifier for the rule (e.g., "CORE-008")
        severity: Severity level of the violation
        message: Human-readable violation message
        timestamp: When the violation was detected
    """
    rule_id: str
    severity: RuleSeverity
    message: str
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, str]:
        """
        Convert violation to dictionary.
        
        Returns:
            Dictionary with rule_id, severity value, message, timestamp ISO string
        """
        return {
            "rule_id": self.rule_id,
            "severity": self.severity.value,
            "message": self.message,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class GateResult:
    """
    Result of gate evaluation.
    
    Attributes:
        passed: Whether gate passed (BLOCKED gates only)
        violations: List of detected violations
        gate_name: Name of gate that was evaluated
        execution_time_ms: Time spent in gate evaluation (milliseconds)
    """
    passed: bool
    violations: List[RuleViolation] = field(default_factory=list)
    gate_name: str = ""
    execution_time_ms: float = 0.0
    
    def to_dict(self) -> Dict[str, any]:
        """
        Convert gate result to dictionary.
        
        Returns:
            Dictionary representation for serialization/logging
        """
        return {
            "passed": self.passed,
            "gate_name": self.gate_name,
            "violations_count": len(self.violations),
            "violations": [v.to_dict() for v in self.violations],
            "execution_time_ms": self.execution_time_ms
        }


class SeverityGate:
    """
    Executes governance rules in severity order with deterministic results.
    
    Processing order:
        1. BLOCKED rules (fail-fast: first violation stops all processing)
        2. WARNING rules (logged but not blocking)
        3. INFO rules (audit trail only)
    
    Provides specialized gates for each severity level and combined evaluation.
    All results include audit trail with timestamps and violation messages.
    """
    
    def __init__(self, audit_log_path: Optional[Path] = None) -> None:
        """
        Initialize severity gate executor.
        
        Args:
            audit_log_path: Optional path for audit trail logging
        """
        self._execution_order: List[RuleSeverity] = [
            RuleSeverity.BLOCKED,
            RuleSeverity.WARNING,
            RuleSeverity.INFO
        ]
        self._audit_log_path = audit_log_path
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def evaluate(
        self,
        rules: Dict[str, Tuple[RuleSeverity, bool]],
        gate_name: str = "default",
        audit: bool = True
    ) -> GateResult:
        """
        Evaluate all rules in severity order.
        
        Processes BLOCKED gate first (fail-fast). If no BLOCKED violations,
        continues to WARNING gate (logged but passing). Finally audits INFO
        level violations to trail.
        
        Args:
            rules: Mapping of rule_id → (severity, passes) tuple
            gate_name: Name of gate for audit trail
            audit: Whether to log to audit trail
        
        Returns:
            GateResult with all violations and pass/fail status
        """
        violations: List[RuleViolation] = []
        passed: bool = True
        
        # Stage 1: Evaluate BLOCKED rules (fail-fast)
        for rule_id, (severity, passes) in rules.items():
            if severity == RuleSeverity.BLOCKED and not passes:
                violation = RuleViolation(
                    rule_id=rule_id,
                    severity=severity,
                    message=f"{rule_id} violation: BLOCKED rule failed"
                )
                violations.append(violation)
                passed = False
                self._logger.error(
                    f"BLOCKED gate violation: {rule_id}",
                    extra={"gate": gate_name, "violation": violation.to_dict()}
                )
        
        # If BLOCKED gate failed, return immediately (fail-fast)
        if not passed:
            result = GateResult(
                passed=False,
                violations=violations,
                gate_name=f"{gate_name}_BLOCKED"
            )
            if audit:
                self._audit_log(result)
            return result
        
        # Stage 2: Evaluate WARNING rules (never blocking)
        for rule_id, (severity, passes) in rules.items():
            if severity == RuleSeverity.WARNING and not passes:
                violation = RuleViolation(
                    rule_id=rule_id,
                    severity=severity,
                    message=f"{rule_id} violation: WARNING (logged, not blocking)"
                )
                violations.append(violation)
                self._logger.warning(
                    f"WARNING gate violation: {rule_id}",
                    extra={"gate": gate_name, "violation": violation.to_dict()}
                )
        
        # Stage 3: Evaluate INFO rules (audit-only)
        for rule_id, (severity, passes) in rules.items():
            if severity == RuleSeverity.INFO and not passes:
                violation = RuleViolation(
                    rule_id=rule_id,
                    severity=severity,
                    message=f"{rule_id} info: logged to audit trail"
                )
                violations.append(violation)
                self._logger.info(
                    f"INFO gate: {rule_id}",
                    extra={"gate": gate_name, "violation": violation.to_dict()}
                )
        
        result = GateResult(
            passed=True,
            violations=violations,
            gate_name=f"{gate_name}_WARNING_INFO"
        )
        if audit:
            self._audit_log(result)
        return result
    
    def evaluate_blocked_gate(
        self,
        rules: Dict[str, bool],
        gate_name: str = "BLOCKED",
        audit: bool = True
    ) -> GateResult:
        """
        Evaluate BLOCKED rules only (fail-fast enforcement).
        
        Returns False on first violation without processing remaining rules.
        
        Args:
            rules: Mapping of rule_id → passes
            gate_name: Name for audit trail
            audit: Whether to log to audit trail
        
        Returns:
            GateResult (False on first violation, True if all pass)
        """
        violations: List[RuleViolation] = []
        
        # Deterministic iteration order
        for rule_id in sorted(rules.keys()):
            passes = rules[rule_id]
            if not passes:
                violation = RuleViolation(
                    rule_id=rule_id,
                    severity=RuleSeverity.BLOCKED,
                    message=f"{rule_id} violation: BLOCKED rule failed"
                )
                violations.append(violation)
                self._logger.error(
                    f"BLOCKED gate: {rule_id} failed",
                    extra={"violation": violation.to_dict()}
                )
                result = GateResult(
                    passed=False,
                    violations=violations,
                    gate_name=gate_name
                )
                if audit:
                    self._audit_log(result)
                return result
        
        result = GateResult(
            passed=True,
            violations=[],
            gate_name=gate_name
        )
        if audit:
            self._audit_log(result)
        return result
    
    def evaluate_warning_gate(
        self,
        rules: Dict[str, bool],
        gate_name: str = "WARNING",
        audit: bool = True
    ) -> GateResult:
        """
        Evaluate WARNING rules (never blocking).
        
        Logs all violations but always returns passed=True.
        
        Args:
            rules: Mapping of rule_id → passes
            gate_name: Name for audit trail
            audit: Whether to log to audit trail
        
        Returns:
            GateResult (always passed=True)
        """
        violations: List[RuleViolation] = []
        
        # Deterministic iteration order
        for rule_id in sorted(rules.keys()):
            passes = rules[rule_id]
            if not passes:
                violation = RuleViolation(
                    rule_id=rule_id,
                    severity=RuleSeverity.WARNING,
                    message=f"{rule_id} violation: WARNING (logged, not blocking)"
                )
                violations.append(violation)
                self._logger.warning(
                    f"WARNING gate: {rule_id}",
                    extra={"violation": violation.to_dict()}
                )
        
        result = GateResult(
            passed=True,  # Always passes
            violations=violations,
            gate_name=gate_name
        )
        if audit:
            self._audit_log(result)
        return result
    
    def evaluate_info_gate(
        self,
        rules: Dict[str, bool],
        gate_name: str = "INFO",
        audit: bool = True
    ) -> GateResult:
        """
        Evaluate INFO rules (audit trail only).
        
        No enforcement; always returns passed=True with violations logged.
        
        Args:
            rules: Mapping of rule_id → passes
            gate_name: Name for audit trail
            audit: Whether to log to audit trail
        
        Returns:
            GateResult (always passed=True, audit-only)
        """
        violations: List[RuleViolation] = []
        
        # Deterministic iteration order
        for rule_id in sorted(rules.keys()):
            passes = rules[rule_id]
            if not passes:
                violation = RuleViolation(
                    rule_id=rule_id,
                    severity=RuleSeverity.INFO,
                    message=f"{rule_id} info: logged to audit trail"
                )
                violations.append(violation)
                self._logger.info(
                    f"INFO gate: {rule_id}",
                    extra={"violation": violation.to_dict()}
                )
        
        result = GateResult(
            passed=True,  # Always passes
            violations=violations,
            gate_name=gate_name
        )
        if audit:
            self._audit_log(result)
        return result
    
    def _audit_log(self, result: GateResult) -> None:
        """
        Log gate result to audit trail.
        
        Args:
            result: GateResult to log
        """
        if self._audit_log_path:
            try:
                with open(self._audit_log_path, "a") as f:
                    f.write(f"{datetime.now().isoformat()}: {result.gate_name}\n")
                    f.write(f"  Passed: {result.passed}\n")
                    f.write(f"  Violations: {len(result.violations)}\n")
                    for v in result.violations:
                        f.write(f"    - {v.rule_id}: {v.message}\n")
            except Exception as e:
                self._logger.error(
                    f"Failed to write audit trail: {e}",
                    exc_info=True
                )
        
        self._logger.info(
            f"Gate evaluation complete: {result.gate_name}",
            extra={"result": result.to_dict()}
        )
    
    @property
    def execution_order(self) -> List[RuleSeverity]:
        """
        Get deterministic execution order.
        
        Returns:
            List of severity levels in evaluation order
        """
        return self._execution_order.copy()
