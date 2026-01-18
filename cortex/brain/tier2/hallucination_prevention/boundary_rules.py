"""
Behavioral Boundary Rules Module (AC-HP-001-02)

Enforces behavioral boundaries to prevent:
- Locked phase modification
- AC deletion without approval
- Governance bypass attempts
- Unauthorized modifications

Implements CORE-013 (Boundary Enforcement) and CORE-014 (Violation Handling).
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum


# =========================================================================
# ENUMS
# =========================================================================

class SeverityLevel(Enum):
    """Violation severity levels."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class RuleType(Enum):
    """Types of boundary rules."""
    PHASE_LOCK = "PHASE_LOCK"
    AC_DELETION = "AC_DELETION"
    GOVERNANCE_BYPASS = "GOVERNANCE_BYPASS"
    UNAUTHORIZED_MODIFICATION = "UNAUTHORIZED_MODIFICATION"
    PERMISSION_VIOLATION = "PERMISSION_VIOLATION"


class ViolationActionType(Enum):
    """Actions to take on violation."""
    REJECT = "REJECT"
    LOG = "LOG"
    REQUIRE_APPROVAL = "REQUIRE_APPROVAL"
    ISOLATE = "ISOLATE"
    ALERT = "ALERT"


class RecoveryActionType(Enum):
    """Recovery actions for violations."""
    LOG_ALERT = "LOG_ALERT"
    QUARANTINE = "QUARANTINE"
    ROLLBACK = "ROLLBACK"
    ISOLATE = "ISOLATE"
    ESCALATE = "ESCALATE"


# =========================================================================
# DATA STRUCTURES
# =========================================================================

@dataclass
class BoundaryRule:
    """
    Represents a boundary rule that enforces behavioral constraints.
    
    Attributes:
        rule_id: Unique rule identifier (e.g., 'BR-001')
        rule_type: Type of boundary rule (from RuleType enum)
        description: Human-readable rule description
        severity: Severity level of violations (from SeverityLevel enum)
        action: Action to take on violation (from ViolationActionType enum)
        recovery_action: Recovery action on violation (from RecoveryActionType enum)
        metadata: Optional metadata with additional rule configuration
    """
    rule_id: str
    rule_type: str
    description: str
    severity: str
    action: str
    recovery_action: str
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class BoundaryViolation:
    """
    Represents a violation of a boundary rule.
    
    Attributes:
        violation_id: Unique violation identifier
        rule_id: ID of the violated rule
        rule_type: Type of boundary rule violated
        severity: Severity level of this violation
        description: Description of the violation
        attempted_action: The action that violated the boundary
        actor: User or system component attempting the action
        timestamp: When the violation occurred
        context: Optional contextual data about the violation
    """
    violation_id: str
    rule_id: str
    rule_type: str
    severity: str
    description: str
    attempted_action: str
    actor: str
    timestamp: datetime
    context: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        """Ensure context is initialized."""
        if self.context is None:
            self.context = {}


@dataclass
class RecoveryPlan:
    """
    Represents a plan to recover from a boundary violation.
    
    Attributes:
        violation_id: ID of the violation being addressed
        action: Primary recovery action to execute
        steps: Ordered list of recovery steps
        estimated_duration_seconds: Estimated time to complete recovery
        metadata: Optional additional recovery metadata
    """
    violation_id: str
    action: str
    steps: List[str] = field(default_factory=list)
    estimated_duration_seconds: int = 0
    metadata: Optional[Dict[str, Any]] = None


# =========================================================================
# BOUNDARY ENFORCER
# =========================================================================

class BoundaryEnforcer:
    """
    Enforces behavioral boundaries by checking operations against rules.
    
    Implements detection and validation of:
    - Locked phase modifications
    - AC deletion without approval
    - Governance bypass attempts
    - Unauthorized modifications
    """

    def __init__(self):
        """Initialize enforcer with standard boundary rules."""
        self.rules: Dict[str, BoundaryRule] = {}
        self._initialize_standard_rules()

    def _initialize_standard_rules(self):
        """Initialize standard boundary rules."""
        # Phase lock rule
        self.rules['BR-001'] = BoundaryRule(
            rule_id='BR-001',
            rule_type='PHASE_LOCK',
            description='Prevent modification of locked phases',
            severity='CRITICAL',
            action='REJECT',
            recovery_action='LOG_ALERT',
            metadata={'applies_to': ['STATUS_UPDATE', 'DELETE_PHASE', 'RESET_PROGRESS']},
        )

        # AC deletion rule
        self.rules['BR-002'] = BoundaryRule(
            rule_id='BR-002',
            rule_type='AC_DELETION',
            description='Prevent AC deletion without sufficient approval',
            severity='HIGH',
            action='REQUIRE_APPROVAL',
            recovery_action='QUARANTINE',
            metadata={'requires_approvals': 2, 'can_delete_status': ['NOT_STARTED']},
        )

        # Governance bypass rule
        self.rules['BR-003'] = BoundaryRule(
            rule_id='BR-003',
            rule_type='GOVERNANCE_BYPASS',
            description='Prevent direct file/database modification bypassing API',
            severity='CRITICAL',
            action='REJECT',
            recovery_action='ISOLATE',
            metadata={
                'blocked_operations': ['DIRECT_FILE_WRITE', 'DIRECT_DB_WRITE', 'AUDIT_LOG_MODIFICATION']
            },
        )

        # Unauthorized modification rule
        self.rules['BR-004'] = BoundaryRule(
            rule_id='BR-004',
            rule_type='UNAUTHORIZED_MODIFICATION',
            description='Prevent unauthorized modifications',
            severity='HIGH',
            action='REJECT',
            recovery_action='LOG_ALERT',
        )

    def check_phase_modification(
        self,
        phase_state: Dict[str, Any],
        modification_type: str,
        actor: str,
    ) -> Optional[BoundaryViolation]:
        """
        Check if a phase modification violates boundaries.
        
        Args:
            phase_state: Current phase state dictionary
            modification_type: Type of modification attempted
            actor: User or component attempting modification
            
        Returns:
            BoundaryViolation if boundary violated, None if allowed
        """
        # Check if phase is locked
        if phase_state.get('locked', False):
            violation = BoundaryViolation(
                violation_id=f'BV-PHASE-{actor[:8]}-{int(datetime.now().timestamp())}',
                rule_id='BR-001',
                rule_type='PHASE_LOCK',
                severity='CRITICAL',
                description=f'Attempted {modification_type} on locked phase {phase_state.get("phase_id")}',
                attempted_action=modification_type,
                actor=actor,
                timestamp=datetime.now(),
                context={'phase_id': phase_state.get('phase_id'), 'locked': True},
            )
            return violation
        return None

    def check_ac_deletion(
        self,
        ac_id: str,
        phase_id: str,
        actor: str,
        approval_count: int = 0,
        ac_status: Optional[str] = None,
    ) -> Optional[BoundaryViolation]:
        """
        Check if an AC deletion violates boundaries.
        
        Args:
            ac_id: ID of AC to delete
            phase_id: Phase containing the AC
            actor: User attempting deletion
            approval_count: Number of approvals obtained (requires 2)
            ac_status: Current status of AC (COMPLETED cannot be deleted)
            
        Returns:
            BoundaryViolation if boundary violated, None if allowed
        """
        # Check approval count
        required_approvals = 2
        if approval_count < required_approvals:
            violation = BoundaryViolation(
                violation_id=f'BV-ACDEL-{actor[:8]}-{int(datetime.now().timestamp())}',
                rule_id='BR-002',
                rule_type='AC_DELETION',
                severity='HIGH',
                description=f'AC {ac_id} deletion attempt with insufficient approval (have {approval_count}, need {required_approvals})',
                attempted_action='DELETE_AC',
                actor=actor,
                timestamp=datetime.now(),
                context={'ac_id': ac_id, 'phase_id': phase_id, 'approval_count': approval_count},
            )
            return violation

        # Check if AC is already completed
        if ac_status == 'COMPLETED':
            violation = BoundaryViolation(
                violation_id=f'BV-ACDEL-{actor[:8]}-{int(datetime.now().timestamp())}',
                rule_id='BR-002',
                rule_type='AC_DELETION',
                severity='HIGH',
                description=f'Cannot delete completed AC {ac_id}',
                attempted_action='DELETE_AC',
                actor=actor,
                timestamp=datetime.now(),
                context={'ac_id': ac_id, 'ac_status': ac_status},
            )
            return violation

        return None

    def check_governance_bypass(
        self,
        operation_type: str,
        target: str,
        actor: str,
        bypass_method: Optional[str] = None,
    ) -> Optional[BoundaryViolation]:
        """
        Check if an operation bypasses governance controls.
        
        Args:
            operation_type: Type of operation (e.g., DIRECT_FILE_WRITE)
            target: Target of operation (file or system)
            actor: User attempting operation
            bypass_method: Method of bypass if detected
            
        Returns:
            BoundaryViolation if bypass attempted, None if allowed
        """
        # Blocked operations
        blocked_ops = ['DIRECT_FILE_WRITE', 'DIRECT_DB_WRITE', 'AUDIT_LOG_MODIFICATION']
        
        if operation_type in blocked_ops:
            severity = 'CRITICAL' if operation_type == 'AUDIT_LOG_MODIFICATION' else 'CRITICAL'
            violation = BoundaryViolation(
                violation_id=f'BV-BYPASS-{actor[:8]}-{int(datetime.now().timestamp())}',
                rule_id='BR-003',
                rule_type='GOVERNANCE_BYPASS',
                severity=severity,
                description=f'Governance bypass attempt via {operation_type} to {target}',
                attempted_action=operation_type,
                actor=actor,
                timestamp=datetime.now(),
                context={'target': target, 'bypass_method': bypass_method},
            )
            return violation

        return None

    def check_unauthorized_modification(
        self,
        modification_type: str,
        ac_id: Optional[str] = None,
        phase_id: Optional[str] = None,
        actor: Optional[str] = None,
        required_role: Optional[str] = None,
        current_sequence: Optional[int] = None,
        target_sequence: Optional[int] = None,
        phase_dependencies_met: bool = True,
    ) -> Optional[BoundaryViolation]:
        """
        Check if a modification is unauthorized.
        
        Args:
            modification_type: Type of modification
            ac_id: AC being modified (optional)
            phase_id: Phase being modified (optional)
            actor: User attempting modification
            required_role: Role required for modification (e.g., 'LEAD')
            current_sequence: Current phase sequence
            target_sequence: Target phase sequence
            phase_dependencies_met: Whether dependencies are met
            
        Returns:
            BoundaryViolation if unauthorized, None if allowed
        """
        # Check role-based authorization
        if required_role and actor:
            # Simplified check: if actor doesn't have role tag, deny
            # In real system, would check against role database
            if required_role == 'LEAD' and 'lead' not in actor.lower():
                violation = BoundaryViolation(
                    violation_id=f'BV-AUTHZ-{actor[:8]}-{int(datetime.now().timestamp())}',
                    rule_id='BR-004',
                    rule_type='UNAUTHORIZED_MODIFICATION',
                    severity='HIGH',
                    description=f'Unauthorized modification by {actor}: requires {required_role} role',
                    attempted_action=modification_type,
                    actor=actor,
                    timestamp=datetime.now(),
                    context={'required_role': required_role, 'ac_id': ac_id, 'phase_id': phase_id},
                )
                return violation

        # Check sequence ordering
        if current_sequence is not None and target_sequence is not None:
            if not phase_dependencies_met:
                violation = BoundaryViolation(
                    violation_id=f'BV-SEQ-{actor[:8]}-{int(datetime.now().timestamp())}',
                    rule_id='BR-004',
                    rule_type='UNAUTHORIZED_MODIFICATION',
                    severity='HIGH',
                    description=f'Out-of-sequence modification: cannot advance from PHASE-{current_sequence} to PHASE-{target_sequence} without dependencies',
                    attempted_action=modification_type,
                    actor=actor or 'unknown',
                    timestamp=datetime.now(),
                    context={
                        'current_sequence': current_sequence,
                        'target_sequence': target_sequence,
                        'dependencies_met': phase_dependencies_met,
                    },
                )
                return violation

        return None


# =========================================================================
# BOUNDARY AUDIT LOGGER
# =========================================================================

class BoundaryAuditLogger:
    """
    Logs and tracks boundary violations for auditing.
    
    Provides querying capabilities by rule, actor, severity, and time range.
    """

    def __init__(self):
        """Initialize audit logger."""
        self.violations: List[BoundaryViolation] = []

    def log_violation(self, violation: BoundaryViolation) -> str:
        """
        Log a boundary violation.
        
        Args:
            violation: BoundaryViolation to log
            
        Returns:
            Violation ID
        """
        self.violations.append(violation)
        return violation.violation_id

    def get_all_violations(self) -> List[BoundaryViolation]:
        """Get all logged violations."""
        return self.violations.copy()

    def get_violations_by_rule(self, rule_id: str) -> List[BoundaryViolation]:
        """Get violations for a specific rule."""
        return [v for v in self.violations if v.rule_id == rule_id]

    def get_violations_by_actor(self, actor: str) -> List[BoundaryViolation]:
        """Get violations by a specific actor."""
        return [v for v in self.violations if v.actor == actor]

    def get_violations_by_severity(self, severity: str) -> List[BoundaryViolation]:
        """Get violations by severity level."""
        return [v for v in self.violations if v.severity == severity]

    def get_critical_violations(self) -> List[BoundaryViolation]:
        """Get all critical severity violations."""
        return self.get_violations_by_severity('CRITICAL')

    def violation_count_by_rule(self) -> Dict[str, int]:
        """Get count of violations by rule."""
        counts: Dict[str, int] = {}
        for v in self.violations:
            counts[v.rule_id] = counts.get(v.rule_id, 0) + 1
        return counts


# =========================================================================
# BOUNDARY RECOVERY
# =========================================================================

class BoundaryRecovery:
    """
    Handles recovery from boundary violations.
    
    Implements recovery plans and executes recovery actions.
    """

    def __init__(self):
        """Initialize recovery handler."""
        self.recovery_plans: Dict[str, RecoveryPlan] = {}

    def create_recovery_plan(self, violation: BoundaryViolation) -> RecoveryPlan:
        """
        Create a recovery plan for a violation.
        
        Args:
            violation: BoundaryViolation to create plan for
            
        Returns:
            RecoveryPlan with steps and actions
        """
        plan_id = violation.violation_id

        # Create plan based on violation type
        if violation.rule_type == 'PHASE_LOCK':
            plan = RecoveryPlan(
                violation_id=plan_id,
                action='LOG_ALERT',
                steps=[
                    'Log violation to audit trail',
                    'Send alert to phase lead',
                    'Record attempted modification details',
                    'Prevent modification from taking effect',
                ],
                estimated_duration_seconds=5,
                metadata={'priority': 'HIGH'},
            )
        elif violation.rule_type == 'AC_DELETION':
            plan = RecoveryPlan(
                violation_id=plan_id,
                action='QUARANTINE',
                steps=[
                    'Quarantine AC from modification',
                    'Log deletion attempt',
                    'Notify approvers',
                    'Request additional approvals if needed',
                ],
                estimated_duration_seconds=10,
                metadata={'priority': 'HIGH'},
            )
        elif violation.rule_type == 'GOVERNANCE_BYPASS':
            plan = RecoveryPlan(
                violation_id=plan_id,
                action='ISOLATE',
                steps=[
                    'Immediately isolate affected systems',
                    'Log critical violation',
                    'Escalate to security team',
                    'Prevent further access from actor',
                    'Review audit trail for other bypass attempts',
                ],
                estimated_duration_seconds=30,
                metadata={'priority': 'CRITICAL'},
            )
        else:
            plan = RecoveryPlan(
                violation_id=plan_id,
                action='LOG_ALERT',
                steps=[
                    'Log violation',
                    'Alert relevant stakeholders',
                ],
                estimated_duration_seconds=5,
                metadata={'priority': 'MEDIUM'},
            )

        self.recovery_plans[plan_id] = plan
        return plan

    def execute_recovery(
        self,
        violation: BoundaryViolation,
        plan: RecoveryPlan,
    ) -> Dict[str, Any]:
        """
        Execute a recovery plan.
        
        Args:
            violation: The boundary violation
            plan: The recovery plan to execute
            
        Returns:
            Result dictionary with status and details
        """
        result = {
            'status': 'SUCCESS',
            'violation_id': violation.violation_id,
            'plan_id': plan.violation_id,
            'action': plan.action,
            'steps_executed': len(plan.steps),
            'timestamp': datetime.now().isoformat(),
        }

        # In real implementation, would execute actual recovery steps
        # For now, simulate successful execution
        return result


# =========================================================================
# MODULE EXPORTS
# =========================================================================

__all__ = [
    'BoundaryRule',
    'BoundaryViolation',
    'RecoveryPlan',
    'BoundaryEnforcer',
    'BoundaryAuditLogger',
    'BoundaryRecovery',
    'SeverityLevel',
    'RuleType',
    'ViolationActionType',
    'RecoveryActionType',
]
