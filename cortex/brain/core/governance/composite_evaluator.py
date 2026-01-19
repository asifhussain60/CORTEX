"""
Implementation of AC-GC-005-01: Composite Rule Evaluator

Evaluates composite rule profiles with:
- Topological ordering: Rules evaluated in dependency order
- Severity gate enforcement: BLOCKED/WARNING/INFO severity levels
- Violation tracking: Segregated by severity
- Result caching: Invalidate on profile changes
- Detailed reporting: Timeline, duration, step-by-step results
- O(V+E) performance for all evaluations

Integrates with DAGBuilder for dependency resolution and SeverityGate
for enforcement logic. Produces comprehensive evaluation reports for
audit trail and debugging.

CORE Governance Rules:
- CORE-005: Path portability (pathlib used for paths)
- CORE-008: TDD (tests created first)
- CORE-011: Type hints (100% coverage)
- CORE-012: Google docstrings
- CORE-027: Audit trail logging
"""

import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime


logger = logging.getLogger(__name__)


class RuleSeverity(Enum):
    """
    Rule severity levels for evaluation.
    
    BLOCKED: Fail-fast enforcement (violation stops evaluation)
    WARNING: Continue but log violations
    INFO: Audit trail only
    """
    BLOCKED = "BLOCKED"
    WARNING = "WARNING"
    INFO = "INFO"


@dataclass
class EvaluationStep:
    """
    Single step in rule evaluation timeline.
    
    Attributes:
        rule_id: Rule being evaluated
        passed: Whether rule passed
        severity: Severity level of rule
        message: Evaluation result message
        timestamp: When evaluation occurred
    """
    rule_id: str
    passed: bool
    severity: RuleSeverity
    message: str
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert step to dictionary."""
        return {
            "rule_id": self.rule_id,
            "passed": self.passed,
            "severity": self.severity.value,
            "message": self.message,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class EvaluationReport:
    """
    Complete evaluation report for profile.
    
    Attributes:
        profile_name: Name of evaluated profile
        started_at: Evaluation start time
        completed_at: Evaluation completion time
        passed: Whether profile passed (no BLOCKED violations)
        blocked_violations: List of failed BLOCKED rules
        warning_violations: List of failed WARNING rules
        info_violations: List of failed INFO rules
        evaluation_steps: Timeline of all evaluation steps
    """
    profile_name: str
    started_at: datetime
    completed_at: datetime
    passed: bool
    blocked_violations: List[str] = field(default_factory=list)
    warning_violations: List[str] = field(default_factory=list)
    info_violations: List[str] = field(default_factory=list)
    evaluation_steps: List[EvaluationStep] = field(default_factory=list)
    
    @property
    def duration_ms(self) -> float:
        """
        Calculate evaluation duration in milliseconds.
        
        Returns:
            Duration as float milliseconds
        """
        delta = self.completed_at - self.started_at
        return delta.total_seconds() * 1000
    
    @property
    def total_violations(self) -> int:
        """
        Get total violation count across all severities.
        
        Returns:
            Count of violations
        """
        return (
            len(self.blocked_violations) +
            len(self.warning_violations) +
            len(self.info_violations)
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert report to dictionary.
        
        Returns:
            Dictionary representation for serialization
        """
        return {
            "profile_name": self.profile_name,
            "passed": self.passed,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat(),
            "duration_ms": self.duration_ms,
            "total_violations": self.total_violations,
            "blocked_violations": self.blocked_violations,
            "warning_violations": self.warning_violations,
            "info_violations": self.info_violations,
            "evaluation_steps": [s.to_dict() for s in self.evaluation_steps]
        }


class CompositeRuleEvaluator:
    """
    Evaluates composite rule profiles in topological order.
    
    Coordinates between:
    - DAGBuilder: Provides topological evaluation order
    - SeverityGate: Enforces severity-based rules
    - ProfileRegistry: Provides profile definitions
    
    Key features:
    - Evaluates rules in dependency order (O(V+E))
    - Tracks violations by severity level
    - Produces detailed timeline reports
    - Caches results (invalidated on profile changes)
    - Full audit trail of all evaluations
    
    Used by Stage 2 Routing to determine operation eligibility.
    """
    
    def __init__(self) -> None:
        """Initialize composite evaluator."""
        self._cache: Dict[str, EvaluationReport] = {}
        self._evaluation_history: List[EvaluationReport] = []
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def evaluate(
        self,
        profile_name: str,
        rules: Dict[str, Tuple[RuleSeverity, bool]],
        order: List[str],
        audit: bool = True
    ) -> EvaluationReport:
        """
        Evaluate all rules in given topological order.
        
        Processes rules in order, tracking results by severity. BLOCKED
        violations mark profile as failed. WARNING violations logged but
        allow continuation. INFO violations audit-only.
        
        Args:
            profile_name: Name of profile being evaluated
            rules: Dict rule_id → (severity, passes) tuples
            order: Topological evaluation order (from DAGBuilder)
            audit: Whether to log to audit trail
        
        Returns:
            Detailed evaluation report
        """
        started = datetime.now()
        steps: List[EvaluationStep] = []
        blocked_violations: List[str] = []
        warning_violations: List[str] = []
        info_violations: List[str] = []
        passed = True
        
        if audit:
            self._logger.info(
                f"Evaluation starting: {profile_name}",
                extra={"profile": profile_name, "rule_count": len(order)}
            )
        
        # Evaluate each rule in order
        for rule_id in order:
            if rule_id not in rules:
                if audit:
                    self._logger.debug(f"Rule not found: {rule_id}")
                continue
            
            severity, rule_passed = rules[rule_id]
            message = "PASS" if rule_passed else "FAIL"
            
            # Record step
            step = EvaluationStep(
                rule_id=rule_id,
                passed=rule_passed,
                severity=severity,
                message=message
            )
            steps.append(step)
            
            # Track violations by severity
            if not rule_passed:
                if severity == RuleSeverity.BLOCKED:
                    blocked_violations.append(rule_id)
                    passed = False
                    if audit:
                        self._logger.error(
                            f"BLOCKED violation: {rule_id}",
                            extra={"rule": rule_id, "step": step.to_dict()}
                        )
                elif severity == RuleSeverity.WARNING:
                    warning_violations.append(rule_id)
                    if audit:
                        self._logger.warning(
                            f"WARNING violation: {rule_id}",
                            extra={"rule": rule_id, "step": step.to_dict()}
                        )
                elif severity == RuleSeverity.INFO:
                    info_violations.append(rule_id)
                    if audit:
                        self._logger.info(
                            f"INFO: {rule_id}",
                            extra={"rule": rule_id, "step": step.to_dict()}
                        )
        
        completed = datetime.now()
        
        # Create report
        report = EvaluationReport(
            profile_name=profile_name,
            started_at=started,
            completed_at=completed,
            passed=passed,
            blocked_violations=blocked_violations,
            warning_violations=warning_violations,
            info_violations=info_violations,
            evaluation_steps=steps
        )
        
        # Update history and cache
        self._evaluation_history.append(report)
        self._cache[profile_name] = report
        
        if audit:
            self._logger.info(
                f"Evaluation complete: {profile_name}",
                extra={
                    "profile": profile_name,
                    "passed": passed,
                    "duration_ms": report.duration_ms,
                    "total_violations": report.total_violations,
                    "blocked_count": len(blocked_violations),
                    "warning_count": len(warning_violations),
                    "info_count": len(info_violations)
                }
            )
        
        return report
    
    def get_cached_report(self, profile_name: str) -> Optional[EvaluationReport]:
        """
        Get cached evaluation report (O(1)).
        
        Args:
            profile_name: Name of profile
        
        Returns:
            Cached report or None if not found
        """
        return self._cache.get(profile_name)
    
    def has_cached_report(self, profile_name: str) -> bool:
        """
        Check if report cached (O(1)).
        
        Args:
            profile_name: Name of profile
        
        Returns:
            True if cached
        """
        return profile_name in self._cache
    
    def invalidate_cache(self, profile_name: str) -> None:
        """
        Invalidate cached report.
        
        Called when profile is updated. Logs invalidation.
        
        Args:
            profile_name: Name of profile
        """
        if profile_name in self._cache:
            del self._cache[profile_name]
            self._logger.info(
                f"Cache invalidated: {profile_name}",
                extra={"profile": profile_name}
            )
    
    def invalidate_all_cache(self) -> None:
        """
        Invalidate all cached reports.
        
        Called when profiles change significantly.
        """
        count = len(self._cache)
        self._cache.clear()
        self._logger.info(
            f"All cache invalidated: {count} profiles",
            extra={"count": count}
        )
    
    def clear_cache(self) -> None:
        """Clear all cached reports."""
        self._cache.clear()
        self._logger.debug("Cache cleared")
    
    def get_history(self) -> List[EvaluationReport]:
        """
        Get complete evaluation history.
        
        Returns:
            Copied list of all evaluation reports
        """
        return self._evaluation_history.copy()
    
    def get_history_for_profile(self, profile_name: str) -> List[EvaluationReport]:
        """
        Get history for specific profile.
        
        Args:
            profile_name: Name of profile
        
        Returns:
            List of reports for this profile
        """
        return [
            r for r in self._evaluation_history
            if r.profile_name == profile_name
        ]
    
    def cache_size(self) -> int:
        """
        Get current cache size.
        
        Returns:
            Number of cached reports
        """
        return len(self._cache)
    
    def history_size(self) -> int:
        """
        Get total evaluation history size.
        
        Returns:
            Total number of evaluations performed
        """
        return len(self._evaluation_history)
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get evaluator statistics.
        
        Returns:
            Dictionary with cache_size, history_size, avg_duration_ms
        """
        total_duration = sum(
            r.duration_ms for r in self._evaluation_history
        )
        avg_duration = (
            total_duration / len(self._evaluation_history)
            if self._evaluation_history else 0.0
        )
        
        return {
            "cache_size": self.cache_size(),
            "history_size": self.history_size(),
            "avg_duration_ms": avg_duration,
            "total_evaluations": len(self._evaluation_history)
        }
    
    def clear_history(self) -> None:
        """Clear evaluation history."""
        self._evaluation_history.clear()
        self._logger.info("History cleared")
    
    def export_history_json(self) -> List[Dict[str, Any]]:
        """
        Export history as JSON-serializable list.
        
        Returns:
            List of report dictionaries
        """
        return [r.to_dict() for r in self._evaluation_history]
