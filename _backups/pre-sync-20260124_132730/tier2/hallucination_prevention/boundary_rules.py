"""Boundary Rules - Behavioral boundaries for hallucination prevention.

Defines and enforces behavioral boundaries to prevent hallucinations.

Author: CORTEX Framework
"""

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional
from enum import Enum
import uuid
from datetime import datetime


class ViolationType(str, Enum):
    """Types of boundary violations."""
    SCOPE = "scope"
    FORMAT = "format"
    CONTENT = "content"
    BEHAVIOR = "behavior"
    SECURITY = "security"
    LOCKED_PHASE_MODIFICATION = "locked_phase_modification"
    AC_DELETION_WITHOUT_APPROVAL = "ac_deletion_without_approval"
    GOVERNANCE_BYPASS_ATTEMPT = "governance_bypass_attempt"


class BoundaryViolation(Exception):
    """Exception raised for boundary violations.
    
    Attributes:
        violation_type: Type of violation
        message: Violation message
        severity: Severity level (INFO, WARNING, CRITICAL)
        violation_id: Unique violation identifier
        context: Context dict that triggered violation
    """
    def __init__(self, violation_type: ViolationType, message: str, severity: str = "WARNING", context: Optional[Dict[str, Any]] = None):
        self.violation_type = violation_type
        self.message = message
        self.severity = severity
        self.violation_id = str(uuid.uuid4())
        self.context = context or {}
        super().__init__(message)


@dataclass
class BoundaryRule:
    """A behavioral boundary rule.

    Attributes:
        rule_id: Unique rule identifier.
        name: Rule name.
        description: Rule description.
        validator: Function that validates against rule.
        severity: Rule severity (0-100).
    """

    rule_id: str
    name: str
    description: str
    validator: Callable[[Any], bool]
    severity: int = 50


class BehavioralBoundaryRules:
    """Manages behavioral boundary rules."""

    def __init__(self) -> None:
        """Initialize boundary rules."""
        self.rules: Dict[str, BoundaryRule] = {}
        self.violations: list = []
        self._violation_cache: Dict[str, Any] = {}

    def register_rule(self, rule: BoundaryRule) -> None:
        """Register a boundary rule.

        Args:
            rule: BoundaryRule to register.
        """
        self.rules[rule.rule_id] = rule

    def unregister_rule(self, rule_id: str) -> None:
        """Unregister a rule.

        Args:
            rule_id: ID of rule to unregister.
        """
        if rule_id in self.rules:
            del self.rules[rule_id]

    def validate(self, rule_id: str, value: Any) -> bool:
        """Validate value against a rule.

        Args:
            rule_id: Rule ID to validate against.
            value: Value to validate.

        Returns:
            True if valid, False if violation.
        """
        if rule_id not in self.rules:
            return True  # Unknown rule, allow

        rule = self.rules[rule_id]
        try:
            is_valid = rule.validator(value)
            if not is_valid:
                self.violations.append(
                    {
                        "rule_id": rule_id,
                        "rule_name": rule.name,
                        "severity": rule.severity,
                        "value": str(value)[:100],  # Truncate for logging
                    }
                )
            return is_valid
        except Exception:
            return False

    def validate_all(self, value: Any) -> bool:
        """Validate value against all rules.

        Args:
            value: Value to validate.

        Returns:
            True if all rules pass, False if any violation.
        """
        for rule_id in self.rules:
            if not self.validate(rule_id, value):
                return False
        return True

    def get_rule(self, rule_id: str) -> Optional[BoundaryRule]:
        """Get a rule by ID.

        Args:
            rule_id: Rule ID.

        Returns:
            BoundaryRule or None if not found.
        """
        return self.rules.get(rule_id)

    def get_all_rules(self) -> List[BoundaryRule]:
        """Get all registered rules.

        Returns:
            List of all rules.
        """
        return list(self.rules.values())

    def get_violations(self) -> list:
        """Get recorded violations.

        Returns:
            List of violations.
        """
        return self.violations.copy()

    def clear_violations(self) -> None:
        """Clear violation history."""
        self.violations.clear()
    
    def check_ac_deletion(self, context: Dict[str, Any]) -> bool:
        """Check if AC deletion is allowed with proper approval.
        
        Args:
            context: Context dict with ac_id, action, approval, ac_status, etc.
            
        Returns:
            True if allowed
            
        Raises:
            BoundaryViolation: If AC deletion attempted without proper approval
        """
        if not context:
            return True
        
        from datetime import datetime
        
        action = context.get("action", "")
        # Check if this is a deletion action (exact "DELETE" or contains "DELETE")
        if not (action == "DELETE" or "DELETE" in action):
            return True  # Not a deletion action
        
        ac_id = context.get("ac_id", "UNKNOWN")
        approval = context.get("approval")
        ac_status = context.get("ac_status", "PENDING")
        
        # Check if approval exists and is valid
        if not approval or not approval.get("approved"):
            raise BoundaryViolation(
                ViolationType.AC_DELETION_WITHOUT_APPROVAL,
                f"AC {ac_id} deletion requires governance approval",
                severity="CRITICAL",
                context=context
            )
        
        # Check expiration if present
        if "expires_at" in approval:
            expires_at = datetime.fromisoformat(approval["expires_at"].replace("Z", "+00:00"))
            if expires_at < datetime.now(expires_at.tzinfo):
                raise BoundaryViolation(
                    ViolationType.AC_DELETION_WITHOUT_APPROVAL,
                    f"AC {ac_id} deletion approval has expired",
                    severity="CRITICAL",
                    context=context
                )
        
        # Check reason field
        if "reason" not in approval:
            raise BoundaryViolation(
                ViolationType.AC_DELETION_WITHOUT_APPROVAL,
                f"AC {ac_id} deletion requires audit reason",
                severity="CRITICAL",
                context=context
            )
        
        # For completed ACs, check approval authority level
        if ac_status == "COMPLETED":
            approved_by = approval.get("approved_by", "")
            if approved_by not in ("governance_admin", "system_admin", "owner"):
                raise BoundaryViolation(
                    ViolationType.AC_DELETION_WITHOUT_APPROVAL,
                    f"Completed AC {ac_id} deletion requires high-level approval",
                    severity="CRITICAL",
                    context=context
                )
        
        return True
    
    def check_governance_compliance(self, context: Dict[str, Any]) -> bool:
        """Check if governance compliance rules are being followed.
        
        Args:
            context: Context dict with operation_type, target, etc.
            
        Returns:
            True if allowed
            
        Raises:
            BoundaryViolation: If governance bypass detected
        """
        if not context:
            return True
        
        import re
        
        operation_type = context.get("operation_type")
        
        # Detect phase modification by unauthorized users
        if operation_type == "PHASE_MODIFICATION":
            tier = context.get("tier")
            action = context.get("action")
            
            # Only TIER0/TIER1 users can modify phase locks
            if action == "MODIFY_LOCK_STATUS" and tier and tier.startswith("TIER") and int(tier[4:]) > 1:
                violation = BoundaryViolation(
                    ViolationType.GOVERNANCE_BYPASS_ATTEMPT,
                    f"Unauthorized tier {tier} attempt to {action}",
                    severity="CRITICAL",
                    context=context
                )
                self.violations.append({
                    "violation_id": violation.violation_id,
                    "violation_type": ViolationType.GOVERNANCE_BYPASS_ATTEMPT.value,
                    "message": violation.message,
                    "severity": violation.severity,
                    "timestamp": datetime.now().isoformat(),
                })
                raise violation
        
        # Detect SQL injection patterns
        if operation_type == "QUERY_EXECUTION":
            query = context.get("query", "").upper()
            dangerous_patterns = [
                r"DROP\s+TABLE",
                r"DROP\s+DATABASE",
                r"DELETE\s+FROM",
                r"TRUNCATE",
                r"ALTER\s+TABLE",
            ]
            
            for pattern in dangerous_patterns:
                if re.search(pattern, query):
                    violation = BoundaryViolation(
                        ViolationType.GOVERNANCE_BYPASS_ATTEMPT,
                        f"SQL injection pattern detected: {pattern}",
                        severity="CRITICAL",
                        context=context
                    )
                    self.violations.append({
                        "violation_id": violation.violation_id,
                        "violation_type": ViolationType.GOVERNANCE_BYPASS_ATTEMPT.value,
                        "message": violation.message,
                        "severity": violation.severity,
                        "timestamp": datetime.now().isoformat(),
                    })
                    raise violation
        
        # Detect API bypass attempts
        if operation_type == "API_CALL":
            if context.get("bypass_lock"):
                violation = BoundaryViolation(
                    ViolationType.GOVERNANCE_BYPASS_ATTEMPT,
                    f"API call with explicit bypass flag: {context.get('endpoint')}",
                    severity="CRITICAL",
                    context=context
                )
                self.violations.append({
                    "violation_id": violation.violation_id,
                    "violation_type": ViolationType.GOVERNANCE_BYPASS_ATTEMPT.value,
                    "message": violation.message,
                    "severity": violation.severity,
                    "timestamp": datetime.now().isoformat(),
                })
                raise violation
        
        # Detect direct database modifications that bypass governance
        if operation_type in ("DIRECT_DB_WRITE", "RAW_SQL", "ORM_BYPASS"):
            target = context.get("target", "")
            
            # Governance-critical tables cannot be directly modified
            critical_tables = [
                "governance.db",
                "phase_locks",
                "audit_trail",
                "approval_records",
            ]
            
            for critical_table in critical_tables:
                if critical_table in target or critical_table in str(context.get("table", "")):
                    violation = BoundaryViolation(
                        ViolationType.GOVERNANCE_BYPASS_ATTEMPT,
                        f"Direct modification of {target} bypasses governance",
                        severity="CRITICAL",
                        context=context
                    )
                    self.violations.append({
                        "violation_id": violation.violation_id,
                        "violation_type": ViolationType.GOVERNANCE_BYPASS_ATTEMPT.value,
                        "message": violation.message,
                        "severity": violation.severity,
                        "timestamp": datetime.now().isoformat(),
                    })
                    raise violation
        
        # Detect unauthorized user bypass attempts
        if context.get("user_role") == "unauthorized":
            violation = BoundaryViolation(
                ViolationType.GOVERNANCE_BYPASS_ATTEMPT,
                f"Unauthorized user bypass attempt",
                severity="CRITICAL",
                context=context
            )
            self.violations.append({
                "violation_id": violation.violation_id,
                "violation_type": ViolationType.GOVERNANCE_BYPASS_ATTEMPT.value,
                "message": violation.message,
                "severity": violation.severity,
                "timestamp": datetime.now().isoformat(),
            })
            raise violation
        
        return True
    
    def get_recent_violations(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent violations from cache.
        
        Args:
            limit: Maximum number of violations to return
            
        Returns:
            List of violation records
        """
        return self.violations[-limit:] if self.violations else []
    
    def get_violation_chain(self, correlation_id: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Get violations in a chain (by correlation ID).
        
        Args:
            correlation_id: Optional correlation ID to filter by
            limit: Maximum number to return
            
        Returns:
            List of violation records in the chain
        """
        if not correlation_id:
            return self.get_recent_violations(limit)
        
        chain = [v for v in self.violations if v.get("correlation_id") == correlation_id]
        return chain[-limit:] if chain else []
    
    def check_phase_lock(self, context: Dict[str, Any]) -> bool:
        """Check if phase modification is allowed.
        
        Args:
            context: Context dict with phase_id, phase_locked, action, etc.
            
        Returns:
            True if allowed
            
        Raises:
            BoundaryViolation: If locked phase modification attempted
        """
        if not context:
            raise ValueError("Context cannot be None for phase lock check")
        
        phase_locked = context.get("phase_locked", False)
        action = context.get("action", "READ")
        
        if phase_locked and action in ("MODIFY", "DELETE"):
            phase_id = context.get("phase_id", "UNKNOWN")
            violation = BoundaryViolation(
                ViolationType.LOCKED_PHASE_MODIFICATION,
                f"Cannot {action} locked phase {phase_id}",
                severity="CRITICAL",
                context=context
            )
            self.violations.append({
                "violation_id": violation.violation_id,
                "violation_type": ViolationType.LOCKED_PHASE_MODIFICATION.value,
                "message": violation.message,
                "severity": violation.severity,
                "timestamp": datetime.now().isoformat(),
                "context": context,  # Store full context
                "phase_id": phase_id,
                "action": action,
                "user_id": context.get("user_id"),
                "correlation_id": context.get("correlation_id"),
            })
            raise violation
        
        return True
    
    def check_combined_boundaries(self, context: Dict[str, Any]) -> bool:
        """Check multiple boundary rules together.
        
        Applies all applicable boundary checks and reports the most critical violation.
        
        Args:
            context: Context dict with all boundary check parameters
            
        Returns:
            True if all checks pass
            
        Raises:
            BoundaryViolation: For most critical violation detected
        """
        if not context:
            return True
        
        violations_found: List[BoundaryViolation] = []
        
        # Try AC deletion check
        try:
            self.check_ac_deletion(context)
        except BoundaryViolation as e:
            violations_found.append(e)
        
        # Try governance compliance check
        try:
            self.check_governance_compliance(context)
        except BoundaryViolation as e:
            violations_found.append(e)
        
        # Try phase lock check
        try:
            self.check_phase_lock(context)
        except BoundaryViolation as e:
            violations_found.append(e)
        
        # If violations found, raise the most critical one
        if violations_found:
            # Sort by severity level
            severity_order = {"CRITICAL": 3, "WARNING": 2, "INFO": 1}
            most_critical = max(
                violations_found,
                key=lambda v: severity_order.get(v.severity, 0)
            )
            raise most_critical
        
        return True


# Global instance
_global_boundary_rules: Optional[BehavioralBoundaryRules] = None


def get_behavioral_boundary_rules() -> BehavioralBoundaryRules:
    """Get global boundary rules instance.

    Returns:
        BehavioralBoundaryRules singleton.
    """
    global _global_boundary_rules
    if _global_boundary_rules is None:
        _global_boundary_rules = BehavioralBoundaryRules()
    return _global_boundary_rules


__all__ = [
    "BehavioralBoundaryRules",
    "BoundaryRule",
    "BoundaryViolation",
    "ViolationType",
    "get_behavioral_boundary_rules",
]
